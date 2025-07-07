import os
import pytest # type: ignore

from ui.settings import load_settings, save_settings


def test_settings_save_and_load(tmp_path):
    # Isolate test: patch the SETTINGS_PATH for this test only
    import ui.settings as settings_mod
    orig_path = settings_mod.SETTINGS_PATH
    test_path = tmp_path / "settings.json"
    settings_mod.SETTINGS_PATH = str(test_path)

    # Save settings
    test_data = {"k": "v", "n": 123}
    assert save_settings(test_data) is True
    assert os.path.exists(test_path)

    # Load settings
    loaded = load_settings()
    assert loaded == test_data

    # Restore
    settings_mod.SETTINGS_PATH = orig_path
