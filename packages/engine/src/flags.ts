/**
 * Difficulty flag annotation — ARCHITECTURE.md Section 3.5.
 *
 * Flags are how the UI answers "why is this note here, and what did I lose?".
 */

import type { DifficultyFlags, DifficultyLevel } from "@audiosheet/schema";

/** Notes below this confidence are flagged for UI highlighting. */
export const LOW_CONFIDENCE_THRESHOLD = 0.35;

/**
 * Return the neutral flag set for a level: nothing dropped, nothing rewritten.
 *
 * @param level - The difficulty level being produced.
 */
export function neutralFlags(level: DifficultyLevel): DifficultyFlags {
  return {
    level,
    dropped: false,
    drop_reason: null,
    quantized: false,
    quantize_shift_ticks: 0,
    merged_count: 1,
    simplified_from_chord: false,
    arpeggio_collapsed: false,
    octave_shifted: 0,
    transposed: 0,
    swing_flattened: false,
    ornament_stripped: false,
    tuplet_removed: false,
    tab_relaxed: false,
    synthetic: false,
    confidence_low: false,
  };
}

/**
 * Return `flags` with `confidence_low` resolved from a confidence value.
 *
 * @param flags - The flags to update.
 * @param confidence - Transcription confidence in [0, 1].
 */
export function withConfidence(flags: DifficultyFlags, confidence: number): DifficultyFlags {
  return { ...flags, confidence_low: confidence < LOW_CONFIDENCE_THRESHOLD };
}
