# ADR 0001: ONNX Runtime at runtime, PyTorch only for Demucs

- Status: accepted
- Date: 2026-08-18
- Relates to: ARCHITECTURE.md Section 4.2

## Context

The pipeline runs six models. Shipping a full PyTorch stack to end users costs
roughly 2 GB installed, drags in a CUDA/MPS dependency matrix, and starts slowly.
ONNX Runtime is small, fast to start, and gives native execution providers on all
three desktop platforms plus a WASM build for the browser target.

Demucs v4 (`htdemucs_6s`) is the exception. Its hybrid transformer runs a
complex-spectrogram branch with dynamic shapes that ONNX export handles poorly.
Forcing an export risks silent accuracy regressions in the stage the whole
transcription depends on — a bad stem makes every downstream number worse.

## Decision

Runtime inference uses ONNX Runtime. PyTorch appears only in
`scripts/convert_models.py` (development-time conversion) and in
`core/audiosheet/separation/demucs_runner.py`, which is the single module in the
shipped application permitted to import `torch`.

## Consequences

- The desktop bundle carries `torch` for one stage. Accepted.
- The browser target cannot separate at all, and transcribes the full mix with a
  `W_SEPARATION_SKIPPED` warning. Accepted: WASM Demucs is 10-20x realtime.
- A future CoreML or ONNX port of Demucs is a one-file change, because nothing
  outside `separation/` knows PyTorch exists. This isolation is the point of the
  decision, not a side effect.
- `shifts` is pinned to 0. Random-shift averaging buys a fraction of a dB of SDR
  and breaks INV-2, which is not a trade worth making.
