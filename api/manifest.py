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

# Load .env variables if present
try:
    from dotenv import load_dotenv # type: ignore

    load_dotenv()
except ImportError:
    pass  # Continue if dotenv is not available; fall back to OS/env/hardcoded

BASE_URL = "https://www.bungie.net"
MANIFEST_URL = f"{BASE_URL}/Platform/Destiny2/Manifest/"
DEST_DIR = "RaidAssist/cache/manifest"
MANIFEST_FILE = os.path.join(DEST_DIR, "DestinyInventoryItemDefinition.json")
LOG_PATH = "RaidAssist/logs/manifest.log"

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
