#!/usr/bin/env python3
"""Reproducible PNG asset generator for the rw4-poc quick app.

Why images? The Redmi Watch 4 Vela runtime does not draw text glyphs (verified
on device: <text>, <input type=button> and <input type=text> all paint nothing
or notdef boxes), while <image> renders perfectly. So every visible piece of
text is pre-rendered to PNG and shown with <image>.

Dynamic values (the clock, timezone, unix timestamp) are composed at runtime
from a small monospace glyph atlas: one transparent PNG per character,
addressed by its codepoint in hex (g_<hex>.png). index.ux maps each character
of a string to '/common/txt/g_' + code.toString(16) + '.png'.

Run from anywhere:

    python3 scripts/gen_assets.py

Writes into src/common/txt/:
  - title.png      screen header
  - lbl_*.png      static field labels (green)
  - g_*.png        monospace glyph cells, g_<codepoint hex>.png (green)

Idempotent, and every written file is re-opened and verified.
"""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "src", "common")
TXT_DIR = os.path.join(OUT_DIR, "txt")
FONT_PATH = os.path.join(ROOT, "scripts", "assets", "gpsinfo.ttf")

if os.path.isdir(TXT_DIR):
    for name in os.listdir(TXT_DIR):
        if name.endswith(".png"):
            os.remove(os.path.join(TXT_DIR, name))
os.makedirs(TXT_DIR, exist_ok=True)

SS = 4  # supersampling factor for crisp anti-aliasing

# ---- palette (docs/design.md) ----
GREEN = (0, 200, 83, 255)     # #00C853

# ---- geometry (design px; PNG is SS x larger) ----
LABEL_CANVAS = (360, 60)
LABEL_FONT = 40
LABEL_AT = (8, 30)            # left-middle anchor

GLYPH_CANVAS = (48, 64)
GLYPH_FONT = 50
GLYPH_BASELINE = 52           # y of the baseline inside the cell

TITLE_CANVAS = (620, 84)
TITLE_FONT = 54
TITLE_AT = (8, 42)
TITLE = ("title", "Redmi Watch 4 PoC")

# ---- character set for the glyph atlas ----
# Exactly what the clock screen can render: digits, separators and "UTC".
CHARS = list("0123456789.-:+UTC")

LABELS = [
    ("tarih", "Tarih"),
    ("saat", "Saat"),
    ("dilim", "Dilim"),
    ("unix", "Unix"),
]


def _font(size):
    return ImageFont.truetype(FONT_PATH, size)


def _save_verified(name, img, size):
    assert img.size == size, (name, img.size, size)
    assert img.getbbox() is not None, "blank image: %s" % name
    path = os.path.join(TXT_DIR, name)
    img.save(path)
    chk = Image.open(path)
    chk.load()
    assert chk.size == size, (name, chk.size, size)
    assert chk.getbbox() is not None, "blank on disk: %s" % name


def make_text_image(name, text, size, font_size, at, fill):
    n = (size[0] * SS, size[1] * SS)
    img = Image.new("RGBA", n, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((at[0] * SS, at[1] * SS), text, font=_font(font_size * SS),
           fill=fill, anchor="lm")
    img = img.resize(size, Image.LANCZOS)
    _save_verified(name + ".png", img, size)


def make_glyph(ch):
    n = (GLYPH_CANVAS[0] * SS, GLYPH_CANVAS[1] * SS)
    img = Image.new("RGBA", n, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = (GLYPH_CANVAS[0] * SS) / 2.0
    by = GLYPH_BASELINE * SS
    d.text((cx, by), ch, font=_font(GLYPH_FONT * SS), fill=GREEN, anchor="ms")
    img = img.resize(GLYPH_CANVAS, Image.LANCZOS)
    _save_verified("g_%x.png" % ord(ch), img, GLYPH_CANVAS)


def make_logo():
    """Launcher icon: nothing but a single green disc.

    The Redmi Watch 4 launcher reserves a fixed slot to the left of the app
    name, so the slot must hold *visible* content -- an empty/transparent icon
    leaves a gap that pushes the label to the middle of the row. Keep it as
    simple as possible: one green (brand) circle on a transparent ground."""
    size = (192, 192)
    n = size[0] * SS
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, n - 1, n - 1], fill=GREEN)
    img = img.resize(size, Image.LANCZOS)

    path = os.path.join(OUT_DIR, "logo.png")
    img.save(path)
    chk = Image.open(path)
    chk.load()
    assert chk.size == size
    assert chk.getbbox() is not None, "logo must not be empty"
    # centre pixel is opaque green, corners stay transparent
    assert chk.getpixel((size[0] // 2, size[1] // 2))[3] > 200
    assert chk.getpixel((0, 0))[3] < 20


def main():
    make_logo()
    make_text_image(TITLE[0], TITLE[1], TITLE_CANVAS, TITLE_FONT, TITLE_AT, GREEN)
    for stem, text in LABELS:
        make_text_image("lbl_" + stem, text, LABEL_CANVAS, LABEL_FONT, LABEL_AT, GREEN)
    for ch in CHARS:
        make_glyph(ch)
    print("generated green-disc logo + title + %d labels + %d glyphs"
          % (len(LABELS), len(CHARS)))


if __name__ == "__main__":
    main()
