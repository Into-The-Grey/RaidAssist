import json
import os

import pytest  # type: ignore

from api.exotics import (all_exotics, build_exotic_cache, is_exotic,
                         load_exotic_cache)


def test_exotics_cache_roundtrip(tmp_path, monkeypatch):
    import api.exotics as exotics_mod

    # Patch get_cache_path to use a temp location for this test only
    def temp_cache_path():
        return str(tmp_path / "exotics_cache.json")

    monkeypatch.setattr(exotics_mod, "get_cache_path", temp_cache_path)

    # Build and load cache
    exotics = build_exotic_cache()
    assert isinstance(exotics, dict)
    loaded = load_exotic_cache()
    assert exotics == loaded

    # all_exotics returns same
    assert all_exotics() == loaded

    # Pick any hash and test is_exotic
    if loaded:
        some_hash = next(iter(loaded))
        assert is_exotic(some_hash) is True
        assert is_exotic(int(some_hash)) is True

    # Negative test (should not crash, may return False)
    assert is_exotic(99999999) is False
