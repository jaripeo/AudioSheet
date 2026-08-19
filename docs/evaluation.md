# Evaluation plan

Targets and method for every accuracy gate in ARCHITECTURE.md Section 5.3. The
reference machine and fixture families are defined in Appendix 5.6.

Phase 8 completes this document with measured numbers; Phases 3-7 fill in their own
rows as their gates go green. Nothing here is measured yet — Phase 0 delivers the
harness, not the results.

## Reference machine

Apple M2 Pro, 10-core CPU, 16 GB unified memory, macOS 14, no discrete GPU, Demucs
on `mps`, ONNX on CoreML/CPU. The CI target (4 vCPU / 16 GB Linux x64, CPU-only) is
allowed a **3x wall-clock multiplier** and must meet every accuracy gate identically.

## Fixture families

| Family | What it is | Ground truth |
| --- | --- | --- |
| `handmade/` | Hand-authored `ScoreDocument`s | The file itself |
| `synth/` | WAVs rendered from known MIDI | The source MIDI — exact |
| `timing/` | Metronome, rubato, swing, odd meters, tempo ramps | Generated beat grid |
| `real/` | Clearly-licensed (CC0/CC-BY) recordings | Expert annotation |
| `tab/` | 20 guitar riffs | Expert-authored fingerings |
| `adversarial/` | Silence, DC offset, clipping, 8 kHz-bandlimited MP3, mono-as-stereo, 600 s, single click, white noise | Expected failure mode |

`synth/` is the backbone of every accuracy gate, because its ground truth is the
MIDI the audio was rendered from rather than a human's opinion.

## Targets

| Metric | Gate | Target | Method |
| --- | --- | --- | --- |
| Beat F-measure | G3 | >= 0.90 | `mir_eval.beat`, +/- 70 ms |
| Downbeat F-measure | G3 | >= 0.80 | `mir_eval.beat`, +/- 70 ms |
| Meter accuracy | G3 | >= 0.85 | Exact numerator/denominator match |
| Key accuracy | G3 | >= 0.75 | MIREX-weighted (credit for relative/dominant) |
| Separation SDR | G4 | within 1.0 dB of reference | `museval` on a 5-track held-out set |
| Note F (monophonic) | G5 | >= 0.80 | `mir_eval.transcription` |
| Note F (polyphonic piano) | G5 | >= 0.65 | `mir_eval.transcription` |
| Note F (full mix) | G5 | >= 0.60 | `mir_eval.transcription` |
| Octave-error rate | G5 | <= 3 % | Pitch-class match with octave mismatch |
| Quantisation error | G6 | <= 1/2 finest grid unit | Mean absolute tick shift |
| Pitch-spelling accuracy | G6 | >= 0.95 | Step/alter match against known keys |
| Tab position match | G7 | >= 85 % within +/- 2 frets | Against expert fingerings |
| Position shifts at Simple | G7 | <= 50 % of Complex | Shifts per minute |
| V-1..V-7 violations | every gate | 0 | `check_invariants` over the whole suite |

Note-level F-measure uses onset +/- 50 ms, pitch +/- 50 cents, offset ratio 0.2.

## Performance budgets

| Budget | Target | Enforced by |
| --- | --- | --- |
| Full analysis, 4-minute track | <= 150 s | `scripts/bench.py` |
| Slider re-render (p95) | <= 400 ms | `scripts/bench.py` (INV-7) |
| First paint after analysis | <= 1.5 s | `scripts/bench.py` |
| Peak resident memory | <= 6 GiB | `scripts/bench.py` |
| Installed bundle | <= 900 MB | `electron-builder` output check |

## Determinism

INV-2 is tested directly rather than assumed: `core/tests/test_determinism.py` runs
the pipeline twice and asserts byte-identical cache contents, and checks that
fingerprints and canonical JSON are stable **across processes** (Python randomises
string hashing per process, so an in-process check would not catch a dependency on
it).
