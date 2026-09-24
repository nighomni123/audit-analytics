#!/usr/bin/env python3
"""Source-checkout entry point for the audit-analytics CLI."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from audit_analytics.cli import main


if __name__ == "__main__":
    main()
