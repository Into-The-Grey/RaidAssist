"""
api_tester.py — Bungie API call tester dialog for RaidAssist.

Allows power users to send requests to any Bungie API endpoint and view/save the response.
"""

from PySide2.QtWidgets import ( # type: ignore
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

SESSION_PATH = os.path.expanduser("~/.raidassist/session.json")
API_KEY = os.environ.get("BUNGIE_API_KEY", "YOUR_BUNGIE_API_KEY")

# Optionally configure logging here if desired


def load_token():
    """
    Loads OAuth token from session file, if present.
    Returns:
        str: OAuth access token, or empty string if not found.
    """
    if os.path.exists(SESSION_PATH):
        with open(SESSION_PATH, "r") as f:
            return json.load(f).get("access_token", "")
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
        try:
            r = requests.get(url, headers=headers)
            try:
                data = r.json()
                pretty = json.dumps(data, indent=2)
            except Exception:
                pretty = r.text
            self.result_view.setPlainText(pretty)
        except Exception as e:
            self.result_view.setPlainText(f"Error: {e}")

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
            except Exception as e:
                self.result_view.append(f"\nSave error: {e}")
