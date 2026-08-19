"""The error/warning registry — ARCHITECTURE.md Appendix 5.4."""

from __future__ import annotations

import re
from pathlib import Path

from audiosheet.pipeline.errors import (
    AudioSheetError,
    ErrorCode,
    InvariantViolationError,
    SchemaValidationError,
    StageCancelledError,
    WarningCode,
)

ARCHITECTURE = Path(__file__).resolve().parents[3] / "ARCHITECTURE.md"


def test_error_codes_are_their_own_values() -> None:
    for code in ErrorCode:
        assert code.value == code.name


def test_warning_codes_are_their_own_values() -> None:
    for code in WarningCode:
        assert code.value == code.name


def test_codes_carry_the_expected_prefix() -> None:
    assert all(code.value.startswith("E_") for code in ErrorCode)
    assert all(code.value.startswith("W_") for code in WarningCode)


def test_every_appendix_code_exists_in_the_registry() -> None:
    """The registry may extend the appendix, but must never omit one of its codes."""
    text = ARCHITECTURE.read_text(encoding="utf-8")
    documented = set(re.findall(r"\b([EW]_[A-Z_]+)\b", text))
    known = {code.value for code in ErrorCode} | {code.value for code in WarningCode}
    assert documented - known == set()


def test_error_wire_form() -> None:
    error = AudioSheetError(
        ErrorCode.E_INGEST_LIMIT, "file too large", detail={"limit": 120}, tick=None
    )
    assert error.as_dict() == {
        "code": "E_INGEST_LIMIT",
        "message": "file too large",
        "detail": {"limit": 120},
        "tick": None,
    }


def test_error_message_leads_with_the_code() -> None:
    assert str(AudioSheetError(ErrorCode.E_EXPORT_FAILED, "nope")).startswith("E_EXPORT_FAILED:")


def test_schema_validation_error_uses_its_own_code() -> None:
    assert SchemaValidationError("bad").code is ErrorCode.E_SCHEMA_INVALID


def test_invariant_violation_records_the_invariant() -> None:
    error = InvariantViolationError("V-2", "notes overlap", tick=480)
    assert error.invariant == "V-2"
    assert error.detail["invariant"] == "V-2"
    assert error.tick == 480
    assert "V-2" in error.message


def test_stage_cancelled_names_the_stage() -> None:
    error = StageCancelledError("S2.separate")
    assert error.code is ErrorCode.E_STAGE_CANCELLED
    assert "S2.separate" in error.message


def test_every_error_is_an_audiosheet_error() -> None:
    for error in (
        SchemaValidationError("x"),
        InvariantViolationError("V-1", "x"),
        StageCancelledError("S0"),
    ):
        assert isinstance(error, AudioSheetError)
