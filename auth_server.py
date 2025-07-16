# RaidAssist — Destiny 2 Progression Tracker and Overlay
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>
#
# Legacy auth_server.py - maintained for compatibility
# New OAuth implementation uses PKCE flow in api/oauth.py

import html
import os
import threading
import webbrowser

# Import new OAuth implementation
try:
    from api.oauth import get_access_token, is_authenticated, clear_session

    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False
    print("⚠️  OAuth module not available")

# Flask imports with fallback
try:
    from flask import Flask, request  # type: ignore

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️  Flask not available - OAuth authentication disabled")
    print("   Install with: pip install flask")

# Enhanced logging
try:
    from utils.logging_manager import get_logger, log_context

    logger = get_logger("raidassist.auth")
    LOGGING = True
except ImportError:
    import logging

    LOG_PATH = os.path.join(os.path.dirname(__file__), "logs", "auth_server.log")
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logger = logging.getLogger("auth_server")
    LOGGING = False


# Compatibility functions for new OAuth implementation
def get_auth_code(auth_url, ssl_context=None, timeout=180):
    """
    Compatibility wrapper for legacy auth_server usage.

    Note: The new OAuth PKCE implementation handles everything internally.
    This function exists for backward compatibility but will trigger
    the full OAuth flow when called.

    Args:
        auth_url: Legacy parameter (ignored - PKCE flow generates its own)
        ssl_context: Legacy parameter (ignored)
        timeout: Legacy parameter (ignored)

    Returns:
        str: Access token (not auth code) from OAuth flow

    Raises:
        RuntimeError: If OAuth flow fails
    """
    if not OAUTH_AVAILABLE:
        raise RuntimeError("OAuth not available - check api.oauth module")

    try:
        logger.info("Legacy auth_server called - redirecting to modern OAuth PKCE flow")
        # The new implementation handles the complete flow
        token = get_access_token()
        if token:
            logger.info("OAuth PKCE flow completed successfully")
            return token
        else:
            raise RuntimeError("OAuth authentication failed")
    except Exception as e:
        logger.error(f"OAuth flow failed: {e}")
        raise RuntimeError(f"Authentication failed: {e}")


def run_auth_server(ssl_context=None):
    """
    Compatibility wrapper - no longer needed with PKCE flow.

    The new OAuth implementation uses a lightweight HTTP server
    internally only during the OAuth callback phase.
    """
    logger.info("Legacy run_auth_server called - modern OAuth handles this internally")
    if ssl_context:
        logger.debug("SSL context ignored in modern OAuth PKCE flow")


# Legacy Flask app (maintained for compatibility)
if FLASK_AVAILABLE:
    app = Flask(__name__)
    received_code = {}

    @app.route("/callback")
    def callback():
        """Legacy callback - OAuth PKCE handles this internally now."""
        logger.warning("Legacy Flask callback called - OAuth PKCE should handle this")
        return (
            "<h2>RaidAssist OAuth</h2>"
            + "<p>This is the legacy callback. Modern OAuth PKCE handles authentication internally.</p>"
            + "<p>If you see this, please restart RaidAssist.</p>",
            200,
        )

else:
    # Fallback implementations when Flask is not available
    received_code = {}

    class nullcontext:  # type: ignore
        """Fallback context manager when enhanced logging not available."""

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def run_auth_server(ssl_context=None):
        """Fallback - uses OAuth PKCE flow instead."""
        logger.info("Flask not available - using OAuth PKCE flow")
        if ssl_context:
            logger.debug("SSL context not needed for OAuth PKCE")

    def get_auth_code(auth_url, ssl_context=None, timeout=180):
        """Fallback - redirects to OAuth PKCE flow."""
        if not OAUTH_AVAILABLE:
            raise RuntimeError("OAuth not available and Flask not installed")
        return get_access_token()


# Also define nullcontext for when Flask is available but enhanced logging is not
if FLASK_AVAILABLE and not LOGGING:

    class nullcontext:
        """Fallback context manager when enhanced logging not available."""

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass
