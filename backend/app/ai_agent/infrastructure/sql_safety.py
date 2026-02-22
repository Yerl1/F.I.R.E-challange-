from __future__ import annotations

import re

from ..application.errors import AnalyticsError


ALLOWED_TABLE = "ticket_results"
FORBIDDEN_SQL = (
    "insert ",
    "update ",
    "delete ",
    "drop ",
    "alter ",
    "create ",
    "truncate ",
    "grant ",
    "revoke ",
)


def validate_sql_is_safe(sql: str) -> None:
    normalized = re.sub(r"\s+", " ", sql.strip().lower())
    if not normalized.startswith("select "):
        raise AnalyticsError("sql_not_select", "Only SELECT queries are allowed")
    if ";" in normalized:
        raise AnalyticsError("sql_multi_statement", "Multiple SQL statements are not allowed")
    if f" from {ALLOWED_TABLE} " not in f" {normalized} ":
        raise AnalyticsError("sql_disallowed_table", "Query uses disallowed table")
    for token in FORBIDDEN_SQL:
        if token in normalized:
            raise AnalyticsError("sql_forbidden_keyword", f"Forbidden SQL keyword detected: {token.strip()}")
