"""The content-addressed stage cache and its canonical serialisation."""

from __future__ import annotations

import json
from typing import Any

import pytest

from audiosheet.pipeline.cache import (
    FINGERPRINT_PREFIX,
    StageCache,
    blake3_hex,
    canonical_json,
    hash_json,
)
from audiosheet.pipeline.errors import AudioSheetError, ErrorCode


def test_canonical_json_sorts_keys_and_terminates_with_a_newline() -> None:
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}\n'


def test_canonical_json_is_order_independent() -> None:
    assert canonical_json({"a": 1, "b": 2}) == canonical_json({"b": 2, "a": 1})


def test_canonical_json_preserves_non_ascii() -> None:
    assert "é" in canonical_json({"k": "é"})


def test_fingerprints_are_prefixed_and_stable() -> None:
    first = blake3_hex(b"abc")
    assert first.startswith(FINGERPRINT_PREFIX)
    assert first == blake3_hex(b"abc")


def test_fingerprint_parts_are_length_prefixed() -> None:
    """Splitting the same bytes differently must not collide."""
    assert blake3_hex(b"ab", b"c") != blake3_hex(b"a", b"bc")


def test_hash_json_ignores_key_order() -> None:
    assert hash_json({"a": 1, "b": 2}) == hash_json({"b": 2, "a": 1})


def test_put_then_get_round_trips(cache: StageCache) -> None:
    fingerprint = hash_json({"x": 1})
    cache.put("S_test", fingerprint, {"value": [1, 2, 3]})
    assert cache.has("S_test", fingerprint)
    assert cache.get("S_test", fingerprint) == {"value": [1, 2, 3]}


def test_get_returns_none_on_a_miss(cache: StageCache) -> None:
    assert cache.get("S_test", "b3:absent") is None


def test_entries_are_written_in_canonical_form(cache: StageCache) -> None:
    """INV-2: two runs must produce byte-identical cache contents."""
    path = cache.put("S_test", "b3:deadbeef", {"b": 1, "a": 2})
    assert path.read_text(encoding="utf-8") == canonical_json({"a": 2, "b": 1})


def test_no_temp_files_are_left_behind(cache: StageCache) -> None:
    cache.put("S_test", "b3:deadbeef", {"a": 1})
    assert list(cache.root.rglob("*.tmp")) == []


def test_corrupt_entry_raises_a_typed_error(cache: StageCache) -> None:
    path = cache.json_path("S_test", "b3:corrupt")
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(AudioSheetError) as excinfo:
        cache.get("S_test", "b3:corrupt")
    assert excinfo.value.code is ErrorCode.E_CACHE_CORRUPT


def test_blob_paths_accept_an_extension_with_or_without_a_dot(cache: StageCache) -> None:
    with_dot = cache.blob_path("S_test", "b3:abc", ".flac")
    without = cache.blob_path("S_test", "b3:abc", "flac")
    assert with_dot == without
    assert with_dot.suffix == ".flac"


def test_fingerprints_are_filename_safe(cache: StageCache) -> None:
    path = cache.json_path("S_test", "b3:ab/cd")
    assert ":" not in path.name
    assert "/" not in path.name


def test_clear_removes_entries_and_counts_them(cache: StageCache) -> None:
    cache.put("S_a", "b3:1", {"v": 1})
    cache.put("S_b", "b3:2", {"v": 2})
    assert cache.clear() == 2
    assert cache.get("S_a", "b3:1") is None


def test_clear_can_target_one_stage(cache: StageCache) -> None:
    cache.put("S_a", "b3:1", {"v": 1})
    cache.put("S_b", "b3:2", {"v": 2})
    assert cache.clear("S_a") == 1
    assert cache.get("S_b", "b3:2") == {"v": 2}


def test_cached_document_survives_a_json_round_trip(
    cache: StageCache, simple_scale_payload: dict[str, Any]
) -> None:
    cache.put("S6", "b3:doc", simple_scale_payload)
    reloaded = cache.get("S6", "b3:doc")
    assert json.dumps(reloaded, sort_keys=True) == json.dumps(simple_scale_payload, sort_keys=True)
