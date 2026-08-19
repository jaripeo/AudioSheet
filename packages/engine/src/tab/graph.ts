/**
 * The layered fretboard DAG — ARCHITECTURE.md Section 2.3.1.
 *
 * One layer per note; nodes are every playable (string, fret) inside the profile's
 * window. An empty layer triggers relaxation: widen the window, then octave-fold
 * the pitch, then drop the note with `E_TAB_UNPLAYABLE` recorded as a warning.
 */

import type { DifficultyProfile, Note, Tuning } from "@audiosheet/schema";
import type { TabNode } from "./costs";

/** The relaxation ladder applied when a layer comes out empty. */
export const RELAXATION_STEPS = ["widen_window", "octave_fold", "drop_note"] as const;

export type RelaxationStep = (typeof RELAXATION_STEPS)[number];

/** One layer of the DAG. */
export interface TabLayer {
  readonly note: Note;
  readonly nodes: readonly TabNode[];
  readonly relaxation: RelaxationStep | null;
}

/**
 * Build the layered graph for a monophonic reduction.
 *
 * @param notes - Notes in onset order; chord frames are contracted upstream.
 * @param tuning - The part's tuning.
 * @param profile - Supplies the fret window.
 * @throws Always in Phase 0; lands in Phase 7.
 */
export function buildGraph(
  notes: readonly Note[],
  tuning: Tuning,
  profile: DifficultyProfile,
): TabLayer[] {
  throw new Error("unimplemented: fretboard graph construction lands in Phase 7");
}
