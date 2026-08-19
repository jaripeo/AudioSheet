"""The Stage protocol: fingerprinting, progress, cancellation, pass-through."""

from __future__ import annotations

from typing import Any

import pytest

from audiosheet.config.constants import AUDIOSHEET_SEED
from audiosheet.pipeline.cache import StageCache
from audiosheet.pipeline.errors import ErrorCode, StageCancelledError, WarningCode
from audiosheet.pipeline.stage import (
    PassThroughStage,
    Stage,
    StageContext,
    StageReport,
    fingerprint_input,
)


class Doubler(Stage[int, int]):
    """A stage that doubles an integer, used to exercise the base class."""

    name = "S_double"
    version = "1.0.0"

    def __init__(self, factor: int = 2) -> None:
        """Create the stage with the given multiplier."""
        self.factor = factor

    def config(self) -> dict[str, Any]:
        return {"factor": self.factor}

    def execute(self, data: int, ctx: StageContext) -> int:
        return data * self.factor

    def decode(self, raw: Any) -> int:
        return int(raw)


def make_ctx(cache: StageCache) -> StageContext:
    return StageContext(job_id="test", cache=cache)


def test_context_defaults_to_the_deterministic_seed(cache: StageCache) -> None:
    """INV-2: all randomness is seeded from one constant."""
    assert make_ctx(cache).seed == AUDIOSHEET_SEED


def test_pass_through_returns_its_input_unchanged(cache: StageCache) -> None:
    ctx = make_ctx(cache)
    payload = {"a": [1, 2, 3]}
    assert PassThroughStage().run(payload, ctx) is payload


def test_run_reports_start_and_completion(cache: StageCache) -> None:
    ctx = make_ctx(cache)
    PassThroughStage().run(1, ctx)
    fractions = [fraction for _, fraction, _ in ctx.progress_log]
    assert fractions[0] == 0.0
    assert fractions[-1] == 1.0
    assert 0.5 in fractions


def test_progress_is_clamped(cache: StageCache) -> None:
    ctx = make_ctx(cache)
    ctx.report_progress("S_x", 5.0)
    ctx.report_progress("S_x", -5.0)
    assert [f for _, f, _ in ctx.progress_log] == [1.0, 0.0]


def test_cancellation_raises_before_the_stage_body(cache: StageCache) -> None:
    ctx = make_ctx(cache)
    ctx.cancel()
    assert ctx.is_cancelled
    with pytest.raises(StageCancelledError) as excinfo:
        PassThroughStage().run(1, ctx)
    assert excinfo.value.code is ErrorCode.E_STAGE_CANCELLED


def test_cancellation_is_observed_mid_stage(cache: StageCache) -> None:
    """The pass-through stage has a checkpoint after its 0.5 progress report."""

    class CancelMidway(PassThroughStage):
        def execute(self, data: Any, ctx: StageContext) -> Any:
            ctx.cancel()
            return super().execute(data, ctx)

    with pytest.raises(StageCancelledError):
        CancelMidway().run(1, make_ctx(cache))


def test_warnings_accumulate_on_the_context(cache: StageCache) -> None:
    ctx = make_ctx(cache)
    ctx.warn(WarningCode.W_STEM_QUIET, "piano 34 dB down", tick=None)
    assert [w.code for w in ctx.warnings] == [WarningCode.W_STEM_QUIET]
    assert ctx.warnings[0].as_dict()["code"] == "W_STEM_QUIET"


def test_fingerprint_is_stable_for_identical_input() -> None:
    stage = Doubler()
    assert stage.fingerprint(21) == stage.fingerprint(21)


def test_fingerprint_changes_with_the_input() -> None:
    stage = Doubler()
    assert stage.fingerprint(21) != stage.fingerprint(22)


def test_fingerprint_changes_with_the_configuration() -> None:
    """Config participates in the key, so a re-tuned stage cannot serve stale output."""
    assert Doubler(2).fingerprint(21) != Doubler(3).fingerprint(21)


def test_fingerprint_changes_with_the_version() -> None:
    class Bumped(Doubler):
        version = "2.0.0"

    assert Doubler().fingerprint(21) != Bumped().fingerprint(21)


def test_fingerprint_is_namespaced_by_stage_name() -> None:
    assert PassThroughStage("S_a").fingerprint(1) != PassThroughStage("S_b").fingerprint(1)


def test_fingerprint_input_prefers_an_explicit_content_hash() -> None:
    class Payload:
        def content_hash(self) -> str:
            return "b3:explicit"

    assert fingerprint_input(Payload()) == "b3:explicit"


def test_fingerprint_input_handles_pydantic_models(simple_scale: Any) -> None:
    assert fingerprint_input(simple_scale).startswith("b3:")


def test_fingerprint_input_ignores_dict_ordering() -> None:
    assert fingerprint_input({"a": 1, "b": 2}) == fingerprint_input({"b": 2, "a": 1})


def test_a_cacheable_stage_without_decode_says_so(cache: StageCache) -> None:
    class Undecodable(Stage[int, int]):
        name = "S_undecodable"
        version = "1.0.0"

        def execute(self, data: int, ctx: StageContext) -> int:
            return data

    with pytest.raises(NotImplementedError, match="decode"):
        Undecodable().decode({"a": 1})


def test_report_renders_a_processing_step() -> None:
    report = StageReport(
        stage="S3.basic_pitch",
        version="1.0.0",
        fingerprint="b3:abc",
        duration_ms=12.5,
        device="cpu",
        params_hash="b3:def",
        cache_hit=False,
        warnings=["W_LOW_CONFIDENCE"],
    )
    step = report.as_processing_step()
    assert step == {
        "stage": "S3.basic_pitch",
        "version": "1.0.0",
        "duration_ms": 12.5,
        "device": "cpu",
        "params_hash": "b3:def",
        "warnings": ["W_LOW_CONFIDENCE"],
    }
    assert "fingerprint" not in step
