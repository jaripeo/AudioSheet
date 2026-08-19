"""The pipeline DAG: chaining, caching, progress, cancellation, provenance."""

from __future__ import annotations

from typing import Any

import pytest

from audiosheet.pipeline.cache import StageCache
from audiosheet.pipeline.errors import AudioSheetError, ErrorCode, StageCancelledError
from audiosheet.pipeline.runner import PipelineRunner, run_chain
from audiosheet.pipeline.stage import PassThroughStage, Stage, StageContext


class Counting(Stage[int, int]):
    """Adds one and records how many times it actually executed."""

    version = "1.0.0"

    def __init__(self, name: str) -> None:
        """Create the stage under ``name`` with a zeroed call counter."""
        self.name = name
        self.calls = 0

    def execute(self, data: int, ctx: StageContext) -> int:
        self.calls += 1
        return data + 1

    def decode(self, raw: Any) -> int:
        return int(raw)


class Exploding(Stage[int, int]):
    """Raises a typed pipeline error."""

    name = "S_boom"
    version = "1.0.0"
    cacheable = False

    def execute(self, data: int, ctx: StageContext) -> int:
        raise AudioSheetError(ErrorCode.E_SEPARATION_OOM, "out of memory")


def test_a_three_stage_chain_threads_output_into_input(cache: StageCache) -> None:
    stages = [Counting("S_a"), Counting("S_b"), Counting("S_c")]
    result = run_chain(stages, 0, cache)
    assert result.output == 3
    assert [s.calls for s in stages] == [1, 1, 1]


def test_every_stage_is_reported(cache: StageCache) -> None:
    result = run_chain([Counting("S_a"), Counting("S_b")], 0, cache)
    assert [r.stage for r in result.reports] == ["S_a", "S_b"]
    assert all(r.fingerprint.startswith("b3:") for r in result.reports)
    assert all(r.duration_ms >= 0.0 for r in result.reports)


def test_a_second_run_is_served_entirely_from_cache(cache: StageCache) -> None:
    """Section 1.2: a stage MUST be skippable when its fingerprint hits the cache."""
    first = [Counting("S_a"), Counting("S_b")]
    run_chain(first, 0, cache)
    second = [Counting("S_a"), Counting("S_b")]
    result = run_chain(second, 0, cache)
    assert result.output == 2
    assert [s.calls for s in second] == [0, 0]
    assert result.cache_hits == 2
    assert all(r.cache_hit for r in result.reports)


def test_a_changed_input_misses_the_cache(cache: StageCache) -> None:
    run_chain([Counting("S_a")], 0, cache)
    stage = Counting("S_a")
    run_chain([stage], 5, cache)
    assert stage.calls == 1


def test_a_bumped_version_invalidates_the_cache(cache: StageCache) -> None:
    run_chain([Counting("S_a")], 0, cache)

    class Bumped(Counting):
        version = "2.0.0"

    stage = Bumped("S_a")
    run_chain([stage], 0, cache)
    assert stage.calls == 1


def test_use_cache_false_forces_recomputation(cache: StageCache) -> None:
    run_chain([Counting("S_a")], 0, cache)
    stage = Counting("S_a")
    run_chain([stage], 0, cache, use_cache=False)
    assert stage.calls == 1


def test_an_uncacheable_stage_is_never_stored(cache: StageCache) -> None:
    stage = PassThroughStage("S_volatile", cacheable=False)
    runner = PipelineRunner([stage], cache)
    runner.run(1, runner.make_context("job"))
    assert not cache.json_path("S_volatile", stage.fingerprint(1)).exists()


def test_duplicate_stage_names_are_rejected(cache: StageCache) -> None:
    """Two stages sharing a name would collide in the cache."""
    with pytest.raises(ValueError, match="duplicate stage names"):
        PipelineRunner([Counting("S_same"), Counting("S_same")], cache)


def test_progress_is_recorded_for_every_stage(cache: StageCache) -> None:
    runner = PipelineRunner([Counting("S_a"), Counting("S_b")], cache)
    ctx = runner.make_context("job")
    runner.run(0, ctx)
    assert {stage for stage, _, _ in ctx.progress_log} == {"S_a", "S_b"}


def test_a_cache_hit_still_reports_completion(cache: StageCache) -> None:
    run_chain([Counting("S_a")], 0, cache)
    runner = PipelineRunner([Counting("S_a")], cache)
    ctx = runner.make_context("job")
    runner.run(0, ctx)
    assert ("S_a", 1.0, "cache hit") in ctx.progress_log


def test_cancellation_stops_the_chain_between_stages(cache: StageCache) -> None:
    first, second = Counting("S_a"), Counting("S_b")
    runner = PipelineRunner([first, second], cache)
    ctx = runner.make_context("job")

    class CancelAfterFirst(Counting):
        def execute(self, data: int, ctx: StageContext) -> int:
            ctx.cancel()
            return super().execute(data, ctx)

    first = CancelAfterFirst("S_a")
    runner = PipelineRunner([first, second], cache)
    ctx = runner.make_context("job")
    with pytest.raises(StageCancelledError):
        runner.run(0, ctx)
    assert second.calls == 0


def test_stage_errors_propagate_unchanged(cache: StageCache) -> None:
    with pytest.raises(AudioSheetError) as excinfo:
        run_chain([Exploding()], 0, cache)
    assert excinfo.value.code is ErrorCode.E_SEPARATION_OOM


def test_processing_steps_are_provenance_shaped(cache: StageCache) -> None:
    result = run_chain([Counting("S_a")], 0, cache)
    step = result.processing_steps()[0]
    assert set(step) == {"stage", "version", "duration_ms", "device", "params_hash", "warnings"}


def test_describe_lists_the_chain(cache: StageCache) -> None:
    runner = PipelineRunner([Counting("S_a"), Counting("S_b")], cache)
    assert runner.describe() == [
        {"stage": "S_a", "version": "1.0.0"},
        {"stage": "S_b", "version": "1.0.0"},
    ]


def test_a_document_survives_a_pass_through_chain(
    cache: StageCache, simple_scale_payload: dict[str, Any]
) -> None:
    """The DAG carries a real ScoreDocument payload, cache round-trip included."""
    stages = [PassThroughStage("S6"), PassThroughStage("S7")]
    first = run_chain(stages, simple_scale_payload, cache)
    second = run_chain(
        [PassThroughStage("S6"), PassThroughStage("S7")], simple_scale_payload, cache
    )
    assert first.output == simple_scale_payload
    assert second.output == simple_scale_payload
    assert second.cache_hits == 2
