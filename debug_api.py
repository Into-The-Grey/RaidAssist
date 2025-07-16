#!/usr/bin/env python3
"""
Debug script to test Bungie API endpoints and identify    # Test 2: SearchDestinyPlayer endpoint (fixed format)
    test_endpoint(
        "https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayer/-1/TestUser/",
        headers
    )s.
This will help diagnose the "Endpoint not found" errors.
"""

import os
import requests
import json
from typing import Dict, Any, Optional

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Get API key (same logic as in bungie.py)
API_KEY = os.environ.get("BUNGIE_API_KEY") or "YOUR_BUNGIE_API_KEY"
USER_AGENT = "RaidAssist/1.0"


def test_endpoint(
    url: str, headers: Dict[str, str], params: Optional[Dict[str, Any]] = None
) -> None:
    """Test a single endpoint and report results."""
    print(f"\n{'='*60}")
    print(f"Testing: {url}")
    print(f"Headers: {headers}")
    if params:
        print(f"Params: {params}")

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ SUCCESS")
            try:
                data = response.json()
                if "Response" in data:
                    print("✅ Valid Bungie API response structure")
                else:
                    print("⚠️  Response doesn't have expected 'Response' field")
            except json.JSONDecodeError:
                print("⚠️  Response is not valid JSON")
        else:
            print("❌ FAILED")
            print(f"Response text: {response.text[:500]}...")

    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")


def main():
    """Run all endpoint tests."""
    print("Bungie API Endpoint Debug Tool")
    print("=" * 60)

    # Check API key configuration
    print(
        f"\nAPI Key configured: {'✅ YES' if API_KEY != 'YOUR_BUNGIE_API_KEY' else '❌ NO (using placeholder)'}"
    )
    print(f"API Key length: {len(API_KEY)} characters")

    if API_KEY == "YOUR_BUNGIE_API_KEY":
        print(
            "\n⚠️  WARNING: Using placeholder API key. Set BUNGIE_API_KEY environment variable!"
        )
        print("Without a valid API key, all requests will fail.")

    # Common headers for all requests
    headers = {"X-API-Key": API_KEY, "User-Agent": USER_AGENT}

    # Test 1: Manifest endpoint (should work without auth)
    test_endpoint("https://www.bungie.net/Platform/Destiny2/Manifest/", headers)

    # Test 2: SearchDestinyPlayer endpoint (fixed format)
    test_endpoint(
        "https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayer/-1/TestUser/",
        headers,
    )

    # Test 3: Profile endpoint (requires auth and valid IDs, but let's see the error)
    test_endpoint(
        "https://www.bungie.net/Platform/Destiny2/3/Profile/12345/",
        headers,
        {"components": "100"},
    )

    # Test 4: OAuth token endpoint (different base, should accept POST)
    oauth_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    print(f"\n{'='*60}")
    print("Testing OAuth endpoint (should return 400 for GET request, not 404)")
    print("URL: https://www.bungie.net/platform/app/oauth/token/")

    try:
        response = requests.get(
            "https://www.bungie.net/platform/app/oauth/token/",
            headers=oauth_headers,
            timeout=10,
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✅ Endpoint exists (400 expected for GET request)")
        elif response.status_code == 404:
            print("❌ Endpoint not found (this would indicate a URL issue)")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ ERROR: {e}")  # Test 5: Check for common URL mistakes
    print(f"\n{'='*60}")
    print("Testing common URL mistakes:")

    # OLD BROKEN FORMAT (query parameter)
    print("\n" + "=" * 40)
    print("Testing OLD BROKEN format (query parameter):")
    test_endpoint(
        "https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayer/-1/",
        headers,
        {"displayName": "TestUser"},
    )

    # Wrong capitalization
    test_endpoint("https://www.bungie.net/platform/destiny2/manifest/", headers)

    # Missing trailing slash
    test_endpoint("https://www.bungie.net/Platform/Destiny2/Manifest", headers)

    # Extra path components
    test_endpoint("https://www.bungie.net/Platform/Destiny2/Manifest/extra/", headers)

    print(f"\n{'='*60}")
    print("Debug complete!")
    print("\nNext steps if issues found:")
    print("1. If API key errors: Set BUNGIE_API_KEY environment variable")
    print("2. If 404 errors on valid endpoints: Check for typos in your code")
    print("3. If connection errors: Check network/firewall settings")
    print("4. For auth endpoints: Ensure OAuth flow is working properly")


if __name__ == "__main__":
    main()
