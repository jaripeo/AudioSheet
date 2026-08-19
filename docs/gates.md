# Phase gate log

One row per phase gate from ARCHITECTURE.md Section 5.3. An agent implementing a
phase records its result here before starting the next one. A phase MUST NOT start
while its predecessor's gate is red.

## G0 — Foundation and contracts

Status: **PASSED**

| Requirement | Result |
| --- | --- |
| `make test` green | Pass |
| `make lint` green | Pass |
| Hand-authored document round-trips JSON -> Pydantic -> JSON byte-identically | Pass — `tests/unit/test_schema_generated.py::test_fixture_round_trips_byte_identically` |
| Every V-* validator has a passing **and** a deliberately-failing test | Pass — `tests/unit/test_invariants.py`, V-1 through V-7 |
| `make bootstrap` works offline after the first run | Pass — only `bootstrap` touches the network |

Deviations from the phase text are recorded in `docs/adr/0004-python-schema-generator.md`
and in the Phase 0 handover notes.

## G1 — Ingestion and export skeleton

Status: not started

| Requirement | Result |
| --- | --- |
| Click-track first click within +/- 3 ms of ground truth | — |
| Exported MusicXML validates against the MusicXML 4.0 XSD | — |
| MusicXML opens in MuseScore and imports into AlphaTab | — |

## G2 — Rendering and the difficulty slider

Status: not started

| Requirement | Result |
| --- | --- |
| Slider re-render <= 400 ms p95, 4-minute fixture | — |
| `T-DIFF-MONO` passes | — |
| Zero validator failures at any level | — |

## G3 — Global analysis

Status: not started

| Requirement | Result |
| --- | --- |
| Beat F >= 0.90 | — |
| Downbeat F >= 0.80 | — |
| Meter accuracy >= 0.85 | — |
| Key accuracy >= 0.75 | — |

## G4 — Stem isolation

Status: not started

| Requirement | Result |
| --- | --- |
| SDR within 1.0 dB of reference | — |
| Two runs produce byte-identical stems | — |
| Peak RSS <= 6 GiB on a 6-minute track | — |

## G5 — Transcription

Status: not started

| Requirement | Result |
| --- | --- |
| Note F >= 0.80 mono / 0.65 poly piano / 0.60 full mix | — |
| Octave-error rate <= 3 % | — |
| Every threshold read from config, not literal in code | — |

## G6 — Symbolic consolidation

Status: not started

| Requirement | Result |
| --- | --- |
| Quantisation mean absolute shift <= 1/2 finest grid unit | — |
| Pitch-spelling accuracy >= 0.95 | — |
| Zero V-1..V-7 violations across the fixture suite | — |
| `quantize.py` and `quantize.ts` agree on all shared golden vectors | — |

## G7 — Voicing and fretboard optimisation

Status: not started

| Requirement | Result |
| --- | --- |
| >= 85 % of notes within +/- 2 frets of expert reference | — |
| 100 % of emitted (string, fret) pairs pass V-7 | — |
| Simple position shifts <= 50 % of Complex | — |
| No Simple fret outside [0, 4] or span > 3 | — |

## G8 — Packaging and offline hardening

Status: not started

| Requirement | Result |
| --- | --- |
| All performance budgets met | — |
| Clean-machine install transcribes with no network | — |
| Playwright E2E covers upload -> analyze -> slide -> export | — |
| Every licence verified | — |
