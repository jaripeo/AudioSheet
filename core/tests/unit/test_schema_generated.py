"""Gate G0: the generated schema artefacts are in sync and round-trip cleanly."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from audiosheet.pipeline.cache import canonical_json
from audiosheet.schema import ScoreDocument
from audiosheet.validate.jsonschema_gate import load_schema, schema_path


@pytest.mark.gate
def test_generated_artefacts_are_not_stale(repo_root: Path) -> None:
    """`gen_schema.py --check` must pass, or the generated files have drifted."""
    result = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "gen_schema.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"schema drift:\n{result.stdout}\n{result.stderr}"


def test_schema_file_exists_and_is_draft_2020_12() -> None:
    """The S6 gate validator is present and declares the expected dialect."""
    schema = load_schema()
    assert schema_path().is_file()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$ref"] == "#/$defs/ScoreDocument"


def test_every_object_forbids_unknown_keys() -> None:
    """Section 3.7: additionalProperties is false at every level."""
    schema = load_schema()
    offenders = [
        name
        for name, fragment in schema["$defs"].items()
        if fragment.get("type") == "object" and fragment.get("additionalProperties") is not False
    ]
    assert offenders == []


def test_every_object_property_is_required() -> None:
    """Optional fields use null, never omission, so every property is required."""
    schema = load_schema()
    offenders = {
        name: sorted(set(fragment["properties"]) - set(fragment["required"]))
        for name, fragment in schema["$defs"].items()
        if fragment.get("type") == "object"
        and set(fragment["properties"]) != set(fragment["required"])
    }
    assert offenders == {}


@pytest.mark.gate
def test_fixture_round_trips_byte_identically(
    simple_scale_path: Path, simple_scale_payload: dict[str, Any]
) -> None:
    """Gate G0: JSON -> Pydantic -> JSON is byte-identical in canonical form."""
    document = ScoreDocument.model_validate(simple_scale_payload)
    dumped = document.model_dump(mode="json")

    assert canonical_json(dumped) == canonical_json(simple_scale_payload)

    # And a second pass through the model changes nothing further.
    again = ScoreDocument.model_validate(dumped).model_dump(mode="json")
    assert canonical_json(again) == canonical_json(dumped)

    # The file on disk is itself in the stable pretty form, so regenerating or
    # re-saving it produces no diff noise.
    text = simple_scale_path.read_text(encoding="utf-8")
    assert text == json.dumps(simple_scale_payload, indent=2, ensure_ascii=False) + "\n"


def test_model_field_order_matches_schema_required_order() -> None:
    """The Pydantic models and the JSON Schema list the same fields."""
    schema = load_schema()
    assert list(ScoreDocument.model_fields) == schema["$defs"]["ScoreDocument"]["required"]
