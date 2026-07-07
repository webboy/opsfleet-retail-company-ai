"""Tests for SQL helper utilities."""

from retail_agent.sql_utils import extract_sql, is_schema_question


def test_extract_sql_from_code_block():
    text = "Here is the query:\n```sql\nSELECT 1\n```"
    assert extract_sql(text) == "SELECT 1"


def test_is_schema_question_detects_structure_queries():
    assert is_schema_question("What tables and columns do you have?")
    assert not is_schema_question("What was monthly revenue last quarter?")
