"""
api_tester.py — Bungie API call tester dialog for RaidAssist.

Allows power users to send requests to any Bungie API endpoint and view/save the response.
"""

import json
import logging
import os

import requests
from PySide6.QtCore import Qt  # type: ignore
from PySide6.QtGui import QFont, QIcon  # type: ignore
from PySide6.QtWidgets import (
    QApplication,
    QDialog,  # type: ignore
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
)

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

# ---- Environment variable loading for development only ----
if load_dotenv is not None and os.environ.get("RAIDASSIST_DEV_MODE"):
    env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
    )
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        logging.info(
            ".env file not found in project root; using bundled configuration."
        )

SESSION_PATH = os.path.expanduser("~/.raidassist/session.json")

# Bungie API configuration - bundled credentials
BUNGIE_API_KEY = "b4c3ff9cf4fb4ba3a1a0b8a5a8e3f8e9c2d6b5a8c9f2e1d4a7b0c6f5e8d9c2a5"

# Allow environment variable override for development/testing
if os.environ.get("BUNGIE_API_KEY"):
    BUNGIE_API_KEY = os.environ.get("BUNGIE_API_KEY")


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


def get_asset_path(filename):
    """
    Helper function to get asset file paths.
    Returns:
        str: Path to asset file or empty string if not found.
    """
    # Look for assets in the project's assets directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    asset_path = os.path.join(project_root, "assets", filename)
    if os.path.exists(asset_path):
        return asset_path
    # Fallback to system icons or return empty string
    return ""


class ApiTesterDialog(QDialog):
    """
    Simple dialog to send API requests and show/save responses.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        app = QApplication.instance()
        # Note: load_qss function not available, using default Qt styling
        if app:
            pass  # Could apply custom styling here if needed

        self.setWindowTitle("Bungie API Tester")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(16)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Hero area
        self.create_hero_area()

        # Request card
        self.create_request_card()

        # Results card
        self.create_results_card()

        # Action buttons
        self.create_action_buttons()

        self.setLayout(self.main_layout)

        self.send_button.clicked.connect(self.make_request)
        self.save_button.clicked.connect(self.save_result)

    def create_hero_area(self):
        """Create the hero area with welcome message and status."""
        hero_frame = QFrame()
        hero_frame.setObjectName("heroFrame")
        hero_layout = QHBoxLayout(hero_frame)

        # Status icon/text
        status_label = QLabel("🎮 Bungie API Tester")
        status_font = QFont()
        status_font.setPointSize(16)
        status_font.setBold(True)
        status_label.setFont(status_font)

        # Connection status
        token = load_token()
        auth_status = QLabel(f"🔐 Auth: {'Connected' if token else 'API Key Only'}")
        auth_status.setStyleSheet("color: #4caf50;" if token else "color: #ff9800;")

        hero_layout.addWidget(status_label)
        hero_layout.addStretch()
        hero_layout.addWidget(auth_status)

        self.main_layout.addWidget(hero_frame)

    def create_request_card(self):
        """Create the request input card."""
        request_group = QGroupBox("API Request")
        request_layout = QVBoxLayout()

        # Endpoint input row
        endpoint_row = QHBoxLayout()
        endpoint_label = QLabel("Endpoint:")
        self.endpoint_input = QLineEdit()
        self.endpoint_input.setPlaceholderText("/Destiny2/Manifest/")
        self.endpoint_input.setStyleSheet(
            "padding: 8px; border-radius: 4px; border: 1px solid #ccc;"
        )

        self.send_button = QPushButton("Send Request")
        send_icon_path = get_asset_path("send_icon.png")
        if send_icon_path:
            self.send_button.setIcon(QIcon(send_icon_path))
        else:
            self.send_button.setText("🚀 Send Request")

        endpoint_row.addWidget(endpoint_label)
        endpoint_row.addWidget(self.endpoint_input, 1)
        endpoint_row.addWidget(self.send_button)

        request_layout.addLayout(endpoint_row)
        request_group.setLayout(request_layout)
        self.main_layout.addWidget(request_group)

    def create_results_card(self):
        """Create the results display card."""
        results_group = QGroupBox("API Response")
        results_layout = QVBoxLayout()

        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        self.result_view.setPlaceholderText(
            "Response will appear here after sending a request..."
        )
        self.result_view.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                background-color: #fafafa;
            }
        """
        )

        results_layout.addWidget(self.result_view)
        results_group.setLayout(results_layout)
        self.main_layout.addWidget(results_group, 1)  # Allow to expand

    def create_action_buttons(self):
        """Create the action buttons area."""
        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)

        # Add spacer to push buttons to the right
        spacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        actions_layout.addItem(spacer)

        self.save_button = QPushButton("Save Result")
        save_icon_path = get_asset_path("save_icon.png")
        if save_icon_path:
            self.save_button.setIcon(QIcon(save_icon_path))
        else:
            self.save_button.setText("💾 Save Result")

        actions_layout.addWidget(self.save_button)
        self.main_layout.addWidget(actions_frame)

    def make_request(self):
        """
        Sends a GET request to the provided Bungie API endpoint and displays the result.
        """
        endpoint = self.endpoint_input.text().strip()
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        url = "https://www.bungie.net/Platform" + endpoint
        headers = {"X-API-Key": BUNGIE_API_KEY}
        token = load_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        logging.info(f"Sending GET to {url} (auth: {'yes' if token else 'no'})")

        # Update UI to show loading state
        self.send_button.setText("🔄 Sending...")
        self.send_button.setEnabled(False)

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
        finally:
            # Restore button state
            send_icon_path = get_asset_path("send_icon.png")
            if send_icon_path:
                self.send_button.setIcon(QIcon(send_icon_path))
                self.send_button.setText("Send Request")
            else:
                self.send_button.setText("🚀 Send Request")
            self.send_button.setEnabled(True)

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
