/**
 * The duration table — ARCHITECTURE.md Appendix 5.5 (Normative).
 *
 * This table is the only legal source of notated_type and dots, so every value in
 * it is checked against the appendix, and the decomposition rule is checked
 * against the cases the quantiser will actually hand it.
 */

import { describe, expect, it } from "vitest";

import { DURATION_TABLE, durationFor, isNotatable, tiedChain } from "../src/durations";

describe("DURATION_TABLE", () => {
  it("matches the Appendix 5.5 table exactly", () => {
    expect(DURATION_TABLE).toEqual([
      { ticks: 3840, type: "whole", dots: 0 },
      { ticks: 2880, type: "half", dots: 1 },
      { ticks: 1920, type: "half", dots: 0 },
      { ticks: 1680, type: "quarter", dots: 2 },
      { ticks: 1440, type: "quarter", dots: 1 },
      { ticks: 960, type: "quarter", dots: 0 },
      { ticks: 840, type: "eighth", dots: 2 },
      { ticks: 720, type: "eighth", dots: 1 },
      { ticks: 480, type: "eighth", dots: 0 },
      { ticks: 420, type: "16th", dots: 2 },
      { ticks: 360, type: "16th", dots: 1 },
      { ticks: 240, type: "16th", dots: 0 },
      { ticks: 180, type: "32nd", dots: 1 },
      { ticks: 120, type: "32nd", dots: 0 },
      { ticks: 60, type: "64th", dots: 0 },
    ]);
  });

  it("is sorted longest first, which tiedChain relies on", () => {
    const ticks = DURATION_TABLE.map((entry) => entry.ticks);
    expect([...ticks].sort((a, b) => b - a)).toEqual(ticks);
  });

  it("has no duplicate tick values", () => {
    const ticks = DURATION_TABLE.map((entry) => entry.ticks);
    expect(new Set(ticks).size).toBe(ticks.length);
  });

  it("keeps every dotted value consistent with its base", () => {
    for (const entry of DURATION_TABLE) {
      if (entry.dots === 0) continue;
      const base = DURATION_TABLE.find((e) => e.type === entry.type && e.dots === 0);
      expect(base).toBeDefined();
      const multiplier = entry.dots === 1 ? 1.5 : 1.75;
      expect(entry.ticks).toBe(base!.ticks * multiplier);
    }
  });
});

describe("durationFor", () => {
  it("resolves a quarter note at PPQ 960", () => {
    expect(durationFor(960)).toEqual({ ticks: 960, type: "quarter", dots: 0 });
  });

  it("returns undefined for a tick count that is not notatable alone", () => {
    expect(durationFor(1000)).toBeUndefined();
    expect(durationFor(320)).toBeUndefined();
  });
});

describe("isNotatable", () => {
  it.each([3840, 1920, 960, 480, 240, 120, 60])("accepts %i ticks", (ticks) => {
    expect(isNotatable(ticks)).toBe(true);
  });

  it.each([320, 640, 1000, 7])("rejects %i ticks", (ticks) => {
    expect(isNotatable(ticks)).toBe(false);
  });

  it("rejects the eighth-triplet, which must be carried as a tuplet", () => {
    expect(isNotatable(320)).toBe(false);
  });
});

describe("tiedChain", () => {
  it("returns a single entry for a directly notatable duration", () => {
    expect(tiedChain(960)).toEqual([{ ticks: 960, type: "quarter", dots: 0 }]);
  });

  it("decomposes five quarters into a whole tied to a quarter", () => {
    expect(tiedChain(4800).map((e) => e.ticks)).toEqual([3840, 960]);
  });

  it("prefers a dotted value over a tie when one exists", () => {
    expect(tiedChain(1440)).toHaveLength(1);
    expect(tiedChain(1440)[0]?.dots).toBe(1);
  });

  it("decomposes longest first", () => {
    const chain = tiedChain(3840 + 1920 + 240);
    expect(chain.map((e) => e.ticks)).toEqual([3840, 1920, 240]);
  });

  it("sums to the requested duration", () => {
    for (const ticks of [60, 120, 300, 960, 1020, 4800, 7680]) {
      const chain = tiedChain(ticks);
      if (chain.length > 0) {
        expect(chain.reduce((sum, e) => sum + e.ticks, 0)).toBe(ticks);
      }
    }
  });

  it("returns an empty chain when a duration cannot be decomposed", () => {
    // 7 ticks is finer than a 64th note and has no representation.
    expect(tiedChain(7)).toEqual([]);
  });

  it("returns an empty chain for zero", () => {
    expect(tiedChain(0)).toEqual([]);
  });
});
