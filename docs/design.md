# UI/UX Tasarım Spesifikasyonu: Pusula & GPS (Redmi Watch 4)

Bu belge, Redmi Watch 4 akıllı saat için geliştirilen Pusula ve GPS uygulamasının kesin tasarım kurallarını belirler. Yazılım ekibi tarafından herhangi bir tasarım kararı verilmeden doğrudan uygulanmalıdır.

## 1. Genel Görsel Dil

### Tema ve Renk Paleti
AMOLED enerji tasarrufu için tamamen siyah arka plan zorunludur.

| Kullanım Alanı | Değer (Hex) | Açıklama |
| :--- | :--- | :--- |
| **Arka Plan** | `#000000` | Saf Siyah (True Black) |
| **Birincil Metin** | `#FFFFFF` | Beyaz - Ana veriler ve başlıklar |
| **İkincil Metin** | `#BDBDBD` | Açık Gri - Etiketler ve yardımcı bilgiler |
| **Vurgu (Kuzey)** | `#FF4D4D` | Parlak Kırmızı - Kuzey oku ve kritik uyarılar |
| **Başarı/Sabitlendi** | `#00C853` | Canlı Yeşil - GPS Fix durumu |
| **Uyarı/Arama** | `#FFD600` | Sarı - Konum aranıyor durumu |
| **Hata** | `#CF6679` | Pastel Kırmızı - Sensör hatası / Desteklenmiyor |

### Tipografi Ölçeği (Sistem Fontu)
Font ailesi olarak cihazın sistem varsayılanı kullanılır.

- **Devasa Veri (Derece):** `64px` / Bold / Center
- **Ana Başlık/Değer:** `20px` / Medium / Left/Right
- **Yardımcı Bilgi (Etiket):** `16px` / Regular / Left
- **Rozet Metni:** `14px` / Medium / Center / Letter-spacing: `1px`

### Boşluk ve Yerleşim (Spacing)
- **Güvenli Kenar Payı (Safe Margin):** `16px` (Köşe yuvarlatmaları nedeniyle tüm kenarlarda bırakılmalıdır).
- **Satır Aralığı:** `12px` ile `18px` arası standart boşluklar.

---

## 2. Ekran 1: Pusula (Giriş Ekranı)

Bu ekran, kullanıcıyı karşılayan temel navigasyon merkezidir. Katmanlı yapı için `<stack>` bileşeni kullanılacaktır.

### Yerleşim Yapısı (Alt'tan Üst'e)
1. **Katman 1 (Kadran):** Merkezde dönen `dial.png` dosyası.
2. **Katman 2 (İndeks):** En üst ortada sabit duran `index-marker.png`.
3. **Katman 3 (Bilgi Paneli):** Alt bölgede dereceler ve durum bilgileri içeren şeffaf panel.

### Detaylar
- **Merkez Derece:** `64px` beyaz metin. Örn: `"247°"`
- **Yön Kısaltması:** Derecenin hemen altında `20px` gri metin. Örn: `"GB"` (K, KD, D, GD, G, GB, B, KB).
- **Kaynak Rozeti:** En altta küçük bir kapsül. 
  - Manyeto aktifse: `bg: #333`, text: `"MANYETO"`, renk: Beyaz.
  - GPS Fallback ise: `bg: #443300`, text: `"GPS YÖNÜ"`, renk: Sarı (`#FFD600`).
  - Hata varsa: `bg: #442222`, text: `"SENSÖR HATASI"`, renk: Kırmızı.
- **Hassasiyet Göstergesi:** İndeks marker'ın yanına veya altına konulan nokta:
  - High (3): Yeşil | Med (2): Sarı | Low (1): Turuncu | Fail (-1): Kırmızı.

### Dinamik Hareket
- **Rotasyon:** Kadran `transform: rotate(Ndeg)` ile döndürülür.
- **Geçiş:** `transition: transform 120ms linear`. Keskin sıçramaları önlemek adına doğrusal geçiş tercih edilmiştir.
- **Mantık:** $359^\circ \to 0^\circ$ geçişlerinde görsele takılma olmaması için yazılımsal "angle wrapping" uygulanmalı, ancak CSS tarafında sadece hedef açıya odaklanılmalıdır.

---

## 3. Ekran 2: GPS (Detay Ekranı)

Canlı GNSS verilerinin sunulduğu liste tabanlı bilgi ekranıdır. Tüm elemanlar dikey bir `flex` yapısında sıralanır.

### Veri Satırları (Yerleşim: Flex Row, Space-Between)
Her satır; sol tarafta `16px Secondary Text` etiket ve sağ tarafta `20px Primary Text` değer şeklinde kurgulanır.

| Alan | Format (Sağ Taraf) | Notlar |
| :--- | :--- | :--- |
| **Enlem** | `41.00823°` <br/> `41° 00' 29.6" K` | Alt satır daha küçük (`14px grey`) |
| **Boylam** | `28.97839°` <br/> `28° 58' 42.2" D` | Alt satır daha küçük (`14px grey`) |
| **İrtifa** | `152 m` | Deniz seviyesinden yükseklik |
| **Hız** | `1.2 m/s (4.3 km/h)` | Birimler parantez içinde |
| **Doğruluk** | `± 3.5 m` | Yatay hassasiyet değeri |
| **Zaman** | `14:20:05` | Son güncelleme saati |

### Durum Çubuğu (Alt Bölüm)
En alt satırda konum durumunu belirtir:
- **Aranıyor:** Sarı metin, yanında yanıp sönen (opacity pulse) bir nokta. `"Konum Aranıyor..."`
- **Aktif (Fix):** Yeşil metin. `"Sinyal Güçlü"`
- **Hatalar:** Kırmızı metin.
  - Kod 203: `"Desteklenmiyor"`
  - Kod 204: `"Zaman Aşımı"`
  - Kod 1000+: `"Konum Kapalı"`

---

## 4. Navigasyon ve Akış

- **Kontrol:** Vertikal Swiper (`vertical=true`).
- **Yön:** Yukarı kaydırma $\to$ GPS ekranı; Aşağı kaydırma $\to$ Pusula ekranı.
- **Gösterge:** Sayfa altındaki nokta göstergeleri (dots) kapatılmıştır; temiz görüntü hedeflenmektedir.

---

## 5. Durum Matrisi (Copy Guide)

| Senaryo | Ekran 1 Metin | Ekran 2 Metin | Görsel Durum |
| :--- | :--- | :--- | :--- |
| **İlk Açılış** | `"Sensörler Hazırlanıyor..."` | `"Uydu Bağlantısı Kuruluyor..."` | Pulse Animasyon |
| **Normal Çalışma** | `[Derece]°` | `[Koordinatlar]` | Standart Temiz Görünüm |
| **Manyeto Yok** | `"GPS Yönü"` (Badge) | `[Veriler]` | Badge Rengi: Sarı |
| **Tamamen Çevrimdışı** | `"SENSÖR DESTEKLENMİYOR"` | `"SİNYAL YOK (Kod: XXX)"` | Renk: Kırmızı |

---

## 6. Varlık (Asset) Spesifikasyonları

Tüm varlıklar PNG formatında, şeffaf arka planla üretilecektir.

### `dial.png` (Ana Kadran)
- **Boyut:** $360 \times 360\text{ px}$
- **Merkez Noktası:** $(180, 180)$
- **Ticks (Çentikler):**
  - Major ($30^\circ$ ara): Uzun çizgi, Genişlik: $2\text{px}$, Boy: $15\text{px}$. Renk: `#FFFFFF`.
  - Minor ($15^\circ$ ara): Kısa çizgi, Genişlik: $2\text{px}$, Boy: $8\text{px}$. Renk: `#BDBDBD`.
- **Harfler (Cardinal Points):**
  - **K** ($0^\circ$), **D** ($90^\circ$), **G** ($180^\circ$), **B** ($270^\circ$).
  - Font size: $24\text{px}$, Weight: Bold, Color: `#FFFFFF`.
- **Ara Yönler:** KD, GD, GB, KB. Daha küçük font ($16\text{px}$) ve hafif gri renkte.
- **Kuzey İşareti:** "K" harfinin üzerinde veya merkezden dışa doğru uzanan ince bir kırmızı vurgu çizgisi (`#FF4D4D`).
- **Alignment:** Resmin en üst orta noktası $0^\circ$ (Kuzey) olarak kabul edilir.

### `index-marker.png` ( Sabit Gösterge)
- **Boyut:** $40 \times 40\text{ px}$
- **Şekil:** Aşağı bakan dar bir üçgen veya elmas formu.
- **Renk:** `#FF4D4D` (Parlak Kırmızı).
- **Pozisyon:** Ekranda kadranın üst kenarıyla hizalanmış şekilde sabitlenir.

### `logo.png` (App Icon)
- **Boyut:** $192 \times 192\text{ px}$
- **İçerik:** Siyah kare zemin üzerine minimalist beyaz pusula iğnesi; iğnenin uç kısmı parlak kırmızı.

---

## 7. Uygulama Notları ve Stil Blokları

Taslak CSS sınıfları aşağıdadır. `stack` kullanımı kritik olduğundan, katmanlama bu mantığa göre yapılmalıdır.

```css
/* Ana Konteyner */
.screen-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #000000;
  width: 390px;
  height: 450px;
  padding: 16px;
}

/* Dönüş Efekti */
.rotating-dial {
  width: 360px;
  height: 360px;
  transition: transform 120ms linear;
}

/* Veri Satırı Stili */
.data-row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 12px;
}

.label {
  color: #BDBDBD;
  font-size: 16px;
}

.value {
  color: #FFFFFF;
  font-size: 20px;
  text-align: right;
}

/* Durum Rozeti */
.badge {
  padding: 4px 8px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: medium;
  letter-spacing: 1px;
}
```