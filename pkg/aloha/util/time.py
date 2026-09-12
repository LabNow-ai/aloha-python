"""Time and timeout utilities."""

import asyncio
import concurrent.futures
import inspect
from collections.abc import Callable
from typing import Any

__all__ = ("run_async_with_timeout", "run_with_timeout")


def run_with_timeout(
    func: Callable[..., Any],
    timeout_seconds: float,
    *args: Any,
    fn_callback_success: Callable[[Any], Any] | None = None,
    fn_callback_fail: Callable[[Exception], Any] | None = None,
    **kwargs: Any,
) -> Any:
    """Wrap a synchronous function call with a timeout.

    If the operation completes within `timeout_seconds`, `fn_callback_success(result)`
    is executed if provided, and the result is returned.
    If the operation times out or raises an exception, `fn_callback_fail(exception)`
    is executed if provided, and the exception is reraised.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            result = future.result(timeout=timeout_seconds)
            if fn_callback_success is not None:
                fn_callback_success(result)
            return result
        except Exception as e:  # noqa: BLE001
            if isinstance(e, concurrent.futures.TimeoutError):
                exc = TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
            else:
                exc = e
            if fn_callback_fail is not None:
                fn_callback_fail(exc)
            raise exc


async def run_async_with_timeout(
    func: Callable[..., Any],
    timeout_seconds: float,
    *args: Any,
    fn_callback_success: Callable[[Any], Any] | None = None,
    fn_callback_fail: Callable[[Exception], Any] | None = None,
    **kwargs: Any,
) -> Any:
    """Wrap an asynchronous function call (coroutine function or sync function inside executor) with a timeout.

    If the operation completes within `timeout_seconds`, `fn_callback_success(result)`
    is executed if provided, and the result is returned.
    If the operation times out or raises an exception, `fn_callback_fail(exception)`
    is executed if provided, and the exception is reraised.
    """
    try:
        if inspect.iscoroutinefunction(func):
            coro = func(*args, **kwargs)
        else:
            # Run sync function in default executor to prevent blocking the event loop
            loop = asyncio.get_running_loop()
            coro = loop.run_in_executor(None, lambda: func(*args, **kwargs))

        result = await asyncio.wait_for(coro, timeout=timeout_seconds)
        if fn_callback_success is not None:
            fn_callback_success(result)
        return result
    except Exception as e:  # noqa: BLE001
        if isinstance(e, (asyncio.TimeoutError, concurrent.futures.TimeoutError)):
            exc = TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
        else:
            exc = e
        if fn_callback_fail is not None:
            fn_callback_fail(exc)
        raise exc
