/**
 * The normative difficulty profiles — ARCHITECTURE.md Section 2.0.
 *
 * profiles.json is the difficulty engine's constant table, so it is worth more
 * test attention than most data files: a typo here silently changes musical
 * output at every level.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import { PROFILES, profileFor } from "../src/index";
import { TAB_WEIGHTS } from "../src/tab/costs";

const LEVELS = ["simple", "medium", "complex"] as const;

const SCHEMA = JSON.parse(
  readFileSync(
    fileURLToPath(
      new URL("../../schema/schema/score-document.schema.json", import.meta.url),
    ),
    "utf-8",
  ),
) as { $defs: Record<string, { required: string[] }> };

describe("profiles.json", () => {
  it("declares exactly the three levels", () => {
    expect(Object.keys(PROFILES).sort()).toEqual([...LEVELS].sort());
  });

  it.each(LEVELS)("%s carries a self-consistent id and level", (level) => {
    const profile = profileFor(level);
    expect(profile.id).toBe(level);
    expect(profile.level).toBe(level);
  });

  it.each(LEVELS)("%s has exactly the fields the generated schema requires", (level) => {
    const required = SCHEMA.$defs["DifficultyProfile"]?.required;
    expect(required).toBeDefined();
    expect(Object.keys(profileFor(level)).sort()).toEqual([...(required ?? [])].sort());
  });

  it.each(LEVELS)("%s salience weights sum to 1.0", (level) => {
    // Named explicitly rather than via Object.values, so the test also pins the
    // exact set of terms in the Section 2.1.1 formula.
    const w = profileFor(level).salience_weights;
    const total = w.conf + w.metric + w.dur + w.pitch + w.energy + w.contour + w.harm;
    expect(total).toBeCloseTo(1.0, 10);
    expect(Object.keys(w).sort()).toEqual([
      "conf",
      "contour",
      "dur",
      "energy",
      "harm",
      "metric",
      "pitch",
    ]);
  });

  it("matches the Section 2.0 table at Simple", () => {
    const p = profileFor("simple");
    expect(p.grid_divisions).toBe(2);
    expect(p.allow_tuplets).toEqual([]);
    expect(p.swing_notation).toBe("flatten");
    expect(p.min_note_duration_ticks).toBe(480);
    expect(p.note_budget_nps).toBe(3.0);
    expect(p.max_simultaneous_notes).toBe(1);
    expect(p.max_voices).toBe(1);
    expect(p.chord_max_notes).toBe(2);
    expect(p.chord_tone_priority).toEqual([1, 5]);
    expect(p.pitch_range_semitones).toBe(24);
    expect(p.max_accidentals_in_key).toBe(2);
    expect(p.guitar_fret_window).toEqual([0, 4]);
    expect(p.guitar_max_span).toBe(3);
    expect(p.guitar_max_strings_per_chord).toBe(2);
    expect(p.guitar_allow_barre).toBe(false);
    expect(p.guitar_techniques).toEqual([]);
    expect(p.parts_max).toBe(1);
    expect(p.drum_kit_subset).toEqual(["kick", "snare", "closed_hat"]);
    expect(p.ornaments).toBe("strip");
    expect(p.show_dynamics).toBe(false);
  });

  it("matches the Section 2.0 table at Medium", () => {
    const p = profileFor("medium");
    expect(p.grid_divisions).toBe(4);
    expect(p.allow_tuplets).toEqual([3]);
    expect(p.min_note_duration_ticks).toBe(240);
    expect(p.note_budget_nps).toBe(7.0);
    expect(p.max_simultaneous_notes).toBe(3);
    expect(p.max_voices).toBe(2);
    expect(p.chord_max_notes).toBe(4);
    expect(p.chord_tone_priority).toEqual([1, 3, 7, 5]);
    expect(p.pitch_range_semitones).toBe(36);
    expect(p.max_accidentals_in_key).toBe(4);
    expect(p.guitar_fret_window).toEqual([0, 12]);
    expect(p.guitar_max_span).toBe(4);
    expect(p.guitar_allow_barre).toBe(true);
    expect(p.parts_max).toBe(2);
  });

  it("matches the Section 2.0 table at Complex", () => {
    const p = profileFor("complex");
    expect(p.grid_divisions).toBe(8);
    expect(p.allow_tuplets).toEqual([3, 5, 6, 7]);
    expect(p.min_note_duration_ticks).toBe(120);
    expect(p.max_simultaneous_notes).toBe(6);
    expect(p.max_voices).toBe(4);
    expect(p.chord_max_notes).toBe(6);
    expect(p.guitar_fret_window).toEqual([0, 24]);
    expect(p.guitar_max_span).toBe(5);
    expect(p.guitar_max_strings_per_chord).toBe(6);
    expect(p.allow_transposition).toBe(false);
  });

  it("uses null, not Infinity, for the unrestricted values", () => {
    const p = profileFor("complex");
    expect(p.note_budget_nps).toBeNull();
    expect(p.pitch_range_semitones).toBeNull();
    expect(p.max_accidentals_in_key).toBeNull();
    expect(p.parts_max).toBeNull();
  });

  it("forbids tuplets at Simple through allow_tuplets, not through gamma", () => {
    const p = profileFor("simple");
    expect(p.allow_tuplets).toEqual([]);
    expect(Number.isFinite(p.quantize_weights.gamma)).toBe(true);
  });
});

describe("profile monotonicity", () => {
  const [simple, medium, complex] = LEVELS.map(profileFor);

  it("resolves all three levels", () => {
    expect(simple && medium && complex).toBeTruthy();
  });

  it("refines the rhythmic grid as difficulty rises", () => {
    expect(simple!.grid_divisions).toBeLessThan(medium!.grid_divisions);
    expect(medium!.grid_divisions).toBeLessThan(complex!.grid_divisions);
    expect(simple!.min_note_duration_ticks).toBeGreaterThan(medium!.min_note_duration_ticks);
    expect(medium!.min_note_duration_ticks).toBeGreaterThan(complex!.min_note_duration_ticks);
  });

  it("admits more polyphony as difficulty rises", () => {
    expect(simple!.max_voices).toBeLessThan(medium!.max_voices);
    expect(medium!.max_voices).toBeLessThan(complex!.max_voices);
    expect(simple!.chord_max_notes).toBeLessThan(medium!.chord_max_notes);
    expect(medium!.chord_max_notes).toBeLessThan(complex!.chord_max_notes);
  });

  it("widens the fretboard as difficulty rises", () => {
    expect(simple!.guitar_fret_window[1]).toBeLessThan(medium!.guitar_fret_window[1]);
    expect(medium!.guitar_fret_window[1]).toBeLessThan(complex!.guitar_fret_window[1]);
    expect(simple!.guitar_max_span).toBeLessThan(medium!.guitar_max_span);
    expect(medium!.guitar_max_span).toBeLessThan(complex!.guitar_max_span);
  });

  it("keeps each level's techniques a superset of the level below", () => {
    const mediumSet = new Set<string>(medium!.guitar_techniques);
    const complexSet = new Set<string>(complex!.guitar_techniques);
    for (const technique of simple!.guitar_techniques) {
      expect(mediumSet.has(technique)).toBe(true);
    }
    for (const technique of medium!.guitar_techniques) {
      expect(complexSet.has(technique)).toBe(true);
    }
  });

  it("keeps each level's drum kit a superset of the level below", () => {
    const mediumSet = new Set<string>(medium!.drum_kit_subset);
    const complexSet = new Set<string>(complex!.drum_kit_subset);
    for (const piece of simple!.drum_kit_subset) {
      expect(mediumSet.has(piece)).toBe(true);
    }
    for (const piece of medium!.drum_kit_subset) {
      expect(complexSet.has(piece)).toBe(true);
    }
  });

  it("relaxes quantisation penalties as difficulty rises", () => {
    expect(simple!.quantize_weights.beta).toBeGreaterThan(medium!.quantize_weights.beta);
    expect(medium!.quantize_weights.beta).toBeGreaterThan(complex!.quantize_weights.beta);
    expect(simple!.quantize_weights.delta).toBeGreaterThan(medium!.quantize_weights.delta);
  });
});

describe("tab weights", () => {
  it.each(LEVELS)("%s profile agrees with weights.json", (level) => {
    expect(profileFor(level).tab_weights).toEqual(TAB_WEIGHTS[level]);
  });

  it.each(LEVELS)("%s matches the Section 2.3.4 table", (level) => {
    const expected = {
      simple: { k_fret: 3.0, k_shift: 4.0, k_high: 6.0, k_legato: 0.0 },
      medium: { k_fret: 1.5, k_shift: 2.0, k_high: 2.0, k_legato: 1.0 },
      complex: { k_fret: 0.8, k_shift: 1.0, k_high: 0.5, k_legato: 1.5 },
    }[level];
    expect(profileFor(level).tab_weights).toMatchObject(expected);
  });

  it("penalises hand movement less as difficulty rises", () => {
    const [simple, medium, complex] = LEVELS.map((l) => profileFor(l).tab_weights);
    expect(simple!.k_shift).toBeGreaterThan(medium!.k_shift);
    expect(medium!.k_shift).toBeGreaterThan(complex!.k_shift);
  });
});

describe("profileFor", () => {
  it("rejects an unknown level", () => {
    // @ts-expect-error deliberately outside the union
    expect(() => profileFor("expert")).toThrow(/unknown difficulty level/);
  });
});
