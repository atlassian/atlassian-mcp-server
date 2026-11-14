"""Regression test for jql_builder's default order_by value."""

import jql_builder


def test_default_order_by_does_not_crash():
    """build_project_query's own default order_by contains a comma, which
    used to be rejected by sanitize_jql_value before it ever ran a query."""
    query = jql_builder.build_project_query("PROJ")
    assert 'ORDER BY priority DESC, updated DESC' in query


def test_sanitize_jql_value_still_rejects_quotes():
    try:
        jql_builder.sanitize_jql_value('PROJ" OR 1=1 --')
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for a quote in the value")


if __name__ == "__main__":
    test_default_order_by_does_not_crash()
    test_sanitize_jql_value_still_rejects_quotes()
    print("ALL CHECKS PASSED")
