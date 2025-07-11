"""
settings.py — Settings dialog and config loader for RaidAssist.

Stores and loads app preferences in JSON.
"""

from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QGroupBox, QFrame  # type: ignore
from PySide2.QtCore import Qt  # type: ignore
from PySide2.QtGui import QIcon, QFont  # type: ignore
import json
import os
import logging


def get_project_root():
    """Returns the absolute path to the project root."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_asset_path(filename):
    """Returns the path to an asset file in the assets directory."""
    return os.path.join(get_project_root(), "RaidAssist", "assets", filename)


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
    Modern settings dialog with card-based interface.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(400, 300)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Hero area
        self.create_hero_area()

        # Settings card
        self.create_settings_card()

        # Button area
        self.create_button_area()

        self.setLayout(self.layout)

        self.settings = load_settings()
        self.interval_spin.setValue(self.settings.get("refresh_interval_seconds", 60))

    def create_hero_area(self):
        """Creates the hero area with welcome message and icon."""
        hero_frame = QFrame()
        hero_frame.setFrameStyle(QFrame.StyledPanel)
        hero_frame.setStyleSheet(
            "QFrame { background-color: #f0f0f0; border-radius: 8px; padding: 15px; }"
        )

        hero_layout = QHBoxLayout()

        # Icon
        icon_label = QLabel()
        if os.path.exists(get_asset_path("settings_icon.png")):
            icon_label.setPixmap(
                QIcon(get_asset_path("settings_icon.png")).pixmap(48, 48)
            )
        else:
            icon_label.setText("⚙️")
            icon_label.setStyleSheet("font-size: 32px;")
        icon_label.setAlignment(Qt.AlignCenter)

        # Welcome text
        welcome_label = QLabel("Application Settings")
        welcome_font = QFont()
        welcome_font.setPointSize(16)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        welcome_label.setAlignment(Qt.AlignVCenter)

        hero_layout.addWidget(icon_label)
        hero_layout.addWidget(welcome_label)
        hero_layout.addStretch()

        hero_frame.setLayout(hero_layout)
        self.layout.addWidget(hero_frame)

    def create_settings_card(self):
        """Creates the settings form as a card."""
        settings_group = QGroupBox("Configuration")
        settings_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        )

        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(15)
        settings_layout.setContentsMargins(15, 15, 15, 15)

        # Refresh interval setting
        interval_frame = QFrame()
        interval_layout = QHBoxLayout()

        self.interval_label = QLabel("Refresh Interval (seconds):")
        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(10)
        self.interval_spin.setMaximum(3600)
        self.interval_spin.setStyleSheet("QSpinBox { padding: 5px; }")

        interval_layout.addWidget(self.interval_label)
        interval_layout.addStretch()
        interval_layout.addWidget(self.interval_spin)

        interval_frame.setLayout(interval_layout)
        settings_layout.addWidget(interval_frame)

        settings_group.setLayout(settings_layout)
        self.layout.addWidget(settings_group)

    def create_button_area(self):
        """Creates the button area with icons."""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Cancel button
        cancel_button = QPushButton("Cancel")
        if os.path.exists(get_asset_path("cancel_icon.png")):
            cancel_button.setIcon(QIcon(get_asset_path("cancel_icon.png")))
        cancel_button.setStyleSheet("QPushButton { padding: 8px 15px; }")
        cancel_button.clicked.connect(self.reject)

        # Save button
        self.save_button = QPushButton("Save")
        if os.path.exists(get_asset_path("save_icon.png")):
            self.save_button.setIcon(QIcon(get_asset_path("save_icon.png")))
        self.save_button.setStyleSheet(
            """
            QPushButton { 
                padding: 8px 15px; 
                background-color: #007acc; 
                color: white; 
                border: none; 
                border-radius: 4px; 
            }
            QPushButton:hover { 
                background-color: #005a9e; 
            }
        """
        )
        self.save_button.clicked.connect(self.save_and_close)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.save_button)

        self.layout.addWidget(QFrame())  # Spacer
        self.layout.addLayout(button_layout)

    def save_and_close(self):
        """
        Saves settings and closes the dialog.
        """
        self.settings["refresh_interval_seconds"] = self.interval_spin.value()
        save_settings(self.settings)
        self.accept()
