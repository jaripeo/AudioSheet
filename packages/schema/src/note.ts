/**
 * Notes, rests, and tablature positions — ARCHITECTURE.md Section 3.2.
 *
 * INV-3 (Immutability + provenance): every Note carries origin_ids tracing back
 * to the RawNote records emitted by S3/S4, so the UI can always answer
 * "why is this note here?".
 */

import type { Ticks, Seconds } from "./timing";
import type { StemName } from "./part";
import type { DifficultyFlags } from "./difficulty";

export type Accidental =
  | "natural"
  | "sharp"
  | "flat"
  | "double-sharp"
  | "double-flat"
  | "none";

export type Articulation =
  | "staccato"
  | "accent"
  | "tenuto"
  | "marcato"
  | "legato"
  | "vibrato"
  | "harmonic"
  | "palm_mute"
  | "ghost"
  | "dead_note";

export type TabTechnique =
  | "hammer_on"
  | "pull_off"
  | "slide_up"
  | "slide_down"
  | "slide_legato"
  | "bend"
  | "release"
  | "prebend"
  | "tap"
  | "slap"
  | "pop"
  | "natural_harmonic"
  | "pinch_harmonic";

export type NotatedType =
  | "whole"
  | "half"
  | "quarter"
  | "eighth"
  | "16th"
  | "32nd"
  | "64th";

export type Step = "C" | "D" | "E" | "F" | "G" | "A" | "B";

export type Alter = -2 | -1 | 0 | 1 | 2;

export type Dots = 0 | 1 | 2;

export type Finger = 1 | 2 | 3 | 4 | "T" | "barre" | null;

export type TieRole = "none" | "start" | "stop" | "continue";

export type Dynamic = "pp" | "p" | "mp" | "mf" | "f" | "ff";

export type TranscriptionModel = "basic-pitch" | "crepe" | "drum-cnn" | "tabcnn";

export interface DurationRational {
  /** @integer @minimum 1 */
  numerator: number;
  /** @integer @minimum 1 */
  denominator: number;
}

export interface TupletSpec {
  /** Notes actually played in the span. @integer @minimum 2 */
  actual: number;
  /** Notes the span would normally hold. @integer @minimum 1 */
  normal: number;
  /** Nesting depth; one level of nesting is the maximum (Section 2.2.3). */
  level: 1 | 2;
}

export interface SlurRef {
  id: string;
  role: "start" | "stop";
}

export interface TabPosition {
  /** 1 = highest-pitched string (matches MusicXML and AlphaTab). @integer @minimum 1 @maximum 12 */
  string: number;
  /** 0 = open; -1 = muted (chord frames only). @integer @minimum -1 @maximum 24 */
  fret: number;
  finger: Finger;
  is_barre_root: boolean;
  /** Hand position — the fret under the index finger. @integer @minimum 0 @maximum 24 */
  position: number;
}

/** A note event straight out of S3/S4, before any symbolic decision is taken. */
export interface RawNote {
  id: string;
  stem: StemName;
  onset_s: Seconds;
  offset_s: Seconds;
  /** @integer @minimum 0 @maximum 127 */
  midi: number;
  /** Deviation from equal temperament. @minimum -100 @maximum 100 */
  micro_cents: number;
  /** @integer @minimum 1 @maximum 127 */
  velocity: number;
  energy_db: number;
  /** @minimum 0 @maximum 1 */
  confidence: number;
  model: TranscriptionModel;
  octave_corrected: boolean;
}

export interface Note {
  id: string;
  /** RawNote ids (INV-3); empty only for engine-inserted material. */
  origin_ids: string[];
  tick_on: Ticks;
  tick_off: Ticks;
  time_on_s: Seconds;
  time_off_s: Seconds;
  /** Non-null only for tuplet durations that are not integral in ticks. */
  duration_rational: DurationRational | null;
  notated_type: NotatedType;
  dots: Dots;
  tuplet: TupletSpec | null;
  /** @integer @minimum 0 @maximum 127 */
  midi: number;
  step: Step;
  alter: Alter;
  /** Scientific pitch notation; middle C = C4. @integer @minimum -1 @maximum 9 */
  octave: number;
  accidental_display: Accidental;
  /** @minimum -100 @maximum 100 */
  micro_cents: number;
  part_id: string;
  /** 1-based. @integer @minimum 1 */
  staff: number;
  /** 1-based, unique within (part, staff). @integer @minimum 1 */
  voice: number;
  /** MusicXML <chord/>: shares an onset with the previous note. */
  is_chord_member: boolean;
  /** @integer @minimum 1 @maximum 127 */
  velocity: number;
  dynamic: Dynamic | null;
  articulations: Articulation[];
  tie: TieRole;
  slur: SlurRef | null;
  tab: TabPosition | null;
  techniques: TabTechnique[];
  bend_semitones: number | null;
  /** Musical importance, drives note reduction (Section 2.1.1). @minimum 0 @maximum 1 */
  salience: number;
  /** @minimum 0 @maximum 1 */
  confidence: number;
  flags: DifficultyFlags;
  /** false => retained for provenance but not drawn. */
  render: boolean;
}

export interface Rest {
  id: string;
  tick_on: Ticks;
  tick_off: Ticks;
  notated_type: NotatedType;
  dots: Dots;
  part_id: string;
  /** @integer @minimum 1 */
  staff: number;
  /** @integer @minimum 1 */
  voice: number;
  is_multi_measure: boolean;
  /** > 1 only when is_multi_measure. @integer @minimum 1 */
  measure_count: number;
}
