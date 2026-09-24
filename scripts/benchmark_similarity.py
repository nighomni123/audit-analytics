"""Measure bounded similarity retrieval at fixed synthetic population sizes."""
from __future__ import annotations

import argparse
import array
import json
import tempfile
import time
import tracemalloc
from pathlib import Path
from unittest.mock import patch

from audit_analytics.semantic import similar_transactions
from audit_analytics.store import Store


def run_size(size: int, dimensions: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="audit-benchmark-") as directory:
        store = Store(str(Path(directory) / "benchmark.db"))
        store.conn.execute("INSERT INTO imports(kind,original_name,evidence_path,sha256,imported_at,accepted_rows,rejected_rows) VALUES('gl','synthetic.csv','synthetic.csv','synthetic',0,?,0)", (size,))
        import_id = store.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        entries = []
        embeddings = []
        vector = array.array("f", [1.0] + [0.0] * (dimensions - 1)).tobytes()
        for index in range(size):
            entries.append((import_id, f"J{index}", "2026-03-31", "6000", 100, 0, 100, f"manual tax provision {index}", index, f"h{index}", "{}"))
            embeddings.append((index + 1, "synthetic", dimensions, f"t{index}", vector, 1))
        store.conn.executemany(
            """INSERT INTO ledger_entries(import_id,entry_id,posting_date,account_code,debit,credit,signed_amount,description,source_row,source_hash,raw_json)
               VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            entries,
        )
        store.conn.executemany("INSERT INTO ledger_embeddings VALUES(?,?,?,?,?,?)", embeddings)
        store.conn.commit()
        query_vector = array.array("f", [1.0] + [0.0] * (dimensions - 1))
        tracemalloc.start()
        started = time.perf_counter()
        with patch("audit_analytics.semantic.LocalEmbedder.embed", return_value=[query_vector]):
            results = similar_transactions(store, "manual tax provision", limit=25, model="synthetic")
        elapsed = time.perf_counter() - started
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        store.close()
        return {"entries": size, "dimensions": dimensions, "seconds": round(elapsed, 3), "peak_python_bytes": peak, "results": len(results)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", default="10000,50000,100000")
    parser.add_argument("--dimensions", type=int, default=64)
    args = parser.parse_args()
    sizes = [int(value) for value in args.sizes.split(",") if value.strip()]
    if args.dimensions < 2 or args.dimensions > 1024:
        parser.error("dimensions must be from 2 to 1024")
    print(json.dumps([run_size(size, args.dimensions) for size in sizes], indent=2))


if __name__ == "__main__":
    main()
