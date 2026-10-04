import time

import pytest

from recon.execution import RetryPolicy, execute, execute_many


def test_execute_success_records_event():
    report = execute("read", lambda: {"rows": 2})
    assert report.succeeded and report.result == {"rows": 2}
    assert report.attempts == 1 and report.events[0].status == "success"


def test_execute_retries_then_succeeds():
    calls = []

    def action():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("temporary")
        return "ok"

    report = execute("retry", action, RetryPolicy(attempts=3))
    assert report.succeeded and report.attempts == 3
    assert [event.status for event in report.events] == ["failed", "failed", "success"]


def test_execute_exhausted_retries_returns_failure():
    report = execute("broken", lambda: 1 / 0, RetryPolicy(attempts=2))
    assert report.status == "failed" and report.attempts == 2
    assert "ZeroDivisionError" in report.error


def test_execute_timeout_is_reported():
    report = execute("slow", lambda: time.sleep(0.05), RetryPolicy(timeout=0.001))
    assert report.status == "failed"
    assert report.events[0].status == "timeout"


def test_execute_many_fail_fast_and_continue_modes():
    actions = [("a", lambda: 1), ("b", lambda: (_ for _ in ()).throw(ValueError("bad"))), ("c", lambda: 3)]
    assert [item.task for item in execute_many(actions, fail_fast=True)] == ["a", "b"]
    assert [item.task for item in execute_many(actions)] == ["a", "b", "c"]


@pytest.mark.parametrize("kwargs", [{"attempts": 0}, {"attempts": -1}, {"delay": -0.1}, {"timeout": 0}])
def test_retry_policy_rejects_invalid_values(kwargs):
    with pytest.raises(ValueError):
        RetryPolicy(**kwargs)


def test_execute_rejects_non_callable():
    with pytest.raises(TypeError):
        execute("bad", None)
