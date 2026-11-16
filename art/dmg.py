# Wick · fondo de la ventana del .dmg (660×400 pt, con versión @2x)
#   python3 art/dmg.py  → art/dmg/background.tiff
import os, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dmg")
FONTS = os.path.expanduser("~/Library/Fonts")
PAPER, INK, MUTED, CLAY = (247, 243, 236), (33, 28, 24), (125, 110, 96), (200, 121, 76)


def font(weight, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS, f"Roobert-{weight}.otf"), size)
    except OSError:
        return ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", size)


def render(scale):
    W, H = 660 * scale, 400 * scale
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    # retícula de puntos, como la web
    for y in range(11 * scale, H, 22 * scale):
        for x in range(11 * scale, W, 22 * scale):
            d.ellipse((x - scale * .6, y - scale * .6, x + scale * .6, y + scale * .6), fill=(226, 218, 206))

    def center(text, y, f, fill):
        w = d.textlength(text, font=f)
        d.text(((W - w) / 2, y), text, font=f, fill=fill)

    center("Drag Wick into Applications", 42 * scale, font("SemiBold", 26 * scale), INK)
    center("Arrastra Wick a Aplicaciones", 78 * scale, font("Regular", 15 * scale), MUTED)

    # flecha a mano entre los dos iconos (iconos en x=170 y x=490, y=215)
    pts = []
    import math
    for i in range(41):
        t = i / 40
        x = (262 + (398 - 262) * t) * scale
        y = (212 - 18 * math.sin(math.pi * t)) * scale
        pts.append((x, y))
    d.line(pts, fill=CLAY, width=int(3.2 * scale), joint="curve")
    tip = pts[-1]
    d.line([(tip[0] - 13 * scale, tip[1] - 11 * scale), tip, (tip[0] - 15 * scale, tip[1] + 9 * scale)],
           fill=CLAY, width=int(3.2 * scale), joint="curve")

    center("Then open it: it lives in your menu bar, at the top right.", 330 * scale, font("Regular", 13 * scale), MUTED)
    center("Luego ábrela: vive en tu barra de menú, arriba a la derecha.", 350 * scale, font("Regular", 13 * scale), MUTED)
    return im


os.makedirs(OUT, exist_ok=True)
p1, p2 = os.path.join(OUT, "bg.png"), os.path.join(OUT, "bg@2x.png")
render(1).save(p1)
render(2).save(p2)
subprocess.run(["tiffutil", "-cathidpicheck", p1, p2, "-out", os.path.join(OUT, "background.tiff")], check=True)
print("ok", os.path.join(OUT, "background.tiff"))
