"""
loading.py — Simple loading modal dialog for RaidAssist.
"""

import os

from PySide6.QtCore import Qt  # type: ignore
from PySide6.QtGui import QIcon, QPixmap  # type: ignore
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,  # type: ignore
    QLabel,
    QVBoxLayout,
)


def get_asset_path(filename):
    """Helper function to get asset path"""
    return os.path.join(os.path.dirname(__file__), "..", "assets", filename)


class LoadingDialog(QDialog):
    """
    Displays a modal loading window with a customizable message using modern card design.
    """

    def __init__(self, message="Loading...", parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Please Wait")
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Card frame for modern look
        card_frame = QFrame()
        card_frame.setFrameStyle(QFrame.Shape.Box)
        card_frame.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
            }
        """
        )

        # Card content layout
        card_layout = QVBoxLayout(card_frame)
        card_layout.setSpacing(15)

        # Icon and message layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)

        # Loading icon
        icon_label = QLabel()
        try:
            icon_pixmap = QIcon(get_asset_path("loading_icon.png")).pixmap(32, 32)
            icon_label.setPixmap(icon_pixmap)
        except:
            # Fallback text if icon not found
            icon_label.setText("⏳")
            icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Message label
        message_label = QLabel(message)
        message_label.setStyleSheet("font-size: 14px; color: #333;")
        message_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        content_layout.addWidget(icon_label)
        content_layout.addWidget(message_label)
        content_layout.addStretch()

        card_layout.addLayout(content_layout)
        main_layout.addWidget(card_frame)

        self.setLayout(main_layout)
        self.setFixedWidth(280)
        self.setFixedHeight(100)
