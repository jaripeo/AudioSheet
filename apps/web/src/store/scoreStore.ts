/**
 * The score store — ARCHITECTURE.md Sections 4.1 and 2.4, Phase 2.
 *
 * Zustand rather than Redux: the store is one large immutable document with
 * fine-grained selectors, and Zustand's transient updates avoid re-rendering the
 * whole score on every playback tick. Updates are structurally shared so the
 * renderer can diff by reference.
 *
 * The canonical Complex document is always retained (INV-6); Simple and Medium are
 * derived and memoised by (fingerprint, profile id) in an LRU of size
 * DIFFICULTY_MEMO_SIZE.
 */

import type { DifficultyLevel, ScoreDocument } from "@audiosheet/schema";

/** LRU size for memoised reduce() results (Section 2.4). */
export const DIFFICULTY_MEMO_SIZE = 8;

/** What the store holds. */
export interface ScoreState {
  /** The canonical S6 output; never discarded. */
  readonly canonical: ScoreDocument | null;
  /** The level currently displayed. */
  readonly level: DifficultyLevel;
  /** The reduced document for `level`, or null while it is being computed. */
  readonly displayed: ScoreDocument | null;
  /** True while the difficulty worker is running. */
  readonly reducing: boolean;
}

/**
 * Create the store.
 *
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function createScoreStore(): never {
  throw new Error("unimplemented: the score store lands in Phase 2");
}
