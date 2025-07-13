# RaidAssist — Destiny 2 Progression Tracker and Overlay
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>

"""
advanced_overlay.py — Modern, customizable overlay system for RaidAssist.

Features:
- Multiple overlay widgets (progress bars, charts, notifications)
- Drag-and-drop layout customization
- Real-time data updates
- Multiple display modes (compact, detailed, charts)
- Themeable and customizable appearance
- Performance optimized for gaming
"""

import sys
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import math
import time

# Qt imports with proper error handling
QT_AVAILABLE = False
try:
    from PySide2.QtWidgets import ( # type: ignore
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSlider,
        QFrame,
        QGraphicsEffect,
        QGraphicsDropShadowEffect,
        QGridLayout,
        QScrollArea,
        QCheckBox,
        QComboBox,
        QSpinBox,
        QGroupBox,
        QProgressBar,
        QApplication,
        QSystemTrayIcon,
        QMenu,
        QAction,
        QColorDialog,
        QFontDialog,
        QSizePolicy,
        QStackedWidget,
    )
    from PySide2.QtCore import ( # type: ignore
        Qt,
        QTimer,
        QPropertyAnimation,
        QEasingCurve,
        QRect,
        QPoint,
        QSize,
        Signal,
        QThread,
        QMutex,
        QObject,
        Slot,
    )
    from PySide2.QtGui import ( # type: ignore
        QPainter,
        QColor,
        QFont,
        QPixmap,
        QIcon,
        QPen,
        QBrush,
        QLinearGradient,
        QRadialGradient,
        QPainterPath,
        QFontMetrics,
        QMouseEvent,
        QPaintEvent,
    )

    QT_AVAILABLE = True
except ImportError:
    # Create placeholder classes when Qt is not available
    pass

# Always import these for type definitions
from utils.logging_manager import get_logger, log_context
# utils.error_handler provides ``safe_execute`` and ``handle_error`` for
# generalised exception handling. ``handle_exception`` was never a public
# helper, so attempting to import it causes an ImportError when this module
# is loaded.  Import the correct helper instead.
from utils.error_handler import safe_execute, handle_error


class OverlayDisplayMode(Enum):
    """Display modes for overlay widgets."""

    COMPACT = "compact"
    DETAILED = "detailed"
    CHARTS = "charts"
    MINIMAL = "minimal"


class OverlayTheme(Enum):
    """Predefined overlay themes."""

    DARK = "dark"
    LIGHT = "light"
    DESTINY = "destiny"
    MINIMAL = "minimal"
    GAMING = "gaming"
    CUSTOM = "custom"


class WidgetType(Enum):
    """Types of overlay widgets."""

    PROGRESS_BAR = "progress_bar"
    PROGRESS_RING = "progress_ring"
    TEXT_DISPLAY = "text_display"
    CHART = "chart"
    NOTIFICATION = "notification"
    SUMMARY = "summary"
    TIMER = "timer"
    STATS = "stats"


@dataclass
class OverlayConfig:
    """Configuration for overlay appearance and behavior."""

    # Position and size
    x: int = 100
    y: int = 100
    width: int = 350
    height: int = 450

    # Appearance
    theme: str = OverlayTheme.DARK.value
    opacity: float = 0.9
    background_color: str = "#1a1a1a"
    text_color: str = "#ffffff"
    accent_color: str = "#00d4ff"
    font_family: str = "Segoe UI"
    font_size: int = 10

    # Behavior
    always_on_top: bool = True
    frameless: bool = True
    draggable: bool = True
    resizable: bool = True
    auto_hide: bool = False
    auto_hide_delay: int = 5000

    # Animation settings
    enable_animations: bool = True
    animation_speed: int = 300
    fade_duration: int = 200

    # Data refresh
    auto_refresh: bool = True
    refresh_interval: int = 30000  # 30 seconds

    # Widget configuration
    widgets_enabled: Dict[str, bool] = field(default_factory=dict)
    widget_order: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize default widget configurations."""
        if not self.widgets_enabled:
            self.widgets_enabled = {
                WidgetType.PROGRESS_BAR.value: True,
                WidgetType.TEXT_DISPLAY.value: True,
                WidgetType.NOTIFICATION.value: True,
                WidgetType.SUMMARY.value: True,
                WidgetType.TIMER.value: False,
                WidgetType.STATS.value: True,
            }

        if not self.widget_order:
            self.widget_order = [
                WidgetType.SUMMARY.value,
                WidgetType.PROGRESS_BAR.value,
                WidgetType.TEXT_DISPLAY.value,
                WidgetType.NOTIFICATION.value,
            ]


# Only define Qt-dependent classes when Qt is available
if QT_AVAILABLE:

    class BaseOverlayWidget(QWidget):
        """Base class for all overlay widgets with common functionality."""

        def __init__(self, widget_type: WidgetType, config: OverlayConfig):
            super().__init__()
            self.widget_type = widget_type
            self.config = config
            self.logger = get_logger("raidassist.overlay")
            self.last_update = 0
            self.data = {}

            self.setMinimumSize(200, 40)
            self.setAttribute(Qt.WA_TranslucentBackground)

            # Setup styling
            self._setup_styling()

            # Animation setup
            if config.enable_animations:
                self._setup_animations()

        def _setup_styling(self):
            """Setup basic widget styling."""
            self.setStyleSheet(
                f"""
                QWidget {{
                    background-color: {self.config.background_color};
                    color: {self.config.text_color};
                    font-family: {self.config.font_family};
                    font-size: {self.config.font_size}px;
                    border-radius: 8px;
                    border: 1px solid {self.config.accent_color};
                }}
            """
            )

        def _setup_animations(self):
            """Setup animations for the widget."""
            self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
            self.fade_animation.setDuration(self.config.fade_duration)
            self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

        def fade_in(self):
            """Animate widget fade in."""
            if hasattr(self, "fade_animation"):
                self.fade_animation.setStartValue(0.0)
                self.fade_animation.setEndValue(self.config.opacity)
                self.fade_animation.start()

        def fade_out(self):
            """Animate widget fade out."""
            if hasattr(self, "fade_animation"):
                self.fade_animation.setStartValue(self.config.opacity)
                self.fade_animation.setEndValue(0.0)
                self.fade_animation.start()

        def update_data(self, data: Dict[str, Any]):
            """Update widget with new data."""
            self.data = data
            self.last_update = time.time()
            self.update_display()

        def update_display(self):
            """Update the visual display - override in subclasses."""
            pass

    class ProgressOverlayWidget(BaseOverlayWidget):
        """Widget for displaying progress bars for various activities."""

        def __init__(self, config: OverlayConfig):
            super().__init__(WidgetType.PROGRESS_BAR, config)
            self.progress_bars = {}
            self.progress_labels = {}
            self._setup_ui()

        def _setup_ui(self):
            """Setup the progress widget UI."""
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(8)

            # Title
            self.title_label = QLabel("Progress Overview")
            self.title_label.setAlignment(Qt.AlignCenter)
            self.title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            layout.addWidget(self.title_label)

            # Progress container
            self.progress_container = QVBoxLayout()
            layout.addLayout(self.progress_container)

            # Initialize default progress items
            self._setup_default_progress_items()

        def _setup_default_progress_items(self):
            """Setup default progress tracking items."""
            progress_items = [
                ("Raid Completions", "#ff6b35"),
                ("Dungeon Completions", "#f7931e"),
                ("Exotic Collections", "#00d4ff"),
                ("Triumph Score", "#c77dff"),
                ("Season Pass", "#90e0ef"),
            ]

            for name, color in progress_items:
                self._add_progress_item(name, color)

        def _add_progress_item(self, name: str, color: str):
            """Add a progress tracking item."""
            # Label
            label = QLabel(f"{name}: 0/0 (0%)")
            label.setStyleSheet(f"color: {color}; font-weight: bold;")
            self.progress_labels[name] = label

            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setMaximum(100)
            progress_bar.setValue(0)
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(8)
            progress_bar.setStyleSheet(
                f"""
                QProgressBar {{
                    border: 1px solid #555;
                    border-radius: 4px;
                    background-color: #333;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 3px;
                }}
            """
            )
            self.progress_bars[name] = progress_bar

            # Add to layout
            self.progress_container.addWidget(label)
            self.progress_container.addWidget(progress_bar)

        def update_display(self):
            """Update progress bars with current data."""
            if not self.data:
                return

            # Update each progress item
            progress_data = self.data.get("progress", {})
            for name, progress_bar in self.progress_bars.items():
                if name in progress_data:
                    data = progress_data[name]
                    current = data.get("current", 0)
                    total = data.get("total", 1)
                    percentage = int((current / total) * 100) if total > 0 else 0

                    # Update progress bar
                    self._animate_progress_change(progress_bar, percentage)

                    # Update label
                    label = self.progress_labels[name]
                    label.setText(f"{name}: {current}/{total} ({percentage}%)")

        def _animate_progress_change(
            self, progress_bar: QProgressBar, target_value: int
        ):
            """Animate progress bar value changes."""
            if not self.config.enable_animations:
                progress_bar.setValue(target_value)
                return

            current_value = progress_bar.value()
            if current_value == target_value:
                return

            # Create animation for smooth progress updates
            animation = QPropertyAnimation(progress_bar, b"value")
            animation.setDuration(500)
            animation.setStartValue(current_value)
            animation.setEndValue(target_value)
            animation.setEasingCurve(QEasingCurve.OutCubic)

            # Store animation to prevent garbage collection
            progress_bar._animation = animation
            animation.start()

    class AdvancedOverlay(QWidget): # type: ignore
        """Main advanced overlay window with multiple widgets."""

        # Signals for communication
        data_updated = Signal(dict)
        widget_added = Signal(str)
        widget_removed = Signal(str)
        config_changed = Signal(dict)

        def __init__(self, config: Optional[OverlayConfig] = None):
            super().__init__()
            self.config = config or OverlayConfig()
            self.logger = get_logger("raidassist.overlay.main")
            self.widgets = {}
            self.data_cache = {}

            # Setup window properties
            self._setup_window()

            # Setup UI
            self._setup_ui()

            # Setup timers for auto-refresh
            self._setup_timers()

            self.logger.info("Advanced overlay initialized")

        def _setup_window(self):
            """Setup window properties and behavior."""
            self.setWindowTitle("RaidAssist Overlay")
            self.setGeometry(
                self.config.x, self.config.y, self.config.width, self.config.height
            )

            # Window flags for overlay behavior
            flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
            if self.config.frameless:
                flags |= Qt.Tool
            self.setWindowFlags(flags)

            # Transparency and styling
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setWindowOpacity(self.config.opacity)

            # Apply theme styling
            self._apply_theme()

        def _setup_ui(self):
            """Setup the overlay user interface."""
            self.main_layout = QVBoxLayout(self)
            self.main_layout.setContentsMargins(5, 5, 5, 5)
            self.main_layout.setSpacing(5)

            # Add enabled widgets
            self._create_enabled_widgets()

        def _setup_timers(self):
            """Setup auto-refresh timers."""
            if self.config.auto_refresh:
                self.refresh_timer = QTimer()
                self.refresh_timer.timeout.connect(self._auto_refresh_data)
                self.refresh_timer.start(self.config.refresh_interval)

        def _apply_theme(self):
            """Apply the selected theme to the overlay."""
            themes = {
                "dark": {
                    "background": "#1a1a1a",
                    "text": "#ffffff",
                    "accent": "#00d4ff",
                    "border": "#333333",
                },
                "light": {
                    "background": "#f0f0f0",
                    "text": "#000000",
                    "accent": "#0066cc",
                    "border": "#cccccc",
                },
                "destiny": {
                    "background": "#0d1421",
                    "text": "#f1c40f",
                    "accent": "#e74c3c",
                    "border": "#34495e",
                },
            }

            theme = themes.get(self.config.theme, themes["dark"])

            self.setStyleSheet(
                f"""
                QWidget {{
                    background-color: {theme['background']};
                    color: {theme['text']};
                    border: 2px solid {theme['border']};
                    border-radius: 10px;
                }}
            """
            )

        def _create_enabled_widgets(self):
            """Create and add enabled overlay widgets."""
            for widget_type in self.config.widget_order:
                if self.config.widgets_enabled.get(widget_type, False):
                    self._add_widget(widget_type)

        def _add_widget(self, widget_type: str):
            """Add a widget to the overlay."""
            try:
                if widget_type == WidgetType.PROGRESS_BAR.value:
                    widget = ProgressOverlayWidget(self.config)
                    self.widgets[widget_type] = widget
                    self.main_layout.addWidget(widget)
                    self.widget_added.emit(widget_type)

                self.logger.debug(f"Added widget: {widget_type}")

            except Exception as e:
                self.logger.error(f"Failed to add widget {widget_type}: {e}")

        def update_data(self, data: Dict[str, Any]):
            """Update all widgets with new data."""
            self.data_cache.update(data)

            for widget in self.widgets.values():
                safe_execute(widget.update_data, data, default_return=None)

            self.data_updated.emit(data)

        def _auto_refresh_data(self):
            """Auto-refresh data from API sources."""
            # This would be connected to actual data sources
            self.logger.debug("Auto-refreshing overlay data")

        def show_overlay(self):
            """Show the overlay with animations if enabled."""
            self.show()
            if self.config.enable_animations:
                for widget in self.widgets.values():
                    if hasattr(widget, "fade_in"):
                        widget.fade_in()

        def hide_overlay(self):
            """Hide the overlay with animations if enabled."""
            if self.config.enable_animations:
                for widget in self.widgets.values():
                    if hasattr(widget, "fade_out"):
                        widget.fade_out()

            # Hide after animation completes
            QTimer.singleShot(self.config.fade_duration, self.hide)

        def mousePressEvent(self, event: QMouseEvent):
            """Handle mouse press for dragging."""
            if self.config.draggable and event.button() == Qt.LeftButton:
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

        def mouseMoveEvent(self, event: QMouseEvent):
            """Handle mouse move for dragging."""
            if (
                self.config.draggable
                and event.buttons() == Qt.LeftButton
                and hasattr(self, "drag_position")
            ):
                self.move(event.globalPos() - self.drag_position)
                event.accept()

else:
    # Fallback classes when Qt is not available
    class AdvancedOverlay:
        """Fallback overlay class when Qt is not available."""

        def __init__(self, config=None):
            self.logger = get_logger("raidassist.overlay.fallback")
            self.logger.warning("Qt not available - overlay disabled")

        def show_overlay(self):
            self.logger.warning("Cannot show overlay - Qt not available")

        def hide_overlay(self):
            pass

        def update_data(self, data):
            pass


def create_advanced_overlay(config: Optional[OverlayConfig] = None) -> AdvancedOverlay:
    """Create and return an advanced overlay instance."""
    if not QT_AVAILABLE:
        logger = get_logger("raidassist.overlay")
        logger.warning("Creating fallback overlay - Qt not available")

    return AdvancedOverlay(config)


def load_overlay_config(config_path: str) -> OverlayConfig:
    """Load overlay configuration from file."""
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                data = json.load(f)
                return OverlayConfig(**data)
    except Exception as e:
        logger = get_logger("raidassist.overlay")
        logger.error(f"Failed to load overlay config: {e}")

    return OverlayConfig()


def save_overlay_config(config: OverlayConfig, config_path: str):
    """Save overlay configuration to file."""
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(asdict(config), f, indent=2)
    except Exception as e:
        logger = get_logger("raidassist.overlay")
        logger.error(f"Failed to save overlay config: {e}")
