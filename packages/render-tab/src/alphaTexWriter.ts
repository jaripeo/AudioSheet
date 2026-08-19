/**
 * alphaTex writer — ARCHITECTURE.md Section 4.4.
 *
 * The fallback import path, for percussion articulations and bend curves that
 * MusicXML round-trips poorly.
 */

import type { ScoreDocument } from "@audiosheet/schema";

/**
 * Serialise a document to alphaTex.
 *
 * @param doc - The reduced document.
 * @throws Always in Phase 2; the writer lands with the adapter.
 */
export function toAlphaTex(doc: ScoreDocument): string {
  throw new Error("unimplemented: the alphaTex writer lands in Phase 2");
}
