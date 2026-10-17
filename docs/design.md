# UI/UX Tasarım Spesifikasyonu: GPS Info (Redmi Watch 4)

Bu belge, Redmi Watch 4 akıllı saat için geliştirilen GPS Info uygulamasının kesin tasarım kurallarını belirler. Uygulama, tek ekran üzerinden yüksek okunabilirlikte GNSS verilerini sunmayı amaçlar.

## 1. Genel Görsel Dil

### Tema ve Renk Paleti
AMOLED enerji tasarrufu için tamamen siyah arka plan zorunludur. Kontrast, düşük ışıklı ortamlarda okunabilirliği artırmak için maksimize edilmiştir.

| Kullanım Alanı | Değer (Hex) | Açıklama |
| :--- | :--- | :--- |
| **Arka Plan** | `#000000` | Saf Siyah (True Black) |
| **Genel Veri Metni** | `#00C853` | Canlı Yeşil - Tüm koordinat, etiket ve değerler |
| **Uyarı/Arama** | `#FFD600` | Sarı - Uydu araması devam ediyor |
| **Hata** | `#CF6679` | Pastel Kırmızı - Sistem hataları veya kapalı sensör |
| **Vurgu/Logo** | `#FF4D4D` | Parlak Kırmızı - Uygulama ikonu detayı |

### Cihaz Uyumluluğu Notu
RW4 Vela metin işleyici sistemi, `<text>` bileşenleri için açıkça belirtilmiş `width` ve `height` değerlerine ihtiyaç duyar; aksi takdirde otomatik boyutlandırma (~0x0) nedeniyle metinler kaybolmakta veya tek karakterden sonra alt satıra geçerek okunmaz hale gelmektedir. Bu nedenle yerleşim planı, esnek (flex auto-sizing) yapılar yerine sabit boyutlu geometrik kutular üzerine kurulmuştur. Metinlerin yanlış yere kırılmasını önlemek için `lines: 1` parametresi kullanılmış ve uzun değerlerin düzgünce kesilmesi için `text-overflow: ellipsis` uygulanmıştır. Standart tasarım genişliği (`designWidth`) 390px olarak belirlenmiştir.

### Tipografi Ölçeği (Sistem Fontu)
Sadelik ve netlik için sınırlı bir yazı tipi skalası kullanılır. Hiyerarşi renklerle değil, boyutlarla sağlanır.

- **Ana Değer:** `20px` / Medium / Right
- **Yardımcı Bilgi (Etiket):** `16px` / Regular / Left
- **Alt Satır Detayı (DMS):** `14px` / Regular / Right

### Boşluk ve Yerleşim (Spacing)
- **Güvenli Kenar Payı (Safe Margin):** `12px` (Tüm kenarlarda korunmalıdır — `.screen` padding).
- **Satır Aralığı:** Sabit `6px` (Her veri bloğu arasında — `.data-row` margin-bottom).

---

## 2. Ekran: GPS (Veri Listesi)

GNSS verilerinin sunulduğu tek ekran yapısıdır. Elemanlar yukarıdan aşağıya doğru dikey bir liste halinde sıralanır.

### Veri Satırları (Sabit Geometri)
Her satır; sol tarafta `16px Yeşil Metin` etiket ve sağ tarafta `20px Yeşil Metin` değer içeren sabit boyutlu kapsayıcılar şeklinde kurgulanır.

| Alan | Format (Sağ Taraf) | Notlar |
| :--- | :--- | :--- |
| **Enlem** | `41.00823°` <br/> `41° 00' 29.6" K` | Alt satır DMS formatındadır (`14px yeşil`) |
| **Boylam** | `28.97839°` <br/> `28° 58' 42.2" D` | Alt satır DMS formatındadır (`14px yeşil`) |
| **İrtifa** | `152 m` | Deniz seviyesinden metre cinsinden yükseklik |
| **Hız** | `1.2 m/s (4.3 km/h)` | Hem m/s hem km/h gösterimi yapılır |
| **Doğruluk** | `± 3.5 m` | Mevcut konumun yatay hassasiyeti |
| **Zaman** | `14:20:05` | Güncel UTC/Local zaman damgası |

### Durum Çubuğu (Ekran Altı)
Listenin en altında yer alan dinamik bilgi alanı:
- **Aranıyor:** Sarı metin ve sarı nokta. `"Konum Aranıyor..."`
- **Aktif (Fix):** Yeşil metin. `"Sinyal Güçlü"`
- **Hatalar:** Kırmızı metin.
  - Kod 203: `"Desteklenmiyor"`
  - Kod 204: `"Zaman Aşımı"`
  - Kod 1000+: `"Konum Kapalı"`

---

## 3. Durum Matrisi (Copy Guide)

Uygulamanın çalışma anındaki farklı senaryolar için içerik rehberi:

| Senaryo | Metin İçeriği | Görsel Durum |
| :--- | :--- | :--- |
| **İlk Açılış** | `"Uydu Bağlantısı Kuruluyor..."` | Sarı Dot (Statik) |
| **Normal Çalışma** | `[Güncel Koordinatlar ve Veriler]` | Yeşil Durum Metni / Statik Liste |
| **Çevrimdışı** | `"SİNYAL YOK (Kod: XXX)"` | Kırmızı Durum Metni / Veri Alanları Boş |

---

## 4. Varlık (Asset) Spesifikasyonları

Sadece uygulama simgesine ait tanımlamalar mevcuttur.

### `logo.png` (App Icon)
- **Boyut:** $192 \times 192\text{ px}$ (Opaque RGB)
- **Zemin:** Siyah (`#000000`), köşeler $22\%$ oranında yuvarlatılmış kare.
- **Simge Geometrisi:** 
  - **Tip:** Modern Lokasyon Pini (Location Pin).
  - **Renk:** Ana gövde Beyaz (`#FFFFFF`).
  - **Yapı:** Ortalanmış dairesel başlık ve aşağıya doğru sivrilen kuyruk.
  - **Detay:** Başlık merkezinde koyu gri (`#111111`) dairesel boşluk; boşluğun çevresinde çok ince kırmızı (`#FF4D4D`) vurgu halkası.
- **Teknik:** Asset, $4\times$ süper örnekleme (supersampling) sonrası Lanczos filtresiyle küçültülmüştür.

---

## 5. Uygulama Notları ve Stil Blokları

Aşağıdaki blok, `src/pages/index/index.ux` içinde referans alınan stillerdir. Vela'da `display` ve `gap` yoktur; yerleşim doğrudan `flex-direction` ile kurulur, aralıklar `margin` ile verilir. 

**Not:** Gerçek cihazdaki render sorunlarını aşmak amacıyla her `<text>` bileşenine inline `width`, `height`, `lines`, `font-size` ve `color` nitelikleri atanmıştır. Aşağıdaki CSS kuralları bu inline tanımların aynısını yansıtmaktadır.

```css
.app { width: 390px; height: 450px; background-color: #000000; }
.screen { width: 390px; height: 450px; padding: 12px; flex-direction: column; align-items: flex-start; justify-content: flex-start; background-color: #000000; }
.gps-list { width: 366px; height: 360px; flex-direction: column; align-items: flex-start; }
.data-row { width: 366px; height: 54px; flex-direction: row; align-items: center; justify-content: flex-start; margin-bottom: 6px; }
.label { width: 120px; height: 26px; font-size: 16px; lines: 1; color: #00C853; }
.value-col { width: 240px; height: 52px; flex-direction: column; align-items: flex-end; justify-content: center; }
.value { width: 240px; height: 28px; font-size: 20px; lines: 1; text-align: right; text-overflow: ellipsis; color: #00C853; }
.sub { width: 240px; height: 22px; font-size: 14px; lines: 1; text-align: right; text-overflow: ellipsis; color: #00C853; }
.status-row { width: 366px; height: 36px; margin-top: 6px; flex-direction: row; align-items: center; justify-content: center; }
.status-dot { width: 12px; height: 12px; border-radius: 6px; margin-right: 8px; }
.status-text { width: 320px; height: 24px; font-size: 16px; lines: 1; text-overflow: ellipsis; color: #00C853; }
```
