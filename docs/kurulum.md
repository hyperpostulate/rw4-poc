# Pusula'yı REDMI WATCH 4'e Kurma Kılavuzu

Bu kılavuz, Xiaomi Vela hızlı uygulamamız **Pusula**'nın (`com.hyperpostulate.rw4compass`)
derlenmiş paketini (`dist/com.hyperpostulate.rw4compass.debug.1.0.0.rpk`, ~17 KB) bir Android
telefon ve kablosuz (Bluetooth) bağlantı üzerinden **REDMI WATCH 4** saatine kurmayı anlatır.

Vela (JS) hızlı uygulamaları `.rpk` uzantılı paketlerdir. Saat ile telefon arasındaki iletişim
Bluetooth üzerinden yapılır ve REDMI WATCH 4'te **cihazın kendi mağazası dışında doğrudan
`.rpk` yükleme** desteği standart Mi Fitness (小米运动健康) sürümünde **kapalıdır**. Aşağıda,
toplulukta gerçekten çalışan üç yol ve bugünkü (2025–2026) durumları anlatılmıştır.

> **Önemli terminoloji:** Xiaomi'nin telefon uygulaması Türkçe mağazalarda "Mi Fitness",
> Çince'de "小米运动健康" (Xiaomi Sağlık) olarak geçer. Eski adı "小米穿戴 / Xiaomi Wear"
> (Mi Wear) idi. Metinde hangi uygulamadan bahsedildiğini her zaman belirttik.

---

## Hangi yöntemi seçmeliyim?

| Durumunuz | Önerilen yol |
|---|---|
| İş/geliştirici kanalınız var, Xiaomi'den özel debug Mi Fitness alabildiniz | **Yöntem 1** (en temiz, resmi) |
| Telefonunuzda **donanım yazılımı engeli yok** ve hızlı, resmi olmayan bir yol istiyorsunuz (en çok kullanılan) | **Yöntem 2 — 表盘自定义工具 + Shizuku** |
| Shizuku kurmak istemiyorsunuz ve elinizde **小米穿戴 debug APK** var | **Yöntem 3** (en basit ama kaynağı gayri resmi) |

Pratik gerçek: bugün (2026 itibarıyla) toplulukta **en güvenilir ve herkesin erişebildiği yol
Yöntem 2'dir**. Yöntem 1 resmi ama özel bir uygulama sürümü gerektirir ve bireysel
başvurular çoğu zaman yanıtsız kalır. Yöntem 3 kurulumu en kolay olsa da APK kaynağı yalnızca
QQ grupları/gayri resmi paylaşımlar üzerindendir.

---

## Yöntem 1 — Resmi Mi Fitness "Debug" yolu (özel sürüm gerekir)

Xiaomi Vela dokümanları bu menüyü resmen tanımlar, ancak **kurulabilir uygulama sürümünün
varsayılan (Google Play / Mi Store) sürüm OLMADIĞINI** açıkça belirtir.

### Gerçek durum (dikkatle okuyun)

- Resmi Vela SSS sayfası şöyle der: *"Install Mi Fitness on your phone (**currently provided
  through business group 对接**). For Vela third-party app development, please contact
  Chang Jian via email: changjian@xiaomi.com."*
  → Yani uygulamayı yükleme yeteneği olan sürüm, **iş grubu üzerinden talep edilen özel bir
  build**'dir; herkese açık değildir.
- Bağımsız bir geliştirici (IYATT blog, Ağustos 2025 güncellemesi), şahsi geliştirici olduğunu
  belirterek `changjian@xiaomi.com` adresine e-posta attığını ve **hiçbir yanıt alamadığını**
  yazıyor.
- Topluluk raporları, Google Play'den veya Mi Store'dan inen **standart Mi Fitness'ın
  Debug → Third-Party Apps menüsünü göstermediğini** söylüyor.
  **UNCONFIRMED / Kısmen doğrulanmamış:** Google Play'deki hangi tam sürümün bu menüyü
  içerdiği net değildir; farklı ülke/bölge build'lerinde değişebilir. Riski göze almayın;
  varsayılan sürümde bu menü **yok** kabul edin.

### Resmi adımlar (yalnızca uygun debug sürüme sahipseniz)

1. Telefona, uygulama yükleme destekli **özel Mi Fitness** sürümünü kurun.
2. Mi Fitness'ı saatle senkronize edin (Bluetooth bağlı olsun).
3. **Ben (Me / 我的) → Hakkında (About / 关于) → Debug** yolunu izleyin.
4. **Üçüncü taraf uygulamalar (第三方应用 / Third-Party Apps)** seçeneğine dokunun.
5. **"Click to input package name"** (Paket adı girin) alanına dokunun.
6. Buraya `com.hyperpostulate.rw4compass` yazın (kurulumda herhangi bir şey yazılabilir;
   gerçek paket adı yalnızca **kaldırma** sırasında önemlidir).
7. **"Install third app"** (Üçüncü uygulama yükle) seçeneğini seçin.
8. Telefonda `dist/com.hyperpostulate.rw4compass.debug.1.0.0.rpk` dosyasını seçin.
9. Kurulum başarılı olursa bir **Toast bildirimi** görünür.

### Alternatif: resmi Mi Fitness'a eklenti enjekte etme (Wearable-Debug)

Kurulabilir sürümü alamayanlar için topluluk, resmi Mi Fitness'a **Wearable-Debug** eklentisini
enjekte etmeyi önerir:

- <https://github.com/A5245/Wearable-Debug>
- <https://github.com/loveCNL/Wearable-Debug>
- <https://github.com/YifePlayte/Wearable-Debug>

- **Xposed** (root gerekir) ile eklentiyi yükleyebilirsiniz; veya
- **LSPatch** (<https://github.com/LSPosed/LSPatch>) ile Mi Fitness'ı yamalayıp menüyü
  ekleyebilirsiniz.
- IYATT, Xiaomi HyperOS'lu bir telefonda yamanın kurulabildiğini ve menünün göründüğünü, ancak
  **Xiaomi hesabına giriş yapılamadığını ve saatin bağlanamadığını** bildiriyor. Bazı
  kullanıcılar **Xiaomi marka olmayan telefonlarda** çalıştığını söylüyor. **UNCONFIRMED.**

> **Sonuç:** Yöntem 1'i ancak özel build'e veya köklü/yamalı bir kurulum deneyimine sahipseniz
> deneyin. Çoğu kullanıcı için pratik değildir.

---

## Yöntem 2 — 表盘自定义工具 ("Watchface Custom Tool") + Shizuku

Bu, toplulukta **en yaygın ve en güncel (2025–2026)** yöntemdir. Araç, Mi Fitness'in günlük
(log) dosyasından telefon↔saat arası **AuthKey**'i okur ve `.rpk`'yi doğrudan Bluetooth ile
saate gönderir.

- Araç: **表盘自定义工具** (Türkçe: "Kadran Özelleştirme Aracı"), paket adı `tech.pingx.watchface`.
- Resmi indirme (米坛社区 / BandBBS resmi başlığı): <https://www.bandbbs.cn/threads/9797/>
  (Ekim 2026 itibarıyla sürüm **v6.5.4**; aynı sayfada Quark/Google Drive bağlantıları vardır).
- **Donanım:** Bluetooth kurulumu ("蓝牙一键安装") özelliği **bağış (donate)** gerektirir
  (yaklaşık 10 RMB, en az 3 yıl geçerli). Bağış yapmayanlar için reklam izleyerek açma sınırlı
  olarak sunulmuştur (v6.1.10'dan itibaren günde 6 kez).
- **Önemli uyumluluk:** Mi Fitness 3.29 sürümünden sonra "akıllı hızlı kurulum" mekanizması
  değişti. Aracın güncel sürümleri (v6.5.x) yeni Mi Fitness sürümleriyle (v3.59.0+) Shizuku
  üzerinden AuthKey okumayı destekler. Eski araç + yeni Mi Fitness **çalışmayabilir**; aracı
  güncel tutun.

### Ön koşullar

**Shizuku:** Android 11 ve üzeri sürümlerde, bilgisayar gerektirmeden **kablosuz hata ayıklama
(wireless debugging)** ile başlatılabilir. Android 10 ve altında USB ile bilgisayardan
başlatmak gerekir. Root varsa doğrudan çalışır. Kaynak: <https://shizuku.rikka.app/guide/setup/>

Shizuku'yu şu şekilde kurun:

1. Shizuku'yu (<https://shizuku.rikka.app/>) ve isterseniz Play Store'dan edinin.
2. Telefonda **Geliştirici Seçenekleri**'ni açın, **USB hata ayıklama**'yı ve (Xiaomi/MIUI/HyperOS
   için gerekli) **"USB hata ayıklama (Güvenlik ayarları)"** seçeneğini de açın.
3. Android 11+: **Kablosuz hata ayıklama**'yı açın → Shizuku'da "Pair device with pairing code"
   akışını izleyip eşleştirin → Shizuku'yu başlatın.
4. Android 10 ve altı: bilgisayarda platform-tools (adb) kurun, telefonu USB ile bağlayın ve
   `<sürüme göre>` `adb shell sh /sdcard/Android/data/moe.shizuku.privileged.api/start.sh`
   komutunu çalıştırın.
5. Shizuku çalışırken **表盘自定义工具**'a Shizuku iznini verin.

> MIUI/HyperOS ipuçları: Kablosuz hata ayıklama eşleştirmesi hemen başarısız olursa bildirim
> stilini "Android" yapın. Kablosuz hata ayıklamada Shizuku'nun arka planda çalışmasına izin
> verin (arka plan kısıtını kaldırın).

### 2a. Doğrudan Bluetooth kurulumu (önerilen yol)

1. 表盘自定义工具'u açın, **sağ üstten cihaz modelini "Redmi Watch 4" (红米手表4) seçin.**
2. Alt menüden **"Araçlar" (工具)** → **"AuthKey okuma aracı" (AuthKey读取工具)** seçin
   (bazı sürümlerde "快应用管理"/"蓝牙一键安装" ilk açılışta da ister).
   - "Okumaya başla" (开始读取) → cihazın yanındaki "Kopyala" (复制) düğmesine dokunun.
   - **Gerekirse:** Mi Fitness'ı açıp saatle bir kez bağlanın, sonra **Ben → Hakkında**'da
     Mi Fitness simgesine hızlıca birkaç kez dokunarak log dışa aktarımını tetikleyin (log
     `Android/data/com.mi.health/files/log/` altına yazılır). Aracın güncel sürümü bunu
     Shizuku üzerinden okur. **Android 11+**, `Android/data` klasörüne doğrudan erişimi
     engellediği için Shizuku (veya dosya yöneticisi izni) gerekir; eski Android sürümlerinde
     kısıt yoktur.
3. Ana sayfaya dönüp **"Araçlar" → "Bluetooth ile tek tıkla kurulum" (蓝牙一键安装)**
   seçeneğine dokunun.
   - Saat modelinizi seçin, AuthKey'i yapıştırın (gerekirse uzun basıp yapıştırın) ve bağlanın.
4. Kurmak istediğiniz `.rpk` dosyasını seçin: `com.hyperpostulate.rw4compass.debug.1.0.0.rpk`.
   - Araç "Dosya Seç" ekranını açarsa, indirdiğiniz `.rpk` dosyasını seçin.
5. **"Kurulumu başlat" (开始安装)** düğmesine basın.
   - "Mi Fitness saati meşgul ediyor" uyarısı çıkarsa, aracın gösterdiği talimatı uygulayın
     (genelde Mi Fitness'ta bağlantıyı geçici olarak bırakmak/kesmek gerekir).
6. Kurulum biter; saatte kurulum/onay ekranı görünebilir. Onayladığınızda **saat kendini
   yeniden başlatır** ve uygulama kurulmuş olur.

> Bu yöntem,表盘自定义工具'un Shizuku ile Mi Fitness günlüklerini okuyup telefon↔saat arası
> doğrulama anahtarını (AuthKey) almasına ve paketi doğrudan saate göndermesine dayanır.

### 2b. Kadran "yer değiştirme" hilesi (狸猫换太子) — donanım/bağış yoksa

Bu yol, resmi bir kadran kurulumu arasına hızlı uygulamayı gizlice yerleştirir:

1. Mi Fitness'ta **kadran mağazasından resmi bir kadran** seçip "İndir ve kullan"a basın.
2. 表盘自定义工具'da cihaz modelini RW4 seçin, indirdiğiniz **`.rpk`** dosyasını
   **"Araçlar" → "Hızlı uygulama kurulumu" (快应用安装)** ile açın.
   - **"Kurulum kadranı oluştur" (制作安装表盘)** düğmesine basın.
   - (Alternatif "usta yöntemi"/大师级方式: dönüştürülen kadran `tech.pingx.watchface/files/ebook.bin`
     olarak kaydedilir.)
3. 表盘自定义工具'u **küçük pencere (small window) moduna** alın.
4. Mi Fitness'ta az önce kurduğunuz resmi kadranın detayına gidin; sağ üstteki üç nokta →
   **kadranı sil (删除表盘)**.
5. Küçük pencerede 表盘自定义工具'daki **"Kurulumu başlat" (开始安装)** düğmesine basın, ardından
   Mi Fitness'taki **"İndir ve kullan" (下载并使用)** düğmesine dokunun.
6. Kurulum bitince 表盘自定义工具'da **"Durdur" (停止)** düğmesine basın.
7. Saatte bir **kurulum arayüzü** görünecek; dokunup onaylayın. **REDMI WATCH 4 genellikle hemen
   yeniden başlar.**
8. Yeniden başlatma sonrası kurduğunuz uygulama uygulama listesinde görünür. (Not: Bu yöntemde
   kadran, hızlı uygulama kurulum arayüzünü göstermeye devam edebilir; uygulamanın kendisi
   normal çalışır.)

> **Kritik uyarı:** Seçtiğiniz resmi kadran dosyası, yerleştirmek istediğiniz `.rpk`'den
> **daha büyük olmalıdır**, aksi halde kurulum başarısız olur. (IYATT blog ve BandBBS 9269
> bağımsız olarak teyit eder.)

---

## Yöntem 3 — 小米穿戴 (Xiaomi Wear) debug APK

Bu, bir topluluk/QQ grubu tarafından paylaşılan **debug sürümlü 小米穿戴** uygulamasıdır.
Mi Fitness ile **aynı telefonda birlikte var olabilir** ve **aynı hesapla giriş yapıldığında**
Mi Fitness'taki bağlı cihaz senkronize olur.

- IYATT testinde sürüm: **小米穿戴 debug 9.11.59**.
- **Yalnızca üçüncü taraf hızlı uygulama kurulumunu** destekler; **üçüncü taraf kadran
  desteklemez**.
- IYATT'a göre bu sürümde **kaldırma (uninstall) çalışmıyor**; kaldırmak için başka yol gerekir.

Adımlar:

1. 小米穿戴 debug APK'yı kurun (kaynak gayri resmi — aşağıdaki güvenlik notuna bakın).
2. Uygulamayı açın; Mi Fitness ile aynı Xiaomi hesabıyla giriş yapın ve bağlı cihazın
   (Redmi Watch 4) gelmesini bekleyin.
3. **"Cihaz fabrika testi" (设备工厂测试)** menüsünü açın.
4. **"ThirdAppDemo" (三方应用演示)** seçeneğine dokunun.
5. **"CLICK TO INPUT PACKAGE NAME"** alanına dokunup `com.hyperpostulate.rw4compass` yazın ve
   onaylayın.
6. **"INSTALL THIRD APP"** düğmesine basın ve telefondaki
   `com.hyperpostulate.rw4compass.debug.1.0.0.rpk` dosyasını seçin.
7. Kurulum doğrudan gerçekleşir (kadran yer değiştirme hilesine gerek yoktur).

> Bu yöntem en kolayı gibi görünse de kaynağı güvenilir bir resmi kanal değildir; APK'nın
> nereden geldiğini mutlaka doğrulayın ve mümkünse yalnızca sanal/atıl bir cihazda deneyin.

---

## Kurulumun başarılı olduğu nasıl doğrulanır?

- **Yöntem 1:** Kurulum sonrası bir **Toast** bildirimi görünür.
- **Yöntem 2 ve 3:** Saat, kurulum sırasında onay ekranı gösterir ve genelde **yeniden
  başlar**. Yeniden başlatma sonrası uygulama görünür.
- **Genel doğrulama:** 表盘自定义工具 → **"Araçlar" (工具) → "Hızlı uygulama yönetimi"
  (快应用管理)** yolundan bağlanıp, **kurulu uygulamalar listesinde** `com.hyperpostulate.rw4compass`
  (Pusula) görünüyor mu bakın. (Shizuku'nun çalışıyor olması gerekir.)

## Uygulama saatte nerede görünür?

- Saat, kurulumdan sonra yeniden başlar ve uygulama **uygulama listesinde (app list)** çıkar.
- Saatinizin ana ekranında uygulama çekmecesi/liste görünümünü açarak **Pusula**'yı arayın.
- Bazı durumlarda uygulamanın, kurulum aracı kadranı yerine normal liste girişinden açılması
  gerekir; kurulum sırasında saatte kalan "kurulum/kadran" arayüzünü normal bir kadranla
  değiştirebilirsiniz.

## Kaldırma ve güncelleme

- **Kaldırma (Yöntem 2):** Shizuku çalışır durumdayken 表盘自定义工具 → **"Araçlar" →
  "Hızlı uygulama yönetimi" (快应用管理)** → cihaza bağlanın → listeden uygulamayı seçip
  **"Kaldır" (卸载)**.
- **Kaldırma (Yöntem 1):** Resmi debug Mi Fitness → Debug → Third-Party Apps → paket adını
  `com.hyperpostulate.rw4compass` olarak girip kaldırın.
- **Kaldırma (Yöntem 3):** IYATT'a göre bu debug APK'da kaldırma **çalışmıyor**; 表盘自定义工具
  üzerinden kaldırmak gerekir.
- **Güncelleme:** Yeni bir `.rpk` derlediğinizde, aynı **paket adı** (`com.hyperpostulate.rw4compass`)
  ile üzerine kurun. Aynı sertifika/imza kullanılmasına dikkat edin (aşağıya bakın).

## Hızlı uygulama sayısı sınırı (~20) ve depolama

- REDMI WATCH 4 ve benzeri Vela cihazlarında **en fazla 20 hızlı uygulama** kurulabilir.
  (Yalnızca Mi Band 10 Pro ve Xiaomi Watch S5 bu sınırın dışındadır.) **İki bağımsız kaynak
  teyit eder.**
- REDMI WATCH 4'te hızlı uygulama kurmak için **en az ~87 MB boş alan** gerekir.
- **UNCONFIRMED / kullanıcı raporu:** "Usta yöntemi" (kadranı hızlı uygulamaya çevirme) ile
  20'lik sayı sınırı bir ölçüde aşılabiliyor; ancak REDMI WATCH 4'te bu yöntemin de depolama
  sınırına tabi olduğu ve çok zorlamanın sistem güncellemesini/veri kaydını etkileyebileceği
  belirtiliyor. Kesin davranış cihaz/yazılım sürümüne göre değişebilir.

## Sorun giderme

| Belirti | Olası neden | Çözüm |
|---|---|---|
| Kadran yer değiştirme kurulumu başarısız | Seçilen **resmi kadran, `.rpk`'den küçük** | Daha büyük bir resmi kadran seçip tekrar deneyin. |
| "Mi Fitness saati meşgul ediyor" hatası | Mi Fitness bağlantıyı tutuyor | Aracın talimatını uygulayıp Mi Fitness'ın bağlantısını geçici olarak bırakın/kesin, sonra kurun. |
| AuthKey okunamıyor / bağlanamıyor | Saat sıfırlandı veya eşleşme kaldırıldı → log'da **birden çok anahtar** var; araç ilkini okuyor | Aracın güncel sürümünü kullanın; gerekirse `Android/data/com.mi.health/files/log/` altındaki log dosyasını silin veya Mi Fitness'ı kaldırıp yeniden kurun; ya da `Download/wearable/` altındaki dışa aktarılmış logda `encryptKey`'i bulup son anahtarı elle girin. |
| Android 11+ `Android/data`'ya erişilemiyor | Android 11+ kısıtı | Shizuku'yu kurup 表盘自定义工具'a izin verin. |
| Kurulum "takılı" kalıyor / başarısız | **Çok hızlı art arda kurulum**; saat önceki uygulamayı yükleyemeden yenisi geldi | Her kurulumdan sonra saatin yanıt vermesini bekleyin; art arda hızlı kurulum yapmayın. |
| Araç "eski Mi Fitness" ile uyumsuz | Mi Fitness 3.29+ mekanizma değişikliği | 表盘自定义工具'u güncelleyin (v6.5.x). Eski sürüm gerekiyorsa bağış sayfası/araç 3.28.1 gibi eski Mi Fitness sürümlerine referans verir. |
| Saatte kurulum sonrası görünmüyor | Cihaz gerçekten kurmadı, sadece dosya indirildi | 表盘自定义工具 → 快应用管理 → kurulu uygulamalar listesini kontrol edin. |
| iPhone bağlıyken uygulama kayboldu | Vela hızlı uygulamaları iOS bağlantısında gizlenir | Saati Android telefondan yeniden bağlayın; iOS'ta kullanılamaz. |
| Paket kurulmuyor / imza hatası | İmza/sertifika uyuşmazlığı (özellikle saate telefonla veri gönderen uygulamalarda) | `.rpk` ve gerekliyse telefon uygulaması **aynı sertifika** ile paketlenmiş olmalı (Vela resmi dokümanı). |

## Güvenlik ve risk notu

- Yöntem 2 ve 3 **gayri resmi** araçlara ve gayri resmi APK kaynaklarına dayanır. 表盘自定义工具
  米坛社区 (BandBBS) topluluğu tarafından geliştirilir; kaynağı resmi Xiaomi kanalı değildir.
- Mi Fitness'a **Xposed/LSPatch ile yama** uygulamak (Wearable-Debug) hesap girişini bozabilir
  ve cihaz bağlamayı engelleyebilir.
- Kurulum sırasında **saat beklenmedik şekilde yeniden başlar**; devam eden senkronizasyon
  kesilebilir. Önemli verinizi önce senkronize edin.
- **Kırılmış (cracked) araç sürümlerini kullanmayın:** IYATT blogu, kullandığı kırılmış sürümün
  Kasım 2024'ten sonra geçersiz olduğunu ve **hesap yasağına** yol açtığını açıkça yazıyor.
- Üçüncü taraf `.rpk` yalnızca güvendiğiniz kaynaktan yükleyin; saate kurulan uygulamalar
  cihaz verilerine erişebilir.
- Xiaomi firmware/sürüm güncellemeleri bu gayri resmi yöntemleri her an bozabilir; araçların
  güncel sürümlerini takip edin.

## Kaynaklar

**Resmi (Xiaomi)**

- Xiaomi Vela JS App FAQ (İngilizce) — rpk'yı saate yükleme adımları ve "business group" notu:
  <https://iot.mi.com/vela/quickapp/en/guide/other/faq.html>
- Xiaomi Vela JS 应用 常见问题 (Çince) — aynı içerik, özgün ifade:
  <https://iot.mi.com/vela/quickapp/zh/guide/other/faq.html>
- Shizuku resmi kurulum kılavuzu:
  <https://shizuku.rikka.app/guide/setup/>

**Community (米坛社区 / BandBBS)**

- 表盘自定义工具 resmi indirme/güncelleme başlığı (v6.5.4, Ekim 2026):
  <https://www.bandbbs.cn/threads/9797/>
- REDMI WATCH 4 kurulum rehberi (常规/大师级 yöntem, AuthKey, 20 uygulama sınırı, 87 MB kural):
  <https://www.bandbbs.cn/threads/9269/>
- Shizuku kurulum eğitimi (米坛社区):
  <https://www.bandbbs.cn/threads/10268/>
- Hızlı uygulama indirme/kurulum SSS'i (20 sınırı, kurulum hataları):
  <https://www.bandbbs.cn/threads/29641>
- Xposed enjeksiyonlu Mi Fitness alternatif yöntemi:
  <https://www.bandbbs.cn/threads/15641>

**Community (blog / GitHub)**

- IYATT-yx blogu — "Redmi Watch 4 安装快应用/第三方表盘的方案" (Ağustos 2025 güncellemesi;
  üç yolu da kapsamlı anlatır):
  <https://blog.iyatt.com/?p=17811>
- Wearable-Debug (Mi Fitness'a kurulum menüsü ekleme eklentisi):
  <https://github.com/A5245/Wearable-Debug> ·
  <https://github.com/loveCNL/Wearable-Debug> ·
  <https://github.com/YifePlayte/Wearable-Debug>
- LSPatch (root'suz uygulama yamama):
  <https://github.com/LSPosed/LSPatch>

---

### Doğrulama durumu özeti

- **Doğrulanmış (≥2 bağımsız kaynak):** Resmi Mi Fitness Debug menü yolu ve adımları (Xiaomi
  resmi dokümanı, EN + ZH); kurulabilir Mi Fitness sürümünün varsayılan olmadığı (Xiaomi resmi
  metni + IYATT); 表盘自定义工具 + Shizuku AuthKey mekanizması (IYATT + BandBBS); kadranın
  `.rpk`'den büyük olması gerekliliği (IYATT + BandBBS 9269); ~20 hızlı uygulama sınırı ve RW4
  için ~87 MB boş alan (BandBBS 9269 + BandBBS 29641).
- **UNCONFIRMED / kullanıcı raporu:** Google Play'deki standart Mi Fitness'ın Debug menüsünü
  kesinlikle içermediği (topluluk genel kanısı, kesin sürüm belirsiz); Wearable-Debug
  enjeksiyonunun Xiaomi marka olmayan telefonlarda çalışması; "usta yöntemi"nin RW4'te 20
  sınırını tamamen aştığı.
- **UNCONFIRMED:** Yöntem 3 (小米穿戴 debug 9.11.59) APK'sının kaynağı yalnızca QQ grubu/gayri
  resmi paylaşımdır ve güncel sürümlerde davranış değişmiş olabilir.
