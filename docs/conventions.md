# Conventions

> Bootstrap'ta belirlendi (2026-11-07). Yalnızca gerçek kurallar: her kural ya araçla denetlenir
> (tercih edilen) ya da review'da kontrol edilir. Temenniler buraya girmez.

## Language
<!-- Set at bootstrap (step 0) and mirrored in AGENTS.md. Changing it later is allowed — edit both
     places; existing documents are not translated retroactively. -->
- Chat language (interviews, sessions): Turkish
- Document language (docs/, specs, plans, ADRs, review and verify reports): Turkish
- Always English (protocol, not prose): ANEW core files, template headings and field labels,
  `Status:` values (Draft / Approved / In progress / Shipped), `Approved by / on:`, `Source:`.
- Code identifiers, branch names, commit messages: English
- Kullanıcıya gösterilen metinler (UI, ProblemDetails `detail`): Turkish
- Agent messages (handoff summaries, refusals, `Next:` lines): chat language; command names, file
  paths and protocol fields verbatim.

## Language & framework versions
- Python **3.12** · FastAPI · SQLAlchemy **2.x** (senkron) · Pydantic **v2** · SQLite (Python'un yerleşik `sqlite3`'ü).
- Frontend: vanilla JS (ES modules), HTML, CSS — çatı ve derleme adımı yok.
- Frontend testleri için Node **22 LTS** (`node --test`) + `jsdom`.
- Araçlar: pytest, ruff (lint + format), mypy, pwdlib[argon2].
- Kesin sürümler walking skeleton spec'inde `pyproject.toml` / `package.json` içinde sabitlenir
  (sürüm aralığı değil, tam sürüm); bağımlılık eklemek `docs/security.md` "Dependencies"e tabidir.

## Naming
- Python: `snake_case` fonksiyon/değişken/modül, `PascalCase` sınıf, `UPPER_SNAKE` sabit.
- JS: `camelCase` fonksiyon/değişken, `PascalCase` sınıf; dosya adları küçük harf, `kebab-case`.
- Alan terimleri kodda: `Employee`, `LeaveRequest`, `LeaveBalance`, `LeaveType`
  (`ANNUAL`/`EXCUSE`/`SICK`), `LeaveStatus` (`PENDING`/`APPROVED`/`REJECTED`) — `docs/domain.md`.
- Kural sınıfları `<Entity>BusinessRules` (ör. `LeaveRequestBusinessRules`), `services/rules/` altında;
  metot adı kuralı cümle gibi söyler: `balance_must_be_sufficient()`, `dates_must_not_overlap()`.
- Servisler `<Entity>Service`, repository'ler `<Entity>Repository`, şemalar `<Entity>Create` / `<Entity>Response`.
- Testler: `tests/<katman>/test_<konu>.py`, test adı davranışı söyler:
  `test_approve_deducts_annual_balance`. Frontend: `frontend/**/*.test.js`.
- Dallar ve commit'ler: `docs/git.md`.

## Error handling
- Hata tipleri `app/core/exceptions.py`'de: `BusinessException` (400), `NotFoundException` (404),
  `AuthenticationException` (401), `AuthorizationException` (403). Pydantic doğrulama hatası 422.
- İş kuralı ihlalleri yalnızca `services/rules` içinde fırlatılır; her hata sabit, İngilizce bir
  `type` kodu taşır (ör. `insufficient-balance`, `overlapping-leave`).
- `api` katmanında `try/except` yazılmaz; `main.py`'de kayıtlı **tek merkezi işleyici** her hatayı
  ProblemDetails (RFC 7807) JSON'ına çevirir: `{"type", "title", "status", "detail"}` (+ doğrulamada `errors`).
- Beklenmeyen hata: sunucuda loglanır, istemciye genel bir 500 döner. İstisna mesajı, stack trace,
  SQL ve iç yollar **asla** istemciye gitmez.
- Frontend kararını `type`'a göre verir, kullanıcıya Türkçe `detail`'i gösterir (`textContent` ile).

## Data rules
- İzin tarihleri `date` (saat yok); zaman damgaları (oluşturma, karar anı) UTC `datetime`.
- "Bugün" ve "şimdi" yalnızca enjekte edilen `Clock`'tan okunur (`app/core/clock.py`).
- Bakiye ve gün sayısı tam sayı gündür; yarım gün yok.
- ID'ler otomatik artan tam sayı.
- Durum ve izin türü enum; serbest metin değil. Veritabanında da enum değeri saklanır.
- Bakiye değişikliği ile durum değişikliği aynı transaction'da olur (servis yönetir).

## Known traps
<!-- "<trap> — <what to do instead> — from <spec/finding>". Builders read this section before the first plan step. -->
- SQLite yabancı anahtarları varsayılan olarak denetlemez — her bağlantıda `PRAGMA foreign_keys=ON` (SQLAlchemy `connect` olayı) — from bootstrap
- Bellek içi SQLite her bağlantıda ayrı veritabanıdır — testlerde `StaticPool` + `check_same_thread=False` — from bootstrap
- Senkron SQLAlchemy + `async def` endpoint event loop'u bloklar — endpoint'ler `def` ile yazılır — from bootstrap
- Pydantic v1/v2 API karışıklığı — yalnızca v2: `model_validate`, `model_dump`, `ConfigDict(from_attributes=True)`; `orm_mode`, `.dict()` yok — from bootstrap
- `date.today()` / `datetime.now()` doğrudan çağrısı testleri gün değişince kırar — enjekte edilen `Clock` kullan (araçla denetime taşınacak: ruff `DTZ`) — from bootstrap
- Frontend'de API hata metnini `innerHTML` ile basmak XSS'tir — `textContent` kullan — from bootstrap

## Enforced by tooling
<!-- List what the compiler/linter/analyzers already enforce, so review doesn't re-litigate it.
Wire new rules into `scripts/check` whenever possible — prose is advice, tooling is law. -->
Walking skeleton ile devreye girer (şu an planlı, `scripts/check.conf`):
- ruff lint + format (kural seti, `DTZ` dahil, `pyproject.toml`'da).
- mypy tip denetimi.
- Yasak bağımlılıklar: `tests/architecture/` (`docs/architecture.md`).
