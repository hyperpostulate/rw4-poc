# On-device findings — rw4-poc (Redmi Watch 4)

Everything below was verified on a **real Redmi Watch 4**; the official Xiaomi Vela support tables agree.

## Text does not render

- `<text>`, `<span>` and native widgets (`<input type="button">`, `<input type="text">`) paint **no readable glyphs** on this unit (nothing, or notdef "tofu" boxes). A bundled `@font-face` font had zero effect.
- `<image>`, `<div>`, `background-color`, `<style>`/`class` all render correctly.
- **Consequence:** every visible string in this app is a **pre-rendered PNG**. Static labels are single images; dynamic values are composed character-by-character from a monospace **glyph atlas** (`src/common/txt/g_<hex>.png`, one PNG per codepoint) using the `for` directive. `scripts/gen_assets.py` generates all of them deterministically.

## Which system APIs actually work

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

## Launcher icon size moves the app name

- The launcher reserves a slot to the left of the app name, and that slot's **width follows the icon PNG's pixel size** — so the icon also decides where the label starts.
- Verified on device: a **`192x192`** icon (the size the Vela docs recommend) pushed the app name to the *middle* of the row, while shrinking the icon to **`96x96`** pulled the name back to its normal position.
- No manifest field controls the label's position, alignment or size (`name` is the only label input), so the icon is the only lever. Shipping a **`96x96`** `logo.png` is therefore deliberate, not an accident.

## Canvas crashes the device

- Verified on-device with a canvas probe build of **another project based on this one**: the Vela runtime **exposes a complete canvas JS API surface** — `this.$element('cv')` resolves the node, `getContext('2d')` returns a context object, `fillRect`/`drawImage` are callable functions, and a global `Image` constructor exists. An API-presence probe therefore passes cleanly and no automatic fallback triggers.
- But the canvas **paints nothing**: the screen stayed permanently black (not even a solid green `fillRect` diagnosis strip appeared), and shortly after, using it **crashed the quick app runtime so hard that the watch rebooted**.
- Corroboration: `<canvas>` is absent from the official Vela component catalog. The aiot-toolkit compiler whitelist accepts the tag, but that proves nothing about the runtime — the parser is hap-derived and permissive (it also whitelists `web`, `video`, `camera`, `map`).
- **Consequence:** canvas is unusable and unsafe on this device. Any renderer must compose pre-rendered PNGs with `<image>` nodes; there is no single-surface drawing alternative. The downstream project has since reverted to its `<image>`-grid renderer.

* * *

# Cihaz üstü bulgular — rw4-poc (Redmi Watch 4)

Aşağıdaki her şey **gerçek bir Redmi Watch 4** üzerinde doğrulandı; resmî Xiaomi Vela destek tabloları da bunu doğruluyor.

## Metin çizilmiyor

- `<text>`, `<span>` ve yerel widget'lar (`<input type="button">`, `<input type="text">`) bu cihazda **okunabilir glif çizmiyor** (hiçbir şey ya da notdef "tofu" kutuları). Paketlenen bir `@font-face` fontunun hiçbir etkisi olmadı.
- `<image>`, `<div>`, `background-color`, `<style>`/`class` düzgün çalışıyor.
- **Sonuç:** bu uygulamadaki her görünür yazı **önceden üretilmiş PNG**'dir. Statik etiketler tek görseldir; dinamik değerler ise tek aralıklı (monospace) bir **glif atlasından** (`src/common/txt/g_<hex>.png`, her kod noktası için bir PNG) karakter karakter `for` yönergesiyle dizilir. Tümünü `scripts/gen_assets.py` belirlenimci biçimde üretir.

## Hangi sistem API'leri gerçekten çalışıyor

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

## Başlatıcı simge boyutu, uygulama ismini kaydırır

- Başlatıcı, uygulama isminin solunda bir alan ayırır ve bu alanın **genişliği simge PNG'sinin piksel boyutunu izler** — yani ismin nereden başlayacağını da simge belirler.
- Cihazda doğrulandı: **`192x192`** simge (Vela dokümanlarının önerdiği boyut) uygulama ismini satırın *ortasına* itti; simgeyi **`96x96`**'ya küçültmek ismi normal konumuna geri getirdi.
- İsmin konumunu, hizasını veya boyutunu kontrol eden bir manifest alanı yoktur (`name` tek etiket girdisidir); tek kaldıraç simgedir. Bu yüzden **`96x96`** `logo.png` bilinçlidir, tesadüf değildir.

## Canvas cihazı çökertiyor

- **Bu projeden temellenen başka bir projenin** canvas deneme derlemesiyle cihaz üstünde doğrulandı: Vela çalışma zamanı **eksiksiz bir canvas JS API yüzeyi sunar** — `this.$element('cv')` düğümü bulur, `getContext('2d')` bir bağlam nesnesi döndürür, `fillRect`/`drawImage` çağrılabilir fonksiyonlardır ve global bir `Image` yapıcısı vardır. Dolayısıyla API-varlığı denemesi temiz geçer; otomatik bir yedek devreye girmez.
- Ancak canvas **hiçbir şey çizmez**: ekran kalıcı olarak siyah kaldı (düz yeşil bir `fillRect` teşhis şeridi bile görünmedi) ve kullanıldıktan kısa süre sonra quick app çalışma zamanını **saat yeniden başlayacak kadar sert çökertti**.
- Destekleyici kanıt: `<canvas>` resmî Vela bileşen kataloğunda yoktur. aiot-toolkit derleyici beyaz listesi etiketi kabul eder ama bu, çalışma zamanı hakkında hiçbir şey kanıtlamaz — ayrıştırıcı hap kaynaklı ve izin vericidir (`web`, `video`, `camera`, `map`'i de beyaz listeye alır).
- **Sonuç:** canvas bu cihazda kullanılamaz ve güvenli değildir. Her işleyici önceden üretilmiş PNG'leri `<image>` düğümleriyle dizmek zorundadır; tek yüzeyli çizim alternatifi yoktur. Sözü edilen proje, `<image>`-ızgara işleyicisine geri dönmüştür.
