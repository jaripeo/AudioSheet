# AudioSheet

Turn an audio file into playable sheet music or guitar tab, entirely offline, with a
three-position difficulty slider.

The design is specified in [ARCHITECTURE.md](ARCHITECTURE.md). That document is
normative: it defines the nine-stage pipeline, the difficulty engine, the
`ScoreDocument` contract, the tech stack, and a phased implementation plan.

**Current state: Phase 0 (foundation and contracts) complete.** The module tree,
the schema and its generator, the pipeline DAG, the validation gates, and the
toolchain are in place. No audio is processed yet — Phase 1 begins that.

## Requirements

- `python3` (any 3.9+; the pinned CPython 3.11 is installed for you)
- `make`
- Network access for the first `make bootstrap` only

Node, pnpm, `uv` and CPython 3.11 are all installed into the project by
`make bootstrap`; nothing is required system-wide. Set
`AUDIOSHEET_USE_SYSTEM_NODE=1` to use a Node you already have.

## Getting started

```bash
make bootstrap   # once, needs network
make gate        # schema drift, lint, types, tests, fixture, model manifest
```

Every target other than `bootstrap` runs with no network access, which is INV-1
(offline) applied to the build as well as the product.

## Common targets

| Target | What it does |
| --- | --- |
| `make gate` | The full phase exit gate |
| `make test` | pytest + vitest |
| `make lint` | ruff, mypy --strict, tsc, eslint |
| `make schema` | Regenerate the JSON Schema and Pydantic models from the TypeScript |
| `make schema-check` | Fail if the generated artefacts have drifted |
| `make validate-fixture` | Run the S6 gate over the hand-authored fixture |
| `make format` | Apply ruff and eslint autofixes |
| `make clean` | Remove build output, keep the toolchain |
| `make help` | List every target |

## Layout

```
core/          Python 3.11 DSP/ML core (stages S0-S6) and the loopback service
packages/      TypeScript: schema, difficulty engine (S7), renderers (S8), playback
apps/          Electron shell and the React UI
models/        Vendored model weights, verified by sha256 on startup
scripts/       Code generation, model verification, fixtures, benchmarks
docs/adr/      Architecture decision records
```

## Where the source of truth lives

`packages/schema/src/*.ts` defines every inter-stage contract. Both
`packages/schema/schema/score-document.schema.json` and
`core/audiosheet/schema/*.py` are **generated** from it by `scripts/gen_schema.py`
and must not be hand-edited — run `make schema`. CI fails on drift.

## Offline guarantee

No stage may open a network socket. Models, fonts and soundfonts are vendored at
build time, and the runtime fails closed (`E_MODEL_MISSING`) rather than attempting
a download. The desktop shell enforces this with a Content Security Policy that has
no `connect-src` beyond `self`; the browser target enforces it again in a Service
Worker. Two independent layers, because "this works offline" is a promise.
