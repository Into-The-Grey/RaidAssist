# RaidAssist — Destiny 2 Progression Tracker and Overlay
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>

"""
interface.py — Completely overhauled UI for RaidAssist with advanced features.
"""

import csv
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional

# Enhanced error handling and logging
try:
    from utils.error_handler import (
        get_error_handler,  # type: ignore
        handle_error,
        safe_execute,
    )
    from utils.logging_manager import get_logger, log_context  # type: ignore

    ERROR_HANDLING = True
except ImportError:
    ERROR_HANDLING = False

    def get_logger(name):
        return logging.getLogger(name)

    def log_context(ctx):
        class DummyContext:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        return DummyContext()

    def safe_execute(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return kwargs.get("default_return")


from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,  # type: ignore
    Qt,
    QThread,
    QTimer,
    Signal,
)
from PySide6.QtGui import QColor, QFont, QIcon, QPalette, QPixmap  # type: ignore

# Qt imports
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,  # type: ignore
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplashScreen,
    QSplitter,
    QStatusBar,
    QSystemTrayIcon,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Import application modules
from api.bungie import (
    ensure_authenticated,
    fetch_profile,
    load_cached_profile,
    test_api_connection,
)
from api.manifest import get_item_info, load_item_definitions
from api.parse_profile import (
    extract_catalysts,
    extract_exotics,
    extract_red_borders,
    load_profile,
)
from ui.api_tester import ApiTesterDialog
from ui.loading import LoadingDialog
from ui.settings import SettingsDialog, load_settings

# Overlay system (name is fine; it's an import, not a UI class)
try:
    from ui.overlay import Overlay, create_overlay

    OVERLAY_AVAILABLE = True
except ImportError:
    OVERLAY_AVAILABLE = False

# Hotkey support
try:
    import keybind  # type: ignore

    HOTKEY_AVAILABLE = True
except ImportError:
    HOTKEY_AVAILABLE = False


def get_asset_path(filename):
    """Get the full path to an asset file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "..", "assets")
    path = os.path.join(assets_dir, filename)
    return os.path.normpath(path)


class DataRefreshThread(QThread):
    """Background thread for data refresh operations."""

    data_loaded = Signal(dict)
    error_occurred = Signal(str)
    progress_updated = Signal(int, str)

    def __init__(self, membership_type=None, membership_id=None):
        super().__init__()
        self.membership_type = membership_type
        self.membership_id = membership_id
        self.logger = get_logger("raidassist.data_thread")

    def run(self):
        """Run the data refresh in background."""
        try:
            with log_context("background_data_refresh"):
                self.progress_updated.emit(10, "Loading cached profile...")

                # Try cached data first
                profile = load_cached_profile()
                if not profile and self.membership_type and self.membership_id:
                    self.progress_updated.emit(30, "Fetching fresh profile data...")
                    profile = fetch_profile(self.membership_type, self.membership_id)
                elif not profile:
                    self.progress_updated.emit(30, "Loading profile from disk...")
                    profile = load_profile()

                if not profile:
                    self.error_occurred.emit("No profile data available")
                    return

                self.progress_updated.emit(50, "Processing red borders...")
                red_borders = extract_red_borders(profile)

                self.progress_updated.emit(70, "Processing catalysts...")
                catalysts = extract_catalysts(profile)

                self.progress_updated.emit(90, "Processing exotics...")
                exotics = extract_exotics(profile)

                data = {
                    "red_borders": red_borders,
                    "catalysts": catalysts,
                    "exotics": exotics,
                    "profile": profile,
                }

                self.progress_updated.emit(100, "Data loaded successfully")
                self.data_loaded.emit(data)

        except Exception as e:
            self.logger.error(f"Background data refresh failed: {e}")
            self.error_occurred.emit(str(e))


class RaidAssistUI(QWidget):
    """
    Main application window for RaidAssist.
    """

    # UI Constants
    NO_DATA_MESSAGE = "No data available"
    NO_MATCHES_MESSAGE = "No matches found"
    LOADING_MESSAGE = "Loading..."

    def __init__(self):
        super().__init__()

        # Initialize components
        self._initialize_logging()
        self._initialize_application()

    def _initialize_logging(self):
        """Initialize logging and error handling."""
        if ERROR_HANDLING:
            self.logger = get_logger("raidassist.ui")
            get_error_handler().set_ui_parent(self)
        else:
            self.logger = get_logger("raidassist")

    def _initialize_application(self):
        """Initialize the application with comprehensive setup."""
        try:
            with log_context("ui_initialization"):
                self.logger.info("Starting RaidAssist UI initialization")

                # Show splash screen
                self._show_splash_screen()

                # Core initialization
                self._verify_prerequisites()
                self._setup_data_structures()
                self._setup_window()
                self._setup_ui_components()
                self._setup_connections()
                self._setup_background_services()

                # Load initial data
                self._start_initial_data_load()

                self.logger.info("UI initialization completed successfully")

        except Exception as e:
            self._handle_initialization_error(e)

    def _show_splash_screen(self):
        """Show a professional splash screen during initialization."""
        splash_pixmap = QPixmap(200, 200)
        splash_pixmap.fill(QColor("#2b2b2b"))

        self.splash = QSplashScreen(splash_pixmap)
        self.splash.setStyleSheet(
            """
            QSplashScreen {
                background-color: #2b2b2b;
                border: 2px solid #00d4ff;
                border-radius: 10px;
            }
        """
        )
        self.splash.showMessage(
            "🎮 Initializing RaidAssist...",
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
            QColor("#00d4ff"),
        )
        self.splash.show()
        QApplication.processEvents()

    def _verify_prerequisites(self):
        """Verify all prerequisites are met."""
        # Test API connectivity
        if not test_api_connection():
            raise RuntimeError("Cannot connect to Bungie API")

        # Verify authentication
        if not ensure_authenticated():
            raise RuntimeError("User authentication failed")

        self.splash.showMessage(
            "🔐 Authentication verified...",
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
            QColor("#00ff00"),
        )
        QApplication.processEvents()

    def _setup_data_structures(self):
        """Initialize all data structures."""
        # Item definitions
        self.item_defs = safe_execute(
            load_item_definitions, default_return={}, context=["manifest_loading"]
        )

        # Data containers
        self._rb_items: List[Dict[str, Any]] = []
        self._cat_items: List[Dict[str, Any]] = []
        self._exotic_items: List[Dict[str, Any]] = []

        # State tracking
        self._prev_rb = set()
        self._prev_cat = set()
        self._prev_exo = set()
        self._last_refresh_time = 0

        # UI state
        self._is_refreshing = False
        self._connection_status = "Unknown"

        # Overlay references
        self.overlay_ref: Optional[Overlay] = None

        self.splash.showMessage(
            "📊 Data structures initialized...",
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
            QColor("#00d4ff"),
        )
        QApplication.processEvents()

    def _setup_window(self):
        """Setup the main window with enhanced appearance."""
        self.setWindowTitle("RaidAssist - Meta Progression Assistant")
        self.setWindowIcon(QIcon(get_asset_path("raidassist_icon.png")))
        self.setMinimumSize(900, 700)
        self.resize(1200, 800)

        # Apply dark theme
        self._apply_dark_theme()

        # Center window
        self._center_window()

    def _apply_dark_theme(self):
        """Apply professional dark theme."""
        self.setStyleSheet(
            """
            /* Main Window */
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                font-size: 10pt;
            }
            
            /* Headers */
            QLabel[heading="true"] {
                font-size: 14pt;
                font-weight: bold;
                color: #00d4ff;
                padding: 8px;
            }
            
            /* Tabs */
            QTabWidget::pane {
                border: 2px solid #404040;
                border-radius: 8px;
                background-color: #2b2b2b;
                padding: 4px;
            }
            
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 10px 20px;
                margin: 2px;
                border-radius: 6px;
                min-width: 80px;
            }
            
            QTabBar::tab:selected {
                background-color: #00d4ff;
                color: #000000;
                font-weight: bold;
            }
            
            QTabBar::tab:hover {
                background-color: #0099cc;
                color: #ffffff;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #404040;
                border: 2px solid #00d4ff;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                color: #ffffff;
            }
            
            QPushButton:hover {
                background-color: #00d4ff;
                color: #000000;
            }
            
            QPushButton:pressed {
                background-color: #0080cc;
                border-color: #0080cc;
            }
            
            QPushButton:disabled {
                background-color: #2b2b2b;
                border-color: #666666;
                color: #666666;
            }
            
            /* Input Fields */
            QLineEdit {
                background-color: #333333;
                border: 2px solid #666666;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 10pt;
            }
            
            QLineEdit:focus {
                border-color: #00d4ff;
                background-color: #404040;
            }
            
            /* Lists */
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #666666;
                border-radius: 6px;
                alternate-background-color: #333333;
                gridline-color: #404040;
            }
            
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
                border-radius: 3px;
                margin: 1px;
            }
            
            QListWidget::item:selected {
                background-color: #00d4ff;
                color: #000000;
            }
            
            QListWidget::item:hover {
                background-color: #404040;
            }
            
            /* Progress Bars */
            QProgressBar {
                border: 2px solid #00d4ff;
                border-radius: 8px;
                text-align: center;
                background-color: #333333;
                color: #ffffff;
                font-weight: bold;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #0099cc);
                border-radius: 6px;
                margin: 2px;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #333333;
                border-top: 1px solid #666666;
                color: #ffffff;
                font-size: 9pt;
            }
            
            /* Frames */
            QFrame[frameShape="4"] {
                color: #666666;
            }
            
            /* Checkboxes */
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #666666;
                border-radius: 3px;
                background-color: #333333;
            }
            
            QCheckBox::indicator:checked {
                background-color: #00d4ff;
                border-color: #00d4ff;
            }
            
            /* Sliders */
            QSlider::groove:horizontal {
                border: 1px solid #666666;
                height: 6px;
                background: #333333;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: #00d4ff;
                border: 1px solid #0099cc;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            
            QSlider::sub-page:horizontal {
                background: #00d4ff;
                border-radius: 3px;
            }
        """
        )

    def _center_window(self):
        """Center the window on screen."""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2
        )

    def _setup_ui_components(self):
        """Setup all UI components with enhanced design."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(8)

        # Setup components
        self._setup_header()
        self._setup_main_content()
        self._setup_footer()
        self._setup_system_tray()

        self.splash.showMessage(
            "🎨 UI components created...",
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
            QColor("#00d4ff"),
        )
        QApplication.processEvents()

    def _setup_header(self):
        """Setup the application header."""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Title and status
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        title_label = QLabel("🎮 RaidAssist")
        title_label.setProperty("heading", True)
        title_layout.addWidget(title_label)

        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("color: #00d4ff; font-size: 9pt;")
        title_layout.addWidget(self.status_label)

        header_layout.addWidget(title_widget)
        header_layout.addStretch()

        # Connection indicator
        self.connection_indicator = QLabel("🔴")
        self.connection_indicator.setToolTip("Connection status")
        header_layout.addWidget(self.connection_indicator)

        self.main_layout.addWidget(header_frame)

        # Progress bar for operations
        self.main_progress = QProgressBar()
        self.main_progress.setVisible(False)
        self.main_progress.setMinimum(0)
        self.main_progress.setMaximum(100)
        self.main_layout.addWidget(self.main_progress)

    def _setup_main_content(self):
        """Setup the main content area with enhanced tabs."""
        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - quick stats
        self._setup_stats_panel(main_splitter)

        # Right panel - detailed tabs
        self._setup_tabs_panel(main_splitter)

        # Set splitter proportions
        main_splitter.setSizes([300, 700])
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)

        self.main_layout.addWidget(main_splitter)

    def _setup_stats_panel(self, parent):
        """Setup the quick stats panel."""
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        stats_layout = QVBoxLayout(stats_frame)

        # Panel title
        stats_title = QLabel("📊 Quick Stats")
        stats_title.setProperty("heading", True)
        stats_layout.addWidget(stats_title)

        # Stats widgets
        self.rb_summary = self._create_stat_widget("🔴 Red Borders", "0/0 (0%)")
        self.cat_summary = self._create_stat_widget("⚡ Catalysts", "0/0 (0%)")
        self.ex_summary = self._create_stat_widget("💎 Exotics", "0")

        stats_layout.addWidget(self.rb_summary)
        stats_layout.addWidget(self.cat_summary)
        stats_layout.addWidget(self.ex_summary)

        # Recent activity
        recent_title = QLabel("🏆 Recent")
        recent_title.setStyleSheet("font-weight: bold; margin-top: 16px;")
        stats_layout.addWidget(recent_title)

        self.recent_activity = QTextEdit()
        self.recent_activity.setMaximumHeight(150)
        self.recent_activity.setStyleSheet(
            """
            QTextEdit {
                background-color: #333333;
                border: 1px solid #666666;
                border-radius: 4px;
                font-size: 9pt;
            }
        """
        )
        self.recent_activity.setPlainText("No recent activity")
        stats_layout.addWidget(self.recent_activity)

        # Control buttons
        controls_frame = QFrame()
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(6)

        self.refresh_button = QPushButton("🔄 Refresh Data")
        self.overlay_button = QPushButton("🎮 Overlay")
        self.settings_button = QPushButton("⚙️ Settings")

        controls_layout.addWidget(self.refresh_button)
        controls_layout.addWidget(self.overlay_button)
        controls_layout.addWidget(self.settings_button)

        stats_layout.addWidget(controls_frame)
        stats_layout.addStretch()

        parent.addWidget(stats_frame)

    def _create_stat_widget(self, title: str, value: str) -> QFrame:
        """Create a statistics display widget."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        widget.setStyleSheet(
            """
            QFrame {
                background-color: #333333;
                border: 1px solid #666666;
                border-radius: 6px;
                padding: 8px;
            }
        """
        )

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; color: #00d4ff;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(value_label)

        # Store reference to value label for updates
        widget.value_label = value_label  # type: ignore[misc]

        return widget

    def _setup_tabs_panel(self, parent):
        """Setup the detailed tabs panel."""
        tabs_frame = QFrame()
        tabs_layout = QVBoxLayout(tabs_frame)
        tabs_layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tabs = QTabWidget()

        # Setup tabs
        self._setup_red_borders_tab()
        self._setup_catalysts_tab()
        self._setup_exotics_tab()
        self._setup_tools_tab()

        tabs_layout.addWidget(self.tabs)
        parent.addWidget(tabs_frame)

    def _setup_red_borders_tab(self):
        """Setup red borders tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # Search and filters
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)

        self.rb_search = QLineEdit()
        self.rb_search.setPlaceholderText("🔍 Search red border weapons...")
        search_layout.addWidget(self.rb_search)

        self.rb_show_completed = QCheckBox("Show Completed")
        self.rb_show_completed.setChecked(True)
        search_layout.addWidget(self.rb_show_completed)

        self.rb_sort_combo = QComboBox()
        self.rb_sort_combo.addItems(["Progress %", "Name", "Type", "Completion"])
        search_layout.addWidget(self.rb_sort_combo)

        layout.addWidget(search_frame)

        # List widget with features
        self.red_border_list = QListWidget()
        self.red_border_list.setAlternatingRowColors(True)
        layout.addWidget(self.red_border_list)

        # Stats footer
        self.rb_stats = QLabel("No data loaded")
        self.rb_stats.setStyleSheet("color: #00d4ff; font-weight: bold;")
        layout.addWidget(self.rb_stats)

        self.tabs.addTab(tab_widget, "🔴 Red Borders")

    def _setup_catalysts_tab(self):
        """Setup catalysts tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # Search and filters
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)

        self.cat_search = QLineEdit()
        self.cat_search.setPlaceholderText("🔍 Search catalyst progress...")
        search_layout.addWidget(self.cat_search)

        self.cat_show_completed = QCheckBox("Show Completed")
        self.cat_show_completed.setChecked(True)
        search_layout.addWidget(self.cat_show_completed)

        self.cat_sort_combo = QComboBox()
        self.cat_sort_combo.addItems(["Progress %", "Name", "Type", "Completion"])
        search_layout.addWidget(self.cat_sort_combo)

        layout.addWidget(search_frame)

        # List widget
        self.catalyst_list = QListWidget()
        self.catalyst_list.setAlternatingRowColors(True)
        layout.addWidget(self.catalyst_list)

        # Stats footer
        self.cat_stats = QLabel("No data loaded")
        self.cat_stats.setStyleSheet("color: #00d4ff; font-weight: bold;")
        layout.addWidget(self.cat_stats)

        self.tabs.addTab(tab_widget, "⚡ Catalysts")

    def _setup_exotics_tab(self):
        """Setup exotics tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # Search
        self.ex_search = QLineEdit()
        self.ex_search.setPlaceholderText("🔍 Search exotic collection...")
        layout.addWidget(self.ex_search)

        # Tree widget for categorized view
        self.exotic_tree = QTreeWidget()
        self.exotic_tree.setHeaderLabels(["Name", "Type", "Source"])
        self.exotic_tree.setAlternatingRowColors(True)
        layout.addWidget(self.exotic_tree)

        # Stats footer
        self.ex_stats = QLabel("No data loaded")
        self.ex_stats.setStyleSheet("color: #00d4ff; font-weight: bold;")
        layout.addWidget(self.ex_stats)

        self.tabs.addTab(tab_widget, "💎 Exotics")

    def _setup_tools_tab(self):
        """Setup tools and utilities tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # Tools grid
        tools_grid = QGridLayout()

        # Export tools
        export_group = QGroupBox("📊 Data Export")
        export_layout = QVBoxLayout(export_group)

        self.export_json_btn = QPushButton("Export as JSON")
        self.export_csv_btn = QPushButton("Export as CSV")
        self.export_report_btn = QPushButton("Generate Report")

        export_layout.addWidget(self.export_json_btn)
        export_layout.addWidget(self.export_csv_btn)
        export_layout.addWidget(self.export_report_btn)

        tools_grid.addWidget(export_group, 0, 0)

        # API tools
        api_group = QGroupBox("🔧 API Tools")
        api_layout = QVBoxLayout(api_group)

        self.api_tester_btn = QPushButton("API Tester")
        self.refresh_manifest_btn = QPushButton("Refresh Manifest")
        self.clear_cache_btn = QPushButton("Clear Cache")

        api_layout.addWidget(self.api_tester_btn)
        api_layout.addWidget(self.refresh_manifest_btn)
        api_layout.addWidget(self.clear_cache_btn)

        tools_grid.addWidget(api_group, 0, 1)

        # Overlay tools
        overlay_group = QGroupBox("🎮 Overlay")
        overlay_layout = QVBoxLayout(overlay_group)

        self.overlay_btn = QPushButton("Overlay")
        self.overlay_config_btn = QPushButton("Overlay Settings")
        self.overlay_test_btn = QPushButton("Test Overlay")

        overlay_layout.addWidget(self.overlay_btn)
        overlay_layout.addWidget(self.overlay_config_btn)
        overlay_layout.addWidget(self.overlay_test_btn)

        tools_grid.addWidget(overlay_group, 1, 0)

        # System tools
        system_group = QGroupBox("⚙️ System")
        system_layout = QVBoxLayout(system_group)

        self.settings_btn = QPushButton("Settings")
        self.logs_viewer_btn = QPushButton("View Logs")
        self.diagnostics_btn = QPushButton("Run Diagnostics")

        system_layout.addWidget(self.settings_btn)
        system_layout.addWidget(self.logs_viewer_btn)
        system_layout.addWidget(self.diagnostics_btn)

        tools_grid.addWidget(system_group, 1, 1)

        layout.addLayout(tools_grid)
        layout.addStretch()

        self.tabs.addTab(tab_widget, "🔧 Tools")

    def _setup_footer(self):
        """Setup the application footer."""
        # Status bar
        self.status_bar = QStatusBar()

        # Add permanent widgets
        self.refresh_status = QLabel("Never refreshed")
        self.status_bar.addPermanentWidget(self.refresh_status)

        self.main_layout.addWidget(self.status_bar)

    def _setup_system_tray(self):
        """Setup enhanced system tray."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.warning("System tray not available")
            return

        tray_icon_path = get_asset_path("raidassist_icon.png")
        tray_icon = QIcon(tray_icon_path) if os.path.exists(tray_icon_path) else QIcon()

        self.tray_icon = QSystemTrayIcon(tray_icon, self)
        self.tray_icon.setToolTip("RaidAssist - Meta Progression Assistant")

        # Enhanced tray menu
        tray_menu = QMenu()

        # Main actions
        tray_menu.addAction("🏠 Show Dashboard", self._show_dashboard)
        tray_menu.addAction("🎮 Overlay", self._show_overlay)
        tray_menu.addSeparator()

        # Quick actions
        tray_menu.addAction("🔄 Refresh Data", self.refresh_data)
        tray_menu.addAction("📊 Quick Stats", self._show_quick_stats)
        tray_menu.addSeparator()

        # Settings and exit
        tray_menu.addAction("⚙️ Settings", self.open_settings)
        tray_menu.addAction("❌ Quit", self._quit_application)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _setup_connections(self):
        """Setup signal connections."""
        # Button connections
        self.refresh_button.clicked.connect(self.refresh_data)
        self.overlay_button.clicked.connect(self._show_overlay)
        self.settings_button.clicked.connect(self.open_settings)

        # Search connections
        if hasattr(self, "rb_search"):
            self.rb_search.textChanged.connect(self._filter_red_borders)
        if hasattr(self, "cat_search"):
            self.cat_search.textChanged.connect(self._filter_catalysts)
        if hasattr(self, "ex_search"):
            self.ex_search.textChanged.connect(self._filter_exotics)

        # Filter connections
        if hasattr(self, "rb_show_completed"):
            self.rb_show_completed.toggled.connect(self._filter_red_borders)
        if hasattr(self, "cat_show_completed"):
            self.cat_show_completed.toggled.connect(self._filter_catalysts)

        # Tools connections
        if hasattr(self, "export_json_btn"):
            self.export_json_btn.clicked.connect(lambda: self._export_data("json"))
            self.export_csv_btn.clicked.connect(lambda: self._export_data("csv"))
            self.api_tester_btn.clicked.connect(self._open_api_tester)

            # Additional tools connections
            self.overlay_btn.clicked.connect(self._show_overlay)
            self.settings_btn.clicked.connect(self.open_settings)

    def _setup_background_services(self):
        """Setup background services and timers."""
        # Auto-refresh timer
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self._auto_refresh)

        # Update refresh interval from settings
        self._update_refresh_interval()

        # Connection check timer
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self._check_connection)
        self.connection_timer.start(30000)  # Check every 30 seconds

        # Setup hotkeys if available
        self._setup_hotkeys()

    def _setup_hotkeys(self):
        """Setup global hotkeys."""
        if not HOTKEY_AVAILABLE:
            self.logger.info("Hotkey support not available")
            return

        try:
            # Register hotkeys using keybind
            keybind.register("ctrl+alt+r", self.refresh_data)  # type: ignore[misc]
            keybind.register("ctrl+alt+o", self._toggle_overlay)  # type: ignore[misc]
            self.logger.info("Global hotkeys registered successfully")
        except Exception as e:
            self.logger.warning(f"Failed to setup hotkeys: {e}")

    def _handle_initialization_error(self, error: Exception):
        """Handle initialization errors gracefully."""
        self.logger.error(f"UI initialization failed: {error}")

        if hasattr(self, "splash"):
            self.splash.close()

        QMessageBox.critical(
            None,
            "Initialization Error",
            f"Failed to initialize RaidAssist:\n\n{error}\n\n"
            "Please check your internet connection and try again.",
        )
        sys.exit(1)

    def _start_initial_data_load(self):
        """Start loading initial data in background."""
        self.splash.showMessage(
            "📡 Loading initial data...",
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
            QColor("#00d4ff"),
        )
        QApplication.processEvents()

        # Start background refresh
        self.refresh_data()

        # Hide splash screen
        QTimer.singleShot(1000, self._hide_splash)

    def _hide_splash(self):
        """Hide the splash screen."""
        if hasattr(self, "splash"):
            self.splash.close()

    # Data Management Methods
    def refresh_data(self):
        """Refresh all data with enhanced error handling."""
        if self._is_refreshing:
            self.logger.info("Refresh already in progress")
            return

        self._is_refreshing = True
        self.refresh_button.setEnabled(False)
        self.main_progress.setVisible(True)
        self.main_progress.setValue(0)

        # Start background refresh
        self.refresh_thread = DataRefreshThread()
        self.refresh_thread.data_loaded.connect(self._on_data_loaded)
        self.refresh_thread.error_occurred.connect(self._on_refresh_error)
        self.refresh_thread.progress_updated.connect(self._on_refresh_progress)
        self.refresh_thread.start()

    def _on_data_loaded(self, data: Dict[str, Any]):
        """Handle successful data loading."""
        try:
            with log_context("data_processing"):
                self._rb_items = self._process_red_borders(data.get("red_borders", []))
                self._cat_items = self._process_catalysts(data.get("catalysts", []))
                self._exotic_items = self._process_exotics(data.get("exotics", []))

                # Update UI
                self._update_all_displays()
                self._update_overlay_data()
                self._check_for_notifications()

                # Update status
                self._last_refresh_time = time.time()
                self.refresh_status.setText(
                    f"Last refresh: {time.strftime('%H:%M:%S')}"
                )
                self.status_label.setText("Data loaded successfully")
                self._connection_status = "Connected"
                self.connection_indicator.setText("🟢")

                self.logger.info("Data refresh completed successfully")

        except Exception as e:
            self.logger.error(f"Error processing loaded data: {e}")
            self._on_refresh_error(str(e))

        finally:
            self._is_refreshing = False
            self.refresh_button.setEnabled(True)
            self.main_progress.setVisible(False)

    def _on_refresh_error(self, error_message: str):
        """Handle refresh errors."""
        self.logger.error(f"Data refresh failed: {error_message}")

        self.status_label.setText(f"Refresh failed: {error_message}")
        self._connection_status = "Error"
        self.connection_indicator.setText("🔴")

        # Try to load cached data
        try:
            profile = load_profile()
            if profile:
                data = {
                    "red_borders": extract_red_borders(profile),
                    "catalysts": extract_catalysts(profile),
                    "exotics": extract_exotics(profile),
                }
                self._on_data_loaded(data)
                self.status_label.setText("Using cached data")
                return
        except:
            pass

        self._is_refreshing = False
        self.refresh_button.setEnabled(True)
        self.main_progress.setVisible(False)

    def _on_refresh_progress(self, value: int, message: str):
        """Handle refresh progress updates."""
        self.main_progress.setValue(value)
        self.status_label.setText(message)

    def _process_red_borders(
        self, red_borders: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process red border data for display."""
        processed = []
        for item in red_borders:
            item_info = get_item_info(item.get("itemInstanceId", ""), self.item_defs)
            processed.append(
                {
                    "raw": item,
                    "name": item_info.get("name", "Unknown"),
                    "type": item_info.get("type", "Unknown"),
                    "progress": item.get("progress", 0),
                    "needed": item.get("needed", 1),
                    "percent": item.get("percent", 0),
                    "icon": item_info.get("icon", ""),
                    "tooltip": self._build_tooltip(item_info),
                }
            )
        return processed

    def _process_catalysts(
        self, catalysts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process catalyst data for display."""
        processed = []
        for item in catalysts:
            item_info = get_item_info(item.get("itemInstanceId", ""), self.item_defs)
            processed.append(
                {
                    "raw": item,
                    "name": item_info.get("name", "Unknown"),
                    "type": item_info.get("type", "Unknown"),
                    "progress": item.get("progress", 0),
                    "needed": item.get("needed", 1),
                    "percent": item.get("percent", 0),
                    "icon": item_info.get("icon", ""),
                    "tooltip": self._build_tooltip(item_info),
                }
            )
        return processed

    def _process_exotics(self, exotics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process exotic data for display."""
        processed = []
        for item in exotics:
            item_info = get_item_info(item.get("itemHash", ""), self.item_defs)
            processed.append(
                {
                    "raw": item,
                    "name": item_info.get("name", "Unknown"),
                    "type": item_info.get("type", "Unknown"),
                    "icon": item_info.get("icon", ""),
                    "tooltip": self._build_tooltip(item_info),
                }
            )
        return processed

    def _build_tooltip(self, item_info: Dict[str, Any]) -> str:
        """Build enhanced tooltip for items."""
        lines = []
        if item_info.get("name"):
            lines.append(f"<b>{item_info['name']}</b>")
        if item_info.get("type"):
            lines.append(f"Type: {item_info['type']}")
        if item_info.get("archetype"):
            lines.append(f"Archetype: {item_info['archetype']}")
        if item_info.get("description"):
            lines.append(f"<i>{item_info['description']}</i>")
        return "<br>".join(lines)

    # UI Update Methods
    def _update_all_displays(self):
        """Update all UI displays with current data."""
        self._update_stats_panel()
        self._update_red_borders_display()
        self._update_catalysts_display()
        self._update_exotics_display()

    def _update_stats_panel(self):
        """Update the quick stats panel."""
        # Red borders stats
        rb_completed = sum(1 for item in self._rb_items if item["percent"] >= 100)
        rb_total = len(self._rb_items)
        rb_percent = int(100 * rb_completed / rb_total) if rb_total > 0 else 0
        self.rb_summary.value_label.setText(  # type: ignore[misc]
            f"{rb_completed}/{rb_total} ({rb_percent}%)"
        )

        # Catalysts stats
        cat_completed = sum(1 for item in self._cat_items if item["percent"] >= 100)
        cat_total = len(self._cat_items)
        cat_percent = int(100 * cat_completed / cat_total) if cat_total > 0 else 0
        self.cat_summary.value_label.setText(  # type: ignore[misc]
            f"{cat_completed}/{cat_total} ({cat_percent}%)"
        )

        # Exotics stats
        ex_total = len(self._exotic_items)
        self.ex_summary.value_label.setText(f"{ex_total}")  # type: ignore[misc]

    def _update_red_borders_display(self):
        """Update red borders list display."""
        self.red_border_list.clear()

        for item in self._rb_items:
            if not self._should_show_item(
                item, self.rb_search.text(), self.rb_show_completed.isChecked()
            ):
                continue

            list_item = QListWidgetItem()
            list_item.setText(
                f"{item['name']} - {item['progress']}/{item['needed']} ({item['percent']}%)"
            )
            list_item.setToolTip(item["tooltip"])

            # Color coding based on progress
            if item["percent"] >= 100:
                list_item.setData(Qt.ItemDataRole.ForegroundRole, QColor("#00ff00"))
            elif item["percent"] >= 50:
                list_item.setData(Qt.ItemDataRole.ForegroundRole, QColor("#ffff00"))
            else:
                list_item.setData(Qt.ItemDataRole.ForegroundRole, QColor("#ffffff"))

            self.red_border_list.addItem(list_item)

        # Update stats
        displayed = self.red_border_list.count()
        total = len(self._rb_items)
        self.rb_stats.setText(f"Showing {displayed} of {total} red border weapons")

    def _update_catalysts_display(self):
        """Update catalysts list display."""
        self.catalyst_list.clear()

        for item in self._cat_items:
            if not self._should_show_item(
                item, self.cat_search.text(), self.cat_show_completed.isChecked()
            ):
                continue

            list_item = QListWidgetItem()
            list_item.setText(
                f"{item['name']} - {item['progress']}/{item['needed']} ({item['percent']}%)"
            )
            list_item.setToolTip(item["tooltip"])

            # Color coding
            if item["percent"] >= 100:
                list_item.setData(Qt.ItemDataRole.ForegroundRole, QColor("#00ff00"))
            elif item["percent"] >= 50:
                list_item.setData(Qt.ItemDataRole.ForegroundRole, QColor("#ffff00"))

            self.catalyst_list.addItem(list_item)

        # Update stats
        displayed = self.catalyst_list.count()
        total = len(self._cat_items)
        self.cat_stats.setText(f"Showing {displayed} of {total} catalysts")

    def _update_exotics_display(self):
        """Update exotics tree display."""
        self.exotic_tree.clear()

        # Group by type
        categories = {}
        for item in self._exotic_items:
            item_type = item["type"] or "Unknown"
            if item_type not in categories:
                categories[item_type] = []
            categories[item_type].append(item)

        # Add to tree
        for category, items in categories.items():
            category_item = QTreeWidgetItem([category, "", ""])
            category_item.setExpanded(True)

            for item in items:
                if not self._should_show_exotic(item, self.ex_search.text()):
                    continue

                child_item = QTreeWidgetItem([item["name"], item["type"], "Collection"])
                child_item.setToolTip(0, item["tooltip"])
                category_item.addChild(child_item)

            if category_item.childCount() > 0:
                self.exotic_tree.addTopLevelItem(category_item)

        # Update stats
        total = len(self._exotic_items)
        self.ex_stats.setText(f"Collection: {total} exotics")

    def _should_show_item(
        self, item: Dict[str, Any], search_text: str, show_completed: bool
    ) -> bool:
        """Determine if item should be shown based on filters."""
        # Search filter
        if search_text and search_text.lower() not in item["name"].lower():
            return False

        # Completion filter
        if not show_completed and item["percent"] >= 100:
            return False

        return True

    def _should_show_exotic(self, item: Dict[str, Any], search_text: str) -> bool:
        """Determine if exotic should be shown based on search."""
        if search_text and search_text.lower() not in item["name"].lower():
            return False
        return True

    # Filter Methods
    def _filter_red_borders(self):
        """Apply filters to red borders display."""
        self._update_red_borders_display()

    def _filter_catalysts(self):
        """Apply filters to catalysts display."""
        self._update_catalysts_display()

    def _filter_exotics(self):
        """Apply filters to exotics display."""
        self._update_exotics_display()

    # Overlay Methods
    def _show_overlay(self):
        """Show the overlay system."""
        if not OVERLAY_AVAILABLE:
            QMessageBox.warning(
                self,
                "Overlay Unavailable",
                "The overlay system is not available.\n"
                "Please check that all required components are installed.",
            )
            return

        try:
            if (
                self.overlay_ref
                and hasattr(self.overlay_ref, "isVisible")
                and getattr(self.overlay_ref, "isVisible", lambda: False)()
            ):
                if hasattr(self.overlay_ref, "raise_"):
                    getattr(self.overlay_ref, "raise_", lambda: None)()
                if hasattr(self.overlay_ref, "activateWindow"):
                    getattr(self.overlay_ref, "activateWindow", lambda: None)()
                return

            # Prepare data for overlay
            overlay_data = {
                "red_borders": [item["raw"] for item in self._rb_items],
                "catalysts": [item["raw"] for item in self._cat_items],
                "exotics": [item["raw"] for item in self._exotic_items],
            }

            self.overlay_ref = create_overlay(None)
            if self.overlay_ref:
                if hasattr(self.overlay_ref, "update_data"):
                    getattr(self.overlay_ref, "update_data", lambda x: None)(
                        overlay_data
                    )
                if hasattr(self.overlay_ref, "show"):
                    getattr(self.overlay_ref, "show", lambda: None)()
                self.logger.info("Overlay opened successfully")
            else:
                raise RuntimeError("Failed to create overlay instance")

        except Exception as e:
            self.logger.error(f"Failed to show overlay: {e}")
            QMessageBox.warning(self, "Overlay Error", f"Failed to open overlay:\n{e}")

    def _toggle_overlay(self):
        """Toggle overlay visibility."""
        if (
            self.overlay_ref
            and hasattr(self.overlay_ref, "isVisible")
            and getattr(self.overlay_ref, "isVisible", lambda: False)()
        ):
            if hasattr(self.overlay_ref, "close"):
                getattr(self.overlay_ref, "close", lambda: None)()
        else:
            self._show_overlay()

    def _update_overlay_data(self):
        """Update overlay with current data."""
        if (
            self.overlay_ref
            and hasattr(self.overlay_ref, "isVisible")
            and getattr(self.overlay_ref, "isVisible", lambda: False)()
        ):
            overlay_data = {
                "red_borders": [item["raw"] for item in self._rb_items],
                "catalysts": [item["raw"] for item in self._cat_items],
                "exotics": [item["raw"] for item in self._exotic_items],
            }
            if hasattr(self.overlay_ref, "update_data"):
                getattr(self.overlay_ref, "update_data", lambda x: None)(overlay_data)

    # Utility Methods
    def _check_connection(self):
        """Check API connection status."""

        def check_in_background():
            try:
                if test_api_connection():
                    self._connection_status = "Connected"
                    self.connection_indicator.setText("🟢")
                else:
                    self._connection_status = "Disconnected"
                    self.connection_indicator.setText("🔴")
            except:
                self._connection_status = "Error"
                self.connection_indicator.setText("🔴")

        # Run in background to avoid blocking UI
        QTimer.singleShot(0, check_in_background)

    def _auto_refresh(self):
        """Perform automatic refresh."""
        if not self._is_refreshing:
            self.refresh_data()

    def _update_refresh_interval(self):
        """Update auto-refresh interval from settings."""
        settings = load_settings()
        interval = settings.get("refresh_interval_seconds", 300) * 1000  # Convert to ms
        self.auto_refresh_timer.start(interval)

    def _check_for_notifications(self):
        """Check for completion notifications."""
        # This would implement notification logic similar to the original
        # but with enhanced error handling
        pass

    def _export_data(self, format_type: str):
        """Export data in specified format."""
        try:
            current_tab = self.tabs.currentIndex()
            if current_tab == 0:  # Red Borders
                data = [item["raw"] for item in self._rb_items]
                filename = f"red_borders.{format_type}"
            elif current_tab == 1:  # Catalysts
                data = [item["raw"] for item in self._cat_items]
                filename = f"catalysts.{format_type}"
            elif current_tab == 2:  # Exotics
                data = [item["raw"] for item in self._exotic_items]
                filename = f"exotics.{format_type}"
            else:
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Data",
                filename,
                f"{format_type.upper()} Files (*.{format_type})",
            )

            if file_path:
                if format_type == "json":
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                elif format_type == "csv":
                    # CSV export logic would go here
                    pass

                QMessageBox.information(
                    self, "Export Successful", f"Data exported to {file_path}"
                )

        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            QMessageBox.warning(self, "Export Failed", f"Failed to export data:\n{e}")

    def _open_api_tester(self):
        """Open the API tester dialog."""
        try:
            dialog = ApiTesterDialog(self)
            dialog.exec_()
        except Exception as e:
            self.logger.error(f"Failed to open API tester: {e}")

    def open_settings(self):
        """Open settings dialog."""
        try:
            dialog = SettingsDialog(self)
            if dialog.exec_():
                self._update_refresh_interval()
        except Exception as e:
            self.logger.error(f"Failed to open settings: {e}")

    # System tray handlers
    def _on_tray_activated(self, reason):
        """Handle system tray activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_dashboard()

    def _show_dashboard(self):
        """Show the main dashboard."""
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _show_quick_stats(self):
        """Show quick stats notification."""
        if hasattr(self, "tray_icon"):
            rb_stats = f"Red Borders: {len(self._rb_items)}"
            cat_stats = f"Catalysts: {len(self._cat_items)}"
            ex_stats = f"Exotics: {len(self._exotic_items)}"

            self.tray_icon.showMessage(
                "RaidAssist Quick Stats",
                f"{rb_stats}\n{cat_stats}\n{ex_stats}",
                QSystemTrayIcon.MessageIcon.Information,
                5000,
            )

    def closeEvent(self, event):
        """Handle window close event."""
        # Cleanup hotkeys before closing
        if HOTKEY_AVAILABLE:
            try:
                keybind.clear()  # type: ignore[misc]
            except:
                pass

        # Minimize to tray instead of closing
        if hasattr(self, "tray_icon") and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

    def _quit_application(self):
        """Quit the application properly."""
        app = QApplication.instance()
        if app:
            app.quit()


if __name__ == "__main__":
    """Entry point for testing."""
    app = QApplication(sys.argv)

    # Setup application properties
    app.setApplicationName("RaidAssist")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("RaidAssist")

    # Create and show main window
    window = RaidAssistUI()
    window.show()

    sys.exit(app.exec_())
