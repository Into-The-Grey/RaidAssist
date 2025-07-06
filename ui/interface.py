# interface.py — PySide2 UI for RaidAssist

"""
Main UI for RaidAssist Destiny 2 overlay app. Includes dashboard tabs, overlay mode, notifications, API tester, and settings.
"""

import os
import sys

# Ensure the root project folder is on sys.path for module imports (works in EXE and dev)
if getattr(sys, 'frozen', False):
    # PyInstaller EXE case
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(base_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from pyqt_hotkey import HotKeyManager  # type: ignore
except ImportError:
    HotKeyManager = None
    # TODO: Ensure pyqt-hotkey is bundled in installer for production builds

from PySide2.QtWidgets import (  # type: ignore
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QLineEdit,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QSlider,
    QSystemTrayIcon,
    QMenu,
)
from PySide2.QtGui import QIcon, QPixmap  # type: ignore
from PySide2.QtCore import QTimer, Qt  # type: ignore
import requests
import json
import csv
import logging
from api.parse_profile import (
    load_profile,
    extract_red_borders,
    extract_catalysts,
    extract_exotics,
)
from api.manifest import load_item_definitions
from ui.settings import SettingsDialog, load_settings
from ui.loading import LoadingDialog
from ui.api_tester import ApiTesterDialog


def get_asset_path(filename):
    """
    Returns the full path to an asset file, regardless of how the app is run.
    Looks for assets/ folder next to the current file (works in EXE and dev mode).
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "..", "assets")
    path = os.path.join(assets_dir, filename)
    # Normalize path (especially for Windows EXE)
    return os.path.normpath(path)


# ---- Logging (Optional, for debugging/future proof) ----
LOG_PATH = "RaidAssist/logs/interface.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

BASE_BUNGIE_URL = "https://www.bungie.net"


def get_item_info(item_hash, item_defs):
    """
    Returns key display data for a Destiny 2 item from the manifest.
    """
    item = item_defs.get(str(item_hash))
    if not item:
        return {
            "name": f"Unknown Item ({item_hash})",
            "icon": None,
            "description": "",
            "type": "",
            "archetype": "",
            "ammo": "",
            "source": "",
        }
    props = item.get("displayProperties", {})
    return {
        "name": props.get("name", f"Unnamed ({item_hash})"),
        "icon": props.get("icon"),
        "description": props.get("description", ""),
        "type": item.get("itemTypeDisplayName", ""),
        "archetype": item.get("itemSubType", ""),
        "ammo": item.get("equippingBlock", {}).get("ammoType", ""),
        "source": item.get("sourceData", {}).get("sourceHash", ""),
    }


def build_tooltip(info, extra=""):
    """
    Builds a manifest-rich tooltip for an item (used on hover).
    """
    ammo_types = {0: "None", 1: "Primary", 2: "Special", 3: "Heavy"}
    ammo = info["ammo"]
    if isinstance(ammo, int) and ammo in ammo_types:
        ammo_str = ammo_types[ammo]
    elif isinstance(ammo, str) and ammo.isdigit() and int(ammo) in ammo_types:
        ammo_str = ammo_types[int(ammo)]
    else:
        ammo_str = ""
    lines = [
        info["type"],
        f"Archetype: {info['archetype']}" if info["archetype"] else "",
        f"Ammo: {ammo_str}" if ammo_str else "",
        info["description"],
        extra,
    ]
    return "\n".join(line for line in lines if line)


class RaidAssistUI(QWidget):
    """
    Main application window for RaidAssist Destiny 2 overlay tool.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RaidAssist - Meta Progression Assistant")
        self.setWindowIcon(QIcon(get_asset_path("raidassist_icon.png")))
        self.setMinimumWidth(600)
        self.layout = QVBoxLayout()

        # System tray icon
        tray_icon_path = get_asset_path("raidassist_icon.png")
        tray_icon = QIcon(tray_icon_path) if os.path.exists(tray_icon_path) else QIcon()
        self.tray_icon = QSystemTrayIcon(tray_icon)
        self.tray_icon.setToolTip("RaidAssist is running")
        tray_menu = QMenu()
        tray_menu.addAction("Show", self.showNormal)
        tray_menu.addAction("Quit", QApplication.instance().quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # UI elements and layout setup
        self.tabs = QTabWidget()
        self.red_border_search = QLineEdit()
        self.red_border_search.setPlaceholderText("Search red borders...")
        self.catalyst_search = QLineEdit()
        self.catalyst_search.setPlaceholderText("Search catalysts...")
        self.exotic_search = QLineEdit()
        self.exotic_search.setPlaceholderText("Search exotics...")

        self.red_border_tab = QListWidget()
        self.catalyst_tab = QListWidget()
        self.exotic_tab = QListWidget()
        self.refresh_button = QPushButton("Refresh")
        self.settings_button = QPushButton("Settings")
        self.export_button = QPushButton("Export")
        self.api_tester_button = QPushButton("API Tester")
        self.overlay_button = QPushButton("Overlay Mode")
        self.status_bar = QStatusBar()

        # Red Borders Tab Layout
        self.red_border_widget = QWidget()
        rb_layout = QVBoxLayout()
        rb_layout.addWidget(self.red_border_search)
        rb_layout.addWidget(self.red_border_tab)
        self.red_border_widget.setLayout(rb_layout)

        # Catalysts Tab Layout
        self.catalyst_widget = QWidget()
        cat_layout = QVBoxLayout()
        cat_layout.addWidget(self.catalyst_search)
        cat_layout.addWidget(self.catalyst_tab)
        self.catalyst_widget.setLayout(cat_layout)

        # Exotics Tab Layout
        self.exotic_widget = QWidget()
        ex_layout = QVBoxLayout()
        ex_layout.addWidget(self.exotic_search)
        ex_layout.addWidget(self.exotic_tab)
        self.exotic_widget.setLayout(ex_layout)

        self.tabs.addTab(self.red_border_widget, "Red Borders")
        self.tabs.addTab(self.catalyst_widget, "Catalysts")
        self.tabs.addTab(self.exotic_widget, "Exotics")

        # Controls row
        controls_row = QHBoxLayout()
        controls_row.addWidget(self.refresh_button)
        controls_row.addWidget(self.settings_button)
        controls_row.addWidget(self.export_button)
        controls_row.addWidget(self.api_tester_button)
        controls_row.addWidget(self.overlay_button)

        self.layout.addWidget(QLabel("RaidAssist Progress Dashboard"))
        self.layout.addWidget(self.tabs)
        self.layout.addLayout(controls_row)
        self.layout.addWidget(self.status_bar)
        self.setLayout(self.layout)

        self.item_defs = load_item_definitions()
        self.refresh_button.clicked.connect(self.refresh_data)
        self.settings_button.clicked.connect(self.open_settings)
        self.export_button.clicked.connect(self.export_data)
        self.api_tester_button.clicked.connect(self.open_api_tester)
        self.overlay_button.clicked.connect(self.open_overlay)

        self.red_border_search.textChanged.connect(self.filter_red_borders)
        self.catalyst_search.textChanged.connect(self.filter_catalysts)
        self.exotic_search.textChanged.connect(self.filter_exotics)

        self._rb_items = []
        self._cat_items = []
        self._exotic_items = []
        self.overlay_ref = None

        self._prev_rb = set()
        self._prev_cat = set()
        self._prev_exo = set()

        # Auto-refresh timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_refresh)
        self.update_refresh_interval()
        self.timer.start()

        self.setup_hotkey()
        self.refresh_data()

    def open_settings(self):
        """Open the app settings dialog."""
        dlg = SettingsDialog(self)
        if dlg.exec_():
            self.update_refresh_interval()

    def update_refresh_interval(self):
        """Update refresh interval from settings."""
        interval = load_settings().get("refresh_interval_seconds", 60)
        self.timer.setInterval(interval * 1000)
        self.show_status(f"Auto-refresh every {interval} seconds.")

    def add_item_with_icon(self, list_widget, text, icon_path, tooltip=""):
        """
        Add a list item with manifest icon and tooltip.
        """
        item = QListWidgetItem(text)
        if icon_path:
            url = BASE_BUNGIE_URL + icon_path
            try:
                resp = requests.get(url)
                if resp.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(resp.content)
                    icon = QIcon(pixmap)
                    item.setIcon(icon)
            except Exception as e:
                logging.error(f"Failed to load icon for item: {e}")
        if tooltip:
            item.setToolTip(tooltip)
        list_widget.addItem(item)

    def show_status(self, message, timeout=3000):
        """Show a message in the status bar."""
        self.status_bar.showMessage(message, timeout)

    def refresh_data(self):
        """Manual refresh of all progress data and widgets."""
        dlg = LoadingDialog("Refreshing profile data...", self)
        dlg.show()
        QApplication.processEvents()
        self._refresh_main(dlg)

    def auto_refresh(self):
        """Auto-refresh callback for the QTimer."""
        self._refresh_main(None, auto=True)

    def _refresh_main(self, dlg=None, auto=False):
        """
        Main refresh routine. Loads data, populates lists, fires notifications.
        """
        try:
            self.red_border_tab.clear()
            self.catalyst_tab.clear()
            self.exotic_tab.clear()
            self._rb_items = []
            self._cat_items = []
            self._exotic_items = []

            profile = load_profile()
            if not profile:
                self.red_border_tab.addItem("No profile data found.")
                self.catalyst_tab.addItem("No profile data found.")
                self.exotic_tab.addItem("No profile data found.")
                self.show_status("Profile data not found!", 4000)
                if dlg:
                    dlg.close()
                return

            red_borders = extract_red_borders(profile)
            catalysts = extract_catalysts(profile)
            exotics = extract_exotics(profile)

            if not red_borders:
                self.red_border_tab.addItem("No red border weapons found.")
            else:
                for item in red_borders:
                    item_info = get_item_info(item["itemInstanceId"], self.item_defs)
                    tooltip = build_tooltip(item_info)
                    entry = {
                        "text": f"{item_info['name']} — Pattern: {item['progress']}/{item['needed']} ({item['percent']}%)",
                        "icon": item_info["icon"],
                        "raw": item,
                        "tooltip": tooltip,
                    }
                    self._rb_items.append(entry)

            if not catalysts:
                self.catalyst_tab.addItem("No catalysts found.")
            else:
                for cat in catalysts:
                    item_info = get_item_info(cat["itemInstanceId"], self.item_defs)
                    tooltip = build_tooltip(item_info)
                    entry = {
                        "text": f"{item_info['name']} — Catalyst: {cat['progress']}/{cat['needed']} ({cat['percent']}%)",
                        "icon": item_info["icon"],
                        "raw": cat,
                        "tooltip": tooltip,
                    }
                    self._cat_items.append(entry)

            if not exotics:
                self.exotic_tab.addItem("No exotics found.")
            else:
                for ex in exotics:
                    item_info = get_item_info(ex["itemHash"], self.item_defs)
                    tooltip = build_tooltip(item_info)
                    entry = {
                        "text": f"{item_info['name']} (hash: {ex['itemHash']})",
                        "icon": item_info["icon"],
                        "raw": ex,
                        "tooltip": tooltip,
                    }
                    self._exotic_items.append(entry)

            self.filter_red_borders()
            self.filter_catalysts()
            self.filter_exotics()
            self.check_for_notifications()

            if auto:
                self.show_status("Profile auto-refreshed.", 1500)
            else:
                self.show_status("Profile data refreshed.", 2000)
        except Exception as e:
            logging.error(f"Refresh failed: {e}")
            self.show_status(f"Error: {e}", 6000)
        finally:
            if dlg:
                dlg.close()

    def check_for_notifications(self):
        """
        Checks for new completions (pattern, catalyst, exotic) and shows tray notifications.
        """
        rb_done = set(
            item["raw"]["itemInstanceId"]
            for item in self._rb_items
            if item["raw"].get("progress", 0) >= item["raw"].get("needed", 1)
        )
        new_rb = rb_done - self._prev_rb
        for iid in new_rb:
            name = next(
                (
                    i["text"]
                    for i in self._rb_items
                    if i["raw"]["itemInstanceId"] == iid
                ),
                "Red Border",
            )
            self.tray_icon.showMessage(
                "Pattern Complete!",
                f"{name} is now craftable!",
                QSystemTrayIcon.Information,
                5000,
            )
        self._prev_rb = rb_done

        cat_done = set(
            item["raw"]["itemInstanceId"]
            for item in self._cat_items
            if item["raw"].get("progress", 0) >= item["raw"].get("needed", 1)
        )
        new_cat = cat_done - self._prev_cat
        for iid in new_cat:
            name = next(
                (
                    i["text"]
                    for i in self._cat_items
                    if i["raw"]["itemInstanceId"] == iid
                ),
                "Catalyst",
            )
            self.tray_icon.showMessage(
                "Catalyst Complete!",
                f"{name} catalyst unlocked!",
                QSystemTrayIcon.Information,
                5000,
            )
        self._prev_cat = cat_done

        exo_now = set(item["raw"].get("itemHash", "") for item in self._exotic_items)
        new_exo = exo_now - self._prev_exo
        for h in new_exo:
            name = next(
                (
                    i["text"]
                    for i in self._exotic_items
                    if i["raw"].get("itemHash", "") == h
                ),
                "Exotic",
            )
            self.tray_icon.showMessage(
                "New Exotic!",
                f"You acquired: {name}",
                QSystemTrayIcon.Information,
                5000,
            )
        self._prev_exo = exo_now

    def filter_red_borders(self):
        """Apply search filter to red borders list."""
        filter_text = self.red_border_search.text().lower()
        self.red_border_tab.clear()
        for item in self._rb_items:
            if filter_text in item["text"].lower():
                self.add_item_with_icon(
                    self.red_border_tab,
                    item["text"],
                    item["icon"],
                    item.get("tooltip", ""),
                )
        if not self.red_border_tab.count():
            self.red_border_tab.addItem("No matches.")

    def filter_catalysts(self):
        """Apply search filter to catalysts list."""
        filter_text = self.catalyst_search.text().lower()
        self.catalyst_tab.clear()
        for item in self._cat_items:
            if filter_text in item["text"].lower():
                self.add_item_with_icon(
                    self.catalyst_tab,
                    item["text"],
                    item["icon"],
                    item.get("tooltip", ""),
                )
        if not self.catalyst_tab.count():
            self.catalyst_tab.addItem("No matches.")

    def filter_exotics(self):
        """Apply search filter to exotics list."""
        filter_text = self.exotic_search.text().lower()
        self.exotic_tab.clear()
        for item in self._exotic_items:
            if filter_text in item["text"].lower():
                self.add_item_with_icon(
                    self.exotic_tab, item["text"], item["icon"], item.get("tooltip", "")
                )
        if not self.exotic_tab.count():
            self.exotic_tab.addItem("No matches.")

    def export_data(self):
        """Export current tab data as JSON or CSV."""
        tab = self.tabs.currentIndex()
        if tab == 0:
            data = [item["raw"] for item in self._rb_items]
            tab_name = "red_borders"
        elif tab == 1:
            data = [item["raw"] for item in self._cat_items]
            tab_name = "catalysts"
        elif tab == 2:
            data = [item["raw"] for item in self._exotic_items]
            tab_name = "exotics"
        else:
            return

        fname, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            f"{tab_name}.json",
            "JSON Files (*.json);;CSV Files (*.csv)",
        )
        if fname:
            try:
                if fname.endswith(".csv"):
                    with open(fname, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(data[0].keys() if data else ["Empty"])
                        for entry in data:
                            writer.writerow([entry.get(k, "") for k in data[0].keys()])
                else:
                    with open(fname, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                QMessageBox.information(
                    self, "Export Successful", f"Data exported to {fname}"
                )
            except Exception as e:
                logging.error(f"Export failed: {e}")
                QMessageBox.warning(
                    self, "Export Failed", f"Could not export data: {e}"
                )

    def open_api_tester(self):
        """Open the Bungie API Tester dialog."""
        dlg = ApiTesterDialog(self)
        dlg.exec_()

    def setup_hotkey(self):
        """
        Setup global hotkey for overlay toggle. Requires pyqt-hotkey to be installed and bundled.
        """
        if HotKeyManager:
            self.hotkey_mgr = HotKeyManager(self)
            self.hotkey_mgr.registerHotKey("ctrl+alt+o", self.toggle_overlay)
            self.show_status("Global hotkey set: Ctrl+Alt+O toggles overlay", 5000)
        else:
            self.show_status(
                "pyqt-hotkey not installed, no global hotkey support.", 6000
            )

    def toggle_overlay(self):
        """Toggle overlay visibility via hotkey."""
        if self.overlay_ref and self.overlay_ref.isVisible():
            self.overlay_ref.close()
        else:
            self.open_overlay()

    def open_overlay(self):
        """Show the overlay window."""
        if self.overlay_ref and self.overlay_ref.isVisible():
            self.overlay_ref.raise_()
            return
        self.overlay_ref = OverlayWindow(
            self._rb_items, self._cat_items, self._exotic_items
        )
        self.overlay_ref.show()


class OverlayWindow(QWidget):
    """
    Always-on-top, draggable, translucent overlay for quick progress viewing in-game.
    """

    def __init__(self, rb_items, cat_items, exotic_items):
        super().__init__()
        self.setWindowTitle("RaidAssist Overlay")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(
            "background: rgba(20, 20, 20, 190); color: white; border-radius: 16px;"
        )
        self.setFixedWidth(340)
        self._drag_pos = None

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>RaidAssist Overlay</b>"))
        if rb_items:
            layout.addWidget(QLabel("Red Borders:"))
            for item in rb_items[:5]:
                layout.addWidget(QLabel(item["text"]))
        if cat_items:
            layout.addWidget(QLabel("Catalysts:"))
            for item in cat_items[:5]:
                layout.addWidget(QLabel(item["text"]))
        if exotic_items:
            layout.addWidget(QLabel("Exotics:"))
            for item in exotic_items[:5]:
                layout.addWidget(QLabel(item["text"]))

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(20)
        self.slider.setMaximum(100)
        self.slider.setValue(80)
        self.slider.valueChanged.connect(self.change_opacity)
        layout.addWidget(QLabel("Overlay Opacity"))
        layout.addWidget(self.slider)

        close_btn = QPushButton("Close Overlay")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        self.setLayout(layout)

        self.change_opacity(self.slider.value())

    def change_opacity(self, value):
        """Adjust overlay window opacity."""
        self.setWindowOpacity(value / 100.0)

    def mousePressEvent(self, event):
        """Enable drag-to-move for overlay."""
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle overlay dragging."""
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Finish drag-to-move."""
        self._drag_pos = None


if __name__ == "__main__":
    """
    Entrypoint for manual/test launch. Use main.py for more complex orchestrations.
    """
    app = QApplication(sys.argv)
    window = RaidAssistUI()
    window.show()
    sys.exit(app.exec_())
