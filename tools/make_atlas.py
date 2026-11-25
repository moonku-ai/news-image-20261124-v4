#!/usr/bin/env python3
"""Build-time glyph atlas for news-image-20261124-v4.

Rasterises Liberation Serif / DejaVu Sans with PIL (build machine only)
into atlas.bin in the ATL4 format read by main.py (stdlib only):

  magic "ATL4", u32 num_glyphs, u32 bitmap_bytes
  per glyph (22 bytes): u32 codepoint, u16 font_id, u16 size,
      u16 w, u16 h, i16 bearing_x, i16 bearing_y, u16 advance, u32 bmp_off
  then bitmap data: each glyph's w*h pixels nibble-packed (4-bit gray,
  high nibble first), ceil(w*h/2) bytes per glyph, in directory order.

Glyphs missing from a serif face fall back to the DejaVu Sans face of the
same weight at build time, so main.py never has to care.
"""
import os
import struct
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# (font_id, path, size)
COMBOS = [
    (0, SERIF_R, 12), (0, SERIF_R, 13), (0, SERIF_R, 15),
    (1, SERIF_B, 14), (1, SERIF_B, 18), (1, SERIF_B, 22),
    (1, SERIF_B, 28), (1, SERIF_B, 30), (1, SERIF_B, 66),
    (2, SERIF_I, 15),
    (3, SANS_R, 10), (3, SANS_R, 12),
    (4, SANS_B, 9), (4, SANS_B, 10), (4, SANS_B, 11),
    (4, SANS_B, 12), (4, SANS_B, 13), (4, SANS_B, 16),
]

EXTRA = "·—–‘’“”●○◐▲▼↑↓×±→✓★◆−…"
CHARS = [chr(c) for c in range(32, 127)] + list(EXTRA)


def has_glyph(font, ch):
    try:
        mask = font.getmask(ch)
    except Exception:
        return False
    return mask.getbbox() is not None


def main():
    out_path = os.path.join(ROOT, "atlas.bin")
    fonts = {}
    for fid, path, size in COMBOS:
        fonts[(fid, size)] = ImageFont.truetype(path, size)
    fallback = {}
    for size in sorted({s for _, _, s in COMBOS}):
        fallback[(False, size)] = ImageFont.truetype(SANS_R, size)
        fallback[(True, size)] = ImageFont.truetype(SANS_B, size)

    glyphs = []  # (codepoint, fid, size, bitmap_bytes, w, h, bx, by, adv)
    for fid, path, size in COMBOS:
        font = fonts[(fid, size)]
        bold = fid in (1, 4)
        fb = fallback[(bold, size)]
        for ch in CHARS:
            if ch == " ":
                adv = font.getlength(" ")
                glyphs.append((32, fid, size, b"", 0, 0, 0, 0,
                               int(round(adv))))
                continue
            use = font if has_glyph(font, ch) else fb
            try:
                left, top, right, bottom = use.getbbox(ch)
            except Exception:
                continue
            # getbbox is relative to the ascender line ("la" anchor):
            # convert the top bearing to be relative to the baseline.
            ascent = use.getmetrics()[0]
            w, h = right - left, bottom - top
            if w <= 0 or h <= 0:
                adv = use.getlength(ch)
                glyphs.append((ord(ch), fid, size, b"", 0, 0, 0, 0,
                               int(round(adv))))
                continue
            canvas = Image.new("L", (w + 4, h + 4), 0)
            ImageDraw.Draw(canvas).text((2 - left, 2 - top), ch, font=use,
                                        fill=255)
            img = canvas.crop((2, 2, 2 + w, 2 + h))
            adv = use.getlength(ch)
            glyphs.append((ord(ch), fid, size, img.tobytes(), w, h,
                           left, top - ascent, int(round(adv))))

    # nibble-pack all glyph bitmaps (4-bit gray, high nibble first)
    blobs = bytearray()
    recs = bytearray()
    for g in glyphs:
        cp, fid, size, bmp, w, h, bx, by, adv = g
        off = len(blobs)
        n = w * h
        packed = bytearray((n + 1) // 2)
        for i, a in enumerate(bmp):
            if i % 2 == 0:
                packed[i // 2] = (a >> 4) << 4
            else:
                packed[i // 2] |= a >> 4
        blobs += packed
        recs += struct.pack("<IHHHHhhHI", cp, fid, size, w, h,
                            bx, by, adv, off)
    hdr = struct.pack("<4sII", b"ATL4", len(glyphs), len(blobs))
    with open(out_path, "wb") as f:
        f.write(hdr)
        f.write(recs)
        f.write(bytes(blobs))
    print("glyphs:", len(glyphs), "bitmap bytes:", len(blobs),
          "total:", os.path.getsize(out_path))


if __name__ == "__main__":
    sys.exit(main())
