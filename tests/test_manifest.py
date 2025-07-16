# tests/test_manifest.py

import json
import os
import shutil

import pytest  # type: ignore

from api import manifest


def test_project_root_path_is_correct():
    root = manifest.get_project_root()
    assert os.path.isdir(root), f"Project root does not exist: {root}"


def test_manifest_cache_path():
    # The manifest should be cached in the correct absolute path
    dest_dir = manifest.DEST_DIR
    manifest_file = manifest.MANIFEST_FILE
    assert dest_dir.endswith(os.path.join("RaidAssist", "cache", "manifest"))
    assert manifest_file.endswith("DestinyInventoryItemDefinition.json")


def test_manifest_download_and_load(tmp_path):
    """
    This test will:
    - Remove the manifest cache if it exists (to test cold fetch)
    - Run fetch_manifest() to download a fresh manifest (requires API key and internet)
    - Load the manifest and check its structure
    """
    manifest_file = manifest.MANIFEST_FILE

    # Remove manifest file if exists (simulate "cold cache")
    if os.path.exists(manifest_file):
        os.remove(manifest_file)

    # Download and cache manifest
    manifest.fetch_manifest()
    assert os.path.exists(manifest_file), "Manifest file was not created."

    # Load manifest and check keys
    item_defs = manifest.load_item_definitions()
    assert isinstance(item_defs, dict), "Loaded manifest should be a dictionary"
    assert len(item_defs) > 1000, "Manifest seems suspiciously small"
    first_key = next(iter(item_defs))
    item = item_defs[first_key]
    assert "displayProperties" in item, "displayProperties missing from an item"


def test_get_item_display():
    item_defs = manifest.load_item_definitions()

    # If manifest is empty, skip this test
    if not item_defs:
        pytest.skip("Manifest is empty, cannot test item display")

    # Test with any available item from the manifest
    first_hash = next(iter(item_defs))
    name = manifest.get_item_display(first_hash, item_defs)
    assert isinstance(name, str)

    # Should not be empty and should not be "Unknown Item" since we're using a valid hash
    assert len(name) > 0
    assert not name.startswith("Unknown Item")

    # Test with an invalid hash that definitely won't exist
    invalid_hash = "99999999999"
    unknown_name = manifest.get_item_display(invalid_hash, item_defs)
    assert "Unknown Item" in unknown_name


@pytest.mark.skipif(
    not os.path.exists(manifest.MANIFEST_FILE), reason="Manifest not yet downloaded"
)
def test_load_item_definitions_returns_dict():
    d = manifest.load_item_definitions()
    assert isinstance(d, dict)
    assert len(d) > 0
