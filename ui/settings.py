"""
settings.py — Settings dialog and config loader for RaidAssist.

Stores and loads app preferences in JSON.
"""

from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QSpinBox, QPushButton  # type: ignore
import json
import os
import logging


def get_project_root():
    """Returns the absolute path to the project root."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SETTINGS_PATH = os.path.join(
    get_project_root(), "RaidAssist", "config", "settings.json"
)
LOG_PATH = os.path.join(get_project_root(), "RaidAssist", "logs", "settings.log")

os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def load_settings():
    """
    Loads app settings from disk.
    Returns:
        dict: Settings dictionary.
    """
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                settings = json.load(f)
                logging.info("Settings loaded.")
                return settings
        except Exception as e:
            logging.error(f"Failed to load settings: {e}")
    else:
        logging.warning("Settings file does not exist.")
    return {"refresh_interval_seconds": 60}


def save_settings(settings):
    """
    Saves the provided settings dictionary to disk.
    Args:
        settings (dict): Settings to save.
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        logging.info("Settings saved.")
        return True
    except Exception as e:
        logging.error(f"Failed to save settings: {e}")
        return False


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
