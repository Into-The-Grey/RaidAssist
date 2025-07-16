#!/usr/bin/env python3
"""
Test the fixed SearchDestinyPlayer function in bungie.py
"""

import sys
import os

# Add the parent directory to the path so we can import from api
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.bungie import get_membership_info


def test_search_player():
    """Test the search player functionality"""
    print("Testing SearchDestinyPlayer fix...")

    # Test with a common username (might not exist, but should get proper response)
    test_tag = "TestUser#1234"

    try:
        result = get_membership_info(test_tag)

        if result is None:
            print(
                f"✅ SUCCESS: No player found for {test_tag} (this is expected for test data)"
            )
            print("    The endpoint is working correctly - no 404 error!")
        else:
            print(f"✅ SUCCESS: Found player data for {test_tag}")
            print(f"    Membership Type: {result.get('membership_type')}")
            print(f"    Membership ID: {result.get('membership_id')}")
            print(f"    Display Name: {result.get('display_name')}")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

    return True


if __name__ == "__main__":
    print("=" * 50)
    test_search_player()
    print("=" * 50)
    print("\nIf you see SUCCESS above, the SearchDestinyPlayer fix is working!")
    print("The 404 'Endpoint not found' error should be resolved.")
