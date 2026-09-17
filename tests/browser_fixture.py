"""Temporary synthetic review server for manual/Playwright rendering checks.
Run: PYTHONPATH=src python3 -u tests/browser_fixture.py
"""
import tempfile
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from audit_analytics.store import Store
from audit_analytics.importer import import_gl, import_coa
from audit_analytics.semantic_risk import semantic_profile
from audit_analytics.analytics import analyze
from audit_analytics import server


def main():
    with tempfile.TemporaryDirectory() as directory:
        db = str(Path(directory) / 'browser.db')
        store = Store(db)
        store.conn.execute("INSERT INTO engagement VALUES(1,'Synthetic browser verification','2025-01-01','2025-12-31',0)")
        store.add_user('reviewer', 'manager'); store.conn.commit()
        import_gl(store, 'examples/semantic/ledger.csv')
        import_coa(store, 'examples/semantic/coa.csv')
        store.conn.execute('UPDATE imports SET acknowledged_at=1'); store.conn.commit()
        def embed(texts):
            return [[1.,0.,0.,0.] if 'repair' in t.lower() else [0.,1.,0.,0.] if any(w in t.lower() for w in ('fees','advisory')) else [0.,0.,1.,0.] if 'payroll' in t.lower() else [0.,0.,0.,1.] for t in texts]
        with patch('audit_analytics.semantic_risk.LocalEmbedder.identity', return_value={'digest':'browser-fixed-vectors'}), patch('audit_analytics.semantic_risk.LocalEmbedder.embed', side_effect=embed):
            profile = semantic_profile(store, actor='reviewer')
        analyze(store, 'reviewer', False, profile['run_id'])
        store.close()
        def factory(address, handler):
            http = ThreadingHTTPServer(('127.0.0.1', 0), handler)
            print(f'BROWSER_URL=http://127.0.0.1:{http.server_port}', flush=True)
            return http
        with patch.object(server, 'ThreadingHTTPServer', side_effect=factory):
            server.serve(db, 0)


if __name__ == '__main__':
    main()
