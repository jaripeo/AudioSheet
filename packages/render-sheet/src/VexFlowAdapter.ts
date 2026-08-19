/**
 * VexFlow sheet-music adapter — ARCHITECTURE.md Section 4.4.
 *
 * Builds Stave/Voice/StaveNote/Beam/Tuplet/Curve objects and formats one system at
 * a time. Ghost notes (`flags.dropped`, `render: false`) are drawn at
 * `GHOST_OPACITY` with pointer targets, which is what makes "show me what was
 * removed" a one-click affordance.
 *
 * VexFlow itself is added as a dependency in Phase 2 (Section 5.3).
 */

import type { RenderModel, System } from "@audiosheet/render-core";

/** Fill opacity for provenance-only notes. */
export const GHOST_OPACITY = 0.25;

/** The surface a system is drawn onto. VexFlow's own types arrive in Phase 2. */
export type RenderSurface = unknown;

/**
 * Draw one system.
 *
 * @param surface - The target surface.
 * @param model - The render model.
 * @param system - The system to draw.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function drawSystem(
  surface: RenderSurface,
  model: RenderModel,
  system: System,
): void {
  throw new Error("unimplemented: the VexFlow adapter lands in Phase 2");
}

/**
 * Map a tick to an x offset within a system, for cursor tracking.
 *
 * @param tick - Position in ticks.
 * @param systemIndex - Index of the system the tick falls in.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function tickToPixel(tick: number, systemIndex: number): number {
  throw new Error("unimplemented: the VexFlow adapter lands in Phase 2");
}
