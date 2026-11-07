# Security

> Bootstrap'ta belirlendi (2026-11-07). Ajanların her plan ve review'da uyduğu temel kurallar.

## Secrets
- Secrets never enter the repo, specs, prompts, or chat. `.env` is gitignored; provide `.env.example`.
- Agents never print secret values, even when debugging.
- Bu projenin gizli değeri: `SESSION_SECRET` (oturum çerezini imzalar) — yalnızca `.env`'de;
  testler sabit, gizli olmayan bir test değeri kullanır.

## Input & output
- Sınırdaki her girdi Pydantic v2 şemasıyla doğrulanır (tip, zorunlu alan, enum, tarih).
- SQL yalnızca ORM / parametreli sorgu; ham SQL'e string birleştirme / f-string **yasak**.
- Frontend metni `textContent` ile yazar; `innerHTML` ile kullanıcı veya API verisi basılmaz.
- Güvenlik başlıkları her yanıtta: `Content-Security-Policy: default-src 'self'` (satır içi
  script/stil yok), `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`.
- Hata yanıtları iç ayrıntı sızdırmaz (istisna mesajı, stack trace, SQL, dosya yolu) —
  `docs/conventions.md` "Error handling".
- Parola ve hash hiçbir yanıtta ve logda yer almaz.

## AuthN / AuthZ
- **Kimlik doğrulama:** kullanıcı adı + parola; parolalar **argon2** ile hash'lenir (`pwdlib`).
  Demo kullanıcıları tohum (seed) verisiyle gelir; düz parola repoda yalnızca açıkça demo amaçlı
  seed değeri olarak bulunur.
- **Oturum:** imzalı, `HttpOnly`, `SameSite=Strict` çerez (`Secure` HTTPS'te). JWT / localStorage
  token kullanılmaz (gerekçe: aynı origin; XSS'te token çalınamaz; SameSite CSRF'i kapatır).
- **Varsayılan: reddet.** `/api/auth/login` ve statik dosyalar dışındaki her uç oturum ister; bu
  router seviyesinde topluca uygulanır, endpoint başına hatırlamaya bırakılmaz.
- **İstisnalar (oturumsuz uçlar)** — liste kapalıdır; ekleme kendi spec'iyle olur:
  - `GET /api/health` — yalnızca `{"status": "ok"}` döner; sürüm, ortam, sunucu bilgisi yok (spec 0001).
- **Rol denetimi** `api` katmanında `Depends(require_role(...))` ile; **sahiplik kuralları**
  `services/rules` içinde (BR-9, BR-10, `docs/domain.md`):
  - çalışan yalnızca kendi taleplerini ve bakiyesini görür;
  - onay/ret yalnızca `MANAGER`; yönetici kendi talebini onaylayamaz/reddedemez (403, `AuthorizationException`);
  - başkasının kaydına ID ile erişim (IDOR) 403 döner.
- Yetki kuralları hassas alandır: her biri izinsiz haliyle de testle kanıtlanır (`docs/testing.md`).

## Dependencies
- Her yeni bağımlılık (runtime veya geliştirme) plan'da gerekçesiyle listelenir ve plan onayıyla
  insan tarafından onaylanır; plan dışı bağımlılık eklenmez.
- Kontrol: lisans izin verici (MIT, BSD, Apache-2.0), aktif bakım, bilinen CVE yok.
- Sürümler tam sabitlenir (`pyproject.toml`, `package.json` + lock dosyası).
- `pip-audit` / `npm audit` ağ gerektirir: `check` içinde çalışmaz; bağımlılık ekleyen plan'da
  elle ya da CI'da çalıştırılır, sonuç plan'a tek satır yazılır.

## Review lens
Security is a mandatory dimension of every independent review (see `prompts/review.md`), not a
separate afterthought phase.
