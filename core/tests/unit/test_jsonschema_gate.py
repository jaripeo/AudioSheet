"""The S6 schema gate: what it accepts, and what it must reject."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from audiosheet.pipeline.errors import AudioSheetError, ErrorCode, SchemaValidationError
from audiosheet.validate.jsonschema_gate import (
    load_document,
    parse_document,
    validate_payload,
)


def test_accepts_the_handmade_fixture(simple_scale_payload: dict[str, Any]) -> None:
    validate_payload(simple_scale_payload)


def test_parse_returns_a_typed_document(simple_scale_payload: dict[str, Any]) -> None:
    document = parse_document(simple_scale_payload)
    assert document.schema_version == "1.0.0"
    assert document.timing.ppq == 960
    assert document.difficulty.level == "complex"


def test_rejects_an_unknown_key(simple_scale_payload: dict[str, Any]) -> None:
    """Section 3.7: an unexpected key means a version mismatch and MUST fail."""
    simple_scale_payload["parts"][0]["notes"][0]["surprise"] = 1
    with pytest.raises(SchemaValidationError) as excinfo:
        validate_payload(simple_scale_payload)
    assert excinfo.value.code is ErrorCode.E_SCHEMA_INVALID


def test_rejects_a_missing_key(simple_scale_payload: dict[str, Any]) -> None:
    del simple_scale_payload["parts"][0]["notes"][0]["salience"]
    with pytest.raises(SchemaValidationError):
        validate_payload(simple_scale_payload)


def test_rejects_an_out_of_range_value(simple_scale_payload: dict[str, Any]) -> None:
    simple_scale_payload["parts"][0]["notes"][0]["midi"] = 200
    with pytest.raises(SchemaValidationError):
        validate_payload(simple_scale_payload)


def test_rejects_a_non_integral_tick(simple_scale_payload: dict[str, Any]) -> None:
    """Ticks are integers; 480.5 is not a tick."""
    simple_scale_payload["parts"][0]["notes"][0]["tick_on"] = 480.5
    with pytest.raises(SchemaValidationError):
        validate_payload(simple_scale_payload)


def test_rejects_an_unknown_enum_member(simple_scale_payload: dict[str, Any]) -> None:
    simple_scale_payload["parts"][0]["notes"][0]["notated_type"] = "crotchet"
    with pytest.raises(SchemaValidationError):
        validate_payload(simple_scale_payload)


def test_rejects_a_wrong_schema_version(simple_scale_payload: dict[str, Any]) -> None:
    simple_scale_payload["schema_version"] = "2.0.0"
    with pytest.raises(SchemaValidationError):
        validate_payload(simple_scale_payload)


def test_error_detail_names_the_offending_path(simple_scale_payload: dict[str, Any]) -> None:
    simple_scale_payload["parts"][0]["notes"][0]["midi"] = -1
    with pytest.raises(SchemaValidationError) as excinfo:
        validate_payload(simple_scale_payload)
    errors = excinfo.value.detail["errors"]
    assert isinstance(errors, list)
    assert errors[0]["path"] == "parts/0/notes/0/midi"


def test_load_document_reports_bad_json(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(SchemaValidationError):
        load_document(path)


def test_load_document_round_trip(tmp_path: Path, simple_scale_payload: dict[str, Any]) -> None:
    path = tmp_path / "doc.json"
    path.write_text(json.dumps(simple_scale_payload), encoding="utf-8")
    assert load_document(path).id == simple_scale_payload["id"]


def test_missing_schema_file_is_a_typed_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """INV-1: a missing generated artefact fails closed with a clear code."""
    from audiosheet.validate import jsonschema_gate

    jsonschema_gate.load_schema.cache_clear()
    jsonschema_gate.validator.cache_clear()
    monkeypatch.setattr(jsonschema_gate, "schema_path", lambda: Path("/nonexistent.json"))
    try:
        with pytest.raises(AudioSheetError) as excinfo:
            jsonschema_gate.load_schema()
        assert excinfo.value.code is ErrorCode.E_SCHEMA_INVALID
    finally:
        jsonschema_gate.load_schema.cache_clear()
        jsonschema_gate.validator.cache_clear()
