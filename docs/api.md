# Local service API

The loopback service defined in ARCHITECTURE.md Section 5.2. Phase 1 implements it
and generates the OpenAPI document from the FastAPI application; this file records
the contract in the meantime.

## Binding and auth

- Binds `127.0.0.1` only, on an ephemeral port.
- Every request requires `Authorization: Bearer <token>`, where the token is written
  by the sidecar to its runtime directory and read by the shell.
- `Access-Control-Allow-Origin` names the app origin alone.
- INV-1: the service makes no outbound connections of any kind.

## Endpoints

| Method | Path | Request | Response |
| --- | --- | --- | --- |
| `POST` | `/jobs` | multipart audio + `{filename, sha256}` | `{job_id}` |
| `GET` | `/jobs/{id}/events` | — | SSE: `{stage, progress, message}` per stage |
| `GET` | `/jobs/{id}/document` | — | `ScoreDocument` at Complex difficulty |
| `POST` | `/jobs/{id}/cancel` | — | `204` |
| `POST` | `/export/musicxml` | `{document}` | `application/vnd.recordare.musicxml+xml` |
| `POST` | `/export/midi` | `{document, practice}` | `audio/midi` |
| `GET` | `/health` | — | `{ok, version, models: [{name, ok}]}` |

## Errors

Every non-2xx body is:

```json
{ "code": "E_INGEST_FORMAT", "message": "...", "detail": {} }
```

`code` is always a member of the registry in Appendix 5.4, mirrored in
`core/audiosheet/pipeline/errors.py`. A test asserts that every code documented in
`ARCHITECTURE.md` exists in that registry.

## Progress

Progress is reported per stage, as `stage`, a fraction in `[0, 1]`, and a message.
Separation dominates wall-clock and MUST report at >= 2 Hz derived from
`chunks_done / chunks_total`, or the UI looks frozen (Section 1.5).
