# Wick · posproceso de los frames de Blender
#
#   python3 art/post.py
#
# - Añade un halo cálido detrás de la llama (EEVEE no tiene bloom).
# - Exporta los frames para la app (Resources/mascot/<estado>/NN.png, 256 px).
# - Genera el icono de la app (Resources/AppIcon.icns) y las imágenes del README (docs/).

import os, subprocess, shutil, colorsys
from PIL import Image, ImageFilter, ImageDraw, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")
RES = os.path.join(ROOT, "Resources")
DOCS = os.path.join(ROOT, "docs")
STATES = ["trabajando", "esperando", "descansando"]
BG = (240, 232, 220, 255)


def flame_mask(im):
    """Píxeles de llama: naranja/amarillo saturado y muy luminoso."""
    small = im.convert("RGBA")
    px = small.load()
    mask = Image.new("L", small.size, 0)
    mp = mask.load()
    w, h = small.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128 or r < 200:
                continue
            hh, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if s > 0.62 and v > 0.9 and 0.0 <= hh <= 0.16:
                mp[x, y] = 255
    return mask


def with_glow(im, strength=0.6):
    w, h = im.size
    # la máscara se calcula a menor tamaño: más rápido y el halo es suave igualmente
    q = 4
    m = flame_mask(im.resize((w // q, h // q), Image.BILINEAR)).resize((w, h), Image.BILINEAR)
    if not m.getbbox():
        return im
    halo = m.filter(ImageFilter.GaussianBlur(w * 0.06))
    halo2 = m.filter(ImageFilter.GaussianBlur(w * 0.018))
    alpha = ImageChops.add(halo.point(lambda v: min(255, int(v * 2.2 * strength))),
                           halo2.point(lambda v: min(255, int(v * 1.2 * strength))))
    glow = Image.new("RGBA", (w, h), (255, 168, 72, 0))
    glow.putalpha(alpha)
    base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    base.alpha_composite(glow)
    base.alpha_composite(im)
    # un poco de brillo también por encima de la llama
    over = Image.new("RGBA", (w, h), (255, 200, 120, 0))
    over.putalpha(halo2.point(lambda v: int(v * 0.35 * strength)))
    base.alpha_composite(over)
    return base


def frames(state):
    d = os.path.join(OUT, state)
    return [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".png")]


def main():
    processed = {}
    for state in STATES:
        dst = os.path.join(RES, "mascot", state)
        shutil.rmtree(dst, ignore_errors=True)
        os.makedirs(dst)
        seq = []
        for i, path in enumerate(frames(state)):
            im = Image.open(path).convert("RGBA")
            im = with_glow(im, 0.55 if state == "esperando" else 0.75) if state != "descansando" else im
            seq.append(im)
            im.resize((256, 256), Image.LANCZOS).save(os.path.join(dst, f"{i:02d}.png"), optimize=True)
        processed[state] = seq
        print("frames", state, len(seq))

    os.makedirs(DOCS, exist_ok=True)

    # README: GIF animado de los tres estados en fila, sobre crema
    size = 300
    gif = []
    n = len(processed["trabajando"])
    for i in range(n):
        canvas = Image.new("RGBA", (size * 3, size), BG)
        for c, state in enumerate(STATES):
            canvas.alpha_composite(processed[state][i % len(processed[state])].resize((size, size), Image.LANCZOS),
                                   (c * size, 0))
        gif.append(canvas.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255))
    gif[0].save(os.path.join(DOCS, "estados.gif"), save_all=True, append_images=gif[1:],
                duration=1000 // 12, loop=0, optimize=True, disposal=2)
    # Estado trabajando solo, más grande, para la cabecera del README
    hero = []
    for im in processed["trabajando"]:
        canvas = Image.new("RGBA", (420, 420), BG)
        canvas.alpha_composite(im.resize((420, 420), Image.LANCZOS))
        hero.append(canvas.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255))
    hero[0].save(os.path.join(DOCS, "wick.gif"), save_all=True, append_images=hero[1:],
                 duration=1000 // 12, loop=0, optimize=True, disposal=2)

    make_icon(processed["trabajando"][0])


def make_icon(char):
    """Icono de macOS: cuadrado redondeado oscuro, halo cálido y la vela encendida (Wick)."""
    S = 1024
    pad = 100  # rejilla de iconos de macOS: el cuadrado ocupa 824 px
    box = S - 2 * pad
    radius = int(box * 0.225)

    base = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    # sombra suave del icono
    sh = Image.new("L", (S, S), 0)
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 14, S - pad, S - pad + 14), radius, fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shadow.putalpha(sh)
    base.alpha_composite(shadow)

    # fondo: degradado vertical tinta cálida
    tile = Image.new("RGBA", (box, box))
    top, bottom = (44, 36, 30), (18, 15, 13)
    td = ImageDraw.Draw(tile)
    for y in range(box):
        t = y / (box - 1)
        td.line([(0, y), (box, y)], fill=tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3)) + (255,))
    # luz cálida de la llama
    glow = Image.new("L", (box, box), 0)
    ImageDraw.Draw(glow).ellipse((box * 0.16, box * 0.02, box * 0.84, box * 0.62), fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(box * 0.12))
    warm = Image.new("RGBA", (box, box), (255, 150, 60, 0))
    warm.putalpha(glow)
    tile.alpha_composite(warm)

    c = char.resize((int(box * 1.08), int(box * 1.08)), Image.LANCZOS)
    tile.alpha_composite(c, ((box - c.width) // 2 + int(box * -0.02), int(box * 0.0)))

    # brillo fino en el borde superior
    rim = Image.new("RGBA", (box, box), (0, 0, 0, 0))
    ImageDraw.Draw(rim).rounded_rectangle((1, 1, box - 2, box - 2), radius, outline=(255, 235, 210, 40), width=3)
    tile.alpha_composite(rim)

    mask = Image.new("L", (box, box), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, box - 1, box - 1), radius, fill=255)
    base.paste(tile, (pad, pad), mask)

    os.makedirs(DOCS, exist_ok=True)
    base.save(os.path.join(DOCS, "icono.png"))

    iconset = os.path.join(HERE, "AppIcon.iconset")
    shutil.rmtree(iconset, ignore_errors=True)
    os.makedirs(iconset)
    for pt in (16, 32, 128, 256, 512):
        for scale in (1, 2):
            px = pt * scale
            name = f"icon_{pt}x{pt}{'@2x' if scale == 2 else ''}.png"
            base.resize((px, px), Image.LANCZOS).save(os.path.join(iconset, name))
    subprocess.run(["iconutil", "-c", "icns", iconset, "-o", os.path.join(RES, "AppIcon.icns")], check=True)
    shutil.rmtree(iconset)
    print("icono ok")


if __name__ == "__main__":
    main()
