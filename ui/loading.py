"""
loading.py — Simple loading modal dialog for RaidAssist.
"""

from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel # type: ignore
from PySide2.QtCore import Qt # type: ignore


class LoadingDialog(QDialog):
    """
    Displays a modal loading window with a customizable message.
    """

    def __init__(self, message="Loading...", parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Please Wait")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(message))
        self.setLayout(layout)
        self.setFixedWidth(200)
        self.setFixedHeight(80)
