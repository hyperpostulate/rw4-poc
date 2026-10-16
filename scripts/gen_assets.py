#!/usr/bin/env python3
"""Reproducible PNG asset generator for rw4-compass.

Follows docs/design.md section 6. Run from anywhere:

    python3 scripts/gen_assets.py

Writes into src/common/:
  - dial.png          360x360, transparent bg, ticks + cardinal letters + red N accent
  - index-marker.png   40x40,  transparent bg, downward red triangle
  - logo.png          192x192, black rounded square + white compass needle w/ red tip

Idempotent: running repeatedly produces the same output. After writing each
file it is re-opened and verified (dimensions + non-blank content).
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "src", "common")
os.makedirs(OUT_DIR, exist_ok=True)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

SS = 4  # supersampling factor for crisp anti-aliasing

# Design palette (docs/design.md section 1)
WHITE = (255, 255, 255, 255)
GRAY = (189, 189, 189, 255)     # #BDBDBD
RED = (255, 77, 77, 255)        # #FF4D4D
BLACK = (0, 0, 0, 255)


def _load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _lerp(p, q, f):
    return (p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f)


# ---------------------------------------------------------------------------
# dial.png
# ---------------------------------------------------------------------------
def make_dial():
    S = 360
    N = S * SS
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = N / 2.0

    def pt(angle_deg, r):
        # 0 deg == top center; angles increase clockwise
        a = math.radians(angle_deg)
        return (cx + r * math.sin(a), cy - r * math.cos(a))

    r_outer = (S / 2.0 - 6) * SS  # 174 * SS

    # Ticks: major every 30 deg (2px/15px, white), minor every 15 deg (2px/8px, gray)
    for a in range(0, 360, 15):
        major = (a % 30 == 0)
        length = 15 if major else 8
        color = WHITE if major else GRAY
        d.line([pt(a, r_outer), pt(a, r_outer - length * SS)], fill=color, width=2 * SS)

    # Thin red north accent line, from near center outward toward 0 deg (top)
    d.line([pt(0, 80 * SS), pt(0, 110 * SS)], fill=RED, width=2 * SS)

    f_card = _load_font(FONT_BOLD, 24 * SS)
    f_inter = _load_font(FONT_REG, 16 * SS)

    def draw_text(txt, angle, r, font, fill):
        x, y = pt(angle, r)
        bbox = d.textbbox((0, 0), txt, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        d.text((x - w / 2.0 - bbox[0], y - h / 2.0 - bbox[1]), txt, font=font, fill=fill)

    for a, t in [(0, "K"), (90, "D"), (180, "G"), (270, "B")]:
        draw_text(t, a, 130 * SS, f_card, WHITE)
    for a, t in [(45, "KD"), (135, "GD"), (225, "GB"), (315, "KB")]:
        draw_text(t, a, 135 * SS, f_inter, GRAY)

    img = img.resize((S, S), Image.LANCZOS)
    path = os.path.join(OUT_DIR, "dial.png")
    img.save(path)
    return path, (S, S)


# ---------------------------------------------------------------------------
# index-marker.png
# ---------------------------------------------------------------------------
def make_marker():
    S = 40
    N = S * SS
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # narrow downward-pointing triangle
    apex = (N / 2.0, N * 0.95)
    left = (N * 0.20, N * 0.05)
    right = (N * 0.80, N * 0.05)
    d.polygon([apex, left, right], fill=RED)
    img = img.resize((S, S), Image.LANCZOS)
    path = os.path.join(OUT_DIR, "index-marker.png")
    img.save(path)
    return path, (S, S)


# ---------------------------------------------------------------------------
# logo.png
# ---------------------------------------------------------------------------
def make_logo():
    S = 192
    N = S * SS
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = N / 2.0

    # black rounded square
    margin = int(N * 0.02)
    radius = int(N * 0.22)
    d.rounded_rectangle([margin, margin, N - margin, N - margin], radius=radius, fill=BLACK)

    def pt(angle_deg, r):
        a = math.radians(angle_deg)
        return (cx + r * math.sin(a), cy - r * math.cos(a))

    outer = N * 0.41
    inner = N * 0.115

    # 4-point star needle, white
    star = []
    for i in range(4):
        star.append(pt(i * 90, outer))
        star.append(pt(i * 90 + 45, inner))
    d.polygon(star, fill=WHITE)

    # red tip on the north spike (top ~55% of the spike)
    tip_n = pt(0, outer)
    v_l = pt(315, inner)
    v_r = pt(45, inner)
    f = 0.45
    d.polygon([tip_n, _lerp(v_r, tip_n, f), _lerp(v_l, tip_n, f)], fill=RED)

    # small center dot
    cr = N * 0.030
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(17, 17, 17, 255))

    img = img.resize((S, S), Image.LANCZOS)
    # flatten onto opaque black so the icon has no soft transparent halo
    bg = Image.new("RGB", (S, S), (0, 0, 0))
    bg.paste(img, (0, 0), img)
    path = os.path.join(OUT_DIR, "logo.png")
    bg.save(path)
    return path, (S, S)


# ---------------------------------------------------------------------------
# verification
# ---------------------------------------------------------------------------
def verify(path, expected_size, expect_transparent):
    im = Image.open(path)
    assert im.size == expected_size, f"{path}: size {im.size} != {expected_size}"
    if expect_transparent:
        assert im.mode == "RGBA", f"{path}: expected RGBA, got {im.mode}"
        alpha = im.getchannel("A")
        hist = alpha.histogram()
        opaque = im.size[0] * im.size[1] - hist[0]  # hist[0] == fully transparent px
        assert opaque > 0, f"{path}: fully transparent (blank)"
        # content should not fill the entire canvas (transparent bg present)
        assert opaque < im.size[0] * im.size[1], f"{path}: no transparent area"
        nonblank = f"{opaque} opaque px"
    else:
        colors = im.convert("RGB").getcolors(maxcolors=1 << 24)
        assert colors and len(colors) > 1, f"{path}: blank single-color image"
        nonblank = f"{len(colors)} distinct colors"
    print(f"  ok  {os.path.relpath(path, ROOT)}  {im.size[0]}x{im.size[1]}  {im.mode}  ({nonblank})")


def main():
    print("generating assets ->", os.path.relpath(OUT_DIR, ROOT))
    dial_path, dial_size = make_dial()
    marker_path, marker_size = make_marker()
    logo_path, logo_size = make_logo()
    verify(dial_path, dial_size, expect_transparent=True)
    verify(marker_path, marker_size, expect_transparent=True)
    verify(logo_path, logo_size, expect_transparent=False)
    print("done.")


if __name__ == "__main__":
    main()
