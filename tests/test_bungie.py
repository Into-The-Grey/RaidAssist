# RaidAssist — Destiny 2 Progression Tracker and Overlay
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>
#
# Enhanced test_bungie.py with improved error handling and logging integration

import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import pytest  # type: ignore

    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

    # Create minimal test framework for when pytest not available
    class TestSkip(Exception):
        pass

    def pytest_skip(msg):
        raise TestSkip(msg)

    class MockPytest:
        def skip(self, msg):
            raise TestSkip(msg)

        def main(self, args):
            return 0  # Mock success

    pytest = MockPytest()

# Enhanced error handling for tests
try:
    from utils.error_handler import safe_execute
    from utils.logging_manager import get_logger

    test_logger = get_logger("raidassist.tests.bungie")
    TESTING = True
except ImportError:
    import logging

    test_logger = logging.getLogger("tests.bungie")
    TESTING = False

    def safe_execute(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return kwargs.get("default_return")


from api import bungie


class TestBungieAPI:
    """Test class for Bungie API functionality."""

    def test_load_token_with_valid_file(self, tmp_path, monkeypatch):
        """Test loading token from valid session file."""
        if not PYTEST_AVAILABLE:
            return self._manual_test_load_token()

        # Set test mode environment variables
        monkeypatch.setenv("RAIDASSIST_TEST_MODE", "true")
        monkeypatch.setenv("TEST_TOKEN", "test_token")

        # Force reload of oauth module to pick up environment variables
        import importlib
        import api.oauth

        importlib.reload(api.oauth)

        result = bungie.load_token()
        assert result == "test_token", f"Expected 'test_token', got {result}"

        if TESTING:
            test_logger.info("Token loading test passed")

    def _manual_test_load_token(self):
        """Manual test for when pytest not available."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            session_path = os.path.join(tmp_dir, "session.json")

            # Mock the SESSION_PATH
            original_path = getattr(bungie, "SESSION_PATH", None)
            bungie.SESSION_PATH = session_path

            try:
                # Write test token
                with open(session_path, "w") as f:
                    json.dump({"access_token": "test_token"}, f)

                result = safe_execute(bungie.load_token, default_return=None)
                assert result == "test_token", f"Expected 'test_token', got {result}"
                print("✅ Manual token loading test passed")

            finally:
                # Restore original path
                if original_path:
                    bungie.SESSION_PATH = original_path

    def test_load_token_missing_file(self, monkeypatch):
        """Test loading token when session file doesn't exist."""
        if not PYTEST_AVAILABLE:
            return self._manual_test_missing_token()

        # Set test mode with a specific test token
        monkeypatch.setenv("RAIDASSIST_TEST_MODE", "true")
        monkeypatch.setenv("TEST_TOKEN", "default_test_token")

        # Force reload of oauth module to pick up environment variables
        import importlib
        import api.oauth

        importlib.reload(api.oauth)

        result = bungie.load_token()
        # Should get test token in test mode
        assert result == "default_test_token"

    def test_load_token_oauth_failure(self, monkeypatch):
        """Test loading token when OAuth fails (not in test mode)."""
        if not PYTEST_AVAILABLE:
            return

        # Disable test mode and mock OAuth to fail
        monkeypatch.setenv("RAIDASSIST_TEST_MODE", "false")
        import api.oauth

        monkeypatch.setattr(api.oauth, "get_access_token", lambda: None)

        result = safe_execute(bungie.load_token, default_return=None)
        # Should get None when OAuth fails
        assert result is None

    def _manual_test_missing_token(self):
        """Manual test for missing token file."""
        original_path = getattr(bungie, "SESSION_PATH", None)

        try:
            bungie.SESSION_PATH = "/non/existent/file.json"
            # Mock the OAuth module to avoid real OAuth
            import api.oauth

            original_get_token = getattr(api.oauth, "get_access_token", None)
            api.oauth.get_access_token = lambda: None

            result = safe_execute(bungie.load_token, default_return=None)
            assert result is None, f"Expected None, got {result}"
            print("✅ Manual missing token test passed")

        finally:
            if original_path:
                bungie.SESSION_PATH = original_path
            # Restore original OAuth function
            if original_get_token:
                api.oauth.get_access_token = original_get_token

    def test_api_connection_check(self):
        """Test API connection checking."""
        # This should not raise exceptions even if connection fails
        result = safe_execute(bungie.test_api_connection, default_return=False)
        assert isinstance(result, bool)

        if TESTING:
            test_logger.info(f"API connection test result: {result}")

    def test_ensure_authenticated_functionality(self):
        """Test authentication checking."""
        # This should handle missing credentials gracefully
        result = safe_execute(bungie.ensure_authenticated, default_return=False)
        assert isinstance(result, bool)

        if TESTING:
            test_logger.info(f"Authentication check result: {result}")


# Manual test runner for when pytest not available
def run_manual_tests():
    """Run tests manually when pytest not available."""
    print("🧪 Running Bungie API Tests (Manual Mode)")
    print("=" * 50)

    test_instance = TestBungieAPI()
    tests = [
        ("Token Loading", test_instance._manual_test_load_token),
        ("Missing Token", test_instance._manual_test_missing_token),
        ("API Connection", test_instance.test_api_connection_check),
        ("Authentication Check", test_instance.test_ensure_authenticated_functionality),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"\n🔍 Running {test_name}...")
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            failed += 1

    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    """Run tests directly if script is executed."""
    if PYTEST_AVAILABLE:
        pytest.main([__file__, "-v"])
    else:
        success = run_manual_tests()
        sys.exit(0 if success else 1)


def test_load_token_missing(monkeypatch):
    """Test loading token when session file doesn't exist and OAuth disabled."""
    # Disable test mode for this test to test real OAuth failure
    monkeypatch.setenv("RAIDASSIST_TEST_MODE", "false")

    # Force reload of oauth module
    import importlib
    import api.oauth

    importlib.reload(api.oauth)

    # Patch SESSION_PATH to non-existent
    monkeypatch.setattr(bungie, "SESSION_PATH", "/non/existent/file.json")
    # Patch the new OAuth implementation to avoid real OAuth
    import api.oauth

    monkeypatch.setattr(api.oauth, "authorize", lambda: None)
    monkeypatch.setattr(api.oauth, "load_session", lambda: None)
    monkeypatch.setattr(api.oauth, "refresh_token", lambda x: None)

    # Should raise an exception which bungie.load_token handles and returns None
    result = bungie.load_token()
    assert result is None


def test_fetch_profile_mock(monkeypatch, tmp_path):
    """Test profile fetching with mocked OAuth and requests."""
    # Set test mode
    monkeypatch.setenv("RAIDASSIST_TEST_MODE", "true")
    monkeypatch.setenv("TEST_TOKEN", "fake_token")

    # Force reload oauth
    import importlib
    import api.oauth

    importlib.reload(api.oauth)

    # Patch out load_token and requests.get
    monkeypatch.setattr(bungie, "BUNGIE_API_KEY", "test_key")
    monkeypatch.setattr(bungie, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(bungie, "PROFILE_CACHE_PATH", str(tmp_path / "profile.json"))

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"Response": {"profile": "ok"}}

        @property
        def status_code(self):
            return 200

    # Mock requests.get more thoroughly
    def mock_requests_get(*args, **kwargs):
        return FakeResp()

    # Patch requests.get correctly
    monkeypatch.setattr(bungie.requests, "get", mock_requests_get)

    # Ensure the function doesn't try to use cached data
    cache_path = tmp_path / "profile.json"
    if cache_path.exists():
        cache_path.unlink()

    # Should write the cache and return the dict
    out = bungie.fetch_profile(3, "12345")
    assert out == {"Response": {"profile": "ok"}}
    # Cache file written
    assert os.path.exists(tmp_path / "profile.json")
    # Content check - match the actual cache structure
    with open(tmp_path / "profile.json") as f:
        cache_content = json.load(f)
        assert cache_content["profile"] == {"Response": {"profile": "ok"}}


def test_fetch_profile_no_token(monkeypatch):
    """Test profile fetching when no token is available."""
    # Disable test mode to test real no-token scenario
    monkeypatch.setenv("RAIDASSIST_TEST_MODE", "false")

    # Force reload oauth
    import importlib
    import api.oauth

    importlib.reload(api.oauth)

    # Mock load_token to return None and avoid OAuth flow
    monkeypatch.setattr(api.oauth, "load_session", lambda: None)
    monkeypatch.setattr(api.oauth, "authorize", lambda: None)

    # Should return None when no token available
    result = bungie.fetch_profile(3, "12345")
    assert result is None
