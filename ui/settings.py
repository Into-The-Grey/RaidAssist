"""
settings.py — Settings dialog and config loader for RaidAssist.

Stores and loads app preferences in JSON.
"""

from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QSpinBox, QPushButton # type: ignore
import json
import os
import logging

SETTINGS_PATH = "RaidAssist/config/settings.json"
# Optionally configure logging here


def load_settings():
    """
    Loads app settings from disk.
    Returns:
        dict: Settings dictionary.
    """
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    return {"refresh_interval_seconds": 60}


def save_settings(settings):
    """
    Saves the provided settings dictionary to disk.
    Args:
        settings (dict): Settings to save.
    """
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)


class SettingsDialog(QDialog):
    """
    Simple settings dialog for refresh interval.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.layout = QVBoxLayout()

        self.interval_label = QLabel("Refresh Interval (seconds):")
        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(10)
        self.interval_spin.setMaximum(3600)
        self.save_button = QPushButton("Save")

        self.layout.addWidget(self.interval_label)
        self.layout.addWidget(self.interval_spin)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

        self.settings = load_settings()
        self.interval_spin.setValue(self.settings.get("refresh_interval_seconds", 60))

        self.save_button.clicked.connect(self.save_and_close)

    def save_and_close(self):
        """
        Saves settings and closes the dialog.
        """
        self.settings["refresh_interval_seconds"] = self.interval_spin.value()
        save_settings(self.settings)
        self.accept()
