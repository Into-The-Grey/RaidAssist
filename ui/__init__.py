# RaidAssist — UI Module
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>

"""
RaidAssist UI Module - Interface components.

This module provides the user interface components including:
- RaidAssistUI: Main application interface
- Overlay: Professional overlay system (8/10 quality)
- Settings, API tester, and loading dialogs
"""

__version__ = "2.0.0"
__author__ = "Nicholas Acord"

# Check for Qt availability
QT_AVAILABLE = False
try:
    import PySide6

    QT_AVAILABLE = True
except ImportError:
    pass

# UI imports with fallbacks
UI_AVAILABLE = False
OVERLAY_AVAILABLE = False

if QT_AVAILABLE:
    try:
        from .api_tester import ApiTesterDialog
        from .interface import RaidAssistUI
        from .loading import LoadingDialog
        from .settings import SettingsDialog

        UI_AVAILABLE = True
    except ImportError:
        pass

    try:
        from .overlay import Overlay, create_overlay

        OVERLAY_AVAILABLE = True
    except ImportError:
        pass

# Export available components
__all__ = [
    "QT_AVAILABLE",
    "UI_AVAILABLE",
    "OVERLAY_AVAILABLE",
]

# Add components if available
if UI_AVAILABLE:
    __all__.extend(
        [
            "RaidAssistUI",
            "SettingsDialog",
            "LoadingDialog",
            "ApiTesterDialog",
        ]
    )

if OVERLAY_AVAILABLE:
    __all__.extend(["Overlay", "create_overlay"])


# Version info
def get_ui_version():
    """Get UI module version information."""
    return {
        "version": __version__,
        "qt_available": QT_AVAILABLE,
        "ui_available": UI_AVAILABLE,
        "overlay_available": OVERLAY_AVAILABLE,
        "components": __all__,
    }
