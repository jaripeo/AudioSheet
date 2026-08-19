# Hand-authored fixtures

`ScoreDocument`s written by hand, not produced by the pipeline. They exist so the
schema gate and the V-1..V-7 invariants can be tested before any stage that
generates a document exists (ARCHITECTURE.md Section 5.3, Phase 0 step 6).

## `simple_scale.json`

A two-measure C major scale, eight quarter notes at 120 BPM in 4/4, on one
`standard+tab` guitar part in standard tuning, plus one open-C chord event with its
voicing.

Chosen to exercise the parts of the contract that are easiest to get wrong:

- **V-6** — 120 BPM makes the tick/seconds relationship exact (a quarter note is
  0.5 s, tick 960), so a drift bug shows up rather than hiding in float noise.
- **V-7** — every note carries a `(string, fret)` that genuinely sounds its pitch on
  standard tuning, so the validator has real arithmetic to check. Notes span two
  strings and include an open string.
- **V-4** — two full 4/4 measures, each exactly at capacity, so an off-by-one in the
  capacity calculation fails.
- `ChordEvent` and `Voicing`, including a muted string (`-1`) and unplayed strings.

### The digests are synthetic

There is no audio file behind this fixture, so `source.sha256` and `fingerprint` are
not digests of any recording. Both are derived deterministically from the ASCII
string `audiosheet:fixture:simple_scale`:

- `source.sha256` = `sha256("audiosheet:fixture:simple_scale")`
- `fingerprint` = `"b3:" + blake3("audiosheet:fixture:simple_scale")[:32]`

They are stable and reproducible, and they are deliberately not plausible as real
audio digests. Phase 1 adds fixtures with real synthesised audio and real digests
(`scripts/make_fixtures.py`).

### Formatting

The file is stored pretty-printed with two-space indent and the key order the schema
declares. `test_fixture_round_trips_byte_identically` asserts both that the file is
already in that stable form and that its canonical form survives a round trip
through the Pydantic models unchanged.
