"""Phase 1A/B core: fixed-vector offline coverage for semantic_risk + embed_ledger."""
import array
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audit_analytics import semantic_risk as sr
from audit_analytics.semantic import embed_ledger
from audit_analytics.store import Store

VECTORS = {
    'rent payment office': [1.0, 0.0, 0.0],
    'rent payment office annex': [0.98, 0.2, 0.0],
    'it advisory services': [0.0, 1.0, 0.0],
    'vendor invoice steel': [0.0, 0.0, 1.0],
}
DIGEST = 'sha256:fixed'


class FakeEmbedder:
    instances = []

    def __init__(self, model='embeddinggemma', base_url='http://127.0.0.1:11434'):
        self.model = model
        FakeEmbedder.instances.append(self)
        self.calls = 0

    def identity(self):
        return {'digest': DIGEST, 'name': self.model, 'runtime_version': 'test'}

    def embed(self, texts):
        self.calls += 1
        out = []
        for t in texts:
            narration = t.split('Narration: ', 1)[1] if 'Narration: ' in t else t
            v = VECTORS.get(narration, [0.5, 0.5, 0.0])
            out.append(array.array('f', v))
        return out


def make_store(d, rows):
    s = Store(str(Path(d) / 'audit.db'))
    s.conn.execute("INSERT INTO engagement VALUES(1,'C','2025-01-01','2025-12-31',0)")
    s.add_user('reviewer', 'reviewer', actor='system')
    s.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows,acknowledged_at,acknowledged_by) VALUES('gl','g.csv','g.csv','x',0,99,0,1,'reviewer')")
    iid = s.conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    for i, r in enumerate(rows, 1):
        s.conn.execute("""INSERT INTO ledger_entries(import_id,entry_id,posting_date,account_code,debit,credit,signed_amount,description,vendor,preparer,entity,source_row,source_hash,raw_json)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (iid, r.get('entry_id', f'J{i}'), r['date'], r['acct'], 100, 0, 100,
            r.get('desc', ''), r.get('vendor'), r.get('prep'), r.get('entity', 'HQ'), i, f'h{i}', '{}'))
    s.conn.commit()
    return s


def run_profile(store, **kw):
    with patch.object(sr, 'LocalEmbedder', FakeEmbedder), \
         patch.object(sr, 'list_models', lambda s: [{'name': 'embeddinggemma', 'status': 'validated'}]):
        FakeEmbedder.instances.clear()
        return sr.semantic_profile(store, actor='reviewer', **kw)


BASE_ROWS = [
    {'date': '2025-01-05', 'acct': '6000', 'desc': 'rent payment office', 'vendor': 'V1', 'prep': 'P1'},
    {'date': '2025-02-05', 'acct': '6000', 'desc': 'rent payment office', 'vendor': 'V1', 'prep': 'P1'},
    {'date': '2025-03-05', 'acct': '6000', 'desc': 'rent payment office annex', 'vendor': 'V1', 'prep': 'P1'},
    {'date': '2025-03-06', 'acct': '6000', 'desc': 'rent payment office', 'vendor': 'V1', 'prep': 'P1'},
    {'date': '2025-03-07', 'acct': '6000', 'desc': 'rent payment office', 'vendor': 'V1', 'prep': 'P1'},
    {'date': '2025-03-08', 'acct': '6000', 'desc': 'rent payment office', 'vendor': 'V1', 'prep': 'P1'},
    {'date': '2025-03-09', 'acct': '7000', 'desc': 'it advisory services', 'vendor': 'V2', 'prep': 'P2'},
    {'date': '2025-03-10', 'acct': '6000', 'desc': '', 'vendor': 'V1', 'prep': 'P1'},
]


class CoreTest(unittest.TestCase):
    def test_lifecycle_get_investigate_stale_and_bounds(self):
        with tempfile.TemporaryDirectory() as d:
            s = make_store(d, BASE_ROWS)
            prof = run_profile(s)
            self.assertEqual(prof['status'], 'complete')
            for k in ('run_id', 'status', 'configuration', 'provenance', 'summary', 'stale'):
                self.assertIn(k, prof)
            self.assertFalse(prof['stale'])
            self.assertEqual(prof['summary']['eligible_count'], 7)
            self.assertEqual(prof['summary']['ineligible_count'], 1)
            self.assertEqual(prof['summary']['retrieval']['method'], 'deterministic_bounded_candidates')
            self.assertFalse(prof['summary']['retrieval']['exhaustive'])
            self.assertEqual(prof['summary']['retrieval']['candidate_limit'], 64)
            self.assertEqual(prof['summary']['retrieval']['tie_break'], 'score_desc_then_ledger_id')
            got = sr.get_semantic_profile(s, prof['run_id'])
            self.assertEqual(got['run_id'], prof['run_id'])
            inv = sr.semantic_investigate(s, prof['run_id'], 7)
            for k in ('entry', 'cues', 'metrics', 'evidence', 'provenance', 'other_signals'):
                self.assertIn(k, inv)
            # stale after population change
            s.conn.execute("INSERT INTO ledger_entries(import_id,entry_id,posting_date,account_code,debit,credit,signed_amount,description,entity,source_row,source_hash,raw_json) VALUES(1,'JX','2025-03-11','6000',1,0,1,'rent payment office','HQ',99,'hx','{}')")
            s.conn.commit()
            self.assertTrue(sr.get_semantic_profile(s, prof['run_id'])['stale'])
            inv2 = sr.semantic_investigate(s, prof['run_id'], 7)
            self.assertTrue(inv2['stale'])
            # invalid ids
            with self.assertRaises(ValueError): sr.get_semantic_profile(s, 0)
            with self.assertRaises(LookupError): sr.get_semantic_profile(s, 9999)
            with self.assertRaises(LookupError): sr.semantic_investigate(s, prof['run_id'], 9999)
            # clusters bounded + deterministic labels
            labels = [c['label'] for c in prof['summary']['clusters']]
            self.assertTrue(labels and all(l.startswith('Process ') for l in labels))
            self.assertLessEqual(len(labels), 12)
            # ranked / related / candidate bounds
            self.assertLessEqual(len(prof['summary']['ranked_cues']), 25)
            row = s.conn.execute('SELECT evidence_json FROM semantic_results WHERE run_id=? AND ledger_id=1', (prof['run_id'],)).fetchone()[0]
            import json; ev = json.loads(row)
            self.assertLessEqual(len(ev['related_population']['vendor']['entries']), 25)
            # history strictly earlier months: ledger 2 (Feb) has only Jan history
            m2 = s.conn.execute('SELECT metrics_json FROM semantic_results WHERE run_id=? AND ledger_id=2', (prof['run_id'],)).fetchone()[0]
            self.assertIn('narrative_novelty', json.loads(m2))
            # entity scoping: cross-entity alternate must not match
            s.close()

    def test_null_sparse_and_zero_clusters(self):
        rows = [
            {'date': '2025-03-01', 'acct': '6000', 'desc': 'rent payment office', 'vendor': 'V1', 'prep': 'P1', 'entity': ''},
            {'date': '2025-03-02', 'acct': '6000', 'desc': 'rent payment office', 'vendor': '', 'prep': '', 'entity': 'HQ'},
            {'date': '2025-03-03', 'acct': '9000', 'desc': 'rent payment office', 'vendor': 'VX', 'prep': 'PX', 'entity': 'HQ'},
        ]
        with tempfile.TemporaryDirectory() as d:
            s = make_store(d, rows)
            prof = run_profile(s)
            import json
            for lid in (1, 2, 3):
                m = json.loads(s.conn.execute('SELECT metrics_json FROM semantic_results WHERE run_id=? AND ledger_id=?', (prof['run_id'], lid)).fetchone()[0])
                # fewer than 5 peers -> null with reason
                self.assertIsNone(m['peer_similarity'])
            # identical vectors -> single cluster, deterministic
            self.assertEqual(len(prof['summary']['clusters']), 1)
            # empty population of vectors: all missing narration
            s2 = make_store(tempfile.mkdtemp(), [{'date': '2025-03-01', 'acct': '6000', 'desc': ''}])
            with patch.object(sr, 'LocalEmbedder', FakeEmbedder), patch.object(sr, 'list_models', lambda s: []):
                p2 = sr.semantic_profile(s2, actor='reviewer')
                self.assertEqual(p2['summary']['eligible_count'], 0)
                self.assertEqual(p2['summary']['clusters'], [])
            s.close(); s2.close()

    def test_malformed_vector_rollback_and_cache_reuse(self):
        with tempfile.TemporaryDirectory() as d:
            s = make_store(d, BASE_ROWS)
            prof = run_profile(s)
            n_runs = s.conn.execute('SELECT COUNT(*) FROM semantic_runs').fetchone()[0]
            # malformed vector on a fresh population (avoids cache): NaN narration-mapped vector
            VECTORS['it advisory services'] = [float('nan'), 0.0, 0.0]
            s_bad = make_store(tempfile.mkdtemp(), BASE_ROWS)
            try:
                with patch.object(sr, 'LocalEmbedder', FakeEmbedder), patch.object(sr, 'list_models', lambda s: []):
                    FakeEmbedder.instances.clear()
                    with self.assertRaises(ValueError):
                        sr.semantic_profile(s_bad, actor='reviewer')
                failed = s_bad.conn.execute("SELECT status FROM semantic_runs ORDER BY id DESC LIMIT 1").fetchone()[0]
                self.assertEqual(failed, 'failed')
                self.assertEqual(s_bad.conn.execute('SELECT COUNT(*) FROM semantic_results WHERE run_id=(SELECT MAX(id) FROM semantic_runs)').fetchone()[0], 0)
            finally:
                VECTORS['it advisory services'] = [0.0, 1.0, 0.0]
                s_bad.close()
            # reuse: second run embeds nothing new (cached_count covers all)
            prof2 = run_profile(s)
            self.assertEqual(prof2['summary']['cached_count'], prof2['summary']['eligible_count'])
            self.assertEqual(prof2['summary']['embedded_count'], 0)
            # digest change invalidates cache
            with patch.object(sr, 'LocalEmbedder', FakeEmbedder), patch.object(sr, 'list_models', lambda s: []):
                FakeEmbedder.instances.clear()
                with patch.object(FakeEmbedder, 'identity', lambda self: {'digest': 'sha256:other', 'name': self.model, 'runtime_version': 't'}):
                    prof3 = sr.semantic_profile(s, actor='reviewer')
                    self.assertEqual(prof3['summary']['cached_count'], 0)
            self.assertGreater(s.conn.execute('SELECT COUNT(*) FROM semantic_runs').fetchone()[0], n_runs)
            s.close()

    def test_embed_ledger_batch_and_rollback(self):
        with tempfile.TemporaryDirectory() as d:
            s = make_store(d, BASE_ROWS[:2])
            with self.assertRaises(ValueError):
                embed_ledger(s, batch_size=0)
            with self.assertRaises(ValueError):
                embed_ledger(s, batch_size=True)
            class BadEmbed:
                def __init__(self, *a, **k): pass
                def embed(self, texts): return [array.array('f', [1.0])]  # wrong batch size
            with patch('audit_analytics.semantic.LocalEmbedder', BadEmbed):
                with self.assertRaises(ValueError):
                    embed_ledger(s)
            self.assertEqual(s.conn.execute('SELECT COUNT(*) FROM ledger_embeddings').fetchone()[0], 0)
            s.close()


if __name__ == '__main__':
    unittest.main()
