#!/usr/bin/env python3
import os
import sys
import math
import argparse
from pathlib import Path


def load_env_file(dotenv_path: Path):
    if not dotenv_path.exists():
        return
    try:
        for line in dotenv_path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    except Exception as e:
        print(f"[warn] .env parse failed: {e}", file=sys.stderr)


def get_font(size: int, font_path: str | None):
    try:
        from PIL import ImageFont
    except Exception:
        print("[error] Python package 'Pillow' is not installed.\n"
              "Install with: pip install Pillow", file=sys.stderr)
        sys.exit(2)
    if font_path:
        try:
            return ImageFont.truetype(font_path, size=size)
        except Exception:
            print(f"[warn] Failed to load font at {font_path}, falling back to default.")
    return ImageFont.load_default()


def draw_overlay(img_path: Path, out_path: Path, title: str, subtitle: str | None,
                 position: str = "center", margin_ratio: float = 0.10,
                 band: bool = True, font: str | None = None, color: str = "#FFFFFF",
                 shadow: bool = True):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        print("[error] Python package 'Pillow' is not installed.\n"
              "Install with: pip install Pillow", file=sys.stderr)
        sys.exit(2)

    img = Image.open(img_path).convert("RGBA")
    W, H = img.size
    safe = (
        int(W * margin_ratio),
        int(H * margin_ratio),
        int(W * (1 - margin_ratio)),
        int(H * (1 - margin_ratio)),
    )  # (x0, y0, x1, y1)

    draw = ImageDraw.Draw(img, "RGBA")

    # Optional band to improve legibility
    if band:
        if position == "top":
            y0, y1 = safe[1], safe[1] + int((safe[3] - safe[1]) * 0.35)
        elif position == "bottom":
            y1 = safe[3]
            y0 = y1 - int((safe[3] - safe[1]) * 0.35)
        else:  # center
            center = (safe[1] + safe[3]) // 2
            band_h = int((safe[3] - safe[1]) * 0.4)
            y0, y1 = center - band_h // 2, center + band_h // 2
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        band_rect = Image.new("RGBA", (W, y1 - y0), (0, 0, 0, 120))
        overlay.paste(band_rect, (0, y0))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img, "RGBA")

    # Text layout within safe area
    x0, y0, x1, y1 = safe
    max_w = x1 - x0
    max_h = y1 - y0

    # Fit title size
    def text_bbox(font_obj, text):
        return draw.textbbox((0, 0), text, font=font_obj)

    # Try sizes descending
    size = max(24, int(min(W, H) * 0.09))
    font_title = get_font(size=size, font_path=font)

    # Wrap title by space
    import textwrap
    def fits(font_obj, lines):
        total_h = 0
        max_line_w = 0
        for line in lines:
            if not line:
                line = " "
            bbox = text_bbox(font_obj, line)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            total_h += h
            max_line_w = max(max_line_w, w)
        return max_line_w <= max_w and total_h <= int(max_h * 0.65)

    words = title.split()
    best_lines = [title]
    while size >= 20:
        font_title = get_font(size=size, font_path=font)
        # try wrapping to 1..3 lines
        success = False
        for width in range(10, 80, 2):  # rough wrap width
            lines = textwrap.wrap(title, width=width)
            if 1 <= len(lines) <= 3 and fits(font_title, lines):
                best_lines = lines
                success = True
                break
        if success:
            break
        size -= 2

    # Subtitle (optional)
    if subtitle:
        sub_size = max(16, int(size * 0.45))
        font_sub = get_font(size=sub_size, font_path=font)
    else:
        font_sub = None

    # Compute block height
    line_heights = []
    for line in best_lines:
        bbox = text_bbox(font_title, line or " ")
        line_heights.append(bbox[3] - bbox[1])
    title_h = sum(line_heights)
    gap = max(6, size // 6)
    sub_h = 0
    if subtitle and font_sub:
        bbox = text_bbox(font_sub, subtitle)
        sub_h = bbox[3] - bbox[1]
    block_h = title_h + (gap if subtitle else 0) + sub_h

    # Position block
    if position == "top":
        cur_y = y0 + (max_h - block_h) // 10
    elif position == "bottom":
        cur_y = y1 - block_h - (max_h // 10)
    else:
        cur_y = y0 + (max_h - block_h) // 2

    # Shadow
    def draw_line(text, y, font_obj):
        if shadow:
            draw.text((x0 + 2, y + 2), text, font=font_obj, fill=(0, 0, 0, 140))
        draw.text((x0, y), text, font=font_obj, fill=color)

    # Draw title
    for i, line in enumerate(best_lines):
        draw_line(line, cur_y, font_title)
        cur_y += line_heights[i]

    # Draw subtitle
    if subtitle and font_sub:
        cur_y += gap
        draw_line(subtitle, cur_y, font_sub)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path)
    print(f"[ok] Saved: {out_path}")


def main():
    ap = argparse.ArgumentParser(description="Overlay title text onto an eyecatch with safe margins")
    ap.add_argument("--in", dest="inp", required=True, help="Input image path")
    ap.add_argument("--out", required=True, help="Output image path")
    ap.add_argument("--title", required=True, help="Title text to overlay")
    ap.add_argument("--subtitle", default=None, help="Optional subtitle")
    ap.add_argument("--position", choices=["top", "center", "bottom"], default="center")
    ap.add_argument("--margin", type=float, default=0.10, help="Safe-area margin ratio per side (0.10=10%)")
    ap.add_argument("--font", default=None, help="Path to TTF/OTF font")
    ap.add_argument("--color", default="#FFFFFF", help="Title color (hex)")
    ap.add_argument("--no-band", action="store_true", help="Disable background band")
    ap.add_argument("--no-shadow", action="store_true", help="Disable text shadow")
    args = ap.parse_args()

    draw_overlay(
        img_path=Path(args.inp),
        out_path=Path(args.out),
        title=args.title,
        subtitle=args.subtitle,
        position=args.position,
        margin_ratio=args.margin,
        band=not args.no_band,
        font=args.font,
        color=args.color,
        shadow=not args.no_shadow,
    )


if __name__ == "__main__":
    main()

