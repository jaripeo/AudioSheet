/**
 * ScoreDocument to RenderModel — ARCHITECTURE.md Section 4.4.
 *
 * Both renderers consume this one model, so the VexFlow and AlphaTab adapters stay
 * thin and cannot disagree about what the score says.
 */

import type { ScoreDocument } from "@audiosheet/schema";
import type { BeamGroup } from "./beaming";
import type { System } from "./layout";

/** A note prepared for drawing. */
export interface RenderNote {
  readonly id: string;
  readonly tick: number;
  readonly durationTicks: number;
  readonly midi: number;
  readonly step: string;
  readonly alter: number;
  readonly octave: number;
  readonly staff: number;
  readonly voice: number;
  /** False for notes kept only for provenance; drawn faintly when ghosting is on. */
  readonly visible: boolean;
  readonly tab: { string: number; fret: number } | null;
}

/** Everything a renderer needs, and nothing it does not. */
export interface RenderModel {
  readonly systems: readonly System[];
  readonly notes: readonly RenderNote[];
  readonly beams: readonly BeamGroup[];
  readonly showGhostNotes: boolean;
}

/**
 * Build the render model.
 *
 * @param doc - The reduced document.
 * @param availableWidthPx - Usable width of the render surface.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function buildRenderModel(doc: ScoreDocument, availableWidthPx: number): RenderModel {
  throw new Error("unimplemented: render model construction lands in Phase 2");
}
