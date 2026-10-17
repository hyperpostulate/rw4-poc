# rw4-poc — Redmi Watch 4 Vela Time PoC

![Platform](https://img.shields.io/badge/platform-Xiaomi%20Vela-blue)
![Device](https://img.shields.io/badge/device-Redmi%20Watch%204-orange)
![Version](https://img.shields.io/badge/version-1.0.0-green)

A minimal Xiaomi Vela JS quick app (`.rpk`) for the Redmi Watch 4. The project began as a GPS/compass idea, but the watch exposes **no GNSS or health API** to third-party apps, so GPS is impossible on this device (see [On-device findings](#on-device-findings)). What ships instead is a **platform PoC**: the smallest useful app — a clock — that documents what a Vela quick app can and cannot do here.

* * *

## Table of Contents

- [What this is](#what-this-is)
- [What it shows](#what-it-shows)
- [Install on the Watch](#install-on-the-watch)
- [Build & Run](#build--run)
- [Project Structure](#project-structure)
- [On-device findings](#on-device-findings)
- [Limitations](#limitations)
- [License](#license)
- [Developer](#developer)
- [Contributing](#contributing)

* * *

## What this is

The repository started as a GPS/compass experiment; on-device testing proved a GPS quick app cannot exist on the Redmi Watch 4, so it became a platform PoC instead. It is deliberately tiny: one screen, no permissions, and a written record of what a third-party Vela quick app can actually do.

## What it shows

One screen — black background, green values — with exactly four fields read from the device clock:

| Field | Meaning | Example |
| :-- | :-- | :-- |
| **Tarih** | Local date | `2026-10-18` |
| **Saat** | Local time (updates every second) | `14:23:05` |
| **Dilim** | UTC offset | `UTC+03:00` |
| **Unix** | Unix timestamp (seconds) | `1760797385` |

No permission is requested: the JS clock needs none.

* * *

## Install on the Watch

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

## Build & Run

Requirements:

| Requirement | Version / Notes |
| :-- | :-- |
| Node.js | 18+ (tested on v24.12.0) |
| npm | 9+ (tested on 11.6.2) |
| Python 3 + Pillow | Only needed to regenerate the PNG assets (`scripts/gen_assets.py`) |
| Android phone | Only needed to install the `.rpk` onto the watch via **Notify for Xiaomi** (see [Install on the Watch](#install-on-the-watch)) |
| `aiot-toolkit` | Pulled in automatically as a dev dependency (`npm install`) |

```
git clone https://github.com/hyperpostulate/redmi-watch4-compass.git
cd redmi-watch4-compass
npm install                          # Install the aiot-toolkit toolchain
npm run build                        # Build a debug .rpk into dist/
npm run release                      # Build a release .rpk (requires signing keys)
npm run start                        # aiot start --watch (live development)
python3 scripts/gen_assets.py        # Regenerate the PNG assets from code
```

The toolchain is `aiot-toolkit`. Every text asset is generated at exactly the size it is displayed at, which keeps the bundle small (the toolkit's `--enable-image-png8` flag actually makes the bundle *larger* at this asset size, so it is not used). The build produces `dist/com.hyperpostulate.rw4poc.debug.1.0.0.rpk`. The debug `.rpk` needs no signing; a release package needs `sign/private.pem` and `sign/certificate.pem` (generate with OpenSSL).

On-device verification checklist:

1. Do the four values (Tarih, Saat, Dilim, Unix) render and match the phone?
2. Does `Saat` advance every second?
3. Is the app responsive (no visible lag)?

* * *

## Project Structure

```
redmi-watch4-compass/
├── src/
│   ├── manifest.json          # package com.hyperpostulate.rw4poc, name "RW4 - PoC", designWidth 390
│   ├── app.ux                 # app entry (onCreate/onDestroy)
│   ├── common/
│   │   ├── logo.png           # launcher icon: watch motif, 96x96 (see On-device findings: icon size moves the app name)
│   │   └── txt/               # generated PNG text: labels, title and the glyph atlas (g_<hex>.png)
│   └── pages/
│       └── index/
│           └── index.ux       # the whole app: title + 4 rows + clock logic
├── scripts/
│   ├── gen_assets.py          # reproducible Pillow generator for every PNG asset
│   └── assets/
│       └── ui-subset.ttf      # font used only at generation time (not shipped)
├── docs/
│   ├── design.md              # UI/UX design specification (Turkish)
│   └── findings.md            # bilingual on-device findings
├── dist/                      # build output (.rpk) - gitignored
├── build/                     # intermediate build output - gitignored
├── package.json
└── README.md
```

### Core Files

| File | Purpose |
| :-- | :-- |
| `src/manifest.json` | Vela app manifest: `package` = `com.hyperpostulate.rw4poc`, `name` = `RW4 - PoC`, `deviceTypeList: ["watch"]`, `designWidth: 390`, `features: ["system.router"]` (the PoC uses no other system API) |
| `src/pages/index/index.ux` | The whole app: template (title + four label/value rows), script (clock formatting + glyph mapping) and styles |
| `scripts/gen_assets.py` | Generates the title, the labels, the glyph atlas and the launcher icon (a 96x96 watch motif) deterministically; re-reads every file it writes and asserts dimensions (and non-blank content for the text images) |
| `docs/design.md` | The authoritative UI/UX spec (palette, geometry, text-as-image approach) |
| `docs/findings.md` | Full bilingual write-up of the on-device findings |

* * *

## On-device findings

Verified on a **real Redmi Watch 4**. Full detail — including the complete system-API table — is in **[docs/findings.md](docs/findings.md)**.

- **Text does not render.** `<text>`/`<span>`/`<input>` paint no readable glyphs and a bundled `@font-face` has no effect, so every visible string is a pre-rendered PNG (static labels as single images; dynamic values composed from a glyph atlas).
- **Which system APIs work.** `@system.device`, `@system.storage`, `@system.brightness`, `@system.app`, `vibrator.vibrate()` and the JS clock work; geolocation (GPS, error `203`), sensor, battery, network, bluetooth, record, fetch and crypto do not.
- **No GNSS or health API** is exposed to quick apps, so a GPS/location quick app is impossible on this device.
- **`203`** is Vela's *"function not supported"* code (a permission problem would be `400`/`402`); it is not recoverable by the app.
- **Launcher icon size moves the app name.** The launcher reserves a slot whose width follows the icon PNG's pixel size, so the icon also sets where the label starts — and no manifest field controls label position. The **96x96** `logo.png` is deliberate: `192x192` pushed the app name to the middle of the row, while `96x96` kept it in its normal position.

* * *

## Limitations

- **No GPS/location is possible** on the Redmi Watch 4 from a quick app (see [On-device findings](#on-device-findings)). This repository is a platform PoC, not a GPS app.
- **Text must be images.** Adding new *dynamic* strings requires extending the glyph atlas in `scripts/gen_assets.py` (add the characters to `CHARS`) and rebuilding; characters outside the atlas render as `?`.
- **Many glyph images slow the app down.** Drawing hundreds of `<image>` elements noticeably slows the screen; keep the number of on-screen glyph images small.
- **`npm audit` reports vulnerabilities in transitive dev dependencies** of `aiot-toolkit`. They are build-time only and do not ship inside the `.rpk`.

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

Redmi Watch 4 için minimal bir Xiaomi Vela JS hızlı uygulaması (`.rpk`). Proje bir GPS/pusula fikri olarak başladı; ancak saat, üçüncü taraf uygulamalara **GNSS veya sağlık API'si sunmaz**, dolayısıyla bu cihazda GPS imkânsızdır (bkz. [Cihaz üstü bulgular](#cihaz-üstü-bulgular)). Bunun yerine gelen şey bir **platform PoC**'sidir: burada bir Vela hızlı uygulamasının neleri yapabildiğini belgeleyen en küçük kullanışlı uygulama — bir saat.

* * *

## İçindekiler

- [Bu nedir](#bu-nedir)
- [Ne gösterir](#ne-gösterir)
- [Saate Kurulum](#saate-kurulum)
- [Derleme ve Çalıştırma](#derleme-ve-çalıştırma)
- [Proje Yapısı](#proje-yapısı)
- [Cihaz üstü bulgular](#cihaz-üstü-bulgular)
- [Sınırlamalar](#sınırlamalar)
- [Lisans](#lisans)
- [Geliştirici](#geliştirici)
- [Katkıda Bulunma](#katkıda-bulunma)

* * *

## Bu nedir

Depo bir GPS/pusula denemesi olarak başladı; cihaz üstü testler Redmi Watch 4'te bir GPS hızlı uygulamasının var olamayacağını gösterdi, bu yüzden bir platform PoC'sine dönüştü. Bilinçli olarak çok küçüktür: tek ekran, izin yok ve bir üçüncü taraf Vela hızlı uygulamasının gerçekte neleri yapabildiğinin yazılı kaydı.

## Ne gösterir

Tek ekran — siyah arka plan, yeşil değerler — cihaz saatinden okunan tam olarak dört alan:

| Alan | Anlamı | Örnek |
| :-- | :-- | :-- |
| **Tarih** | Yerel tarih | `2026-10-18` |
| **Saat** | Yerel saat (her saniye güncellenir) | `14:23:05` |
| **Dilim** | UTC farkı | `UTC+03:00` |
| **Unix** | Unix zaman damgası (saniye) | `1760797385` |

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

## Derleme ve Çalıştırma

Gereksinimler:

| Gereksinim | Sürüm / Not |
| :-- | :-- |
| Node.js | 18+ (v24.12.0 ile test edildi) |
| npm | 9+ (11.6.2 ile test edildi) |
| Python 3 + Pillow | Yalnızca PNG varlıklarını yeniden üretmek için gerekir (`scripts/gen_assets.py`) |
| Android telefon | Yalnızca `.rpk` dosyasını **Notify for Xiaomi** ile saate kurmak için gerekir (bkz. [Saate Kurulum](#saate-kurulum)) |
| `aiot-toolkit` | `npm install` ile geliştirme bağımlılığı olarak otomatik gelir |

```
git clone https://github.com/hyperpostulate/redmi-watch4-compass.git
cd redmi-watch4-compass
npm install                          # aiot-toolkit araç zincirini kur
npm run build                        # dist/ içine debug .rpk derle
npm run release                      # release .rpk derle (imza anahtarları gerekir)
npm run start                        # aiot start --watch (canlı geliştirme)
python3 scripts/gen_assets.py        # PNG varlıklarını koddan yeniden üret
```

Araç zinciri `aiot-toolkit`'tir. Her metin varlığı ekranda gösterildiği boyutta üretilir; bu paketi küçük tutar (araç zincirinin `--enable-image-png8` bayrağı bu varlık boyutunda paketi daha da *büyütür*, bu yüzden kullanılmaz). Derleme `dist/com.hyperpostulate.rw4poc.debug.1.0.0.rpk` dosyasını üretir. Debug `.rpk` imza gerektirmez; release paketi için `sign/private.pem` ve `sign/certificate.pem` gerekir (OpenSSL ile üretilir).

Cihaz üstü kontrol listesi:

1. Dört değer (Tarih, Saat, Dilim, Unix) çiziliyor ve telefonla uyuşuyor mu?
2. `Saat` her saniye ilerliyor mu?
3. Uygulama akıcı mı (görünür gecikme yok mu)?

* * *

## Proje Yapısı

```
redmi-watch4-compass/
├── src/
│   ├── manifest.json          # paket com.hyperpostulate.rw4poc, ad "RW4 - PoC", designWidth 390
│   ├── app.ux                 # uygulama girişi (onCreate/onDestroy)
│   ├── common/
│   │   ├── logo.png           # başlatıcı simgesi: saat motifi, 96x96 (bkz. Cihaz üstü bulgular: simge boyutu ismi kaydırır)
│   │   └── txt/               # üretilen PNG metinler: etiketler, başlık ve glif atlası (g_<hex>.png)
│   └── pages/
│       └── index/
│           └── index.ux       # uygulamanın tamamı: başlık + 4 satır + saat mantığı
├── scripts/
│   ├── gen_assets.py          # her PNG varlığı için tekrarlanabilir Pillow üreteci
│   └── assets/
│       └── ui-subset.ttf      # yalnızca üretim zamanında kullanılan font (pakete girmez)
├── docs/
│   ├── design.md              # UI/UX tasarım spesifikasyonu
│   └── findings.md            # iki dilli cihaz üstü bulgular
├── dist/                      # derleme çıktısı (.rpk) - gitignore'da
├── build/                     # ara derleme çıktısı - gitignore'da
├── package.json
└── README.md
```

### Temel Dosyalar

| Dosya | Amaç |
| :-- | :-- |
| `src/manifest.json` | Vela uygulama manifesti: `package` = `com.hyperpostulate.rw4poc`, `name` = `RW4 - PoC`, `deviceTypeList: ["watch"]`, `designWidth: 390`, `features: ["system.router"]` (PoC başka sistem API'si kullanmaz) |
| `src/pages/index/index.ux` | Uygulamanın tamamı: şablon (başlık + dört etiket/değer satırı), script (saat biçimlendirme + glif eşleme) ve stiller |
| `scripts/gen_assets.py` | Başlığı, etiketleri, glif atlasını ve başlatıcı simgesini (96x96 saat motifi) belirlenimci biçimde üretir; yazdığı her dosyayı geri okuyup boyutunu (metin görsellerinde ayrıca boş olmadığını) doğrular |
| `docs/design.md` | Yetkili UI/UX spesifikasyonu (palet, geometri, metin-görsel yaklaşımı) |
| `docs/findings.md` | Cihaz üstü bulguların tam iki dilli yazımı |

* * *

## Cihaz üstü bulgular

**Gerçek bir Redmi Watch 4** üzerinde doğrulandı. Sistem API tablosunun tamamı dâhil ayrıntılar **[docs/findings.md](docs/findings.md)** içinde.

- **Metin çizilmiyor.** `<text>`/`<span>`/`<input>` okunabilir glif çizmiyor ve paketlenen `@font-face` etkisiz; bu yüzden her görünür yazı önceden üretilmiş PNG'dir (statik etiketler tek görsel; dinamik değerler glif atlasından dizilir).
- **Hangi sistem API'leri çalışıyor.** `@system.device`, `@system.storage`, `@system.brightness`, `@system.app`, `vibrator.vibrate()` ve JS saati çalışıyor; geolocation (GPS, hata `203`), sensor, battery, network, bluetooth, record, fetch ve crypto çalışmıyor.
- **GNSS veya sağlık API'si** hızlı uygulamalara açık değildir; bu cihazda bir GPS/konum hızlı uygulaması imkânsızdır.
- **`203`**, Vela'nın *"bu işlev desteklenmiyor"* kodu (izin sorunu olsaydı `400`/`402` olurdu); uygulama tarafından giderilemez.
- **Başlatıcı simge boyutu uygulama ismini kaydırır.** Başlatıcı, genişliği simge PNG'sinin piksel boyutunu izleyen bir alan ayırır; böylece simge ismin nereden başlayacağını da belirler ve ismi konumlandıran bir manifest alanı yoktur. **96x96** `logo.png` bilinçlidir: `192x192` ismi satırın ortasına iterken `96x96` normal konumunda tuttu.

* * *

## Sınırlamalar

- **Redmi Watch 4'te GPS/konum bir hızlı uygulamayla mümkün değildir** (bkz. [Cihaz üstü bulgular](#cihaz-üstü-bulgular)). Bu depo bir GPS uygulaması değil, bir platform PoC'sidir.
- **Metin görsel olmak zorundadır.** Yeni *dinamik* metin eklemek, `scripts/gen_assets.py` içindeki glif atlasını (`CHARS`'a karakter ekleyerek) genişletmeyi ve yeniden derlemeyi gerektirir; atlas dışındaki karakterler `?` olarak çizilir.
- **Çok sayıda glif görseli uygulamayı yavaşlatır.** Yüzlerce `<image>` çizmek ekranı belirgin biçimde yavaşlatır; ekrandaki glif görseli sayısını az tutun.
- **`npm audit`**, `aiot-toolkit`'in geçişli geliştirme bağımlılıklarında güvenlik açıkları bildirir. Bunlar yalnızca derleme zamanıyla ilgilidir ve `.rpk` paketine dâhil olmaz.

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
