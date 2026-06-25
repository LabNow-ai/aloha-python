# Testing Utilities Module (`aloha.testing`)

The `aloha.testing` subpackage provides base classes and helper utilities for writing unit tests and integration tests for API services.

## 1. Unit Testing Base (`aloha.testing.unit`)

Contains the base test case class for standard unit tests.

### Key Classes

- `UnitTestCase`: Extends `unittest.TestCase` and `abc.ABC`.
  - Automatically loads the configured logger as `self.LOG`.
  - Automatically loads the configuration dictionary as `self.config`.

### Usage Example

```python
from aloha.testing.unit import UnitTestCase

class MyServiceTest(UnitTestCase):
    def test_logic(self):
        self.LOG.info("Running custom test...")
        self.assertEqual(self.config.get("app_name"), "MyAlohaApp")
```
