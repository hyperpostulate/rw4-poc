#!/usr/bin/env python3
"""Reproducible PNG asset generator for gps-info.

Follows docs/design.md section 4. Run from anywhere:

    python3 scripts/gen_assets.py

Writes into src/common/:
  - logo.png          192x192, black rounded square + white location pin

Idempotent: running repeatedly produces the same output. After writing
the file it is re-opened and verified (dimensions + non-blank content).
"""

import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "src", "common")
os.makedirs(OUT_DIR, exist_ok=True)

SS = 4  # supersampling factor for crisp anti-aliasing

# Design palette (docs/design.md section 1)
WHITE = (255, 255, 255, 255)
ACCENT_RED = (255, 77, 77, 255)  # #FF4D4D
BLACK = (0, 0, 0, 255)
DARK_HOLE = (17, 17, 17, 255)


def make_logo():
    S = 192
    N = S * SS
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = N / 2.0, N / 2.0

    # 1. Black rounded square background
    margin = int(N * 0.02)
    radius = int(N * 0.22)
    d.rounded_rectangle(
        [margin, margin, N - margin, N - margin], 
        radius=radius, 
        fill=BLACK
    )

    # 2. Location Pin Geometry
    # Positioned slightly above center for visual balance (optical centering)
    head_center_y = cy - (N * 0.05)
    head_rad = N * 0.22
    tail_bottom_y = cy + (N * 0.22)
    
    # Outer Pin Shape (White)
    # Combine a circle head and a triangular tail
    d.ellipse(
        [cx - head_rad, head_center_y - head_rad, cx + head_rad, head_center_y + head_rad], 
        fill=WHITE
    )
    d.polygon(
        [
            (cx - head_rad, head_center_y), 
            (cx + head_rad, head_center_y), 
            (cx, tail_bottom_y)
        ], 
        fill=WHITE
    )

    # 3. Inner Detail (The "Hole")
    hole_rad = N * 0.07
    # Subtle accent ring around the hole
    d.ellipse(
        [cx - hole_rad - 2, head_center_y - hole_rad - 2, cx + hole_rad + 2, head_center_y + hole_rad + 2], 
        fill=ACCENT_RED
    )
    # Dark center
    d.ellipse(
        [cx - hole_rad, head_center_y - hole_rad, cx + hole_rad, head_center_y + hole_rad], 
        fill=DARK_HOLE
    )

    # Downscale for production size
    img = img.resize((S, S), Image.LANCZOS)
    
    # Flatten onto opaque black RGB to eliminate potential semi-transparent halos
    bg = Image.new("RGB", (S, S), (0, 0, 0))
    bg.paste(img, (0, 0), img)
    
    path = os.path.join(OUT_DIR, "logo.png")
    bg.save(path)
    return path, (S, S)


def verify(path, expected_size, expect_transparent):
    im = Image.open(path)
    assert im.size == expected_size, f"{path}: size {im.size} != {expected_size}"
    if expect_transparent:
        assert im.mode == "RGBA", f"{path}: expected RGBA, got {im.mode}"
        alpha = im.getchannel("A")
        hist = alpha.histogram()
        opaque = im.size[0] * im.size[1] - hist[0]
        assert opaque > 0, f"{path}: fully transparent (blank)"
        assert opaque < im.size[0] * im.size[1], f"{path}: no transparent area"
        nonblank = f"{opaque} opaque px"
    else:
        colors = im.convert("RGB").getcolors(maxcolors=1 << 24)
        assert colors and len(colors) > 1, f"{path}: blank single-color image"
        nonblank = f"{len(colors)} distinct colors"
    print(f"  ok  {os.path.relpath(path, ROOT)}  {im.size[0]}x{im.size[1]}  {im.mode}  ({nonblank})")


def main():
    print("generating assets ->", os.path.relpath(OUT_DIR, ROOT))
    logo_path, logo_size = make_logo()
    verify(logo_path, logo_size, expect_transparent=False)
    print("done.")


if __name__ == "__main__":
    main()
