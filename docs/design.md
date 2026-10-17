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
Vela işletim sisteminin varsayılan metin rengi `rgba(0,0,0,0.54)` olduğu için gerçek siyah (`#000000`) arka planda görünmez hale gelmektedir. Ayrıca bazı cihazlarda sınıf tabanlı renk tanımlamaları her zaman stabil çalışmayabilmektedir. Okunabilirliği garanti altına almak adına tüm metne genel bir `text { color: #00C853; }` kuralı atanmış ve kritik alanlara inline (satır içi) renk stilleri eklenmiştir.

### Tipografi Ölçeği (Sistem Fontu)
Sadelik ve netlik için sınırlı bir yazı tipi skalası kullanılır. Hiyerarşi renklerle değil, boyutlarla sağlanır.

- **Ana Değer:** `20px` / Medium / Right
- **Yardımcı Bilgi (Etiket):** `16px` / Regular / Left
- **Alt Satır Detayı (DMS):** `14px` / Regular / Right

### Boşluk ve Yerleşim (Spacing)
- **Güvenli Kenar Payı (Safe Margin):** `16px` (Tüm kenarlarda korunmalıdır).
- **Satır Aralığı:** Sabit `12px` (Her veri bloğu arasında).

---

## 2. Ekran: GPS (Veri Listesi)

GNSS verilerinin sunulduğu tek ekran yapısıdır. Elemanlar yukarıdan aşağıya doğru dikey bir liste halinde sıralanır.

### Veri Satırları (Yerleşim: Flex Row, Space-Between)
Her satır; sol tarafta `16px Yeşil Metin` etiket ve sağ tarafta `20px Yeşil Metin` değer şeklinde kurgulanır.

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

**Önemli:** Kararlılık için her `<text>` bileşenine inline `color` ve `font-size` atanmıştır. Global seçici ise temel fallback sağlar.

```css
/* Temel Fallback */
text {
  color: #00C853;
}

.app {
  width: 100%;
  height: 100%;
  background-color: #000000;
}

.screen {
  position: relative;
  width: 100%;
  height: 100%;
  background-color: #000000;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* GPS veri listesi */
.gps {
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  padding: 16px;
}

.gps-list {
  width: 100%;
  flex-direction: column;
  align-items: flex-start;
  flex-grow: 1;
}

/* Veri Satırı Stili */
.data-row {
  width: 100%;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.label {
  font-size: 16px;
  color: #00C853;
}

.value-col {
  flex-direction: column;
  align-items: flex-end;
}

.value {
  font-size: 20px;
  color: #00C853;
  text-align: right;
}

.sub {
  font-size: 14px;
  color: #00C853;
  text-align: right;
}

/* Durum Çubuğu */
.status-row {
  width: 100%;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin-top: 6px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 6px;
  margin-right: 8px;
  background-color: #FFD600;
}

.status-text {
  font-size: 16px;
}
```
