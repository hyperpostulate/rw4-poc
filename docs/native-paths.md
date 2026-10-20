# Alternative development paths — rw4-poc (Redmi Watch 4)

Research date: October 2026. Question: **can you build software for the Redmi Watch 4 by any means other than Vela quick apps (`.rpk`) and watch faces — e.g., native C/C++?** The findings below were gathered by web research, cross-checked between two independent research lanes, and the load-bearing repository claims were re-verified against the primary sources. Evidence grades: **OFFICIAL** (Xiaomi / openvela documentation) > **REPO** (project repository) > **RE** (technical write-up) > **FORUM** (community).

## The short answer

- **Officially: no.** The quick app (`.rpk`) and the watch face are the only documented third-party channels; everything else is closed or partner-gated.
- **Unofficially: yes — and it is proven.** Native ARM C code runs on a retail Redmi Watch 4 today, without custom firmware, loaded as an unsigned NuttX ELF module by a privileged Lua watch face. It is a fragile, per-firmware reverse-engineering path, not an SDK.

## Device background

- Model `M2314W1` (CN) / `M2315W1` (global); SoC **Bestechnic BES2700iBP**; OS = Xiaomi Vela on **NuttX + LVGL**. Two app engines ship on the watch: **AiotJS** (quick apps, `.rpk`) and **Lua 5.4** (watch faces). [RE: 52audio teardown, BandBBS wiki]
- The 2-pin magnetic charger is **power-only** (no data pair), and there is **no ADB on retail hardware** (`adbd` appears only in emulator environments; the device is not Android, so no fastboot either). [OFFICIAL: iot.mi.com devicedebug] [RE: m0tral]
- Phone↔watch bulk transfer is a proprietary protocol over Bluetooth SPP (`L1` framing, CRC16-CCITT, protobuf payloads, ECDH/AES-CCM session after pairing). "Notify for Xiaomi" is a third-party app (OneZeroBit — "in no way associated with Xiaomi") that speaks this protocol; **AstroBox-NG** reimplements the Vela BLE protocol stack in Rust (self-described ~99 % coverage). [RE: Byterialab] [REPO: AstroBox-NG]

## The channel ladder

| Path | Status | Notes |
| :-- | :-- | :-- |
| `.rpk` quick app (this repo) | ✅ works | official toolchain, community install path; the safe default |
| Lua watch face (LVGL) | ✅ works | privileged runtime with a real drawing surface and shell access |
| Native C/C++ (`insmod` ELF) | ⚠️ proven on physical RW4 | per-firmware ABI, no sandbox, lost on reboot |
| Custom firmware | ❌ blocked | signed OTA, no BSP, no unlock |
| Official native SDK | ❌ does not exist | nothing documented outside partner/NDA arrangements |

## What is officially possible

- Real-device quick-app debugging is documented for **Xiaomi Watch S4 only**: it requires a special debug OTA obtained through Xiaomi staff and is "open to specific partners" — the Redmi Watch 4 is not listed at all. Publishing a Vela quick app means contacting Xiaomi staff; the Xiaomi App Store accepts no individual developer accounts (enterprise only — that policy is written for HyperOS apps, but no individual self-serve route exists for Vela wearables either). [OFFICIAL: iot.mi.com, dev.mi.com]
- **openvela** (the open-source Vela; intent announced late 2023, code published December 2024, Apache-2.0) is real and buildable, and it does define **native C/C++ apps** (LVGL UIs built with Kconfig/Makefile) — but they are **compiled into the firmware image**, not installed as apps afterwards. [OFFICIAL: openvela docs]
- What openvela does not give you for this watch: **no board support package** (the only Bes port targets the BES2600WM/BEST2003 evaluation board; `vendor_xiaomi_vela` is an empty stub), **no signing keys**, **no flashing or bootloader-unlock path**, and **no installable native app format**. openvela's own FAQ also notes the Quick App runtime is not integrated there. [OFFICIAL: openvela docs/GitHub]

## The native path in detail

The chain (no firmware modification involved):

1. The **Lua watch face runtime is privileged**: it exposes `os.execute()`, which reaches the NuttX `nsh` shell — including `insmod`/`rmmod`/`lsmod`. [REPO: Pizofh R191, Vela-Shell-Bridge]
2. Ship an **ELF32 ARM `ET_REL` module** (arm-none-eabi-gcc, constructor entry point, no imports) inside the watch face, write it to `/data` and `insmod` it. `rmmod` unloads it; a reboot clears it.
3. Install the watch face with community tooling (Notify / AstroBox-NG / EasyFace). Pizofh went further and paired the watch directly with a PC, pushing packages with his own protocol client.

Evidence on physical hardware:

- **Pizofh/Doomed** (RW4 `M2315W1`, stock FW 2.2.86, checkpoint-gated log): NuttX shell confirmed (R191); **own C executed and unloaded** (R204, 784-byte initializer); file I/O through five 2.2.86-specific APIs (R217); C-generated frames animated on screen via Lua/LVGL (R222); a 13-command control channel to a resident module (R264); clean unload (R270). Full Doom on RW4 is still pending (PC/Watch S3 only). Self-reported, but hash- and offset-documented. [REPO]
- **m0tral/MiWatchNativeApps**: the same mechanism running real native apps (a calculator) on SmartBand 10 Pro and Watch S3; explicitly "loaded manually, lost after reboot". [REPO, RE: habr]

Costs and limits of this path:

- **No stable ABI/SDK** — API addresses are reverse-engineered per firmware build; a module for one device does not port to another unchanged.
- **No sandbox** — openvela's FAQ confirms Flat Build shares the kernel address space; a crash can take the whole system down. [OFFICIAL]
- **No persistence** across reboots without a firmware modification.
- **No public RW4 native GUI framework** yet (Doom-on-RW4 is unfinished).

## Custom firmware: blocked

- OTA packages are ZIPs (`ota.json`, `vela_ap.bin`, resource bins) with CRC32 and **signature verification that cannot be disabled**; the bootloader validates the app before jumping. [FORUM: 4PDA] [RE: m0tral RW5 bootloader analysis]
- The only public BES2700-class custom firmware (atc1441, Mi Band 10) required opening the device, UART pads and a leaked second-stage bootloader — no equivalent public RW4 result exists. [REPO]
- m0tral's paid RW4 "custom firmware" mods are resource/configuration-level changes delivered through the normal signed OTA channel, method unpublished — vendor-adjacent modding, not open firmware. [FORUM]

## Cross-validation of this repo's findings

Pizofh independently observed that **text does not render in the Lua/LVGL runtime either** (R182: LVGL `Label` calls complete, no glyphs appear; R183: a font investigation followed). This corroborates [findings.md](findings.md): the missing text rendering is not quick-app-specific — it reaches down into the device's font/service layer.

## Explicit unknowns

- RW4 UART/SWD test-pad locations, and whether the bootloader would accept an unsigned app image — no public data.
- The exact signature checks performed on watch-face/`.rpk` install for RW4 — custom watch faces install fine in practice, but the check itself is unpublished.
- Whether Xiaomi runs a non-public (NDA) native-app programme for partners — unknown by definition.

## Source list

**Official**

- Xiaomi Vela quick-app docs, real-device debugging (Watch S4 only, partner-only): https://iot.mi.com/vela/quickapp/zh/tools/devicedebug/start.html
- Vela quick-app publishing (staff contact): https://iot.mi.com/vela/quickapp/en/guide/publish/
- Xiaomi App Store developer policy (no individual accounts): https://dev.mi.com/xiaomihyperos/documentation/detail?pId=1731
- openvela project overview + FAQ (Flat Build, native apps, RPK runtime status): https://doc.openvela.com/document?id=198&language=en&version=trunk · https://doc.openvela.com/document?id=866&language=en&version=trunk
- openvela native app tutorial: https://github.com/open-vela/docs/blob/dev/zh-cn/app_dev/system_apps/Dev_UI_App.md
- openvela supported boards (no Xiaomi watch): https://github.com/open-vela/docs/blob/dev/zh-cn/dev_board/Development_Board.md
- open-vela/vendor_bes (BES2600WM/BEST2003 only): https://github.com/open-vela/vendor_bes

**Repositories / technical write-ups**

- Pizofh — native research on physical RW4 (checkpoint log): https://github.com/Pizofh/Doomed---Doom-for-Redmi-watch-4-
- m0tral — native apps on Xiaomi watches: https://github.com/m0tral/MiWatchNativeApps · https://habr.com/ru/articles/1079066/
- m0tral — EasyFace / emulator / Lua watchfaces: https://github.com/m0tral/EasyFace · https://github.com/m0tral/MiWatchEmulator · https://github.com/m0tral/MiWatchLuaWatchfaces
- AstroBox-NG (Vela BLE protocol reimplementation): https://github.com/AstralSightStudios/AstroBox-NG
- MiWearBridge (LSPosed hooks for Mi Fitness): https://github.com/batareya16/MiWearBridge
- Vela-Shell-Bridge (Lua shell daemon for QuickApps): https://github.com/FangAiden/Vela-Shell-Bridge
- atc1441 — Mi Band 10 BES2700 custom firmware: https://github.com/atc1441/MiBand10-BES2700iMP-BEST1503-Hacking
- Byterialab — Xiaomi watch BLE/SPP protocol RE: https://blog.byterialab.com/reversing-the-xiaomi-redmi-watch-through-crafted-watchfaces/

**Forums / corroboration**

- 4PDA HyperOS wearable knowledge base (OTA layout, signing): https://4pda.to/forum/index.php?showtopic=1120610
- m0tral — RW5 bootloader/UART analysis: https://habr.com/ru/articles/1027516/
- Teardown (BES2700iBP, power-only charger): https://www.52audio.com/archives/191060.html
- openvela open-source announcement (2024-12-11): https://www.oschina.net/news/324579/xiaomi-openvela-opensource

* * *

# Alternatif geliştirme yolları — rw4-poc (Redmi Watch 4)

Araştırma tarihi: Ekim 2026. Soru: **Redmi Watch 4'e quick app (`.rpk`) ve watch face dışında bir yolla — örneğin native C/C++ ile — yazılım geliştirilebilir mi?** Aşağıdaki bulgular web araştırmasıyla toplandı, iki bağımsız araştırma şeridi arasında çapraz kontrol edildi ve yük taşıyan depo iddiaları birincil kaynaklara karşı yeniden doğrulandı. Kanıt dereceleri: **OFFICIAL/resmî** (Xiaomi / openvela dokümantasyonu) > **REPO** (proje deposu) > **RE** (teknik yazı) > **FORUM** (topluluk).

## Kısa cevap

- **Resmî olarak: hayır.** Quick app (`.rpk`) ve watch face, belgelenmiş tek üçüncü taraf kanal; gerisi kapalı ya da partner-kapılı.
- **Gayriresmî olarak: evet — ve kanıtlanmış.** Native ARM C kodu bugün, custom firmware olmadan, perakende bir Redmi Watch 4'te çalışıyor: ayrıcalıklı bir Lua watch face tarafından imzasız bir NuttX ELF modülü olarak yükleniyor. Bu bir SDK değil; firmware başına tersine mühendislik gerektiren kırılgan bir yol.

## Cihaz arka planı

- Model `M2314W1` (CN) / `M2315W1` (global); yongaseti **Bestechnic BES2700iBP**; işletim sistemi = **NuttX + LVGL** üzerinde Xiaomi Vela. Saatte iki uygulama motoru var: **AiotJS** (quick app, `.rpk`) ve **Lua 5.4** (watch face). [RE: 52audio sökümü, BandBBS wiki]
- 2 pimli mıknatıslı şarj cihazı **yalnız güç** verir (veri çifti yok) ve perakende donanımda **ADB yoktur** (`adbd` yalnız emülatör ortamlarında görünür; cihaz Android değildir, fastboot da yoktur). [OFFICIAL: iot.mi.com devicedebug] [RE: m0tral]
- Telefon↔saat toplu aktarımı SPP üzerinden tescilli bir protokoldür (`L1` çerçeveleme, CRC16-CCITT, protobuf payload, eşleştirmeden sonra ECDH/AES-CCM oturumu). "Notify for Xiaomi" bu protokolü konuşan üçüncü taraf bir uygulamadır (OneZeroBit — "Xiaomi ile hiçbir ilgisi yoktur"); **AstroBox-NG** Vela BLE protokol yığınını Rust'ta yeniden uygular (öz-beyanla ~%99 kapsam). [RE: Byterialab] [REPO: AstroBox-NG]

## Kanal merdiveni

| Yol | Durum | Not |
| :-- | :-- | :-- |
| `.rpk` quick app (bu repo) | ✅ çalışıyor | resmî araç zinciri, topluluk kurulum yolu; güvenli varsayılan |
| Lua watch face (LVGL) | ✅ çalışıyor | gerçek çizim yüzeyi ve shell erişimi olan ayrıcalıklı çalışma zamanı |
| Native C/C++ (`insmod` ELF) | ⚠️ fiziksel RW4'te kanıtlanmış | firmware'e bağlı ABI, sandbox yok, reboot'ta kaybolur |
| Custom firmware | ❌ kapalı | imzalı OTA, BSP yok, unlock yok |
| Resmî native SDK | ❌ mevcut değil | partner/NDA anlaşmaları dışında hiçbir şey belgelenmemiş |

## Resmî olarak mümkün olan

- Gerçek cihazda quick-app debug yalnız **Xiaomi Watch S4** için belgelenmiştir: Xiaomi personeli aracılığıyla alınan özel bir debug OTA ister ve "belirli partnerlara" açıktır — Redmi Watch 4 hiç listelenmez. Vela quick app yayınlamak Xiaomi personeliyle iletişim demektir; Xiaomi App Store bireysel geliştirici hesabı kabul etmez (yalnız kurumsal — politika HyperOS uygulamaları için yazılmıştır ama Vela giyilebilirleri için de bireysel self-servis yol yoktur). [OFFICIAL: iot.mi.com, dev.mi.com]
- **openvela** (açık kaynak Vela; niyet 2023 sonunda duyuruldu, kod Aralık 2024'te yayımlandı, Apache-2.0) gerçek ve derlenebilirdir ve **native C/C++ uygulamaları** tanımlar (Kconfig/Makefile ile derlenen LVGL arayüzleri) — ama bunlar firmware imajının **içine derlenen** şeylerdir, sonradan kurulmaz. [OFFICIAL: openvela dokümantasyonu]
- openvela'nın bu saat için vermedikleri: **BSP yok** (tek Bes portu BES2600WM/BEST2003 değerlendirme kartını hedefler; `vendor_xiaomi_vela` boş bir stub'dur), **imzalama anahtarı yok**, **flash ya da bootloader-unlock yolu yok**, **kurulabilir native uygulama formatı yok**. openvela'nın kendi SSS'si ayrıca Quick App çalışma zamanının orada entegre olmadığını belirtir. [OFFICIAL: openvela dokümantasyonu/GitHub]

## Native yolun ayrıntısı

Zincir (firmware değişikliği içermez):

1. **Lua watch face çalışma zamanı ayrıcalıklıdır**: `os.execute()` ifşa eder ve bu, NuttX `nsh` shell'ine — `insmod`/`rmmod`/`lsmod` dahil — ulaşır. [REPO: Pizofh R191, Vela-Shell-Bridge]
2. Watch face içine gömülü bir **ELF32 ARM `ET_REL` modülü** (arm-none-eabi-gcc, constructor giriş noktası, importsuz) `/data`'ya yazılır ve `insmod` ile yüklenir. `rmmod` kaldırır; reboot temizler.
3. Watch face, topluluk araçlarıyla kurulur (Notify / AstroBox-NG / EasyFace). Pizofh daha da ileri gidip saati doğrudan bir PC ile eşleştirdi ve paketleri kendi protokol istemcisiyle gönderdi.

Fiziksel donanımdaki kanıtlar:

- **Pizofh/Doomed** (RW4 `M2315W1`, stok FW 2.2.86, checkpoint-kapılı günlük): NuttX shell doğrulandı (R191); **kendi C'si çalıştı ve kaldırıldı** (R204, 784 baytlık başlatıcı); 2.2.86'ya özgü beş API ile dosya I/O (R217); C'nin ürettiği kareler Lua/LVGL ile ekranda animasyonlu gösterildi (R222); kalıcı modüle 13 komutluk kontrol kanalı (R264); temiz kaldırma (R270). Tam Doom RW4'te hâlâ bekliyor (yalnız PC/Watch S3). Öz-beyan ama hash ve ofset bazlı belgelenmiş. [REPO]
- **m0tral/MiWatchNativeApps**: aynı mekanizma, SmartBand 10 Pro ve Watch S3'te gerçek native uygulamalar (hesap makinesi) çalıştırıyor; açıkça "elle yüklenir, reboot'tan sonra kaybolur". [REPO, RE: habr]

Bu yolun maliyetleri ve sınırları:

- **Stabil ABI/SDK yok** — API adresleri firmware sürümü başına tersine mühendislikle bulunur; bir cihaz için derlenen modül değiştirilmeden diğerine taşınmaz.
- **Sandbox yok** — openvela SSS'si Flat Build'in çekirdek adres alanını paylaştığını doğrular; bir çöküş tüm sistemi düşürebilir. [OFFICIAL]
- **Kalıcılık yok** — bir firmware değişikliği olmadan reboot'lardan sonra kalmaz.
- **Herkese açık RW4 native GUI çerçevesi henüz yok** (RW4'te Doom bitirilemedi).

## Custom firmware: kapalı

- OTA paketleri, CRC32 ve **kapatılamayan imza doğrulaması** içeren ZIP'lerdir (`ota.json`, `vela_ap.bin`, kaynak bin'leri); bootloader geçmeden önce uygulamayı doğrular. [FORUM: 4PDA] [RE: m0tral RW5 bootloader analizi]
- Genel olarak erişilebilir tek BES2700-sınıfı custom firmware (atc1441, Mi Band 10) cihazın açılmasını, UART pad'lerini ve sızmış bir ikinci aşama bootloader'ı gerektirdi — eşdeğer bir kamuya açık RW4 sonucu yok. [REPO]
- m0tral'ın paralı RW4 "custom firmware" modları, normal imzalı OTA kanalından dağıtılan kaynak/yapılandırma seviyesi değişikliklerdir; yöntem yayımlanmamıştır — satıcı-yanlı modlama, açık firmware değil. [FORUM]

## Bu reponun bulgularının çapraz doğrulaması

Pizofh, **Lua/LVGL çalışma zamanında da metnin çizilmediğini** bağımsız olarak gözlemledi (R182: LVGL `Label` çağrıları tamamlanıyor, glif görünmüyor; R183: bir font araştırması izledi). Bu, [findings.md](findings.md)'yi doğrular: eksik metin render'ı quick app'e özgü değildir — cihazın font/servis katmanına kadar iner.

## Açık bilinmeyenler

- RW4 UART/SWD test-pad konumları ve bootloader'ın imzasız bir uygulama imajını kabul edip etmeyeceği — kamuya açık veri yok.
- RW4 için watch-face/`.rpk` kurulumunda yapılan imza denetimlerinin tam biçimi — özel watch face'ler pratikte kuruluyor ama denetimin kendisi yayımlanmamış.
- Xiaomi'nin partnerler için kamuya kapalı (NDA'lı) bir native-uygulama programı işletip işletmediği — tanımı gereği bilinmiyor.

## Kaynak listesi

Bağlantılar yukarıdaki İngilizce bölümdeki listede ortaktır (OFFICIAL / REPO-RE / FORUM gruplamasıyla); Türkçe bölümde tekrarlanmamıştır.
