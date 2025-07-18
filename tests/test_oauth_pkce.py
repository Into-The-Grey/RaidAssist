"""
Test script for OAuth PKCE implementation.

Tests the new OAuth PKCE flow without requiring real authentication.
Verifies bundled configuration and function signatures.
"""

import os
import sys
import tempfile
import json
import time

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_bundled_configuration():
    """Test that OAuth configuration can be properly set up."""
    print("Testing OAuth configuration setup...")

    # Set test environment variables
    import os

    os.environ["BUNGIE_API_KEY"] = "test_api_key_12345"
    os.environ["BUNGIE_CLIENT_ID"] = "12345"
    os.environ["BUNGIE_REDIRECT_URI"] = "http://localhost:7777/callback"
    os.environ["RAIDASSIST_TEST_MODE"] = "true"  # Enable test mode

    # Re-import to pick up new environment variables
    import importlib
    import api.oauth

    importlib.reload(api.oauth)

    from api.oauth import BUNGIE_API_KEY, BUNGIE_CLIENT_ID, BUNGIE_REDIRECT_URI

    assert (
        BUNGIE_API_KEY == "test_api_key_12345"
    ), f"API key not loaded from environment - got '{BUNGIE_API_KEY}'"
    assert (
        BUNGIE_CLIENT_ID == "12345"
    ), f"Client ID not loaded from environment - got '{BUNGIE_CLIENT_ID}'"
    assert (
        BUNGIE_REDIRECT_URI == "http://localhost:7777/callback"
    ), f"Redirect URI mismatch - got '{BUNGIE_REDIRECT_URI}'"

    print("✅ OAuth configuration setup working correctly")


def test_pkce_utilities():
    """Test PKCE code generation utilities."""
    print("Testing PKCE utilities...")

    from api.oauth import generate_code_verifier, generate_code_challenge

    # Test code verifier generation
    verifier = generate_code_verifier()
    assert len(verifier) >= 43, "Code verifier too short"
    assert len(verifier) <= 128, "Code verifier too long"
    assert (
        verifier.replace("-", "").replace("_", "").isalnum()
    ), "Invalid characters in verifier"

    # Test code challenge generation
    challenge = generate_code_challenge(verifier)
    assert len(challenge) == 43, "Code challenge wrong length"
    assert (
        challenge.replace("-", "").replace("_", "").isalnum()
    ), "Invalid characters in challenge"

    print("✅ PKCE utilities working correctly")


def test_session_management():
    """Test session save/load functionality."""
    print("Testing session management...")

    from api.oauth import save_session, load_session, is_token_expired

    # Create temporary session file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_session_path = f.name

    # Mock the session path
    import api.oauth

    original_path = api.oauth.SESSION_PATH
    api.oauth.SESSION_PATH = temp_session_path

    try:
        # Test session save/load
        test_session = {
            "access_token": "test_token_123",
            "refresh_token": "refresh_123",
            "expires_at": time.time() + 3600,
        }

        save_session(test_session)
        loaded_session = load_session()

        assert loaded_session is not None, "Failed to load session"
        assert loaded_session["access_token"] == "test_token_123", "Token mismatch"
        assert not is_token_expired(loaded_session), "Token should not be expired"

        # Test expired token
        expired_session = {
            "access_token": "expired_token",
            "expires_at": time.time() - 100,
        }
        save_session(expired_session)
        loaded_expired = load_session()
        assert is_token_expired(loaded_expired), "Token should be expired"

        print("✅ Session management working correctly")

    finally:
        # Restore original path and cleanup
        api.oauth.SESSION_PATH = original_path
        if os.path.exists(temp_session_path):
            os.unlink(temp_session_path)


def test_bungie_integration():
    """Test Bungie API integration functions."""
    print("Testing Bungie API integration...")

    # Set test environment variables before importing
    import os

    os.environ["BUNGIE_API_KEY"] = "test_api_key_12345"
    os.environ["BUNGIE_CLIENT_ID"] = "12345"
    os.environ["BUNGIE_REDIRECT_URI"] = "http://localhost:7777/callback"
    os.environ["RAIDASSIST_TEST_MODE"] = "true"  # Enable test mode

    # Force reload of modules to pick up environment variables
    import importlib
    import api.oauth
    import api.bungie

    importlib.reload(api.oauth)
    importlib.reload(api.bungie)

    from api.oauth import (
        BUNGIE_API_KEY as OAUTH_API_KEY,
        BUNGIE_CLIENT_ID as OAUTH_CLIENT_ID,
    )
    from api.bungie import (
        BUNGIE_API_KEY,
        BUNGIE_CLIENT_ID,
        ensure_authenticated,
        logout_user,
    )

    # Test environment configuration (should use same test values set earlier)
    assert (
        OAUTH_API_KEY == "test_api_key_12345"
    ), f"OAuth API key not from environment - got '{OAUTH_API_KEY}'"
    assert (
        BUNGIE_API_KEY == "test_api_key_12345"
    ), f"Bungie API key not from environment - got '{BUNGIE_API_KEY}'"
    assert (
        OAUTH_CLIENT_ID == "12345"
    ), f"OAuth Client ID not from environment - got '{OAUTH_CLIENT_ID}'"
    assert (
        BUNGIE_CLIENT_ID == "12345"
    ), f"Bungie Client ID not from environment - got '{BUNGIE_CLIENT_ID}'"

    # Test function availability (shouldn't raise errors)
    assert callable(ensure_authenticated), "ensure_authenticated not callable"
    assert callable(logout_user), "logout_user not callable"

    print("✅ Bungie API integration configured correctly")


def test_bundled_credentials():
    """Test that the system properly handles bundled credentials."""
    print("Testing bundled credential configuration...")

    # Back up environment variables
    env_backup = {}
    for var in ["BUNGIE_API_KEY", "BUNGIE_CLIENT_ID", "BUNGIE_REDIRECT_URI"]:
        if var in os.environ:
            env_backup[var] = os.environ[var]
            del os.environ[var]

    try:
        # Re-import to test without env vars
        import importlib
        import api.oauth
        import api.bungie

        importlib.reload(api.oauth)
        importlib.reload(api.bungie)

        # Should use bundled values when env vars not set
        assert (
            api.oauth.BUNGIE_API_KEY
            == "b4c3ff9cf4fb4ba3a1a0b8a5a8e3f8e9c2d6b5a8c9f2e1d4a7b0c6f5e8d9c2a5"
        )
        assert api.oauth.BUNGIE_CLIENT_ID == "31415926"

        print("✅ Bundled credential handling works correctly")

    finally:
        # Restore environment variables
        for var, value in env_backup.items():
            os.environ[var] = value


def run_all_tests():
    """Run all OAuth PKCE tests."""
    print("Running OAuth PKCE Implementation Tests")
    print("=" * 50)

    try:
        test_bundled_configuration()
        test_pkce_utilities()
        test_session_management()
        test_bungie_integration()
        test_bundled_credentials()

        print("\n" + "=" * 50)
        print("🎉 All OAuth PKCE tests passed!")
        print("The new authentication system is ready to use.")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


# Additional pytest-compatible test functions for CI
def test_oauth_environment_setup():
    """Pytest version of test_bungie_integration for CI."""
    import os

    # Set test environment variables
    os.environ["BUNGIE_API_KEY"] = "test_api_key_12345"
    os.environ["BUNGIE_CLIENT_ID"] = "12345"
    os.environ["BUNGIE_REDIRECT_URI"] = "http://localhost:7777/callback"
    os.environ["RAIDASSIST_TEST_MODE"] = "true"

    # Force reload of modules to pick up environment variables
    import importlib
    import api.oauth
    import api.bungie

    importlib.reload(api.oauth)
    importlib.reload(api.bungie)

    from api.oauth import (
        BUNGIE_API_KEY as OAUTH_API_KEY,
        BUNGIE_CLIENT_ID as OAUTH_CLIENT_ID,
    )
    from api.bungie import BUNGIE_API_KEY, BUNGIE_CLIENT_ID

    # Test environment configuration
    assert (
        OAUTH_API_KEY == "test_api_key_12345"
    ), f"OAuth API key not from environment - got '{OAUTH_API_KEY}'"
    assert (
        BUNGIE_API_KEY == "test_api_key_12345"
    ), f"Bungie API key not from environment - got '{BUNGIE_API_KEY}'"
    assert (
        OAUTH_CLIENT_ID == "12345"
    ), f"OAuth Client ID not from environment - got '{OAUTH_CLIENT_ID}'"
    assert (
        BUNGIE_CLIENT_ID == "12345"
    ), f"Bungie Client ID not from environment - got '{BUNGIE_CLIENT_ID}'"
