"""Regression checks for semantic schema/import and opt-in evidence aggregation."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audit_analytics.store import Store
from audit_analytics.importer import import_gl, import_coa, preview_gl
from audit_analytics.connectors import DemoCsvConnector


class SemanticImportTest(unittest.TestCase):
    def test_vendor_alias_coa_and_repeatable_migration(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gl = root / 'gl.csv'
            gl.write_text('entry_id,posting_date,account_code,amount,description,supplier_name\nJ1,2025-01-02,005,123,Repair pump,001 Vendor\n')
            coa = root / 'coa.csv'
            coa.write_text('account_code,account_name,account_type\n005,Repairs,Expense\n')
            s = Store(str(root / 'audit.db'))
            self.assertEqual(preview_gl(str(gl))['mapping']['vendor'], 'supplier_name')
            self.assertEqual(DemoCsvConnector().extract(str(gl))[0]['vendor'], '001 Vendor')
            import_gl(s, str(gl)); import_coa(s, str(coa))
            self.assertEqual(s.conn.execute('SELECT vendor FROM ledger_entries').fetchone()[0], '001 Vendor')
            self.assertEqual(s.conn.execute('SELECT account_name FROM coa WHERE account_code=?', ('005',)).fetchone()[0], 'Repairs')
            s.close()
            s = Store(str(root / 'audit.db'))
            self.assertEqual(s.conn.execute('SELECT count(*) FROM ledger_entries').fetchone()[0], 1)
            self.assertEqual([r[1] for r in s.conn.execute('PRAGMA table_info(ledger_entries)')].count('vendor'), 1)
            for table in ('semantic_runs', 'semantic_profiles', 'semantic_results'):
                self.assertEqual(s.conn.execute(f'SELECT count(*) FROM {table}').fetchone()[0], 0)
            s.close()


class SemanticWorkflowTest(unittest.TestCase):
    def test_fixture_profile_aggregation_export_and_http(self):
        import threading
        import urllib.request
        import urllib.error
        from http.server import ThreadingHTTPServer
        from audit_analytics.semantic_risk import semantic_profile, semantic_investigate
        from audit_analytics.semantic_evaluation import evaluate_semantic
        from audit_analytics.analytics import analyze
        from audit_analytics.reports import export_workpaper
        from audit_analytics import server
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); store=Store(str(root/'audit.db'))
            store.conn.execute("INSERT INTO engagement VALUES(1,'Fixture','2025-01-01','2025-12-31',0)")
            store.add_user('owner','manager');store.conn.commit()
            import_gl(store,'examples/semantic/ledger.csv');import_coa(store,'examples/semantic/coa.csv')
            store.conn.execute('UPDATE imports SET acknowledged_at=1');store.conn.commit()
            def embed(texts):
                return [[1.,0.,0.,0.] if 'repair' in t.lower() else [0.,1.,0.,0.] if any(w in t.lower() for w in ('fees','advisory')) else [0.,0.,1.,0.] if 'payroll' in t.lower() else [0.,0.,0.,1.] for t in texts]
            with patch('audit_analytics.semantic_risk.LocalEmbedder.identity',return_value={'digest':'fixed-fixture'}), patch('audit_analytics.semantic_risk.LocalEmbedder.embed',side_effect=embed):
                profile=semantic_profile(store,actor='owner')
            rid=profile['run_id']; lid=store.conn.execute("SELECT id FROM ledger_entries WHERE entry_id='A1'").fetchone()[0]
            inv=semantic_investigate(store,rid,lid)
            self.assertIn('semantic_account_mismatch',inv['cues'])
            v=store.conn.execute("SELECT id FROM ledger_entries WHERE entry_id='V1'").fetchone()[0]
            self.assertIn('semantic_vendor_shift',semantic_investigate(store,rid,v)['cues'])
            baseline=analyze(store,'owner',False)
            combined=analyze(store,'owner',False,rid)
            # Zero-cue entries keep their signal snapshot even without an exception row.
            zero=[r['ledger_id'] for r in store.conn.execute('SELECT * FROM exceptions WHERE run_id=?',(combined,))]+[
                  r[0] for r in store.conn.execute('SELECT id FROM ledger_entries ORDER BY id')]
            zero_cue=[l for l in zero if not store.conn.execute('SELECT COUNT(*) FROM exceptions WHERE run_id=? AND ledger_id=?',(combined,l)).fetchone()[0]]
            self.assertTrue(zero_cue,'fixture should contain entries with no cues')
            for l in zero_cue:
                snap=store.conn.execute('SELECT components_json FROM analysis_signal_results WHERE run_id=? AND ledger_id=?',(combined,l)).fetchone()
                self.assertIsNotNone(snap,f'snapshot missing for zero-cue ledger {l}')
                comps=json.loads(snap[0])
                self.assertEqual(comps['semantic_contribution'],0)
                self.assertEqual(comps['semantic_reasons'],[])
            self.assertEqual(store.conn.execute('SELECT COUNT(*) FROM analysis_signal_results WHERE run_id=?',(combined,)).fetchone()[0],
                             store.conn.execute('SELECT COUNT(*) FROM ledger_entries').fetchone()[0])
            self.assertEqual(store.conn.execute('SELECT COUNT(*) FROM analysis_signal_results WHERE run_id=?',(baseline,)).fetchone()[0],0)
            # Investigation returns snapshot-backed components for a zero-cue entry.
            inv0=semantic_investigate(store,rid,zero_cue[0])
            sig0=inv0['other_signals'][0]
            self.assertEqual(sig0['components_source'],'analysis_snapshot')
            self.assertEqual(sig0['components']['semantic_contribution'],0)
            self.assertEqual(sig0['analysis_run_id'],combined)
            scores={r['ledger_id']:r['risk_score'] for r in store.conn.execute('SELECT * FROM exceptions WHERE run_id=?',(baseline,))}
            for row in store.conn.execute('SELECT * FROM exceptions WHERE run_id=?',(combined,)):
                evidence=json.loads(row['evidence_json'])
                addition=evidence['signal_components']['semantic_contribution']
                self.assertEqual(row['risk_score'],min(100,scores.get(row['ledger_id'],0)+addition))
                self.assertIn(addition,(0,20))
            evaluation=evaluate_semantic(store,rid,'examples/semantic/labels.csv','owner')
            self.assertEqual(evaluation['mismatch']['recall'],1.0)
            _,manifest,_=export_workpaper(store,str(root/'workpaper.csv'))
            self.assertTrue(json.loads(manifest.read_text())['semantic_runs'])
            captured=[]
            def make_server(address,handler):
                http=ThreadingHTTPServer(('127.0.0.1',0),handler)
                captured.append((http,http.serve_forever));http.serve_forever=lambda:None
                return http
            with patch.object(server,'ThreadingHTTPServer',side_effect=make_server):
                server.serve(str(store.path),0)
            http,serve=captured[0]; thread=threading.Thread(target=serve,daemon=True);thread.start()
            base=f'http://127.0.0.1:{http.server_port}'
            try:
                def get(path):
                    with urllib.request.urlopen(base+path) as response:return json.load(response)
                profile=get('/api/semantic-profile')
                self.assertEqual(profile['run_id'],rid)
                for key in ('status','started_at','completed_at','population_count','population_hash','stale','configuration','provenance','summary','limitation_note','available_runs'):
                    self.assertIn(key,profile)
                self.assertEqual(profile['provenance']['digest'],'fixed-fixture')
                investigation=get(f'/api/semantic-investigation?run={rid}&ledger_id={lid}')
                self.assertEqual(investigation['entry']['entry_id'],'A1')
                for key in ('run_id','ledger_id','stale','entry','cluster_id','metrics','cues','evidence','other_signals','provenance'):
                    self.assertIn(key,investigation)
                self.assertEqual(investigation['other_signals'][0]['components_source'],'analysis_snapshot')
                for key in ('normal_peers','alternative_matches','related_population','comparisons','suggested_evidence','limitations'):
                    self.assertIn(key,investigation['evidence'])
                self.assertTrue(all(x['run_id']==combined for x in get(f'/api/exceptions?run={combined}')['rows']))
                for path,status in [('/api/semantic-profile?run=-1',400),('/api/semantic-profile?run=999',404),('/api/semantic-investigation?run=1&ledger_id=0',400),('/api/exceptions?run=no',400)]:
                    with self.assertRaises(urllib.error.HTTPError) as exc:get(path)
                    self.assertEqual(exc.exception.code,status)
                store.conn.execute("UPDATE ledger_entries SET description='changed' WHERE id=?",(lid,));store.conn.commit()
                self.assertTrue(get('/api/semantic-profile')['stale'])
                with self.assertRaisesRegex(ValueError,'stale'):analyze(store,'owner',False,rid)
                self.assertEqual(semantic_investigate(store,rid,lid)['entry']['description'],'Strategic advisory engagement')
            finally:
                http.shutdown();thread.join();http.server_close();store.close()


if __name__ == '__main__':
    unittest.main()
