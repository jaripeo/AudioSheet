# HANDOFF — Phase 1 (Ingestion and export skeleton)

**Date:** 2026-08-18
**From:** Claude (Opus 5) · **To:** next agent
**Repo state:** `main`, working tree clean, HEAD `359619a`
**Status:** Phase 1 is **partially complete**. S0 ingestion is done and tested.
Export, service, fixtures, and Gate G1 are **not started**.

Read `ARCHITECTURE.md` §1.3, §1.11, §5.2 and §5.3 before touching anything. It is
the normative contract and **MUST NOT be edited**. `CLAUDE.md` carries the
project rules and the Phase 0 deviation list; read it first.

---

## 1. What is done

### 1.1 Commits

| Commit | Contents |
| --- | --- |
| `5148a39` | `config/limits.py` verified, `ingest/sniff.py` implemented |
| `adddce7` | LAME/Xing parsing, `PcmVariant.load`, `downmix`, `detect_edge_silence` |
| `359619a` | ffmpeg integration, soxr resampling, BS.1770-4 loudness, full `decode()` |

### 1.2 `core/audiosheet/ingest/` — S0 complete (§1.3 steps 1–6)

| Module | Public surface | Notes |
| --- | --- | --- |
| `sniff.py` | `sniff_bytes`, `sniff_file` | Magic anchored at offset 0. Extension and MIME never trusted. Rejects with `E_INGEST_FORMAT`. |
| `decode.py` | `decode`, `read_pcm`, `ffmpeg_decode`, `ffmpeg_binary`, `ffmpeg_command`, `mp3_trim_samples`, `lame_delay_and_padding`, `lame_encoder_delay`, `id3v2_length`, `mpeg_frame_shape`, `sha256_file`, `write_variant` | Full S0 flow. |
| `resample.py` | `resample`, `downmix`, `to_channels` | soxr VHQ. Resampling happens **only** here (§1.3 step 4). |
| `loudness.py` | `integrated_lufs`, `true_peak_dbtp`, `normalise`, `detect_edge_silence`, `dbfs_to_amplitude`, `amplitude_to_dbfs` | pyloudnorm / BS.1770-4, 4× oversampled true peak. |

`decode()` performs, in order: file-size limit → `sniff_file` → SHA-256 →
decode (libsndfile for WAV, ffmpeg subprocess for MP3) → duration limits →
downmix if >2 channels → `mp3_trim_samples` → loudness normalise → edge-silence
detection → write four PCM variants → return `AudioBundle`.

### 1.3 Toolchain changes

- `Makefile`: `bootstrap-py` now runs `uv sync --group dev --extra ingest`, and
  venv creation is guarded by `test -x $(PY)` so `make bootstrap` is re-runnable.
  It previously hard-failed on an existing `core/.venv`.
- `core/pyproject.toml`: mypy `ignore_missing_imports` overrides added for
  `soundfile.*`, `soxr.*`, `pyloudnorm.*` — none ship type information.
- Installed by bootstrap: soundfile 0.14.0, soxr 1.1.0, pyloudnorm 0.2.0, scipy.

### 1.4 Tests

`core/tests/unit/test_ingest.py` — **181 tests**. Suite total: 352 pytest, 55 vitest.
`make lint`, `make test` and `make gate` are all green as of `359619a`.

`core/tests/unit/test_tree_contract.py` was amended twice, both times necessarily:
the vacuity guard `test_the_stub_scan_actually_finds_stubs` now points at
`audiosheet.symbolic.quantize` (Phase 6), and `sniff_bytes`, `resample.resample`
and `loudness.integrated_lufs` were removed from the
`test_stubs_raise_not_implemented` table as they are no longer stubs.
**You must do the same for every stub you implement**, or that test will fail.

---

## 2. Decisions already ratified by the user

Do **not** revisit or "fix" these. They were each explicitly approved.

1. **`MP3_FRAME_SYNC` keeps `0xFFF2`** (MPEG-2 Layer III) even though §1.3 names
   only `0xFFFB`/`0xFFF3`/`0xFFFA`.
2. **Container magic is anchored at offset 0.** No scanning the sniff window for
   a 2-byte sync — the false-positive rate is unacceptable.
3. **A missing file raises `FileNotFoundError`, not `E_INGEST_FORMAT`.** Absence
   is a system error, not a user format verdict. Same rule in `PcmVariant.load`.
4. **`downmix` folds round-robin with equal weights.** 5.1 gives `(L C Ls)` and
   `(R LFE Rs)`.
5. **A fourth variant, `pcm_44k_stereo_display`, holds un-normalised 44.1 kHz
   stereo.** §1.3 step 5 forbids gaining the display copy, but the normative
   variant table gives waveform display and Demucs the same row, so one array
   cannot serve both. `PCM_VARIANTS` in `config/constants.py` still holds exactly
   the three normative entries; the display copy is `decode.DISPLAY_VARIANT`.
6. **Normalisation is a single linear gain**, `min(target gain, headroom gain)` —
   the EBU R128 resolution when −18 LUFS and −1.0 dBTP conflict. No dynamics
   processing. A hot master therefore lands *below* −18 LUFS. The display copy is
   recoverable exactly by undoing `gain_db`.
7. **ffmpeg writes a temp WAV rather than piping raw `f32le`.** A seekable file
   carries the sample rate and channel count; a raw pipe would need ffprobe.
   This adds `-c:a pcm_f32le -f wav -y` to the four normative flags.
8. **Silence detection runs after normalisation**, so the −60 dBFS floor means
   the same thing across files of differing levels.
9. **ffmpeg resolution never consults `PATH`.** `vendor/ffmpeg/ffmpeg` by
   default, `AUDIOSHEET_FFMPEG` to override, `E_INGEST_DECODE` when absent. An
   arbitrary system build would not decode like the one the gates measured (INV-2).

---

## 3. Environment facts you need

- **There is no vendored ffmpeg.** `vendor/` does not exist. Real MP3 ingestion
  fails closed with `E_INGEST_DECODE` until someone vendors an LGPL build and
  documents the flags (`THIRD_PARTY_LICENSES.md:50`). This is a licensing
  decision for the user, not an agent task.
- **libsndfile 1.2.2 in this environment reads *and writes* MP3.** The test suite
  exploits this twice, and you should too:
  - `write_mp3()` in `test_ingest.py` produces genuine LAME-encoded MP3s. The
    LAME parser is validated against real encoder output (delay = 576).
  - The `fake_ffmpeg` fixture is a stand-in binary that decodes via libsndfile,
    honouring the same argv. It exercises the whole subprocess path — argv order,
    exit codes, stderr capture, temp-file handoff — with no vendored binary.
  This also means MP3 *could* be decoded without ffmpeg at all. The user was told
  and chose to keep the ffmpeg design. **Do not switch it unilaterally.**
- `models/manifest.json` — all 8 entries are `status: "pending"`, including
  `gm-soundfont` (phase 2), which `scripts/make_fixtures.py` will need.
- The `notation` extra (`music21`, `pretty_midi`, `mido`) is declared in
  `core/pyproject.toml` but **not installed**. Add `--extra notation` to
  `bootstrap-py` and run `make bootstrap` before starting §4.2 below.
  `make bootstrap` is the only target permitted to touch the network (INV-1).

---

## 4. Checklist to finish Phase 1

Work top to bottom. After each item: `make lint`, then `make test`, in that order.
Never run tests before linting.

### 4.1 Corrupt-frame failure policy — `ingest/decode.py`

§1.3 "Failure policy". Currently **any** ffmpeg failure is fatal;
`MAX_CORRUPT_FRACTION` (0.02) and `MAX_ZERO_FILL_GAP_S` (0.5) in
`config/constants.py` are declared but **unreferenced**. Grep them to confirm.

- [ ] Decode as far as possible rather than aborting on the first bad frame.
- [ ] Zero-fill contiguous corrupt gaps shorter than `MAX_ZERO_FILL_GAP_S`.
- [ ] Abort with `E_INGEST_DECODE` when the total corrupt span exceeds
      `MAX_CORRUPT_FRACTION` of duration.
- [ ] Populate `core/tests/fixtures/adversarial/` — it currently holds only a
      README. Truncated files, mid-file byte corruption, zero-length streams.
- [ ] Note: getting per-frame error information out of ffmpeg is the hard part.
      `-err_detect` and stderr parsing are the likely levers; a decoded-vs-
      container duration comparison is the fallback. If you cannot do this
      faithfully, say so rather than approximating silently.

### 4.2 Export skeletons — `export/musicxml.py`, `export/midi.py`

§1.11. Both are `NotImplementedError` stubs with settled signatures:
`to_musicxml`, `write_musicxml`, `to_midi_bytes`, `write_midi`.

- [ ] Install the `notation` extra first (see §3 above).
- [ ] MusicXML 4.0 `score-partwise` with `<divisions>960</divisions>`.
- [ ] Map every row of the §1.11 table. `Note.{step,alter,octave}` go through
      verbatim — **never recompute pitch spelling from MIDI**.
- [ ] Tuplets carry `<time-modification>` **and** `<notations><tuplet>`. Missing
      either causes silent misrendering in most consumers.
- [ ] Beaming is emitted explicitly as `<beam>`, not delegated to the consumer.
- [ ] MIDI 1.0 Type 1, PPQ 960, one track per part, drums forced to channel 9.
      Pitch bends only when `Note.micro_cents` exceeds ±25 cents.
- [ ] `export/practice_midi.py` is also stubbed: quantize to the difficulty grid,
      flatten velocities to 80.
- [ ] INV-4: these are exports only. Nothing may ever parse them back in.
- [ ] Build against `core/tests/fixtures/handmade/simple_scale.json`.

### 4.3 Service — `service/app.py`, `routes.py`, `jobs.py`, `auth.py`

§5.2 is normative for paths, payloads and status codes. All four modules are stubs.

- [ ] `GET /health` → `{ok, version, models: [{name, ok}]}`.
- [ ] `POST /jobs` `{filename, sha256}` + multipart audio → `{job_id}`.
- [ ] `GET /jobs/{id}/events` → SSE `{stage, progress: 0..1, message}` per stage.
      `StageContext.report_progress` already records exactly this shape.
- [ ] `GET /jobs/{id}/document` → `ScoreDocument@complex`.
- [ ] `POST /jobs/{id}/cancel` → `204`. `StageContext.cancel()` and
      `check_cancelled()` already exist and `decode()` honours them.
- [ ] `POST /export/musicxml`, `POST /export/midi` — depends on §4.2.
- [ ] Bind `127.0.0.1` **only**. `Authorization: Bearer <token>` from the token
      file. `Access-Control-Allow-Origin` set to the app origin alone.
- [ ] Every non-2xx body is `{code: "E_*", message, detail}`.
      `AudioSheetError.as_dict()` already emits this shape.
- [ ] Phase 1 scope: the job pipeline is **ingestion-only and returns a stub
      document**. Do not wire real analysis — that is Phase 3+.

### 4.4 Fixtures — `scripts/make_fixtures.py`

- [ ] Synthesize WAVs from known MIDI using a vendored soundfont, with **exact
      ground truth**. Blocked on `gm-soundfont` being vendored (manifest status
      is `pending`); raise it with the user rather than downloading anything.

### 4.5 Gate G1

Record the result in `docs/gates.md` — the G1 table is stubbed with `—` rows.
A phase MUST NOT start while its predecessor's gate is red.

- [ ] `pytest core/tests/unit/test_ingest.py` proves sample-accurate alignment on
      a click-track fixture: **first click within ±3 ms of ground truth**. This
      is the one G1 criterion that tests work already done — it validates the
      `trim_samples` / encoder-delay handling end to end. Note that **ffmpeg
      performs the actual trim** (ratified decision, §2 above); `trim_samples` is
      provenance only. If the click lands late by roughly the encoder delay,
      suspect a double trim, not a parser bug.
- [ ] Exported MusicXML validates against the **MusicXML 4.0 XSD**.
- [ ] DoD: upload a WAV, get a valid stub `ScoreDocument` and a MusicXML file
      that opens in MuseScore **and** imports into AlphaTab.

---

## 5. Rules that will bite you

From `CLAUDE.md`, restated because each one has teeth in this phase:

- `pytest` runs with `filterwarnings = ["error"]`. One new warning fails the suite.
- Never run tests before linting. `make lint`, then `make test`.
- Never hand-edit generated schemas. Edit `packages/schema/src/*.ts`, run `make schema`.
- Never open a network socket at runtime (INV-1). `make bootstrap` only.
- Never introduce nondeterminism (INV-2). No unseeded `random`, no wall-clock in
  outputs. The ingest tests synthesize sine waves precisely to stay deterministic.
- Never mutate a stage's input (INV-3). `PcmVariant.load` returns a read-only
  memmap specifically to enforce this.
- Never convert seconds ↔ ticks outside the tempo map (INV-5).
- Never add a `raise NotImplementedError` without naming its phase — a test
  enforces it, and bare `TODO`/`FIXME`/`XXX` markers are banned outright.
- Never hard-code a normative constant twice.
- Never commit or push unless the user asks.
- **Never modify `ARCHITECTURE.md`.** Report inconsistencies in chat instead.
  Several were found and reported during Phase 1; the ratified resolutions are
  in §2 above and in `CLAUDE.md`.
