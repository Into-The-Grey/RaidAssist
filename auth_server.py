import os
import logging
import threading
import webbrowser
from flask import Flask, request # type: ignore

LOG_PATH = os.path.join(
    os.path.dirname(__file__), "RaidAssist", "logs", "auth_server.log"
)
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = Flask(__name__)
received_code = {}


@app.route("/callback")
def callback():
    code = request.args.get("code")
    error = request.args.get("error")
    if error:
        logging.error(f"OAuth error: {error}")
        return (
            "<h3>Authentication failed.</h3>"
            f"<p>Error from Bungie: <b>{error}</b></p>",
            400,
        )
    if not code:
        logging.warning("No code in callback.")
        return (
            "<h3>Authentication error</h3>"
            "<p>No authorization code was received from Bungie.</p>",
            400,
        )
    received_code["code"] = code
    logging.info("OAuth code received successfully.")
    return (
        "<h2>RaidAssist Authentication Complete!</h2>"
        "<p>You may now return to the app. This window can be closed.</p>",
        200,
    )


def run_auth_server(ssl_context=None):
    try:
        app.run(host="localhost", port=7777, ssl_context=ssl_context)
    except OSError as e:
        logging.error(f"Failed to start auth server: {e}")
        received_code["error"] = "Server start failure"


def get_auth_code(auth_url, ssl_context=None, timeout=180):
    threading.Thread(
        target=run_auth_server, kwargs={"ssl_context": ssl_context}, daemon=True
    ).start()
    webbrowser.open(auth_url)
    logging.info("Browser opened for OAuth login.")

    import time

    waited = 0
    while "code" not in received_code and "error" not in received_code:
        time.sleep(0.5)
        waited += 0.5
        if waited > timeout:
            logging.error("OAuth code wait timed out.")
            raise TimeoutError("OAuth flow timed out. Please try again.")
    if "error" in received_code:
        raise RuntimeError(f"Auth server error: {received_code['error']}")
    return received_code["code"]
