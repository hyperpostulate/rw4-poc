# rw4-poc — Redmi Watch 4 Vela Time PoC

![Platform](https://img.shields.io/badge/platform-Xiaomi%20Vela-blue)
![Device](https://img.shields.io/badge/device-Redmi%20Watch%204-orange)
![Version](https://img.shields.io/badge/version-1.0.0-green)

A minimal Xiaomi Vela JS quick app (`.rpk`) for the Redmi Watch 4. One screen, black background, green values, four fields read from the device clock:

| Field | Meaning | Example |
| :-- | :-- | :-- |
| **Tarih** | Local date | `2026-10-18` |
| **Saat** | Local time (updates every second) | `14:23:05` |
| **Dilim** | UTC offset | `UTC+03:00` |
| **Unix** | Unix timestamp (seconds) | `1760797385` |

The app is deliberately tiny. Its real value is documenting **what a third-party quick app can and cannot do on the Redmi Watch 4**, which was verified on real hardware — see [On-device findings](#on-device-findings).

* * *

## Table of Contents

- [On-device findings](#on-device-findings)
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

## On-device findings

Everything below was verified on a **real Redmi Watch 4**; the official Xiaomi Vela support tables agree.

### Text does not render

- `<text>`, `<span>` and native widgets (`<input type="button">`, `<input type="text">`) paint **no readable glyphs** on this unit (nothing, or notdef "tofu" boxes). A bundled `@font-face` font had zero effect.
- `<image>`, `<div>`, `background-color`, `<style>`/`class` all render correctly.
- **Consequence:** every visible string in this app is a **pre-rendered PNG**. Static labels are single images; dynamic values are composed character-by-character from a monospace **glyph atlas** (`src/common/txt/g_<hex>.png`, one PNG per codepoint) using the `for` directive. `scripts/gen_assets.py` generates all of them deterministically.

### Which system APIs actually work

| API | Redmi Watch 4 |
| :-- | :-- |
| `@system.geolocation` (GPS) | ❌ not supported (error `203`) |
| `@system.sensor` (accelerometer / pressure / compass) | ❌ not supported |
| `@system.battery` (level) | ❌ not supported |
| `@system.network` | ❌ not supported |
| `@system.bluetooth`, `@system.record`, `@system.fetch`, `@system.crypto` | ❌ not supported |
| `@system.device` (`getInfo`, storage sizes) | ✅ works |
| `@system.storage` (local key/value) | ✅ works |
| `@system.brightness` | ✅ works |
| `@system.app` | ✅ works |
| `vibrator.vibrate()` | ✅ the only supported entry in the vibrator table |
| JS clock (`new Date()`) | ✅ always available |

There is **no GNSS sensor API** in Vela and **no step/heart-rate/health API** exposed to quick apps at all. The watch's GNSS hardware is reserved for Xiaomi's native apps, so a GPS/location quick app is impossible on this device. That is why this repository ships a clock PoC (the one live data every Vela quick app can read).

> `203` is the Vela system code for *"this function is not supported"* (a permission problem would be `400`/`402`). It is not recoverable by the app.

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

The build produces `dist/com.hyperpostulate.rw4poc.debug.1.0.0.rpk`.

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

* * *

## Project Structure

```
redmi-watch4-compass/
├── src/
│   ├── manifest.json          # package com.hyperpostulate.rw4poc, name "RW4 - PoC", designWidth 390
│   ├── app.ux                 # app entry (onCreate/onDestroy)
│   ├── i18n/
│   │   └── defaults.json      # default string bundle
│   ├── common/
│   │   ├── logo.png           # generated app icon (watch), 192x192
│   │   └── txt/               # generated PNG text: labels, title and the glyph atlas (g_<hex>.png)
│   └── pages/
│       └── index/
│           └── index.ux       # the whole app: title + 4 rows + clock logic
├── scripts/
│   ├── gen_assets.py          # reproducible Pillow generator for every PNG asset
│   └── assets/
│       └── gpsinfo.ttf        # font used only at generation time (not shipped)
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

Vela app manifest: `package` = `com.hyperpostulate.rw4poc`, `name` = `RW4 - PoC`, `deviceTypeList: ["watch"]`, `designWidth: 390`, `features: ["system.router"]` (the PoC uses no other system API)

`src/pages/index/index.ux`

The whole app: template (title + four label/value rows), script (clock formatting + glyph mapping) and styles

`scripts/gen_assets.py`

Generates the title, the labels, the app icon and the glyph atlas deterministically; re-reads every file it writes and asserts dimensions and non-blank content

`docs/design.md`

The authoritative UI/UX spec (palette, geometry, text-as-image approach)

* * *

## Screen & Features

The app has a **single screen**. A one-second interval keeps the clock fresh; it starts on page show and stops on page hide to save battery. All values are green on a black background.

- **Tarih** — local date, `YYYY-AA-GG`.
- **Saat** — local time, `SS:DD:SS`, updated every second.
- **Dilim** — UTC offset derived from `Date.getTimezoneOffset()`, e.g. `UTC+03:00`.
- **Unix** — `Math.floor(Date.now() / 1000)`, the device time as a Unix timestamp.

No permission is requested: the JS clock needs none.

* * *

## Installing on the Watch

The `.rpk` is installed over Bluetooth from an Android phone using the **[Notify for Xiaomi](https://play.google.com/store/apps/details?id=com.mc.xiaomi1)** app (Google Play listing "Notify for Xiaomi/Mi Band 8-10", package `com.mc.xiaomi1`, by OneZeroBit). The Redmi Watch 4 is on the app's official compatibility list, and the app's official site documents installing custom VelaJS (`.rpk`) apps this way.

> **Verification status:** verified on a real Redmi Watch 4 — this PoC installs and runs correctly with this method.

### Prerequisites

- An **Android phone** (iOS cannot install `.rpk` files).
- **Notify for Xiaomi** installed from Google Play.
- The watch paired with Notify: the in-app setup wizard fetches the pairing (auth) key through your Xiaomi account, so Mi Fitness does not need to stay installed.
- Only one app can hold the watch's Bluetooth connection at a time. If Mi Fitness is installed, force-stop it, deny its "Nearby devices" permission, or uninstall it — but **do not un-pair the watch from Mi Fitness before uninstalling**.

### Steps

1. Build the package: `npm run build` → `dist/com.hyperpostulate.rw4poc.debug.1.0.0.rpk`.
2. Open **Notify for Xiaomi**.
3. Go to **Device**.
4. Select **Third party app**.
5. Select the `.rpk` file (`dist/com.hyperpostulate.rw4poc.debug.1.0.0.rpk`).
6. Keep the watch near the phone and follow the guided steps.
7. When the installation finishes, **RW4 - PoC** appears in the watch's app list.

### Notes

- The debug-signed `.rpk` produced by `npm run build` is fine for this app: Vela only checks the certificate for watch↔phone Interconnect communication, which this PoC does not use.
- Redmi Watch 4 limits: at most ~20 quick apps installed, and ~87 MB of free space is required for quick-app installs.
- To update, build a new `.rpk` and install it over the same package name (`com.hyperpostulate.rw4poc`). Changing the `package` value installs a **separate** app instead of updating.
- Unverified details: the app version that introduced `.rpk` installs, and whether the feature requires the (about €3, one-time) PRO purchase, are not officially documented. The menu labels above are the English ones; the app itself is localized, but the Turkish labels were not verified.

Sources: [Notify for Xiaomi VelaJS install guide](https://mibandnotify.com/xiaomi-mi-band/notify-xms-app-instructions.php) · [Google Play listing](https://play.google.com/store/apps/details?id=com.mc.xiaomi1)

* * *

## Documentation

Document

Contents

[docs/design.md](docs/design.md)

UI/UX specification: palette, geometry, the text-as-image approach, glyph atlas rules

* * *

## Known Limitations & Risks

- **No GPS/location is possible** on the Redmi Watch 4 from a quick app (see [On-device findings](#on-device-findings)). This repository is a platform PoC, not a GPS app.
- **Text must be images.** Adding new *dynamic* strings requires extending the glyph atlas in `scripts/gen_assets.py` (add the characters to `CHARS`) and rebuilding; characters outside the atlas render as `?`.
- **Symbolic links / large glyph sets slow the app down.** Drawing hundreds of `<image>` elements noticeably slows the screen; keep the number of on-screen glyph images small.
- **`npm audit` reports vulnerabilities in transitive dev dependencies** of `aiot-toolkit`. They are build-time only and do not ship inside the `.rpk`.

* * *

## Verification

```
npm run build                        # must succeed and emit dist/*.rpk
python3 scripts/gen_assets.py        # regenerates and self-checks the PNG assets
```

On-device checklist:

1. Do the four values (Tarih, Saat, Dilim, Unix) render and match the phone?
2. Does `Saat` advance every second?
3. Is the app responsive (no visible lag)?

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

# rw4-poc — Redmi Watch 4 Vela Zaman PoC

![Platform](https://img.shields.io/badge/platform-Xiaomi%20Vela-blue)
![Device](https://img.shields.io/badge/device-Redmi%20Watch%204-orange)
![Version](https://img.shields.io/badge/version-1.0.0-green)

Redmi Watch 4 için minimal bir Xiaomi Vela JS hızlı uygulaması (`.rpk`). Tek ekran, siyah arka plan, yeşil değerler; cihaz saatinden okunan dört alan:

| Alan | Anlamı | Örnek |
| :-- | :-- | :-- |
| **Tarih** | Yerel tarih | `2026-10-18` |
| **Saat** | Yerel saat (her saniye güncellenir) | `14:23:05` |
| **Dilim** | UTC farkı | `UTC+03:00` |
| **Unix** | Unix zaman damgası (saniye) | `1760797385` |

Uygulama bilinçli olarak çok küçüktür. Asıl değeri, bir üçüncü taraf hızlı uygulamanın **Redmi Watch 4'te neleri yapabildiğini/yapamadığını** gerçek donanımda belgelemesidir — bkz. [Cihaz üstü bulgular](#cihaz-üstü-bulgular).

* * *

## İçindekiler

- [Cihaz üstü bulgular](#cihaz-üstü-bulgular)
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

## Cihaz üstü bulgular

Aşağıdaki her şey **gerçek bir Redmi Watch 4** üzerinde doğrulandı; resmî Xiaomi Vela destek tabloları da bunu doğruluyor.

### Metin çizilmiyor

- `<text>`, `<span>` ve yerel widget'lar (`<input type="button">`, `<input type="text">`) bu cihazda **okunabilir glif çizmiyor** (hiçbir şey ya da notdef "tofu" kutuları). Paketlenen bir `@font-face` fontunun hiçbir etkisi olmadı.
- `<image>`, `<div>`, `background-color`, `<style>`/`class` düzgün çalışıyor.
- **Sonuç:** bu uygulamadaki her görünür yazı **önceden üretilmiş PNG**'dir. Statik etiketler tek görseldir; dinamik değerler ise tek aralıklı (monospace) bir **glif atlasından** (`src/common/txt/g_<hex>.png`, her kod noktası için bir PNG) karakter karakter `for` yönergesiyle dizilir. Tümünü `scripts/gen_assets.py` belirlenimci biçimde üretir.

### Hangi sistem API'leri gerçekten çalışıyor

| API | Redmi Watch 4 |
| :-- | :-- |
| `@system.geolocation` (GPS) | ❌ desteklenmiyor (hata `203`) |
| `@system.sensor` (ivmeölçer / basınç / pusula) | ❌ desteklenmiyor |
| `@system.battery` (pil) | ❌ desteklenmiyor |
| `@system.network` | ❌ desteklenmiyor |
| `@system.bluetooth`, `@system.record`, `@system.fetch`, `@system.crypto` | ❌ desteklenmiyor |
| `@system.device` (`getInfo`, depolama boyutları) | ✅ çalışıyor |
| `@system.storage` (yerel anahtar/değer) | ✅ çalışıyor |
| `@system.brightness` | ✅ çalışıyor |
| `@system.app` | ✅ çalışıyor |
| `vibrator.vibrate()` | ✅ titreşim tablosundaki tek destekli giriş |
| JS saati (`new Date()`) | ✅ her zaman kullanılabilir |

Vela'da **GNSS sensör API'si yoktur** ve hızlı uygulamalara açık **adım/nabız/sağlık API'si hiç yoktur**. Saatin GNSS donanımı Xiaomi'nin yerleşik uygulamalarına ayrılmıştır; dolayısıyla bu cihazda bir GPS/konum hızlı uygulaması imkânsızdır. Bu depo bu yüzden bir saat PoC'si içerir (her Vela hızlı uygulamasının okuyabildiği tek canlı veri).

> `203`, Vela'nın *"bu işlev desteklenmiyor"* sistem kodudur (izin sorunu olsaydı `400`/`402` olurdu). Uygulama tarafından giderilemez.

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

Derleme `dist/com.hyperpostulate.rw4poc.debug.1.0.0.rpk` dosyasını üretir.

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

* * *

## Proje Yapısı

```
redmi-watch4-compass/
├── src/
│   ├── manifest.json          # paket com.hyperpostulate.rw4poc, ad "RW4 - PoC", designWidth 390
│   ├── app.ux                 # uygulama girişi (onCreate/onDestroy)
│   ├── i18n/
│   │   └── defaults.json      # varsayılan metin paketi
│   ├── common/
│   │   ├── logo.png           # üretilen uygulama ikonu (saat), 192x192
│   │   └── txt/               # üretilen PNG metinler: etiketler, başlık ve glif atlası (g_<hex>.png)
│   └── pages/
│       └── index/
│           └── index.ux       # uygulamanın tamamı: başlık + 4 satır + saat mantığı
├── scripts/
│   ├── gen_assets.py          # her PNG varlığı için tekrarlanabilir Pillow üreteci
│   └── assets/
│       └── gpsinfo.ttf        # yalnızca üretim zamanında kullanılan font (pakete girmez)
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

Vela uygulama manifesti: `package` = `com.hyperpostulate.rw4poc`, `name` = `RW4 - PoC`, `deviceTypeList: ["watch"]`, `designWidth: 390`, `features: ["system.router"]` (PoC başka sistem API'si kullanmaz)

`src/pages/index/index.ux`

Uygulamanın tamamı: şablon (başlık + dört etiket/değer satırı), script (saat biçimlendirme + glif eşleme) ve stiller

`scripts/gen_assets.py`

Başlığı, etiketleri, uygulama ikonunu ve glif atlasını belirlenimci biçimde üretir; yazdığı her dosyayı geri okuyup boyut ve boş olmama kontrolünü yapar

`docs/design.md`

Yetkili UI/UX spesifikasyonu (palet, geometri, metin-görsel yaklaşımı)

* * *

## Ekran ve Özellikler

Uygulamanın **tek ekranı** vardır. Bir saniyelik zamanlayıcı saati taze tutar; sayfa gösterildiğinde başlar, gizlendiğinde durur (pil tasarrufu). Tüm değerler siyah arka plan üzerinde yeşildir.

- **Tarih** — yerel tarih, `YYYY-AA-GG`.
- **Saat** — yerel saat, `SS:DD:SS`, her saniye güncellenir.
- **Dilim** — `Date.getTimezoneOffset()`'tan türetilen UTC farkı, ör. `UTC+03:00`.
- **Unix** — `Math.floor(Date.now() / 1000)`, cihaz zamanının Unix zaman damgası.

Hiçbir izin istenmez: JS saati hiçbir izin gerektirmez.

* * *

## Saate Kurulum

`.rpk` dosyası, Android telefonda yüklü **[Notify for Xiaomi](https://play.google.com/store/apps/details?id=com.mc.xiaomi1)** uygulaması (Google Play adı "Notify for Xiaomi/Mi Band 8-10", paket `com.mc.xiaomi1`, geliştirici OneZeroBit) ile Bluetooth üzerinden saate kurulur. Redmi Watch 4, uygulamanın resmî uyumluluk listesinde yer alır; uygulamanın resmî sitesi özel VelaJS (`.rpk`) uygulamalarının bu yolla kurulmasını belgeler.

> **Doğrulama durumu:** gerçek bir Redmi Watch 4 üzerinde doğrulandı — bu PoC bu yöntemle sorunsuz kurulup çalışıyor.

### Ön koşullar

- **Android telefon** (iOS ile `.rpk` kurulamaz).
- Google Play'den kurulmuş **Notify for Xiaomi**.
- Saatin Notify ile eşlenmiş olması: uygulamadaki kurulum sihirbazı eşleme (auth) anahtarını Xiaomi hesabınız üzerinden alır; Mi Fitness'in kurulu kalması zorunlu değildir.
- Saatin Bluetooth bağlantısını aynı anda tek uygulama tutabilir. Mi Fitness kuruluysa durdurun, "Yakındaki cihazlar" iznini kaldırın ya da uygulamayı kaldırın — ama **kaldırmadan önce saati Mi Fitness eşleşmesinden ayırmayın**.

### Adımlar

1. Paketi derleyin: `npm run build` → `dist/com.hyperpostulate.rw4poc.debug.1.0.0.rpk`.
2. **Notify for Xiaomi**'i açın.
3. **Device** bölümüne gidin.
4. **Third party app** seçeneğini seçin.
5. `.rpk` dosyasını (`dist/com.hyperpostulate.rw4poc.debug.1.0.0.rpk`) seçin.
6. Saati telefonun yakınında tutun ve yönlendirmeli adımları izleyin.
7. Kurulum bitince **RW4 - PoC** saatin uygulama listesinde görünür.

### Notlar

- `npm run build` ile üretilen debug imzalı `.rpk` bu uygulama için yeterlidir: Vela sertifikayı yalnızca saat↔telefon Interconnect iletişiminde denetler; bu PoC Interconnect kullanmaz.
- Redmi Watch 4 sınırları: en fazla ~20 hızlı uygulama kurulabilir ve kurulum için ~87 MB boş alan gerekir.
- Güncelleme için yeni bir `.rpk` derleyip aynı paket adının (`com.hyperpostulate.rw4poc`) üzerine kurun. `package` değerini değiştirmek güncelleme yerine **ayrı** bir uygulama kurar.
- Doğrulanmayan ayrıntılar: `.rpk` kurulumunu ekleyen uygulama sürümü ve özelliğin (yaklaşık 3 €, tek seferlik) PRO satın alımı gerektirip gerektirmediği resmî olarak belgelenmemiştir. Yukarıdaki menü etiketleri İngilizcedir; uygulama Türkçeleştirilmiştir ama Türkçe etiketler doğrulanamamıştır.

Kaynaklar: [Notify for Xiaomi VelaJS kurulum kılavuzu](https://mibandnotify.com/xiaomi-mi-band/notify-xms-app-instructions.php) · [Google Play sayfası](https://play.google.com/store/apps/details?id=com.mc.xiaomi1)

* * *

## Belgeler

Belge

İçerik

[docs/design.md](docs/design.md)

UI/UX spesifikasyonu: palet, geometri, metin-görsel yaklaşımı, glif atlası kuralları

* * *

## Bilinen Sınırlamalar ve Riskler

- **Redmi Watch 4'te GPS/konum bir hızlı uygulamayla mümkün değildir** (bkz. [Cihaz üstü bulgular](#cihaz-üstü-bulgular)). Bu depo bir GPS uygulaması değil, bir platform PoC'sidir.
- **Metin görsel olmak zorundadır.** Yeni *dinamik* metin eklemek, `scripts/gen_assets.py` içindeki glif atlasını (`CHARS`'a karakter ekleyerek) genişletmeyi ve yeniden derlemeyi gerektirir; atlas dışındaki karakterler `?` olarak çizilir.
- **Yüzlerce `<image>` ekranı yavaşlatır.** Çok sayıda glif görseli çizmek ekranı belirgin biçimde yavaşlatır; ekrandaki glif görseli sayısını az tutun.
- **`npm audit`**, `aiot-toolkit`'in geçişli geliştirme bağımlılıklarında güvenlik açıkları bildirir. Bunlar yalnızca derleme zamanıyla ilgilidir ve `.rpk` paketine dâhil olmaz.

* * *

## Doğrulama

```
npm run build                        # başarılı olmalı ve dist/*.rpk üretmeli
python3 scripts/gen_assets.py        # PNG varlıklarını yeniden üretip kendi kendini kontrol eder
```

Cihaz üstü kontrol listesi:

1. Dört değer (Tarih, Saat, Dilim, Unix) çiziliyor ve telefonla uyuşuyor mu?
2. `Saat` her saniye ilerliyor mu?
3. Uygulama akıcı mı (görünür gecikme yok mu)?

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
