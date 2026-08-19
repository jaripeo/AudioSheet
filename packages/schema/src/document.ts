/**
 * The root document — ARCHITECTURE.md Section 3.6.
 *
 * INV-4 (Single source of truth): ScoreDocument is the only inter-stage
 * contract. MusicXML and MIDI are exports, never intermediates.
 */

import type { Ticks, Seconds, TimingGrid } from "./timing";
import type { DifficultyProfile } from "./difficulty";
import type { Part } from "./part";

export type SourceFormat = "mp3" | "wav";

export type Mode = "major" | "minor";

export type Device = "cpu" | "cuda" | "mps" | "wasm";

export type RenderTarget = "sheet" | "tab" | "both";

export type PageSize = "letter" | "a4" | "screen";

export interface SourceInfo {
  filename: string;
  sha256: string;
  format: SourceFormat;
  duration_s: Seconds;
  /** @integer @minimum 1 */
  sample_rate: number;
  /** @integer @minimum 1 @maximum 2 */
  channels: number;
  /** Loudness-normalisation gain applied at S0. */
  gain_db: number;
  /** Encoder-delay samples stripped at S0. @integer @minimum 0 */
  trim_samples: number;
  leading_silence_s: Seconds;
}

export interface KeyRegion {
  tick_on: Ticks;
  tick_off: Ticks;
  /** @integer @minimum 0 @maximum 11 */
  tonic_pc: number;
  mode: Mode;
  /** MusicXML key signature. @integer @minimum -7 @maximum 7 */
  fifths: number;
  /** @minimum 0 @maximum 1 */
  confidence: number;
}

export interface KeyEstimate {
  /** @integer @minimum 0 @maximum 11 */
  tonic_pc: number;
  mode: Mode;
  /** MusicXML key signature. @integer @minimum -7 @maximum 7 */
  fifths: number;
  /** @minimum 0 @maximum 1 */
  confidence: number;
  regions: KeyRegion[];
}

export interface Transposition {
  /** @integer */
  semitones: number;
  as_capo: boolean;
}

export interface RenderDirectives {
  target: RenderTarget;
  /** Renderer hints; empty means auto. */
  system_breaks: Ticks[];
  /** @integer @minimum 1 */
  measures_per_system: number | null;
  page_size: PageSize;
  /** Draw flags.dropped notes faintly. */
  show_ghost_notes: boolean;
}

export interface ModelRecord {
  name: string;
  version: string;
  sha256: string;
  license: string;
}

export interface ProcessingStep {
  /** e.g. "S3.basic_pitch". */
  stage: string;
  version: string;
  /** @minimum 0 */
  duration_ms: number;
  device: Device;
  params_hash: string;
  warnings: string[];
}

export interface Provenance {
  app_version: string;
  models: ModelRecord[];
  steps: ProcessingStep[];
  /** ISO-8601, UTC. */
  created_at_utc: string;
  /** AUDIOSHEET_SEED (INV-2). @integer */
  seed: number;
}

export interface Diagnostic {
  /** An E_* or W_* code from the registry in Appendix 5.4. */
  code: string;
  message: string;
  tick: Ticks | null;
}

export interface DocumentStats {
  /** @integer @minimum 0 */
  raw_note_count: number;
  /** @integer @minimum 0 */
  rendered_note_count: number;
  /** @integer @minimum 0 */
  dropped_note_count: number;
  mean_quantize_shift_ticks: number;
  /** @minimum 0 @maximum 1 */
  mean_confidence: number;
  /** Transcription time resolution; 11.61 ms for basic-pitch. @minimum 0 */
  transcription_frame_ms: number;
}

export interface Diagnostics {
  errors: Diagnostic[];
  warnings: Diagnostic[];
  stats: DocumentStats;
}

export interface ScoreDocument {
  schema_version: "1.0.0";
  id: string;
  /** BLAKE3 over the audio hash and every stage fingerprint. */
  fingerprint: string;
  source: SourceInfo;
  timing: TimingGrid;
  key: KeyEstimate;
  transposition: Transposition | null;
  difficulty: DifficultyProfile;
  parts: Part[];
  render: RenderDirectives;
  provenance: Provenance;
  diagnostics: Diagnostics;
}
