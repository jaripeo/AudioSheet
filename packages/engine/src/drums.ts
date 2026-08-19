/**
 * Drum reduction — ARCHITECTURE.md Section 2.1.7.
 */

import type { DifficultyProfile, Note } from "@audiosheet/schema";

/** Where an excluded kit piece is folded when the profile omits it. */
export const KIT_FALLBACKS: Record<string, string> = {
  tom_hi: "snare",
  tom_mid: "snare",
  tom_lo: "snare",
  ride: "closed_hat",
  crash: "closed_hat",
  open_hat: "closed_hat",
};

/** Simultaneous percussion notes allowed at Simple: one stem up, one down. */
export const SIMPLE_MAX_SIMULTANEOUS = 2;

/**
 * Reduce a percussion part to the profile's kit subset.
 *
 * @param notes - Percussion notes, pitched by the GM key map.
 * @param profile - Supplies `drum_kit_subset`.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function reduceDrums(notes: readonly Note[], profile: DifficultyProfile): Note[] {
  throw new Error("unimplemented: drum reduction lands in Phase 2");
}
