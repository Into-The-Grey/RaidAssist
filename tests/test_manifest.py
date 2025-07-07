# tests/test_manifest.py

import os
import shutil
import pytest # type: ignore
import json

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
    # Pick a known weapon hash for testing (e.g., Ace of Spades: 1256108509)
    ace_hash = 1256108509
    name = manifest.get_item_display(ace_hash, item_defs)
    assert isinstance(name, str)
    # The result should not be an 'Unknown Item' unless manifest is missing
    if len(item_defs) > 0:
        assert "Ace of Spades" in name or "Unknown Item" not in name


@pytest.mark.skipif(
    not os.path.exists(manifest.MANIFEST_FILE), reason="Manifest not yet downloaded"
)
def test_load_item_definitions_returns_dict():
    d = manifest.load_item_definitions()
    assert isinstance(d, dict)
    assert len(d) > 0
