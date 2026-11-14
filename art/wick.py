# Wick · mascota de plastilina (Blender en modo script)
#
# Una vela de cera con cara, sobre un platito de barro. Tres estados en bucle:
#   trabajando  · llama viva, saltitos, parpadeo
#   esperando   · llama pequeña, se balancea y mira a un lado
#   descansando · llama apagada, ojos cerrados, respira, brasa en la mecha
#
# Uso:
#   /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
#       --python art/wick.py -- art/out [estado] [frames] [res]
#
# Genera <out>/<estado>/0001.png … (fondo transparente). Después: python3 art/post.py

import bpy, bmesh, sys, os, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else os.path.join(os.path.dirname(__file__), "out")
ONLY = argv[1] if len(argv) > 1 and argv[1] != "all" else None
FRAMES = int(argv[2]) if len(argv) > 2 else 24
RES = int(argv[3]) if len(argv) > 3 else 768

TAU = math.tau


def srgb(h, a=1.0):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return (*[x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c], a)


# Paleta: cera crema, barro cálido, tinta (familia HQ)
WAX = "#f6dcb2"
WAX_DRIP = "#f8e2bd"
CLAY = "#c8794c"
CLAY_DARK = "#a65f3a"
INK = "#1d1916"
CHEEK = "#f0937f"
FLAME_A = "#ff3d00"
FLAME_B = "#ff9500"
FLAME_C = "#fff1b8"


# ---------------------------------------------------------------- escena
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = RES
    sc.render.resolution_y = RES
    sc.render.film_transparent = True
    sc.render.filter_size = 1.2
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Base Contrast"
    except Exception:
        pass
    for attr, val in (("taa_render_samples", 64), ("use_shadows", True), ("use_raytracing", True),
                      ("shadow_ray_count", 2), ("shadow_step_count", 10), ("use_fast_gi", True)):
        try:
            setattr(sc.eevee, attr, val)
        except Exception:
            pass
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = srgb("#e9e1d6")
    bg.inputs[1].default_value = 0.55
    return sc


def mat_clay(name, color, rough=0.55, sss=0.0, bump=0.06):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = srgb(color)
    p.inputs["Roughness"].default_value = rough
    if sss:
        try:
            p.inputs["Subsurface Weight"].default_value = sss
            p.inputs["Subsurface Radius"].default_value = (0.9, 0.5, 0.3)
            p.inputs["Subsurface Scale"].default_value = 0.12
        except Exception:
            pass
    if bump:
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 38.0
        noise.inputs["Detail"].default_value = 6.0
        b = nt.nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = bump
        b.inputs["Distance"].default_value = 0.02
        nt.links.new(noise.outputs["Fac"], b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def mat_gloss(name, color):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = srgb(color)
    p.inputs["Roughness"].default_value = 0.18
    try:
        p.inputs["Coat Weight"].default_value = 0.6
    except Exception:
        pass
    return m


def mat_emit(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = srgb(color)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def mat_flame(name, strength):
    """Emisión con degradado vertical: naranja abajo, amarillo y casi blanco arriba."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position = 0.0
    els[0].color = srgb("#ffc93a")
    els[1].position = 1.0
    els[1].color = srgb(FLAME_A)
    mid = els.new(0.5)
    mid.color = srgb(FLAME_B)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True


def link(obj, parent=None):
    if parent is not None:
        obj.parent = parent
    return obj


def sphere(name, loc, scale, mat, parent=None, segs=48):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=segs // 2, radius=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    smooth(o)
    o.data.materials.append(mat)
    return link(o, parent)


def cylinder(name, loc, radius, depth, mat, bevel=0.0, parent=None, verts=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 10
        mod.limit_method = "ANGLE"
    smooth(o)
    o.data.materials.append(mat)
    return link(o, parent)


def teardrop(name, loc, size, mat, parent=None):
    """Gota de llama: esfera estirada hacia arriba y afilada en la punta."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=32, radius=1.0)
    for v in bm.verts:
        z = v.co.z
        if z > 0:
            f = (1 - z) ** 0.9
            v.co.x *= f
            v.co.y *= f
            v.co.z = z * 1.9
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.scale = (size, size * 0.8, size)
    smooth(o)
    o.data.materials.append(mat)
    return link(o, parent)


def arc(name, loc, width, depth, sag, mat, parent=None, thick=0.014):
    """Arco (boca o ojo cerrado) en el plano XZ, mirando a cámara (-Y)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = thick
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(2)
    pts = [(-width, 0, 0), (0, depth, -sag), (width, 0, 0)]
    for bp, co in zip(sp.bezier_points, pts):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.data.materials.append(mat)
    return link(o, parent)


# ---------------------------------------------------------------- personaje
def build():
    m_wax = mat_clay("wax", WAX, rough=0.42, sss=0.35, bump=0.035)
    m_drip = mat_clay("drip", WAX_DRIP, rough=0.3, sss=0.4, bump=0.02)
    m_clay = mat_clay("clay", CLAY, rough=0.62, bump=0.08)
    m_clay_d = mat_clay("clay_d", CLAY_DARK, rough=0.62, bump=0.08)
    m_ink = mat_gloss("ink", INK)
    m_cheek = mat_clay("cheek", CHEEK, rough=0.6, bump=0.02)
    m_hi = mat_emit("hi", "#ffffff", 2.5)
    m_flame = mat_flame("flame", 1.25)
    m_core = mat_emit("core", "#fff0a8", 2.2)
    m_ember = mat_emit("ember", "#ff5a1a", 6.0)

    # Platito de barro (no se mueve)
    cylinder("plato", (0, 0, 0.07), 0.82, 0.14, m_clay, bevel=0.06)
    cylinder("plato_borde", (0, 0, 0.16), 0.62, 0.05, m_clay_d, bevel=0.02)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.045, location=(0.88, 0, 0.08),
                                     rotation=(math.pi / 2, 0, 0))
    asa = bpy.context.object
    asa.name = "asa"
    smooth(asa)
    asa.data.materials.append(m_clay)

    # Rig: el pivote está en la base de la vela para aplastar y balancear
    bpy.ops.object.empty_add(location=(0, 0, 0.18))
    rig = bpy.context.object
    rig.name = "rig"

    H = 1.18
    R = 0.5
    body = cylinder("cuerpo", (0, 0, 0.18 + H / 2), R, H, m_wax, bevel=0.16, parent=None)
    body.parent = rig
    body.location = (0, 0, H / 2)
    top = H

    # Goterones de cera en el borde superior
    for ang, length in ((-0.62, 0.22), (0.55, 0.3), (1.6, 0.18), (3.3, 0.24), (4.7, 0.2)):
        a = ang - math.pi / 2
        x, y = math.cos(a) * (R - 0.005), math.sin(a) * (R - 0.005)
        d = sphere(f"gota{ang}", (0, 0, 0), (0.075, 0.045, length), m_drip, parent=rig, segs=32)
        d.location = (x, y, top - length * 0.55)
        d.rotation_euler = (0, 0, a)
        sphere(f"gotapunta{ang}", (0, 0, 0), (0.072, 0.05, 0.072), m_drip, parent=rig,
               segs=32).location = (x * 1.01, y * 1.01, top - length * 1.05)
    # charco de cera arriba
    pool = cylinder("charco", (0, 0, 0), R - 0.035, 0.05, m_drip, bevel=0.02, parent=rig)
    pool.location = (0, 0, top - 0.005)

    # Wick
    wick = cylinder("mecha", (0, 0, 0), 0.028, 0.16, m_ink, parent=rig, verts=24)
    wick.location = (0, 0, top + 0.08)
    wick.rotation_euler = (0, 0.12, 0)
    ember = sphere("brasa", (0, 0, 0), (0.03, 0.03, 0.03), m_ember, parent=rig, segs=24)
    ember.location = (0.012, 0, top + 0.16)

    # Llama (pivote en su base)
    bpy.ops.object.empty_add(location=(0, 0, 0))
    fl = bpy.context.object
    fl.name = "llama_pivote"
    fl.parent = rig
    fl.location = (0, 0, top + 0.17)
    flame = teardrop("llama", (0, 0, 0.13), 0.17, m_flame, parent=fl)
    core = teardrop("nucleo", (0, -0.06, 0.08), 0.095, m_core, parent=fl)
    bpy.ops.object.light_add(type="POINT", location=(0, 0, 0.25))
    lamp = bpy.context.object
    lamp.name = "luz_llama"
    lamp.data.color = srgb(FLAME_B)[:3]
    lamp.data.energy = 60
    lamp.data.shadow_soft_size = 0.15
    lamp.parent = fl

    # Cara
    fz = 0.62
    face = {}
    for side in (-1, 1):
        x = 0.17 * side
        y = -math.sqrt(R * R - x * x) + 0.012
        eye = sphere(f"ojo{side}", (0, 0, 0), (0.068, 0.04, 0.088), m_ink, parent=rig, segs=32)
        eye.location = (x, y, fz)
        eye.rotation_euler = (0, 0, math.asin(x / R))
        hi = sphere(f"brillo{side}", (0, 0, 0), (0.022, 0.012, 0.022), m_hi, parent=eye, segs=16)
        hi.location = (-0.35, -0.9, 0.38)  # coordenadas locales del ojo (escaladas)
        closed = arc(f"ojo_cerrado{side}", (x, y - 0.03, fz - 0.01), 0.06, -0.01, -0.04, m_ink,
                     parent=rig, thick=0.016)
        cx = 0.3 * side
        cy = -math.sqrt(R * R - cx * cx) + 0.02
        ck = sphere(f"moflete{side}", (0, 0, 0), (0.075, 0.03, 0.045), m_cheek, parent=rig, segs=24)
        ck.location = (cx, cy, fz - 0.14)
        ck.rotation_euler = (0, 0, math.asin(cx / R))
        face[side] = (eye, closed)
    mouth = arc("boca", (0, -R + 0.005, fz - 0.15), 0.065, -0.01, 0.05, m_ink, parent=rig)
    mouth_o = sphere("boca_o", (0, 0, 0), (0.05, 0.025, 0.055), m_ink, parent=rig, segs=24)
    mouth_o.location = (0, -R + 0.01, fz - 0.17)

    return dict(rig=rig, fl=fl, flame=flame, core=core, lamp=lamp, ember=ember, face=face,
                mouth=mouth, mouth_o=mouth_o)


def lights_and_camera():
    def area(name, loc, energy, size, color="#ffffff"):
        bpy.ops.object.light_add(type="AREA", location=loc)
        o = bpy.context.object
        o.name = name
        o.data.energy = energy
        o.data.size = size
        o.data.color = srgb(color)[:3]
        d = Vector((0, 0, 0.8)) - o.location
        o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        return o

    area("key", (-3.2, -4.0, 4.2), 780, 3.5, "#fff1de")
    area("fill", (3.5, -3.0, 1.6), 240, 4.0, "#eef0f5")
    area("rim", (1.5, 3.5, 3.5), 380, 2.5, "#ffe2c2")

    bpy.ops.object.camera_add(location=(0, -6.6, 2.1))
    cam = bpy.context.object
    cam.data.lens = 80
    target = Vector((0.06, 0, 0.88))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam


# ---------------------------------------------------------------- animación
def key(obj, path, frame):
    obj.keyframe_insert(data_path=path, frame=frame)


def set_visible(obj, visible, frame):
    obj.hide_render = not visible
    obj.keyframe_insert(data_path="hide_render", frame=frame)


def animate(p, state, frames):
    sc = bpy.context.scene
    sc.frame_start = 1
    sc.frame_end = frames
    rig, fl = p["rig"], p["fl"]

    for i in range(frames):
        f = i + 1
        t = i / frames  # 0..1, bucle perfecto con ciclos enteros
        s1 = math.sin(TAU * t)
        s2 = math.sin(TAU * 2 * t)
        s3 = math.sin(TAU * 3 * t + 0.7)
        s5 = math.sin(TAU * 5 * t + 1.9)

        blink = False
        eye_dx = 0.0
        if state == "trabajando":
            # saltito: dos rebotes por ciclo, con aplastado al tocar
            hop = abs(math.sin(TAU * t * 2))
            rig.location = (0, 0, 0.18 + 0.07 * hop)
            sq = 1 - 0.05 * (1 - hop)
            rig.scale = (1 / math.sqrt(sq), 1 / math.sqrt(sq), sq)
            rig.rotation_euler = (0, 0.025 * s1, 0)
            fl.scale = (1 + 0.06 * s3, 1 + 0.06 * s3, 1.1 + 0.14 * s5 + 0.06 * s2)
            fl.rotation_euler = (0.05 * s3, 0.12 * s2 + 0.05 * s5, 0)
            p["lamp"].data.energy = 62 + 14 * s5
            blink = 0.70 <= t < 0.76
            mouth_open = True
        elif state == "esperando":
            rig.location = (0, 0, 0.18)
            rig.rotation_euler = (0, 0.075 * s1, 0)
            br = 1 + 0.012 * s2
            rig.scale = (1, 1, br)
            fl.scale = (0.72 + 0.03 * s3, 0.72 + 0.03 * s3, 0.72 + 0.06 * s5)
            fl.rotation_euler = (0, -0.18 * s1 + 0.04 * s3, 0)
            p["lamp"].data.energy = 34 + 6 * s3
            eye_dx = 0.028 * math.copysign(min(1, abs(s1) * 1.6), s1)
            blink = 0.46 <= t < 0.52
            mouth_open = False
        else:  # descansando
            rig.location = (0, 0, 0.18)
            rig.rotation_euler = (0, 0, 0)
            br = 1 + 0.022 * (0.5 - 0.5 * math.cos(TAU * t))
            rig.scale = (1 + 0.012 * (br - 1) * 40 / 40, 1, br)
            fl.scale = (0.001, 0.001, 0.001)
            p["lamp"].data.energy = 0
            p["ember"].scale = [0.03 * (0.8 + 0.25 * (0.5 - 0.5 * math.cos(TAU * t)))] * 3
            key(p["ember"], "scale", f)
            mouth_open = False

        for obj, path in ((rig, "location"), (rig, "scale"), (rig, "rotation_euler"),
                          (fl, "scale"), (fl, "rotation_euler")):
            key(obj, path, f)
        p["lamp"].data.keyframe_insert(data_path="energy", frame=f)

        sleeping = state == "descansando"
        for side, (eye, closed) in p["face"].items():
            base_x = 0.17 * side
            eye.location.x = base_x + eye_dx
            eye.scale = (0.068, 0.04, 0.012 if blink else 0.088)
            key(eye, "location", f)
            key(eye, "scale", f)
            set_visible(eye, not sleeping, f)
            for ch in eye.children:
                set_visible(ch, not sleeping and not blink, f)
            set_visible(closed, sleeping, f)
        set_visible(p["mouth"], not mouth_open, f)
        set_visible(p["mouth_o"], mouth_open, f)
        set_visible(p["ember"], sleeping, f)
        for o in (p["flame"], p["core"]):
            set_visible(o, not sleeping, f)

    # interpolación constante: cada frame ya trae su valor exacto
    for obj in bpy.data.objects:
        ad = obj.animation_data
        if ad and ad.action:
            try:
                for fc in ad.action.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = "CONSTANT"
            except Exception:
                pass


# ---------------------------------------------------------------- render
STATES = ["trabajando", "esperando", "descansando"]
for state in STATES:
    if ONLY and state != ONLY:
        continue
    sc = reset()
    parts = build()
    lights_and_camera()
    animate(parts, state, FRAMES)
    d = os.path.join(OUT, state)
    os.makedirs(d, exist_ok=True)
    sc.render.filepath = os.path.join(d, "")
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    bpy.ops.render.render(animation=True)
    print("OK", state)
