# ADR 0004: The schema generator is pure Python

- Status: accepted
- Date: 2026-08-18
- Relates to: ARCHITECTURE.md Sections 3 and 3.7

## Context

`packages/schema/src/*.ts` is the single source of truth for every inter-stage
contract (INV-4), and both downstream artefacts are generated from it: the JSON
Schema used at the S6 gate, and the Pydantic models the Python core uses.

Section 3.7 names `ts-json-schema-generator` as the tool. That works, but it makes
the Python core's type definitions depend on a Node toolchain: `make schema` — and
therefore any Python-only checkout, and the schema-drift CI step — cannot run
without `node_modules` installed. It also only produces half the output; the
Pydantic side needs a second generator with its own conventions.

## Decision

`scripts/gen_schema.py` parses the TypeScript directly and emits both artefacts.
The parsed subset is deliberately small — type aliases, interfaces, literal unions,
arrays, tuples, parenthesised and nullable types — and the schema sources are written
to stay inside it. Numeric refinements the TypeScript type system cannot express
(integrality, bounds) are carried as `@integer`, `@minimum` and `@maximum` annotations
in doc comments.

## Consequences

- One generator, one pass, two artefacts, no cross-ecosystem build dependency.
- The parser is ours to maintain. Contained by the narrow subset and by
  `make schema-check`, which fails CI on any drift; a construct the parser cannot
  handle fails loudly at generation time rather than producing wrong output.
- The annotations are a small dialect a reader has to learn. Documented at the top
  of `timing.ts` and in the generator's own docstring.
- Every generated model lives in `core/audiosheet/schema/score_document.py`, with
  `timing.py`, `note.py`, `chord.py` and `difficulty.py` re-exporting their slice.
  The TypeScript modules are mutually dependent (`note` needs `DifficultyFlags`,
  `difficulty` needs `TabTechnique`), which would be an import cycle if each
  generated its own module. One module plus thin re-exports avoids it without
  changing the public import paths.
