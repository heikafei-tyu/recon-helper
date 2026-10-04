"""可复用的任务执行策略：超时、重试、状态和事件记录。

该模块不绑定具体的核对函数，计划执行器和定时调度器都可以用同一套
策略处理瞬时失败。事件使用普通数据类，便于写入日志或持久层。
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class RetryPolicy:
    """任务失败后的重试策略。attempts 是包含首次执行在内的总次数。"""

    attempts: int = 1
    delay: float = 0.0
    timeout: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.attempts, int) or self.attempts < 1:
            raise ValueError("attempts 必须是正整数")
        if self.delay < 0:
            raise ValueError("delay 不能为负数")
        if self.timeout is not None and self.timeout <= 0:
            raise ValueError("timeout 必须为正数")


@dataclass(frozen=True)
class ExecutionEvent:
    task: str
    attempt: int
    status: str
    started_at: str
    elapsed: float
    error: str | None = None


@dataclass
class ExecutionReport:
    task: str
    status: str
    attempts: int
    result: Any = None
    error: str | None = None
    events: list[ExecutionEvent] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return self.status == "success"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def execute(
    task: str,
    action: Callable[[], Any],
    policy: RetryPolicy | None = None,
    sleep: Callable[[float], None] | None = None,
) -> ExecutionReport:
    """执行一个动作并返回完整报告。

    超时通过独立线程实现，超时后线程仍可能在后台收尾，因此调用方不应
    在动作中修改不可恢复的共享状态。重试只针对动作抛出的异常或超时。
    """
    policy = policy or RetryPolicy()
    if not callable(action):
        raise TypeError("action 必须是可调用对象")
    sleeper = sleep or __import__("time").sleep
    events: list[ExecutionEvent] = []
    last_error: str | None = None
    for attempt in range(1, policy.attempts + 1):
        started_at, started = _timestamp(), perf_counter()
        status, result, error = "success", None, None
        try:
            if policy.timeout is None:
                result = action()
            else:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future: Future[Any] = pool.submit(action)
                    result = future.result(timeout=policy.timeout)
        except FutureTimeout:
            status, error = "timeout", f"任务超过 {policy.timeout} 秒"
        except Exception as exc:  # action 的异常需要进入可审计报告
            status, error = "failed", f"{type(exc).__name__}: {exc}"
        elapsed = round(perf_counter() - started, 6)
        events.append(ExecutionEvent(task, attempt, status, started_at, elapsed, error))
        if status == "success":
            return ExecutionReport(task, status, attempt, result, events=events)
        last_error = error
        if attempt < policy.attempts and policy.delay:
            sleeper(policy.delay)
    return ExecutionReport(task, "failed", policy.attempts, error=last_error, events=events)


def execute_many(
    tasks: Iterable[tuple[str, Callable[[], Any]]], policy: RetryPolicy | None = None, fail_fast: bool = False
) -> list[ExecutionReport]:
    """按给定顺序执行多个动作，可选择首个失败即停止。"""
    reports: list[ExecutionReport] = []
    for name, action in tasks:
        report = execute(name, action, policy)
        reports.append(report)
        if fail_fast and not report.succeeded:
            break
    return reports
