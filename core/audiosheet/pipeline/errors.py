"""Error and warning code registry — ARCHITECTURE.md Appendix 5.4 (Normative).

Every failure surfaced to the UI carries one of these codes. Adding a code here
without adding it to Appendix 5.4 is a specification drift and MUST NOT happen.
"""

from __future__ import annotations

from enum import StrEnum


class ErrorCode(StrEnum):
    """Fatal conditions. The job stops and the UI shows a remediation."""

    E_INGEST_FORMAT = "E_INGEST_FORMAT"
    E_INGEST_LIMIT = "E_INGEST_LIMIT"
    E_INGEST_DECODE = "E_INGEST_DECODE"
    E_MODEL_MISSING = "E_MODEL_MISSING"
    E_MODEL_INTEGRITY = "E_MODEL_INTEGRITY"
    E_SEPARATION_OOM = "E_SEPARATION_OOM"
    E_DIFF_INVALID = "E_DIFF_INVALID"
    E_TAB_UNPLAYABLE = "E_TAB_UNPLAYABLE"
    E_EXPORT_FAILED = "E_EXPORT_FAILED"
    E_SCHEMA_INVALID = "E_SCHEMA_INVALID"
    E_INVARIANT_VIOLATED = "E_INVARIANT_VIOLATED"
    E_CACHE_CORRUPT = "E_CACHE_CORRUPT"
    E_STAGE_CANCELLED = "E_STAGE_CANCELLED"


class WarningCode(StrEnum):
    """Non-fatal conditions. Recorded in ScoreDocument.diagnostics.warnings."""

    W_INGEST_DOWNMIX = "W_INGEST_DOWNMIX"
    W_STEM_QUIET = "W_STEM_QUIET"
    W_TEMPO_UNSTABLE = "W_TEMPO_UNSTABLE"
    W_METER_AMBIGUOUS = "W_METER_AMBIGUOUS"
    W_LOW_CONFIDENCE = "W_LOW_CONFIDENCE"
    W_POLYPHONY_TRUNCATED = "W_POLYPHONY_TRUNCATED"
    W_SEPARATION_SKIPPED = "W_SEPARATION_SKIPPED"
    W_OCTAVE_CORRECTED = "W_OCTAVE_CORRECTED"


class AudioSheetError(Exception):
    """A pipeline failure carrying a registry code.

    Attributes:
        code: The registry code, surfaced verbatim to the UI.
        message: Human-readable summary.
        detail: Optional structured context for diagnostics.
        tick: Optional tick position the failure is anchored to.
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        detail: dict[str, object] | None = None,
        tick: int | None = None,
    ) -> None:
        """Initialise the error with its registry code and context."""
        super().__init__(f"{code.value}: {message}")
        self.code = code
        self.message = message
        self.detail: dict[str, object] = detail or {}
        self.tick = tick

    def as_dict(self) -> dict[str, object]:
        """Return the wire form used by the local service and diagnostics."""
        return {
            "code": self.code.value,
            "message": self.message,
            "detail": self.detail,
            "tick": self.tick,
        }


class SchemaValidationError(AudioSheetError):
    """The document failed JSON Schema validation at the S6 gate."""

    def __init__(self, message: str, *, detail: dict[str, object] | None = None) -> None:
        """Initialise with ``E_SCHEMA_INVALID``."""
        super().__init__(ErrorCode.E_SCHEMA_INVALID, message, detail=detail)


class InvariantViolationError(AudioSheetError):
    """A V-1..V-7 invariant failed (ARCHITECTURE.md Section 1.9)."""

    def __init__(
        self,
        invariant: str,
        message: str,
        *,
        tick: int | None = None,
        detail: dict[str, object] | None = None,
    ) -> None:
        """Initialise with ``E_INVARIANT_VIOLATED`` and the invariant's id."""
        super().__init__(
            ErrorCode.E_INVARIANT_VIOLATED,
            f"{invariant}: {message}",
            detail={**(detail or {}), "invariant": invariant},
            tick=tick,
        )
        self.invariant = invariant


class StageCancelledError(AudioSheetError):
    """The job was cancelled between or inside a stage."""

    def __init__(self, stage: str) -> None:
        """Initialise with ``E_STAGE_CANCELLED``."""
        super().__init__(ErrorCode.E_STAGE_CANCELLED, f"cancelled during {stage}")
