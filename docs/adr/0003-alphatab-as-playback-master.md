# ADR 0003: AlphaSynth is the clock master for both views

- Status: accepted
- Date: 2026-08-18
- Relates to: ARCHITECTURE.md Section 4.4

## Context

The product shows the same music two ways: standard notation via VexFlow and
tablature via AlphaTab. Both need a playback cursor, and the two cursors must agree
to the millisecond or the UI looks broken.

VexFlow has no synthesiser. AlphaTab ships AlphaSynth, a SoundFont2 player with its
own scheduling clock. Running a second engine — Web Audio driving VexFlow, AlphaSynth
driving the tab — means two clocks, two drift profiles, and a synchronisation bug that
will never fully close.

## Decision

AlphaSynth is the single playback engine and the clock master for both views.
`PlaybackController` owns transport state in **seconds** and both adapters expose
`tickToPixel(tick, systemIndex)`. VexFlow's cursor is a follower drawn on an overlay
canvas.

## Consequences

- One soundfont, one scheduler, one source of position truth.
- The tab renderer is on the critical path for playback even when the user is looking
  at standard notation. Accepted: AlphaTab can render headless.
- Because position is held in seconds and converted through the timing grid (INV-5),
  changing difficulty mid-playback re-maps the cursor instead of jumping it.
- If AlphaTab is ever dropped, playback has to be rebuilt. Contained by keeping the
  seconds-domain transport in `packages/playback`, independent of the synth.
