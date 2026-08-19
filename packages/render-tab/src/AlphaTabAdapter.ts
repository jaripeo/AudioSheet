/**
 * AlphaTab tablature adapter — ARCHITECTURE.md Section 4.4.
 *
 * The preferred path is ScoreDocument -> MusicXML -> alphaTab.importer, because
 * AlphaTab's MusicXML importer already handles tab staves, techniques and chord
 * diagrams. `alphaTexWriter` is the fallback for the features MusicXML
 * round-trips poorly.
 *
 * AlphaTab itself is added as a dependency in Phase 2 (Section 5.3).
 */

import type { ScoreDocument } from "@audiosheet/schema";

/** How a document reaches AlphaTab. */
export type ImportPath = "musicxml" | "alphatex";

/** The element AlphaTab renders into. Its own types arrive in Phase 2. */
export type TabSurface = unknown;

/**
 * Render a document as tablature.
 *
 * @param surface - The target element.
 * @param doc - The reduced document.
 * @param path - Which import path to use.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function renderTab(surface: TabSurface, doc: ScoreDocument, path: ImportPath): void {
  throw new Error("unimplemented: the AlphaTab adapter lands in Phase 2");
}

/**
 * Map a tick to an x offset within a system, for cursor tracking.
 *
 * @param tick - Position in ticks.
 * @param systemIndex - Index of the system the tick falls in.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function tickToPixel(tick: number, systemIndex: number): number {
  throw new Error("unimplemented: the AlphaTab adapter lands in Phase 2");
}
