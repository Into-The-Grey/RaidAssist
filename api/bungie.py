import os
import json
import requests
import time
from typing import Optional, Dict, Any

# Load .env variables if present
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except ImportError:
    pass  # Continue if dotenv is not available; fall back to OS/env/hardcoded

# Fallback implementations first
import logging

def _get_logger_fallback(name):
    return logging.getLogger(name)

def _log_context_fallback(context: str):
    class DummyContext:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            # Dummy context manager - does nothing
            pass

    return DummyContext()

def _safe_execute_fallback(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # Simple fallback logging
        print(f"Safe execute failed: {e}")
        return kwargs.get("default_return")

# Try to import enhanced utils, fall back to basic implementations
try:
    from utils.logging_manager import get_logger, log_context
    from utils.error_handler import safe_execute

    ENHANCED_UTILS_AVAILABLE = True
except ImportError:
    # Use fallback implementations
    get_logger = _get_logger_fallback
    log_context = _log_context_fallback
    safe_execute = _safe_execute_fallback
    
    ENHANCED_UTILS_AVAILABLE = False


# Define constants
USER_AGENT = "RaidAssist/1.0"


from auth_server import get_auth_code


def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Initialize logger
logger = get_logger("raidassist.api")

CACHE_DIR = os.path.join(get_project_root(), "RaidAssist", "cache")
LOG_DIR = os.path.join(get_project_root(), "RaidAssist", "logs")
SESSION_PATH = os.path.expanduser("~/.raidassist/session.json")

# Ensure directories exist
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)

# Fallback order: .env → OS → hardcoded default
API_KEY = os.environ.get("BUNGIE_API_KEY") or "YOUR_BUNGIE_API_KEY"
BUNGIE_CLIENT_ID = os.environ.get("BUNGIE_CLIENT_ID", "")
BUNGIE_CLIENT_SECRET = os.environ.get("BUNGIE_CLIENT_SECRET", "")
BUNGIE_REDIRECT_URI = os.environ.get(
    "BUNGIE_REDIRECT_URI", "https://localhost:8080/callback"
)

PROFILE_CACHE_PATH = os.path.join(CACHE_DIR, "profile.json")

# Rate limiting
LAST_REQUEST_TIME = 0
MIN_REQUEST_INTERVAL = 0.1  # 100ms between requests


def _rate_limit():
    """Enforce rate limiting between API requests."""
    global LAST_REQUEST_TIME
    current_time = time.time()
    time_since_last = current_time - LAST_REQUEST_TIME

    if time_since_last < MIN_REQUEST_INTERVAL:
        sleep_time = MIN_REQUEST_INTERVAL - time_since_last
        time.sleep(sleep_time)

    LAST_REQUEST_TIME = time.time()


def prompt_for_oauth_token():
    """
    Prompt user for OAuth authentication and return access token.

    Returns:
        str: Access token if successful, None if failed

    Raises:
        Exception: If OAuth flow fails
    """
    if not BUNGIE_CLIENT_ID or not BUNGIE_CLIENT_SECRET:
        raise ValueError("Bungie OAuth credentials not configured")

    with log_context("oauth_flow"):
        logger.info("Starting OAuth authentication flow")

        auth_url = (
            f"https://www.bungie.net/en/OAuth/Authorize"
            f"?client_id={BUNGIE_CLIENT_ID}"
            f"&response_type=code"
            f"&redirect_uri={BUNGIE_REDIRECT_URI}"
        )

        try:
            # SSL context (use your local certs for dev; comment out for prod with user browser trust)
            ssl_ctx = None  # or ('localhost.pem', 'localhost-key.pem')
            code = get_auth_code(auth_url, ssl_context=ssl_ctx)

            # Exchange code for token
            logger.info("Exchanging authorization code for access token")
            token_url = "https://www.bungie.net/platform/app/oauth/token/"
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": BUNGIE_CLIENT_ID,
                "client_secret": BUNGIE_CLIENT_SECRET,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            _rate_limit()
            response = requests.post(token_url, data=data, headers=headers, timeout=30)
            response.raise_for_status()

            token_json = response.json()
            access_token = token_json.get("access_token")

            if not access_token:
                raise ValueError("No access token received from Bungie")

            logger.info("OAuth authentication successful")
            return access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during OAuth: {e}")
            raise
        except Exception as e:
            logger.error(f"OAuth authentication failed: {e}")
            raise


def load_token() -> Optional[str]:
    """
    Load Bungie OAuth access token from the session file.

    Returns:
        str: Access token if found and valid, else None.
    """
    with log_context("token_loading"):
        if os.path.exists(SESSION_PATH):
            try:
                with open(SESSION_PATH, "r", encoding="utf-8") as f:
                    session_data = json.load(f)
                    token = session_data.get("access_token", "")

                    if token:
                        # Validate token by checking expiry if available
                        expires_at = session_data.get("expires_at")
                        if expires_at and time.time() > expires_at:
                            logger.info("Token expired, requiring re-authentication")
                            return None

                        logger.debug("Valid token loaded from session")
                        return token

            except (json.JSONDecodeError, KeyError, IOError) as e:
                logger.warning(f"Failed to load token from session: {e}")
            except Exception as e:
                logger.error(f"Unexpected error loading token: {e}")

        # If no token found, prompt for OAuth
        logger.info("No valid token found, initiating OAuth flow")
        try:
            token = prompt_for_oauth_token()
            if token:
                _save_token(token)
            return token
        except Exception as e:
            logger.error(f"Failed to obtain OAuth token: {e}")
            return None


def _save_token(token: str, expires_in: int = 3600):
    """
    Save token to session file with expiration.

    Args:
        token: Access token to save
        expires_in: Token lifetime in seconds (default 1 hour)
    """
    try:
        session_data = {
            "access_token": token,
            "expires_at": time.time() + expires_in,
            "created_at": time.time(),
        }

        with open(SESSION_PATH, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2)

        logger.debug("Token saved to session file")

    except Exception as e:
        logger.error(f"Failed to save token: {e}")


def fetch_profile(
    membership_type: int,
    membership_id: str,
    components: Optional[str] = None,
    retry_attempts: int = 3,
) -> Optional[Dict[str, Any]]:
    """
    Fetches Destiny 2 profile data using Bungie API with robust error handling.

    Args:
        membership_type: Bungie membership type (1=Xbox, 2=PSN, 3=Steam, etc).
        membership_id: Bungie membership ID.
        components: Comma-separated component IDs (optional, uses default if None)
        retry_attempts: Number of retry attempts for failed requests

    Returns:
        dict: Profile data if successful, else None.
    """
    if components is None:
        components = "100,102,103,104,200,201,202,205,300,301,302,304,305,306,307,308,309,310,311,312,313,315,316,317,318"

    with log_context("profile_fetch"):
        logger.info(
            f"Fetching profile for membership {membership_id} (type {membership_type})"
        )

        for attempt in range(retry_attempts):
            try:
                token = load_token()
                if not token:
                    logger.error("No valid OAuth token available")
                    return None

                url = f"https://www.bungie.net/Platform/Destiny2/{membership_type}/Profile/{membership_id}/"
                params = {"components": components}
                headers = {
                    "X-API-Key": API_KEY,
                    "Authorization": f"Bearer {token}",
                    "User-Agent": USER_AGENT,
                }

                logger.debug(
                    f"Making API request (attempt {attempt + 1}/{retry_attempts})"
                )

                _rate_limit()
                response = requests.get(url, params=params, headers=headers, timeout=30)

                # Handle different response codes appropriately
                if response.status_code == 200:
                    profile_data = response.json()

                    # Validate response structure
                    if not _validate_profile_response(profile_data):
                        logger.warning("Invalid profile response structure")
                        return None

                    # Cache the successful response
                    _cache_profile(profile_data)

                    logger.info(f"Profile fetched successfully for {membership_id}")
                    return profile_data

                elif response.status_code == 401:
                    logger.warning("Authentication failed, clearing token")
                    _clear_token()
                    if attempt < retry_attempts - 1:
                        logger.info("Retrying with fresh authentication")
                        continue
                    else:
                        logger.error("Authentication failed after retries")
                        return None

                elif response.status_code == 429:
                    # Rate limited
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited, waiting {retry_after} seconds")
                    if attempt < retry_attempts - 1:
                        time.sleep(retry_after)
                        continue
                    else:
                        logger.error("Rate limit exceeded after retries")
                        return None

                elif response.status_code == 503:
                    # Service unavailable
                    logger.warning("Bungie API service unavailable")
                    if attempt < retry_attempts - 1:
                        time.sleep(5 * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        logger.error("Service unavailable after retries")
                        return None

                else:
                    logger.error(
                        f"API request failed with status {response.status_code}: {response.text}"
                    )
                    response.raise_for_status()

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt < retry_attempts - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                else:
                    logger.error("Request timed out after all retries")
                    return None

            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error on attempt {attempt + 1}")
                if attempt < retry_attempts - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
                else:
                    logger.error("Connection failed after all retries")
                    return None

            except requests.exceptions.RequestException as e:
                logger.error(f"Network error during profile fetch: {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                else:
                    return None

            except Exception as e:
                logger.error(f"Unexpected error during profile fetch: {e}")
                return None

        logger.error("Profile fetch failed after all retry attempts")
        return None


def _validate_profile_response(profile_data: Dict[str, Any]) -> bool:
    """
    Validate that the profile response has the expected structure.

    Args:
        profile_data: Raw API response data

    Returns:
        bool: True if response is valid, False otherwise
    """
    try:
        # Check basic response structure
        if not isinstance(profile_data, dict):
            return False

        if "Response" not in profile_data:
            return False

        response = profile_data["Response"]
        if not isinstance(response, dict):
            return False

        # Check for essential components
        required_components = ["profile", "characters"]
        for component in required_components:
            if component in response:
                return True  # At least one essential component exists

        # If no essential components found, response might still be valid but empty
        logger.warning("Profile response missing essential components")
        return True  # Allow processing anyway

    except Exception as e:
        logger.error(f"Error validating profile response: {e}")
        return False


def _cache_profile(profile_data: Dict[str, Any]):
    """
    Cache profile data to disk with metadata.

    Args:
        profile_data: Profile data to cache
    """
    try:
        cache_data = {
            "profile": profile_data,
            "cached_at": time.time(),
            "cache_version": "1.0",
        }

        with open(PROFILE_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)

        logger.debug("Profile cached successfully")

    except Exception as e:
        logger.error(f"Failed to cache profile: {e}")


def _clear_token():
    """Clear the saved authentication token."""
    try:
        if os.path.exists(SESSION_PATH):
            os.remove(SESSION_PATH)
        logger.info("Authentication token cleared")
    except Exception as e:
        logger.error(f"Failed to clear token: {e}")


def load_cached_profile() -> Optional[Dict[str, Any]]:
    """
    Load cached profile data if available and not too old.

    Returns:
        dict: Cached profile data or None if not available/expired
    """
    try:
        if not os.path.exists(PROFILE_CACHE_PATH):
            return None

        with open(PROFILE_CACHE_PATH, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

        # Check cache age (24 hours max)
        cached_at = cache_data.get("cached_at", 0)
        max_age = 24 * 60 * 60  # 24 hours in seconds

        if time.time() - cached_at > max_age:
            logger.info("Cached profile expired")
            return None

        logger.debug("Loaded cached profile data")
        return cache_data.get("profile")

    except Exception as e:
        logger.warning(f"Failed to load cached profile: {e}")
        return None


def ensure_authenticated() -> bool:
    """
    Ensures the user is authenticated with Bungie OAuth.
    Prompts login if no valid token is found.

    Returns:
        bool: True if authenticated, False if authentication failed.
    """
    with log_context("authentication_check"):
        try:
            token = load_token()
            if token:
                logger.info("User authentication verified")
                return True
            else:
                logger.error("User authentication failed or was cancelled")
                return False

        except Exception as e:
            logger.error(f"Authentication check failed: {e}")
            return False


def get_membership_info(bungie_tag: str) -> Optional[Dict[str, Any]]:
    """
    Get membership information from a Bungie tag (username#1234).

    Args:
        bungie_tag: Bungie tag in format "username#1234"

    Returns:
        dict: Membership information or None if not found
    """
    with log_context("membership_lookup"):
        try:
            # Split tag into username and discriminator
            if "#" not in bungie_tag:
                logger.error("Invalid Bungie tag format, must be 'username#1234'")
                return None

            username, discriminator = bungie_tag.split("#", 1)

            token = load_token()
            if not token:
                logger.error("No authentication token available")
                return None

            url = "https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayer/-1/"
            params = {"displayName": username}
            headers = {
                "X-API-Key": API_KEY,
                "Authorization": f"Bearer {token}",
                "User-Agent": USER_AGENT,
            }

            _rate_limit()
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            players = data.get("Response", [])

            # Find player with matching discriminator
            for player in players:
                if player.get("bungieGlobalDisplayNameCode") == int(discriminator):
                    logger.info(f"Found membership for {bungie_tag}")
                    return {
                        "membership_type": player.get("membershipType"),
                        "membership_id": player.get("membershipId"),
                        "display_name": player.get("displayName"),
                        "bungie_tag": bungie_tag,
                    }

            logger.warning(f"No membership found for {bungie_tag}")
            return None

        except Exception as e:
            logger.error(f"Failed to lookup membership for {bungie_tag}: {e}")
            return None


def test_api_connection() -> bool:
    """
    Test basic API connectivity without authentication.

    Returns:
        bool: True if API is reachable, False otherwise
    """
    try:
        url = "https://www.bungie.net/Platform/Destiny2/Manifest/"
        headers = {"X-API-Key": API_KEY, "User-Agent": USER_AGENT}

        _rate_limit()
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            logger.info("API connection test successful")
            return True
        else:
            logger.warning(
                f"API connection test failed with status {response.status_code}"
            )
            return False

    except Exception as e:
        logger.error(f"API connection test failed: {e}")
        return False
