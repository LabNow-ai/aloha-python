# 工具函数

::: aloha.util

::: aloha.util.html

::: aloha.util.json

::: aloha.util.random

::: aloha.util.sys_cuda

::: aloha.util.sys_gpu

::: aloha.util.sys_info

## 时间工具 (`aloha.util.time`)

该模块提供用于包装函数调用（如通过 `httpx2` 发起外部 HTTP 请求）的超时控制工具，并在操作成功或失败（超时/异常）时触发可选的回调函数。

### 核心函数
- `run_with_timeout`: 以同步方式运行函数，并应用超时限制。
- `run_async_with_timeout`: 以异步方式（协程或在执行器中运行同步函数）运行函数，并应用超时限制。

### 使用示例
```python
from aloha.util.time import run_with_timeout
import httpx2

def success_callback(response):
    print("请求成功:", response.status_code)

def fail_callback(exception):
    print("请求失败或超时:", exception)

# 同步超时包装调用
try:
    run_with_timeout(
        httpx2.get,
        2.5,  # 2.5 秒超时限制
        "https://httpbin.org/delay/1",
        fn_callback_success=success_callback,
        fn_callback_fail=fail_callback
    )
except TimeoutError:
    print("捕获到超时异常 (TimeoutError)")
```

::: aloha.util.time

