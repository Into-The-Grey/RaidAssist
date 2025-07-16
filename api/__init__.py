# RaidAssist — API Module
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>

"""
RaidAssist API Module - Bungie API integration with enhanced error handling.

This module provides all the API functionality for interacting with the Bungie API:
- bungie: Core API communication with rate limiting and retry logic
- manifest: Item definition loading and management
- oauth: Enhanced OAuth authentication flow
- parse_profile: Profile data extraction and processing
- exotics: Exotic item collection tracking
"""

__version__ = "2.0.0"
__author__ = "Nicholas Acord"

# Core API components
from .bungie import (ensure_authenticated, fetch_profile, load_cached_profile,
                     test_api_connection)
from .manifest import \
    get_item_info  # This function exists, get_item_name doesn't
from .manifest import load_item_definitions

# OAuth functionality (may not be a class)
try:
    from .oauth import OAuth

    OAUTH_CLASS_AVAILABLE = True
except ImportError:
    OAUTH_CLASS_AVAILABLE = False

from .parse_profile import (extract_catalysts, extract_exotics,
                            extract_red_borders, load_profile)

# Exotics module (may not have collect_exotics function)
try:
    from .exotics import collect_exotics

    COLLECT_EXOTICS_AVAILABLE = True
except ImportError:
    COLLECT_EXOTICS_AVAILABLE = False

__all__ = [
    # Authentication
    "ensure_authenticated",
    # Profile data
    "fetch_profile",
    "load_cached_profile",
    "load_profile",
    # Data extraction
    "extract_red_borders",
    "extract_catalysts",
    "extract_exotics",
    # Manifest and items
    "load_item_definitions",
    "get_item_info",
    # Utilities
    "test_api_connection",
]

# Add optional components if available
if OAUTH_CLASS_AVAILABLE:
    __all__.append("OAuth")

if COLLECT_EXOTICS_AVAILABLE:
    __all__.append("collect_exotics")


# API health check
def get_api_status():
    """Get API module status and health check."""
    try:
        connection_ok = test_api_connection()
        auth_ok = ensure_authenticated()

        return {
            "version": __version__,
            "connection": connection_ok,
            "authenticated": auth_ok,
            "modules": __all__,
        }
    except Exception as e:
        return {
            "version": __version__,
            "connection": False,
            "authenticated": False,
            "error": str(e),
            "modules": __all__,
        }
