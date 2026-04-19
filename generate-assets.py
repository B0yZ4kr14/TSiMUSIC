#!/usr/bin/env python3
"""Generate TSi MUSIC assets for the Music Assistant rebrand patch."""

import os
from pathlib import Path

HOME = Path.home()
ASSETS_DIR = HOME / "scripts/patch-tsimusic/assets"

def write_file(path: Path, content: str):
    path.write_text(content, encoding="utf-8")
    print(f"Generated: {path}")

# ── SVG LOGO (Light) ──
LOGO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 120" width="400" height="120">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#7c3aed;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#a78bfa;stop-opacity:1" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <!-- Sound wave decoration -->
  <path d="M10 60 Q30 30 50 60 T90 60 T130 60 T170 60" fill="none" stroke="url(#grad)" stroke-width="3" stroke-linecap="round" opacity="0.6"/>
  <!-- TSi text -->
  <text x="200" y="58" font-family="system-ui, -apple-system, sans-serif" font-size="52" font-weight="900" fill="#1a1a1e" text-anchor="middle" letter-spacing="-2">TSi</text>
  <!-- MUSIC text -->
  <text x="200" y="92" font-family="system-ui, -apple-system, sans-serif" font-size="22" font-weight="500" fill="#7c3aed" text-anchor="middle" letter-spacing="8">MUSIC</text>
</svg>'''

# ── SVG LOGO (Dark) ──
LOGO_DARK_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 120" width="400" height="120">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#7c3aed;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#c4b5fd;stop-opacity:1" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <!-- Sound wave decoration -->
  <path d="M10 60 Q30 30 50 60 T90 60 T130 60 T170 60" fill="none" stroke="url(#grad)" stroke-width="3" stroke-linecap="round" opacity="0.8"/>
  <!-- TSi text -->
  <text x="200" y="58" font-family="system-ui, -apple-system, sans-serif" font-size="52" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="-2">TSi</text>
  <!-- MUSIC text -->
  <text x="200" y="92" font-family="system-ui, -apple-system, sans-serif" font-size="22" font-weight="500" fill="#a78bfa" text-anchor="middle" letter-spacing="8">MUSIC</text>
</svg>'''

# ── SVG ICON ──
ICON_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">
  <defs>
    <linearGradient id="iconGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#7c3aed"/>
      <stop offset="100%" style="stop-color:#4c1d95"/>
    </linearGradient>
    <filter id="iconShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#7c3aed" flood-opacity="0.4"/>
    </filter>
  </defs>
  <!-- Background circle -->
  <circle cx="128" cy="128" r="110" fill="url(#iconGrad)"/>
  <!-- Sound wave bars -->
  <rect x="70" y="100" width="14" rx="7" height="56" fill="white" opacity="0.9"/>
  <rect x="96" y="78" width="14" rx="7" height="100" fill="white" opacity="0.9"/>
  <rect x="122" y="60" width="14" rx="7" height="136" fill="white" opacity="1"/>
  <rect x="148" y="78" width="14" rx="7" height="100" fill="white" opacity="0.9"/>
  <rect x="174" y="100" width="14" rx="7" height="56" fill="white" opacity="0.9"/>
</svg>'''

def generate_placeholders():
    """Generate PNG placeholder images using Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow not available, skipping PNG placeholders")
        return

    # Fallback / cover placeholders
    for name, bg_color, text_color in [
        ("fallback.png", (26, 26, 30), (124, 58, 237)),
        ("cover_dark.png", (15, 15, 17), (167, 139, 250)),
        ("cover_light.png", (245, 245, 245), (124, 58, 237)),
    ]:
        img = Image.new("RGB", (512, 512), bg_color)
        draw = ImageDraw.Draw(img)

        # Draw a subtle gradient circle in center
        cx, cy = 256, 200
        for r in range(180, 0, -2):
            alpha = int(20 * (r / 180))
            color = (bg_color[0] + alpha, bg_color[1] + alpha, bg_color[2] + alpha)
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)

        # Try to load a font, fallback to default
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            font_large = ImageFont.load_default()
            font_small = font_large

        # Draw TSi
        bbox = draw.textbbox((0, 0), "TSi", font=font_large)
        tw = bbox[2] - bbox[0]
        draw.text(((512 - tw) // 2, 160), "TSi", fill=text_color, font=font_large)

        # Draw MUSIC
        bbox2 = draw.textbbox((0, 0), "MUSIC", font=font_small)
        tw2 = bbox2[2] - bbox2[0]
        draw.text(((512 - tw2) // 2, 250), "MUSIC", fill=text_color, font=font_small)

        # Draw sound wave bars at bottom
        bar_color = (*text_color, 180) if len(text_color) == 3 else text_color
        bars = [(100, 40), (130, 70), (160, 100), (190, 70), (220, 40)]
        base_y = 380
        for bx, bh in bars:
            draw.rounded_rectangle([bx, base_y - bh, bx + 18, base_y], radius=9, fill=text_color + (60,) if isinstance(text_color, tuple) and len(text_color)==3 else text_color)

        out_path = ASSETS_DIR / name
        img.save(out_path, "PNG")
        print(f"Generated: {out_path}")

if __name__ == "__main__":
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    write_file(ASSETS_DIR / "logo.svg", LOGO_SVG)
    write_file(ASSETS_DIR / "logo-dark.svg", LOGO_DARK_SVG)
    write_file(ASSETS_DIR / "icon.svg", ICON_SVG)
    generate_placeholders()
    print("\nAll assets generated successfully!")
