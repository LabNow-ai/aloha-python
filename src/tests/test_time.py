import pytest
import time
import asyncio
from aloha.util.time import run_with_timeout, run_async_with_timeout

# Helpers
def sync_add(a, b, delay=0):
    if delay > 0:
        time.sleep(delay)
    return a + b

def sync_raise():
    raise ValueError("sync error")

async def async_add(a, b, delay=0):
    if delay > 0:
        await asyncio.sleep(delay)
    return a + b

async def async_raise():
    raise ValueError("async error")


# 1. Sync Tests
def test_sync_success():
    success_called = False
    result_val = None

    def on_success(res):
        nonlocal success_called, result_val
        success_called = True
        result_val = res

    res = run_with_timeout(sync_add, 1.0, 2, 3, fn_callback_success=on_success)
    assert res == 5
    assert success_called is True
    assert result_val == 5

def test_sync_timeout():
    fail_called = False
    error_val = None

    def on_fail(err):
        nonlocal fail_called, error_val
        fail_called = True
        error_val = err

    with pytest.raises(TimeoutError):
        run_with_timeout(sync_add, 0.1, 2, 3, delay=0.5, fn_callback_fail=on_fail)
    assert fail_called is True
    assert isinstance(error_val, TimeoutError)

def test_sync_exception():
    fail_called = False
    error_val = None

    def on_fail(err):
        nonlocal fail_called, error_val
        fail_called = True
        error_val = err

    with pytest.raises(ValueError, match="sync error"):
        run_with_timeout(sync_raise, 1.0, fn_callback_fail=on_fail)
    assert fail_called is True
    assert isinstance(error_val, ValueError)


# 2. Async Tests
def test_async_success():
    success_called = False
    result_val = None

    def on_success(res):
        nonlocal success_called, result_val
        success_called = True
        result_val = res

    res = asyncio.run(run_async_with_timeout(async_add, 1.0, 2, 3, fn_callback_success=on_success))
    assert res == 5
    assert success_called is True
    assert result_val == 5

def test_async_timeout():
    fail_called = False
    error_val = None

    def on_fail(err):
        nonlocal fail_called, error_val
        fail_called = True
        error_val = err

    with pytest.raises(TimeoutError):
        asyncio.run(run_async_with_timeout(async_add, 0.1, 2, 3, delay=0.5, fn_callback_fail=on_fail))
    assert fail_called is True
    assert isinstance(error_val, TimeoutError)

def test_async_exception():
    fail_called = False
    error_val = None

    def on_fail(err):
        nonlocal fail_called, error_val
        fail_called = True
        error_val = err

    with pytest.raises(ValueError, match="async error"):
        asyncio.run(run_async_with_timeout(async_raise, 1.0, fn_callback_fail=on_fail))
    assert fail_called is True
    assert isinstance(error_val, ValueError)
