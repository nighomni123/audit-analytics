"""Experimental, run-scoped semantic evidence. No audit conclusions or model downloads."""
from __future__ import annotations

import hashlib
import json
import math
import struct
import time
import tracemalloc
from collections import defaultdict

from .semantic import LocalEmbedder, _entries, _cosine, classify, tokens
from .model_registry import list_models

ENGINE_VERSION = 'semantic-risk-v1'
TEMPLATE_VERSION = 'narration-only-v1'
LIMITATION = 'Experimental semantic cues are investigation aids, not audit conclusions. Thresholds require authorised validation.'
DEFAULTS = dict(min_peers=5, seed=7, clusters=None, max_iterations=10,
                training_limit=512, candidate_limit=64, peer_limit=5, related_limit=25,
                own_similarity_max=.50, alternate_similarity_min=.75, mismatch_margin_min=.25,
                novelty_min=.50, vendor_distance_min=.50, process_similarity_max=.50,
                cluster_distance_min=.50)


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _hash(value):
    return hashlib.sha256(_json(value).encode()).hexdigest()


def population_hash(store):
    return _hash({'engagement': dict(store.engagement() or {}), 'entries': _entries(store),
                  'coa': [dict(r) for r in store.conn.execute('SELECT * FROM coa ORDER BY account_code')],
                  'imports': [dict(r) for r in store.conn.execute('SELECT * FROM imports ORDER BY id')]})


def _key(value):
    return ' '.join(str(value or '').split()).casefold()


def _unit(vector):
    if not isinstance(vector, (list, tuple)):
        vector = list(vector)
    if not vector or any(isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) for x in vector):
        raise ValueError('embedding must contain finite numeric values')
    norm = math.sqrt(sum(x*x for x in vector))
    if not norm or not math.isfinite(norm): raise ValueError('embedding must have finite nonzero norm')
    return [x/norm for x in vector]


def _pack(vector):
    return struct.pack('<' + 'f'*len(vector), *vector)


def _unpack(blob, dims):
    if len(blob) != 4*dims: raise ValueError('corrupt semantic vector dimensions')
    return _unit(struct.unpack('<'+'f'*dims, blob))


def _config(config):
    if config is not None and not isinstance(config, dict): raise ValueError('semantic config must be an object')
    unknown = set(config or {}) - set(DEFAULTS)
    if unknown: raise ValueError('unknown semantic config: '+', '.join(sorted(unknown)))
    cfg = {**DEFAULTS, **(config or {})}
    for k in ('min_peers','seed','clusters','max_iterations','training_limit','candidate_limit','peer_limit','related_limit'):
        v = cfg[k]
        if k == 'clusters' and v is None: continue
        if isinstance(v,bool) or not isinstance(v,int) or v < (0 if k=='seed' else 1): raise ValueError(k+' must be a positive integer (seed may be zero)')
    for k, ceiling in [('training_limit',512),('candidate_limit',64),('peer_limit',5),('related_limit',25),('max_iterations',10),('clusters',12)]:
        if cfg[k] is not None and cfg[k]>ceiling: raise ValueError(f'{k} must be <= {ceiling}')
    for k in set(DEFAULTS)-{'min_peers','seed','clusters','max_iterations','training_limit','candidate_limit','peer_limit','related_limit'}:
        v=cfg[k]; lo,hi=(-1,1) if 'similarity' in k else (0,2)
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not lo<=v<=hi: raise ValueError(f'{k} must be in [{lo},{hi}]')
    return cfg


def _dot(a, b):
    # ponytail: validation-free inner product; callers pass vectors already checked by _unit/_cosine at the boundary.
    return sum(x*y for x, y in zip(a, b))


def _raw_cosine(a, b):
    denom = math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(x*x for x in b))
    if not denom or not math.isfinite(denom): raise ValueError('cosine requires finite nonzero norms')
    return max(-1.0, min(1.0, _dot(a, b) / denom))


def _bounded(ids, limit, seed):
    return sorted(ids, key=lambda i: (_hash([seed,i]),i))[:limit]


def _centroid(ids, vectors):
    if not ids: return None
    total=[0.0]*len(vectors[ids[0]])
    for i in ids:
        for j,x in enumerate(vectors[i]): total[j]+=x
    if sum(x*x for x in total) < 1e-20: return None
    return _unit(total)


def _clusters(vectors, cfg):
    if not vectors: return {}, []
    # ponytail: bounded spherical k-means training; use a measured indexed/vectorized backend if 512 samples cease to represent the population.
    train=_bounded(vectors, cfg['training_limit'],cfg['seed'])
    unique=[]; seen=set()
    for i in train:
        signature=tuple(round(v,7) for v in vectors[i])
        if signature not in seen: unique.append(i); seen.add(signature)
    k=min(cfg['clusters'] or min(12,max(2,int(math.sqrt(len(vectors)/5)))),len(unique))
    centers=[vectors[i] for i in unique[:k]]
    for _ in range(cfg['max_iterations']):
        groups=defaultdict(list)
        for i in train:
            c=max(range(k),key=lambda c:(_raw_cosine(vectors[i],centers[c]),-c)); groups[c].append(i)
        new=[_centroid(groups[c],vectors) or centers[c] for c in range(k)]
        if max(1-_raw_cosine(a,b) for a,b in zip(centers,new))<1e-8:
            centers=new; break
        centers=new
    assignments={i:1+max(range(k),key=lambda c:(_raw_cosine(vectors[i],centers[c]),-c)) for i in vectors}
    return assignments, train


def _calculate(entries, vectors, cfg):
    byid={e['id']:e for e in entries}; groups={k:defaultdict(list) for k in ('account','vendor','preparer','entity','period','cluster')}
    assignments, training_ids=_clusters(vectors,cfg)
    keys={}
    for e in entries:
        i=e['id']; entity=_key(e.get('entity'))
        keys[i]={'account':(entity,_key(e['account_code'])), 'vendor':(entity,_key(e.get('vendor'))),
                 'preparer':(entity,_key(e.get('preparer'))), 'entity':(entity,),
                 'period':(entity,e['posting_date'][:7]),'cluster':(assignments.get(i),)}
        if i not in vectors: continue
        for kind,key in keys[i].items():
            if kind in ('vendor','preparer','entity') and not key[-1]: continue
            groups[kind][key].append(i)
    sums={}; centers={}
    for kind,populations in groups.items():
        for key,ids in populations.items():
            total=[sum(vectors[i][d] for i in ids) for d in range(len(vectors[ids[0]]))]
            sums[kind,key]=total; centers[kind,key]=_centroid(ids,vectors)
    def nearest(i, ids):
        # ponytail: deterministic candidate cap bounds scans; approximate neighbours disclose full population and candidate IDs.
        candidates=_bounded((x for x in ids if x!=i),cfg['candidate_limit'],cfg['seed'])
        scored=[( _raw_cosine(vectors[i],vectors[x]),x) for x in candidates]
        ranked=sorted(scored,key=lambda t:(-t[0],t[1]))
        return [{'ledger_id':x,'similarity':s,'entry':byid[x]} for s,x in ranked[:cfg['peer_limit']]], candidates
    results=[]
    for e in entries:
        i=e['id']; comparisons={}; metrics={}; cues=[]
        ev={'entry':e,'normal_peers':[],'alternative_matches':[],'related_population':{},'comparisons':comparisons,
            'suggested_evidence':['Inspect source invoice/contract, posting rationale and authorisation; compare the cited peer documents.'],
            'limitations':[LIMITATION,'Nearest examples are sampled deterministically, not an exhaustive nearest-neighbour index.'], 'cue_details':{}}
        if not e.get('entity'): ev['limitations'].append('Entity is missing; comparisons use only the missing-entity population.')
        if i not in vectors:
            results.append((i,None,{},[],{**ev,'eligibility':'missing narration'})); continue
        for kind,metric in [('account','peer_similarity'),('vendor','vendor_peer_similarity'),('preparer','preparer_peer_similarity'),('entity','entity_peer_similarity'),('period','period_peer_similarity'),('cluster','cluster_similarity')]:
            key=keys[i][kind]; ids=groups[kind].get(key,[]); count=len(ids)-(i in ids)
            total=sums.get((kind,key)); vector=None
            if total is not None and count>=cfg['min_peers']:
                remaining=[x-y for x,y in zip(total,vectors[i])]
                if sum(x*x for x in remaining)>1e-20: vector=_unit(remaining)
            metrics[metric]=_raw_cosine(vectors[i],vector) if vector else None
            comparisons[metric]={'formula':'cosine(target, normalized mean of peers excluding target)', 'basis':'current population excluding self','peer_count':count,'minimum_peers':cfg['min_peers'], 'applicable':vector is not None,'reason':None if vector else 'missing identity, insufficient peers or cancelling centroid'}
        metrics['account_semantic_distance']=None if metrics['peer_similarity'] is None else 1-metrics['peer_similarity']
        metrics['cluster_distance']=None if metrics['cluster_similarity'] is None else 1-metrics['cluster_similarity']
        own=groups['account'][keys[i]['account']]
        ev['normal_peers'],cand=nearest(i,own)
        comparisons['peer_similarity'].update(candidate_ids=cand,population_count=len(own)-1)
        alternatives=[]
        for key,ids in groups['account'].items():
            center=centers['account',key]
            if key==keys[i]['account'] or key[0]!=keys[i]['account'][0] or len(ids)<cfg['min_peers'] or center is None: continue
            alternatives.append((_raw_cosine(vectors[i],center),key,ids))
        best=sorted(alternatives,key=lambda x:(-x[0],x[1]))[0] if alternatives else None
        metrics['cross_account_similarity']=best[0] if best else None
        metrics['account_mismatch_margin']=best[0]-metrics['peer_similarity'] if best and metrics['peer_similarity'] is not None else None
        comparisons['cross_account_similarity']={'formula':'maximum cosine to another account centroid in same entity','applicable':bool(best),'peer_count':len(best[2]) if best else 0,'alternative_account':byid[best[2][0]]['account_code'] if best else None,'reason':None if best else 'no eligible alternate account'}
        if best:
            ev['alternative_matches'],cand=nearest(i,best[2]); comparisons['cross_account_similarity']['candidate_ids']=cand
        for kind,metric in [('account','narrative_novelty'),('vendor','vendor_semantic_distance')]:
            hist=[x for x in groups[kind].get(keys[i][kind],[]) if byid[x]['posting_date'][:7]<e['posting_date'][:7]]
            examples,cand=nearest(i,hist)
            centroid=_centroid(hist,vectors) if len(hist)>=cfg['min_peers'] else None
            applicable=len(hist)>=cfg['min_peers'] and bool(examples) and (kind=='account' or centroid is not None)
            metrics[metric]=(1-examples[0]['similarity'] if kind=='account' else 1-_raw_cosine(vectors[i],centroid)) if applicable else None
            comparisons[metric]={'formula':'1 - maximum sampled historical cosine' if kind=='account' else '1 - cosine to historical vendor centroid','basis':'strictly earlier calendar months in this engagement/entity', 'peer_count':len(hist),'candidate_ids':cand,'applicable':applicable,'reason':None if applicable else 'missing identity or insufficient history','examples':examples}
        for kind in ('vendor','preparer','entity','cluster'):
            ids=[x for x in groups[kind].get(keys[i][kind],[]) if x!=i]
            ev['related_population'][kind]={'count':len(ids),'entries':[byid[x] for x in sorted(ids)[:cfg['related_limit']]],'truncated':len(ids)>cfg['related_limit']}
        def flag(name, condition, values, thresholds):
            if condition:
                cues.append(name); ev['cue_details'][name]={'values':values,'thresholds':thresholds,'note':LIMITATION}
        p=metrics['peer_similarity']; alt=metrics['cross_account_similarity']; margin=metrics['account_mismatch_margin']
        flag('semantic_account_mismatch',p is not None and alt is not None and p<=cfg['own_similarity_max'] and alt>=cfg['alternate_similarity_min'] and margin>=cfg['mismatch_margin_min'],{'own':p,'alternative':alt,'margin':margin},{k:cfg[k] for k in ('own_similarity_max','alternate_similarity_min','mismatch_margin_min')})
        for cue,metric,threshold in [('semantic_novel_transaction','narrative_novelty','novelty_min'),('semantic_vendor_shift','vendor_semantic_distance','vendor_distance_min'),('semantic_cluster_outlier','cluster_distance','cluster_distance_min')]:
            v=metrics[metric]; flag(cue,v is not None and v>=cfg[threshold],{metric:v},{threshold:cfg[threshold]})
        peer_values={k:metrics[k] for k in ('peer_similarity','vendor_peer_similarity','preparer_peer_similarity')}
        flag('semantic_process_outlier',all(v is not None and v<=cfg['process_similarity_max'] for v in peer_values.values()),peer_values,{'process_similarity_max':cfg['process_similarity_max']})
        results.append((i,assignments[i],metrics,sorted(cues),ev))
    profiles=[]; cluster_summary=[]
    for kind in ('account','vendor','preparer','entity','cluster'):
        for key,ids in sorted(groups[kind].items()):
            center=centers[kind,key]
            if center is None: continue
            reps=sorted(ids,key=lambda i:(-_raw_cosine(vectors[i],center),i))[:cfg['peer_limit']]
            meta={'group_key':key,'date_start':min(byid[i]['posting_date'] for i in ids),'date_end':max(byid[i]['posting_date'] for i in ids),'representatives':[byid[i] for i in reps]}
            if kind=='cluster':
                meta.update(label=f'Process {key[0]:02d}',heuristic_class_hints=sorted({c for i in reps for c in classify(byid[i]['description'])}),training_ids=training_ids)
                cluster_summary.append({'cluster_id':key[0],'member_count':len(ids),**meta})
            profiles.append(('process' if kind=='cluster' else kind,_json(key),None,center,len(ids),meta))
    return results,profiles,cluster_summary


def semantic_profile(store,model='embeddinggemma',batch_size=64,actor='system',config=None):
    cfg=_config(config)
    if isinstance(batch_size,bool) or not isinstance(batch_size,int) or batch_size<=0: raise ValueError('batch_size must be positive')
    store.require_role(actor,{'preparer','reviewer','manager','partner'})
    if not store.population_acknowledged(): raise ValueError('acknowledge every GL population before semantic profiling')
    entries=_entries(store)
    if not entries: raise ValueError('no ledger entries')
    fingerprint=population_hash(store); started=time.time()
    run=store.conn.execute('INSERT INTO semantic_runs(started_at,actor,status,population_count,population_hash,configuration_json,provenance_json) VALUES(?,?,?,?,?,?,?)',(started,actor,'running',len(entries),fingerprint,_json(cfg),'{}')).lastrowid
    store.conn.commit()
    tracing=not tracemalloc.is_tracing()
    if tracing: tracemalloc.start()
    try:
        embedder=LocalEmbedder(model); identity=embedder.identity()
        registry=[r for r in list_models(store) if r['name']==model]
        provenance={'model':model,'digest':identity['digest'],'runtime':identity,'template_version':TEMPLATE_VERSION,'engine_version':ENGINE_VERSION,'serialization':'little-endian float32','registry_snapshot':registry,'validation_status':registry[0]['status'] if registry else 'unregistered','input_hashes':[dict(r) for r in store.conn.execute('SELECT id,sha256 FROM imports ORDER BY id')]}
        cache={}
        for row in store.conn.execute("SELECT p.*,r.provenance_json FROM semantic_profiles p JOIN semantic_runs r ON r.id=p.run_id WHERE p.kind='transaction' AND r.status='complete' ORDER BY r.id DESC"):
            prov=json.loads(row['provenance_json'])
            if prov.get('digest')==identity['digest'] and prov.get('template_version')==TEMPLATE_VERSION:
                meta=json.loads(row['metadata_json']); cache.setdefault(meta['text_hash'],(row['vector'],row['dims']))
        vectors={}; pending=[]; hashes={}; reused=0; dims=None
        for e in entries:
            narration=' '.join(str(e.get('description') or '').split())
            if not narration: continue
            text='Narration: '+narration; digest=_hash([TEMPLATE_VERSION,text]); hashes[e['id']]=digest
            if digest in cache:
                blob,d=cache[digest]; vectors[e['id']]=_unpack(blob,d); reused+=1
                if dims is not None and dims!=d: raise ValueError('cached dimensions disagree')
                dims=d
            else: pending.append((e['id'],text))
        for start in range(0,len(pending),batch_size):
            batch=pending[start:start+batch_size]; outputs=embedder.embed([t for _,t in batch])
            if len(outputs)!=len(batch): raise ValueError('invalid embedding batch size')
            for (i,_),out in zip(batch,outputs):
                v=_unit(out)
                if dims is not None and len(v)!=dims: raise ValueError('model dimensions changed')
                dims=len(v); vectors[i]=_unpack(_pack(v),dims)
        if embedder.identity()['digest']!=identity['digest']: raise ValueError('installed model changed during embedding')
        provenance['dimensions']=dims
        results,aggregates,clusters=_calculate(entries,vectors,cfg)
        if population_hash(store)!=fingerprint: raise ValueError('population changed during semantic profiling')
        for e in entries:
            i=e['id']
            if i in vectors:
                store.conn.execute('INSERT INTO semantic_profiles VALUES(?,?,?,?,?,?,?,?)',(run,'transaction',str(i),i,dims,_pack(vectors[i]),1,_json({'entry':e,'text_hash':hashes[i],'template_version':TEMPLATE_VERSION})))
        for kind,key,lid,v,count,meta in aggregates:
            store.conn.execute('INSERT INTO semantic_profiles VALUES(?,?,?,?,?,?,?,?)',(run,kind,key,lid,len(v),_pack(v),count,_json(meta)))
        for i,cluster,metrics,cues,evidence in results:
            store.conn.execute('INSERT INTO semantic_results VALUES(?,?,?,?,?,?)',(run,i,cluster,_json(metrics),_json(cues),_json(evidence)))
        entry_by_id={e['id']:e['entry_id'] for e in entries}
        ranked=sorted([{'ledger_id':i,'entry_id':entry_by_id[i],'cues':c,'metrics':m} for i,_,m,c,_ in results if c],key=lambda r:(-len(r['cues']),r['ledger_id']))
        summary={'run_id':run,'eligible_count':len(vectors),'ineligible_count':len(entries)-len(vectors),'coverage':len(vectors)/len(entries),'dimensions':dims,'embedded_count':len(pending),'cached_count':reused,'missing_fields':{k:sum(not _key(e.get(k)) for e in entries) for k in ('description','vendor','preparer','entity')},'clusters':clusters,'ranked_cues':ranked[:25],'novel_narratives':sorted([{'ledger_id':i,'novelty':m['narrative_novelty']} for i,_,m,_,_ in results if m.get('narrative_novelty') is not None],key=lambda r:(-r['novelty'],r['ledger_id']))[:25], 'retrieval':{'method':'deterministic_bounded_candidates','exhaustive':False,'candidate_limit':cfg['candidate_limit'],'peer_limit':cfg['peer_limit'],'training_limit':cfg['training_limit'],'tie_break':'score_desc_then_ledger_id'},'runtime_seconds':time.time()-started,'peak_python_bytes':tracemalloc.get_traced_memory()[1], 'limitations':[LIMITATION,'Peak allocation excludes Ollama/native memory. Candidate retrieval is bounded and approximate.']}
        store.conn.execute("UPDATE semantic_runs SET completed_at=?,status='complete',provenance_json=?,summary_json=?,limitation_note=? WHERE id=?",(time.time(),_json(provenance),_json(summary),LIMITATION,run))
        store.log(actor,'semantic_profile','semantic_run',run,{'population_hash':fingerprint,'model':model,'digest':identity['digest']}); store.conn.commit()
        return get_semantic_profile(store,run)
    except Exception as exc:
        store.conn.rollback()
        store.conn.execute("UPDATE semantic_runs SET completed_at=?,status='failed',limitation_note=? WHERE id=?",(time.time(),f'{type(exc).__name__}: {str(exc)[:500]}',run)); store.conn.commit()
        raise
    finally:
        if tracing: tracemalloc.stop()


def _positive(value,name):
    if isinstance(value,bool) or not isinstance(value,int) or value<=0: raise ValueError(name+' must be a positive integer')


def _analysis_components(store, run_id, ledger_id):
    """Components for a linked analysis run: snapshot first, legacy exception fallback, else unavailable."""
    row = store.conn.execute('SELECT components_json FROM analysis_signal_results WHERE run_id=? AND ledger_id=?', (run_id, ledger_id)).fetchone()
    if row: return json.loads(row['components_json']), 'analysis_snapshot'
    for a in store.conn.execute("SELECT id,configuration FROM model_runs WHERE status='complete' ORDER BY id DESC"):
        if json.loads(a['configuration']).get('semantic',{}).get('run_id')!=run_id: continue
        ex = store.conn.execute('SELECT evidence_json FROM exceptions WHERE run_id=? AND ledger_id=?', (a['id'], ledger_id)).fetchone()
        if ex:
            components = json.loads(ex['evidence_json']).get('signal_components')
            if components is not None: return components, 'legacy_exception'
    return None, 'unavailable'


def get_semantic_profile(store,run_id=None):
    if run_id is not None: _positive(run_id,'run')
    row=store.conn.execute('SELECT * FROM semantic_runs WHERE id=?',(run_id,)).fetchone() if run_id else store.conn.execute("SELECT * FROM semantic_runs WHERE status='complete' ORDER BY id DESC LIMIT 1").fetchone()
    if not row: raise LookupError('semantic run not found')
    result=dict(row); result['run_id']=result.pop('id')
    for k in ('configuration','provenance','summary'): result[k]=json.loads(result.pop(k+'_json'))
    result['stale']=result['population_hash']!=population_hash(store)
    return result


def semantic_investigate(store,run_id,ledger_id):
    _positive(ledger_id,'ledger_id'); run=get_semantic_profile(store,run_id)
    if run['status']!='complete': raise ValueError('semantic run is not complete')
    r=store.conn.execute('SELECT * FROM semantic_results WHERE run_id=? AND ledger_id=?',(run_id,ledger_id)).fetchone()
    if not r: raise LookupError('ledger line not in semantic run')
    evidence=json.loads(r['evidence_json'])
    other=[]
    for a in store.conn.execute('SELECT id,configuration FROM model_runs WHERE status=? ORDER BY id DESC',('complete',)):
        if json.loads(a['configuration']).get('semantic',{}).get('run_id')!=run_id: continue
        ex=store.conn.execute('SELECT reasons_json,evidence_json FROM exceptions WHERE run_id=? AND ledger_id=?',(a['id'],ledger_id)).fetchone()
        components,source=_analysis_components(store,a['id'],ledger_id)
        other.append({'analysis_run_id':a['id'],'reasons':json.loads(ex['reasons_json']) if ex else [],
                      'components':components,'components_source':source})
    return {'run_id':run_id,'ledger_id':ledger_id,'stale':run['stale'],'entry':evidence['entry'],'cluster_id':r['cluster_id'],'metrics':json.loads(r['metrics_json']),'cues':json.loads(r['cues_json']),'evidence':evidence,'other_signals':other,'provenance':run['provenance']}
