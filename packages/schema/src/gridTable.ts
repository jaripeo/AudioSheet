/**
 * Grid resolution table — ARCHITECTURE.md Section 3.1 (Normative).
 *
 * This module is the single place the tick values of every legal grid symbol
 * appear. Nothing else in the codebase may hard-code them.
 *
 * Tuplet durations that are not integral in ticks are carried as rationals in
 * Note.duration_rational and converted to ticks only at export, rounding the
 * LAST note of the tuplet to absorb the remainder.
 */

import type { DifficultyLevel } from "./difficulty";

/** Pulses per quarter note. Normative (INV-5). */
export const PPQ = 960;

export interface GridSymbol {
  symbol: string;
  /** Exact tick value, or null when the duration is not integral in ticks. */
  ticks: number | null;
  /** Rational duration in quarter notes, always exact. */
  quarters: { numerator: number; denominator: number };
  /** Difficulty levels at which this symbol may be emitted. */
  legalAt: DifficultyLevel[];
  /** Tuplet actual-count, or null for straight subdivisions. */
  tupletActual: number | null;
}

const ALL: DifficultyLevel[] = ["simple", "medium", "complex"];
const MED_UP: DifficultyLevel[] = ["medium", "complex"];
const CPX: DifficultyLevel[] = ["complex"];

export const GRID_TABLE: GridSymbol[] = [
  { symbol: "whole", ticks: 3840, quarters: { numerator: 4, denominator: 1 }, legalAt: ALL, tupletActual: null },
  { symbol: "half", ticks: 1920, quarters: { numerator: 2, denominator: 1 }, legalAt: ALL, tupletActual: null },
  { symbol: "quarter", ticks: 960, quarters: { numerator: 1, denominator: 1 }, legalAt: ALL, tupletActual: null },
  { symbol: "eighth", ticks: 480, quarters: { numerator: 1, denominator: 2 }, legalAt: ALL, tupletActual: null },
  { symbol: "sixteenth", ticks: 240, quarters: { numerator: 1, denominator: 4 }, legalAt: MED_UP, tupletActual: null },
  { symbol: "32nd", ticks: 120, quarters: { numerator: 1, denominator: 8 }, legalAt: CPX, tupletActual: null },
  { symbol: "quarter-triplet", ticks: 640, quarters: { numerator: 2, denominator: 3 }, legalAt: MED_UP, tupletActual: 3 },
  { symbol: "eighth-triplet", ticks: 320, quarters: { numerator: 1, denominator: 3 }, legalAt: MED_UP, tupletActual: 3 },
  { symbol: "sixteenth-triplet", ticks: 160, quarters: { numerator: 1, denominator: 6 }, legalAt: CPX, tupletActual: 3 },
  { symbol: "eighth-quintuplet", ticks: 384, quarters: { numerator: 2, denominator: 5 }, legalAt: CPX, tupletActual: 5 },
  { symbol: "eighth-septuplet", ticks: null, quarters: { numerator: 2, denominator: 7 }, legalAt: CPX, tupletActual: 7 },
];

/** Grid symbols legal at the given difficulty level. */
export function gridSymbolsFor(level: DifficultyLevel): GridSymbol[] {
  return GRID_TABLE.filter((g) => g.legalAt.includes(level));
}

/** Exact tick value of a grid symbol, or null when it is not integral. */
export function ticksOf(symbol: string): number | null {
  const found = GRID_TABLE.find((g) => g.symbol === symbol);
  if (found === undefined) {
    throw new Error(`unknown grid symbol: ${symbol}`);
  }
  return found.ticks;
}
