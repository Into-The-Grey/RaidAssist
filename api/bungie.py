import os
import json
import requests
import logging

# Load .env variables if present
try:
    from dotenv import load_dotenv # type: ignore

    load_dotenv()
except ImportError:
    pass  # Continue if dotenv is not available; fall back to OS/env/hardcoded

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CACHE_DIR = os.path.join(get_project_root(), "RaidAssist", "cache")
LOG_DIR = os.path.join(get_project_root(), "RaidAssist", "logs")
SESSION_PATH = os.path.expanduser("~/.raidassist/session.json")

# Set up basic logging
LOG_PATH = os.path.join(LOG_DIR, "bungie_api.log")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Fallback order: .env → OS → hardcoded default
API_KEY = os.environ.get("BUNGIE_API_KEY") or "YOUR_BUNGIE_API_KEY"

PROFILE_CACHE_PATH = os.path.join(CACHE_DIR, "profile.json")


def load_token():
    """
    Load Bungie OAuth access token from the session file.
    Returns:
        str: Access token if found, else None.
    """
    if os.path.exists(SESSION_PATH):
        try:
            with open(SESSION_PATH, "r") as f:
                return json.load(f).get("access_token", "")
        except Exception as e:
            logging.error(f"Failed to load token: {e}")
    else:
        logging.warning("Session file not found for token loading.")
    return None


def fetch_profile(membership_type, membership_id):
    """
    Fetches Destiny 2 profile data using Bungie API.
    Args:
        membership_type (int or str): Bungie membership type (1=Xbox, 2=PSN, 3=Steam, etc).
        membership_id (str): Bungie membership ID.
    Returns:
        dict: Profile data if successful, else None.
    """
    token = load_token()
    if not token:
        logging.error("No Bungie OAuth token found. Cannot fetch profile.")
        return None

    url = f"https://www.bungie.net/Platform/Destiny2/{membership_type}/Profile/{membership_id}/"
    params = {
        "components": "100,102,103,104,200,201,202,205,300,301,302,304,305,306,307,308,309,310,311,312,313,315,316,317,318"
    }
    headers = {
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {token}",
    }

    try:
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        profile = resp.json()
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(PROFILE_CACHE_PATH, "w") as f:
            json.dump(profile, f, indent=2)
        logging.info(f"Profile fetched and cached for membership_id={membership_id}")
        return profile
    except Exception as e:
        logging.error(f"Failed to fetch or cache profile: {e}")
        return None
