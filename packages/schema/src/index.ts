/**
 * @audiosheet/schema — the single source of truth for every inter-stage
 * contract in AudioSheet (ARCHITECTURE.md Section 3, INV-4).
 *
 * scripts/gen_schema.py reads the type declarations in this directory and
 * generates BOTH packages/schema/schema/score-document.schema.json AND
 * core/audiosheet/schema/*.py. Neither generated artefact may be hand-edited.
 */

export * from "./timing";
export * from "./note";
export * from "./chord";
export * from "./part";
export * from "./difficulty";
export * from "./document";
export * from "./gridTable";
