# Utilities

::: aloha.util

::: aloha.util.html

::: aloha.util.json

::: aloha.util.random

::: aloha.util.sys_cuda

::: aloha.util.sys_gpu

::: aloha.util.sys_info

## Time Utilities (`aloha.util.time`)

This module provides tools for wrapping function calls (such as HTTP requests via `requests` or `httpx`) with time constraints (timeouts), allowing execution of optional callbacks upon completion or failure.

### Key Functions
- `run_with_timeout`: Wrap a synchronous function call with a timeout.
- `run_async_with_timeout`: Wrap an asynchronous function call with a timeout.

### Usage Example
```python
from aloha.util.time import run_with_timeout
import requests

def success_callback(response):
    print("Request succeeded:", response.status_code)

def fail_callback(exception):
    print("Request failed or timed out:", exception)

# Synchronous call with timeout
try:
    run_with_timeout(
        requests.get,
        2.5,  # 2.5 seconds timeout
        "https://httpbin.org/delay/1",
        fn_callback_success=success_callback,
        fn_callback_fail=fail_callback
    )
except TimeoutError:
    print("Caught TimeoutError")
```

::: aloha.util.time

