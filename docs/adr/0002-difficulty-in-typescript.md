# ADR 0002: The difficulty engine lives in TypeScript

- Status: accepted
- Date: 2026-08-18
- Relates to: ARCHITECTURE.md Sections 2.0, 2.4, 4.1; INV-6, INV-7

## Context

The difficulty slider must repaint within 400 ms p95 for a four-minute score
(INV-7). The obvious implementation puts `reduce` next to the models in Python and
has the UI ask the sidecar. That costs a round-trip, a JSON encode of a document
that can reach several megabytes, and a decode — before any musical work starts.

`reduce` is also pure symbolic logic. It reads a `ScoreDocument` and a
`DifficultyProfile` and writes a `ScoreDocument`. It needs no model, no audio, and
no filesystem.

## Decision

`reduce` is implemented in TypeScript in `packages/engine` and runs in a Web
Worker. The canonical Complex document is fetched from the sidecar once and
retained (INV-6); Simple and Medium are derived client-side and memoised by
`(fingerprint, profile id)` in an LRU of 8.

## Consequences

- Moving the slider never touches the sidecar and never re-runs a model.
- The browser-only target gets the difficulty engine for free.
- The rhythm quantiser exists twice: `symbolic/quantize.py` for S5 at Complex
  settings, and `engine/src/quantize.ts` for S7 at profile settings. This is the
  real cost of the decision. It is contained by a shared golden-vector suite in
  `core/tests/golden/quantize/`, consumed by both `pytest` and `vitest`, so the
  two implementations cannot drift silently. Phase 6 populates it.
- The S6 invariants also exist twice, for the same reason (step 14 of `reduce`
  re-runs them). Both ports are checked against the same fixtures.
