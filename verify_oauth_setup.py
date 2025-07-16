#!/usr/bin/env python3
"""
RaidAssist OAuth Setup Verification Script

This script helps verify that your OAuth environment variables are properly configured.
Run this after setting up your .env file to ensure everything is working correctly.
"""

import os
import sys

# Try to load dotenv if available, but don't fail if it's not
try:
    from dotenv import load_dotenv

    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


def check_env_vars():
    """Check if all required environment variables are set."""
    required_vars = {
        "BUNGIE_API_KEY": "Bungie API Key",
        "BUNGIE_CLIENT_ID": "Bungie OAuth Client ID",
        "BUNGIE_REDIRECT_URI": "OAuth Redirect URI",
    }

    missing_vars = []
    placeholder_vars = []

    for var_name, description in required_vars.items():
        value = os.getenv(var_name)

        if not value:
            missing_vars.append(f"  - {var_name} ({description})")
        elif value.startswith("your_") or value.endswith("_here"):
            placeholder_vars.append(
                f"  - {var_name}: '{value}' (appears to be placeholder)"
            )

    return missing_vars, placeholder_vars


def validate_redirect_uri():
    """Validate the redirect URI format."""
    redirect_uri = os.getenv("BUNGIE_REDIRECT_URI")
    if not redirect_uri:
        return False, "Not set"

    if not redirect_uri.startswith("http://localhost:"):
        return False, f"Should start with 'http://localhost:' but got: {redirect_uri}"

    if not redirect_uri.endswith("/callback"):
        return False, f"Should end with '/callback' but got: {redirect_uri}"

    return True, redirect_uri


def main():
    """Main verification function."""
    print("🔍 RaidAssist OAuth Setup Verification")
    print("=" * 50)

    if not DOTENV_AVAILABLE:
        print("⚠️  python-dotenv not installed")
        print("   Install with: pip install python-dotenv")
        print("   Or manually check your environment variables")
        print()

    # Check if .env file exists
    if not os.path.exists(".env"):
        print("❌ No .env file found!")
        print("   Please copy .env.example to .env and fill in your credentials.")
        print("   See docs/OAUTH_SETUP.md for detailed instructions.")
        sys.exit(1)

    print("✅ Found .env file")

    # Check environment variables
    missing_vars, placeholder_vars = check_env_vars()

    if missing_vars:
        print(f"\n❌ Missing environment variables:")
        for var in missing_vars:
            print(var)

    if placeholder_vars:
        print(f"\n⚠️  Placeholder values detected:")
        for var in placeholder_vars:
            print(var)

    if missing_vars or placeholder_vars:
        print("\n📚 Please update your .env file with real values.")
        print(
            "   See docs/OAUTH_SETUP.md for instructions on obtaining these credentials."
        )
        sys.exit(1)

    # Validate redirect URI
    uri_valid, uri_message = validate_redirect_uri()
    if uri_valid:
        print(f"✅ Redirect URI: {uri_message}")
    else:
        print(f"❌ Invalid redirect URI: {uri_message}")
        sys.exit(1)

    # All checks passed
    print("\n🎉 OAuth configuration looks good!")
    print("\n📋 Summary:")
    print(f"   API Key: {'*' * 20}...{os.getenv('BUNGIE_API_KEY', '')[-4:]}")
    print(f"   Client ID: {os.getenv('BUNGIE_CLIENT_ID', '')}")
    print(f"   Redirect URI: {os.getenv('BUNGIE_REDIRECT_URI', '')}")

    print("\n⚠️  Remember:")
    print("   - Your Bungie OAuth app must be configured with the redirect URI above")
    print("   - The OAuth app must be set to 'Confidential' type")
    print("   - Never commit your .env file to version control")

    print("\n🚀 You can now run RaidAssist with OAuth authentication!")


if __name__ == "__main__":
    main()
