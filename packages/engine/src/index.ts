/**
 * @audiosheet/engine — the S7 difficulty engine (ARCHITECTURE.md Section 2).
 *
 * `reduce` is pure, total and monotone: every Simple note's origin_ids are a
 * subset of Medium's, which are a subset of Complex's (INV-6, test T-DIFF-MONO).
 * It runs client-side in a Web Worker with no ML inference and no audio access,
 * which is what makes the 400 ms slider budget achievable (INV-7).
 */

import type { DifficultyLevel, DifficultyProfile, ScoreDocument } from "@audiosheet/schema";
import profileData from "./profiles.json" with { type: "json" };
import { runPipeline } from "./pipeline";

export * from "./pipeline";
export * from "./salience";
export * from "./density";
export * from "./polyphony";
export * from "./quantize";
export * from "./mergeTie";
export * from "./range";
export * from "./keySimplify";
export * from "./drums";
export * from "./voiceLeading";
export * from "./flags";
export * from "./validate";

/**
 * The three normative profiles, keyed by level (Section 2.0).
 *
 * Typed as Partial because the value is parsed from JSON: the type assertion is a
 * claim about the file, not a guarantee, so `profileFor` verifies it at the point
 * of use rather than trusting the cast.
 */
export const PROFILES = profileData.profiles as unknown as Readonly<
  Partial<Record<DifficultyLevel, DifficultyProfile>>
>;

/** Return the normative profile for a difficulty level. */
export function profileFor(level: DifficultyLevel): DifficultyProfile {
  const profile = PROFILES[level];
  if (profile === undefined) {
    throw new Error(`unknown difficulty level: ${level}`);
  }
  return profile;
}

/**
 * Reduce a canonical document to the given difficulty.
 *
 * @param doc - The canonical Complex-difficulty document from S6.
 * @param profile - The target profile.
 * @returns A new document; the input is never mutated (INV-3).
 */
export function reduce(doc: ScoreDocument, profile: DifficultyProfile): ScoreDocument {
  return runPipeline(doc, profile);
}
