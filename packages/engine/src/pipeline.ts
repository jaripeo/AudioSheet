/**
 * The fourteen ordered steps of `reduce` — ARCHITECTURE.md Section 2.0.
 *
 * The order is normative. Steps 1-8 land in Phase 2; steps 9-13 in Phase 7;
 * step 14 re-runs the S6 validators and is available from Phase 0.
 */

import type { DifficultyProfile, ScoreDocument } from "@audiosheet/schema";

/** One named step of the reduce pipeline. */
export interface ReduceStep {
  readonly name: string;
  readonly phase: number;
  readonly apply: (doc: ScoreDocument, profile: DifficultyProfile) => ScoreDocument;
}

/** The normative step order (Section 2.0). */
export const STEP_ORDER = [
  "select_parts",
  "score_salience",
  "collapse_polyphony",
  "reduce_density",
  "quantize_rhythm",
  "merge_and_tie",
  "constrain_range",
  "simplify_key",
  "assign_voices",
  "voice_chords",
  "optimize_fretboard",
  "apply_techniques",
  "annotate_flags",
  "revalidate",
] as const;

export type StepName = (typeof STEP_ORDER)[number];

/**
 * Run every step in order.
 *
 * @param doc - The canonical document.
 * @param profile - The target profile.
 * @returns The reduced document.
 * @throws Always in Phase 0; steps 1-8 arrive in Phase 2 (Section 5.3).
 */
export function runPipeline(doc: ScoreDocument, profile: DifficultyProfile): ScoreDocument {
  throw new Error("unimplemented: reduce pipeline steps 1-8 land in Phase 2");
}
