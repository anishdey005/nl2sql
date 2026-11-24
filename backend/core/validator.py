"""
SQL Validator, AST Security Guardrails & Self-Correction Engine.
Uses sqlglot for dialect-aware AST parsing and schema safety enforcement.
"""

import os
import re
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
import sqlglot
from sqlglot import exp

from backend.core.catalog import TABLE_METADATA, DB_PATH

DANGEROUS_EXPRESSIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.Create,
    exp.Command,
)

FORBIDDEN_KEYWORDS = [
    "drop ", "delete ", "insert ", "update ", "alter ", "create ",
    "truncate ", "attach ", "detach ", "pragma ", "exec ", "grant ", "revoke "
]


class SQLValidationError(Exception):
    """Raised when SQL fails security, schema, or syntax validation."""
    pass


class SQLValidator:
    """Validates SQL safety, structure, and database execution."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.valid_tables = set(TABLE_METADATA.keys())

    def sanitize_sql_text(self, sql: str) -> str:
        """Strips markdown code blocks, comments, and trailing semicolons."""
        cleaned = sql.strip()
        # Strip ```sql ... ```
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:sql)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        # Strip single-line comments and trailing semicolons
        cleaned = re.sub(r"--.*$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip().rstrip(";")
        return cleaned

    def validate_safety_and_ast(self, sql: str) -> Tuple[bool, Optional[str], Optional[exp.Expression]]:
        """
        Parses SQL AST using sqlglot and enforces read-only safety rules.
        Returns (is_valid, error_message, parsed_ast).
        """
        sql_clean = self.sanitize_sql_text(sql)

        # 1. Quick regex check for dangerous commands
        lower_sql = f" {sql_clean.lower()} "
        for kw in FORBIDDEN_KEYWORDS:
            if kw in lower_sql:
                return False, f"Dangerous command forbidden by security guardrails: '{kw.strip().upper()}'", None

        # 2. Parse AST with sqlglot (SQLite dialect)
        try:
            expressions = sqlglot.parse(sql_clean, read="sqlite")
        except Exception as e:
            return False, f"SQL Syntax Error: {str(e)}", None

        if not expressions or expressions[0] is None:
            return False, "Query is empty or could not be parsed.", None

        if len(expressions) > 1:
            return False, "Multiple SQL statements are not permitted for security reasons.", None

        ast = expressions[0]

        # 3. Disallow destructive AST expressions
        for dangerous_type in DANGEROUS_EXPRESSIONS:
            if ast.find(dangerous_type):
                return False, f"Disallowed operation type '{dangerous_type.__name__}'. Only read-only SELECT queries are allowed.", None

        # Must be a Select or CTE (With) query
        if not isinstance(ast, (exp.Select, exp.Union)) and not ast.find(exp.Select):
            return False, "Only SELECT queries are allowed.", None

        # 4. Verify all referenced tables exist in catalog
        tables_in_query = [t.name.lower() for t in ast.find_all(exp.Table)]
        for tbl in tables_in_query:
            if tbl and tbl not in self.valid_tables:
                # Check if it's a CTE alias
                ctes = [cte.alias.lower() for cte in ast.find_all(exp.CTE) if cte.alias]
                if tbl not in ctes:
                    return False, f"Unknown table '{tbl}'. Valid tables are: {', '.join(sorted(list(self.valid_tables)))}", None

        return True, None, ast

    def enforce_row_limit(self, sql: str, default_limit: int = 200) -> str:
        """Injects a LIMIT clause if one is not present to prevent unbounded UI loads."""
        sql_clean = self.sanitize_sql_text(sql)
        try:
            ast = sqlglot.parse_one(sql_clean, read="sqlite")
            if isinstance(ast, exp.Select) and not ast.args.get("limit"):
                ast = ast.limit(default_limit)
                return ast.sql(dialect="sqlite")
        except Exception:
            pass
        
        # Fallback regex if AST rewrite fails
        if not re.search(r"\blimit\s+\d+\b", sql_clean, flags=re.IGNORECASE):
            return f"{sql_clean} LIMIT {default_limit}"
        return sql_clean

    def execute_query(
        self,
        sql: str,
        max_rows: int = 200,
        timeout_sec: float = 5.0
    ) -> Dict[str, Any]:
        """
        Executes query safely against SQLite database and returns structured results.
        Enforces read-only connection mode and query limits.
        """
        # 1. AST & Guardrail Validation
        is_valid, error_msg, _ = self.validate_safety_and_ast(sql)
        if not is_valid:
            return {
                "success": False,
                "error": error_msg,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "sanitized_sql": sql,
            }

        # 2. Limit enforcement
        final_sql = self.enforce_row_limit(sql, default_limit=max_rows)

        # 3. Isolated Read-Only Database Execution
        # Open via sqlite3 URI mode with ?mode=ro for kernel-level read-only guarantee
        db_uri = f"file:{os.path.abspath(self.db_path)}?mode=ro"
        try:
            conn = sqlite3.connect(db_uri, uri=True, timeout=timeout_sec)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(final_sql)
            rows_raw = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = [dict(row) for row in rows_raw]
            conn.close()

            return {
                "success": True,
                "error": None,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "sanitized_sql": final_sql,
            }
        except sqlite3.OperationalError as e:
            return {
                "success": False,
                "error": f"SQLite Execution Error: {str(e)}",
                "columns": [],
                "rows": [],
                "row_count": 0,
                "sanitized_sql": final_sql,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Database Error: {str(e)}",
                "columns": [],
                "rows": [],
                "row_count": 0,
                "sanitized_sql": final_sql,
            }


# Global validator instance
validator = SQLValidator()
