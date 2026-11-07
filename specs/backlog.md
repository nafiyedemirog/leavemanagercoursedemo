# Backlog — deferred findings

Findings a human triaged as **defer**: real, but fixed later by decision (`workflows/feature-development.md`,
step 7). Nothing lands here without that decision; noise is rejected in the triage record, not parked here.

- A criterion moved out at the ship gate (R-08, `→ moved to B-<n>`) lands here too, by the
  human's ship decision; the entry names the spec and criterion.
- One entry per finding, newest last. Delete the entry in the commit of the work that closes it.
- An entry that grows into new behavior becomes a spec (`specs/active/`), not a fix.

<!-- Format (labels stay English):
- **B-<n>** — <finding, one line> — Source: spec <NNNN>, review round <n> (<file:line>) — Severity: <…>
  — Recommendation: <the reviewer's action> — Deferred by: <name>, <YYYY-MM-DD>, <why>
  A decision deferred at bootstrap (its REPORT) uses Source: bootstrap <YYYY-MM-DD>.
-->

- **B-1** — Starlette 1.10 `TestClient`, `httpx` ile kullanımda `StarletteDeprecationWarning` basıyor ("install `httpx2` instead") — Source: spec 0001, review round 1 (`pyproject.toml:15`, `.venv/.../fastapi/testclient.py:1`) — Severity: Info
  — Recommendation: `httpx2`'ye geçişi kendi bağımlılık onayıyla ayrı bir değişiklikte yap; uyarıyı `filterwarnings` ile susturma — Deferred by: Nafiye Demiroğ, 2026-11-07, yeni bağımlılık gerektiriyor ve bugün işlevsel etkisi yok
