"""Draw the site's icons and social (Open Graph) images into static/.

    python3 scripts/og.py

Needs Pillow and rsvg-convert (brew install librsvg). Icons come from static/favicon.svg. Each OG image is the hero in
small: celeste, the title in Archivo at the hero's width and weight, and the flag band along the bottom. Pages pick
theirs with `images:` in front matter; the rest get og.png (params.images in hugo.toml).
"""

import io
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
FONT = ROOT / "scripts/fonts/Archivo[wdth,wght].ttf"

CELESTE = "#5bb5e8"
FLAMBOYAN = "#e23b2e"
NAVY = "#14213d"
WHITE = "#ffffff"

W, H = 1200, 630
PAD = 80
BAND = 72

OG = {
    "og.png": ("Indie Hackers\nPuerto Rico", "El hogar de los emprendedores independientes.\nMastermind online cada viernes y comunidad en Slack."),
    "og-trabajo-remoto.png": ("Dónde trabajar\nremoto en PR", "Cafeterías y coworkings con buen Wi‑Fi y enchufes,\nevaluados por la comunidad."),
    "og-contribuye.png": ("Contribuye con\ntu agente", "Copia un prompt, pégalo en tu agente\ny él abre el pull request por ti."),
    "og-unete.png": ("Únete a la\ncomunidad", "Emprendedores independientes en Puerto Rico.\nEntra gratis al Slack y al Mastermind de los viernes."),
}


def font(size, weight, width=100):
    f = ImageFont.truetype(str(FONT), size)
    f.set_variation_by_axes([weight, width])
    return f


def svg_to_png(svg, size):
    png = subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size)], input=svg, capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGBA")


def flag_band(draw, top):
    stripe = BAND / 5
    for i in range(5):
        draw.rectangle([0, top + i * stripe, W, top + (i + 1) * stripe], fill=FLAMBOYAN if i % 2 == 0 else WHITE)
    tri = BAND * 0.75
    draw.polygon([(0, top), (tri, top + BAND / 2), (0, top + BAND)], fill=CELESTE)
    cx, cy, r = tri * 0.33, top + BAND / 2, BAND * 0.17
    star = []
    for k in range(10):
        rad = r if k % 2 == 0 else r * 0.4
        a = math.pi / 2 + k * math.pi / 5
        star.append((cx + rad * math.cos(a), cy - rad * math.sin(a)))
    draw.polygon(star, fill=WHITE)


def og(title, subtitle, logo):
    img = Image.new("RGB", (W, H), CELESTE)
    draw = ImageDraw.Draw(img)

    # Largest size where the widest title line fits, capped so two lines leave room for the subtitle
    size = 128
    while size > 40:
        f = font(size, 900, 125)
        if max(draw.textlength(line, font=f) for line in title.splitlines()) <= W - 2 * PAD:
            break
        size -= 2
    draw.multiline_text((PAD, PAD - 10), title, font=f, fill=NAVY, spacing=int(size * -0.02))

    sub = font(32, 600)
    sub_h = draw.multiline_textbbox((0, 0), subtitle, font=sub, spacing=10)[3]
    draw.multiline_text((PAD, H - BAND - 56 - sub_h), subtitle, font=sub, fill=NAVY, spacing=10)

    img.paste(logo, (W - PAD - logo.width, H - BAND - 48 - logo.height), logo)
    flag_band(draw, H - BAND)
    return img


def main():
    svg = (STATIC / "favicon.svg").read_bytes()
    square = svg.replace(b'rx="8"', b'rx="0"')  # iOS and Android round the corners themselves

    svg_to_png(svg, 512).save(STATIC / "images/logo.png")
    svg_to_png(square, 180).convert("RGB").save(STATIC / "apple-touch-icon.png")
    svg_to_png(square, 192).save(STATIC / "icon-192.png")
    svg_to_png(square, 512).save(STATIC / "icon-512.png")
    svg_to_png(svg, 48).save(STATIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    logo = svg_to_png(svg, 110)
    for name, (title, subtitle) in OG.items():
        og(title, subtitle, logo).save(STATIC / "images" / name, optimize=True)
        print("wrote", name)


if __name__ == "__main__":
    main()
