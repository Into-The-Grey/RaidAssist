import json
import os

import pytest  # type: ignore

from api.parse_profile import (extract_catalysts, extract_exotics,
                               extract_red_borders, load_profile)


def test_parse_profile_load_and_extract(tmp_path, monkeypatch):
    import api.parse_profile as parse_mod

    # Patch PROFILE_PATH to a temp file
    orig_path = parse_mod.PROFILE_PATH
    test_path = tmp_path / "profile.json"
    parse_mod.PROFILE_PATH = str(test_path)

    # Minimal fake profile data (structure mimics Bungie API)
    fake = {
        "Response": {
            "itemComponents": {
                "instances": {"1001": {}, "1002": {}},
                "objectives": {
                    "1001": {"objectives": [{"completionValue": 5, "progress": 3}]},
                    "1002": {"objectives": [{"completionValue": 2, "progress": 2}]},
                },
            },
            "profileInventory": {
                "data": {
                    "items": [
                        {"itemHash": 999999, "foo": "bar"},
                        # Add a known exotic hash if you want to fully check extract_exotics.
                    ]
                }
            },
        }
    }

    with open(test_path, "w") as f:
        json.dump(fake, f)

    profile = load_profile()
    assert profile == fake

    reds = extract_red_borders(fake)
    assert isinstance(reds, list)
    # Should have at least one "pattern" due to completionValue > 1
    assert any(r.get("progress", 0) for r in reds)

    # Catalysts: Should be list, possibly non-empty due to similar logic
    cats = extract_catalysts(fake)
    assert isinstance(cats, list)

    # Exotics: will be empty unless your all_exotics() returns 999999 as an exotic
    exos = extract_exotics(fake)
    assert isinstance(exos, list)

    # Restore
    parse_mod.PROFILE_PATH = orig_path
