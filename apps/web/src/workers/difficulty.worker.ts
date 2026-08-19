/**
 * Difficulty worker — ARCHITECTURE.md Sections 2.4 and 4.3, Phase 2.
 *
 * INV-6 and INV-7 live here: `reduce` runs off the main thread so a slider move
 * repaints within 400 ms p95 without touching a model or the audio.
 */

import type { DifficultyProfile, ScoreDocument } from "@audiosheet/schema";

/** Request sent to the worker. */
export interface ReduceRequest {
  readonly canonical: ScoreDocument;
  readonly profile: DifficultyProfile;
}

/** Reply from the worker. */
export interface ReduceResponse {
  readonly document: ScoreDocument;
  readonly elapsedMs: number;
}

/**
 * Install the message handler.
 *
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function registerWorker(): void {
  throw new Error("unimplemented: the difficulty worker lands in Phase 2");
}
