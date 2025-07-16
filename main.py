# RaidAssist — Destiny 2 Progression Tracker and Overlay
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact: ncacord@protonmail.com

"""
main.py — Enhanced entry point for RaidAssist.

This now launches the complete enhanced GUI application with:
- Advanced error handling and logging
- Professional UI design
- Enhanced overlay system (7-8/10 quality)
- Robust data management
- System tray integration
- Hotkey support

For CLI-only usage, use the individual API modules directly.
"""

import os
import sys

# Enhanced error handling
try:
    from utils.logging_manager import get_logger

    logger = get_logger("raidassist.main")
    LOGGING = True
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("raidassist.main")
    LOGGING = False

# GUI imports
try:
    from PySide6.QtCore import Qt  # type: ignore
    from PySide6.QtWidgets import QApplication, QMessageBox  # type: ignore

    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


def ensure_gui_dependencies():
    """Ensure GUI dependencies are available."""
    if not GUI_AVAILABLE:
        print("❌ GUI dependencies not available!")
        print("Please install PySide6: pip install PySide6")
        return False
    return True


def launch_ui():
    """Launch the UI application."""
    try:
        from ui import UI_AVAILABLE
        from ui.interface import RaidAssistUI

        if not UI_AVAILABLE:
            logger.error("UI not available - Qt/PySide6 not installed")
            print("❌ No UI available - Qt/PySide6 not installed")
            return 1

        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("RaidAssist")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("RaidAssist")
        app.setQuitOnLastWindowClosed(False)  # Keep running in tray

        # Create and show main window
        window = RaidAssistUI()
        window.show()

        logger.info("RaidAssist UI launched successfully")
        return app.exec_()

    except Exception as e:
        logger.error(f"Failed to launch UI: {e}")
        if GUI_AVAILABLE:
            QMessageBox.critical(
                None,
                "Launch Error",
                f"Failed to start RaidAssist:\n\n{e}\n\n"
                "Please check your installation and try again.",
            )
        else:
            print(f"❌ Launch failed: {e}")
        return 1


def main():
    """Main entry point with error handling."""
    # Check GUI availability
    if not ensure_gui_dependencies():
        return 1

    print("🎮 Starting RaidAssist...")
    print("Destiny 2 Progression Tracker and Overlay")
    print("=" * 50)

    try:
        logger.info("Attempting to launch UI")
        return launch_ui()

    except Exception as e:
        logger.error(f"Unexpected error during launch: {e}")
        print(f"❌ Critical error: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 RaidAssist stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)
