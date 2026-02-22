from backend.app.ai_agent.infrastructure.sql_safety import validate_sql_is_safe
from backend.app.ai_agent.application.errors import AnalyticsError


def test_safe_select_passes() -> None:
    validate_sql_is_safe("SELECT count(*) FROM ticket_results WHERE 1=1 LIMIT :limit")


def test_non_select_rejected() -> None:
    try:
        validate_sql_is_safe("DELETE FROM ticket_results")
        assert False, "Expected AnalyticsError"
    except AnalyticsError as exc:
        assert exc.code == "sql_not_select"


def test_multi_statement_rejected() -> None:
    try:
        validate_sql_is_safe("SELECT * FROM ticket_results; DROP TABLE ticket_results")
        assert False, "Expected AnalyticsError"
    except AnalyticsError as exc:
        assert exc.code == "sql_multi_statement"
