"""Shared test fixtures."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from audiosheet.pipeline.cache import StageCache
from audiosheet.schema import ScoreDocument
from audiosheet.validate.jsonschema_gate import parse_document

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"
SIMPLE_SCALE = FIXTURES / "handmade" / "simple_scale.json"

#: Raw note ids the hand-authored fixture claims as provenance.
SIMPLE_SCALE_RAW_IDS = frozenset(f"raw-{i:04d}" for i in range(1, 9))


@pytest.fixture
def repo_root() -> Path:
    """Return the repository root."""
    return REPO_ROOT


@pytest.fixture
def simple_scale_path() -> Path:
    """Return the path of the hand-authored fixture."""
    return SIMPLE_SCALE


@pytest.fixture
def simple_scale_payload() -> dict[str, Any]:
    """Return the hand-authored fixture as a mutable raw payload."""
    payload: dict[str, Any] = json.loads(SIMPLE_SCALE.read_text(encoding="utf-8"))
    return payload


@pytest.fixture
def mutate_payload(simple_scale_payload: dict[str, Any]) -> Any:
    """Return a helper that deep-copies the fixture and applies a mutation."""

    def _mutate(fn: Any) -> ScoreDocument:
        payload = copy.deepcopy(simple_scale_payload)
        fn(payload)
        return parse_document(payload)

    return _mutate


@pytest.fixture
def simple_scale() -> ScoreDocument:
    """Return the hand-authored fixture as a validated model."""
    return parse_document(json.loads(SIMPLE_SCALE.read_text(encoding="utf-8")))


@pytest.fixture
def raw_ids() -> set[str]:
    """Return the raw note ids for the strict form of V-5."""
    return set(SIMPLE_SCALE_RAW_IDS)


@pytest.fixture
def cache(tmp_path: Path) -> StageCache:
    """Return a cache rooted in a throwaway directory."""
    return StageCache(tmp_path / ".audiosheet")
