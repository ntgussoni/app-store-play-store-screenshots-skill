#!/usr/bin/env python3
"""
App Store Screenshot Compositor

Composites a device screenshot onto a branded canvas with a marketing headline.

Usage:
  python3 compose.py \
    --screenshot path/to/framed_device.png \
    --output path/to/output.png \
    --size 1290x2796 \
    --bg-color "#181020" \
    [--bg-gradient "#2A1B33"] \
    --headline "Drift off in minutes" \
    [--subheadline "Calming stories for adults"] \
    [--headline-color "#c6bfff"] \
    [--font path/to/font.ttf] \
    [--device-scale 0.72]

  # Feature graphic (no device, just branding):
  python3 compose.py \
    --output feature_graphic.png \
    --size 1024x500 \
    --bg-color "#181020" \
    --bg-gradient "#2A1B33" \
    --headline "BedtimeFable" \
    --subheadline "Stories that help you sleep" \
    --headline-color "#c6bfff"
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow not installed. Run: pip3 install Pillow")
    sys.exit(1)


def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_gradient(width: int, height: int, color_top: str, color_bottom: str) -> Image.Image:
    top = hex_to_rgb(color_top)
    bottom = hex_to_rgb(color_bottom)
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for y in range(height):
        t = y / height
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(width):
            pixels[x, y] = (r, g, b)
    return img


def load_font(font_path: str | None, size: int) -> ImageFont.FreeTypeFont:
    if font_path:
        try:
            return ImageFont.truetype(font_path, size)
        except (IOError, OSError):
            print(f"  Warning: Could not load font '{font_path}', using system font.")

    system_fonts = [
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in system_fonts:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except (IOError, OSError):
                continue

    print("  Warning: No TTF font found, using PIL default. Pass --font for better results.")
    return ImageFont.load_default()


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] > max_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def compose(
    screenshot_path: str | None,
    output_path: str,
    canvas_size: tuple[int, int],
    bg_color: str,
    bg_gradient: str | None,
    headline: str,
    subheadline: str | None,
    headline_color: str,
    font_path: str | None,
    device_scale: float,
):
    width, height = canvas_size

    # Canvas
    if bg_gradient:
        canvas = create_gradient(width, height, bg_color, bg_gradient)
    else:
        canvas = Image.new("RGB", (width, height), hex_to_rgb(bg_color))

    draw = ImageDraw.Draw(canvas)

    # Typography sizes
    headline_size = max(48, int(height * 0.048))
    sub_size = max(32, int(height * 0.028))
    text_padding = int(width * 0.08)
    text_area_width = width - 2 * text_padding

    headline_font = load_font(font_path, headline_size)
    sub_font = load_font(font_path, sub_size)

    # Device screenshot
    device_y_start = int(height * 0.38)

    if screenshot_path and Path(screenshot_path).exists():
        device_img = Image.open(screenshot_path).convert("RGBA")
        device_w, device_h = device_img.size

        max_device_width = int(width * device_scale)
        max_device_height = int(height * 0.65)
        scale = min(max_device_width / device_w, max_device_height / device_h)
        new_w = int(device_w * scale)
        new_h = int(device_h * scale)
        device_img = device_img.resize((new_w, new_h), Image.LANCZOS)

        x = (width - new_w) // 2
        bottom_margin = int(height * 0.03)
        y = height - new_h - bottom_margin

        canvas.paste(device_img, (x, y), device_img)
        device_y_start = y

    # Headline text
    text_zone_height = device_y_start
    text_zone_center_y = text_zone_height // 2

    lines = wrap_text(headline, headline_font, text_area_width, draw)

    total_text_h = 0
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=headline_font)
        lh = bbox[3] - bbox[1]
        line_heights.append(lh)
        total_text_h += lh
    line_spacing = int(headline_size * 0.2)
    total_text_h += line_spacing * (len(lines) - 1)

    sub_lines = []
    if subheadline:
        sub_lines = wrap_text(subheadline, sub_font, text_area_width, draw)
        for sub_line in sub_lines:
            bbox = draw.textbbox((0, 0), sub_line, font=sub_font)
            total_text_h += (bbox[3] - bbox[1]) + int(sub_size * 0.3)
        total_text_h += int(headline_size * 0.5)

    y_cursor = text_zone_center_y - total_text_h // 2

    headline_rgb = hex_to_rgb(headline_color)
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=headline_font)
        line_w = bbox[2] - bbox[0]
        x = (width - line_w) // 2
        draw.text((x, y_cursor), line, font=headline_font, fill=headline_rgb)
        y_cursor += line_heights[i] + line_spacing

    if subheadline and sub_lines:
        y_cursor += int(headline_size * 0.5)
        sub_rgb = tuple(min(255, int(c * 0.75)) for c in headline_rgb)
        for sub_line in sub_lines:
            bbox = draw.textbbox((0, 0), sub_line, font=sub_font)
            line_w = bbox[2] - bbox[0]
            sub_line_h = bbox[3] - bbox[1]
            x = (width - line_w) // 2
            draw.text((x, y_cursor), sub_line, font=sub_font, fill=sub_rgb)
            y_cursor += sub_line_h + int(sub_size * 0.3)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, "PNG", optimize=True)
    print(f"  ✓ Saved: {output_path} ({width}×{height})")


def main():
    parser = argparse.ArgumentParser(description="Compose App Store screenshots")
    parser.add_argument("--screenshot", help="Path to framed device screenshot (omit for feature graphic)")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--size", required=True, help="Canvas size, e.g. 1290x2796")
    parser.add_argument("--bg-color", required=True, help="Background color hex, e.g. #181020")
    parser.add_argument("--bg-gradient", help="Gradient end color hex (optional)")
    parser.add_argument("--headline", required=True, help="Marketing headline text")
    parser.add_argument("--subheadline", help="Optional subheadline text")
    parser.add_argument("--headline-color", default="#FFFFFF", help="Headline text color hex")
    parser.add_argument("--font", help="Path to .ttf font file")
    parser.add_argument("--device-scale", type=float, default=0.72,
                        help="Device image width as fraction of canvas width (default: 0.72)")
    args = parser.parse_args()

    parts = args.size.lower().split("x")
    if len(parts) != 2:
        print(f"Invalid --size format: {args.size}. Expected WxH, e.g. 1290x2796")
        sys.exit(1)
    canvas_size = (int(parts[0]), int(parts[1]))

    compose(
        screenshot_path=args.screenshot,
        output_path=args.output,
        canvas_size=canvas_size,
        bg_color=args.bg_color,
        bg_gradient=args.bg_gradient,
        headline=args.headline,
        subheadline=args.subheadline,
        headline_color=args.headline_color,
        font_path=args.font,
        device_scale=args.device_scale,
    )


if __name__ == "__main__":
    main()
