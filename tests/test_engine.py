"""
End-to-end Test Suite for NexSQL NL-to-SQL Engine.
Tests database tables, AST validator guardrails, engine execution,
benchmark metrics (~80% accuracy, >95% validity), and API responses.
"""

import os
import sys
import unittest
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.core.catalog import catalog, TABLE_METADATA, DB_PATH
from backend.core.validator import validator
from backend.core.engine import engine
from backend.eval.evaluator import evaluator


class TestDatabaseAndCatalog(unittest.TestCase):
    """Verifies relational database tables and metadata mapping."""

    def test_database_exists_and_connected(self):
        self.assertTrue(os.path.exists(DB_PATH), f"Database missing at {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
        conn.close()
        self.assertGreaterEqual(len(tables), 22, "Expected at least 22 database tables")

    def test_table_row_counts_exceed_1000_records(self):
        counts = catalog.get_table_row_counts()
        total_rows = sum(counts.values())
        print(f"\n[Test] Verified total database records: {total_rows}")
        self.assertGreaterEqual(total_rows, 1000, "Expected at least 1,000 enterprise records")
        for tbl in TABLE_METADATA:
            self.assertIn(tbl, counts)
            self.assertGreater(counts[tbl], 0, f"Table '{tbl}' has 0 rows")

    def test_schema_join_paths(self):
        path = catalog.find_shortest_join_path("customers", "products")
        self.assertIsNotNone(path, "Expected join path between customers and products")
        self.assertGreater(len(path), 0)


class TestSQLValidatorSecurity(unittest.TestCase):
    """Tests security guardrails, AST validation, and read-only enforcement."""

    def test_blocks_drop_table(self):
        res = validator.execute_query("DROP TABLE customers;")
        self.assertFalse(res["success"])
        self.assertIn("forbidden", res["error"].lower())

    def test_blocks_delete(self):
        res = validator.execute_query("DELETE FROM orders WHERE order_id = 1;")
        self.assertFalse(res["success"])
        self.assertIn("forbidden", res["error"].lower())

    def test_blocks_update(self):
        res = validator.execute_query("UPDATE products SET base_price = 0;")
        self.assertFalse(res["success"])
        self.assertIn("forbidden", res["error"].lower())

    def test_blocks_insert(self):
        res = validator.execute_query("INSERT INTO departments (name, code) VALUES ('Hacked', 'HCK');")
        self.assertFalse(res["success"])
        self.assertIn("forbidden", res["error"].lower())

    def test_blocks_unknown_table(self):
        res = validator.execute_query("SELECT * FROM non_existent_table;")
        self.assertFalse(res["success"])
        self.assertIn("unknown table", res["error"].lower())

    def test_enforces_limit_on_unbounded_query(self):
        limited = validator.enforce_row_limit("SELECT * FROM products")
        self.assertIn("LIMIT", limited)


class TestNL2SQLEngine(unittest.TestCase):
    """Tests end-to-end query processing and sub-second execution."""

    def test_process_query_top_customers(self):
        res = engine.process_query("Show top 5 customers by spend")
        self.assertTrue(res["success"], f"Query failed: {res.get('error')}")
        self.assertGreater(len(res["rows"]), 0)
        self.assertIn("sql", res)
        self.assertTrue(res["timing"]["is_sub_second"], "Query execution exceeded 1000ms")
        self.assertIn("explanation", res)

    def test_process_query_low_stock(self):
        res = engine.process_query("Which products are low on stock below their reorder point?")
        self.assertTrue(res["success"], f"Query failed: {res.get('error')}")
        self.assertGreater(len(res["rows"]), 0)

    def test_process_query_monthly_revenue(self):
        res = engine.process_query("Monthly revenue and order count")
        self.assertTrue(res["success"], f"Query failed: {res.get('error')}")
        self.assertIn("visualization", res)


class TestBenchmarkEvaluation(unittest.TestCase):
    """Verifies target benchmark metrics: >95% validity and ~80% execution accuracy."""

    def test_benchmark_runner_metrics(self):
        report = evaluator.run_benchmark(limit_queries=20)
        print(f"\n[Test Benchmark] Evaluated {report['total_queries']} test cases:")
        print(f"  Validity Rate     : {report['validity_rate_pct']}% (Target: >95%)")
        print(f"  Execution Accuracy: {report['execution_accuracy_pct']}% (Target: ~80%)")
        print(f"  Average Latency   : {report['average_latency_ms']} ms (Target: Sub-Second)")

        self.assertGreaterEqual(report["validity_rate_pct"], 95.0, "Validity rate should be >= 95%")
        self.assertGreaterEqual(report["execution_accuracy_pct"], 75.0, "Execution accuracy should be ~80%")
        self.assertTrue(report["is_sub_second"], "Average latency should be sub-second (<1000ms)")


if __name__ == "__main__":
    unittest.main()
