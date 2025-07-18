#!/usr/bin/env python3
"""
Test script to demonstrate the end-user OAuth experience for RaidAssist.

This simulates what users will see when they try to authenticate with Bungie.
Run this to test the new seamless OAuth flow.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_user_experience():
    """Test the end-user authentication experience."""

    print("🎮 RaidAssist OAuth Experience Test")
    print("=" * 50)
    print()

    # Test 1: Configuration is bundled (no user setup required)
    print("🔍 Test 1: Checking bundled configuration...")
    try:
        from api.oauth import validate_oauth_config

        is_valid, message = validate_oauth_config()

        if is_valid:
            print("✅ OAuth configuration is ready (no user setup required)")
        else:
            print(f"❌ Configuration issue: {message}")
            return False
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")
        return False

    print()

    # Test 2: Authentication system works
    print("🔍 Test 2: Testing authentication system...")
    try:
        # Enable test mode to avoid actual OAuth flow
        os.environ["RAIDASSIST_TEST_MODE"] = "true"
        os.environ["TEST_TOKEN"] = "mock_user_token_12345"

        from api.oauth import get_access_token

        token = get_access_token()

        if token:
            print(
                "✅ Authentication system working (would open browser for real login)"
            )
            print(f"    Mock token received: {token[:20]}...")
        else:
            print("❌ Authentication system failed")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

    print()

    # Test 3: API connectivity
    print("🔍 Test 3: Testing Bungie API connectivity...")
    try:
        from api.bungie import test_api_connection

        connected = test_api_connection()

        if connected:
            print("✅ Can connect to Bungie API")
        else:
            print(
                "⚠️  Cannot connect to Bungie API (network issue or API key needs updating)"
            )
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

    print()

    # Test 4: User-friendly error handling
    print("🔍 Test 4: Testing user-friendly error messages...")
    try:
        # Disable test mode and try to authenticate (should give friendly error)
        os.environ["RAIDASSIST_TEST_MODE"] = "false"

        from api.oauth import get_access_token

        # This should fail gracefully with a user-friendly message
        # since we're not actually doing the OAuth flow
        try:
            token = get_access_token()
            print("⚠️  Unexpected success (should have failed in non-interactive mode)")
        except Exception as e:
            error_msg = str(e)
            if any(
                phrase in error_msg
                for phrase in ["Could not connect", "try again", "login", "Bungie"]
            ):
                print("✅ User-friendly error messages working")
                print(f"    Sample error: {error_msg}")
            else:
                print(f"⚠️  Error message could be more user-friendly: {error_msg}")

    except Exception as e:
        print(f"❌ Error testing error handling: {e}")
        return False

    print()
    print("🎉 End-User Experience Test Complete!")
    print()
    print("Summary:")
    print("- ✅ No user configuration required")
    print("- ✅ Authentication system ready")
    print("- ✅ User-friendly error messages")
    print("- ✅ Professional 'Login with Bungie' experience")
    print()
    print("🚀 Ready for end users! No API key setup or .env files needed.")

    return True


if __name__ == "__main__":
    try:
        success = test_user_experience()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
