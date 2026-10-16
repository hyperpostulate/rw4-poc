# Pusula — Compass & GPS for Redmi Watch 4

![Platform](https://img.shields.io/badge/platform-Xiaomi%20Vela-blue)
![Device](https://img.shields.io/badge/device-Redmi%20Watch%204-orange)
![Version](https://img.shields.io/badge/version-1.0.0-green)

A two-screen compass + GPS app for the Redmi Watch 4, built as a Xiaomi Vela JS app (quick app, `.rpk`). Screen 1 is a live compass with a rotating dial; screen 2 shows raw GNSS data (latitude, longitude, altitude, speed, accuracy, fix time). The UI is Turkish and the compass falls back gracefully when a sensor API is unavailable on the device.

* * *

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Build & Run](#build--run)
- [Project Structure](#project-structure)
- [Screens & Features](#screens--features)
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

Only needed to install the `.rpk` onto the watch (see [kurulum.md](docs/kurulum.md))

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

The build produces `dist/com.hyperpostulate.rw4compass.debug.1.0.0.rpk`.

* * *

## Build & Run

```
npm install                          # Install the aiot-toolkit toolchain
npm run build                        # Build a debug .rpk into dist/
npm run release                      # Build a release .rpk (requires signing keys)
npm run start                        # aiot start --watch (live development)
python3 scripts/gen_assets.py        # Regenerate the PNG assets from code
```

The toolchain is `aiot-toolkit` (`aiot build` / `aiot release` / `aiot start`). The debug `.rpk` needs no signing; a release package needs `sign/private.pem` and `sign/certificate.pem` (generate with OpenSSL). Deployment to the watch itself is described in [docs/kurulum.md](docs/kurulum.md).

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
│   │   ├── dial.png           # generated compass dial, 360x360
│   │   ├── index-marker.png   # generated fixed index marker, 40x40
│   │   └── logo.png           # generated app icon, 192x192
│   └── pages/
│       └── index/
│           └── index.ux       # single page: vertical swiper (Pusula + GPS) + all logic
├── scripts/
│   └── gen_assets.py          # reproducible Pillow generator for the PNG assets
├── docs/
│   ├── design.md              # UI/UX design specification (Turkish)
│   └── kurulum.md             # step-by-step .rpk installation guide (Turkish)
├── dist/                      # build output (.rpk) - gitignored
├── build/                     # intermediate build output - gitignored
├── package.json
└── README.md
```

### Core Files

File

Purpose

`src/manifest.json`

Vela app manifest: `package` = `com.hyperpostulate.rw4compass`, `deviceTypeList: ["watch"]`, `minPlatformVersion: 1200`, `designWidth: 390`, declared features (`system.router`, `system.geolocation`, `system.sensor`, `system.brightness`) and the `LOCATION` permission

`src/pages/index/index.ux`

The whole app: template (two swiper pages), script (sensor/GPS logic, fallback chain, formatting helpers) and styles

`scripts/gen_assets.py`

Generates `dial.png`, `index-marker.png` and `logo.png` deterministically; re-reads every file it writes and asserts dimensions and non-blank content

`docs/design.md`

The authoritative UI/UX spec (palette, typography, layout, states, copy)

`docs/kurulum.md`

Installation guide for getting the `.rpk` onto a Redmi Watch 4

* * *

## Screens & Features

Navigation is a **vertical swipe** between the two screens (`swiper` with `vertical="true"`, indicator dots off). Data subscriptions start on page show and stop on page hide to save battery; the compass sensor subscription is also stopped while the GPS screen is visible.

### Screen 1 — Compass ("Pusula")

- A rotating `dial.png` (North marked with a red accent line) with a fixed index marker at the top and the heading readout in the dial's empty center.
- Large degree readout (`247°`) plus the Turkish cardinal abbreviation (`K`, `KD`, `D`, `GD`, `G`, `GB`, `B`, `KB`).
- Source badge: `MANYETO` (magnetometer), `GPS YÖNÜ` (GPS fallback), or `SENSÖR DESTEKLENMİYOR`.
- Accuracy dot for the compass sensor (high / medium / low / disconnected / unknown).
- Software angle wrapping so `359° → 0°` takes the short path, with a `120ms linear` CSS transition on the dial only (readout and marker never rotate).

### Screen 2 — GPS

- Latitude and longitude in decimal degrees plus a smaller DMS line (`41° 00' 29.6" K`).
- Altitude (metres, GNSS-derived - the Redmi Watch 4 has no barometer), speed (`m/s` and `km/h`), horizontal accuracy, and the last fix time.
- A status row: searching (pulsing yellow), fix acquired (green "Sinyal Güçlü"), or a mapped error (203 → "Desteklenmiyor", 204 → "Zaman Aşımı", 1000+ → "Konum Kapalı").

### Heading Fallback Chain

1. **Magnetometer** — `@system.sensor.subscribeCompass`; direction in radians is converted to degrees.
2. **GPS course-over-ground** — when the compass is unavailable, the bearing between consecutive fixes is used, but only while moving (speed ≥ 0.5 m/s and ≥ 3 m between fixes). The badge shows `GPS YÖNÜ`.
3. **Explicit unavailable state** — if neither source works, the app shows `SENSÖR DESTEKLENMİYOR` instead of guessing.

Every API call is wrapped in `try/catch` and guarded by capability flags, so a missing or failing API is never retried in a loop.

* * *

## Installing on the Watch

The `.rpk` is installed from an Android phone over Bluetooth. The stock Mi Fitness build does **not** expose the third-party app installer, so the practical paths are the community tools, with an open-source experimental alternative:

Path

Status

Mi Fitness "Debug → Third-Party Apps"

Official, but requires a special developer build of Mi Fitness (not the public one)

表盘自定义工具 + Shizuku

Widely used community path; proven on the Redmi Watch 4

小米穿戴 debug APK

Community debug build; simplest, unofficial APK source

Gadgetbridge

Experimental - `.rpk` support exists since 0.91.0 but was tested on Mi Band 9, **not** on the Redmi Watch 4

Full step-by-step instructions, prerequisites, troubleshooting and safety notes: **[docs/kurulum.md](docs/kurulum.md)**.

* * *

## Documentation

Document

Contents

[docs/design.md](docs/design.md)

UI/UX specification: palette, typography scale, layout, states, Turkish copy, asset geometry

[docs/kurulum.md](docs/kurulum.md)

How to install the `.rpk` on a Redmi Watch 4, including the Gadgetbridge experiment

* * *

## Known Limitations & Risks

- **API availability on the Redmi Watch 4 is unverified.** The official Vela support tables mark `@system.geolocation` and `@system.sensor` (compass) as *not supported* on the Redmi Watch 4, even though the watch hardware has GNSS and a magnetometer (the stock compass app works). No public community report confirms or denies it; the app is built to degrade gracefully and the answer only comes from a real-device test.
- **Altitude is GNSS-derived** — the Redmi Watch 4 has no barometer, so altitude accuracy is inherently limited.
- **Compass dial labels rotate with the dial**, as on a physical compass dial (a deliberate design choice).
- **Vela specifics:** the framework has no `swiper-item` component (direct `div` children are used instead), layers are stacked with `position: absolute`, and `letter-spacing` is not in the supported style list, so it is omitted on the badge.
- **`npm audit` reports vulnerabilities in transitive dev dependencies** of `aiot-toolkit`. They are build-time only and do not ship inside the `.rpk`.

* * *

## Verification

```
npm run build                        # must succeed and emit dist/*.rpk
python3 scripts/gen_assets.py        # regenerates and self-checks the PNG assets
```

On-device checklist (the only way to resolve the API questions above):

1. Which badge does the compass screen show - `MANYETO`, `GPS YÖNÜ` or `SENSÖR DESTEKLENMİYOR`?
2. Does the letter under the index marker match the degree reading while turning the watch (e.g. `D` near 90°)?
3. Does the GPS screen show coordinates, and is the status `Sinyal Güçlü` or an error code?
4. Does the vertical swipe work, and does the screen stay awake while the app is open?

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

## Pusula — Redmi Watch 4 için Pusula ve GPS

![Platform](https://img.shields.io/badge/platform-Xiaomi%20Vela-blue)
![Device](https://img.shields.io/badge/device-Redmi%20Watch%204-orange)
![Version](https://img.shields.io/badge/version-1.0.0-green)

Redmi Watch 4 için iki ekranlı pusula + GPS uygulaması; Xiaomi Vela JS uygulaması (hızlı uygulama, `.rpk`) olarak geliştirilmiştir. Birinci ekran dönen kadranlı canlı bir pusuladır; ikinci ekran GNSS verilerini (enlem, boylam, irtifa, hız, doğruluk, düzeltme zamanı) gösterir. Arayüz Türkçedir ve cihazda bir sensör API'si yoksa pusula zarif biçimde düşer.

* * *

## İçindekiler

- [Gereksinimler](#gereksinimler)
- [Kurulum](#kurulum)
- [Derleme ve Çalıştırma](#derleme-ve-çalıştırma)
- [Proje Yapısı](#proje-yapısı)
- [Ekranlar ve Özellikler](#ekranlar-ve-özellikler)
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

Yalnızca `.rpk` dosyasını saate kurmak için gerekir (bkz. [kurulum.md](docs/kurulum.md))

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

Derleme `dist/com.hyperpostulate.rw4compass.debug.1.0.0.rpk` dosyasını üretir.

* * *

## Derleme ve Çalıştırma

```
npm install                          # aiot-toolkit araç zincirini kur
npm run build                        # dist/ içine debug .rpk derle
npm run release                      # release .rpk derle (imza anahtarları gerekir)
npm run start                        # aiot start --watch (canlı geliştirme)
python3 scripts/gen_assets.py        # PNG varlıklarını koddan yeniden üret
```

Araç zinciri `aiot-toolkit`'tir (`aiot build` / `aiot release` / `aiot start`). Debug `.rpk` imza gerektirmez; release paketi için `sign/private.pem` ve `sign/certificate.pem` gerekir (OpenSSL ile üretilir). Saate kurulumun kendisi [docs/kurulum.md](docs/kurulum.md) içinde anlatılır.

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
│   │   ├── dial.png           # üretilen pusula kadranı, 360x360
│   │   ├── index-marker.png   # üretilen sabit indeks işaretçisi, 40x40
│   │   └── logo.png           # üretilen uygulama ikonu, 192x192
│   └── pages/
│       └── index/
│           └── index.ux       # tek sayfa: dikey swiper (Pusula + GPS) + tüm mantık
├── scripts/
│   └── gen_assets.py          # PNG varlıkları için tekrarlanabilir Pillow üreteci
├── docs/
│   ├── design.md              # UI/UX tasarım spesifikasyonu
│   └── kurulum.md             # adım adım .rpk kurulum kılavuzu
├── dist/                      # derleme çıktısı (.rpk) - gitignore'da
├── build/                     # ara derleme çıktısı - gitignore'da
├── package.json
└── README.md
```

### Temel Dosyalar

Dosya

Amaç

`src/manifest.json`

Vela uygulama manifesti: `package` = `com.hyperpostulate.rw4compass`, `deviceTypeList: ["watch"]`, `minPlatformVersion: 1200`, `designWidth: 390`, tanımlı feature'lar (`system.router`, `system.geolocation`, `system.sensor`, `system.brightness`) ve `LOCATION` izni

`src/pages/index/index.ux`

Uygulamanın tamamı: şablon (iki swiper sayfası), script (sensör/GPS mantığı, düşüş zinciri, biçimlendirme yardımcıları) ve stiller

`scripts/gen_assets.py`

`dial.png`, `index-marker.png` ve `logo.png` dosyalarını belirlenimci biçimde üretir; yazdığı her dosyayı geri okuyup boyut ve boş olmama kontrolünü yapar

`docs/design.md`

Yetkili UI/UX spesifikasyonu (palet, tipografi, yerleşim, durumlar, metinler)

`docs/kurulum.md`

`.rpk` dosyasının Redmi Watch 4'e kurulması kılavuzu

* * *

## Ekranlar ve Özellikler

Ekranlar arası geçiş **dikey kaydırmadır** (`vertical="true"` swiper, nokta göstergesi kapalı). Veri abonelikleri sayfa gösterildiğinde başlar, gizlendiğinde durur (pil tasarrufu); GPS ekranı görünürken pusula sensörü aboneliği de durdurulur.

### Ekran 1 — Pusula

- Dönen `dial.png` (kuzey, kırmızı vurgu çizgisiyle işaretli), üstte sabit indeks işaretçisi ve kadranın boş merkezinde yön okuması.
- Büyük derece okuması (`247°`) ve Türkçe ana yön kısaltması (`K`, `KD`, `D`, `GD`, `G`, `GB`, `B`, `KB`).
- Kaynak rozeti: `MANYETO` (manyetometre), `GPS YÖNÜ` (GPS yedeği) veya `SENSÖR DESTEKLENMİYOR`.
- Pusula sensörü için hassasiyet noktası (yüksek / orta / düşük / bağlantı kesik / bilinmiyor).
- Yazılımsal açı sarma ile `359° → 0°` geçişi kısa yolu izler; kadrana özel `120ms linear` CSS geçişi kullanılır (okuma ve işaretçi asla dönmez).

### Ekran 2 — GPS

- Enlem ve boylam, ondalık derece olarak; altında daha küçük DMS satırı (`41° 00' 29.6" K`).
- İrtifa (metre, GNSS kaynaklı - Redmi Watch 4'te barometre yoktur), hız (`m/s` ve `km/h`), yatay doğruluk ve son düzeltme zamanı.
- Durum satırı: aranıyor (sarı, nabız animasyonlu), sinyal var (yeşil "Sinyal Güçlü") veya eşlenmiş hata (203 → "Desteklenmiyor", 204 → "Zaman Aşımı", 1000+ → "Konum Kapalı").

### Yön Düşüş Zinciri

1. **Manyetometre** — `@system.sensor.subscribeCompass`; radyan cinsinden yön dereceye çevrilir.
2. **GPS hareket yönü** — pusula yoksa ardışık düzeltmeler arası kerteriz kullanılır; yalnızca hareket halinde (hız ≥ 0.5 m/s ve düzeltmeler arası ≥ 3 m). Rozet `GPS YÖNÜ` gösterir.
3. **Açık "desteklenmiyor" durumu** — iki kaynak da çalışmazsa uygulama tahmin yürütmek yerine `SENSÖR DESTEKLENMİYOR` gösterir.

Her API çağrısı `try/catch` ile sarılır ve yetenek bayraklarıyla korunur; böylece eksik/başarısız bir API asla döngü içinde tekrar denenmez.

* * *

## Saate Kurulum

`.rpk` dosyası bir Android telefondan Bluetooth üzerinden kurulur. Stok Mi Fitness, üçüncü taraf uygulama kurucusunu **sunmaz**; bu yüzden pratik yollar topluluk araçlarıdır ve açık kaynaklı deneysel bir alternatif vardır:

Yol

Durum

Mi Fitness "Debug → Third-Party Apps"

Resmî, ama özel bir geliştirici Mi Fitness sürümü gerektirir (herkese açık sürümde yok)

表盘自定义工具 + Shizuku

En yaygın topluluk yolu; Redmi Watch 4'te kanıtlanmış

小米穿戴 debug APK

Topluluk debug sürümü; en kolayı, APK kaynağı gayri resmi

Gadgetbridge

Deneysel - `.rpk` desteği 0.91.0'dan beri var ama Mi Band 9'da test edildi, Redmi Watch 4'te **değil**

Adım adım anlatım, ön koşullar, sorun giderme ve güvenlik notları: **[docs/kurulum.md](docs/kurulum.md)**.

* * *

## Belgeler

Belge

İçerik

[docs/design.md](docs/design.md)

UI/UX spesifikasyonu: palet, tipografi ölçeği, yerleşim, durumlar, Türkçe metinler, varlık geometrisi

[docs/kurulum.md](docs/kurulum.md)

`.rpk` dosyasının Redmi Watch 4'e kurulması, Gadgetbridge denemesi dâhil

* * *

## Bilinen Sınırlamalar ve Riskler

- **Redmi Watch 4'te API kullanılabilirliği doğrulanmamıştır.** Resmî Vela destek tabloları `@system.geolocation` ve `@system.sensor` (pusula) API'lerini Redmi Watch 4'te *desteklenmiyor* olarak işaretler; oysa saat donanımında GNSS ve manyetometre vardır (stok pusula uygulaması çalışır). Bunu doğrulayan ya da çürüten bir topluluk raporu yoktur; uygulama zarif düşecek şekilde yazılmıştır ve kesin cevap ancak gerçek cihaz testiyle çıkar.
- **İrtifa GNSS kaynaklıdır** — Redmi Watch 4'te barometre yoktur, dolayısıyla irtifa doğruluğu doğası gereği sınırlıdır.
- **Kadran harfleri kadranla birlikte döner**, tıpkı fiziksel bir pusula kadranında olduğu gibi (bilinçli bir tasarım kararı).
- **Vela'ya özgü ayrıntılar:** çerçevede `swiper-item` bileşeni yoktur (doğrudan `div` çocukları kullanılır), katmanlar `position: absolute` ile üst üste bindirilir ve `letter-spacing` desteklenen stil listesinde olmadığı için rozette kullanılmaz.
- **`npm audit`**, `aiot-toolkit`'in geçişli geliştirme bağımlılıklarında güvenlik açıkları bildirir. Bunlar yalnızca derleme zamanıyla ilgilidir ve `.rpk` paketine dâhil olmaz.

* * *

## Doğrulama

```
npm run build                        # başarılı olmalı ve dist/*.rpk üretmeli
python3 scripts/gen_assets.py        # PNG varlıklarını yeniden üretip kendi kendini kontrol eder
```

Cihaz üstü kontrol listesi (yukarıdaki API sorularını çözmenin tek yolu):

1. Pusula ekranı hangi rozeti gösteriyor - `MANYETO`, `GPS YÖNÜ` yoksa `SENSÖR DESTEKLENMİYOR`?
2. Saati çevirirken indeks işaretçisinin altındaki harf, derece okumasıyla uyuşuyor mu (ör. 90° civarında `D`)?
3. GPS ekranı koordinatları gösteriyor mu; durum `Sinyal Güçlü` mü yoksa bir hata kodu mu?
4. Dikey kaydırma çalışıyor mu ve uygulama açıkken ekran açık kalıyor mu?

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
