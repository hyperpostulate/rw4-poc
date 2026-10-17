#!/usr/bin/env python3
"""Reproducible PNG asset generator for the Device Info quick app (time PoC).

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

Writes into src/common/:
  - logo.png       192x192 app icon
  - txt/lbl_*.png  static field labels (green)
  - txt/g_*.png    monospace glyph cells, g_<codepoint hex>.png (green)

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
AMBER = (255, 214, 0, 255)    # #FFD600
RED = (207, 102, 121, 255)    # #CF6679
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)

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
    S = 192
    N = S * SS
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    margin = int(N * 0.02)
    radius = int(N * 0.22)
    d.rounded_rectangle([margin, margin, N - margin, N - margin],
                        radius=radius, fill=BLACK)

    cx = N / 2.0
    body_w = N * 0.50
    body_h = N * 0.62
    d.rounded_rectangle([cx - body_w / 2, (N - body_h) / 2,
                         cx + body_w / 2, (N + body_h) / 2],
                        radius=N * 0.16, fill=WHITE)

    strap_w = N * 0.20
    strap_h = N * 0.10
    d.rounded_rectangle([cx - strap_w / 2, margin + N * 0.03,
                         cx + strap_w / 2, margin + N * 0.03 + strap_h],
                        radius=strap_h / 2, fill=WHITE)
    d.rounded_rectangle([cx - strap_w / 2, N - margin - N * 0.03 - strap_h,
                         cx + strap_w / 2, N - margin - N * 0.03],
                        radius=strap_h / 2, fill=WHITE)

    screen_w = body_w * 0.68
    screen_h = body_h * 0.62
    d.rounded_rectangle([cx - screen_w / 2, (N - screen_h) / 2,
                         cx + screen_w / 2, (N + screen_h) / 2],
                        radius=N * 0.05, fill=GREEN)

    out = img.resize((S, S), Image.LANCZOS)
    path = os.path.join(OUT_DIR, "logo.png")
    out.save(path)
    chk = Image.open(path)
    chk.load()
    assert chk.size == (S, S)
    assert chk.getbbox() is not None


def main():
    make_logo()
    make_text_image(TITLE[0], TITLE[1], TITLE_CANVAS, TITLE_FONT, TITLE_AT, GREEN)
    for stem, text in LABELS:
        make_text_image("lbl_" + stem, text, LABEL_CANVAS, LABEL_FONT, LABEL_AT, GREEN)
    for ch in CHARS:
        make_glyph(ch)
    print("generated title + %d labels + %d glyphs + logo" % (len(LABELS), len(CHARS)))


if __name__ == "__main__":
    main()
