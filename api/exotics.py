"""
exotics.py — Dynamic Destiny 2 exotic item filter, using the game manifest.

- On first run (or when cache is missing/stale), parses Destiny manifest to find all exotics (weapons & armor).
- Caches exotic hashes and minimal metadata in a single JSON for speed.
- Provides utility functions to check if an item is exotic, or list all known exotics.

Relies on the manifest (see api/manifest.py).
"""

import json
import os

from api.manifest import load_item_definitions


def get_cache_path():
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "RaidAssist",
        "cache",
        "exotics_cache.json",
    )


def build_exotic_cache():
    """
    Scan the loaded Destiny manifest for all exotic weapons and armor.
    Returns:
        dict: {itemHash: {name, type, class, slot}}
    """
    item_defs = load_item_definitions()
    exotics = {}
    for hash_str, item in item_defs.items():
        try:
            if str(item.get("inventory", {}).get("tierType")) == "6":  # 6 = Exotic
                # Weapon or Armor
                item_type = item.get("itemTypeDisplayName", "")
                item_class = item.get(
                    "classType", ""
                )  # 0: Titan, 1: Hunter, 2: Warlock, 3: Any
                item_slot = item.get("equippingBlock", {}).get(
                    "equipmentSlotTypeHash", ""
                )
                exotics[int(hash_str)] = {
                    "name": item.get("displayProperties", {}).get("name", ""),
                    "type": item_type,
                    "class": item_class,
                    "slot": item_slot,
                }
        except Exception:
            continue
    # Cache to disk for fast reloads
    os.makedirs(os.path.dirname(get_cache_path()), exist_ok=True)
    with open(get_cache_path(), "w", encoding="utf-8") as f:
        json.dump(exotics, f, indent=2)
    return exotics


def load_exotic_cache():
    """
    Load the cached exotic dictionary if available, otherwise build it.
    Returns:
        dict: {itemHash: {name, type, class, slot}}
    """
    if os.path.exists(get_cache_path()):
        with open(get_cache_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
            # Convert string keys back to integers to match build_exotic_cache format
            return {int(k): v for k, v in data.items()}
    return build_exotic_cache()


def is_exotic(item_hash):
    """
    Check if an item hash is an exotic (weapon or armor) per manifest cache.
    Args:
        item_hash (int): Destiny item hash.
    Returns:
        bool: True if item is exotic, False otherwise.
    """
    exotics = load_exotic_cache()
    return str(item_hash) in exotics or int(item_hash) in exotics


def all_exotics():
    """
    Return all cached exotics as {itemHash: info}.
    Returns:
        dict
    """
    return load_exotic_cache()
