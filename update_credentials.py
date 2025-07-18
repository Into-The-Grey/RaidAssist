#!/usr/bin/env python3
"""
Production credential updater for RaidAssist.

This script allows updating the bundled OAuth credentials for production deployment.
Use this when you have real Bungie API credentials to replace the placeholder values.

Usage:
    python update_credentials.py <api_key> <client_id>

Example:
    python update_credentials.py abc123def456... 987654321
"""

import os
import sys
import re


def update_credentials(api_key: str, client_id: str):
    """Update bundled credentials in all relevant files."""

    if not api_key or not client_id:
        print("❌ Error: Both API key and Client ID are required")
        return False

    if api_key == "your_bungie_api_key_here" or client_id == "your_client_id_here":
        print("❌ Error: Please provide real Bungie API credentials, not placeholders")
        return False

    files_to_update = [
        "api/oauth.py",
        "api/bungie.py",
        "api/manifest.py",
        "ui/api_tester.py",
        "debug_api.py",
    ]

    project_root = os.path.dirname(os.path.abspath(__file__))

    for file_path in files_to_update:
        full_path = os.path.join(project_root, file_path)

        if not os.path.exists(full_path):
            print(f"⚠️  Warning: {file_path} not found, skipping")
            continue

        try:
            with open(full_path, "r") as f:
                content = f.read()

            # Update API key
            content = re.sub(
                r'BUNGIE_API_KEY.*=.*"[^"]*"', f'BUNGIE_API_KEY = "{api_key}"', content
            )

            # Update Client ID
            content = re.sub(
                r'BUNGIE_CLIENT_ID.*=.*"[^"]*"',
                f'BUNGIE_CLIENT_ID = "{client_id}"',
                content,
            )

            with open(full_path, "w") as f:
                f.write(content)

            print(f"✅ Updated {file_path}")

        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")
            return False

    print(f"\n🎉 Successfully updated all files with new credentials!")
    print(f"📋 API Key: {api_key[:20]}...")
    print(f"📋 Client ID: {client_id}")
    print(f"\n⚠️  Important: Test the authentication flow before deploying to users")

    return True


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        print("❌ Error: Exactly 2 arguments required (API key and Client ID)")
        sys.exit(1)

    api_key = sys.argv[1].strip()
    client_id = sys.argv[2].strip()

    print("🔧 RaidAssist Credential Updater")
    print("=" * 50)
    print(f"📋 API Key: {api_key[:20]}...")
    print(f"📋 Client ID: {client_id}")
    print()

    confirm = input("Update credentials in all files? (y/N): ").strip().lower()
    if confirm != "y":
        print("❌ Update cancelled")
        sys.exit(1)

    success = update_credentials(api_key, client_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
