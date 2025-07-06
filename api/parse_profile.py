"""
parse_profile.py — Extracts red border, catalyst, and exotic data from Bungie profile.
"""

import json
import os
import logging
from api.exotics import all_exotics  # Manifest-driven exotic lookup


def get_project_root():
    """
    Returns the project root directory.
    Returns:
        str: Path to the project root directory.
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


PROFILE_PATH = os.path.join(get_project_root(), "RaidAssist", "cache", "profile.json")
LOG_PATH = os.path.join(get_project_root(), "RaidAssist", "logs", "parse_profile.log")

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def load_profile():
    """
    Loads cached Bungie profile data from disk.
    Returns:
        dict or None: Profile data if found, else None.
    """
    try:
        with open(PROFILE_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning("Cached profile not found.")
        return None
    except Exception as e:
        logging.error(f"Error loading profile: {e}")
        return None


def extract_red_borders(profile_data):
    """
    Extract red border (pattern) progress from the profile data.
    Args:
        profile_data (dict): Profile JSON as loaded from Bungie API.
    Returns:
        list[dict]: List of items with pattern progress/percent.
    """
    red_borders = []
    item_components = (
        profile_data.get("Response", {}).get("itemComponents", {}).get("instances", {})
    )
    patterns = (
        profile_data.get("Response", {}).get("itemComponents", {}).get("objectives", {})
    )
    for item_id, components in item_components.items():
        objectives = patterns.get(item_id, {}).get("objectives", [])
        pattern_obj = None
        for obj in objectives:
            if obj.get("completionValue", 0) > 1:
                pattern_obj = obj
                break
        if pattern_obj:
            progress = pattern_obj.get("progress", 0)
            needed = pattern_obj.get("completionValue", 1)
            percent = int(100 * progress / needed) if needed else 0
            red_borders.append(
                {
                    "itemInstanceId": item_id,
                    "progress": progress,
                    "needed": needed,
                    "percent": percent,
                }
            )
    return red_borders


def extract_exotics(profile_data):
    """
    Extracts all owned exotic items from profile inventory.
    Uses manifest-driven lookup for exotics.
    Args:
        profile_data (dict): Profile JSON as loaded from Bungie API.
    Returns:
        list[dict]: List of exotic items in inventory.
    """
    inventory = (
        profile_data.get("Response", {})
        .get("profileInventory", {})
        .get("data", {})
        .get("items", [])
    )
    exotic_hashes = set(int(h) for h in all_exotics().keys())
    exotics = [
        item for item in inventory if int(item.get("itemHash", 0)) in exotic_hashes
    ]
    return exotics


def extract_catalysts(profile_data):
    """
    Extract catalyst progress for all items in the profile data.
    Args:
        profile_data (dict): Profile JSON as loaded from Bungie API.
    Returns:
        list[dict]: List of catalysts with progress and completion status.
    """
    catalyst_info = []
    instances = (
        profile_data.get("Response", {}).get("itemComponents", {}).get("instances", {})
    )
    objectives = (
        profile_data.get("Response", {}).get("itemComponents", {}).get("objectives", {})
    )
    for item_id, item_data in instances.items():
        item_objectives = objectives.get(item_id, {}).get("objectives", [])
        for obj in item_objectives:
            if obj.get("completionValue", 0) > 1:
                progress = obj.get("progress", 0)
                needed = obj.get("completionValue", 1)
                percent = int(100 * progress / needed) if needed else 0
                catalyst_info.append(
                    {
                        "itemInstanceId": item_id,
                        "progress": progress,
                        "needed": needed,
                        "percent": percent,
                    }
                )
    return catalyst_info


# Placeholders for future advanced catalyst detection (if needed)
def get_known_catalyst_plugs():
    """
    Placeholder for known catalyst plug hashes.
    Returns:
        set: Plug hashes for known catalysts.
    """
    return set()


def get_known_catalyst_objectives():
    """
    Placeholder for known catalyst objective hashes.
    Returns:
        set: Objective hashes for known catalysts.
    """
    return set()
