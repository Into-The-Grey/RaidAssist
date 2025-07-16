"""
oauth.py — Bungie OAuth PKCE handler for RaidAssist.

Implements OAuth2 PKCE (Proof Key for Code Exchange) flow for secure authentication
without requiring client secrets. Bundles all necessary public API keys in the code.

- Uses PKCE flow with code_verifier/code_challenge for security
- Handles browser-based OAuth flow with local callback server
- Manages access/refresh tokens automatically
- No user configuration required - all keys bundled in app
"""

import base64
import hashlib
import json
import logging
import os
import secrets
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import requests

# ==== BUNDLED PUBLIC CONFIGURATION ====
# These are public keys that can be safely bundled with the application
# NOTE: These are placeholder values. For a production application, you would
# need to register your own OAuth application at https://www.bungie.net/en/Application
# and replace these values with your actual client credentials.

BUNGIE_API_KEY = "your_bungie_api_key_here"  # Replace with your actual API key
BUNGIE_CLIENT_ID = "your_client_id_here"  # Replace with your actual client ID
BUNGIE_REDIRECT_URI = "http://localhost:7777/callback"  # Local callback URL

# For development, allow environment variable override
if os.environ.get("BUNGIE_API_KEY"):
    BUNGIE_API_KEY = os.environ.get("BUNGIE_API_KEY")
if os.environ.get("BUNGIE_CLIENT_ID"):
    BUNGIE_CLIENT_ID = os.environ.get("BUNGIE_CLIENT_ID")
if os.environ.get("BUNGIE_REDIRECT_URI"):
    BUNGIE_REDIRECT_URI = os.environ.get("BUNGIE_REDIRECT_URI")

# Runtime configuration
REDIRECT_PORT = 7777
SESSION_PATH = os.path.expanduser("~/.raidassist/session.json")
LOG_PATH = os.path.expanduser("~/.raidassist/oauth.log")

# Ensure directories exist
os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Bungie OAuth endpoints
OAUTH_AUTHORIZE_URL = "https://www.bungie.net/en/OAuth/Authorize"
OAUTH_TOKEN_URL = "https://www.bungie.net/Platform/App/OAuth/Token/"

# ==== CONFIGURATION VALIDATION ====


def validate_oauth_config():
    """
    Validate that OAuth configuration is properly set up.

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    # Allow test mode to bypass validation
    if os.environ.get("RAIDASSIST_TEST_MODE") == "true":
        return (True, "Test mode - validation bypassed")

    if BUNGIE_API_KEY == "your_bungie_api_key_here":
        return (
            False,
            """
OAuth Configuration Error: Missing Bungie API Key

To use RaidAssist, you need to set up a Bungie OAuth application:

1. Visit https://www.bungie.net/en/Application
2. Create a new application or use an existing one
3. Set the redirect URL to: http://localhost:7777/callback
4. Set the OAuth Client Type to: Confidential
5. Set your environment variables:
   - BUNGIE_API_KEY=your_api_key_here
   - BUNGIE_CLIENT_ID=your_client_id_here

For more information, see the RaidAssist setup documentation.
""",
        )

    if BUNGIE_CLIENT_ID == "your_client_id_here":
        return (
            False,
            """
OAuth Configuration Error: Missing Client ID

To use RaidAssist, you need to set up a Bungie OAuth application:

1. Visit https://www.bungie.net/en/Application  
2. Create a new application or use an existing one
3. Set the redirect URL to: http://localhost:7777/callback
4. Set the OAuth Client Type to: Confidential
5. Set your environment variables:
   - BUNGIE_API_KEY=your_api_key_here
   - BUNGIE_CLIENT_ID=your_client_id_here

For more information, see the RaidAssist setup documentation.
""",
        )

    return True, ""


# ==== PKCE UTILITIES ====


def generate_code_verifier():
    """Generate a cryptographically secure code verifier for PKCE."""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")


def generate_code_challenge(code_verifier):
    """Generate code challenge from verifier using SHA256."""
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


# ==== SESSION MANAGEMENT ====


def save_session(data):
    """Save OAuth session data to file."""
    with open(SESSION_PATH, "w") as f:
        json.dump(data, f, indent=2)
    logging.info("OAuth session saved to %s", SESSION_PATH)


def load_session():
    """Load OAuth session data from file."""
    if os.path.exists(SESSION_PATH):
        with open(SESSION_PATH, "r") as f:
            return json.load(f)
    return None


def is_token_expired(session):
    """Check if the access token in session has expired."""
    if not session or "expires_at" not in session:
        return True
    return time.time() >= session["expires_at"]


def refresh_token(session):
    """
    Refresh an expired access token using the refresh token.

    Note: PKCE flow still requires refresh token exchange, but no client secret.
    """
    if not session or "refresh_token" not in session:
        logging.warning("No refresh token available")
        return None

    data = {
        "grant_type": "refresh_token",
        "refresh_token": session["refresh_token"],
        "client_id": BUNGIE_CLIENT_ID,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-API-Key": BUNGIE_API_KEY,
    }

    try:
        resp = requests.post(OAUTH_TOKEN_URL, data=data, headers=headers, timeout=30)
        if resp.status_code == 200:
            token_data = resp.json()
            session["access_token"] = token_data["access_token"]
            session["refresh_token"] = token_data["refresh_token"]
            session["expires_at"] = time.time() + token_data["expires_in"] - 10
            save_session(session)
            logging.info("Token refreshed successfully")
            return session
        else:
            logging.warning("Refresh token failed: %s", resp.text)
            return None
    except requests.RequestException as e:
        logging.error("Network error during token refresh: %s", e)
        return None


class OAuthHandler(BaseHTTPRequestHandler):
    """HTTP handler to receive OAuth authorization code from Bungie."""

    server_version = "RaidAssistBungieOAuth/1.0"
    _code = None
    _error = None

    def do_GET(self):
        """Handle OAuth callback from Bungie."""
        url = urlparse(self.path)
        query = parse_qs(url.query)

        if "error" in query:
            OAuthHandler._error = query["error"][0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Authorization Failed</h1>"
                b"<p>There was an error with the Bungie authentication.</p>"
                b"<p>You can close this window and try again in RaidAssist.</p>"
                b"<style>body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }</style>"
                b"</body></html>"
            )
        elif "code" in query:
            OAuthHandler._code = query["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>RaidAssist Authentication Complete!</h1>"
                b"<p>Successfully authenticated with Bungie.net</p>"
                b"<p>You may now close this window and return to RaidAssist.</p>"
                b"<style>body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }</style>"
                b"</body></html>"
            )
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Error</h1>"
                b"<p>No authorization code received from Bungie.</p>"
                b"<style>body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }</style>"
                b"</body></html>"
            )

    def log_message(self, format, *args):
        """Suppress default HTTP server logging."""
        pass

    @staticmethod
    def wait_for_code(timeout=180):
        """Start HTTP server and wait for OAuth code with timeout."""
        server = HTTPServer(("localhost", REDIRECT_PORT), OAuthHandler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        logging.info("OAuth HTTP server started on port %d", REDIRECT_PORT)

        start_time = time.time()
        while OAuthHandler._code is None and OAuthHandler._error is None:
            if time.time() - start_time > timeout:
                server.shutdown()
                raise TimeoutError(f"OAuth flow timed out after {timeout} seconds")
            time.sleep(0.2)

        server.shutdown()

        if OAuthHandler._error:
            error = OAuthHandler._error
            OAuthHandler._error = None
            raise ValueError(f"OAuth error: {error}")

        code = OAuthHandler._code
        OAuthHandler._code = None
        return code


def authorize():
    """
    Perform OAuth PKCE login, save session, and return token dict.

    Uses PKCE flow for enhanced security without client secrets.
    """
    logging.info("Starting OAuth PKCE authentication flow")

    # Generate PKCE parameters
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    # Build authorization URL with PKCE parameters
    auth_params = {
        "client_id": BUNGIE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": BUNGIE_REDIRECT_URI,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    auth_url = f"{OAUTH_AUTHORIZE_URL}?{urlencode(auth_params)}"

    print("Opening Bungie login in your browser...")
    logging.info("Opening browser for OAuth authorization")

    try:
        webbrowser.open(auth_url)
    except Exception as e:
        logging.warning(f"Failed to open browser automatically: {e}")
        print(f"Please open this URL manually: {auth_url}")

    # Wait for authorization code
    try:
        code = OAuthHandler.wait_for_code()
        logging.info("Authorization code received")
    except (TimeoutError, ValueError) as e:
        logging.error(f"OAuth authorization failed: {e}")
        raise Exception(f"OAuth authorization failed: {e}")

    # Exchange code for tokens using PKCE
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": BUNGIE_CLIENT_ID,
        "code_verifier": code_verifier,
        "redirect_uri": BUNGIE_REDIRECT_URI,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-API-Key": BUNGIE_API_KEY,
    }

    try:
        resp = requests.post(
            OAUTH_TOKEN_URL, data=token_data, headers=headers, timeout=30
        )
        if resp.status_code != 200:
            error_msg = f"Token exchange failed: {resp.status_code} - {resp.text}"
            logging.error(error_msg)
            raise Exception(error_msg)

        token_response = resp.json()

        # Add expiration time
        token_response["expires_at"] = time.time() + token_response["expires_in"] - 10

        save_session(token_response)
        logging.info("OAuth PKCE authentication completed successfully")
        print("Authorization complete. You are now logged in to Bungie.")

        return token_response

    except requests.RequestException as e:
        error_msg = f"Network error during token exchange: {e}"
        logging.error(error_msg)
        raise Exception(error_msg)


def get_access_token():
    """
    Get valid access token (auto-refresh or prompt login if needed).

    Returns:
        str: Valid access token for API calls

    Raises:
        Exception: If authentication fails or configuration is invalid
    """
    # Support test mode
    if os.environ.get("RAIDASSIST_TEST_MODE") == "true":
        test_token = os.environ.get("TEST_TOKEN", "test_token")
        logging.info(f"Test mode - returning test token: {test_token}")
        return test_token

    # First validate OAuth configuration
    is_valid, error_msg = validate_oauth_config()
    if not is_valid:
        logging.error("OAuth configuration invalid")
        raise Exception(error_msg.strip())

    session = load_session()

    # Check if we have a valid token
    if session and not is_token_expired(session):
        logging.info("Using existing valid access token")
        return session["access_token"]

    # Try to refresh if we have a refresh token
    if session and "refresh_token" in session:
        logging.info("Attempting to refresh expired token")
        refreshed_session = refresh_token(session)
        if refreshed_session and not is_token_expired(refreshed_session):
            return refreshed_session["access_token"]

    # No valid session - start OAuth flow
    logging.info("No valid token found, starting OAuth PKCE flow")
    try:
        token_data = authorize()
        return token_data["access_token"]
    except Exception as e:
        logging.error(f"OAuth authentication failed: {e}")
        raise Exception(f"Failed to authenticate with Bungie: {e}")


def clear_session():
    """Clear stored OAuth session (logout)."""
    if os.path.exists(SESSION_PATH):
        os.remove(SESSION_PATH)
        logging.info("OAuth session cleared")
        print("Logged out successfully.")
    else:
        logging.info("No session to clear")
        print("No active session found.")


def is_authenticated():
    """
    Check if user is currently authenticated.

    Returns:
        bool: True if authenticated with valid token
    """
    session = load_session()
    return session is not None and not is_token_expired(session)
