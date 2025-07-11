# RaidAssist Enhanced - Test Configuration and Fixtures
# Copyright (C) 2025 Nicholas Acord <ncacord@protonmail.com>

"""
Enhanced conftest.py for RaidAssist test suite.
Provides shared fixtures and configuration for all tests.
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root path."""
    return project_root


@pytest.fixture
def temp_logs_dir(tmp_path):
    """Create a temporary logs directory for testing."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    return logs_dir


@pytest.fixture
def mock_enhanced_logging():
    """Mock enhanced logging system for tests that don't need real logging."""
    with patch("utils.logging_manager.get_logger") as mock_logger:
        mock_logger.return_value = Mock()
        yield mock_logger


@pytest.fixture
def mock_enhanced_error_handler():
    """Mock enhanced error handling for tests."""
    with patch("utils.error_handler.safe_execute") as mock_safe_execute:
        mock_safe_execute.side_effect = lambda func, *args, **kwargs: func(
            *args, **kwargs
        )
        yield mock_safe_execute


@pytest.fixture
def mock_api_key():
    """Provide a mock API key for testing."""
    return "test_api_key_12345"


@pytest.fixture
def mock_session_data():
    """Provide mock session data for OAuth testing."""
    return {
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "expires_at": 9999999999,  # Far future
        "membership_id": "12345",
        "membership_type": 3,
    }


@pytest.fixture
def mock_profile_data():
    """Provide mock profile data for testing."""
    return {
        "Response": {
            "profile": {
                "data": {
                    "userInfo": {
                        "membershipType": 3,
                        "membershipId": "12345",
                        "displayName": "TestUser",
                    }
                }
            },
            "characterInventories": {"data": {}},
            "characterEquipment": {"data": {}},
            "itemComponents": {"objectives": {"data": {}}},
        }
    }


@pytest.fixture
def mock_manifest_data():
    """Provide mock manifest data for testing."""
    return {
        "12345": {
            "displayProperties": {
                "name": "Test Weapon",
                "description": "A test weapon for unit testing",
                "icon": "/test/icon.jpg",
            },
            "itemTypeDisplayName": "Auto Rifle",
            "itemSubType": 6,
        }
    }


@pytest.fixture
def disable_qt():
    """Disable Qt imports for tests that don't need GUI."""
    with patch.dict(
        "sys.modules",
        {
            "PySide2": Mock(),
            "PySide2.QtWidgets": Mock(),
            "PySide2.QtCore": Mock(),
            "PySide2.QtGui": Mock(),
        },
    ):
        yield


@pytest.fixture
def mock_requests_get():
    """Mock requests.get for API testing."""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Response": {"test": "data"}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_requests_post():
    """Mock requests.post for OAuth testing."""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_token",
            "refresh_token": "new_refresh",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically clean up test files after each test."""
    yield
    # Cleanup logic can be added here if needed


# Test markers for different test categories
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "api: Tests requiring API access")
    config.addinivalue_line("markers", "gui: Tests requiring GUI components")
    config.addinivalue_line("markers", "enhanced: Tests for enhanced features")
    config.addinivalue_line("markers", "slow: Slow running tests")


# Skip GUI tests if PySide2 not available
def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip GUI tests if PySide2 unavailable."""
    try:
        import PySide2

        pyside_available = True
    except ImportError:
        pyside_available = False

    if not pyside_available:
        skip_gui = pytest.mark.skip(reason="PySide2 not available")
        for item in items:
            if "gui" in item.keywords:
                item.add_marker(skip_gui)
