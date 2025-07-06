"""
api_tester.py — Bungie API call tester dialog for RaidAssist.

Allows power users to send requests to any Bungie API endpoint and view/save the response.
"""

from PySide2.QtWidgets import (  # type: ignore
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFileDialog,
)
import requests
import json
import os
import logging

try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    load_dotenv = None

# ---- Logging setup ----
LOG_PATH = os.path.expanduser("~/.raidassist/api_tester.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ---- Environment variable loading ----
if load_dotenv is not None:
    env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
    )
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        logging.warning(
            ".env file not found in project root; falling back to environment variables."
        )

SESSION_PATH = os.path.expanduser("~/.raidassist/session.json")
API_KEY = os.environ.get(
    "BUNGIE_API_KEY", "YOUR_BUNGIE_API_KEY"
)  # Should always be set via .env


def load_token():
    """
    Loads OAuth token from session file, if present.
    Returns:
        str: OAuth access token, or empty string if not found.
    """
    if os.path.exists(SESSION_PATH):
        try:
            with open(SESSION_PATH, "r") as f:
                return json.load(f).get("access_token", "")
        except Exception as e:
            logging.error(f"Failed to load OAuth token: {e}")
    return ""


class ApiTesterDialog(QDialog):
    """
    Simple dialog to send API requests and show/save responses.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bungie API Tester")
        self.setMinimumWidth(600)
        self.layout = QVBoxLayout()

        self.endpoint_input = QLineEdit()
        self.endpoint_input.setPlaceholderText("/Destiny2/Manifest/")
        self.send_button = QPushButton("Send Request")
        self.save_button = QPushButton("Save Result")
        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)

        row = QHBoxLayout()
        row.addWidget(QLabel("Endpoint:"))
        row.addWidget(self.endpoint_input)
        row.addWidget(self.send_button)
        self.layout.addLayout(row)
        self.layout.addWidget(self.result_view)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

        self.send_button.clicked.connect(self.make_request)
        self.save_button.clicked.connect(self.save_result)

    def make_request(self):
        """
        Sends a GET request to the provided Bungie API endpoint and displays the result.
        """
        endpoint = self.endpoint_input.text().strip()
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        url = "https://www.bungie.net/Platform" + endpoint
        headers = {"X-API-Key": API_KEY}
        token = load_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        logging.info(f"Sending GET to {url} (auth: {'yes' if token else 'no'})")
        try:
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            try:
                data = r.json()
                pretty = json.dumps(data, indent=2)
            except Exception:
                pretty = r.text
            self.result_view.setPlainText(pretty)
            logging.info(f"API {endpoint} success, {len(pretty)} chars.")
        except Exception as e:
            error_msg = f"Error: {e}"
            self.result_view.setPlainText(error_msg)
            logging.error(f"API {endpoint} error: {e}")

    def save_result(self):
        """
        Saves the result view's contents to a file.
        """
        fname, _ = QFileDialog.getSaveFileName(
            self,
            "Save Result",
            "api_result.json",
            "JSON Files (*.json);;Text Files (*.txt)",
        )
        if fname:
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(self.result_view.toPlainText())
                logging.info(f"Saved API result to {fname}")
            except Exception as e:
                self.result_view.append(f"\nSave error: {e}")
                logging.error(f"Failed to save result: {e}")
