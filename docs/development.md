# Developing apps from this template — rw4-poc

This repository doubles as a **template plus device guide**: the build pipeline (`aiot-toolkit`), the verified install path (Notify for Xiaomi) and the on-device limits are already in place. Developing a new app means two things: **adapting this repo** to your idea and **staying inside what the device allows**.

## 1. Turning this repo into a new app

1. **Copy** the repository. It is GPLv3, so derivatives must stay GPLv3.
2. **`src/manifest.json`**: change `package` to your own reverse domain name (e.g. `com.yourname.appname`) — keeping the PoC's package installs on top of it. Update `name`, and bump `versionName`/`versionCode` for every release. Keep `designWidth: 390` and the **96×96** `logo.png` as they are: a 192×192 icon pushes the app name to the middle of the launcher row (see [findings](findings.md)).
3. **UI**: edit the template in `src/pages/index/index.ux`; the palette and geometry are specified in [design.md](design.md). For multiple pages, add `src/pages/<page>/<page>.ux` and register it under `router.pages` in the manifest (`router.entry` stays `pages/index` unless you change the landing page); `system.router` is already listed in `features`.
4. **Text = images**: the device draws no readable `<text>`, `<span>` or `<input>` glyphs, so every visible string is a pre-rendered PNG.
   - Static labels → add new `lbl_*.png` definitions in `scripts/gen_assets.py`.
   - Dynamic values → add the characters you will need to `CHARS` (characters outside the atlas render as `?`).
   - Run `python3 scripts/gen_assets.py`. Never hand-edit the PNGs: the generator wipes `src/common/txt/` and regenerates everything deterministically.
5. **Geometry coupling**: every PNG is generated at exactly its display size, matching the boxes in the `.ux` template. Change one, change the other.
6. **Build & install**: `npm run build` → install the `.rpk` from an Android phone via Notify for Xiaomi (see [README](../README.md) → "Install on the Watch"). Updates install over the **same** `package` name with an increased `versionCode`; changing `package` creates a separate app.

## 2. What kinds of apps are possible

The only working system APIs are: **JS clock (`new Date()`), `@system.storage` (persistent key/value), `vibrator.vibrate()`, `@system.brightness`, `@system.device`, `@system.app`** (full table in [findings.md](findings.md)). In practice this enables:

| Category | Example apps | Building blocks |
| :-- | :-- | :-- |
| Timers | pomodoro, interval/HIIT trainer (vibration at turn end), meditation timer, stopwatch, date countdown ("X days until …") | clock + vibration + storage — the device's most natural app shape |
| Counters & lists | tally counter, water-intake counter, shopping list | tap to increment; state persists across restarts via `@system.storage` |
| Chance & games | dice, coin flip, tap-timing games, visual memory games | text does not render, so these must be fully visual; vibration is a good feedback channel |
| Static info cards | emergency contact, WiFi password, blood type | entirely pre-rendered content, zero runtime data |
| QR codes | WiFi-sharing QR, vCard, ticket/room code, runtime-computed QR | static payload → one pre-rendered PNG from `gen_assets.py`; changing payload → pure-JS QR encoder + `<image>` grid (**canvas is unusable**, see [findings](findings.md)); merge horizontal runs of dark modules to keep the image count low; max out `@system.brightness` while the code is shown |
| One-time passwords | TOTP authenticator (30 s time-based codes), HOTP authenticator (tap advances the counter) | pure-JS HMAC-SHA1 (`@system.crypto` is absent) — digits `0-9` are already in the glyph atlas; clock drives TOTP, `@system.storage` + tap drives HOTP; the secret must be embedded at build time (nothing can be typed or received on the watch, and it is extractable from the `.rpk`) |
| Calculators & generators | calculator, tip/bill splitter, fixed-rate unit converter, on-device password/PIN generator | pure JS + a visual button pad (PNG buttons); a clock-seeded PRNG can generate secrets on the watch itself — nothing has to be baked into the build; letters/symbols must be added to `CHARS` |
| Calendar & sky math | world clock, prayer times, sunrise/sunset | astronomical algorithms run fully offline in pure JS; coordinates are fixed at build time (no GPS) |
| Logbooks | habit grid, cycle tracker, medication/mood journal, baby-feeding log | tap-to-select + `@system.storage` + clock; data never leaves the watch on its own (see the QR egress note below) — for medical data that privacy is a feature |
| Haptic tools | metronome, breathing pacer, Morse trainer | periodic `vibrator.vibrate()` + `setInterval`; vibration timing precision needs on-device verification |
| Guided sequences | workout player (PNG exercise deck + set timer + vibration), recipe stepper, flashcards | static content + timer + tap composed together; the routine's images are pre-rendered at build time |
| Slow visual toys | virtual pet whose state decays with elapsed time (storage + clock — no background execution needed), reaction-time test, Simon, pixel doodle pad | image grids are proven, but the full-grid refresh floor is ~0.8–1 s/frame (see [findings](findings.md)) — no smooth action games; few-element updates stay fast (the clock proves it) |
| Screen tools | brightness controller, full-screen white flashlight | `@system.brightness` works |
| Screen test tools | dead/stuck-pixel test, color reference card, red night screen | just `<div>` background colors — the platform's lowest-risk family |

**The QR egress channel:** the watch has no camera, but the phone does. Anything the watch produces or accumulates (a generated secret, a logbook summary) can be displayed as a runtime-computed QR (see the QR row above) and scanned by the phone — the platform's only data-out path. Limits: QR capacity (at most ~2.9 KB, at large versions) and the image count of large matrices; a few hundred bytes is the realistic payload, to be verified on device.

**Beyond quick apps and watch faces:** whether the platform can be targeted in lower-level ways — privileged Lua watch faces, native C/C++ loaded as NuttX ELF modules, custom firmware — is researched in [native-development.md](native-development.md).

### What cannot be built (do-not-attempt list)

- **Weather or any online data** — `@system.network` and `@system.fetch` are not supported. (A "weather app" is only possible as static, pre-rendered PNG content.)
- **GPS / compass / accelerometer apps** — not supported (error `203`).
- **Step / heart-rate / any health data** — not exposed to quick apps at all.
- **Notification replies, audio recording, general phone communication** — not supported; watch↔phone Interconnect is certificate-checked and not an option for debug-signed apps.

## 3. Things to watch

- **Keep the on-screen glyph count small.** Hundreds of `<image>` elements visibly slow the screen. Render continuously changing values with a fixed number of glyphs (e.g. always 5 glyphs for a 5-digit field).
- **Watch limits**: at most ~20 quick apps installed, ~87 MB of free space required for installs.
- **"It works"** means the build succeeds **and** the on-device checklist passes — there is no local runtime, so test every change on the real watch.
- **Before trying a new API**, check the table in [findings.md](findings.md): an unsupported API returns error `203` ("function not supported"), which the app cannot recover from.
- **`@click` is not yet verified on device.** The table above assumes tap-driven apps, but this repo's template contains no touch handler — probe a tap on the real watch before building an app whose only input is touch.
- **No background execution is expected.** Nothing in the verified API set runs code while the app is closed, so reminders, timers and vibration only work while the app is open (an inference to verify on device).

* * *

# Bu şablondan uygulama geliştirme — rw4-poc

Bu depo aynı zamanda bir **şablon artı cihaz kılavuzudur**: derleme zinciri (`aiot-toolkit`), doğrulanmış kurulum yolu (Notify for Xiaomi) ve cihaz üstü sınırlar hazır duruyor. Yeni bir uygulama geliştirmek iki şey demektir: bu repoyu fikrinize **uyarlamak** ve cihazın izin verdiği alanda **kalmak**.

## 1. Bu repoyu yeni bir uygulamaya dönüştürme

1. **Kopyalayın** depoyu. GPLv3 lisanslıdır; türev uygulamalar da GPLv3 kalmak zorundadır.
2. **`src/manifest.json`**: `package` alanını kendi ters alan adınıza değiştirin (örn. `com.seninadi.uygulama`) — PoC'nin paket adını bırakırsanız uygulamanın üzerine kurarsınız. `name`'i güncelleyin ve her yayında `versionName`/`versionCode`'u artırın. `designWidth: 390`'ı ve **96×96** `logo.png`'yi olduğu gibi bırakın: 192×192 simge uygulama adını satırın ortasına itiyor (bkz. [bulgular](findings.md)).
3. **UI**: `src/pages/index/index.ux` içindeki şablonu düzenleyin; palet ve geometri [design.md](design.md) içinde belirtilmiştir. Çok sayfa gerekiyorsa `src/pages/<sayfa>/<sayfa>.ux` ekleyin ve manifestte `router.pages` altına kaydedin (giriş sayfasını değiştirmiyorsanız `router.entry` `pages/index` olarak kalır); `system.router` zaten `features` içinde listeli.
4. **Metin = görsel**: cihaz `<text>`, `<span>` veya `<input>` gliflerini okunabilir çizmiyor; bu yüzden her görünür yazı önceden üretilmiş PNG'dir.
   - Statik etiketler → `scripts/gen_assets.py` içinde yeni `lbl_*.png` tanımları ekleyin.
   - Dinamik değerler → kullanacağınız karakterleri `CHARS` kümesine ekleyin (atlas dışı karakterler `?` olarak çizilir).
   - `python3 scripts/gen_assets.py` çalıştırın. PNG'leri asla elle düzenlemeyin: üreteç `src/common/txt/` dizinini siler ve her şeyi belirlenimci biçimde yeniden üretir.
5. **Geometri eşleşmesi**: her PNG, `.ux` şablonundaki kutularla eşleşen, tam görüntülendiği boyutta üretilir. Birini değiştirirseniz diğerini de değiştirin.
6. **Derleme ve kurulum**: `npm run build` → `.rpk` dosyasını Android telefondan Notify for Xiaomi ile kurun (bkz. [README](../README.md) → "Saate Kurulum"). Güncellemeler **aynı** `package` adının üzerine, artırılmış `versionCode` ile kurulur; `package` değiştirmek ayrı bir uygulama oluşturur.

## 2. Hangi uygulamalar mümkün

Çalışan sistem API'leri yalnızca şunlardır: **JS saati (`new Date()`), `@system.storage` (kalıcı anahtar/değer), `vibrator.vibrate()`, `@system.brightness`, `@system.device`, `@system.app`** (tam tablo [findings.md](findings.md) içinde). Bu, pratikte şunları mümkün kılar:

| Kategori | Örnek uygulamalar | Yapı taşları |
| :-- | :-- | :-- |
| Zamanlayıcılar | pomodoro, interval/HIIT antrenmanı (tur sonunda titreşim), meditasyon sayacı, kronometre, tarih sayacı ("…'a X gün kaldı") | saat + titreşim + storage — cihazın en doğal uygulama biçimi |
| Sayaç ve listeler | el hizalaması sayacı, su sayacı, alışveriş listesi | dokunarak artırma; durum `@system.storage` ile yeniden başlatmalarda kalıcı |
| Şans ve oyunlar | zar, yazı-tura, dokunma-zamanlaması oyunları, görsel hafıza oyunları | metin çizilmediği için tamamen görsel tasarım gerekir; titreşim iyi bir geri bildirim kanalıdır |
| Statik bilgi kartları | acil iletişim bilgisi, WiFi şifresi, kan grubu | tümüyle önceden üretilmiş içerik, sıfır çalışma zamanı verisi |
| QR kodları | WiFi paylaşım QR'u, vCard, bilet/oda kodu, çalışma zamanında hesaplanan QR | sabit içerik → `gen_assets.py` ile üretilen tek PNG; değişen içerik → saf JS QR kodlayıcı + `<image>` ızgarası (**canvas kullanılamaz**, bkz. [bulgular](findings.md)); karanlık modüllerin yatay koşularını birleştirerek görsel sayısını düşürün; kod görünürken `@system.brightness`'ı sonuna kadar açın |
| Tek seferlik şifreler | TOTP kimlik doğrulayıcı (30 saniyelik zaman tabanlı kodlar), HOTP kimlik doğrulayıcı (dokunuş sayacı ilerletir) | saf JS HMAC-SHA1 (`@system.crypto` yok) — `0-9` rakamları glif atlasında zaten var; TOTP'yi saat, HOTP sayacını `@system.storage` + dokunuş sürer; sır build zamanında gömülmek zorunda (saatte yazılamaz ya da alınamaz ve `.rpk` içinden çıkarılabilir) |
| Hesap ve üreteçler | hesap makinesi, bahşiş/bölüşüm hesaplayıcı, sabit kurlu çevirici, cihaz üzerinde şifre/PIN üreteci | saf JS + görsel tuş takımı (PNG düğmeler); saat tohumlu bir PRNG sırları saatin kendisinde üretebilir — hiçbir şey build'e gömülmez; harf/simge glifleri `CHARS`'a eklenmelidir |
| Takvim ve gökyüzü hesabı | dünya saatleri, namaz vakitleri, gün doğumu/batımı | astronomi algoritmaları saf JS ile tamamen çevrimdışı çalışır; koordinatlar build zamanında sabitlenir (GPS yok) |
| Kayıt defterleri | alışkanlık ızgarası, adet takvimi, ilaç/ruh hali günlüğü, bebek besleme kaydı | dokunma-seçim + `@system.storage` + saat; veri kendi başına saatten asla çıkmaz (aşağıdaki QR çıkış notuna bkz.) — tıbbi veri için bu gizlilik bir özelliktir |
| Haptik araçlar | metronom, nefes hızlandırıcı, mors eğitmeni | periyodik `vibrator.vibrate()` + `setInterval`; titreşimin zamanlama hassasiyeti cihazda doğrulanmalı |
| Rehberli akışlar | antrenman oynatıcı (PNG egzersiz destesi + set zamanlayıcısı + titreşim), tarif adımlayıcı, flashcard | statik içerik + zamanlayıcı + dokunma kompozisyonu; akışın görselleri build zamanında üretilir |
| Yavaş görsel oyuncaklar | geçen süreden "bozunan" sanal evcil hayvan (storage + saat — arka plan yürütmeye gerek yok), tepki süresi testi, Simon, piksel karalama defteri | ızgara render'ı kanıtlı ama tam-ızgara yenileme tabanı ~0,8–1 sn/kare (bkz. [bulgular](findings.md)) — akıcı aksiyon oyunu yok; az öğeli güncellemeler hızlı kalır (saat kanıtı) |
| Ekran araçları | parlaklık kontrolcüsü, tam ekran beyaz fener | `@system.brightness` çalışıyor |
| Ekran test araçları | ölü/takılı piksel testi, renk referans kartı, gece için kırmızı ekran | yalnızca `<div>` arka plan renkleri — platformun en düşük riskli ailesi |

**QR çıkış kanalı:** saatin kamerası yok ama telefonunki var. Saatin ürettiği ya da biriktirdiği her şey (üretilmiş bir sır, kayıt defteri özeti) çalışma zamanında hesaplanan QR olarak (yukarıdaki QR satırına bkz.) ekrana basılıp telefonla okutulabilir — platformun tek veri çıkış yolu. Sınırlar: QR kapasitesi (büyük sürümlerde en çok ~2,9 KB) ve büyük matrislerin görsel sayısı; gerçekçi payload birkaç yüz bayttır, cihazda doğrulanmalıdır.

**Quick app ve watch face ötesi:** platforma daha düşük seviyeli yollarla — ayrıcalıklı Lua watch face'ler, NuttX ELF modülü olarak native C/C++, custom firmware — hitap edilip edilemeyeceği [native-development.md](native-development.md) içinde araştırıldı.

### Yapılamayacaklar (denemeyin listesi)

- **Hava durumu veya herhangi bir çevrimiçi veri** — `@system.network` ve `@system.fetch` desteklenmiyor. ("Hava durumu uygulaması" yalnızca statik, önceden render edilmiş PNG içerik olarak mümkün.)
- **GPS / pusula / ivmeölçer uygulamaları** — desteklenmiyor (hata `203`).
- **Adım / nabız / herhangi bir sağlık verisi** — hızlı uygulamalara hiç açılmamış.
- **Bildirim yanıtlama, ses kaydı, genel telefonla iletişim** — desteklenmiyor; saat↔telefon Interconnect'i sertifika denetimlidir ve debug imzalı uygulamalar için seçenek değildir.

## 3. Dikkat edilecekler

- **Ekrandaki glif sayısını küçük tutun.** Yüzlerce `<image>` öğesi ekranı belirgin biçimde yavaşlatıyor. Sürekli değişen değerleri sabit glif sayısıyla çizin (örn. 5 haneli bir alanı her zaman 5 glifle).
- **Saat sınırları**: en fazla ~20 hızlı uygulama kurulabilir, kurulum için ~87 MB boş alan gerekir.
- **"Çalışıyor"un tanımı**: derleme başarılı **ve** cihaz üstü kontrol listesi geçiyor demektir — bu makinada çalışma zamanı yoktur; her değişikliği gerçek saatte test edin.
- **Yeni bir API denemeden önce** [findings.md](findings.md)'deki tabloya bakın: desteklenmeyen API `203` hatası döndürür ("bu işlev desteklenmiyor") ve bu, uygulama tarafından giderilemez.
- **`@click` henüz cihazda doğrulanmadı.** Yukarıdaki tablo dokunma temelli uygulamalar varsayıyor ama bu reponun şablonunda hiç dokunma işleyicisi yok — tek girdisi dokunma olan bir uygulama kurmadan önce gerçek saatte bir dokunma denemesi yapın.
- **Arka plan yürütme beklenmiyor.** Doğrulanmış API kümesinde uygulama kapalıyken kod çalıştıran hiçbir şey yok; dolayısıyla hatırlatıcı, zamanlayıcı ve titreşim yalnız uygulama açıkken çalışır (cihazda doğrulanması gereken bir çıkarım).
