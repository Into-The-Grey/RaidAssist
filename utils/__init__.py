# RaidAssist — Utils Module
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>

"""
RaidAssist Utils Module - Enhanced utility systems.

This module provides the enhanced utility systems that make RaidAssist robust:
- logging_manager: Centralized logging with rotation and context tracking
- error_handler: Comprehensive error handling with user-friendly messages
"""

__version__ = "2.0.0"
__author__ = "Nicholas Acord"

# Enhanced utility imports
try:
    from .logging_manager import (
        get_logger,
        log_context,
        logger_manager,
        RaidAssistLogger,
    )

    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

try:
    from .error_handler import (
        safe_execute,
        handle_exception,
        error_handler,
        ErrorHandler,
        ErrorSeverity,
    )

    ERROR_HANDLING_AVAILABLE = True
except ImportError:
    ERROR_HANDLING_AVAILABLE = False

__all__ = []

# Add components if available
if LOGGING_AVAILABLE:
    __all__.extend(["get_logger", "log_context", "logger_manager", "RaidAssistLogger"])

if ERROR_HANDLING_AVAILABLE:
    __all__.extend(
        [
            "safe_execute",
            "handle_exception",
            "error_handler",
            "ErrorHandler",
            "ErrorSeverity",
        ]
    )


def get_utils_status():
    """Get utils module status and availability."""
    return {
        "version": __version__,
        "logging_available": LOGGING_AVAILABLE,
        "error_handling_available": ERROR_HANDLING_AVAILABLE,
        "components": __all__,
        "enhancement_level": (
            "Full" if (LOGGING_AVAILABLE and ERROR_HANDLING_AVAILABLE) else "Partial"
        ),
    }


# Convenience function for initialization
def initialize_enhanced_systems():
    """Initialize enhanced logging and error handling systems."""
    if LOGGING_AVAILABLE:
        # Logging initializes automatically via singleton
        logger = get_logger("raidassist.utils")
        logger.info("Enhanced utils module initialized")

        if ERROR_HANDLING_AVAILABLE:
            logger.info("Full enhancement suite available")
            return True
        else:
            logger.warning("Error handling not available")
            return False
    else:
        print("Enhanced logging not available")
        return False
