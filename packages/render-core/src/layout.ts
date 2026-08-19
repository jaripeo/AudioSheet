/**
 * System breaking and measure widths — ARCHITECTURE.md Section 4.3.
 *
 * Systems are virtualised: only those within `VIRTUALISATION_MARGIN_SCREENS`
 * viewport heights of the scroll position are rendered. A four-minute score is
 * 100+ systems, and rendering all of them in VexFlow costs seconds.
 */

import type { RenderDirectives, ScoreDocument } from "@audiosheet/schema";

/** How far beyond the viewport systems are kept rendered. */
export const VIRTUALISATION_MARGIN_SCREENS = 2;

/** One laid-out system. */
export interface System {
  readonly index: number;
  readonly startTick: number;
  readonly endTick: number;
  readonly measureIndices: readonly number[];
  readonly widthPx: number;
}

/**
 * Break the score into systems.
 *
 * @param doc - The document to lay out.
 * @param directives - Render hints; empty `system_breaks` means auto.
 * @param availableWidthPx - Usable width of the render surface.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function layoutSystems(
  doc: ScoreDocument,
  directives: RenderDirectives,
  availableWidthPx: number,
): System[] {
  throw new Error("unimplemented: system layout lands in Phase 2");
}
