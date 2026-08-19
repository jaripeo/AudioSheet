# Shared quantiser golden vectors

The rhythm quantiser of ARCHITECTURE.md Section 2.1.3 is implemented twice, on
purpose: `core/audiosheet/symbolic/quantize.py` runs at S5 next to the models, and
`packages/engine/src/quantize.ts` runs at S7 next to the difficulty slider
(see `docs/adr/0002-difficulty-in-typescript.md`).

The vectors in this directory are the contract that stops the two implementations
drifting. They are consumed by **both** `pytest` and `vitest`, and Gate G6 requires
exact agreement on every one.

## Format

Each vector is a JSON file:

```json
{
  "name": "swung-eighths-at-92bpm",
  "description": "why this case exists and what it is guarding against",
  "grid": { "...": "a TimingGrid" },
  "profile_level": "medium",
  "input_onsets_s": [0.0, 0.31, 0.65],
  "expected_ticks": [0, 320, 640],
  "expected_dropped_ids": []
}
```

Phase 6 populates this directory. It is empty in Phase 0 by design: writing the
vectors before the DP exists would fix expectations that have not been reasoned
about.
