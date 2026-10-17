# UI/UX Tasarım Spesifikasyonu: rw4-poc (Redmi Watch 4)

Bu belge, Redmi Watch 4 için geliştirilen **rw4-poc** uygulamasının kesin tasarım kurallarını belirler. Uygulama, cihaz saatinden okunan dört değeri tek ekranda sunar.

## 1. Genel Görsel Dil

### Tema ve Renk Paleti
AMOLED enerji tasarrufu için tamamen siyah arka plan zorunludur.

| Kullanım Alanı | Değer (Hex) | Açıklama |
| :--- | :--- | :--- |
| **Arka Plan** | `#000000` | Saf Siyah (True Black) |
| **Başlık ve Değerler** | `#00C853` | Canlı Yeşil |

### Kritik Cihaz Notu: Metin Görsel Olarak Çizilir
Redmi Watch 4'ün Vela çalışma zamanı `<text>`/`<span>`/`<input>` bileşenleri için **hiçbir okunabilir glif çizmez** (gerçek cihazda doğrulandı; paketlenen bir `@font-face` fontu da etkisizdir). `<image>` ise sorunsuz çizilir. Bu nedenle:

- **Statik yazılar** (başlık, etiketler) tek bir PNG olarak üretilip `<image src="...">` ile gösterilir.
- **Dinamik değerler** (tarih, saat, dilim, unix) tek aralıklı bir **glif atlasından** dizilir: her karakter için ayrı bir şeffaf PNG (`src/common/txt/g_<kod noktası hex>.png`). Şablonda `for="{{ row }}"` + `src="{{ $item }}"` ile karakter başına bir `<image>` çizilir.
- Atlas dışı bir karakter `?` olarak çizilir (`0x3F`).

Tüm görseller `scripts/gen_assets.py` tarafından belirlenimci biçimde üretilir ve her dosya yazıldıktan sonra geri okunup doğrulanır.

### Tipografi Ölçeği (Görsel)
Hiyerarşi renkle değil, görsel boyutuyla sağlanır.

- **Başlık:** 310×42 px görsel ( "Redmi Watch 4 PoC" )
- **Etiket:** 150×25 px görsel
- **Değer glifi:** 16×22 px (glif hücresi 48×64'ten küçültülür)

### Boşluk ve Yerleşim (Spacing)
- **Sol kenar payı:** `16px` (`.app` padding-left).
- **Üst kenar payı:** `44px` (yuvarlak ekran köşesinden kaçınmak için başlık bir satır aşağıda).
- **Başlık altı boşluk:** `18px`.
- **Satır aralığı:** `16px` (her `.row` margin-bottom).

---

## 2. Ekran: Zaman (Tek Ekran)

Elemanlar yukarıdan aşağıya dikey bir liste halinde sıralanır. Her satır; üstte küçük yeşil etiket görseli, altında tam genişlikte yeşil glif dizisi içerir.

| Alan | Format | Örnek |
| :--- | :--- | :--- |
| **Tarih** | `YYYY-AA-GG` | `2026-10-18` |
| **Saat** | `SS:DD:SS` (her saniye) | `14:23:05` |
| **Dilim** | `UTC±SS:DD` | `UTC+03:00` |
| **Unix** | saniye (tam sayı) | `1760797385` |

### Durum Matrisi
Tek durum vardır: saatin her saniye yenilenmesi. Bir saniyelik `setInterval` sayfa gösterildiğinde başlar, gizlendiğinde/destroy edildiğinde durur (pil tasarrufu). Uygulama hiçbir izin istemez; yalnızca JS saati (`new Date()`) kullanılır.

---

## 3. Varlık (Asset) Spesifikasyonları

### `logo.png` (App Icon)
- **Boyut:** **96×96 px** (bilinçli, tesadüf değil). Başlatıcı, ismin solunda ayırdığı alanın genişliğini simge PNG'sinin piksel boyutundan türetir; **192×192** (Vela dokümanlarının önerdiği boyut) ismi satırın ortasına itiyordu, **96×96** normal konumuna getirdi (cihazda doğrulandı).
- **İçerik:** Tam kanama siyah daire + **beyaz saat gövdesi** (üst/alt beyaz kayış çıkıntıları) + ortada **yeşil (`#00C853`) ekran** — uygulamanın özgün simgesi.
- Not: Başlatıcının koyu zemininde siyah daire pratikte görünmez; okunan şey beyaz saat gövdesi ve yeşil ekranıdır.
- Simge konumu ve isim hizası başlatıcı tarafından belirlenir; manifestten değiştirilemez.

### `txt/title.png`, `txt/lbl_*.png`
- Yeşil (`#00C853`) metin, şeffaf zemin, 4× süper örnekleme.
- Etiket tuvali 360×60 (görüntülenen 150×25); başlık tuvali 620×84 (görüntülenen 310×42).

### `txt/g_<hex>.png` (Glif Atlası)
- **Boyut:** 48×64 px (ekranda 16×22).
- Yeşil glif, şeffaf zemin, taban çizgisi hücre içinde 52 px.
- **Karakter seti (`CHARS`):** `0-9`, `.`, `-`, `:`, `+`, `U`, `T`, `C` — yalnızca saat ekranının üretabileceği karakterler. Yeni dinamik metin eklenirse buraya karakter eklenmelidir.
- **Uyarı:** Çok sayıda glif görseli ekranı yavaşlatır; ekrandaki `<image>` sayısını az tutun.

---

## 4. Stil Blokları

`src/pages/index/index.ux` içinde kullanılan stiller. Vela'da `display` ve `gap` yoktur; yerleşim `flex-direction` ve `margin` ile kurulur.

```css
.app { width: 390px; height: 450px; flex-direction: column; align-items: flex-start; justify-content: flex-start; padding-left: 16px; padding-top: 44px; background-color: #000000; }
.title { width: 310px; height: 42px; margin-left: 4px; margin-bottom: 18px; }
.row { width: 360px; flex-direction: column; align-items: flex-start; justify-content: flex-start; margin-bottom: 16px; }
.lbl { width: 150px; height: 25px; margin-left: 4px; }
.val { width: 348px; flex-direction: row; align-items: center; justify-content: flex-start; margin-left: 4px; }
.g { width: 16px; height: 22px; }
```
