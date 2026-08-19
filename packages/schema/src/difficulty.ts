/**
 * Difficulty flags and profiles — ARCHITECTURE.md Section 3.5.
 *
 * INV-6 (Difficulty is non-destructive): reduce(ScoreDocument, DifficultyProfile)
 * is a pure function. The Complex document is always retained; Simple and Medium
 * are recomputed on slider change without re-running any ML model.
 */

import type { Ticks } from "./timing";
import type { TabTechnique } from "./note";

export type DifficultyLevel = "simple" | "medium" | "complex";

export type DropReason =
  | "density_budget"
  | "polyphony_cap"
  | "below_min_duration"
  | "voice_cap"
  | "unplayable"
  | "kit_subset"
  | "ornament";

export type SwingNotation = "flatten" | "directive" | "literal";

/**
 * How ornaments (trills, mordents, grace notes) are treated. Section 2.0's
 * profile table lists this parameter; Section 3.5's interface omitted it, so it
 * is added here — dropping it would lose normative information.
 */
export type OrnamentPolicy = "strip" | "grace_only" | "all";

export interface DifficultyFlags {
  level: DifficultyLevel;
  dropped: boolean;
  drop_reason: DropReason | null;
  quantized: boolean;
  /** Signed magnitude of the applied snap. @integer */
  quantize_shift_ticks: number;
  /** How many source notes collapsed into this one. @integer @minimum 0 */
  merged_count: number;
  simplified_from_chord: boolean;
  arpeggio_collapsed: boolean;
  /** Semitones; a multiple of 12. @integer */
  octave_shifted: number;
  /** Semitones from global key simplification. @integer */
  transposed: number;
  swing_flattened: boolean;
  ornament_stripped: boolean;
  tuplet_removed: boolean;
  /** The guitar fret window had to be widened to place this note. */
  tab_relaxed: boolean;
  /** Engine-inserted, not audio-derived. */
  synthetic: boolean;
  /** confidence < 0.35; the UI highlights these. */
  confidence_low: boolean;
}

export interface QuantizeWeights {
  /** Fidelity: timing error in grid units. */
  alpha: number;
  /** Syncopation penalty. */
  beta: number;
  /**
   * Tuplet penalty. The architecture states Infinity at Simple; because JSON
   * cannot carry Infinity, Simple uses a large finite value and the authoritative
   * gate on tuplets is the empty allow_tuplets list.
   */
  gamma: number;
  /** Grid-switch penalty. */
  delta: number;
}

export interface SalienceWeights {
  conf: number;
  metric: number;
  dur: number;
  pitch: number;
  energy: number;
  contour: number;
  harm: number;
}

export interface TabWeights {
  k_fret: number;
  k_open: number;
  k_string: number;
  k_high: number;
  k_move: number;
  k_shift: number;
  k_stringJump: number;
  k_legato: number;
  k_time: number;
  k_cross: number;
}

export interface DifficultyProfile {
  /** "simple" | "medium" | "complex" | a custom ULID. */
  id: string;
  level: DifficultyLevel;
  label: string;
  /** Subdivisions per quarter note. @integer @minimum 1 */
  grid_divisions: number;
  /** Permitted tuplet actual-counts, e.g. [3, 5, 6, 7]. @integer @minimum 2 */
  allow_tuplets: number[];
  swing_notation: SwingNotation;
  min_note_duration_ticks: Ticks;
  quantize_weights: QuantizeWeights;
  /** Notes per second, per part; null means unrestricted. @minimum 0 */
  note_budget_nps: number | null;
  /** @integer @minimum 1 */
  max_simultaneous_notes: number;
  /** @integer @minimum 1 */
  max_voices: number;
  /** @integer @minimum 1 */
  chord_max_notes: number;
  /** Scale degrees, most-important first, e.g. [1, 3, 7, 5]. @integer @minimum 1 @maximum 13 */
  chord_tone_priority: number[];
  salience_weights: SalienceWeights;
  /** null = unrestricted. @integer @minimum 1 */
  pitch_range_semitones: number | null;
  /** null = unrestricted. @integer @minimum 0 @maximum 7 */
  max_accidentals_in_key: number | null;
  allow_transposition: boolean;
  prefer_capo: boolean;
  /** Inclusive [lo, hi] fret bounds. @integer @minimum 0 @maximum 24 */
  guitar_fret_window: [number, number];
  /** @integer @minimum 1 */
  guitar_max_span: number;
  /** @integer @minimum 1 @maximum 12 */
  guitar_max_strings_per_chord: number;
  guitar_allow_barre: boolean;
  /** Section 2.0 lists this parameter; true at every level, preferred at Simple. */
  guitar_allow_open_strings: boolean;
  guitar_techniques: TabTechnique[];
  tab_weights: TabWeights;
  /** null means every present part. @integer @minimum 1 */
  parts_max: number | null;
  drum_kit_subset: string[];
  ornaments: OrnamentPolicy;
  /**
   * Whether dynamics are notated at all. The vocabulary is a function of `level`:
   * Medium emits p/mf/f only, Complex adds the full range plus hairpins
   * (Section 2.0), so no separate granularity field is needed.
   */
  show_dynamics: boolean;
  show_fingerings: boolean;
  show_chord_diagrams: boolean;
  use_repeat_signs: boolean;
}
