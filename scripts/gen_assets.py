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
FONT_PATH = os.path.join(ROOT, "scripts", "assets", "ui-subset.ttf")

if os.path.isdir(TXT_DIR):
    for name in os.listdir(TXT_DIR):
        if name.endswith(".png"):
            os.remove(os.path.join(TXT_DIR, name))
os.makedirs(TXT_DIR, exist_ok=True)

SS = 4  # supersampling factor for crisp anti-aliasing

# ---- palette (docs/design.md) ----
GREEN = (0, 200, 83, 255)     # #00C853
BLACK = (0, 0, 0, 255)        # #000000
WHITE = (255, 255, 255, 255)  # #FFFFFF

# ---- geometry (assets are generated at their on-screen display size) ----
# These sizes match the CSS boxes in index.ux exactly; the runtime merely
# stretches each PNG to its box, so generating at 1x is both smaller and
# sharper than the old oversized (2-3x) assets. SS is an internal supersample
# factor used only while drawing, never the stored size.
LABEL_CANVAS = (150, 25)
LABEL_FONT = 17
LABEL_AT = (3, 12)            # left-middle anchor

GLYPH_CANVAS = (16, 22)
GLYPH_FONT = 17
GLYPH_BASELINE = 18           # y of the baseline inside the cell

# Launcher icon size in px. Deliberately 96x96, NOT the 192x192 the Vela docs
# recommend: on the Redmi Watch 4 the launcher reserves a slot to the left of
# the app name whose width follows the image's pixel size, so a 192x192 icon
# pushes the name to the middle of the row while 96x96 keeps it in place.
# Verified on device -- see README "On-device findings".
LOGO_SIZE = 96

TITLE_CANVAS = (310, 42)
TITLE_FONT = 27
TITLE_AT = (4, 21)
TITLE = ("title", "Redmi Watch 4 PoC")

# ---- character set for the glyph atlas ----
# Exactly what the clock screen can render: digits, the date separator "-",
# the UTC-offset separators ":"/"+" (and "-" for negative offsets) and "UTC".
# No "." glyph: the app never produces one.
CHARS = list("0123456789-:+UTC")

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
    img.save(path, optimize=True)
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
    """Launcher icon: the original watch motif.

    Full-bleed black disc, white watch body (with strap stubs) and a green
    screen. On the launcher's dark background the black disc is effectively
    invisible, so what reads is a white watch with a green screen -- the icon
    this app has always shipped."""
    size = (LOGO_SIZE, LOGO_SIZE)
    n = size[0] * SS
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    cx = cy = n / 2.0

    d.ellipse([0, 0, n - 1, n - 1], fill=BLACK)

    body_w = n * 0.44
    body_h = n * 0.56
    d.rounded_rectangle([cx - body_w / 2, cy - body_h / 2,
                         cx + body_w / 2, cy + body_h / 2],
                        radius=n * 0.14, fill=WHITE)

    strap_w = n * 0.18
    strap_h = n * 0.09
    d.rounded_rectangle([cx - strap_w / 2, n * 0.06,
                         cx + strap_w / 2, n * 0.06 + strap_h],
                        radius=strap_h / 2, fill=WHITE)
    d.rounded_rectangle([cx - strap_w / 2, n * 0.94 - strap_h,
                         cx + strap_w / 2, n * 0.94],
                        radius=strap_h / 2, fill=WHITE)

    screen_w = body_w * 0.70
    screen_h = body_h * 0.60
    d.rounded_rectangle([cx - screen_w / 2, cy - screen_h / 2,
                         cx + screen_w / 2, cy + screen_h / 2],
                        radius=n * 0.045, fill=GREEN)

    img = img.resize(size, Image.LANCZOS)
    path = os.path.join(OUT_DIR, "logo.png")
    img.save(path, optimize=True)
    chk = Image.open(path)
    chk.load()
    assert chk.size == size
    assert chk.getbbox() is not None, "logo must not be empty"
    assert chk.getpixel((size[0] // 2, size[1] // 2))[3] == 255, \
        "logo centre must be opaque"


def main():
    make_logo()
    make_text_image(TITLE[0], TITLE[1], TITLE_CANVAS, TITLE_FONT, TITLE_AT, GREEN)
    for stem, text in LABELS:
        make_text_image("lbl_" + stem, text, LABEL_CANVAS, LABEL_FONT, LABEL_AT, GREEN)
    for ch in CHARS:
        make_glyph(ch)
    print("generated watch-motif logo + title + %d labels + %d glyphs"
          % (len(LABELS), len(CHARS)))


if __name__ == "__main__":
    main()
