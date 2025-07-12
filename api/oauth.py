"""
oauth.py — Bungie OAuth handler for RaidAssist.

- Opens browser to Bungie login/authorization page (first run or expired session)
- Runs a local webserver to capture OAuth code from Bungie
- Exchanges code for access/refresh tokens, saves in ~/.raidassist/session.json
- Handles automatic token refresh (if expired)
"""

import os
import json
import threading
import requests
import logging
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ==== CONFIGURATION ====
CLIENT_ID = os.environ.get("BUNGIE_CLIENT_ID", "YOUR_CLIENT_ID")
CLIENT_SECRET = os.environ.get("BUNGIE_CLIENT_SECRET", "")
REDIRECT_PORT = int(os.environ.get("BUNGIE_REDIRECT_PORT", "7777"))
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/"
SESSION_PATH = os.path.expanduser("~/.raidassist/session.json")
LOG_PATH = os.path.expanduser("~/.raidassist/oauth.log")

os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

OAUTH_AUTHORIZE_URL = (
    f"https://www.bungie.net/en/OAuth/Authorize?client_id={CLIENT_ID}"
    f"&response_type=code&redirect_uri={REDIRECT_URI}"
)
OAUTH_TOKEN_URL = "https://www.bungie.net/Platform/App/OAuth/Token/"


def save_session(data):
    with open(SESSION_PATH, "w") as f:
        json.dump(data, f, indent=2)
    logging.info("OAuth session saved to %s", SESSION_PATH)


def load_session():
    if os.path.exists(SESSION_PATH):
        with open(SESSION_PATH, "r") as f:
            return json.load(f)
    return None


def is_token_expired(session):
    import time

    if not session or "expires_at" not in session:
        return True
    return time.time() >= session["expires_at"]


def refresh_token(session):
    data = {
        "grant_type": "refresh_token",
        "refresh_token": session["refresh_token"],
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    resp = requests.post(OAUTH_TOKEN_URL, data=data)
    if resp.status_code == 200:
        token_data = resp.json()
        session["access_token"] = token_data["access_token"]
        session["refresh_token"] = token_data["refresh_token"]
        import time

        session["expires_at"] = time.time() + token_data["expires_in"] - 10
        save_session(session)
        return session
    else:
        logging.warning("Refresh token failed: %s", resp.text)
        return None


class OAuthHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler to receive Bungie OAuth code and store it."""

    server_version = "RaidAssistBungieOAuth/1.0"
    _code = None

    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        if "code" in query:
            OAuthHandler._code = query["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Authorization successful!</h1><p>You may now close this window and return to RaidAssist.</p></body></html>"
            )
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: Authorization code not found.")

    @staticmethod
    def wait_for_code():
        """Start HTTP server in thread, block until code received."""
        server = HTTPServer(("localhost", REDIRECT_PORT), OAuthHandler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        logging.info("OAuth HTTP server started on port %d", REDIRECT_PORT)
        while OAuthHandler._code is None:
            import time

            time.sleep(0.2)
        server.shutdown()
        code = OAuthHandler._code
        OAuthHandler._code = None
        return code


def authorize():
    """Perform OAuth login, save session, and return token dict."""
    print("Opening Bungie login in your browser...")
    webbrowser.open(OAUTH_AUTHORIZE_URL)
    code = OAuthHandler.wait_for_code()
    # Exchange code for tokens
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
    }
    resp = requests.post(OAUTH_TOKEN_URL, data=data)
    if resp.status_code != 200:
        raise Exception(f"Token exchange failed: {resp.text}")
    token_data = resp.json()
    # Add 'expires_at'
    import time

    token_data["expires_at"] = time.time() + token_data["expires_in"] - 10
    save_session(token_data)
    print("Authorization complete. You are now logged in to Bungie.")
    return token_data


def get_access_token():
    """Get valid access token (auto-refresh or prompt login if needed)."""
    session = load_session()
    if session and not is_token_expired(session):
        return session["access_token"]
    if session and "refresh_token" in session:
        session = refresh_token(session)
        if session and not is_token_expired(session):
            return session["access_token"]
    # No valid session—prompt login
    token_data = authorize()
    return token_data["access_token"]
