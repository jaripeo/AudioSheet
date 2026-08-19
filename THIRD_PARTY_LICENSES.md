# Third-party licences

ARCHITECTURE.md Section 4.2 makes this a shipping blocker, not a footnote: several
separation-model **weights** carry research-use conditions distinct from their code
licence, and shipping without checking would be a licence violation rather than an
oversight.

## Status

**Incomplete — no model weights are vendored yet.** Every entry in
`models/manifest.json` is `status: "pending"`. `scripts/verify_models.py --strict`
fails while any entry is pending and is a release gate for Phase 8.

Each licence below MUST be re-verified against the actual artefact at vendoring
time, and the verified text reproduced in this file. The notes are a starting point
for that check, not a substitute for it.

## Models

| Model | Vendored | Code licence (upstream claim) | Weights licence | Action |
| --- | --- | --- | --- | --- |
| basic-pitch (`nmp.onnx`) | pending (Phase 5) | Apache-2.0 | to verify | Confirm the weights ship under the same terms as the code |
| CREPE (`crepe_full`, `crepe_tiny`) | pending (Phase 5) | MIT | to verify | Confirm the published checkpoints' terms |
| Demucs v4 (`htdemucs_6s`) | pending (Phase 4) | MIT | **to verify — trained on MUSDB18-HQ** | Highest-risk entry: MUSDB18-HQ carries research-use conditions. Resolve before any release |
| Beat/downbeat tracker | pending (Phase 3) | to determine | to determine | Model not yet chosen |
| Chord recognition | pending (Phase 6) | to determine | to determine | Model not yet chosen |
| Drum classifier | pending (Phase 5) | to determine | to determine | May be trained in-house, which removes the question |
| General MIDI soundfont (`gm.sf2`) | pending (Phase 2) | to determine | to determine | Prefer a clearly CC0 or public-domain bank |

## Runtime and build dependencies

Declared in `core/pyproject.toml` and `package.json` / `pnpm-lock.yaml`. Phase 8
generates the full dependency licence report into this file. Notable direct
dependencies and their commonly-stated licences, to be confirmed by that report:

| Dependency | Commonly stated |
| --- | --- |
| ONNX Runtime | MIT |
| PyTorch, torchaudio | BSD-3-Clause |
| numpy, scipy | BSD-3-Clause |
| librosa, soundfile, soxr | ISC / BSD-3-Clause / LGPL-2.1 (soxr — check linkage) |
| madmom | BSD-3-Clause with a research-use clause — **check before shipping** |
| music21 | BSD-3-Clause |
| pretty_midi, mido | MIT |
| pydantic, jsonschema, FastAPI, uvicorn | MIT |
| VexFlow | MIT |
| AlphaTab | MPL-2.0 — **check the implications of bundling** |
| React, Vite, Zustand, TypeScript | MIT / Apache-2.0 |
| Electron | MIT (bundles Chromium: BSD-3-Clause and others) |
| ffmpeg (vendored binary) | LGPL-2.1 or GPL-2.0 depending on build flags — **build the LGPL configuration and document the flags** |

Two entries above need a decision rather than just a confirmation: `madmom`'s
research clause (an ONNX beat model avoids it, which is why Section 1.4 prefers one)
and the `ffmpeg` build configuration.
