#!/usr/bin/env python3
"""Local journal-entry analytics entry point."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from audit_analytics.cli import main

if __name__ == "__main__":
    main()
