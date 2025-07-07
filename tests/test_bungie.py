import os
import json
import pytest # type: ignore

from api import bungie


def test_load_token(tmp_path, monkeypatch):
    # Patch SESSION_PATH to temp
    session_path = tmp_path / "session.json"
    monkeypatch.setattr(bungie, "SESSION_PATH", str(session_path))
    # Write token
    with open(session_path, "w") as f:
        json.dump({"access_token": "xyz789"}, f)
    assert bungie.load_token() == "xyz789"


def test_load_token_missing(monkeypatch):
    # Patch SESSION_PATH to non-existent
    monkeypatch.setattr(bungie, "SESSION_PATH", "/non/existent/file.json")
    assert bungie.load_token() is None


def test_fetch_profile_mock(monkeypatch, tmp_path):
    # Patch out load_token and requests.get
    monkeypatch.setattr(bungie, "load_token", lambda: "fake_token")
    monkeypatch.setattr(bungie, "API_KEY", "test_key")
    monkeypatch.setattr(bungie, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(bungie, "PROFILE_CACHE_PATH", str(tmp_path / "profile.json"))

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"profile": "ok"}

    monkeypatch.setattr("requests.get", lambda *a, **kw: FakeResp())

    # Should write the cache and return the dict
    out = bungie.fetch_profile(3, "12345")
    assert out == {"profile": "ok"}
    # Cache file written
    assert os.path.exists(tmp_path / "profile.json")
    # Content check
    with open(tmp_path / "profile.json") as f:
        assert json.load(f) == {"profile": "ok"}


def test_fetch_profile_no_token(monkeypatch):
    monkeypatch.setattr(bungie, "load_token", lambda: None)
    assert bungie.fetch_profile(3, "12345") is None
