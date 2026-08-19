"""Model and cache path resolution — offline-only (INV-1).

Nothing here may fetch anything. When a model file is missing the caller gets
``E_MODEL_MISSING`` and the pipeline fails closed.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Final

from audiosheet.pipeline.errors import AudioSheetError, ErrorCode

#: Directory name of the per-project cache, relative to the working directory.
CACHE_DIR_NAME: Final[str] = ".audiosheet"

#: Environment variable that overrides the vendored model root.
MODELS_ROOT_ENV: Final[str] = "AUDIOSHEET_MODELS_ROOT"

#: Environment variable that overrides the cache root.
CACHE_ROOT_ENV: Final[str] = "AUDIOSHEET_CACHE_ROOT"


def repo_root() -> Path:
    """Return the repository root, resolved from this file's location."""
    return Path(__file__).resolve().parents[3]


def models_root() -> Path:
    """Return the directory holding vendored model files.

    Honours ``AUDIOSHEET_MODELS_ROOT`` so a packaged app can point at its own
    resource bundle.
    """
    override = os.environ.get(MODELS_ROOT_ENV)
    if override:
        return Path(override).expanduser().resolve()
    return repo_root() / "models"


def cache_root() -> Path:
    """Return the project cache directory, creating it if absent."""
    override = os.environ.get(CACHE_ROOT_ENV)
    root = Path(override).expanduser().resolve() if override else Path.cwd() / CACHE_DIR_NAME
    root.mkdir(parents=True, exist_ok=True)
    return root


def manifest_path() -> Path:
    """Return the path of ``models/manifest.json``."""
    return models_root() / "manifest.json"


def load_manifest() -> list[dict[str, object]]:
    """Read and return the model manifest entries.

    Raises:
        AudioSheetError: ``E_MODEL_MISSING`` when the manifest is absent.
    """
    path = manifest_path()
    if not path.is_file():
        raise AudioSheetError(ErrorCode.E_MODEL_MISSING, f"model manifest not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    models = raw.get("models", [])
    if not isinstance(models, list):
        raise AudioSheetError(ErrorCode.E_MODEL_MISSING, f"malformed model manifest: {path}")
    return [dict(entry) for entry in models]


def model_path(name: str) -> Path:
    """Resolve a model file by manifest name.

    Args:
        name: The ``name`` field of a ``models/manifest.json`` entry.

    Returns:
        Absolute path to the model file.

    Raises:
        AudioSheetError: ``E_MODEL_MISSING`` when the entry or the file is absent.
    """
    for entry in load_manifest():
        if entry.get("name") == name:
            path = models_root() / str(entry["filename"])
            if not path.is_file():
                raise AudioSheetError(
                    ErrorCode.E_MODEL_MISSING,
                    f"model '{name}' declared in the manifest but not vendored at {path}",
                )
            return path
    raise AudioSheetError(ErrorCode.E_MODEL_MISSING, f"model '{name}' is not in the manifest")
