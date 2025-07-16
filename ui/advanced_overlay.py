"""Backwards compatibility module for advanced overlay.

This module re-exports all public objects from :mod:`ui.overlay` so that
existing imports using ``ui.advanced_overlay`` continue to work.
"""

from .overlay import *  # noqa: F401,F403
