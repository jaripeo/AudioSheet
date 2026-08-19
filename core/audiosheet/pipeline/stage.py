"""Stage protocol and fingerprinting — ARCHITECTURE.md Section 1.2.

Each stage implements ``name``, ``version``, ``fingerprint(data)`` and
``run(data, ctx)``. ``fingerprint`` is a BLAKE3 hash over
``(input_hash, stage_version, relevant_config)`` and is the cache key.

Stages never mutate their input (INV-3) and never open a socket (INV-1).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, Literal, Protocol, TypeVar, runtime_checkable

from audiosheet.config.constants import AUDIOSHEET_SEED
from audiosheet.pipeline.cache import StageCache, blake3_hex, hash_json
from audiosheet.pipeline.errors import StageCancelledError, WarningCode

TIn = TypeVar("TIn")
TOut = TypeVar("TOut")

#: Execution devices recorded in ProcessingStep.device.
Device = Literal["cpu", "cuda", "mps", "wasm"]


@runtime_checkable
class Fingerprintable(Protocol):
    """Anything that can supply its own stable content hash."""

    def content_hash(self) -> str:
        """Return a stable ``b3:<hex>`` fingerprint of this value's content."""
        ...


def fingerprint_input(data: Any) -> str:
    """Return a stable fingerprint for a stage input.

    Resolution order:

    1. ``Fingerprintable.content_hash()`` when the value provides it (used by
       large payloads such as ``AudioBundle``, which hash their backing files
       rather than their contents).
    2. Pydantic models are dumped in JSON mode and hashed canonically.
    3. Anything else is hashed as canonical JSON.

    Args:
        data: The stage input.

    Returns:
        A fingerprint of the form ``b3:<hex>``.
    """
    if isinstance(data, Fingerprintable):
        return data.content_hash()
    dump = getattr(data, "model_dump", None)
    if callable(dump):
        return hash_json(dump(mode="json"))
    return hash_json(data)


@dataclass
class StageWarning:
    """A non-fatal condition raised by a stage."""

    code: WarningCode
    message: str
    tick: int | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return the ScoreDocument.diagnostics.warnings wire form."""
        return {"code": self.code.value, "message": self.message, "tick": self.tick}


@dataclass
class StageReport:
    """What a runner records about one executed (or skipped) stage."""

    stage: str
    version: str
    fingerprint: str
    duration_ms: float
    device: Device
    params_hash: str
    cache_hit: bool
    warnings: list[str] = field(default_factory=list)

    def as_processing_step(self) -> dict[str, Any]:
        """Return the ScoreDocument.provenance.steps wire form."""
        return {
            "stage": self.stage,
            "version": self.version,
            "duration_ms": self.duration_ms,
            "device": self.device,
            "params_hash": self.params_hash,
            "warnings": list(self.warnings),
        }


@dataclass
class StageContext:
    """Ambient services handed to every stage.

    Attributes:
        job_id: Identifier of the enclosing job.
        cache: The content-addressed stage cache.
        device: Device this run resolved to, recorded in provenance.
        seed: Deterministic seed; always ``AUDIOSHEET_SEED`` (INV-2).
        warnings: Accumulated non-fatal conditions.
    """

    job_id: str
    cache: StageCache
    device: Device = "cpu"
    seed: int = AUDIOSHEET_SEED
    warnings: list[StageWarning] = field(default_factory=list)
    _cancelled: bool = False
    _progress: list[tuple[str, float, str]] = field(default_factory=list)

    def report_progress(self, stage: str, fraction: float, message: str = "") -> None:
        """Record progress for ``stage``.

        Args:
            stage: Stage name.
            fraction: Completion in ``[0, 1]``; clamped.
            message: Optional human-readable detail.
        """
        clamped = min(1.0, max(0.0, fraction))
        self._progress.append((stage, clamped, message))

    @property
    def progress_log(self) -> list[tuple[str, float, str]]:
        """Return the recorded progress events, oldest first."""
        return list(self._progress)

    def warn(self, code: WarningCode, message: str, tick: int | None = None) -> None:
        """Record a non-fatal condition."""
        self.warnings.append(StageWarning(code=code, message=message, tick=tick))

    def cancel(self) -> None:
        """Request cancellation; the next checkpoint raises ``StageCancelledError``."""
        self._cancelled = True

    @property
    def is_cancelled(self) -> bool:
        """Return whether cancellation has been requested."""
        return self._cancelled

    def check_cancelled(self, stage: str) -> None:
        """Raise if cancellation was requested.

        Raises:
            StageCancelledError: When ``cancel()`` has been called.
        """
        if self._cancelled:
            raise StageCancelledError(stage)


class Stage(ABC, Generic[TIn, TOut]):
    """Base class for every pipeline stage.

    Subclasses set ``name`` and ``version`` and implement ``execute``.
    ``version`` participates in the fingerprint, so bumping it invalidates the
    cache for that stage and everything downstream of it.
    """

    #: Stable stage identifier, e.g. ``"S0.ingest"``.
    name: str = "stage"

    #: Semantic version of this stage's behaviour.
    version: str = "0.0.0"

    #: Whether the runner may serve this stage from cache.
    cacheable: bool = True

    def config(self) -> dict[str, Any]:
        """Return the configuration that materially affects this stage's output.

        Anything omitted here is, by definition, claimed not to change the
        output. Getting this wrong causes stale cache hits.
        """
        return {}

    def params_hash(self) -> str:
        """Return the fingerprint of this stage's version and configuration."""
        return hash_json({"version": self.version, "config": self.config()})

    def fingerprint(self, data: TIn) -> str:
        """Return the cache key for running this stage on ``data``.

        Args:
            data: The stage input.

        Returns:
            A fingerprint of the form ``b3:<hex>``.
        """
        return blake3_hex(
            self.name.encode("utf-8"),
            fingerprint_input(data).encode("utf-8"),
            self.params_hash().encode("utf-8"),
        )

    @abstractmethod
    def execute(self, data: TIn, ctx: StageContext) -> TOut:
        """Do the stage's work. Implemented by subclasses."""
        raise NotImplementedError

    def run(self, data: TIn, ctx: StageContext) -> TOut:
        """Run the stage, honouring cancellation and reporting progress.

        Args:
            data: The stage input; never mutated (INV-3).
            ctx: Ambient stage services.

        Returns:
            The stage output.
        """
        ctx.check_cancelled(self.name)
        ctx.report_progress(self.name, 0.0, "start")
        result = self.execute(data, ctx)
        ctx.report_progress(self.name, 1.0, "done")
        return result

    # -- cache serialisation ------------------------------------------------
    # Stages whose output is JSON-serialisable get caching for free. Stages
    # producing large binary payloads override these two methods to write blobs
    # and return a manifest.

    def encode(self, value: TOut) -> Any:
        """Convert stage output into a JSON-serialisable form for the cache."""
        dump = getattr(value, "model_dump", None)
        if callable(dump):
            return dump(mode="json")
        return value

    def decode(self, raw: Any) -> TOut:
        """Rebuild stage output from its cached JSON form."""
        raise NotImplementedError(
            f"{self.name} is cacheable but does not implement decode(); "
            "either implement it or set cacheable = False"
        )


class PassThroughStage(Stage[Any, Any]):
    """A stage that returns its input unchanged.

    This exists to prove the DAG, fingerprinting, caching, progress reporting
    and cancellation all work before any real stage is written (Phase 0, step 3).
    """

    name = "S_passthrough"
    version = "1.0.0"

    def __init__(self, name: str | None = None, *, cacheable: bool = True) -> None:
        """Create a pass-through stage, optionally under a distinct name."""
        if name is not None:
            self.name = name
        self.cacheable = cacheable

    def execute(self, data: Any, ctx: StageContext) -> Any:
        """Return ``data`` unchanged after a mid-stage cancellation checkpoint."""
        ctx.report_progress(self.name, 0.5, "passing through")
        ctx.check_cancelled(self.name)
        return data

    def decode(self, raw: Any) -> Any:
        """Return the cached JSON form unchanged."""
        return raw
