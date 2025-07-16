# RaidAssist — Destiny 2 Progression Tracker and Overlay
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
logging_manager.py — Centralized logging system for RaidAssist.

Provides unified logging with proper formatting, rotation, and error tracking.
"""

import json
import logging
import logging.handlers
import os
import sys
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class LogLevel(Enum):
    """Log levels with proper severity ordering."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class RaidAssistLogger:
    """
    Centralized logging manager for RaidAssist.

    Features:
    - Automatic log rotation
    - Structured error tracking
    - Context-aware logging
    - Performance monitoring
    - User-friendly error messages
    """

    _instance: Optional["RaidAssistLogger"] = None
    _initialized = False

    def __new__(cls) -> "RaidAssistLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.log_dir = self._get_log_directory()
        self.error_count = 0
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.context_stack = []

        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Setup loggers
        self._setup_loggers()

        # Log session start
        self.info(
            "RaidAssist logging system initialized",
            extra={"session_id": self.session_id},
        )

    def _get_log_directory(self) -> str:
        """Get the appropriate log directory for the current platform."""
        if getattr(sys, "frozen", False):
            # PyInstaller executable - logs in same directory as executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Development mode - logs in project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        return os.path.join(base_dir, "logs")

    def _setup_loggers(self):
        """Setup all loggers with proper handlers and formatters."""
        # Create formatters
        detailed_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-4d | %(message)s"
        )

        simple_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        # Main application logger
        self.app_logger = logging.getLogger("raidassist")
        self.app_logger.setLevel(logging.DEBUG)

        # Clear any existing handlers
        self.app_logger.handlers.clear()

        # File handler with rotation
        log_file = os.path.join(self.log_dir, "raidassist.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)

        # Error file handler (errors only)
        error_file = os.path.join(self.log_dir, "errors.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_file, maxBytes=5 * 1024 * 1024, backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)

        # Console handler for development
        if not getattr(sys, "frozen", False):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(simple_formatter)
            self.app_logger.addHandler(console_handler)

        # Add handlers
        self.app_logger.addHandler(file_handler)
        self.app_logger.addHandler(error_handler)

        # Setup component-specific loggers
        self._setup_component_loggers(detailed_formatter)

    def _setup_component_loggers(self, formatter):
        """Setup loggers for specific components."""
        components = ["api", "ui", "auth", "overlay", "settings", "manifest"]

        for component in components:
            logger = logging.getLogger(f"raidassist.{component}")
            logger.setLevel(logging.DEBUG)

            # Component-specific log file
            log_file = os.path.join(self.log_dir, f"{component}.log")
            handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=5 * 1024 * 1024, backupCount=3
            )
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            # Don't propagate to avoid duplicate logs
            logger.propagate = False

    def get_logger(self, name: str = "raidassist") -> logging.Logger:
        """Get a logger instance for a specific component."""
        return logging.getLogger(name)

    def push_context(self, context: str):
        """Push a context onto the context stack for hierarchical logging."""
        self.context_stack.append(context)

    def pop_context(self):
        """Pop the most recent context from the stack."""
        if self.context_stack:
            self.context_stack.pop()

    def _format_message(self, message: str, extra: Optional[dict] = None) -> str:
        """Format message with context and extra data."""
        formatted = message

        if self.context_stack:
            context = " -> ".join(self.context_stack)
            formatted = f"[{context}] {formatted}"

        if extra:
            extra_str = " | ".join(f"{k}={v}" for k, v in extra.items())
            formatted = f"{formatted} | {extra_str}"

        return formatted

    def debug(
        self,
        message: str,
        extra: Optional[dict] = None,
        logger_name: str = "raidassist",
    ):
        """Log debug message."""
        logger = self.get_logger(logger_name)
        logger.debug(self._format_message(message, extra))

    def info(
        self,
        message: str,
        extra: Optional[dict] = None,
        logger_name: str = "raidassist",
    ):
        """Log info message."""
        logger = self.get_logger(logger_name)
        logger.info(self._format_message(message, extra))

    def warning(
        self,
        message: str,
        extra: Optional[dict] = None,
        logger_name: str = "raidassist",
    ):
        """Log warning message."""
        logger = self.get_logger(logger_name)
        logger.warning(self._format_message(message, extra))

    def error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        extra: Optional[dict] = None,
        logger_name: str = "raidassist",
    ):
        """Log error message with optional exception details."""
        self.error_count += 1
        logger = self.get_logger(logger_name)

        formatted_message = self._format_message(message, extra)

        if exception:
            # Add exception details
            exc_info = {
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                "traceback": traceback.format_exc(),
            }
            formatted_message += f" | Exception: {exc_info['exception_type']}: {exc_info['exception_message']}"
            logger.error(formatted_message, exc_info=True)

            # Save detailed error to separate file
            self._save_error_details(message, exception, extra)
        else:
            logger.error(formatted_message)

    def critical(
        self,
        message: str,
        exception: Optional[Exception] = None,
        extra: Optional[dict] = None,
        logger_name: str = "raidassist",
    ):
        """Log critical error message."""
        self.error_count += 1
        logger = self.get_logger(logger_name)

        formatted_message = self._format_message(message, extra)

        if exception:
            logger.critical(formatted_message, exc_info=True)
            self._save_error_details(message, exception, extra, critical=True)
        else:
            logger.critical(formatted_message)

    def _save_error_details(
        self,
        message: str,
        exception: Exception,
        extra: Optional[dict] = None,
        critical: bool = False,
    ):
        """Save detailed error information to JSON file for debugging."""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "level": "CRITICAL" if critical else "ERROR",
            "message": message,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc(),
            "context_stack": self.context_stack.copy(),
            "extra": extra or {},
        }

        error_file = os.path.join(self.log_dir, f"error_details_{self.session_id}.json")

        try:
            # Load existing errors or create new list
            if os.path.exists(error_file):
                with open(error_file, "r", encoding="utf-8") as f:
                    errors = json.load(f)
            else:
                errors = []

            errors.append(error_data)

            # Save updated errors
            with open(error_file, "w", encoding="utf-8") as f:
                json.dump(errors, f, indent=2, ensure_ascii=False)

        except Exception as e:
            # Fallback logging to prevent logging errors from breaking the app
            print(f"Failed to save error details: {e}")

    def log_performance(
        self, operation: str, duration: float, extra: Optional[dict] = None
    ):
        """Log performance metrics for operations."""
        perf_data = {"operation": operation, "duration_ms": f"{duration*1000:.2f}"}
        if extra:
            perf_data.update(extra)

        self.info(
            f"Performance: {operation} completed",
            extra=perf_data,
            logger_name="raidassist.performance",
        )

    def get_error_count(self) -> int:
        """Get the current error count for this session."""
        return self.error_count

    def get_session_id(self) -> str:
        """Get the current session ID."""
        return self.session_id

    def create_user_friendly_error(
        self,
        technical_message: str,
        user_message: str,
        suggestions: Optional[list] = None,
    ) -> dict:
        """
        Create a user-friendly error response.

        Args:
            technical_message: Technical error details for logging
            user_message: User-friendly error message
            suggestions: List of suggested actions for the user

        Returns:
            dict: Error response with user and technical details
        """
        error_id = f"ERR_{self.session_id}_{self.error_count + 1:04d}"

        return {
            "error_id": error_id,
            "user_message": user_message,
            "technical_message": technical_message,
            "suggestions": suggestions or [],
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
        }


# Global logger instance
logger_manager = RaidAssistLogger()


def get_logger(name: str = "raidassist") -> logging.Logger:
    """Convenience function to get a logger instance."""
    return logger_manager.get_logger(name)


def log_context(context: str):
    """Context manager for hierarchical logging."""

    class LogContext:
        def __init__(self, ctx: str):
            self.context = ctx

        def __enter__(self):
            logger_manager.push_context(self.context)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            logger_manager.pop_context()
            if exc_type is not None:
                logger_manager.error(
                    f"Exception in context '{self.context}'", exception=exc_val
                )

    return LogContext(context)


def handle_exception(func):
    """Decorator for automatic exception handling and logging."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger_manager.error(
                f"Unhandled exception in {func.__name__}",
                exception=e,
                extra={"args": str(args), "kwargs": str(kwargs)},
            )
            raise

    return wrapper
