"""Phase 0 tree contract: everything imports, and every stub says which phase owns it.

Phase 0 delivers the module tree with correct signatures and NotImplementedError
bodies. These tests protect that: an import error anywhere in the tree fails here
rather than three phases later, and a stub that forgets to name its phase is
caught before it becomes an untracked TODO.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import pkgutil
from pathlib import Path
from types import ModuleType

import pytest

import audiosheet

#: Modules whose contents are generated and therefore exempt from the stub rules.
GENERATED_PREFIX = "audiosheet.schema"

#: NotImplementedError raises that are runtime contract errors, not deferred work.
#: Stage.decode() is the abstract half of the cache protocol: a subclass that sets
#: cacheable = True without implementing it is a programming error, and no phase
#: will ever "implement" it.
CONTRACT_RAISES = {("audiosheet.pipeline.stage", "decode")}


def all_modules() -> list[str]:
    """Return every importable module name under ``audiosheet``."""
    names = ["audiosheet"]
    for info in pkgutil.walk_packages(audiosheet.__path__, prefix="audiosheet."):
        names.append(info.name)
    return sorted(names)


def imported() -> list[ModuleType]:
    """Import and return every module under ``audiosheet``."""
    return [importlib.import_module(name) for name in all_modules()]


def test_the_whole_tree_imports() -> None:
    """A broken import anywhere in the tree fails here, not in a later phase."""
    modules = imported()
    assert len(modules) > 30


def test_every_module_has_a_docstring() -> None:
    missing = [m.__name__ for m in imported() if not (m.__doc__ or "").strip()]
    assert missing == []


def test_the_expected_packages_exist() -> None:
    """The Section 5.1 tree is present under core/audiosheet."""
    expected = {
        "audiosheet.cli",
        "audiosheet.config.constants",
        "audiosheet.config.limits",
        "audiosheet.config.paths",
        "audiosheet.pipeline.cache",
        "audiosheet.pipeline.errors",
        "audiosheet.pipeline.runner",
        "audiosheet.pipeline.stage",
        "audiosheet.ingest.decode",
        "audiosheet.ingest.loudness",
        "audiosheet.ingest.resample",
        "audiosheet.ingest.sniff",
        "audiosheet.analysis.beats",
        "audiosheet.analysis.key",
        "audiosheet.analysis.meter",
        "audiosheet.analysis.onsets",
        "audiosheet.analysis.swing",
        "audiosheet.analysis.tempo_map",
        "audiosheet.separation.bleed",
        "audiosheet.separation.demucs_runner",
        "audiosheet.separation.gating",
        "audiosheet.transcription.basic_pitch",
        "audiosheet.transcription.basic_pitch_params",
        "audiosheet.transcription.crepe",
        "audiosheet.transcription.drums",
        "audiosheet.transcription.mono_segmenter",
        "audiosheet.transcription.postprocess",
        "audiosheet.symbolic.chords",
        "audiosheet.symbolic.consolidate",
        "audiosheet.symbolic.grid",
        "audiosheet.symbolic.quantize",
        "audiosheet.symbolic.spelling",
        "audiosheet.symbolic.staves",
        "audiosheet.symbolic.voices",
        "audiosheet.validate.invariants",
        "audiosheet.validate.jsonschema_gate",
        "audiosheet.export.midi",
        "audiosheet.export.musicxml",
        "audiosheet.export.practice_midi",
        "audiosheet.service.app",
        "audiosheet.service.auth",
        "audiosheet.service.jobs",
        "audiosheet.service.routes",
    }
    assert expected - set(all_modules()) == set()


def _not_implemented_messages(source: str) -> list[tuple[str, str]]:
    """Return (enclosing function name, message text) for each stub raise."""
    found: list[tuple[str, str]] = []
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Raise) or inner.exc is None:
                continue
            call = inner.exc
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
                continue
            if call.func.id != "NotImplementedError":
                continue
            parts: list[str] = []
            for arg in call.args:
                for piece in ast.walk(arg):
                    if isinstance(piece, ast.Constant) and isinstance(piece.value, str):
                        parts.append(piece.value)
            found.append((node.name, " ".join(parts)))
    return found


def test_every_stub_names_the_phase_that_implements_it() -> None:
    """A deferred stub must say which phase owns it — never a bare TODO."""
    offenders: list[str] = []
    for module in imported():
        if module.__name__.startswith(GENERATED_PREFIX):
            continue
        source_file = getattr(module, "__file__", None)
        if source_file is None:
            continue
        source = Path(source_file).read_text(encoding="utf-8")
        for function_name, message in _not_implemented_messages(source):
            if (module.__name__, function_name) in CONTRACT_RAISES:
                continue
            if "Phase" not in message:
                offenders.append(f"{module.__name__}.{function_name}: {message[:60]!r}")
    assert offenders == []


def test_the_stub_scan_actually_finds_stubs() -> None:
    """Guard against the scan silently matching nothing and passing vacuously."""
    source = Path(inspect.getsourcefile(importlib.import_module("audiosheet.ingest.sniff")) or "")
    messages = _not_implemented_messages(source.read_text(encoding="utf-8"))
    assert len(messages) == 2
    assert all("Phase 1" in message for _, message in messages)


def test_no_bare_todo_or_fixme_markers() -> None:
    """Deferred work lives in the phased plan, not in scattered comments."""
    offenders: list[str] = []
    for module in imported():
        source_file = getattr(module, "__file__", None)
        if source_file is None:
            continue
        source = Path(source_file).read_text(encoding="utf-8")
        for marker in ("TODO", "FIXME", "XXX"):
            if marker in source:
                offenders.append(f"{module.__name__}: {marker}")
    assert offenders == []


def test_every_public_function_is_annotated() -> None:
    """Mypy --strict enforces this; the test makes the failure legible."""
    offenders: list[str] = []
    for module in imported():
        if module.__name__.startswith(GENERATED_PREFIX):
            continue
        for name, obj in vars(module).items():
            if name.startswith("_") or not inspect.isfunction(obj):
                continue
            if obj.__module__ != module.__name__:
                continue
            signature = inspect.signature(obj)
            if signature.return_annotation is inspect.Signature.empty:
                offenders.append(f"{module.__name__}.{name}: missing return annotation")
            for parameter in signature.parameters.values():
                if parameter.annotation is inspect.Parameter.empty:
                    offenders.append(f"{module.__name__}.{name}({parameter.name})")
    assert offenders == []


@pytest.mark.parametrize(
    ("module_name", "attribute"),
    [
        ("audiosheet.ingest.sniff", "sniff_bytes"),
        ("audiosheet.ingest.resample", "resample"),
        ("audiosheet.ingest.loudness", "integrated_lufs"),
        ("audiosheet.analysis.beats", "track_beats"),
        ("audiosheet.analysis.meter", "estimate_meter"),
        ("audiosheet.separation.demucs_runner", "resolve_device"),
        ("audiosheet.transcription.basic_pitch", "infer"),
        ("audiosheet.transcription.drums", "classify_onset_heuristic"),
        ("audiosheet.symbolic.quantize", "quantize"),
        ("audiosheet.symbolic.spelling", "spell"),
        ("audiosheet.export.musicxml", "to_musicxml"),
        ("audiosheet.export.midi", "to_midi_bytes"),
        ("audiosheet.service.auth", "generate_token"),
        ("audiosheet.service.app", "create_app"),
    ],
)
def test_stubs_raise_not_implemented(module_name: str, attribute: str) -> None:
    """Calling a Phase 1+ entry point fails loudly rather than returning nonsense."""
    module = importlib.import_module(module_name)
    function = getattr(module, attribute)
    positional = [
        p
        for p in inspect.signature(function).parameters.values()
        if p.kind in {p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD}
    ]
    with pytest.raises(NotImplementedError):
        function(*[None] * len(positional))
