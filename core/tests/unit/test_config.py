"""Normative constants, ingestion limits, and offline-only path resolution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from audiosheet.config import limits
from audiosheet.config.constants import (
    AUDIOSHEET_SEED,
    LOW_CONFIDENCE_THRESHOLD,
    MP3_FALLBACK_TRIM_SAMPLES,
    PCM_VARIANTS,
    PPQ,
    TARGET_LUFS,
    TRANSCRIPTION_FRAME_MS,
    TRUE_PEAK_CEILING_DBTP,
)
from audiosheet.config.paths import (
    CACHE_ROOT_ENV,
    MODELS_ROOT_ENV,
    cache_root,
    load_manifest,
    model_path,
    models_root,
    repo_root,
)
from audiosheet.pipeline.errors import AudioSheetError, ErrorCode


def test_normative_constants_match_the_architecture() -> None:
    assert PPQ == 960
    assert AUDIOSHEET_SEED == 20240101
    assert TARGET_LUFS == -18.0
    assert TRUE_PEAK_CEILING_DBTP == -1.0
    assert MP3_FALLBACK_TRIM_SAMPLES == 1105
    assert pytest.approx(11.61) == TRANSCRIPTION_FRAME_MS
    assert LOW_CONFIDENCE_THRESHOLD == 0.35


def test_the_three_pcm_variants_are_declared_once() -> None:
    """Section 1.3: resampling happens exactly once, into exactly these variants."""
    assert PCM_VARIANTS == {
        "pcm_44k_stereo": (44100, 2),
        "pcm_22k_mono": (22050, 1),
        "pcm_16k_mono": (16000, 1),
    }


def test_ingestion_limits_match_the_architecture() -> None:
    assert limits.MAX_FILE_SIZE_BYTES == 120 * 1024 * 1024
    assert limits.MAX_DURATION_S == 600.0
    assert limits.MIN_DURATION_S == 1.0
    assert limits.MAX_CHANNELS == 2


def test_repo_root_contains_the_architecture_document() -> None:
    assert (repo_root() / "ARCHITECTURE.md").is_file()


def test_models_root_defaults_into_the_repository() -> None:
    assert models_root() == repo_root() / "models"


def test_models_root_honours_the_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(MODELS_ROOT_ENV, str(tmp_path))
    assert models_root() == tmp_path.resolve()


def test_cache_root_honours_the_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(CACHE_ROOT_ENV, str(tmp_path / "cache"))
    assert cache_root() == (tmp_path / "cache").resolve()
    assert cache_root().is_dir()


def test_the_model_manifest_parses() -> None:
    manifest = load_manifest()
    assert manifest, "models/manifest.json declares no models"
    required = {"name", "filename", "sha256", "license", "status", "phase"}
    for entry in manifest:
        assert required <= set(entry)
        assert entry["status"] in {"pending", "vendored"}


def test_pending_models_have_no_pinned_digest() -> None:
    """A pending entry must not claim a digest it has not verified."""
    for entry in load_manifest():
        if entry["status"] == "pending":
            assert entry["sha256"] == ""


def test_manifest_names_are_unique() -> None:
    names = [entry["name"] for entry in load_manifest()]
    assert len(names) == len(set(names))


def test_a_missing_manifest_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """INV-1: a missing model manifest is a hard failure, never a download."""
    monkeypatch.setenv(MODELS_ROOT_ENV, str(tmp_path))
    with pytest.raises(AudioSheetError) as excinfo:
        load_manifest()
    assert excinfo.value.code is ErrorCode.E_MODEL_MISSING


def test_an_unvendored_model_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A manifest entry whose file is absent must not trigger a fetch."""
    monkeypatch.setenv(MODELS_ROOT_ENV, str(tmp_path))
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "models": [
                    {
                        "name": "ghost",
                        "filename": "ghost.onnx",
                        "sha256": "0" * 64,
                        "license": "Apache-2.0",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(AudioSheetError) as excinfo:
        model_path("ghost")
    assert excinfo.value.code is ErrorCode.E_MODEL_MISSING
    assert "not vendored" in excinfo.value.message


def test_an_unknown_model_name_fails_closed() -> None:
    with pytest.raises(AudioSheetError) as excinfo:
        model_path("not-a-model")
    assert excinfo.value.code is ErrorCode.E_MODEL_MISSING
