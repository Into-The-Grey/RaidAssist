# RaidAssist — Destiny 2 Progression Tracker and Overlay
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact: ncacord@protonmail.com


"""
manifest.py — Download, cache, and load the Destiny 2 manifest for item lookups.

- Fetches manifest JSON from Bungie
- Loads DestinyInventoryItemDefinition
- Provides helpers for display name lookup
"""


import os
import requests
import json
import logging


def get_project_root():
    """
    Returns the absolute path to the project root directory.
    Assumes this file is in RaidAssist/api/ and looks for the parent containing RaidAssist/.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while current_dir != os.path.dirname(current_dir):  # Stop at filesystem root
        if os.path.basename(current_dir) == "RaidAssist":
            return os.path.dirname(current_dir)
        current_dir = os.path.dirname(current_dir)
    return os.path.dirname(os.path.dirname(current_dir))  # Fallback


# Load .env variables if present
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except ImportError:
    pass  # Continue if dotenv is not available; fall back to OS/env/hardcoded

BASE_URL = "https://www.bungie.net"
MANIFEST_URL = f"{BASE_URL}/Platform/Destiny2/Manifest/"
DEST_DIR = os.path.join(get_project_root(), "RaidAssist", "cache", "manifest")
MANIFEST_FILE = os.path.join(DEST_DIR, "DestinyInventoryItemDefinition.json")
LOG_PATH = os.path.join(get_project_root(), "RaidAssist", "logs", "manifest.log")

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Fallback order: .env → OS → hardcoded default
API_KEY = os.environ.get("BUNGIE_API_KEY") or "YOUR_BUNGIE_API_KEY"
HEADERS = {"X-API-Key": API_KEY}


def fetch_manifest():
    """
    Downloads the Destiny 2 InventoryItemDefinition manifest.
    Saves to cache for future lookups.
    """
    os.makedirs(DEST_DIR, exist_ok=True)
    try:
        logging.info("Fetching manifest metadata...")
        res = requests.get(MANIFEST_URL, headers=HEADERS)
        res.raise_for_status()
        path = res.json()["Response"]["jsonWorldComponentContentPaths"]["en"][
            "DestinyInventoryItemDefinition"
        ]
        url = BASE_URL + path

        logging.info("Downloading manifest content...")
        manifest_data = requests.get(url, headers=HEADERS)
        manifest_data.raise_for_status()
        with open(MANIFEST_FILE, "wb") as f:
            f.write(manifest_data.content)

        logging.info("Manifest downloaded and saved at %s", MANIFEST_FILE)
    except Exception as e:
        logging.error(f"Failed to fetch or save manifest: {e}")
        raise


def load_item_definitions():
    """
    Loads DestinyInventoryItemDefinition from the local manifest cache.
    Returns:
        dict: All Destiny items keyed by their item hash (as string).
    """
    if not os.path.exists(MANIFEST_FILE):
        logging.warning("Manifest not found. Run fetch_manifest() first.")
        return {}
    try:
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load manifest file: {e}")
        return {}


def get_item_display(item_hash, item_defs):
    """
    Returns the display name for a given item hash.
    Args:
        item_hash (int or str): The Destiny item hash.
        item_defs (dict): Destiny item definitions.
    Returns:
        str: Human-readable name for the item.
    """
    item = item_defs.get(str(item_hash))
    if not item:
        return f"Unknown Item ({item_hash})"
    return item.get("displayProperties", {}).get("name", f"Unnamed ({item_hash})")


def get_item_info(item_hash, item_defs):
    """
    Get comprehensive item information including name, type, description, and icon.

    Args:
        item_hash (int or str): The Destiny item hash.
        item_defs (dict): Destiny item definitions.

    Returns:
        dict: Dictionary containing item information with keys:
            - name: Human-readable name
            - type: Item type/category
            - description: Item description
            - icon: Icon path
            - archetype: Item archetype if available
    """
    item = item_defs.get(str(item_hash))
    if not item:
        return {
            "name": f"Unknown Item ({item_hash})",
            "type": "Unknown",
            "description": "Item information not available",
            "icon": "",
            "archetype": "",
        }

    display_props = item.get("displayProperties", {})

    # Extract item type information
    item_type = "Unknown"
    if "itemTypeDisplayName" in item:
        item_type = item["itemTypeDisplayName"]
    elif "itemTypeAndTierDisplayName" in item:
        item_type = item["itemTypeAndTierDisplayName"]

    return {
        "name": display_props.get("name", f"Unnamed ({item_hash})"),
        "type": item_type,
        "description": display_props.get("description", ""),
        "icon": display_props.get("icon", ""),
        "archetype": item.get("itemSubType", ""),
    }
