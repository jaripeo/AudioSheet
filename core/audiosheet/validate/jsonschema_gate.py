"""JSON Schema validation gate — ARCHITECTURE.md Section 3.7.

``packages/schema/schema/score-document.schema.json`` is the only validator used
at the S6 gate. It is generated from the TypeScript source of truth by
``scripts/gen_schema.py`` and MUST NOT be hand-edited.

``additionalProperties`` is ``false`` at every level: an unexpected key means a
version mismatch and MUST fail.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from audiosheet.config.paths import repo_root
from audiosheet.pipeline.errors import AudioSheetError, ErrorCode, SchemaValidationError
from audiosheet.schema import ScoreDocument

#: Maximum number of schema errors reported before the list is truncated.
MAX_REPORTED_ERRORS = 20


def schema_path() -> Path:
    """Return the path of the generated score-document JSON Schema."""
    return repo_root() / "packages" / "schema" / "schema" / "score-document.schema.json"


@lru_cache(maxsize=1)
def load_schema() -> dict[str, Any]:
    """Load and cache the JSON Schema document.

    Returns:
        The parsed schema.

    Raises:
        AudioSheetError: ``E_SCHEMA_INVALID`` when the schema file is absent.
    """
    path = schema_path()
    if not path.is_file():
        raise AudioSheetError(
            ErrorCode.E_SCHEMA_INVALID,
            f"generated JSON Schema not found at {path}; run `make schema`",
        )
    parsed: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return parsed


@lru_cache(maxsize=1)
def validator() -> Draft202012Validator:
    """Return a cached draft 2020-12 validator for the score document."""
    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_payload(payload: Any) -> None:
    """Validate a raw JSON payload against the generated schema.

    Args:
        payload: The decoded JSON document.

    Raises:
        SchemaValidationError: When the payload does not satisfy the schema. The
            error detail lists every failure, deepest path first, truncated to
            ``MAX_REPORTED_ERRORS``.
    """
    errors = sorted(validator().iter_errors(payload), key=lambda e: list(e.absolute_path))
    if not errors:
        return
    reported = [
        {
            "path": "/".join(str(part) for part in error.absolute_path) or "<root>",
            "message": error.message,
            "validator": str(error.validator),
        }
        for error in errors[:MAX_REPORTED_ERRORS]
    ]
    raise SchemaValidationError(
        f"document failed schema validation with {len(errors)} error(s)",
        detail={"errors": reported, "total": len(errors)},
    )


def parse_document(payload: Any) -> ScoreDocument:
    """Validate a payload and build the typed model.

    The JSON Schema runs first so that a malformed document produces a precise,
    path-anchored diagnostic rather than a Pydantic error tree.

    Args:
        payload: The decoded JSON document.

    Returns:
        The validated ``ScoreDocument``.

    Raises:
        SchemaValidationError: When the payload fails the schema or the model.
    """
    validate_payload(payload)
    try:
        return ScoreDocument.model_validate(payload)
    except Exception as exc:  # pragma: no cover - schema gate catches these first
        raise SchemaValidationError(
            "document passed JSON Schema but failed the Pydantic model; "
            "this indicates schema/model drift — run `make schema`",
            detail={"error": str(exc)},
        ) from exc


def load_document(path: Path) -> ScoreDocument:
    """Read, validate and parse a score document from disk.

    Args:
        path: Path to a JSON score document.

    Returns:
        The validated ``ScoreDocument``.

    Raises:
        SchemaValidationError: When the file is not valid JSON or fails the gate.
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(
            f"{path} is not valid JSON: {exc}", detail={"path": str(path)}
        ) from exc
    return parse_document(payload)
