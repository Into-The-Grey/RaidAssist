import os
import json
import requests
import logging

# Load .env variables if present
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except ImportError:
    pass  # Continue if dotenv is not available; fall back to OS/env/hardcoded

from auth_server import get_auth_code


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
BUNGIE_CLIENT_ID = os.environ["BUNGIE_CLIENT_ID"]
BUNGIE_CLIENT_SECRET = os.environ["BUNGIE_CLIENT_SECRET"]
BUNGIE_REDIRECT_URI = os.environ["BUNGIE_REDIRECT_URI"]

PROFILE_CACHE_PATH = os.path.join(CACHE_DIR, "profile.json")


def prompt_for_oauth_token():
    auth_url = (
        f"https://www.bungie.net/en/OAuth/Authorize"
        f"?client_id={BUNGIE_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={BUNGIE_REDIRECT_URI}"
    )
    # SSL context (use your local certs for dev; comment out for prod with user browser trust)
    ssl_ctx = None  # or ('localhost.pem', 'localhost-key.pem')
    code = get_auth_code(auth_url, ssl_context=ssl_ctx)
    # Exchange code for token
    token_url = "https://www.bungie.net/platform/app/oauth/token/"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": BUNGIE_CLIENT_ID,
        "client_secret": BUNGIE_CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(token_url, data=data, headers=headers)
    r.raise_for_status()
    token_json = r.json()
    # Store access_token for API use
    return token_json["access_token"]


def load_token():
    """
    Load Bungie OAuth access token from the session file.
    Returns:
        str: Access token if found, else None.
    """
    if os.path.exists(SESSION_PATH):
        try:
            with open(SESSION_PATH, "r") as f:
                token = json.load(f).get("access_token", "")
                if token:
                    return token
        except Exception as e:
            logging.error(f"Failed to load token: {e}")

    # If no token found, prompt for OAuth
    logging.info("No valid token found, initiating OAuth flow")
    try:
        token = prompt_for_oauth_token()
        # Save token to session file
        os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
        with open(SESSION_PATH, "w") as f:
            json.dump({"access_token": token}, f)
        return token
    except Exception as e:
        logging.error(f"Failed to obtain OAuth token: {e}")
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


def ensure_authenticated():
    """
    Ensures the user is authenticated with Bungie OAuth.
    Prompts login if no valid token is found. Returns True if authenticated, else False.
    """
    token = load_token()
    if token:
        return True
    else:
        logging.error("User is not authenticated. Login flow failed or was cancelled.")
        return False
