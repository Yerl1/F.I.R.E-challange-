from sqlalchemy import create_engine

from backend.app.ai_agent.domain.analytics_dsl import AnalyticsDSL
from backend.app.ai_agent.infrastructure.sql_compiler import SqlCompiler


def test_distribution_sql_compiles() -> None:
    engine = create_engine("sqlite:///:memory:")
    compiler = SqlCompiler(engine=engine, default_days_range=30, max_rows=500)
    dsl = AnalyticsDSL.model_validate(
        {
            "intent": "distribution",
            "metrics": [{"name": "count", "field": "*", "as": "tickets"}],
            "dimensions": ["city", "ticket_type"],
            "filters": [],
            "time_grain": "null",
            "limit": 100,
            "chart": {"type": "stacked_bar", "x": "city", "y": "tickets", "series": "ticket_type"},
        }
    )
    compiled = compiler.compile(dsl)
    assert "FROM ticket_results" in compiled.sql
    assert "GROUP BY" in compiled.sql
    assert "COUNT(*) AS tickets" in compiled.sql
    assert compiled.params["limit"] == 100


def test_trend_sql_has_time_bucket() -> None:
    engine = create_engine("sqlite:///:memory:")
    compiler = SqlCompiler(engine=engine, default_days_range=30, max_rows=500)
    dsl = AnalyticsDSL.model_validate(
        {
            "intent": "trend",
            "metrics": [{"name": "count", "field": "*", "as": "tickets"}],
            "dimensions": ["created_at"],
            "filters": [],
            "time_grain": "day",
            "limit": 50,
            "chart": {"type": "line", "x": "created_at", "y": "tickets"},
        }
    )
    compiled = compiler.compile(dsl)
    assert "strftime('%Y-%m-%d', created_at)" in compiled.sql
