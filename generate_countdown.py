#!/usr/bin/env python3
"""
Countdown Timer Video Frame Generator

Generates video frames for a 24-hour countdown timer (24:00:00 → 00:00:00)
in 20 different visual styles (10 digital + 10 circle/pie). Frames are saved
as PNG images and can be assembled into a video using ffmpeg.

Usage:
    python generate_countdown.py --style modern --fps 30
    python generate_countdown.py --style all --fps 1 --duration 60
    python generate_countdown.py --list-styles

Requirements:
    pip install Pillow

Assemble frames into video with ffmpeg:
    ffmpeg -framerate 30 -i output/modern/frame_%06d.png -c:v libx264 -pix_fmt yuv420p countdown_modern.mp4
"""

import argparse
import math
import os
import sys
from dataclasses import dataclass

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Style definitions
# ---------------------------------------------------------------------------

@dataclass
class StyleConfig:
    """Visual configuration for a countdown style."""
    name: str
    description: str
    width: int
    height: int
    bg_color: str | tuple
    text_color: str | tuple
    font_size: int
    font_name: str | None  # None = use default
    separator: str  # character between H:M:S
    show_labels: bool  # show "HOURS MINUTES SECONDS" labels
    label_color: str | tuple
    border: bool
    border_color: str | tuple
    border_width: int
    rounded_bg: bool  # draw rounded rectangles behind each digit group
    digit_bg_color: str | tuple | None
    glow: bool
    progress_bar: bool
    progress_color: str | tuple
    gradient_bg: bool
    gradient_colors: tuple | None  # (top_color, bottom_color)
    circle_progress: bool
    circle_color: str | tuple
    monospace: bool


STYLES: dict[str, StyleConfig] = {
    "modern": StyleConfig(
        name="modern",
        description="Clean modern look with dark background and cyan text",
        width=1920, height=1080,
        bg_color="#0a0a0a",
        text_color="#00e5ff",
        font_size=280,
        font_name=None,
        separator=":",
        show_labels=True,
        label_color="#555555",
        border=False, border_color="#000", border_width=0,
        rounded_bg=True,
        digit_bg_color="#1a1a2e",
        glow=False,
        progress_bar=True,
        progress_color="#00e5ff",
        gradient_bg=False, gradient_colors=None,
        circle_progress=False, circle_color="#000",
        monospace=True,
    ),
    "classic": StyleConfig(
        name="classic",
        description="Traditional white on black with serif-style digits",
        width=1920, height=1080,
        bg_color="#000000",
        text_color="#ffffff",
        font_size=300,
        font_name=None,
        separator=":",
        show_labels=False,
        label_color="#888",
        border=True, border_color="#ffffff", border_width=4,
        rounded_bg=False, digit_bg_color=None,
        glow=False,
        progress_bar=False, progress_color="#000",
        gradient_bg=False, gradient_colors=None,
        circle_progress=False, circle_color="#000",
        monospace=True,
    ),
    "neon": StyleConfig(
        name="neon",
        description="Neon glow effect on dark purple background",
        width=1920, height=1080,
        bg_color="#0d0221",
        text_color="#ff2afc",
        font_size=220,
        font_name=None,
        separator=" : ",
        show_labels=False,
        label_color="#555",
        border=False, border_color="#000", border_width=0,
        rounded_bg=False, digit_bg_color=None,
        glow=True,
        progress_bar=False, progress_color="#000",
        gradient_bg=False, gradient_colors=None,
        circle_progress=False, circle_color="#000",
        monospace=True,
    ),
    "minimal": StyleConfig(
        name="minimal",
        description="Minimal white background with thin gray text",
        width=1920, height=1080,
        bg_color="#ffffff",
        text_color="#333333",
        font_size=260,
        font_name=None,
        separator=":",
        show_labels=True,
        label_color="#aaaaaa",
        border=False, border_color="#000", border_width=0,
        rounded_bg=False, digit_bg_color=None,
        glow=False,
        progress_bar=False, progress_color="#000",
        gradient_bg=False, gradient_colors=None,
        circle_progress=False, circle_color="#000",
        monospace=True,
    ),
    "retro": StyleConfig(
        name="retro",
        description="Retro LED display with amber digits on dark background",
        width=1920, height=1080,
        bg_color="#1a1000",
        text_color="#ff8c00",
        font_size=300,
        font_name=None,
        separator=":",
        show_labels=False,
        label_color="#555",
        border=True, border_color="#332200", border_width=8,
        rounded_bg=True, digit_bg_color="#0f0a00",
        glow=True,
        progress_bar=False, progress_color="#000",
        gradient_bg=False, gradient_colors=None,
        circle_progress=False, circle_color="#000",
        monospace=True,
    ),
    "gradient": StyleConfig(
        name="gradient",
        description="Vibrant gradient background with white text",
        width=1920, height=1080,
        bg_color="#000000",
        text_color="#ffffff",
        font_size=280,
        font_name=None,
        separator=":",
        show_labels=True,
        label_color="#dddddd",
        border=False, border_color="#000", border_width=0,
        rounded_bg=False, digit_bg_color=None,
        glow=False,
        progress_bar=True, progress_color="#ffffff",
        gradient_bg=True, gradient_colors=("#667eea", "#764ba2"),
        circle_progress=False, circle_color="#000",
        monospace=True,
    ),
    "terminal": StyleConfig(
        name="terminal",
        description="Hacker-style green on black terminal look",
        width=1920, height=1080,
        bg_color="#0c0c0c",
        text_color="#00ff41",
        font_size=260,
        font_name=None,
        separator=":",
        show_labels=True,
        label_color="#006b1a",
        border=True, border_color="#00ff41", border_width=2,
        rounded_bg=False, digit_bg_color=None,
        glow=True,
        progress_bar=False, progress_color="#000",
        gradient_bg=False, gradient_colors=None,
        circle_progress=False, circle_color="#000",
        monospace=True,
    ),
    "cinematic": StyleConfig(
        name="cinematic",
        description="Cinematic widescreen with gold text on dark gradient",
        width=1920, height=1080,
        bg_color="#000000",
        text_color="#d4af37",
        font_size=220,
        font_name=None,
        separator=" : ",
        show_labels=False,
        label_color="#555",
        border=False, border_color="#000", border_width=0,
        rounded_bg=False, digit_bg_color=None,
        glow=True,
        progress_bar=False, progress_color="#000",
        gradient_bg=True, gradient_colors=("#1a1a1a", "#000000"),
        circle_progress=False, circle_color="#000",
        monospace=True,
    ),
    "sport": StyleConfig(
        name="sport",
        description="Sporty bold red countdown with progress bar",
        width=1920, height=1080,
        bg_color="#111111",
        text_color="#ff1744",
        font_size=300,
        font_name=None,
        separator=":",
        show_labels=True,
        label_color="#666666",
        border=False, border_color="#000", border_width=0,
        rounded_bg=True, digit_bg_color="#1c1c1c",
        glow=False,
        progress_bar=True, progress_color="#ff1744",
        gradient_bg=False, gradient_colors=None,
        circle_progress=False, circle_color="#000",
        monospace=True,
    ),
    "elegant": StyleConfig(
        name="elegant",
        description="Elegant cream background with dark brown text and circle progress",
        width=1920, height=1080,
        bg_color="#f5f0e8",
        text_color="#3e2723",
        font_size=180,
        font_name=None,
        separator="  :  ",
        show_labels=True,
        label_color="#8d6e63",
        border=False, border_color="#000", border_width=0,
        rounded_bg=False, digit_bg_color=None,
        glow=False,
        progress_bar=False, progress_color="#000",
        gradient_bg=False, gradient_colors=None,
        circle_progress=True, circle_color="#8d6e63",
        monospace=True,
    ),
}


# ---------------------------------------------------------------------------
# Circle (Time Timer) style definitions
# ---------------------------------------------------------------------------

@dataclass
class CircleTimerConfig:
    """Visual configuration for a circle/pie countdown style (Time Timer)."""
    name: str
    description: str
    width: int
    height: int
    bg_color: str | tuple
    text_color: str | tuple
    font_size: int
    wedge_color: str | tuple          # the pie wedge fill color
    wedge_alpha: int                   # wedge opacity (0-255)
    ring_color: str | tuple            # outer ring/border color
    ring_width: int                    # outer ring thickness
    tick_color: str | tuple            # tick mark color
    tick_major_len: int                # length of hour tick marks
    tick_minor_len: int                # length of minute tick marks
    show_ticks: bool                   # show tick marks around circle
    show_hour_numbers: bool            # show 0-24 numbers around circle
    hour_number_color: str | tuple
    center_dot: bool                   # dot at center
    center_dot_color: str | tuple
    glow: bool
    gradient_bg: bool
    gradient_colors: tuple | None


CIRCLE_STYLES: dict[str, CircleTimerConfig] = {
    "circle-modern": CircleTimerConfig(
        name="circle-modern",
        description="Modern dark circle timer with cyan wedge",
        width=1080, height=1080,
        bg_color="#0a0a0a",
        text_color="#00e5ff",
        font_size=90,
        wedge_color="#00e5ff",
        wedge_alpha=180,
        ring_color="#00e5ff",
        ring_width=6,
        tick_color="#00e5ff",
        tick_major_len=25,
        tick_minor_len=12,
        show_ticks=True,
        show_hour_numbers=False,
        hour_number_color="#555",
        center_dot=True,
        center_dot_color="#00e5ff",
        glow=False,
        gradient_bg=False,
        gradient_colors=None,
    ),
    "circle-classic": CircleTimerConfig(
        name="circle-classic",
        description="Classic Time Timer style with red wedge on white",
        width=1080, height=1080,
        bg_color="#ffffff",
        text_color="#333333",
        font_size=80,
        wedge_color="#e53935",
        wedge_alpha=200,
        ring_color="#333333",
        ring_width=5,
        tick_color="#333333",
        tick_major_len=30,
        tick_minor_len=15,
        show_ticks=True,
        show_hour_numbers=True,
        hour_number_color="#666666",
        center_dot=True,
        center_dot_color="#333333",
        glow=False,
        gradient_bg=False,
        gradient_colors=None,
    ),
    "circle-neon": CircleTimerConfig(
        name="circle-neon",
        description="Neon glowing circle timer on dark purple",
        width=1080, height=1080,
        bg_color="#0d0221",
        text_color="#ff2afc",
        font_size=90,
        wedge_color="#ff2afc",
        wedge_alpha=150,
        ring_color="#ff2afc",
        ring_width=4,
        tick_color="#ff2afc",
        tick_major_len=20,
        tick_minor_len=10,
        show_ticks=True,
        show_hour_numbers=False,
        hour_number_color="#555",
        center_dot=False,
        center_dot_color="#000",
        glow=True,
        gradient_bg=False,
        gradient_colors=None,
    ),
    "circle-minimal": CircleTimerConfig(
        name="circle-minimal",
        description="Minimal circle timer with thin ring on white",
        width=1080, height=1080,
        bg_color="#ffffff",
        text_color="#333333",
        font_size=80,
        wedge_color="#90caf9",
        wedge_alpha=140,
        ring_color="#cccccc",
        ring_width=2,
        tick_color="#cccccc",
        tick_major_len=15,
        tick_minor_len=0,
        show_ticks=True,
        show_hour_numbers=False,
        hour_number_color="#aaa",
        center_dot=False,
        center_dot_color="#000",
        glow=False,
        gradient_bg=False,
        gradient_colors=None,
    ),
    "circle-retro": CircleTimerConfig(
        name="circle-retro",
        description="Retro amber circle timer with LED look",
        width=1080, height=1080,
        bg_color="#1a1000",
        text_color="#ff8c00",
        font_size=90,
        wedge_color="#ff8c00",
        wedge_alpha=160,
        ring_color="#ff8c00",
        ring_width=5,
        tick_color="#ff8c00",
        tick_major_len=25,
        tick_minor_len=12,
        show_ticks=True,
        show_hour_numbers=False,
        hour_number_color="#555",
        center_dot=True,
        center_dot_color="#ff8c00",
        glow=True,
        gradient_bg=False,
        gradient_colors=None,
    ),
    "circle-gradient": CircleTimerConfig(
        name="circle-gradient",
        description="Circle timer on vibrant purple gradient",
        width=1080, height=1080,
        bg_color="#000000",
        text_color="#ffffff",
        font_size=80,
        wedge_color="#ffffff",
        wedge_alpha=120,
        ring_color="#ffffff",
        ring_width=4,
        tick_color="#ffffffcc",
        tick_major_len=20,
        tick_minor_len=10,
        show_ticks=True,
        show_hour_numbers=False,
        hour_number_color="#ddd",
        center_dot=True,
        center_dot_color="#ffffff",
        glow=False,
        gradient_bg=True,
        gradient_colors=("#667eea", "#764ba2"),
    ),
    "circle-terminal": CircleTimerConfig(
        name="circle-terminal",
        description="Terminal green circle timer on black",
        width=1080, height=1080,
        bg_color="#0c0c0c",
        text_color="#00ff41",
        font_size=80,
        wedge_color="#00ff41",
        wedge_alpha=130,
        ring_color="#00ff41",
        ring_width=3,
        tick_color="#00ff41",
        tick_major_len=20,
        tick_minor_len=10,
        show_ticks=True,
        show_hour_numbers=False,
        hour_number_color="#006b1a",
        center_dot=False,
        center_dot_color="#000",
        glow=True,
        gradient_bg=False,
        gradient_colors=None,
    ),
    "circle-cinematic": CircleTimerConfig(
        name="circle-cinematic",
        description="Cinematic gold circle timer on dark gradient",
        width=1080, height=1080,
        bg_color="#000000",
        text_color="#d4af37",
        font_size=90,
        wedge_color="#d4af37",
        wedge_alpha=160,
        ring_color="#d4af37",
        ring_width=5,
        tick_color="#d4af37",
        tick_major_len=25,
        tick_minor_len=12,
        show_ticks=True,
        show_hour_numbers=True,
        hour_number_color="#8a7a2a",
        center_dot=True,
        center_dot_color="#d4af37",
        glow=True,
        gradient_bg=True,
        gradient_colors=("#1a1a1a", "#000000"),
    ),
    "circle-sport": CircleTimerConfig(
        name="circle-sport",
        description="Sporty red circle timer with bold digits",
        width=1080, height=1080,
        bg_color="#111111",
        text_color="#ff1744",
        font_size=100,
        wedge_color="#ff1744",
        wedge_alpha=180,
        ring_color="#ff1744",
        ring_width=6,
        tick_color="#ff1744",
        tick_major_len=30,
        tick_minor_len=15,
        show_ticks=True,
        show_hour_numbers=False,
        hour_number_color="#666",
        center_dot=True,
        center_dot_color="#ff1744",
        glow=False,
        gradient_bg=False,
        gradient_colors=None,
    ),
    "circle-elegant": CircleTimerConfig(
        name="circle-elegant",
        description="Elegant cream circle timer with brown wedge",
        width=1080, height=1080,
        bg_color="#f5f0e8",
        text_color="#3e2723",
        font_size=80,
        wedge_color="#8d6e63",
        wedge_alpha=150,
        ring_color="#3e2723",
        ring_width=3,
        tick_color="#8d6e63",
        tick_major_len=25,
        tick_minor_len=12,
        show_ticks=True,
        show_hour_numbers=True,
        hour_number_color="#8d6e63",
        center_dot=True,
        center_dot_color="#3e2723",
        glow=False,
        gradient_bg=False,
        gradient_colors=None,
    ),
}


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def get_font_at_size(size: int) -> ImageFont.FreeTypeFont:
    """Get a monospace-friendly font at a given size."""
    font_candidates = [
        # macOS
        "/System/Library/Fonts/SFMono-Bold.otf",
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Courier.dfont",
        "/Library/Fonts/SF-Mono-Bold.otf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/UbuntuMono-Bold.ttf",
        # Windows
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/cour.ttf",
    ]

    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    try:
        return ImageFont.truetype("DejaVuSansMono-Bold", size)
    except Exception:
        return ImageFont.load_default()


def get_label_font_at_size(size: int) -> ImageFont.FreeTypeFont:
    """Get a sans-serif font for labels at a given size."""
    font_candidates = [
        "/System/Library/Fonts/SFMono-Regular.otf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]

    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    try:
        return ImageFont.truetype("DejaVuSans", size)
    except Exception:
        return ImageFont.load_default()


def get_font(style: StyleConfig) -> ImageFont.FreeTypeFont:
    """Get a monospace-friendly font at the style's size."""
    return get_font_at_size(style.font_size)


def get_label_font(style: StyleConfig) -> ImageFont.FreeTypeFont:
    """Get a smaller font for labels."""
    return get_label_font_at_size(style.font_size // 6)


def hex_to_rgb(color) -> tuple:
    """Convert hex color to RGB tuple, or pass through tuples."""
    if isinstance(color, tuple):
        return color
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def draw_gradient(draw: ImageDraw.Draw, width: int, height: int, top_color, bottom_color):
    """Draw a vertical gradient background."""
    top = hex_to_rgb(top_color)
    bottom = hex_to_rgb(bottom_color)
    for y in range(height):
        ratio = y / height
        r = int(top[0] + (bottom[0] - top[0]) * ratio)
        g = int(top[1] + (bottom[1] - top[1]) * ratio)
        b = int(top[2] + (bottom[2] - top[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_glow(draw: ImageDraw.Draw, text: str, x: int, y: int, font, color, layers=5):
    """Draw a glow effect behind text."""
    rgb = hex_to_rgb(color)
    for i in range(layers, 0, -1):
        alpha = int(40 / i)
        glow_color = (rgb[0], rgb[1], rgb[2], alpha)
        for dx in range(-i * 2, i * 2 + 1):
            for dy in range(-i * 2, i * 2 + 1):
                if dx * dx + dy * dy <= (i * 2) ** 2:
                    draw.text((x + dx, y + dy), text, font=font, fill=glow_color, anchor="mm")


def draw_rounded_rect(draw: ImageDraw.Draw, bbox, fill, radius=20):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = bbox
    draw.rounded_rectangle(bbox, radius=radius, fill=fill)


def draw_circle_progress(draw: ImageDraw.Draw, cx: int, cy: int, radius: int,
                          progress: float, color, width: int = 6):
    """Draw a circular progress arc."""
    rgb = hex_to_rgb(color)
    bbox = (cx - radius, cy - radius, cx + radius, cy + radius)
    # Background circle
    draw.arc(bbox, 0, 360, fill=(*rgb, 60), width=width)
    # Progress arc (clockwise from top)
    end_angle = -90 + (360 * progress)
    if progress > 0:
        draw.arc(bbox, -90, end_angle, fill=rgb, width=width * 2)


def format_time(total_seconds: int) -> tuple[str, str, str]:
    """Convert total seconds to HH, MM, SS strings."""
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}", f"{m:02d}", f"{s:02d}"


# ---------------------------------------------------------------------------
# Frame renderer
# ---------------------------------------------------------------------------

def render_frame(style: StyleConfig, total_seconds: int, total_duration: int) -> Image.Image:
    """Render a single countdown frame."""
    w, h = style.width, style.height
    hh, mm, ss = format_time(total_seconds)
    progress = 1.0 - (total_seconds / total_duration) if total_duration > 0 else 1.0
    time_text = f"{hh}{style.separator}{mm}{style.separator}{ss}"

    # Create image (RGBA for glow support)
    img = Image.new("RGBA", (w, h), hex_to_rgb(style.bg_color) + (255,))
    draw = ImageDraw.Draw(img)

    # Gradient background
    if style.gradient_bg and style.gradient_colors:
        draw_gradient(draw, w, h, style.gradient_colors[0], style.gradient_colors[1])

    # Border
    if style.border:
        bw = style.border_width
        bc = hex_to_rgb(style.border_color)
        draw.rectangle([bw // 2, bw // 2, w - bw // 2, h - bw // 2], outline=bc, width=bw)

    font = get_font(style)

    # Measure text
    bbox = draw.textbbox((0, 0), time_text, font=font, anchor="lt")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Center position
    cx = w // 2
    cy = h // 2

    # Rounded digit background
    if style.rounded_bg and style.digit_bg_color:
        pad_x, pad_y = 60, 40
        rect_bbox = (
            cx - text_w // 2 - pad_x,
            cy - text_h // 2 - pad_y,
            cx + text_w // 2 + pad_x,
            cy + text_h // 2 + pad_y,
        )
        draw_rounded_rect(draw, rect_bbox, hex_to_rgb(style.digit_bg_color), radius=30)

    # Circle progress
    if style.circle_progress:
        radius = min(w, h) // 2 - 60
        draw_circle_progress(draw, cx, cy, radius, progress, style.circle_color, width=8)

    # Glow effect
    if style.glow:
        draw_glow(draw, time_text, cx, cy, font, style.text_color, layers=4)

    # Main text
    draw.text((cx, cy), time_text, font=font, fill=hex_to_rgb(style.text_color), anchor="mm")

    # Labels
    if style.show_labels:
        label_font = get_label_font(style)
        label_y = cy + text_h // 2 + 30

        # Calculate positions based on digit groups
        # Measure each part to position labels under them
        hh_bbox = draw.textbbox((0, 0), hh, font=font, anchor="lt")
        sep_bbox = draw.textbbox((0, 0), style.separator, font=font, anchor="lt")
        mm_bbox = draw.textbbox((0, 0), mm, font=font, anchor="lt")

        hh_w = hh_bbox[2] - hh_bbox[0]
        sep_w = sep_bbox[2] - sep_bbox[0]
        mm_w = mm_bbox[2] - mm_bbox[0]

        start_x = cx - text_w // 2
        hh_cx = start_x + hh_w // 2
        mm_cx = start_x + hh_w + sep_w + mm_w // 2
        ss_cx = start_x + hh_w + sep_w + mm_w + sep_w + hh_w // 2

        lc = hex_to_rgb(style.label_color)
        draw.text((hh_cx, label_y), "HOURS", font=label_font, fill=lc, anchor="mt")
        draw.text((mm_cx, label_y), "MINUTES", font=label_font, fill=lc, anchor="mt")
        draw.text((ss_cx, label_y), "SECONDS", font=label_font, fill=lc, anchor="mt")

    # Progress bar
    if style.progress_bar:
        bar_h = 6
        bar_y = h - 40
        bar_margin = 80
        bar_w = w - bar_margin * 2
        pc = hex_to_rgb(style.progress_color)

        # Background
        draw.rectangle(
            [bar_margin, bar_y, bar_margin + bar_w, bar_y + bar_h],
            fill=(*pc, 40),
        )
        # Fill
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            draw.rectangle(
                [bar_margin, bar_y, bar_margin + fill_w, bar_y + bar_h],
                fill=pc,
            )

    # Convert to RGB for PNG output
    return img.convert("RGB")


# ---------------------------------------------------------------------------
# Circle (Time Timer) frame renderer
# ---------------------------------------------------------------------------

def render_circle_frame(style: CircleTimerConfig, total_seconds: int, total_duration: int) -> Image.Image:
    """Render a single circle/pie countdown frame (Time Timer style)."""
    w, h = style.width, style.height
    hh, mm, ss = format_time(total_seconds)
    remaining_ratio = total_seconds / total_duration if total_duration > 0 else 0.0
    time_text = f"{hh}:{mm}:{ss}"

    # Create base image
    img = Image.new("RGBA", (w, h), hex_to_rgb(style.bg_color) + (255,))
    draw = ImageDraw.Draw(img)

    # Gradient background
    if style.gradient_bg and style.gradient_colors:
        draw_gradient(draw, w, h, style.gradient_colors[0], style.gradient_colors[1])

    cx, cy = w // 2, h // 2
    margin = 80
    radius = min(w, h) // 2 - margin

    wedge_rgb = hex_to_rgb(style.wedge_color)
    ring_rgb = hex_to_rgb(style.ring_color)
    tick_rgb = hex_to_rgb(style.tick_color)

    # --- Draw the pie wedge on a separate layer for alpha ---
    if remaining_ratio > 0:
        wedge_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        wedge_draw = ImageDraw.Draw(wedge_layer)

        # Pie wedge: starts at 12 o'clock (-90°), sweeps clockwise
        sweep_angle = remaining_ratio * 360
        start_angle = -90
        end_angle = start_angle + sweep_angle

        wedge_bbox = (cx - radius, cy - radius, cx + radius, cy + radius)
        wedge_draw.pieslice(
            wedge_bbox,
            start=start_angle,
            end=end_angle,
            fill=(*wedge_rgb, style.wedge_alpha),
        )

        img = Image.alpha_composite(img, wedge_layer)
        draw = ImageDraw.Draw(img)

    # --- Outer ring ---
    ring_bbox = (cx - radius, cy - radius, cx + radius, cy + radius)
    draw.ellipse(ring_bbox, outline=ring_rgb, width=style.ring_width)

    # --- Tick marks ---
    if style.show_ticks:
        for i in range(60):
            angle_rad = math.radians(i * 6 - 90)  # 6° per minute, start at top
            is_major = (i % 5 == 0)  # every 5 minutes = major tick
            tick_len = style.tick_major_len if is_major else style.tick_minor_len
            if tick_len <= 0:
                continue
            tick_width = 3 if is_major else 1

            outer_x = cx + (radius - style.ring_width) * math.cos(angle_rad)
            outer_y = cy + (radius - style.ring_width) * math.sin(angle_rad)
            inner_x = cx + (radius - style.ring_width - tick_len) * math.cos(angle_rad)
            inner_y = cy + (radius - style.ring_width - tick_len) * math.sin(angle_rad)

            draw.line(
                [(inner_x, inner_y), (outer_x, outer_y)],
                fill=tick_rgb,
                width=tick_width,
            )

    # --- Hour numbers around the circle ---
    if style.show_hour_numbers:
        num_font = get_label_font_at_size(style.font_size // 3)
        num_rgb = hex_to_rgb(style.hour_number_color)
        # Show 12 labels: 0, 2, 4, ..., 22 (for 24h) mapped to clock positions
        for i in range(12):
            hour_val = i * 2
            angle_rad = math.radians(i * 30 - 90)  # 30° per step
            num_r = radius - style.ring_width - max(style.tick_major_len, style.tick_minor_len) - 30
            nx = cx + num_r * math.cos(angle_rad)
            ny = cy + num_r * math.sin(angle_rad)
            draw.text((nx, ny), str(hour_val), font=num_font, fill=num_rgb, anchor="mm")

    # --- Center dot ---
    if style.center_dot:
        dot_r = 8
        dot_rgb = hex_to_rgb(style.center_dot_color)
        draw.ellipse(
            (cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r),
            fill=dot_rgb,
        )

    # --- Digital time text in center ---
    font = get_font_at_size(style.font_size)

    if style.glow:
        draw_glow(draw, time_text, cx, cy, font, style.text_color, layers=3)

    draw.text((cx, cy), time_text, font=font, fill=hex_to_rgb(style.text_color), anchor="mm")

    return img.convert("RGB")


# ---------------------------------------------------------------------------
# Main generation logic
# ---------------------------------------------------------------------------

ALL_STYLES = {**STYLES, **CIRCLE_STYLES}


def generate_frames(
    style_name: str,
    output_dir: str = "output",
    fps: int = 30,
    duration: int = 86400,
    start_seconds: int = 86400,
):
    """Generate all frames for a countdown.

    Args:
        style_name: Name of the style to use.
        output_dir: Base output directory.
        fps: Frames per second.
        duration: Total countdown duration in seconds (default 24h = 86400).
        start_seconds: Starting time in seconds (default 24:00:00 = 86400).
    """
    if style_name not in ALL_STYLES:
        print(f"Unknown style: {style_name}")
        print(f"Available: {', '.join(ALL_STYLES.keys())}")
        sys.exit(1)

    style = ALL_STYLES[style_name]
    is_circle = isinstance(style, CircleTimerConfig)
    frame_dir = os.path.join(output_dir, style_name)
    os.makedirs(frame_dir, exist_ok=True)

    total_frames = duration * fps
    frame_num = 0

    print(f"Generating {style_name} countdown: {total_frames} frames at {fps} fps")
    print(f"  Resolution: {style.width}x{style.height}")
    print(f"  Output: {frame_dir}/")
    print(f"  Duration: {duration}s ({duration // 3600}h {(duration % 3600) // 60}m {duration % 60}s)")
    print()

    for second in range(start_seconds, start_seconds - duration - 1, -1):
        if second < 0:
            break

        for sub_frame in range(fps):
            # Only render unique time displays (1 per second for the timer)
            # But we still write fps copies so the video runs at correct speed
            if sub_frame == 0:
                if is_circle:
                    img = render_circle_frame(style, second, start_seconds)
                else:
                    img = render_frame(style, second, start_seconds)

            frame_path = os.path.join(frame_dir, f"frame_{frame_num:08d}.png")
            img.save(frame_path, "PNG", optimize=True)
            frame_num += 1

            if frame_num % (fps * 60) == 0:
                elapsed_minutes = frame_num // (fps * 60)
                remaining_minutes = (total_frames - frame_num) // (fps * 60)
                hh, mm, ss = format_time(second)
                print(
                    f"  Progress: {frame_num}/{total_frames} frames "
                    f"({frame_num * 100 // total_frames}%) "
                    f"- Timer at {hh}:{mm}:{ss} "
                    f"- ~{remaining_minutes} min of frames remaining"
                )

    print(f"\nDone! {frame_num} frames saved to {frame_dir}/")
    print(f"\nTo create video with ffmpeg:")
    print(f"  ffmpeg -framerate {fps} -i {frame_dir}/frame_%08d.png \\")
    print(f"    -c:v libx264 -pix_fmt yuv420p -crf 18 countdown_{style_name}.mp4")


def preview_style(style_name: str, output_dir: str = "output"):
    """Generate a single preview frame for a style."""
    if style_name not in ALL_STYLES:
        print(f"Unknown style: {style_name}")
        return

    style = ALL_STYLES[style_name]
    os.makedirs(output_dir, exist_ok=True)

    # Preview at 12:34:56 (representative time)
    preview_seconds = 12 * 3600 + 34 * 60 + 56
    if isinstance(style, CircleTimerConfig):
        img = render_circle_frame(style, preview_seconds, 86400)
    else:
        img = render_frame(style, preview_seconds, 86400)
    path = os.path.join(output_dir, f"preview_{style_name}.png")
    img.save(path, "PNG")
    print(f"Preview saved: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate countdown timer video frames in various styles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a 10-second preview clip in modern style at 30fps
  python generate_countdown.py --style modern --fps 30 --duration 10

  # Generate full 24h countdown (warning: lots of frames!)
  python generate_countdown.py --style neon --fps 30

  # Generate all styles preview frames
  python generate_countdown.py --preview-all

  # List available styles
  python generate_countdown.py --list-styles

  # Generate 1fps for smaller output (1 frame per second)
  python generate_countdown.py --style classic --fps 1 --duration 3600

Assemble into video:
  ffmpeg -framerate 30 -i output/modern/frame_%08d.png \\
    -c:v libx264 -pix_fmt yuv420p -crf 18 countdown_modern.mp4
        """,
    )
    parser.add_argument(
        "--style",
        choices=list(ALL_STYLES.keys()) + ["all"],
        default="modern",
        help="Visual style for the countdown (default: modern)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Frames per second (default: 30)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=86400,
        help="Countdown duration in seconds (default: 86400 = 24 hours)",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=86400,
        help="Start time in seconds (default: 86400 = 24:00:00)",
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Output directory (default: output/)",
    )
    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="List all available styles and exit",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Generate a single preview frame instead of full video",
    )
    parser.add_argument(
        "--preview-all",
        action="store_true",
        help="Generate preview frames for all styles",
    )
    args = parser.parse_args()

    if args.list_styles:
        print("Available countdown styles:")
        print("-" * 60)
        for name, style in ALL_STYLES.items():
            print(f"  {name:12s} - {style.description}")
        print(f"\nTotal: {len(ALL_STYLES)} styles")
        return

    if args.preview_all:
        print("Generating preview frames for all styles...")
        for name in ALL_STYLES:
            preview_style(name, args.output)
        print(f"\nAll previews saved to {args.output}/")
        return

    if args.preview:
        if args.style == "all":
            for name in ALL_STYLES:
                preview_style(name, args.output)
        else:
            preview_style(args.style, args.output)
        return

    if args.style == "all":
        for name in ALL_STYLES:
            generate_frames(name, args.output, args.fps, args.duration, args.start)
    else:
        generate_frames(args.style, args.output, args.fps, args.duration, args.start)


if __name__ == "__main__":
    main()
