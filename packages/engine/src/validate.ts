/**
 * Step 14 of `reduce`: re-run the S6 invariants — ARCHITECTURE.md Sections 1.9
 * and 2.0.
 *
 * The TypeScript port of `core/audiosheet/validate/invariants.py`. A failure means
 * the engine produced an invalid document, which surfaces as `E_DIFF_INVALID` and
 * makes the UI fall back to the previous valid level.
 */

import type { ScoreDocument } from "@audiosheet/schema";

/** The invariants this module enforces, in document order. */
export const INVARIANTS = ["V-1", "V-2", "V-3", "V-4", "V-5", "V-6", "V-7"] as const;

export type InvariantId = (typeof INVARIANTS)[number];

/** One invariant failure. */
export interface InvariantFailure {
  readonly invariant: InvariantId;
  readonly message: string;
  readonly tick: number | null;
}

/**
 * Run every invariant and return the failures found.
 *
 * Unlike the Python gate this collects rather than throws, because the UI wants
 * to show everything that is wrong with a reduction at once.
 *
 * @param doc - The reduced document.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function checkInvariants(doc: ScoreDocument): InvariantFailure[] {
  throw new Error("unimplemented: the TypeScript invariant port lands in Phase 2");
}
