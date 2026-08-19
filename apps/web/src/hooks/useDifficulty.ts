/**
 * Difficulty slider binding: checks the LRU memo, runs reduce() in the worker on a miss, and diffs the result against the displayed notes by origin_ids so only changed notes animate (Section 2.4).
 *
 * Phase 2 implements this (ARCHITECTURE.md Section 5.3).
 */

/**
 * Return the current level, the displayed document, and a setter.
 *
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function useDifficulty(): never {
  throw new Error("unimplemented: useDifficulty lands in Phase 2");
}
