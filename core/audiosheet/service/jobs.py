"""Job registry, progress streaming and cancellation — ARCHITECTURE.md Section 5.2."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from audiosheet.pipeline.stage import StageContext
from audiosheet.schema import ScoreDocument


class JobState(StrEnum):
    """Lifecycle states a job passes through."""

    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProgressEvent:
    """One server-sent progress event."""

    stage: str
    progress: float
    message: str


@dataclass
class Job:
    """A single transcription job.

    Attributes:
        id: Job identifier.
        source_path: The uploaded audio file in the runtime directory.
        state: Current lifecycle state.
        events: Progress events emitted so far.
        document: The finished document, once the pipeline completes.
        error: The error payload, when the job failed.
    """

    id: str
    source_path: Path
    state: JobState = JobState.QUEUED
    events: list[ProgressEvent] = field(default_factory=list)
    document: ScoreDocument | None = None
    error: dict[str, object] | None = None
    context: StageContext | None = None


class JobRegistry:
    """In-process registry of jobs. One worker process per job (Section 4.3)."""

    def __init__(self) -> None:
        """Create an empty registry."""
        self._jobs: dict[str, Job] = {}

    def create(self, source_path: Path) -> Job:
        """Register a new job for an uploaded file.

        Args:
            source_path: The uploaded audio file.

        Returns:
            The registered job.

        Raises:
            NotImplementedError: Phase 1.
        """
        raise NotImplementedError("job registry lands in Phase 1")

    def get(self, job_id: str) -> Job | None:
        """Return a job by id, or ``None`` when unknown."""
        return self._jobs.get(job_id)

    def cancel(self, job_id: str) -> bool:
        """Request cancellation of a job.

        Args:
            job_id: The job to cancel.

        Returns:
            Whether a cancellable job was found.

        Raises:
            NotImplementedError: Phase 1.
        """
        raise NotImplementedError("job cancellation lands in Phase 1")
