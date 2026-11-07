# Spec 0001 — walking skeleton

- Status: In progress
- Mode: lite
- Plan: `specs/plans/0001-plan.md`
- Self-critique: done

## Intent
Geliştirici (ve kurs katılımcısı), ilk iş özelliğini yazmadan önce uçtan uca çalışan en küçük
uygulamayı ister: tarayıcıda açılan bir sayfa, ona cevap veren bir backend ve her şeyi tek komutla
doğrulayan bir kontrol zinciri. Başarı: uygulama yerelde başlar, ana sayfa sistemin ayakta olup
olmadığını gösterir, hatalar projenin kararlaştırılan tek biçiminde döner ve `./scripts/check`
gerçek adımlarla (lint, format, tip, testler, mimari testi) yeşildir. Bilinçli olarak YAPILMAYAN:
izin talebi, bakiye, kullanıcı girişi ve veritabanı tabloları — bunlar sonraki spec'lerin işidir.

## Requirements
1. Uygulama yerelde tek bir belgelenmiş komutla başlatılabilir; ana sayfa tarayıcıda açılır.
2. Sistem, kimlik doğrulaması gerektirmeden sorgulanabilen bir sağlık durumu sunar; yanıt yalnızca
   durumu içerir (sürüm, ortam, sunucu bilgisi gibi iç ayrıntı içermez).
3. Ana sayfa açıldığında sağlık durumunu sorgular ve sonucu kullanıcıya Türkçe gösterir.
4. Bilinmeyen bir adres ve beklenmeyen bir sunucu hatası, projenin kararlaştırılan hata biçiminde
   (`docs/conventions.md` "Error handling") ve Türkçe açıklamayla döner; iç ayrıntı sızmaz.
5. Her yanıt `docs/security.md`'de tanımlı güvenlik başlıklarını taşır.
6. `docs/architecture.md`'deki yasak bağımlılıkları otomatik denetleyen bir test vardır ve bir
   ihlal doğrulama komutunu kırmızıya çevirir.
7. Doğrulama zinciri (`./scripts/check`) bootstrap'ta planlanan adımları gerçekten çalıştırır;
   hızlı (`--fast`) ve tam profiller ayrımı korunur.

## User experience
- Flow: kullanıcı uygulamanın ana adresini açar → sayfa "Leave Manager" başlığını ve sistem
  durumunu gösterir. Başka etkileşim yoktur.
- States:
  - **Yükleniyor:** sağlık sorgusu sürerken "Sistem durumu kontrol ediliyor…" metni.
  - **Başarılı:** "Sistem çalışıyor" metni.
  - **Hata:** sorgu başarısız olursa (sunucuya ulaşılamıyor ya da hata yanıtı) "Sistem şu anda
    yanıt vermiyor. Lütfen daha sonra tekrar deneyin." metni.
  - Boş durum ve yetkisiz durum bu ekranda yoktur (veri yok, giriş yok).
- Design reference: none — the flow above is the design.
- Accessibility: sayfa dili `tr`; durum metni bir canlı bölgede (`aria-live="polite"`) yer alır,
  böylece ekran okuyucu değişikliği duyurur; yalnızca renge dayalı bilgi yok; animasyon yok.

## Constraints & out of scope
- Teknoloji ve katmanlar `docs/architecture.md` ve `docs/conventions.md`'ye uyar (Python 3.12,
  FastAPI, vanilla JS; satır içi script/stil yok — CSP gereği).
- Bağımlılıklar tam sürümle sabitlenir ve plan'da listelenip onaylanır (`docs/security.md` "Dependencies").
- Ortam: frontend testleri bu makinedeki **Node 16.20** ile çalışır (karar: Nafiye Demiroğ,
  2026-11-07, spec onayında). `node --test` Node 16'da deneyseldir; Node 16 desteği bitmiştir (EOL).
  Bootstrap'ta yazılan "Node 22 LTS" ifadeleri (`docs/conventions.md`, `docs/testing.md`) bu
  değişiklikte Node 16'ya göre güncellenir; frontend bağımlılıkları Node 16 ile uyumlu sürümlerden seçilir.
- CI (`.github/workflows/check.yml`), yerelle aynı tam doğrulamayı çalıştıracak araç kurulumunu içerir.
- Sağlık durumunun kimlik doğrulamasız olması, `docs/security.md`'deki "varsayılan: reddet"
  kuralına açık bir istisnadır; bu istisna aynı değişiklikte `docs/security.md`'ye yazılır.
- `.env.example` eklenir (henüz gizli değer kullanılmasa da `SESSION_SECRET` yer tutucusuyla).
- OUT OF SCOPE: veritabanı ve tablolar, kullanıcı girişi/oturum, izin talebi ve bakiye, Alembic,
  dağıtım (deployment), Docker, loglama altyapısı ötesinde gözlemleme, ekran tasarımı/görsel cila.
- Size: 9 kriter, tek kullanıcı yeteneği (sistemin ayakta olduğunu görmek) — bölme önerilmiyor.

## Acceptance criteria
- [ ] AC-1 — Uygulama belgelenmiş tek komutla yerelde başlatıldığında ana adres bir HTML sayfası döner; sayfanın başlığı "Leave Manager"dır ve dili `tr`'dir.
- [ ] AC-2 — Sağlık durumu, oturum olmadan sorgulandığında başarılı yanıt ve "çalışıyor" durumunu döner; yanıtta durum dışında alan yoktur.
- [ ] AC-3 — Ana sayfa, sağlık sorgusu sürerken "Sistem durumu kontrol ediliyor…" metnini gösterir.
- [ ] AC-4 — Ana sayfa, sağlık sorgusu başarılı olduğunda "Sistem çalışıyor" metnini gösterir.
- [ ] AC-5 — Ana sayfa, sağlık sorgusu başarısız olduğunda (ağ hatası veya hata yanıtı) hata metnini gösterir; sunucudan gelen metin sayfaya HTML olarak yorumlanmadan yazılır.
- [ ] AC-6 — Var olmayan bir adres istendiğinde yanıt 404'tür ve kararlaştırılan hata biçimindedir (`type`, `title`, `status`, `detail`; `detail` Türkçe).
- [ ] AC-7 — Beklenmeyen bir sunucu hatasında yanıt 500'dür, kararlaştırılan hata biçimindedir ve genel bir Türkçe mesaj taşır; istisna mesajı, stack trace ve dosya yolu yanıtta yer almaz.
- [ ] AC-8 — Ana sayfa, sağlık yanıtı ve hata yanıtları `Content-Security-Policy: default-src 'self'`, `X-Content-Type-Options: nosniff` ve `Referrer-Policy: same-origin` başlıklarını taşır.
- [ ] AC-9 — Mimari testi, `docs/architecture.md`'deki yasak bağımlılık kurallarından birini ihlal eden bir import'u tespit eder ve başarısız olur; mevcut kodda ihlal yoktur ve test geçer.

## Definition of Done
- [ ] Every acceptance criterion mapped to proof (test or reproducible observation)
- [ ] `scripts/check` green
- [ ] Independent review done; real findings fixed, noise rejected with written rationale, deferred ones in `specs/backlog.md`
- [ ] Docs / ADRs updated if behavior or architecture changed
- [ ] Spec moved to `specs/done/` (it becomes immutable there)

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | |
| Fix rounds | |
| Review findings: real / noise / deferred | |
| Regressions introduced | |
| Bugs escaped to production | |
