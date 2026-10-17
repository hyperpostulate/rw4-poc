# GPS Info — GPS Data for Redmi Watch 4

![Platform](https://img.shields.io/badge/platform-Xiaomi%20Vela-blue)
![Device](https://img.shields.io/badge/device-Redmi%20Watch%204-orange)
![Version](https://img.shields.io/badge/version-1.0.0-green)

A single-screen app for the Redmi Watch 4 that shows raw GNSS data (latitude and longitude in decimal degrees plus DMS, altitude, speed, accuracy, fix time and signal status), built as a Xiaomi Vela JS app (quick app, `.rpk`). The UI is Turkish and the app degrades gracefully when the geolocation API is unavailable on the device.

* * *

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Build & Run](#build--run)
- [Project Structure](#project-structure)
- [Screen & Features](#screen--features)
- [Installing on the Watch](#installing-on-the-watch)
- [Documentation](#documentation)
- [Known Limitations & Risks](#known-limitations--risks)
- [Verification](#verification)
- [License](#license)
- [Developer](#developer)
- [Contributing](#contributing)

* * *

## Requirements

Requirement

Version / Notes

Node.js

18+ (tested on v24.12.0)

npm

9+ (tested on 11.6.2)

Python 3 + Pillow

Only needed to regenerate the PNG assets (`scripts/gen_assets.py`)

Android phone

Only needed to install the `.rpk` onto the watch via **Notify for Xiaomi** (see [Installing on the Watch](#installing-on-the-watch))

`aiot-toolkit`

Pulled in automatically as a dev dependency (`npm install`)

* * *

## Installation

### Manual Build

```
git clone https://github.com/hyperpostulate/redmi-watch4-compass.git
cd redmi-watch4-compass
npm install
npm run build
```

The build produces `dist/com.hyperpostulate.gpsinfo.debug.1.0.0.rpk`.

* * *

## Build & Run

```
npm install                          # Install the aiot-toolkit toolchain
npm run build                        # Build a debug .rpk into dist/
npm run release                      # Build a release .rpk (requires signing keys)
npm run start                        # aiot start --watch (live development)
python3 scripts/gen_assets.py        # Regenerate the PNG assets from code
```

The toolchain is `aiot-toolkit` (`aiot build` / `aiot release` / `aiot start`). The debug `.rpk` needs no signing; a release package needs `sign/private.pem` and `sign/certificate.pem` (generate with OpenSSL). Deployment to the watch itself is described in [Installing on the Watch](#installing-on-the-watch).

For UI preview without hardware, set `SIMULATE = true` at the top of `src/pages/index/index.ux`; the app then drives a slowly rotating synthetic heading and fake coordinates every second instead of calling the real APIs.

* * *

## Project Structure

```
redmi-watch4-compass/
├── src/
│   ├── manifest.json          # package, features, permissions, router, designWidth 390
│   ├── app.ux                 # app entry (onCreate/onDestroy)
│   ├── i18n/
│   │   └── defaults.json      # default string bundle
│   ├── common/
│   │   └── logo.png           # generated app icon (location pin), 192x192
│   └── pages/
│       └── index/
│           └── index.ux       # single page: GPS data list + status row + all logic
├── scripts/
│   └── gen_assets.py          # reproducible Pillow generator for the PNG assets
├── docs/
│   └── design.md              # UI/UX design specification (Turkish)
├── dist/                      # build output (.rpk) - gitignored
├── build/                     # intermediate build output - gitignored
├── package.json
└── README.md
```

### Core Files

File

Purpose

`src/manifest.json`

Vela app manifest: `package` = `com.hyperpostulate.gpsinfo`, `deviceTypeList: ["watch"]`, `minPlatformVersion: 1000`, `designWidth: 390`, declared features (`system.router`, `system.geolocation`, `system.brightness`) and the `LOCATION` permission

`src/pages/index/index.ux`

The whole app: template (GPS data list + status row), script (geolocation logic, formatting helpers) and styles

`scripts/gen_assets.py`

Generates `logo.png` deterministically; re-reads every file it writes and asserts dimensions and non-blank content

`docs/design.md`

The authoritative UI/UX spec (palette, typography, layout, states, copy)

* * *

## Screen & Features

The app has a **single screen**. Data subscriptions start on page show and stop on page hide to save battery. The data is displayed as green text on a black background.

### Screen — GPS

- Latitude and longitude in decimal degrees plus a smaller DMS line (`41° 00' 29.6" K`).
- Altitude (metres, GNSS-derived - the Redmi Watch 4 has no barometer), speed (`m/s` and `km/h`), horizontal accuracy, and the last fix time.
- A status row: searching (yellow), fix acquired (green "Sinyal Güçlü"), or a mapped error (203 → "Desteklenmiyor", 204 → "Zaman Aşımı", 1000+ → "Konum Kapalı").

Every API call is wrapped in `try/catch` and guarded by capability flags, so a missing or failing API is never retried in a loop.

* * *

## Installing on the Watch

The `.rpk` is installed over Bluetooth from an Android phone using the **[Notify for Xiaomi](https://play.google.com/store/apps/details?id=com.mc.xiaomi1)** app (Google Play listing "Notify for Xiaomi/Mi Band 8-10", package `com.mc.xiaomi1`, by OneZeroBit). The Redmi Watch 4 is on the app's official compatibility list, and the app's official site documents installing custom VelaJS (`.rpk`) apps this way.

> **Verification status:** verified on a real Redmi Watch 4 — GPS Info installed successfully with this method. The watch-side GPS data display has not been checked yet.

### Prerequisites

- An **Android phone** (iOS cannot install `.rpk` files).
- **Notify for Xiaomi** installed from Google Play.
- The watch paired with Notify: the in-app setup wizard fetches the pairing (auth) key through your Xiaomi account, so Mi Fitness does not need to stay installed.
- Only one app can hold the watch's Bluetooth connection at a time. If Mi Fitness is installed, force-stop it, deny its "Nearby devices" permission, or uninstall it — but **do not un-pair the watch from Mi Fitness before uninstalling**.

### Steps

1. Build the package: `npm run build` → `dist/com.hyperpostulate.gpsinfo.debug.1.0.0.rpk`.
2. Open **Notify for Xiaomi**.
3. Go to **Device**.
4. Select **Third party app**.
5. Select the `.rpk` file (`dist/com.hyperpostulate.gpsinfo.debug.1.0.0.rpk`).
6. Keep the watch near the phone and follow the guided steps.
7. When the installation finishes, **GPS Info** appears in the watch's app list.

### Notes

- The debug-signed `.rpk` produced by `npm run build` is fine for this app: Vela only checks the certificate for watch↔phone Interconnect communication, which GPS Info does not use.
- Redmi Watch 4 limits: at most ~20 quick apps installed, and ~87 MB of free space is required for quick-app installs.
- To update, build a new `.rpk` and install it over the same package name (`com.hyperpostulate.gpsinfo`).
- Unverified details: the app version that introduced `.rpk` installs, and whether the feature requires the (about €3, one-time) PRO purchase, are not officially documented. The menu labels above are the English ones; the app itself is localized, but the Turkish labels were not verified.

Sources: [Notify for Xiaomi VelaJS install guide](https://mibandnotify.com/xiaomi-mi-band/notify-xms-app-instructions.php) · [Google Play listing](https://play.google.com/store/apps/details?id=com.mc.xiaomi1)

* * *

## Documentation

Document

Contents

[docs/design.md](docs/design.md)

UI/UX specification: palette, typography scale, layout, states, Turkish copy, asset geometry (GPS-only)

* * *

## Known Limitations & Risks

- **Geolocation API availability on the Redmi Watch 4 is unverified.** The official Vela support tables mark @system.geolocation as *not supported* on the Redmi Watch 4, even though the watch hardware has GNSS (the stock apps use it). No public community report confirms or denies it; the app is built to degrade gracefully and the answer only comes from a real-device test.
- **Altitude is GNSS-derived** — the Redmi Watch 4 has no barometer, so altitude accuracy is inherently limited.
- **`npm audit` reports vulnerabilities in transitive dev dependencies** of `aiot-toolkit`. They are build-time only and do not ship inside the `.rpk`.

* * *

## Verification

```
npm run build                        # must succeed and emit dist/*.rpk
python3 scripts/gen_assets.py        # regenerates and self-checks the PNG assets
```

On-device checklist (the only way to resolve the API questions above):

1. Does the GPS screen show coordinates, and is the status `Sinyal Güçlü` or an error code?
2. Does the screen stay awake while the app is open?

* * *

## License

No license file is currently included in this repository. Until one is added, all rights are reserved by the author.

* * *

## Developer

**Mesut ORMANLI**

- Email: [mesutormanli@gmail.com](mailto:mesutormanli@gmail.com)
- GitHub: [@hyperpostulate](https://github.com/hyperpostulate)

* * *

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

* * *

## GPS Info — Redmi Watch 4 için GPS Verileri

![Platform](https://img.shields.io/badge/platform-Xiaomi%20Vela-blue)
![Device](https://img.shields.io/badge/device-Redmi%20Watch%204-orange)
![Version](https://img.shields.io/badge/version-1.0.0-green)

Redmi Watch 4 için ham GNSS verilerini (enlem ve boylam ondalık derece ve DMS olarak, irtifa, hız, doğruluk, düzeltme zamanı ve sinyal durumu) gösteren tek ekranlı bir uygulama; Xiaomi Vela JS uygulaması (hızlı uygulama, `.rpk`) olarak geliştirilmiştir. Arayüz Türkçedir ve cihazda geolocation API'si yoksa uygulama zarif biçimde düşer.

* * *

## İçindekiler

- [Gereksinimler](#gereksinimler)
- [Kurulum](#kurulum)
- [Derleme ve Çalıştırma](#derleme-ve-çalıştırma)
- [Proje Yapısı](#proje-yapısı)
- [Ekran ve Özellikler](#ekran-ve-özellikler)
- [Saate Kurulum](#saate-kurulum)
- [Belgeler](#belgeler)
- [Bilinen Sınırlamalar ve Riskler](#bilinen-sınırlamalar-ve-riskler)
- [Doğrulama](#doğrulama)
- [Lisans](#lisans)
- [Geliştirici](#geliştirici)
- [Katkıda Bulunma](#katkıda-bulunma)

* * *

## Gereksinimler

Gereksinim

Sürüm / Not

Node.js

18+ (v24.12.0 ile test edildi)

npm

9+ (11.6.2 ile test edildi)

Python 3 + Pillow

Yalnızca PNG varlıklarını yeniden üretmek için gerekir (`scripts/gen_assets.py`)

Android telefon

Yalnızca `.rpk` dosyasını **Notify for Xiaomi** ile saate kurmak için gerekir (bkz. [Saate Kurulum](#saate-kurulum))

`aiot-toolkit`

`npm install` ile geliştirme bağımlılığı olarak otomatik gelir

* * *

## Kurulum

### Manuel Derleme

```
git clone https://github.com/hyperpostulate/redmi-watch4-compass.git
cd redmi-watch4-compass
npm install
npm run build
```

Derleme `dist/com.hyperpostulate.gpsinfo.debug.1.0.0.rpk` dosyasını üretir.

* * *

## Derleme ve Çalıştırma

```
npm install                          # aiot-toolkit araç zincirini kur
npm run build                        # dist/ içine debug .rpk derle
npm run release                      # release .rpk derle (imza anahtarları gerekir)
npm run start                        # aiot start --watch (canlı geliştirme)
python3 scripts/gen_assets.py        # PNG varlıklarını koddan yeniden üret
```

Araç zinciri `aiot-toolkit`'tir (`aiot build` / `aiot release` / `aiot start`). Debug `.rpk` imza gerektirmez; release paketi için `sign/private.pem` ve `sign/certificate.pem` gerekir (OpenSSL ile üretilir). Saate kurulumun kendisi [Saate Kurulum](#saate-kurulum) bölümünde anlatılır.

Donanım olmadan arayüz önizlemesi için `src/pages/index/index.ux` dosyasının başındaki `SIMULATE = true` yapılır; uygulama gerçek API'ler yerine her saniye yavaşça dönen sentetik bir yön ve sahte koordinatlar üretir.

* * *

## Proje Yapısı

```
redmi-watch4-compass/
├── src/
│   ├── manifest.json          # paket, features, izinler, router, designWidth 390
│   ├── app.ux                 # uygulama girişi (onCreate/onDestroy)
│   ├── i18n/
│   │   └── defaults.json      # varsayılan metin paketi
│   ├── common/
│   │   └── logo.png           # üretilen uygulama ikonu (konum pini), 192x192
│   └── pages/
│       └── index/
│           └── index.ux       # tek sayfa: GPS veri listesi + durum satırı + tüm mantık
├── scripts/
│   └── gen_assets.py          # PNG varlıkları için tekrarlanabilir Pillow üreteci
├── docs/
│   └── design.md              # UI/UX tasarım spesifikasyonu
├── dist/                      # derleme çıktısı (.rpk) - gitignore'da
├── build/                     # ara derleme çıktısı - gitignore'da
├── package.json
└── README.md
```

### Temel Dosyalar

Dosya

Amaç

`src/manifest.json`

Vela uygulama manifesti: `package` = `com.hyperpostulate.gpsinfo`, `deviceTypeList: ["watch"]`, `minPlatformVersion: 1000`, `designWidth: 390`, tanımlı feature'lar (`system.router`, `system.geolocation`, `system.brightness`) ve `LOCATION` izni

`src/pages/index/index.ux`

Uygulamanın tamamı: şablon (GPS veri listesi + durum satırı), script (geolocation mantığı, biçimlendirme yardımcıları) ve stiller

`scripts/gen_assets.py`

`logo.png` dosyasını belirlenimci biçimde üretir; yazdığı her dosyayı geri okuyup boyut ve boş olmama kontrolünü yapar

`docs/design.md`

Yetkili UI/UX spesifikasyonu (palet, tipografi, yerleşim, durumlar, metinler)

* * *

## Ekran ve Özellikler

Uygulamanın **tek ekranı** vardır. Veri abonelikleri sayfa gösterildiğinde başlar, gizlendiğinde durur (pil tasarrufu). Veriler siyah arka plan üzerinde yeşil metin olarak gösterilir.

### Ekran — GPS

- Enlem ve boylam, ondalık derece olarak; altında daha küçük DMS satırı (`41° 00' 29.6" K`).
- İrtifa (metre, GNSS kaynaklı - Redmi Watch 4'te barometre yoktur), hız (`m/s` ve `km/h`), yatay doğruluk ve son düzeltme zamanı.
- Durum satırı: aranıyor (sarı), sinyal var (yeşil "Sinyal Güçlü") veya eşlenmiş hata (203 → "Desteklenmiyor", 204 → "Zaman Aşımı", 1000+ → "Konum Kapalı").

Her API çağrısı `try/catch` ile sarılır ve yetenek bayraklarıyla korunur; böylece eksik/başarısız bir API asla döngü içinde tekrar denenmez.

* * *

## Saate Kurulum

`.rpk` dosyası, Android telefonda yüklü **[Notify for Xiaomi](https://play.google.com/store/apps/details?id=com.mc.xiaomi1)** uygulaması (Google Play adı "Notify for Xiaomi/Mi Band 8-10", paket `com.mc.xiaomi1`, geliştirici OneZeroBit) ile Bluetooth üzerinden saate kurulur. Redmi Watch 4, uygulamanın resmî uyumluluk listesinde yer alır; uygulamanın resmî sitesi özel VelaJS (`.rpk`) uygulamalarının bu yolla kurulmasını belgeler.

> **Doğrulama durumu:** gerçek bir Redmi Watch 4 üzerinde doğrulandı — GPS Info bu yöntemle başarıyla kuruldu. Saatte GPS verisi gösterimi henüz kontrol edilmedi.

### Ön koşullar

- **Android telefon** (iOS ile `.rpk` kurulamaz).
- Google Play'den kurulmuş **Notify for Xiaomi**.
- Saatin Notify ile eşlenmiş olması: uygulamadaki kurulum sihirbazı eşleme (auth) anahtarını Xiaomi hesabınız üzerinden alır; Mi Fitness'in kurulu kalması zorunlu değildir.
- Saatin Bluetooth bağlantısını aynı anda tek uygulama tutabilir. Mi Fitness kuruluysa durdurun, "Yakındaki cihazlar" iznini kaldırın ya da uygulamayı kaldırın — ama **kaldırmadan önce saati Mi Fitness eşleşmesinden ayırmayın**.

### Adımlar

1. Paketi derleyin: `npm run build` → `dist/com.hyperpostulate.gpsinfo.debug.1.0.0.rpk`.
2. **Notify for Xiaomi**'i açın.
3. **Device** bölümüne gidin.
4. **Third party app** seçeneğini seçin.
5. `.rpk` dosyasını (`dist/com.hyperpostulate.gpsinfo.debug.1.0.0.rpk`) seçin.
6. Saati telefonun yakınında tutun ve yönlendirmeli adımları izleyin.
7. Kurulum bitince **GPS Info** saatin uygulama listesinde görünür.

### Notlar

- `npm run build` ile üretilen debug imzalı `.rpk` bu uygulama için yeterlidir: Vela sertifikayı yalnızca saat↔telefon Interconnect iletişiminde denetler; GPS Info Interconnect kullanmaz.
- Redmi Watch 4 sınırları: en fazla ~20 hızlı uygulama kurulabilir ve kurulum için ~87 MB boş alan gerekir.
- Güncelleme için yeni bir `.rpk` derleyip aynı paket adının (`com.hyperpostulate.gpsinfo`) üzerine kurun.
- Doğrulanmayan ayrıntılar: `.rpk` kurulumunu ekleyen uygulama sürümü ve özelliğin (yaklaşık 3 €, tek seferlik) PRO satın alımı gerektirip gerektirmediği resmî olarak belgelenmemiştir. Yukarıdaki menü etiketleri İngilizcedir; uygulama Türkçeleştirilmiştir ama Türkçe etiketler doğrulanamamıştır.

Kaynaklar: [Notify for Xiaomi VelaJS kurulum kılavuzu](https://mibandnotify.com/xiaomi-mi-band/notify-xms-app-instructions.php) · [Google Play sayfası](https://play.google.com/store/apps/details?id=com.mc.xiaomi1)

* * *

## Belgeler

Belge

İçerik

[docs/design.md](docs/design.md)

UI/UX spesifikasyonu: palet, tipografi ölçeği, yerleşim, durumlar, Türkçe metinler, varlık geometrisi (yalnız GPS)

* * *

## Bilinen Sınırlamalar ve Riskler

- **Redmi Watch 4'te geolocation API kullanılabilirliği doğrulanmamıştır.** Resmî Vela destek tabloları @system.geolocation API'sini Redmi Watch 4'te *desteklenmiyor* olarak işaretler; oysa saat donanımında GNSS vardır (stok uygulamalar onu kullanır). Bunu doğrulayan ya da çürüten bir topluluk raporu yoktur; uygulama zarif düşecek şekilde yazılmıştır ve kesin cevap ancak gerçek cihaz testiyle çıkar.
- **İrtifa GNSS kaynaklıdır** — Redmi Watch 4'te barometre yoktur, dolayısıyla irtifa doğruluğu doğası gereği sınırlıdır.
- **`npm audit`**, `aiot-toolkit`'in geçişli geliştirme bağımlılıklarında güvenlik açıkları bildirir. Bunlar yalnızca derleme zamanıyla ilgilidir ve `.rpk` paketine dâhil olmaz.

* * *

## Doğrulama

```
npm run build                        # başarılı olmalı ve dist/*.rpk üretmeli
python3 scripts/gen_assets.py        # PNG varlıklarını yeniden üretip kendi kendini kontrol eder
```

Cihaz üstü kontrol listesi (yukarıdaki API sorularını çözmenin tek yolu):

1. GPS ekranı koordinatları gösteriyor mu; durum `Sinyal Güçlü` mü yoksa bir hata kodu mu?
2. Uygulama açıkken ekran açık kalıyor mu?

* * *

## Lisans

Bu depoda şu anda bir lisans dosyası bulunmamaktadır. Bir lisans eklenene kadar tüm haklar yazar tarafından saklıdır.

* * *

## Geliştirici

**Mesut ORMANLI**

- E-posta: [mesutormanli@gmail.com](mailto:mesutormanli@gmail.com)
- GitHub: [@hyperpostulate](https://github.com/hyperpostulate)

* * *

## Katkıda Bulunma

1. Depoyu fork edin
2. Bir özellik dalı oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik ekle'`)
4. Dalı push edin (`git push origin feature/yeni-ozellik`)
5. Bir Pull Request oluşturun
