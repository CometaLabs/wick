# Wick · banner del README y vista previa social (1280×640)
#   python3 art/banner.py
#
# Tipografía: Roobert (licencia de escritorio de Cometa Labs). Solo se usa para
# rasterizar estas imágenes; la fuente no se incluye en el repo ni en la app.
import os, sys, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from post import with_glow, OUT, DOCS  # noqa: E402

W, H = 1280, 640
FONTS = os.path.expanduser("~/Library/Fonts")
PAPER = (239, 231, 218)
INK = (33, 28, 24)
MUTED = (120, 106, 92)
CLAY = (200, 121, 76)


def roobert(weight, size):
    return ImageFont.truetype(os.path.join(FONTS, f"Roobert-{weight}.otf"), size)


def paper(w, h):
    """Papel cálido con grano fino, para que no parezca un degradado de plantilla."""
    im = Image.new("RGB", (w, h), PAPER)
    rnd = random.Random(7)
    noise = Image.new("L", (w, h))
    noise.putdata([128 + int(rnd.gauss(0, 9)) for _ in range(w * h)])
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    grain = Image.merge("RGB", (noise, noise, noise))
    im = Image.blend(im, grain, 0.05)
    # viñeta muy suave
    v = Image.new("L", (w, h), 0)
    ImageDraw.Draw(v).ellipse((-w * 0.2, -h * 0.4, w * 1.2, h * 1.4), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new("RGB", (w, h), (214, 202, 186))
    return Image.composite(im, dark, v).convert("RGBA")


def contact_shadow(size, box):
    sh = Image.new("L", size, 0)
    ImageDraw.Draw(sh).ellipse(box, fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    layer = Image.new("RGBA", size, (90, 60, 40, 0))
    layer.putalpha(sh)
    return layer


def main():
    im = paper(W, H)

    # personaje a la derecha, apoyado en una sombra de contacto
    char = Image.open(os.path.join(OUT, "trabajando", "0001.png")).convert("RGBA")
    char = with_glow(char, 0.55).resize((620, 620), Image.LANCZOS)
    cx = W - 620 + 30
    im.alpha_composite(contact_shadow((W, H), (cx + 150, 520, cx + 500, 585)))
    im.alpha_composite(char, (cx, 0))

    d = ImageDraw.Draw(im)
    x = 92
    d.text((x, 92), "A MENU BAR APP FOR CLAUDE CODE", font=roobert("Medium", 17), fill=CLAY,
           spacing=0)
    d.text((x - 6, 120), "Wick", font=roobert("SemiBold", 168), fill=INK)
    d.text((x, 330), "Keeps your Mac awake", font=roobert("Medium", 42), fill=INK)
    d.text((x, 382), "while Claude Code works.", font=roobert("Medium", 42), fill=INK)
    d.text((x, 452), "Tu Mac despierto mientras trabaja Claude Code.", font=roobert("Regular", 22), fill=MUTED)

    # pie: datos sobrios, separados por una línea fina
    d.line((x, 526, x + 470, 526), fill=(205, 192, 176), width=1)
    d.text((x, 544), "Free and open source  ·  macOS 13+  ·  by Cometa Labs", font=roobert("Regular", 18),
           fill=MUTED)

    im.convert("RGB").save(os.path.join(DOCS, "banner.png"), optimize=True)
    print("banner ok")


if __name__ == "__main__":
    main()
