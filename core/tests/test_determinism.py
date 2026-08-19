"""INV-2: identical input must produce byte-identical output, always.

The subprocess checks matter because Python's string hashing is randomised per
process by default; a fingerprint that depends on it would pass in-process and
fail in CI.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from audiosheet.config.constants import AUDIOSHEET_SEED
from audiosheet.pipeline.cache import StageCache, canonical_json, hash_json
from audiosheet.pipeline.runner import run_chain
from audiosheet.pipeline.stage import PassThroughStage


@pytest.mark.gate
def test_two_runs_write_identical_cache_bytes(
    tmp_path: Path, simple_scale_payload: dict[str, Any]
) -> None:
    """Running the same chain twice into two caches yields identical files."""
    outputs = []
    for name in ("run-a", "run-b"):
        cache = StageCache(tmp_path / name)
        run_chain([PassThroughStage("S6"), PassThroughStage("S7")], simple_scale_payload, cache)
        outputs.append(
            {
                path.relative_to(cache.root).as_posix(): path.read_bytes()
                for path in sorted(cache.root.rglob("*.json"))
            }
        )
    assert outputs[0] == outputs[1]
    assert outputs[0], "the chain wrote no cache entries"


def test_stage_fingerprints_are_stable_across_processes() -> None:
    """A fingerprint may not depend on PYTHONHASHSEED."""
    script = (
        "from audiosheet.pipeline.stage import PassThroughStage;"
        "print(PassThroughStage('S_x').fingerprint({'b': 1, 'a': [2, 3]}))"
    )
    first = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=True
    ).stdout
    second = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=True
    ).stdout
    assert first == second
    assert first.startswith("b3:")


def test_canonical_json_is_stable_across_processes(simple_scale_path: Path) -> None:
    script = (
        "import json,sys;"
        "from audiosheet.pipeline.cache import canonical_json;"
        f"sys.stdout.write(canonical_json(json.load(open({str(simple_scale_path)!r}))))"
    )
    runs = [
        subprocess.run(
            [sys.executable, "-c", script], capture_output=True, text=True, check=True
        ).stdout
        for _ in range(2)
    ]
    assert runs[0] == runs[1]


def test_hash_json_is_insensitive_to_key_order(simple_scale_payload: dict[str, Any]) -> None:
    reordered = dict(reversed(list(simple_scale_payload.items())))
    assert hash_json(simple_scale_payload) == hash_json(reordered)


def test_schema_generation_is_deterministic(repo_root: Path) -> None:
    """Regenerating the artefacts twice produces identical content."""
    sys.path.insert(0, str(repo_root / "scripts"))
    try:
        import gen_schema

        first = {a.path: a.content for a in gen_schema.generate(gen_schema.TS_SRC_DIR)}
        second = {a.path: a.content for a in gen_schema.generate(gen_schema.TS_SRC_DIR)}
    finally:
        sys.path.remove(str(repo_root / "scripts"))
    assert first == second


def test_the_seed_is_the_documented_constant() -> None:
    assert AUDIOSHEET_SEED == 20240101


def test_canonical_json_has_no_insignificant_whitespace() -> None:
    text = canonical_json({"a": 1, "b": [1, 2]})
    assert ", " not in text
    assert ": " not in text
    assert text.endswith("\n")
