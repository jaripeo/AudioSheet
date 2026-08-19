"""DAG execution, progress and cancellation — ARCHITECTURE.md Section 1.2.

The Phase 0 runner executes a linear chain of stages, which is the shape S0..S6
actually has once the fan-out to S3/S4 is expressed as a stage that consumes the
whole ``StemSet``. It gives every stage caching, progress, timing, warning
collection and cancellation for free.
"""

from __future__ import annotations

import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

from audiosheet.pipeline.cache import StageCache
from audiosheet.pipeline.errors import AudioSheetError
from audiosheet.pipeline.stage import Stage, StageContext, StageReport, StageWarning


@dataclass
class PipelineResult:
    """The outcome of a pipeline run."""

    output: Any
    reports: list[StageReport] = field(default_factory=list)
    warnings: list[StageWarning] = field(default_factory=list)

    @property
    def cache_hits(self) -> int:
        """Return how many stages were served from cache."""
        return sum(1 for report in self.reports if report.cache_hit)

    def processing_steps(self) -> list[dict[str, Any]]:
        """Return the ScoreDocument.provenance.steps wire form for every stage."""
        return [report.as_processing_step() for report in self.reports]


class PipelineRunner:
    """Executes an ordered chain of stages against a shared context."""

    def __init__(self, stages: Sequence[Stage[Any, Any]], cache: StageCache) -> None:
        """Create a runner over ``stages`` using ``cache``.

        Args:
            stages: The stages to run, in order.
            cache: The content-addressed stage cache.

        Raises:
            ValueError: When two stages share a name, which would collide in the
                cache and make provenance ambiguous.
        """
        names = [stage.name for stage in stages]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            raise ValueError(f"duplicate stage names: {', '.join(duplicates)}")
        self.stages = list(stages)
        self.cache = cache

    def make_context(self, job_id: str) -> StageContext:
        """Return a fresh context bound to this runner's cache."""
        return StageContext(job_id=job_id, cache=self.cache)

    def run(
        self,
        data: Any,
        ctx: StageContext,
        *,
        use_cache: bool = True,
    ) -> PipelineResult:
        """Run every stage in order, threading each output into the next.

        Args:
            data: Input to the first stage.
            ctx: Stage context; cancellation is observed between stages too.
            use_cache: When ``False``, every stage is recomputed.

        Returns:
            The pipeline result, including a per-stage report.

        Raises:
            AudioSheetError: Propagated unchanged from a failing stage.
        """
        reports: list[StageReport] = []
        current = data

        for stage in self.stages:
            ctx.check_cancelled(stage.name)
            fingerprint = stage.fingerprint(current)
            warnings_before = len(ctx.warnings)
            started = time.perf_counter()

            cached: Any | None = None
            if use_cache and stage.cacheable:
                cached = self.cache.get(stage.name, fingerprint)

            if cached is not None:
                current = stage.decode(cached)
                cache_hit = True
                ctx.report_progress(stage.name, 1.0, "cache hit")
            else:
                current = stage.run(current, ctx)
                cache_hit = False
                if use_cache and stage.cacheable:
                    self.cache.put(stage.name, fingerprint, stage.encode(current))

            reports.append(
                StageReport(
                    stage=stage.name,
                    version=stage.version,
                    fingerprint=fingerprint,
                    duration_ms=(time.perf_counter() - started) * 1000.0,
                    device=ctx.device,
                    params_hash=stage.params_hash(),
                    cache_hit=cache_hit,
                    warnings=[w.code.value for w in ctx.warnings[warnings_before:]],
                )
            )

        return PipelineResult(output=current, reports=reports, warnings=list(ctx.warnings))

    def describe(self) -> list[dict[str, str]]:
        """Return the stage chain as name/version pairs, for diagnostics."""
        return [{"stage": s.name, "version": s.version} for s in self.stages]


def run_chain(
    stages: Iterable[Stage[Any, Any]],
    data: Any,
    cache: StageCache,
    *,
    job_id: str = "adhoc",
    use_cache: bool = True,
) -> PipelineResult:
    """Convenience wrapper: build a runner, run it once, return the result.

    Args:
        stages: The stages to run, in order.
        data: Input to the first stage.
        cache: The content-addressed stage cache.
        job_id: Identifier recorded on the context.
        use_cache: When ``False``, every stage is recomputed.

    Returns:
        The pipeline result.
    """
    runner = PipelineRunner(list(stages), cache)
    return runner.run(data, runner.make_context(job_id), use_cache=use_cache)


__all__ = [
    "AudioSheetError",
    "PipelineResult",
    "PipelineRunner",
    "run_chain",
]
