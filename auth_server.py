# RaidAssist — Destiny 2 Progression Tracker and Overlay
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>
#
# Enhanced auth_server.py with improved logging and error handling

import html
import os
import threading
import webbrowser

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

# Only define Flask app and routes when Flask is available
if FLASK_AVAILABLE:
    app = Flask(__name__)
    received_code = {}

    @app.route("/callback")
    def callback():
        """Handle OAuth callback from Bungie API."""
        try:
            if LOGGING:
                from contextlib import nullcontext

                context_manager = log_context("oauth_callback")
            else:
                from contextlib import nullcontext

                context_manager = nullcontext()

            with context_manager:
                code = request.args.get("code")
                error = request.args.get("error")

                if error:
                    sanitized_error = error.replace("\n", "").replace("\r", "")
                    logger.error(f"OAuth error: {sanitized_error}")
                    return (
                        "<h3>🚫 Authentication Failed</h3>"
                        f"<p>Error from Bungie: <b>{html.escape(error)}</b></p>"
                        "<p>Please try again or check your network connection.</p>",
                        400,
                    )

                if not code:
                    logger.warning("No code in OAuth callback")
                    return (
                        "<h3>🚫 Authentication Error</h3>"
                        + "<p>No authorization code was received from Bungie.</p>"
                        + "<p>Please try the authentication process again.</p>",
                        400,
                    )

                received_code["code"] = code
                logger.info("OAuth code received successfully")
                return (
                    "<h2>🎮 RaidAssist Authentication Complete!</h2>"
                    + "<p>✅ Successfully authenticated with Bungie.net</p>"
                    + "<p>You may now return to the app. This window can be closed.</p>"
                    + "<style>body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }</style>",
                    200,
                )
        except Exception as e:
            logger.error(f"Error in OAuth callback: {e}")
            return (
                "<h3>🚫 Authentication Error</h3>"
                + "<p>An unexpected error occurred. Please try again later.</p>"
                + "<p>If the issue persists, contact support.</p>",
                500,
            )

else:
    # Fallback implementations when Flask is not available
    received_code = {}

    class nullcontext:  # type: ignore
        """Fallback context manager when enhanced logging not available."""

        def __enter__(self):
            return self

        def __exit__(self, *args):
            # Empty implementation for fallback compatibility
            pass

    def run_auth_server(ssl_context=None):
        """Fallback auth server - not functional without Flask."""
        logger.error("Cannot run auth server - Flask not available")
        if ssl_context:  # Use parameter to avoid lint warning
            logger.warning("SSL context provided but Flask not available")
        received_code["error"] = "Flask not installed"

    def get_auth_code(auth_url, ssl_context=None, timeout=180):  # type: ignore
        """Fallback auth code getter - not functional without Flask."""
        logger.error(f"Cannot get auth code for {auth_url} - Flask not available")
        if ssl_context:  # Use parameter to avoid lint warning
            logger.warning("SSL context provided but Flask not available")
        if timeout:  # Use parameter to avoid lint warning
            logger.warning(f"Timeout {timeout}s specified but Flask not available")
        raise RuntimeError(
            "OAuth authentication not available - Flask not installed. Install with: pip install flask"
        )


# Also define nullcontext for when Flask is available but enhanced logging is not
if FLASK_AVAILABLE and not LOGGING:

    class nullcontext:
        """Fallback context manager when enhanced logging not available."""

        def __enter__(self):
            return self

        def __exit__(self, *args):
            # Empty implementation for fallback compatibility
            pass


# Flask-dependent functions (only when Flask is available)
if FLASK_AVAILABLE:

    def run_auth_server(ssl_context=None):
        """Run the authentication server with enhanced error handling."""
        try:
            with log_context("auth_server_startup") if LOGGING else nullcontext():
                logger.info("Starting authentication server on localhost:7777")
                app.run(host="localhost", port=7777, ssl_context=ssl_context)
        except OSError as e:
            logger.error(f"Failed to start auth server: {e}")
            received_code["error"] = "Server start failure"

    def get_auth_code(auth_url, ssl_context=None, timeout=180):
        """
        Get OAuth authorization code from Bungie with enhanced monitoring.

        Args:
            auth_url: The OAuth authorization URL
            ssl_context: Optional SSL context for HTTPS
            timeout: Timeout in seconds (default 180)

        Returns:
            str: The authorization code

        Raises:
            TimeoutError: If OAuth flow times out
            RuntimeError: If authentication fails
        """
        with log_context("oauth_flow") if LOGGING else nullcontext():
            # Clear any previous state
            received_code.clear()

            # Start auth server in background
            logger.info("Starting OAuth authentication flow")
            threading.Thread(
                target=run_auth_server, kwargs={"ssl_context": ssl_context}, daemon=True
            ).start()

            # Open browser for user authentication
            try:
                webbrowser.open(auth_url)
                logger.info("Browser opened for OAuth login")
            except Exception as e:
                logger.error(f"Failed to open browser: {e}")
                # Continue anyway - user might manually navigate

            import time

            waited = 0
            check_interval = 0.5

            while "code" not in received_code and "error" not in received_code:
                time.sleep(check_interval)
                waited += check_interval

                # Log progress every 30 seconds
                if waited % 30 == 0:
                    logger.info(
                        f"Waiting for OAuth completion... ({waited:.0f}s elapsed)"
                    )

                if waited > timeout:
                    logger.error(f"OAuth code wait timed out after {timeout}s")
                    raise TimeoutError(
                        f"OAuth flow timed out after {timeout} seconds. "
                        "Please try again or check your browser."
                    )

            if "error" in received_code:
                error_msg = received_code["error"].replace("\n", "").replace("\r", "")
                logger.error(f"Auth server error: {error_msg}")
                raise RuntimeError(f"Authentication failed: {error_msg}")

            logger.info("OAuth authorization code received successfully")
            return received_code["code"]
