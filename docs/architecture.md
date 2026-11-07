# Architecture

> Bootstrap'ta karar verilen mimari (2026-11-07). Burada yazan, hedef değil kararın kendisidir.
> Ajanlar plan yapmadan önce bu dosyayı okur.

## System overview
Leave Manager, çalışanların izin talebi oluşturduğu, yöneticilerin onaylayıp reddettiği ve yıllık
izin bakiyesinin takip edildiği küçük bir web uygulamasıdır (eğitim/demo amaçlı). Mimari **tek
süreçli, klasik N katmanlı bir monolittir** — modüler monolit değildir. Backend Python 3.12 +
FastAPI + SQLAlchemy 2.x + SQLite; frontend derleme adımı olmayan vanilla JS/HTML/CSS'tir ve
FastAPI tarafından aynı origin'den sunulur (CORS yok). Gerekçe: demo boyutunda en az hareketli
parça; iş kuralları HTTP ve veritabanından ayrı test edilebilir. Yapı, sade katmanlı düzen ile
nArchitecture'ın (github.com/engindemirog/nArchitecture) işe yarayan kalıplarının birleşimidir.

```
backend/app/
  main.py          uygulama kurulumu, router kaydı, StaticFiles, hata işleyicilerin kaydı
  api/             FastAPI router'ları: HTTP ↔ şema dönüşümü, yetki bağımlılığı (ince controller)
  schemas/         Pydantic istek/yanıt modelleri (API sözleşmesi)
  services/        kullanım senaryoları + transaction sınırı
    rules/         özellik başına <Varlık>BusinessRules sınıfı
  repositories/    SQLAlchemy sorguları; ortak BaseRepository + sayfalama
  models/          SQLAlchemy ORM tabloları
  core/            ayarlar, DB oturumu, Clock, hata tipleri, güvenlik yardımcıları
frontend/          index.html, *.js (saf mantık ayrı modüllerde), *.css
tests/             unit/ · integration/ · architecture/ (backend) — frontend testleri frontend/ yanında
```

## Modules / components and ownership

| Module | Single responsibility | Owns |
|---|---|---|
| `api` | HTTP sınırı: isteği şemaya çevirir, yetkiyi denetler, servisi çağırır, yanıtı döner | Route'lar, `require_role` bağımlılığı |
| `schemas` | API sözleşmesi (girdi doğrulama, çıktı biçimi) | İstek/yanıt modelleri |
| `services` | Kullanım senaryoları (talep oluştur, onayla, reddet, listele); transaction sınırı | Senaryo akışı |
| `services/rules` | İş kurallarını tek yerde, metot başına bir kural olarak uygular; ihlalde tipli hata fırlatır | BR-n kuralları, sahiplik kuralları |
| `repositories` | Veri erişimi; sorgular | Kalıcılık işlemleri |
| `models` | Tablo tanımları | Şema: Employee, LeaveRequest, LeaveBalance |
| `core` | Kesişen konular | Ayarlar, oturum, `Clock`, hata tipleri, merkezi hata işleyici, parola hash'i |
| `frontend` | Kullanıcı arayüzü; yalnızca `/api` JSON uçlarıyla konuşur | Ekranlar ve ekran durumları |

## Communication rules
- Bağımlılık yönü tek yönlüdür: `api → services → repositories → models`. `schemas` ve `core`
  her katmandan kullanılabilir.
- Katman atlamak yoktur: `api` veriye yalnızca `services` üzerinden ulaşır.
- Transaction'ı servis açar ve kapatır; repository commit etmez.
- Frontend ↔ backend yalnızca HTTP/JSON (`/api/...`); hatalar ProblemDetails (`docs/conventions.md`).
- Senkron çağrılar; mesaj kuyruğu / olay sistemi yoktur.

## Forbidden dependencies (make them testable)
`tests/architecture/` içindeki pytest testi, `ast` ile import'ları tarayarak doğrular (ek paket yok):
1. `app.api` → `app.repositories` ve `app.models` import etmez; yalnızca `app.services`, `app.schemas`, `app.core` kullanır.
2. `app.services` → `app.api` ve `fastapi` import etmez (iş kuralları HTTP'den bağımsız test edilir).
3. `app.repositories` → `app.services` ve `app.api` import etmez.
4. `app.models` → `app` içinden yalnızca `app.core` import eder.
5. `app.core` → `app` içinden hiçbir katmanı import etmez.
6. Frontend backend kodunu ya da veritabanını bilmez; yalnızca `/api` uçlarını çağırır.

## Deliberately out of scope
- Mediator / CQRS, Commands/Queries klasörleri, pipeline davranışları (nArchitecture'dan alınmadı:
  FastAPI `Depends` doğrulama ve yetkiyi karşılıyor; demo için fazla katman).
- AutoMapper/Profiles karşılığı (Pydantic `from_attributes` yeterli).
- Caching, ElasticSearch, e-posta, OTP/2FA; mesajlaşma; çoklu kiracılık.
- Async veritabanı sürücüsü (senkron SQLAlchemy + `def` endpoint'ler).
- Frontend çatısı ve derleme zinciri (bundler, transpiler).
- Resmi tatil / hafta sonu hesabı, yarım gün izin, takım bazlı yönetici hiyerarşisi.
