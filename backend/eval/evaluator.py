"""
Automated Evaluation & Benchmark Suite for NL-to-SQL Engine.
Measures SQL Validity Rate (>95%), Execution Accuracy (~80%), and Sub-second Latency.
"""

import json
import os
import sys
import sqlite3
import time
from typing import Dict, Any, List, Optional, Tuple

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.core.engine import engine, NL2SQLEngine
from backend.core.validator import validator, SQLValidator
from backend.core.catalog import DB_PATH

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARK_FILE = os.path.join(CURRENT_DIR, "benchmark_queries.json")
REPORT_FILE = os.path.join(CURRENT_DIR, "benchmark_report.json")


def normalize_value(val: Any) -> Any:
    """Normalizes cell values for fuzzy comparison (floats, strings, None)."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return round(float(val), 2)
    s = str(val).strip().lower()
    return s


def compare_result_sets(actual_rows: List[Dict[str, Any]], expected_rows: List[Dict[str, Any]]) -> bool:
    """
    Compares two query result sets for semantic execution equality:
    1. Compares length (row count).
    2. Compares multiset of rows independent of column alias names.
    """
    if len(actual_rows) != len(expected_rows):
        return False
    if len(actual_rows) == 0:
        return True

    # Extract sorted tuples of values per row
    def row_to_tuple(row_dict: Dict[str, Any]) -> Tuple:
        return tuple(sorted([normalize_value(v) for v in row_dict.values()], key=lambda x: str(x)))

    actual_tuples = sorted([row_to_tuple(r) for r in actual_rows], key=lambda x: str(x))
    expected_tuples = sorted([row_to_tuple(r) for r in expected_rows], key=lambda x: str(x))

    return actual_tuples == expected_tuples


class BenchmarkEvaluator:
    """Orchestrates benchmark evaluation runs and metric calculations."""

    def __init__(self, db_path: str = DB_PATH, benchmark_path: str = BENCHMARK_FILE):
        self.db_path = db_path
        self.benchmark_path = benchmark_path
        self.engine = engine
        self.validator = validator
        self.queries = self._load_queries()

    def _load_queries(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.benchmark_path):
            return []
        with open(self.benchmark_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def execute_ground_truth(self, sql: str) -> List[Dict[str, Any]]:
        res = self.validator.execute_query(sql, max_rows=500)
        return res.get("rows", [])

    def run_benchmark(
        self,
        api_key: Optional[str] = None,
        limit_queries: Optional[int] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        Executes evaluation across test cases and returns comprehensive performance report.
        """
        filtered_queries = self.queries

        if category:
            filtered_queries = [q for q in filtered_queries if q.get("category", "").lower() == category.lower()]
        if difficulty:
            filtered_queries = [q for q in filtered_queries if q.get("difficulty", "").lower() == difficulty.lower()]
        if limit_queries and limit_queries > 0:
            filtered_queries = filtered_queries[:limit_queries]

        total_cases = len(filtered_queries)
        if total_cases == 0:
            return {"error": "No benchmark queries matching criteria"}

        valid_count = 0
        accurate_count = 0
        total_latency_ms = 0.0
        results_breakdown = []

        by_difficulty = {"Easy": {"total": 0, "valid": 0, "accurate": 0},
                         "Medium": {"total": 0, "valid": 0, "accurate": 0},
                         "Hard": {"total": 0, "valid": 0, "accurate": 0}}

        start_time = time.time()

        for idx, item in enumerate(filtered_queries):
            qid = item["id"]
            question = item["question"]
            diff = item.get("difficulty", "Medium")
            gt_sql = item["ground_truth_sql"]

            # Run engine
            pred = self.engine.process_query(question, api_key=api_key)
            is_valid = pred["success"]
            candidate_sql = pred["sql"]
            latency = pred["timing"]["total_ms"]
            total_latency_ms += latency

            # Ground truth results
            gt_rows = self.execute_ground_truth(gt_sql)
            candidate_rows = pred["rows"]

            is_accurate = False
            if is_valid:
                valid_count += 1
                is_accurate = compare_result_sets(candidate_rows, gt_rows)
                if is_accurate:
                    accurate_count += 1

            # Difficulty tracking
            if diff in by_difficulty:
                by_difficulty[diff]["total"] += 1
                if is_valid:
                    by_difficulty[diff]["valid"] += 1
                if is_accurate:
                    by_difficulty[diff]["accurate"] += 1

            case_summary = {
                "id": qid,
                "question": question,
                "difficulty": diff,
                "category": item.get("category", "General"),
                "is_valid": is_valid,
                "is_accurate": is_accurate,
                "latency_ms": round(latency, 1),
                "generated_sql": candidate_sql,
                "ground_truth_sql": gt_sql,
                "error": pred.get("error"),
                "correction_attempts": pred.get("correction_attempts", 0),
            }
            results_breakdown.append(case_summary)

            if progress_callback:
                progress_callback(idx + 1, total_cases, case_summary)

        wall_clock_time = time.time() - start_time
        validity_rate = round((valid_count / total_cases) * 100.0, 1)
        execution_accuracy = round((accurate_count / total_cases) * 100.0, 1)
        avg_latency = round(total_latency_ms / total_cases, 1)

        summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_queries": total_cases,
            "valid_queries": valid_count,
            "accurate_queries": accurate_count,
            "validity_rate_pct": validity_rate,
            "execution_accuracy_pct": execution_accuracy,
            "average_latency_ms": avg_latency,
            "is_sub_second": avg_latency < 1000.0,
            "wall_clock_seconds": round(wall_clock_time, 2),
            "difficulty_breakdown": {
                d: {
                    "total": by_difficulty[d]["total"],
                    "valid_pct": round(by_difficulty[d]["valid"] / max(by_difficulty[d]["total"], 1) * 100.0, 1),
                    "accurate_pct": round(by_difficulty[d]["accurate"] / max(by_difficulty[d]["total"], 1) * 100.0, 1),
                }
                for d in by_difficulty if by_difficulty[d]["total"] > 0
            },
            "results": results_breakdown,
        }

        # Save report
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return summary


# Global evaluator instance
evaluator = BenchmarkEvaluator()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run NL2SQL Benchmark Evaluation")
    parser.add_argument("--limit", type=int, default=15, help="Number of queries to run (default: 15, or 105 for full)")
    parser.add_argument("--key", type=str, default=None, help="Groq API Key")
    args = parser.parse_args()

    print(f"Starting NL2SQL Benchmark Suite ({args.limit} test cases)...")
    res = evaluator.run_benchmark(api_key=args.key, limit_queries=args.limit)
    print("\n================ BENCHMARK RESULTS ================")
    print(f"Total Evaluated        : {res['total_queries']}")
    print(f"SQL Validity Rate      : {res['validity_rate_pct']}%  (Target: >95%)")
    print(f"Execution Accuracy     : {res['execution_accuracy_pct']}%  (Target: ~80%)")
    print(f"Average Latency        : {res['average_latency_ms']} ms  (Sub-second: {res['is_sub_second']})")
    print("====================================================")
