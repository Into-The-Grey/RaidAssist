# RaidAssist — Destiny 2 Progression Tracker and Overlay
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>

"""
error_handler.py — Robust error handling and recovery system for RaidAssist.

Provides centralized error handling, user-friendly error messages, and automatic recovery.
"""

import sys
import traceback
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import os

try:
    from PySide2.QtWidgets import QMessageBox, QWidget
    from PySide2.QtCore import QTimer

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

    # Dummy classes for type hints when Qt not available
    class QWidget:
        pass

    class QMessageBox:
        # Icon constants
        critical = 3
        warning = 2
        information = 1
        # Keep compatibility with Qt naming
        Critical = critical
        Warning = warning
        Information = information
        
        def __init__(self, parent=None):
            pass
            
        def set_icon(self, icon):
            pass
            
        def setIcon(self, icon):
            """Compatibility method for Qt naming convention"""
            return self.set_icon(icon)
            
        def set_window_title(self, title):
            pass
            
        def setWindowTitle(self, title):
            """Compatibility method for Qt naming convention"""
            return self.set_window_title(title)
            
        def set_text(self, text):
            pass
            
        def setText(self, text):
            """Compatibility method for Qt naming convention"""
            return self.set_text(text)
            
        def set_detailed_text(self, text):
            pass
            
        def setDetailedText(self, text):
            """Compatibility method for Qt naming convention"""
            return self.set_detailed_text(text)
            
        def set_informative_text(self, text):
            pass
            
        def setInformativeText(self, text):
            """Compatibility method for Qt naming convention"""
            return self.set_informative_text(text)
            
        def exec_(self):
            pass

    class QTimer:
        pass


from utils.logging_manager import logger_manager, log_context


class ErrorSeverity(Enum):
    """Error severity levels for proper handling and user notification."""

    LOW = "low"  # Minor issues, app continues normally
    MEDIUM = "medium"  # Noticeable issues, some features may be affected
    HIGH = "high"  # Significant issues, core functionality affected
    CRITICAL = "critical"  # App-breaking issues, requires immediate attention


class ErrorCategory(Enum):
    """Categories of errors for better classification and handling."""

    NETWORK = "network"  # API calls, internet connectivity
    AUTH = "authentication"  # OAuth, token issues
    DATA = "data"  # Profile parsing, manifest loading
    UI = "ui"  # Interface errors, widget issues
    SYSTEM = "system"  # File I/O, permissions, system resources
    UNKNOWN = "unknown"  # Unclassified errors


@dataclass
class ErrorInfo:
    """Complete error information for proper handling and display."""

    id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    technical_details: str
    user_message: str
    suggestions: List[str]
    timestamp: datetime
    context: List[str]
    recoverable: bool
    recovery_action: Optional[Callable] = None


class ErrorHandler:
    """
    Centralized error handling system for RaidAssist.

    Features:
    - Automatic error classification
    - User-friendly error messages
    - Recovery suggestions and actions
    - Error tracking and statistics
    - Integration with logging system
    """

    def __init__(self):
        self.error_history: List[ErrorInfo] = []
        self.error_patterns: Dict[str, ErrorInfo] = {}
        self.recovery_callbacks: Dict[ErrorCategory, List[Callable]] = {}
        self.ui_parent: Optional[QWidget] = None

        # Load known error patterns
        self._load_error_patterns()

        # Setup system exception handler
        self._setup_exception_handler()

    def set_ui_parent(self, parent: QWidget):
        """Set the parent widget for error dialogs."""
        self.ui_parent = parent

    def _setup_exception_handler(self):
        """Setup global exception handler for unhandled exceptions."""

        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                # Allow Ctrl+C to work normally
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            # Handle all other exceptions
            error_info = self._create_error_info(
                exception=exc_value,
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.CRITICAL,
                context=["global_exception_handler"],
            )

            self._handle_error(error_info)

            # Call original handler for proper cleanup
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

        sys.excepthook = handle_exception

    def _load_error_patterns(self):
        """Load known error patterns and their handling strategies."""
        self.error_patterns.update(
            {
                # Network errors
                "connection_timeout": ErrorInfo(
                    id="NET001",
                    category=ErrorCategory.NETWORK,
                    severity=ErrorSeverity.MEDIUM,
                    message="Connection timeout",
                    technical_details="Request timed out",
                    user_message="Unable to connect to Bungie servers. Please check your internet connection.",
                    suggestions=[
                        "Check your internet connection",
                        "Try again in a few moments",
                        "Check if Bungie servers are online",
                    ],
                    timestamp=datetime.now(),
                    context=[],
                    recoverable=True,
                ),
                "api_rate_limit": ErrorInfo(
                    id="NET002",
                    category=ErrorCategory.NETWORK,
                    severity=ErrorSeverity.MEDIUM,
                    message="API rate limit exceeded",
                    technical_details="Too many requests to Bungie API",
                    user_message="You're making requests too quickly. Please wait a moment before trying again.",
                    suggestions=[
                        "Wait 60 seconds before trying again",
                        "Reduce auto-refresh frequency in settings",
                    ],
                    timestamp=datetime.now(),
                    context=[],
                    recoverable=True,
                ),
                # Authentication errors
                "token_expired": ErrorInfo(
                    id="AUTH001",
                    category=ErrorCategory.AUTH,
                    severity=ErrorSeverity.HIGH,
                    message="Access token expired",
                    technical_details="OAuth token has expired",
                    user_message="Your login session has expired. Please log in again.",
                    suggestions=[
                        "Click 'Refresh' to log in again",
                        "Restart the application if the issue persists",
                    ],
                    timestamp=datetime.now(),
                    context=[],
                    recoverable=True,
                ),
                "invalid_credentials": ErrorInfo(
                    id="AUTH002",
                    category=ErrorCategory.AUTH,
                    severity=ErrorSeverity.HIGH,
                    message="Invalid credentials",
                    technical_details="Authentication failed",
                    user_message="Unable to authenticate with Bungie. Please check your login details.",
                    suggestions=[
                        "Restart the application to log in again",
                        "Make sure you're using the correct Bungie account",
                    ],
                    timestamp=datetime.now(),
                    context=[],
                    recoverable=True,
                ),
                # Data errors
                "profile_not_found": ErrorInfo(
                    id="DATA001",
                    category=ErrorCategory.DATA,
                    severity=ErrorSeverity.MEDIUM,
                    message="Profile data not found",
                    technical_details="No cached profile data available",
                    user_message="No profile data found. Please refresh to load your Destiny 2 data.",
                    suggestions=[
                        "Click 'Refresh' to load your profile",
                        "Make sure you have a Destiny 2 character",
                    ],
                    timestamp=datetime.now(),
                    context=[],
                    recoverable=True,
                ),
                "manifest_error": ErrorInfo(
                    id="DATA002",
                    category=ErrorCategory.DATA,
                    severity=ErrorSeverity.HIGH,
                    message="Manifest loading failed",
                    technical_details="Unable to load Destiny 2 manifest data",
                    user_message="Unable to load game data. Some features may not work correctly.",
                    suggestions=[
                        "Restart the application",
                        "Check your internet connection",
                        "Clear cache and try again",
                    ],
                    timestamp=datetime.now(),
                    context=[],
                    recoverable=True,
                ),
            }
        )

    def _create_error_info(
        self,
        exception: Optional[Exception] = None,
        message: Optional[str] = None,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[List[str]] = None,
        user_message: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
    ) -> ErrorInfo:
        """Create a complete ErrorInfo object from exception or message."""

        error_id = f"{category.value.upper()[:3]}{len(self.error_history) + 1:03d}"

        if exception:
            exc_type = type(exception).__name__
            exc_message = str(exception)
            technical_details = f"{exc_type}: {exc_message}\n{traceback.format_exc()}"

            # Try to match known error patterns
            pattern_key = self._match_error_pattern(exception)
            if pattern_key and pattern_key in self.error_patterns:
                pattern = self.error_patterns[pattern_key]
                category = pattern.category
                severity = pattern.severity
                user_message = user_message or pattern.user_message
                suggestions = suggestions or pattern.suggestions

            display_message = message or exc_message
        else:
            display_message = message or "Unknown error occurred"
            technical_details = message or "No technical details available"

        return ErrorInfo(
            id=error_id,
            category=category,
            severity=severity,
            message=display_message,
            technical_details=technical_details,
            user_message=user_message
            or self._generate_user_message(display_message, category),
            suggestions=suggestions or self._generate_suggestions(category),
            timestamp=datetime.now(),
            context=context or [],
            recoverable=self._is_recoverable(category, severity),
        )

    def _match_error_pattern(self, exception: Exception) -> Optional[str]:
        """Match exception to known error patterns."""
        exc_str = str(exception).lower()
        exc_type = type(exception).__name__.lower()

        # Network error patterns
        if "timeout" in exc_str or "timed out" in exc_str:
            return "connection_timeout"

        if "rate limit" in exc_str or "too many requests" in exc_str:
            return "api_rate_limit"

        # Authentication patterns
        if "token" in exc_str and ("expired" in exc_str or "invalid" in exc_str):
            return "token_expired"

        if "unauthorized" in exc_str or "authentication" in exc_str:
            return "invalid_credentials"

        # Data patterns
        if "profile" in exc_str and "not found" in exc_str:
            return "profile_not_found"

        if "manifest" in exc_str:
            return "manifest_error"

        return None

    def _generate_user_message(
        self, technical_message: str, category: ErrorCategory
    ) -> str:
        """Generate a user-friendly message based on error category."""
        category_messages = {
            ErrorCategory.NETWORK: "There was a problem connecting to the internet or Bungie servers.",
            ErrorCategory.AUTH: "There was a problem with your login. You may need to sign in again.",
            ErrorCategory.DATA: "There was a problem loading your Destiny 2 data.",
            ErrorCategory.UI: "There was a problem with the user interface.",
            ErrorCategory.SYSTEM: "There was a problem with your system or file permissions.",
            ErrorCategory.UNKNOWN: "An unexpected error occurred.",
        }

        return category_messages.get(
            category, "An error occurred: " + technical_message
        )

    def _generate_suggestions(self, category: ErrorCategory) -> List[str]:
        """Generate helpful suggestions based on error category."""
        category_suggestions = {
            ErrorCategory.NETWORK: [
                "Check your internet connection",
                "Try again in a few moments",
                "Check if Bungie servers are online",
            ],
            ErrorCategory.AUTH: [
                "Restart the application to log in again",
                "Check your Bungie account status",
            ],
            ErrorCategory.DATA: ["Try refreshing your data", "Restart the application"],
            ErrorCategory.UI: [
                "Try restarting the application",
                "Check if all windows are properly displayed",
            ],
            ErrorCategory.SYSTEM: [
                "Check file permissions",
                "Make sure you have enough disk space",
                "Try running as administrator (Windows)",
            ],
            ErrorCategory.UNKNOWN: [
                "Try restarting the application",
                "Check the log files for more details",
            ],
        }

        return category_suggestions.get(category, ["Try restarting the application"])

    def _is_recoverable(self, category: ErrorCategory, severity: ErrorSeverity) -> bool:
        """Determine if an error is recoverable."""
        if severity == ErrorSeverity.CRITICAL:
            return False

        recoverable_categories = [
            ErrorCategory.NETWORK,
            ErrorCategory.AUTH,
            ErrorCategory.DATA,
        ]

        return category in recoverable_categories

    def _handle_error(self, error_info: ErrorInfo):
        """Process and handle an error appropriately."""
        # Add to error history
        self.error_history.append(error_info)

        # Log the error
        with log_context(f"error_handler_{error_info.category.value}"):
            if error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
                logger_manager.error(
                    error_info.message,
                    extra={
                        "error_id": error_info.id,
                        "category": error_info.category.value,
                        "severity": error_info.severity.value,
                        "recoverable": error_info.recoverable,
                    },
                )
            else:
                logger_manager.warning(
                    error_info.message,
                    extra={
                        "error_id": error_info.id,
                        "category": error_info.category.value,
                        "severity": error_info.severity.value,
                    },
                )

        # Show user notification if appropriate
        if error_info.severity in [
            ErrorSeverity.MEDIUM,
            ErrorSeverity.HIGH,
            ErrorSeverity.CRITICAL,
        ]:
            self._show_user_notification(error_info)

        # Attempt recovery if possible
        if error_info.recoverable and error_info.recovery_action:
            try:
                error_info.recovery_action()
            except Exception as e:
                logger_manager.error(
                    f"Recovery action failed for {error_info.id}", exception=e
                )

    def _show_user_notification(self, error_info: ErrorInfo):
        """Show appropriate user notification for the error."""
        if not QT_AVAILABLE or not self.ui_parent:
            # Fallback to console output
            print(f"Error: {error_info.user_message}")
            if error_info.suggestions:
                print("Suggestions:")
                for suggestion in error_info.suggestions:
                    print(f"  - {suggestion}")
            return

        # Determine dialog type based on severity
        if error_info.severity == ErrorSeverity.CRITICAL:
            icon = QMessageBox.Critical
            title = "Critical Error"
        elif error_info.severity == ErrorSeverity.HIGH:
            icon = QMessageBox.Warning
            title = "Error"
        else:
            icon = QMessageBox.Information
            title = "Notice"

        # Create detailed message
        detailed_message = error_info.user_message
        if error_info.suggestions:
            detailed_message += "\n\nSuggestions:\n"
            detailed_message += "\n".join(
                f"• {suggestion}" for suggestion in error_info.suggestions
            )

        # Show message box
        msg_box = QMessageBox(self.ui_parent)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(error_info.user_message)
        msg_box.setDetailedText(
            f"Error ID: {error_info.id}\n\n{error_info.technical_details}"
        )

        if error_info.suggestions:
            suggestions_text = "\n".join(
                f"• {suggestion}" for suggestion in error_info.suggestions
            )
            msg_box.setInformativeText(f"Suggestions:\n{suggestions_text}")

        msg_box.exec_()

    def handle_exception(
        self,
        exception: Exception,
        context: Optional[List[str]] = None,
        user_message: Optional[str] = None,
        severity: Optional[ErrorSeverity] = None,
    ) -> ErrorInfo:
        """
        Handle an exception with proper classification and user notification.

        Args:
            exception: The exception to handle
            context: Context information for debugging
            user_message: Custom user-friendly message
            severity: Override severity classification

        Returns:
            ErrorInfo: Complete error information
        """
        # Classify the error
        category = self._classify_exception(exception)
        if severity is None:
            severity = self._classify_severity(exception, category)

        # Create error info
        error_info = self._create_error_info(
            exception=exception,
            category=category,
            severity=severity,
            context=context,
            user_message=user_message,
        )

        # Handle the error
        self._handle_error(error_info)

        return error_info

    def _classify_exception(self, exception: Exception) -> ErrorCategory:
        """Classify exception into appropriate category."""
        exc_type = type(exception).__name__
        exc_str = str(exception).lower()

        # Network-related exceptions
        if any(
            keyword in exc_type.lower()
            for keyword in [
                "timeout",
                "connection",
                "network",
                "http",
                "url",
                "request",
            ]
        ):
            return ErrorCategory.NETWORK

        # Authentication-related
        if any(
            keyword in exc_str
            for keyword in ["auth", "token", "unauthorized", "forbidden", "login"]
        ):
            return ErrorCategory.AUTH

        # Data-related
        if any(
            keyword in exc_str
            for keyword in ["json", "parse", "decode", "manifest", "profile", "data"]
        ):
            return ErrorCategory.DATA

        # UI-related
        if any(
            keyword in exc_type.lower()
            for keyword in ["qt", "widget", "gui", "ui", "window"]
        ):
            return ErrorCategory.UI

        # System-related
        if any(
            keyword in exc_type.lower()
            for keyword in ["file", "permission", "io", "os", "system"]
        ):
            return ErrorCategory.SYSTEM

        return ErrorCategory.UNKNOWN

    def _classify_severity(
        self, exception: Exception, category: ErrorCategory
    ) -> ErrorSeverity:
        """Classify exception severity based on type and category."""
        exc_type = type(exception).__name__

        # Critical errors that break the app
        critical_types = ["SystemExit", "KeyboardInterrupt", "MemoryError"]
        if exc_type in critical_types:
            return ErrorSeverity.CRITICAL

        # High severity errors by category
        if category == ErrorCategory.AUTH:
            return ErrorSeverity.HIGH

        if category == ErrorCategory.SYSTEM and "permission" in str(exception).lower():
            return ErrorSeverity.HIGH

        # Medium severity for most network and data errors
        if category in [ErrorCategory.NETWORK, ErrorCategory.DATA]:
            return ErrorSeverity.MEDIUM

        # Low severity for UI issues and unknown errors
        return ErrorSeverity.LOW

    def add_recovery_callback(self, category: ErrorCategory, callback: Callable):
        """Add a recovery callback for a specific error category."""
        if category not in self.recovery_callbacks:
            self.recovery_callbacks[category] = []
        self.recovery_callbacks[category].append(callback)

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for debugging and monitoring."""
        if not self.error_history:
            return {"total_errors": 0}

        by_category = {}
        by_severity = {}

        for error in self.error_history:
            category = error.category.value
            severity = error.severity.value

            by_category[category] = by_category.get(category, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1

        return {
            "total_errors": len(self.error_history),
            "by_category": by_category,
            "by_severity": by_severity,
            "recent_errors": [
                {
                    "id": error.id,
                    "message": error.message,
                    "category": error.category.value,
                    "severity": error.severity.value,
                    "timestamp": error.timestamp.isoformat(),
                }
                for error in self.error_history[-5:]  # Last 5 errors
            ],
        }


# Global error handler instance
error_handler = ErrorHandler()


def handle_exception(
    exception: Exception,
    context: Optional[List[str]] = None,
    user_message: Optional[str] = None,
    severity: Optional[ErrorSeverity] = None,
) -> ErrorInfo:
    """Convenience function to handle exceptions."""
    return error_handler.handle_exception(exception, context, user_message, severity)


def safe_execute(
    func: Callable,
    *args,
    context: Optional[List[str]] = None,
    user_message: Optional[str] = None,
    default_return: Any = None,
    **kwargs,
) -> Any:
    """
    Safely execute a function with automatic error handling.

    Args:
        func: Function to execute
        *args: Function arguments
        context: Context for error logging
        user_message: Custom user message for errors
        default_return: Return value if function fails
        **kwargs: Function keyword arguments

    Returns:
        Function result or default_return if function fails
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler.handle_exception(
            e, context=context or [func.__name__], user_message=user_message
        )
        return default_return
