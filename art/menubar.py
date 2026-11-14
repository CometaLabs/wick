# Wick · tiras de la velita para la barra de menú (22 pt de alto, @2x = 44 px)
#   python3 art/menubar.py
# Recorta todos los frames al mismo rectángulo (la unión de los tres estados) para que
# la vela no cambie de tamaño entre estados, y guarda Resources/menubar/<estado>.webp.
import os
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DST = os.path.join(os.path.dirname(HERE), "Resources", "menubar")
STATES = ["trabajando", "esperando", "descansando"]
H = 44  # px (22 pt @2x)

frames = {s: [Image.open(os.path.join(OUT, s, f)).convert("RGBA")
              for f in sorted(os.listdir(os.path.join(OUT, s))) if f.endswith(".png")] for s in STATES}

box = None
for seq in frames.values():
    for im in seq:
        b = im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
        box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
pad = 6
box = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)
w = round((box[2] - box[0]) * H / (box[3] - box[1]))
os.makedirs(DST, exist_ok=True)
for s, seq in frames.items():
    strip = Image.new("RGBA", (w * len(seq), H))
    for i, im in enumerate(seq):
        small = im.crop(box).resize((w, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1, 60, 2))
        strip.paste(small, (i * w, 0))
    path = os.path.join(DST, f"{s}.webp")
    strip.save(path, quality=92, method=6)
    print(s, f"{w}x{H}", os.path.getsize(path) // 1024, "KB")
