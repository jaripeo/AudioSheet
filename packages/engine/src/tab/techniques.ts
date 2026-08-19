/**
 * Technique inference — ARCHITECTURE.md Section 2.3.5, step 2.
 *
 * Only techniques the profile admits are emitted.
 */

import type { DifficultyProfile, Note, TabTechnique } from "@audiosheet/schema";
import type { TabNode } from "./costs";

/** Fret distance range that reads as a hammer-on or pull-off. */
export const LEGATO_FRET_RANGE: readonly [number, number] = [1, 3];

/** Maximum gap for a hammer-on or pull-off, in seconds. */
export const LEGATO_MAX_GAP_S = 0.06;

/** Cents rise that reads as a bend. */
export const BEND_MIN_CENTS = 80;

/**
 * Infer techniques for consecutive placements.
 *
 * @param from - The previous note and placement.
 * @param to - The next note and placement.
 * @param profile - Supplies `guitar_techniques`.
 * @throws Always in Phase 0; lands in Phase 7.
 */
export function inferTechniques(
  from: { note: Note; node: TabNode },
  to: { note: Note; node: TabNode },
  profile: DifficultyProfile,
): TabTechnique[] {
  throw new Error("unimplemented: technique inference lands in Phase 7");
}

/**
 * Quantise a bend to the nearest half step.
 *
 * @param peakCents - Peak deviation, in cents.
 * @returns The bend depth in semitones, rounded to 0.5.
 */
export function bendSemitones(peakCents: number): number {
  return Math.round((peakCents / 100) * 2) / 2;
}
