/**
 * Meter-aware beam grouping — ARCHITECTURE.md Section 1.11.
 *
 * Beaming is computed explicitly rather than delegated to the consumer, because
 * consumers disagree and a wrongly-beamed bar misreads at a glance.
 */

import type { Note, TimeSignatureEvent } from "@audiosheet/schema";

/** Notes at or shorter than an eighth can be beamed. */
export const BEAMABLE_MAX_TICKS = 480;

/** A run of notes sharing one beam group. */
export interface BeamGroup {
  readonly startTick: number;
  readonly endTick: number;
  readonly noteIds: readonly string[];
}

/**
 * Return the beat-group boundaries a meter beams within, in ticks.
 *
 * 6/8 groups in threes, 4/4 in quarters, 7/8 as 2+2+3.
 *
 * @param signature - The governing time signature.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function beamBoundaries(signature: TimeSignatureEvent): number[] {
  throw new Error("unimplemented: beam grouping lands in Phase 2");
}

/**
 * Group beamable notes within their measure.
 *
 * @param notes - Notes of one voice inside one measure.
 * @param signature - The governing time signature.
 * @throws Always in Phase 0; lands in Phase 2.
 */
export function groupBeams(
  notes: readonly Note[],
  signature: TimeSignatureEvent,
): BeamGroup[] {
  throw new Error("unimplemented: beam grouping lands in Phase 2");
}
