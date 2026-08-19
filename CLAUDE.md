# CLAUDE.md — AudioSheet

Offline audio → sheet music / guitar tab, with a Simple/Medium/Complex slider.

- `ARCHITECTURE.md` is the **normative** spec. Read the relevant section before coding.
- Work strictly phase-by-phase per `ARCHITECTURE.md` §5.3. Record results in `docs/gates.md`.
- **State: Phase 0 complete (Gate G0 passed). Phase 1 is next. Do not skip ahead.**

## Stack

- Python **3.11** (pinned; managed by `uv`) — DSP/ML core in `core/`, stages S0–S6.
- Node **24** + **TypeScript 5.6** — `packages/` (schema, S7 engine, S8 renderers), `apps/`.
- pnpm 9 workspace. Lint: `ruff` + `mypy --strict`, `eslint` + `tsc`. Test: `pytest`, `vitest`.
- Toolchain is project-local: `.tooling/bin` (uv, node, npm, pnpm), `core/.venv` (Python 3.11).

## Validation commands

- Run **in this order, always**:
  - `make lint` — ruff, `ruff format --check`, `mypy --strict` (core + scripts), `tsc --build`, eslint.
  - `make test` — `pytest` (core) then `vitest` (packages).
- `make gate` — full phase exit gate: `schema-check` → `lint` → `test` → `validate-fixture` → `verify-models`.
- `make schema` — regenerate schema artifacts. `make schema-check` — fail on drift.
- `make bootstrap` — **the only target allowed to touch the network.**
- `make format` — ruff + eslint autofixes. `make help` — all targets.
- Everything except `bootstrap` must pass with no network (INV-1). Verify with a dead proxy if unsure.

## Critical architectural deviations (Phase 0 — do not "fix" these)

- **Node via `nodejs-wheel-binaries`** (PyPI wheel), linked into `.tooling/bin` by
  `scripts/link-node.sh`. No brew/nvm in this environment. Set
  `AUDIOSHEET_USE_SYSTEM_NODE=1` to prefer a system Node instead.
- **`scripts/gen_schema.py` is pure Python**, not `ts-json-schema-generator`
  (ADR-0004). It parses a deliberately small TS subset and emits **both** artifacts.
  Keep `packages/schema/src/*.ts` inside that subset.
- **Generated Pydantic models all live in `core/audiosheet/schema/score_document.py`.**
  `timing.py`, `note.py`, `chord.py`, `difficulty.py` are thin re-export shims. This
  avoids the `note` ↔ `difficulty` import cycle. Do not split them.
- **`DifficultyProfile` includes `ornaments` and `guitar_allow_open_strings`.**
  §2.0's table lists them; §3.5's interface omitted them. They are required fields.
- **Measure indexing is 0-based** (`Measure.index`, `TimeSignatureEvent.measure_index`),
  per §3.1. `ARCHITECTURE.md` §3.8's example shows `1` — that example is wrong; the
  0-based convention wins.
- **Guitar techniques use the `TabTechnique` vocabulary**, not §2.0's prose:
  `slide_up`/`slide_down`/`slide_legato` (not `slide`), `natural_harmonic`/
  `pinch_harmonic` (not `harmonic`). `vibrato` and `palm_mute` are `Articulation`s.
- **JSON cannot carry Infinity.** `note_budget_nps`, `parts_max`,
  `pitch_range_semitones`, `max_accidentals_in_key` use `null` for "unrestricted".
  Simple's `quantize_weights.gamma` is `1e9`; the real tuplet gate is `allow_tuplets: []`.
- **`salience_weights` for Complex** copy Medium's (the §2.0 table omits Complex). Must sum to 1.0.
- **`noUnusedParameters: false`** in `tsconfig.base.json` — stub signatures are the
  deliverable. `noUnusedLocals` stays on; eslint covers unused variables.
- **`apps/*` are excluded** from typecheck/lint until Phase 2 (web) and Phase 8 (desktop).
- **All 8 `models/manifest.json` entries are `status: "pending"`.**
  `verify_models.py --strict` is a Phase 8 release gate, not a dev-loop check.

## Prohibitions

- **Never modify `ARCHITECTURE.md`.** It is the contract. Report inconsistencies to the
  user in chat; do not silently edit or "reconcile" them.
- **Never hand-edit the generated schemas.** These files are output only:
  - `core/audiosheet/schema/*.py`
  - `packages/schema/schema/score-document.schema.json`
  - Edit `packages/schema/src/*.ts`, then run `make schema`.
- **Never run tests before linting.** `make lint` first, then `make test`. A type or lint
  error makes test output untrustworthy.
- **Never open a network socket at runtime** (INV-1). No downloads, no fetch, no CDN. A
  missing model fails closed with `E_MODEL_MISSING`.
- **Never introduce nondeterminism** (INV-2). No `random` without `AUDIOSHEET_SEED`, no
  wall-clock in outputs, no `Date.now()`/`Math.random()` in engine logic. Demucs `shifts`
  stays `0`.
- **Never import `torch` outside `core/audiosheet/separation/`** (ADR-0001).
- **Never mutate a stage's input** (INV-3). Return new objects; append to provenance.
- **Never convert seconds ↔ ticks outside the tempo map** (INV-5). Use
  `audiosheet.symbolic.grid.tick_to_seconds` / `seconds_to_tick`.
- **Never parse MusicXML or MIDI as an intermediate** (INV-4). They are exports only.
- **Never add a `raise NotImplementedError` / `throw new Error` without naming its phase.**
  A test enforces this. Bare `TODO`/`FIXME`/`XXX` markers are banned.
- **Never hard-code a normative constant twice.** Each lives in exactly one place:
  `core/audiosheet/config/constants.py`, `config/limits.py`,
  `packages/engine/src/profiles.json`, `packages/engine/src/tab/weights.json`,
  `packages/render-core/src/durations.ts`, `packages/schema/src/gridTable.ts`.
- **Never commit or push unless the user asks.**

## Source of truth

- `packages/schema/src/*.ts` → the `ScoreDocument` contract (INV-4). Generated into
  66 JSON Schema `$defs` + Pydantic models.
- Generator annotations in doc comments: `@integer`, `@minimum <n>`, `@maximum <n>`.
- All fields are **required**; optionality is expressed as `| null`, never omission.
- Ticks: `int`, PPQ **960**. Seconds: `float64`. Both always present (INV-5).

## Invariants (assert, don't assume)

- INV-1 offline · INV-2 deterministic · INV-3 immutable + provenance ·
  INV-4 one contract · INV-5 dual-encoded time · INV-6 pure `reduce` · INV-7 ≤400 ms slider.
- V-1 durations · V-2 no voice overlap · V-3 measures contiguous · V-4 measure capacity ·
  V-5 `origin_ids` resolve · V-6 time round-trip ±2 ms · V-7 tab pitch matches.
- Python: `core/audiosheet/validate/invariants.py`. TS port: `packages/engine/src/validate.ts`.
- Every V-* needs a passing **and** a deliberately-failing test that still satisfies the schema.

## Gotchas

- `pytest` runs with `filterwarnings = ["error"]`. A new warning fails the suite.
- `core/tests/golden/quantize/` is the shared contract between `symbolic/quantize.py` and
  `engine/src/quantize.ts`. Both implementations must agree exactly (Gate G6).
- The hand-authored fixture `core/tests/fixtures/handmade/simple_scale.json` has
  **synthetic** digests derived from `"audiosheet:fixture:simple_scale"`. There is no audio
  behind it. Keep it pretty-printed, 2-space indent.
- Error/warning codes: `core/audiosheet/pipeline/errors.py`. A test asserts the registry
  covers every code documented in `ARCHITECTURE.md` Appendix 5.4.
