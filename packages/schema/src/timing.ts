/**
 * Timing primitives — ARCHITECTURE.md Section 3.1.
 *
 * INV-5 (Time is dual-encoded): every temporal value exists in both seconds
 * (float64, source-of-truth for audio alignment) and ticks (int, PPQ 960,
 * source-of-truth for notation). Conversion goes through TempoMap only.
 *
 * Generator annotations recognised by scripts/gen_schema.py:
 *   @integer          emit an integral type (JSON Schema "integer", Python int)
 *   @minimum <n>      inclusive lower bound
 *   @maximum <n>      inclusive upper bound
 */

/** Notation-domain time. @integer */
export type Ticks = number;

/** Audio-domain time, absolute from the start of the decoded, untrimmed audio. */
export type Seconds = number;

export interface TempoEvent {
  tick: Ticks;
  time_s: Seconds;
  /** Quarter-notes per minute. @minimum 1 @maximum 600 */
  bpm: number;
  /** @minimum 0 @maximum 1 */
  confidence: number;
}

export interface TimeSignatureEvent {
  tick: Ticks;
  time_s: Seconds;
  /** @integer */
  measure_index: number;
  /** @integer @minimum 1 */
  numerator: number;
  /** Power of two. @integer @minimum 1 */
  denominator: number;
  /** @minimum 0 @maximum 1 */
  confidence: number;
}

export interface Beat {
  tick: Ticks;
  time_s: Seconds;
  /** 1-based. @integer @minimum 1 */
  beat_in_bar: number;
  is_downbeat: boolean;
  /** @minimum 0 @maximum 1 */
  confidence: number;
}

export interface SwingSpec {
  enabled: boolean;
  /** 2.0 = triplet swing; 1.0 = straight. @minimum 1 @maximum 3 */
  ratio: number;
  subdivision: 8 | 16;
}

export interface Measure {
  /** 0-based; a pickup measure is index 0 with implicit = true. @integer */
  index: number;
  tick_start: Ticks;
  /** Exclusive. */
  tick_end: Ticks;
  time_start_s: Seconds;
  time_end_s: Seconds;
  /** Index into TimingGrid.time_signatures. @integer @minimum 0 */
  time_signature_ref: number;
  /** Pickup / partial measure. */
  implicit: boolean;
}

/** The timing grid: the only legal bridge between seconds and ticks (INV-5). */
export interface TimingGrid {
  ppq: 960;
  /** >= 1 entry, sorted by tick, first tick == 0. */
  tempo_map: TempoEvent[];
  /** >= 1 entry, sorted by tick, first tick == 0. */
  time_signatures: TimeSignatureEvent[];
  beats: Beat[];
  /** Contiguous and gapless from tick 0. */
  measures: Measure[];
  swing: SwingSpec;
  /** Length of the pickup; 0 if none. */
  anacrusis_ticks: Ticks;
  first_downbeat_s: Seconds;
  /** @minimum 0 @maximum 1 */
  meter_confidence: number;
  tempo_octave_corrected: boolean;
}
