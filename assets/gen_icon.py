#!/usr/bin/env python3
"""Generate fhash app icon — a folder with a hash symbol."""
from PIL import Image, ImageDraw, ImageFont
import os

SIZES = [16, 32, 64, 128, 256, 512, 1024]
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = size
    pad = s * 0.08

    # Folder body — rounded rect
    folder_color = "#4A90D9"
    folder_dark = "#3570B0"
    tab_h = s * 0.12
    body_top = pad + tab_h
    body_bottom = s - pad
    body_left = pad
    body_right = s - pad
    r = s * 0.08

    # Folder tab
    tab_left = body_left
    tab_right = body_left + s * 0.35
    draw.rounded_rectangle(
        [tab_left, pad, tab_right, pad + tab_h + r],
        radius=r,
        fill=folder_dark
    )

    # Folder body
    draw.rounded_rectangle(
        [body_left, body_top, body_right, body_bottom],
        radius=r,
        fill=folder_color
    )

    # Hash symbol #
    hash_color = "#FFFFFF"
    cx, cy = s * 0.52, (body_top + body_bottom) / 2 + s * 0.02
    bar_w = s * 0.06
    bar_len = s * 0.28
    gap = s * 0.10

    # Vertical bars
    for dx in [-gap, gap]:
        x = cx + dx
        draw.rounded_rectangle(
            [x - bar_w / 2, cy - bar_len / 2, x + bar_w / 2, cy + bar_len / 2],
            radius=bar_w * 0.3,
            fill=hash_color
        )

    # Horizontal bars
    for dy in [-gap * 0.65, gap * 0.65]:
        y = cy + dy
        draw.rounded_rectangle(
            [cx - bar_len / 2, y - bar_w / 2, cx + bar_len / 2, y + bar_w / 2],
            radius=bar_w * 0.3,
            fill=hash_color
        )

    return img


def main():
    # Generate all sizes
    images = []
    for sz in SIZES:
        img = draw_icon(sz)
        png_path = os.path.join(OUT_DIR, f"icon_{sz}.png")
        img.save(png_path)
        images.append(img)

    # macOS .icns (use iconutil on macOS)
    iconset_dir = os.path.join(OUT_DIR, "icon.iconset")
    os.makedirs(iconset_dir, exist_ok=True)

    icns_map = {
        16: "icon_16x16.png",
        32: "icon_16x16@2x.png",
        32: "icon_32x32.png",
        64: "icon_32x32@2x.png",
        128: "icon_128x128.png",
        256: "icon_128x128@2x.png",
        256: "icon_256x256.png",
        512: "icon_256x256@2x.png",
        512: "icon_512x512.png",
        1024: "icon_512x512@2x.png",
    }

    # Write iconset files (dedup by filename)
    written = set()
    for sz in SIZES:
        img = draw_icon(sz)
        for mapped_sz, fname in icns_map.items():
            if mapped_sz == sz and fname not in written:
                img.save(os.path.join(iconset_dir, fname))
                written.add(fname)

    # Use iconutil to create .icns
    icns_path = os.path.join(OUT_DIR, "icon.icns")
    ret = os.system(f"iconutil -c icns '{iconset_dir}' -o '{icns_path}'")
    if ret == 0:
        print(f"✅ {icns_path}")
    else:
        print("⚠️  iconutil failed, using PNG fallback")
        # Fallback: just use the 512px PNG
        draw_icon(512).save(os.path.join(OUT_DIR, "icon.png"))

    # Windows .ico
    ico_path = os.path.join(OUT_DIR, "icon.ico")
    ico_sizes = [16, 32, 48, 64, 128, 256]
    ico_images = [draw_icon(s) for s in ico_sizes]
    ico_images[0].save(ico_path, format="ICO", sizes=[(s, s) for s in ico_sizes])
    print(f"✅ {ico_path}")

    print("Done.")


if __name__ == "__main__":
    main()
