# Leave Manager — kurulum ve çalıştırma

## Gereksinimler
- Python 3.12
- Node 16 veya üzeri (yalnızca frontend testleri için)

## Kurulum (repo kökünden)
```sh
python -m venv .venv
# Yalnızca bu makinede pip "access violation" ile çöküyorsa (Windows sertifika deposu sorunu),
# ayarı sadece bu venv'e yazın — global pip ayarına dokunmayın:
printf '[global]\nuse-deprecated = legacy-certs\n' > .venv/pip.ini
tools/py -m pip install -r requirements-lock.txt
npm ci
```

## Uygulamayı başlatma
```sh
tools/py -m uvicorn app.main:app --app-dir backend
```
Ardından tarayıcıda <http://127.0.0.1:8000/> açılır. Durdurmak için `Ctrl+C`.

## Doğrulama
```sh
./scripts/check          # tam profil
./scripts/check --fast   # hızlı profil (geliştirme döngüsü)
```
Adımlar `scripts/check.conf` içinde; kurallar `docs/testing.md`.
