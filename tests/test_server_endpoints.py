"""Lightweight import/route-presence check for server.py new endpoints."""
import inspect
import unittest

import audit_analytics.server as srv

ROUTES = ("/preview-gl", "/mappings", "/compare-runs", "/account-taxonomy", "/bank", "/reviews", "/models")


class TestServerEndpoints(unittest.TestCase):
    def test_server_imports(self):
        self.assertTrue(hasattr(srv, "serve"))
        self.assertTrue(callable(srv.preview_gl))
        self.assertTrue(callable(srv.compare_runs))
        self.assertTrue(callable(srv.list_models))

    def test_new_routes_registered(self):
        src = inspect.getsource(srv.serve)
        for route in ROUTES:
            self.assertIn(route, src)
        self.assertIn("127.0.0.1", src)


if __name__ == "__main__":
    unittest.main()
