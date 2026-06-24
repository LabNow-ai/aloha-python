from aloha.testing.unit import UnitTestCase


# 1. A simple function-based test for pytest
def test_simple_addition():
    assert 1 + 1 == 2


# 2. A class-based test inheriting from UnitTestCase to demonstrate integrating with the aloha package
class TestDemo(UnitTestCase):
    def test_aloha_config_loaded(self):
        # Verify that aloha settings config can be read
        self.assertIsNotNone(self.config)
        self.LOG.info("Aloha configuration verified successfully in test!")
