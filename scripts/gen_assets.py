#!/usr/bin/env python3
"""Reproducible PNG asset generator for gps-info.

Why images? The Redmi Watch 4 Vela quick-app runtime does not render any
text glyphs (verified on device: <text>, <input type=button> and
<input type=text> all paint nothing / notdef boxes), while <image> renders
perfectly. So every piece of visible text is pre-rendered here to PNG and
shown with <image>.

Run from anywhere:

    python3 scripts/gen_assets.py

Writes into src/common/:
  - logo.png                     192x192 app icon (black rounded square + pin)
  - txt/lbl_*.png                static row labels (green)
  - txt/st_*.png                 status strings (colored)
  - txt/g_*.png                  monospace glyph cells for dynamic values (green)

Idempotent: running repeatedly produces the same output. Each written file is
re-opened and verified (dimensions + non-blank content).
"""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "src", "common")
TXT_DIR = os.path.join(OUT_DIR, "txt")
FONT_PATH = os.path.join(ROOT, "scripts", "assets", "gpsinfo.ttf")
os.makedirs(TXT_DIR, exist_ok=True)

SS = 4  # supersampling factor for crisp anti-aliasing

# ---- palette (docs/design.md section 1) ----
GREEN = (0, 200, 83, 255)    # #00C853
AMBER = (255, 214, 0, 255)   # #FFD600
RED = (207, 102, 121, 255)   # #CF6679
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
DARK_HOLE = (17, 17, 17, 255)

# ---- text image geometry (design px; PNG is SS x larger) ----
LABEL_CANVAS = (240, 60)
LABEL_FONT = 38
LABEL_AT = (24, 30)  # left-middle anchor (ample left margin: avoids edge clip)

STATUS_CANVAS = (620, 60)
STATUS_FONT = 34
STATUS_AT = (6, 30)

GLYPH_CANVAS = (40, 64)
GLYPH_FONT = 52
GLYPH_BASELINE = 50  # y of the baseline inside the cell

# Value character set -> file stem. Keep in sync with GMAP in index.ux.
GLYPHS = {
    "0": "g_0", "1": "g_1", "2": "g_2", "3": "g_3", "4": "g_4",
    "5": "g_5", "6": "g_6", "7": "g_7", "8": "g_8", "9": "g_9",
    ".": "g_dot", "-": "g_dash", "\u00b0": "g_deg", "'": "g_min",
    '"': "g_sec", ":": "g_colon", "/": "g_slash",
    "(": "g_lpar", ")": "g_rpar", "+": "g_plus", "\u00b1": "g_pm",
    " ": "g_sp",
    "m": "g_m", "s": "g_s", "k": "g_k", "h": "g_h",
    "K": "g_K", "G": "g_G", "D": "g_D", "B": "g_B",
}

LABELS = [
    ("lbl_enlem", "Enlem"),
    ("lbl_boylam", "Boylam"),
    ("lbl_irtifa", "\u0130rtifa"),
    ("lbl_hiz", "H\u0131z"),
    ("lbl_dogruluk", "Do\u011fruluk"),
    ("lbl_zaman", "Zaman"),
]

STATUS = [
    ("st_uydu", "Uydu Ba\u011flant\u0131s\u0131 Kuruluyor...", AMBER),
    ("st_araniyor", "Konum Aran\u0131yor...", AMBER),
    ("st_guclu", "Sinyal G\u00fc\u00e7l\u00fc", GREEN),
    ("st_desteklenmiyor", "Desteklenmiyor", RED),
    ("st_zamanasimi", "Zaman A\u015f\u0131m\u0131", RED),
    ("st_konumkapali", "Konum Kapal\u0131", RED),
    ("st_sinyalyok", "Sinyal Yok", RED),
]


def _font(size):
    return ImageFont.truetype(FONT_PATH, size)


def _save_verified(name, img, size, allow_blank=False):
    assert img.size == size, (name, img.size, size)
    if not allow_blank:
        assert img.getbbox() is not None, "blank image: %s" % name
    path = os.path.join(TXT_DIR, name)
    img.save(path)
    chk = Image.open(path)
    chk.load()
    assert chk.size == size, (name, chk.size, size)
    if not allow_blank:
        assert chk.getbbox() is not None, "blank on disk: %s" % name


def make_text_image(name, text, size, font_size, at, fill):
    n = (size[0] * SS, size[1] * SS)
    img = Image.new("RGBA", n, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((at[0] * SS, at[1] * SS), text, font=_font(font_size * SS),
           fill=fill, anchor="lm")
    img = img.resize(size, Image.LANCZOS)
    _save_verified(name + ".png", img, size)


def make_glyph(ch, stem):
    n = (GLYPH_CANVAS[0] * SS, GLYPH_CANVAS[1] * SS)
    img = Image.new("RGBA", n, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = (GLYPH_CANVAS[0] * SS) / 2.0
    by = GLYPH_BASELINE * SS
    d.text((cx, by), ch, font=_font(GLYPH_FONT * SS), fill=GREEN, anchor="ms")
    img = img.resize(GLYPH_CANVAS, Image.LANCZOS)
    _save_verified(stem + ".png", img, GLYPH_CANVAS, allow_blank=(ch == " "))


def make_logo():
    S = 192
    N = S * SS
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = N / 2.0, N / 2.0

    margin = int(N * 0.02)
    radius = int(N * 0.22)
    d.rounded_rectangle([margin, margin, N - margin, N - margin],
                        radius=radius, fill=BLACK)

    head_center_y = cy - (N * 0.05)
    head_rad = N * 0.22
    d.ellipse(
        [cx - head_rad, head_center_y - head_rad,
         cx + head_rad, head_center_y + head_rad], fill=WHITE)
    d.polygon(
        [(cx - head_rad * 0.78, head_center_y + head_rad * 0.62),
         (cx + head_rad * 0.78, head_center_y + head_rad * 0.62),
         (cx, cy + N * 0.22)], fill=WHITE)
    hole = head_rad * 0.42
    d.ellipse([cx - hole, head_center_y - hole, cx + hole, head_center_y + hole],
              fill=DARK_HOLE)

    out = img.resize((S, S), Image.LANCZOS)
    path = os.path.join(OUT_DIR, "logo.png")
    out.save(path)
    chk = Image.open(path)
    chk.load()
    assert chk.size == (S, S)
    assert chk.getbbox() is not None


def main():
    make_logo()
    for stem, text in LABELS:
        make_text_image(stem, text, LABEL_CANVAS, LABEL_FONT, LABEL_AT, GREEN)
    for stem, text, color in STATUS:
        make_text_image(stem, text, STATUS_CANVAS, STATUS_FONT, STATUS_AT, color)
    for ch, stem in GLYPHS.items():
        make_glyph(ch, stem)
    print("generated %d label + %d status + %d glyph images + logo"
          % (len(LABELS), len(STATUS), len(GLYPHS)))


if __name__ == "__main__":
    main()
