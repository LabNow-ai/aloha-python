import os
import unittest
import warnings
from unittest.mock import patch

from aloha.config import paths


class TestConfigPaths(unittest.TestCase):
    def setUp(self):
        self.original_env = os.environ.copy()
        for key in ("FILES_CONFIG", "PROFILE_ENV", "ENV_PROFILE", "DIR_CONFIG", "DIR_RESOURCE"):
            os.environ.pop(key, None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch("aloha.config.paths.os.path.exists", return_value=True)
    def test_default_without_profile(self, mock_exists):
        """When neither PROFILE_ENV nor ENV_PROFILE is set, default to main.conf without warning."""
        with warnings.catch_warnings(record=True) as captured_warnings:
            warnings.simplefilter("always")
            files = paths.get_config_files()
            self.assertEqual(files, ["main.conf"])
            deprecation_warnings = [
                w for w in captured_warnings if issubclass(w.category, DeprecationWarning)
            ]
            self.assertEqual(len(deprecation_warnings), 0)

    @patch("aloha.config.paths.os.path.exists", return_value=True)
    def test_profile_env_priority(self, mock_exists):
        """When PROFILE_ENV is set, use main-{PROFILE_ENV}.conf without warning."""
        os.environ["PROFILE_ENV"] = "DEV"
        with warnings.catch_warnings(record=True) as captured_warnings:
            warnings.simplefilter("always")
            files = paths.get_config_files()
            self.assertEqual(files, ["main-DEV.conf"])
            deprecation_warnings = [
                w for w in captured_warnings if issubclass(w.category, DeprecationWarning)
            ]
            self.assertEqual(len(deprecation_warnings), 0)

    @patch("aloha.config.paths.os.path.exists", return_value=True)
    def test_profile_env_precedence_over_env_profile(self, mock_exists):
        """When both PROFILE_ENV and ENV_PROFILE are set, PROFILE_ENV takes precedence without warning."""
        os.environ["PROFILE_ENV"] = "PROD"
        os.environ["ENV_PROFILE"] = "DEV"
        with warnings.catch_warnings(record=True) as captured_warnings:
            warnings.simplefilter("always")
            files = paths.get_config_files()
            self.assertEqual(files, ["main-PROD.conf"])
            deprecation_warnings = [
                w for w in captured_warnings if issubclass(w.category, DeprecationWarning)
            ]
            self.assertEqual(len(deprecation_warnings), 0)

    @patch("aloha.config.paths.os.path.exists", return_value=True)
    def test_legacy_env_profile_fallback_with_warning(self, mock_exists):
        """When PROFILE_ENV is unset but ENV_PROFILE is set, fall back to ENV_PROFILE and issue a DeprecationWarning."""
        os.environ["ENV_PROFILE"] = "STG"
        with warnings.catch_warnings(record=True) as captured_warnings:
            warnings.simplefilter("always")
            files = paths.get_config_files()
            self.assertEqual(files, ["main-STG.conf"])
            deprecation_warnings = [
                w for w in captured_warnings if issubclass(w.category, DeprecationWarning)
            ]
            self.assertEqual(len(deprecation_warnings), 1)
            warning_msg = str(deprecation_warnings[0].message)
            self.assertIn("ENV_PROFILE", warning_msg)
            self.assertIn("deprecated", warning_msg)
            self.assertIn("PROFILE_ENV", warning_msg)

    @patch("aloha.config.paths.os.path.exists", return_value=True)
    def test_profile_env_empty_string_fallback(self, mock_exists):
        """When PROFILE_ENV is empty string and ENV_PROFILE is set, fall back to ENV_PROFILE with warning."""
        os.environ["PROFILE_ENV"] = ""
        os.environ["ENV_PROFILE"] = "STG"
        with warnings.catch_warnings(record=True) as captured_warnings:
            warnings.simplefilter("always")
            files = paths.get_config_files()
            self.assertEqual(files, ["main-STG.conf"])
            deprecation_warnings = [
                w for w in captured_warnings if issubclass(w.category, DeprecationWarning)
            ]
            self.assertEqual(len(deprecation_warnings), 1)

    @patch("aloha.config.paths.os.path.exists", return_value=True)
    def test_both_empty_strings(self, mock_exists):
        """When both PROFILE_ENV and ENV_PROFILE are empty strings, default to main.conf without warning."""
        os.environ["PROFILE_ENV"] = "  "
        os.environ["ENV_PROFILE"] = "  "
        with warnings.catch_warnings(record=True) as captured_warnings:
            warnings.simplefilter("always")
            files = paths.get_config_files()
            self.assertEqual(files, ["main.conf"])
            deprecation_warnings = [
                w for w in captured_warnings if issubclass(w.category, DeprecationWarning)
            ]
            self.assertEqual(len(deprecation_warnings), 0)

    @patch("aloha.config.paths.os.path.exists", return_value=True)
    def test_files_config_precedence(self, mock_exists):
        """FILES_CONFIG overrides both PROFILE_ENV and ENV_PROFILE."""
        os.environ["FILES_CONFIG"] = "custom1.conf,custom2.conf"
        os.environ["PROFILE_ENV"] = "PROD"
        os.environ["ENV_PROFILE"] = "DEV"
        with warnings.catch_warnings(record=True) as captured_warnings:
            warnings.simplefilter("always")
            files = paths.get_config_files()
            self.assertEqual(files, ["custom1.conf", "custom2.conf"])
            deprecation_warnings = [
                w for w in captured_warnings if issubclass(w.category, DeprecationWarning)
            ]
            self.assertEqual(len(deprecation_warnings), 0)


if __name__ == "__main__":
    unittest.main()
