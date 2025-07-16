#!/usr/bin/env python3
"""
Validation script to test CI fixes for the OAuth and token loading issues.
This script simulates the CI environment and validates the fixes.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def set_test_environment():
    """Set up the test environment variables as they would be in CI."""
    test_env = {
        "RAIDASSIST_TEST_MODE": "true",
        "BUNGIE_API_KEY": "test_api_key_12345",
        "BUNGIE_CLIENT_ID": "12345",
        "BUNGIE_REDIRECT_URI": "http://localhost:7777/callback",
        "TEST_TOKEN": "test_token",
        "QT_QPA_PLATFORM": "offscreen",
    }

    for key, value in test_env.items():
        os.environ[key] = value

    print("✅ Test environment variables set:")
    for key, value in test_env.items():
        print(f"   {key}={value}")

    return test_env


def test_oauth_module():
    """Test that the OAuth module works with test configuration."""
    print("\n🔧 Testing OAuth module with test configuration...")

    try:
        import importlib
        import api.oauth

        importlib.reload(api.oauth)

        from api.oauth import (
            BUNGIE_API_KEY,
            BUNGIE_CLIENT_ID,
            get_access_token,
            validate_oauth_config,
        )

        # Test configuration loading
        assert (
            BUNGIE_API_KEY == "test_api_key_12345"
        ), f"API key mismatch: {BUNGIE_API_KEY}"
        assert BUNGIE_CLIENT_ID == "12345", f"Client ID mismatch: {BUNGIE_CLIENT_ID}"
        print("   ✅ Configuration loaded correctly")

        # Test OAuth validation with test mode
        is_valid, msg = validate_oauth_config()
        assert is_valid, f"OAuth validation failed: {msg}"
        print("   ✅ OAuth validation passes in test mode")

        # Test token acquisition
        token = get_access_token()
        assert token == "test_token", f"Token mismatch: {token}"
        print("   ✅ Test token acquired successfully")

        return True

    except Exception as e:
        print(f"   ❌ OAuth module test failed: {e}")
        return False


def test_bungie_module():
    """Test that the Bungie module works with test configuration."""
    print("\n🔧 Testing Bungie module with test configuration...")

    try:
        import importlib
        import api.bungie

        importlib.reload(api.bungie)

        from api.bungie import BUNGIE_API_KEY, load_token

        # Test configuration loading
        assert (
            BUNGIE_API_KEY == "test_api_key_12345"
        ), f"API key mismatch: {BUNGIE_API_KEY}"
        print("   ✅ Configuration loaded correctly")

        # Test token loading
        token = load_token()
        assert token == "test_token", f"Token mismatch: {token}"
        print("   ✅ Test token loaded successfully")

        return True

    except Exception as e:
        print(f"   ❌ Bungie module test failed: {e}")
        return False


def run_specific_tests():
    """Run the specific tests that were failing in CI."""
    print("\n🧪 Running the specific tests that were failing in CI...")

    project_root = Path(__file__).parent
    venv_python = project_root / "venv" / "bin" / "python"

    # Define the failing tests
    failing_tests = [
        "tests/test_bungie.py::TestBungieAPI::test_load_token_with_valid_file",
        "tests/test_oauth_pkce.py::test_bungie_integration",
    ]

    all_passed = True

    for test in failing_tests:
        print(f"\n   Running: {test}")
        try:
            result = subprocess.run(
                [str(venv_python), "-m", "pytest", test, "-v", "--tb=short"],
                cwd=project_root,
                capture_output=True,
                text=True,
                env=os.environ,
            )

            if result.returncode == 0:
                print(f"   ✅ {test} PASSED")
            else:
                print(f"   ❌ {test} FAILED")
                print(f"      stdout: {result.stdout}")
                print(f"      stderr: {result.stderr}")
                all_passed = False

        except Exception as e:
            print(f"   ❌ Error running {test}: {e}")
            all_passed = False

    return all_passed


def main():
    """Main validation function."""
    print("🚀 RaidAssist CI Fix Validation")
    print("=" * 50)

    # Set up test environment
    test_env = set_test_environment()

    # Test individual modules
    oauth_ok = test_oauth_module()
    bungie_ok = test_bungie_module()

    # Run the specific failing tests
    tests_ok = run_specific_tests()

    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"OAuth Module:     {'✅ PASS' if oauth_ok else '❌ FAIL'}")
    print(f"Bungie Module:    {'✅ PASS' if bungie_ok else '❌ FAIL'}")
    print(f"Failing Tests:    {'✅ PASS' if tests_ok else '❌ FAIL'}")

    overall_success = oauth_ok and bungie_ok and tests_ok
    print(f"\nOverall Result:   {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")

    if overall_success:
        print("\n🎉 All fixes are working correctly!")
        print("The CI should now pass with these changes.")
    else:
        print("\n⚠️  Some issues remain. Check the output above for details.")

    return 0 if overall_success else 1


if __name__ == "__main__":
    sys.exit(main())
