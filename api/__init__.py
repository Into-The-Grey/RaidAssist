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
from .bungie import (
    ensure_authenticated,
    fetch_profile,
    load_cached_profile,
    test_api_connection,
)
from .manifest import get_item_info  # This function exists, get_item_name doesn't
from .manifest import load_item_definitions

# OAuth functionality (functions, not a class)
try:
    from .oauth import authorize, get_access_token

    OAUTH_FUNCTIONS_AVAILABLE = True
except ImportError:
    OAUTH_FUNCTIONS_AVAILABLE = False

from .parse_profile import (
    extract_catalysts,
    extract_exotics,
    extract_red_borders,
    load_profile,
)

# Exotics module (available functions)
try:
    from .exotics import is_exotic, all_exotics, build_exotic_cache, load_exotic_cache

    EXOTICS_FUNCTIONS_AVAILABLE = True
except ImportError:
    EXOTICS_FUNCTIONS_AVAILABLE = False

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
if OAUTH_FUNCTIONS_AVAILABLE:
    __all__.extend(["authorize", "get_access_token"])

if EXOTICS_FUNCTIONS_AVAILABLE:
    __all__.extend(
        ["is_exotic", "all_exotics", "build_exotic_cache", "load_exotic_cache"]
    )


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
