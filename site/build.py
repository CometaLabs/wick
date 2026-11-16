# Wick · genera la web en inglés (/) y castellano (/es/) desde una sola plantilla.
#   python3 site/build.py
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
V = "17"  # súbelo al cambiar CSS/JS (los assets llevan caché inmutable)
DOMAIN = "https://wick.cometalabs.io"
ZIP = "https://github.com/CometaLabs/wick/releases/latest/download/Wick.dmg"
REPO = "https://github.com/CometaLabs/wick"
LOGOS = os.path.join(os.path.dirname(HERE), "art", "logos")
SIZE = "1.5 MB"
# (nombre, logo en art/logos o None). Logos monocromos de simple-icons y lobe-icons.
AGENTS = [("Claude Code", "claude"), ("Codex", "codex"), ("Gemini CLI", "gemini"), ("Cursor Agent", "cursor"),
          ("Copilot CLI", "copilot"), ("Qwen Code", "qwen"), ("Goose", "goose"), ("OpenCode", None), ("Aider", None),
          ("Amp", None), ("Crush", None), ("Factory Droid", None)]

APPLE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.6c0-2.5 2-3.6 2.1-3.7-1.2-1.7-3-1.9-3.6-2-1.5-.2-3 .9-3.8.9s-2-.9-3.3-.9C6.1 7 4.5 8 3.6 9.6c-1.8 3.2-.5 7.8 1.3 10.4.9 1.3 1.9 2.7 3.2 2.6 1.3 0 1.8-.8 3.3-.8s2 .8 3.3.8c1.4 0 2.2-1.3 3.1-2.6 1-1.5 1.4-2.9 1.4-3-.1 0-2.8-1.1-2.8-4.4zM14 5.1c.7-.9 1.2-2 1.1-3.2-1 0-2.3.7-3 1.6-.7.8-1.2 2-1.1 3.1 1.1.1 2.3-.6 3-1.5z"/></svg>'
GITHUB = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .5a11.5 11.5 0 0 0-3.6 22.4c.6.1.8-.3.8-.6v-2c-3.2.7-3.9-1.5-3.9-1.5-.5-1.3-1.3-1.7-1.3-1.7-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.7-1.6-2.6-.3-5.3-1.3-5.3-5.7 0-1.3.5-2.3 1.2-3.1-.1-.3-.5-1.5.1-3.1 0 0 1-.3 3.2 1.2a11 11 0 0 1 5.8 0c2.2-1.5 3.2-1.2 3.2-1.2.6 1.6.2 2.8.1 3.1.8.8 1.2 1.9 1.2 3.1 0 4.4-2.7 5.4-5.3 5.7.4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6A11.5 11.5 0 0 0 12 .5z"/></svg>'
TRAY = ('<svg class="tray-icon" data-icon data-mood="working" viewBox="0 0 18 18" aria-hidden="true"><g transform="translate(0 18) scale(1 -1)">'
        '<rect x="4.5" y="1.5" width="9" height="9.2" rx="2.6"/><rect x="4.5" y="6.6" width="1.7" height="3.8" rx=".85"/>'
        '<rect x="11.2" y="5.4" width="1.7" height="4.8" rx=".85"/><rect x="8.55" y="10.2" width=".9" height="1.9" rx=".45"/>'
        '<path class="flame" d="M10.85 13.6a1.85 1.85 0 0 1-3.7 0C7.15 14.7 8.5 16 9 18c.5-2 1.85-3.3 1.85-4.4z"/>'
        '<circle class="eye" cx="7.1" cy="6.15" r="1"/><circle class="eye" cx="10.9" cy="6.15" r="1"/></g></svg>')
COPY_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>'
MOON = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.7 14.1A8.6 8.6 0 0 1 9.9 3.3a.6.6 0 0 0-.8-.7A9.6 9.6 0 1 0 21.4 14.9a.6.6 0 0 0-.7-.8z"/></svg>'
CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'

T = {
 "en": dict(
  lang="en", path="/", other="/es/", other_lang="es", locale="en_US", alt_locale="es_ES",
  title="Wick · Keep your Mac awake while AI agents work",
  desc="Wick is a free, open-source macOS menu bar app that keeps your Mac awake while Claude Code, Codex, Gemini CLI and other AI agents work, and lets it sleep when they're done.",
  og_desc="A tiny clay candle in your menu bar. It lights up when your agent starts working and lets your Mac sleep when it's done. Free and open source.",
  skip="Skip to content", nav_problem="Why", nav_how="How it works", nav_install="Install", nav_faq="FAQ", download="Download",
  pill=f"Free · open source · {SIZE}",
  h1='Your agents work.<br>Your Mac <em>stays awake.</em>',
  lead="Wick is a free app for your menu bar. When Claude Code, Codex or another AI agent starts working, it keeps your Mac awake. When the work is done, it lets it sleep. You don't have to do a thing.",
  cta_dl="Download for macOS", cta_gh="View on GitHub",
  mono="v1.0.3 · macOS 13+ · Apple Silicon &amp; Intel",
  works_short="Works with", hand="lights up on its own", demo_label="Live demo: Wick follows an agent in the terminal",
  clock="Fri 10:42", agents_label="Agents", opt_hooks="Claude Code (hooks)", opt_others="Other agents (Codex, Gemini…)", opt_lid="Also with the lid closed",
  pb_title="The problem", pb_intro="You leave an agent on a long task and go for a coffee. A few minutes later the Mac falls asleep, and the agent stops with it.",
  pb_without="Without Wick", pb_with="With Wick",
  pb_without_task="Refactoring 48 files", pb_without_state="Stopped at 38%", pb_without_note="The Mac went to sleep. When you come back, the work is half done.",
  pb_with_state="Done", pb_with_note="Wick keeps the Mac awake while the agent works. When you come back, it's finished.",
  pb_sleep="Mac asleep",
  how_title="How it works", how_intro="Here's what Wick does on a normal afternoon. You don't touch anything.",
  tl=[("10:00", "working", "You give it a task", "working", "awake"),
      ("10:18", "waiting", "It asks for your OK", "needs you", "can sleep"),
      ("10:20", "working", "You say yes", "working", "awake"),
      ("10:41", "grace", "It finishes", "done", "2 more min"),
      ("10:43", "sleep", "All quiet", "resting", "asleep")],
  tl_agent="Agent", tl_mac="Mac",
  how_note="With Claude Code, Wick knows exactly when it's working and when it needs you. With Codex, Gemini, Cursor and the rest, it notices from their activity.",
  feat_title="Small, and does what it says",
  feats=[("agents", "Works with your agents", "Claude Code, Codex, Gemini CLI, Cursor Agent, Copilot CLI, Aider and more. Several at once, too."),
         ("needs", "Tells you when it needs you", "If an agent is waiting for your answer, the candle in the menu bar turns orange."),
         ("lid", "Even with the lid closed", "Optional. Close your laptop and the agent keeps working. When it's done, the Mac sleeps normally again."),
         ("private", "Free and private", "No account, no internet, no tracking. Open source, so anyone can read the code.")],
  needs_chip="needs you", feat_lid_toggle="Also with the lid closed", priv_badges=["MIT", "No account", "Offline"],
  inst_title="Start in one minute",
  inst_steps=[("Download", f'Open <a href="{ZIP}">Wick.dmg</a> and drag the candle into the <b>Applications</b> folder.'),
              ("Open it", "Open Wick from Applications. If macOS asks, go to <b>System Settings → Privacy &amp; Security → Open Anyway</b>."),
              ("Look up", "Wick has no window: the candle appears in your menu bar, at the top right. If you use Claude Code, accept the connection.")],
  inst_term="Prefer the terminal?", inst_copy="Copy", inst_copied="Copied", inst_uninstall="To remove the Claude Code hooks before deleting the app:",
  faq_title="Questions",
  faq=[("I opened it and nothing happened. Where is it?", "Wick has no window or Dock icon: it lives in the menu bar, as a little candle at the top right next to the clock. If your menu bar is full, macOS hides it behind the camera notch: hold ⌘ and drag other icons to make room."),
       ("Does it only work with Claude Code?", "No. With Claude Code it uses hooks, so it knows exactly when the agent works and when it needs you. Codex, Gemini CLI, Cursor Agent, OpenCode, Aider, Amp, Goose and other terminal agents are noticed from their activity: if they're using the processor, they're working."),
       ("Does it work on Windows or Linux?", "Not yet. Wick is a Mac app (macOS 13 or later, Apple Silicon and Intel)."),
       ("Why does macOS warn me when I open it?", "Wick is signed by Cometa Labs, but Apple's notarization is still on its way. Until then, the first time go to System Settings → Privacy & Security and click Open Anyway."),
       ("Why does it ask for my password?", "Only if you turn on the lid-closed mode. macOS doesn't let a normal app stop the Mac from sleeping when you close the lid, so Wick needs permission once. It never asks otherwise."),
       ("Is the lid-closed mode safe?", "Normal sleep comes back when the agent finishes, when you quit Wick, if it crashes, or below 15% battery. Leave the Mac somewhere it can breathe: a closed laptop in a bag gets warm."),
       ("What does it change on my computer?", "For Claude Code it adds a few hooks to ~/.claude/settings.json (after backing it up). They only tell Wick what's happening and never change what Claude does. You can remove them from the menu."),
       ("Is it really free?", "Yes. Free and open source under the MIT license, made by Cometa Labs. It started from Caffeinator by Jon Kraayen.")],
  studio_k="Made by Cometa Labs", studio_t="We build products with agents every day.",
  studio_p="Cometa Labs is a digital product studio in Palma de Mallorca. We design and build apps, websites and AI products for startups and companies, and we make small tools like Wick when we need them ourselves.",
  studio_cta="Work with us", studio_gh="More open source", studio_url="https://cometalabs.io/en",
  studio_list=[("AI products and agents", "Studio", "https://cometalabs.io/en"), ("Klipp", "Screen recorder", "https://klipp.cometalabs.io/"), ("Wick", "You are here", REPO)],
  end_hand="good night, Mac", end_t="Let your agents work through the night.", end_p=f"Free, open source, {SIZE}.", end_gh="Star on GitHub",
  foot="Palma de Mallorca · MIT license", foot_nav="Footer", releases="Releases",
  demo=[{"mood": "working", "title": "Working", "sub": "Claude Code is working on wick. Your Mac won't sleep.",
         "rows": [["working", "wick", "Claude Code · working · 4 min"], ["working", "api", "Codex · working · 1 min"], ["idle", "landing", "Gemini CLI · idle · 12 min"]],
         "term": [["dim", "~/wick $ claude"], ["", "› add tests for the session store"], ["accent", "✻ Writing tests… (3m 12s)"], ["dim", "  ⎿ Sessions.swift, SessionTests.swift"]]},
        {"mood": "waiting", "title": "Waiting for you", "sub": "In wick. Meanwhile, your Mac may sleep.",
         "rows": [["waiting", "wick", "Claude Code · needs you · now"], ["working", "api", "Codex · working · 3 min"], ["idle", "landing", "Gemini CLI · idle · 14 min"]],
         "term": [["dim", "~/wick $ claude"], ["", "Run swift test?"], ["accent", "❯ 1. Yes"], ["dim", "  2. No, tell it what to do"]]},
        {"mood": "resting", "title": "Resting", "sub": "I light up on my own when your agent starts working.",
         "rows": [["idle", "wick", "Claude Code · done · 2 min"], ["idle", "api", "Codex · idle · 1 min"]],
         "term": [["dim", "~/wick $ claude"], ["ok", "✓ 12 tests passing"], ["", "Done. 3 files changed."], ["dim", "~/wick $ ▍"]]}],
 ),
 "es": dict(
  lang="es", path="/es/", other="/", other_lang="en", locale="es_ES", alt_locale="en_US",
  title="Wick · Tu Mac despierto mientras trabajan tus agentes de IA",
  desc="Wick es una app gratuita y open source para la barra de menú de macOS que mantiene el Mac despierto mientras Claude Code, Codex, Gemini CLI y otros agentes de IA trabajan, y lo deja dormir cuando terminan.",
  og_desc="Una velita de plastilina en tu barra de menú. Se enciende cuando tu agente se pone a trabajar y deja dormir al Mac cuando termina. Gratis y open source.",
  skip="Ir al contenido", nav_problem="Por qué", nav_how="Cómo funciona", nav_install="Instalar", nav_faq="Preguntas", download="Descargar",
  pill=f"Gratis · open source · {SIZE.replace('.', ',')}",
  h1='Tus agentes trabajan.<br>Tu Mac <em>no se duerme.</em>',
  lead="Wick es una app gratuita para la barra de menú. Cuando Claude Code, Codex u otro agente de IA se pone a trabajar, mantiene tu Mac despierto. Cuando termina, lo deja dormir. Tú no tienes que hacer nada.",
  cta_dl="Descargar para macOS", cta_gh="Ver en GitHub",
  mono="v1.0.3 · macOS 13+ · Apple Silicon e Intel",
  works_short="Funciona con", hand="se enciende sola", demo_label="Demo en vivo: Wick sigue a un agente en la terminal",
  clock="vie 10:42", agents_label="Agentes", opt_hooks="Claude Code (hooks)", opt_others="Otros agentes (Codex, Gemini…)", opt_lid="También con la tapa cerrada",
  pb_title="El problema", pb_intro="Dejas a un agente con una tarea larga y te vas a por un café. A los pocos minutos el Mac se duerme, y el agente se para con él.",
  pb_without="Sin Wick", pb_with="Con Wick",
  pb_without_task="Refactorizando 48 archivos", pb_without_state="Parado al 38 %", pb_without_note="El Mac se durmió. Cuando vuelves, el trabajo está a medias.",
  pb_with_state="Terminado", pb_with_note="Wick mantiene el Mac despierto mientras el agente trabaja. Cuando vuelves, está hecho.",
  pb_sleep="Mac dormido",
  how_title="Cómo funciona", how_intro="Esto es lo que hace Wick en una tarde cualquiera. Tú no tocas nada.",
  tl=[("10:00", "working", "Le das una tarea", "trabajando", "despierto"),
      ("10:18", "waiting", "Te pide el OK", "te espera", "puede dormir"),
      ("10:20", "working", "Le dices que sí", "trabajando", "despierto"),
      ("10:41", "grace", "Termina", "terminado", "2 min más"),
      ("10:43", "sleep", "Todo tranquilo", "en reposo", "dormido")],
  tl_agent="Agente", tl_mac="Mac",
  how_note="Con Claude Code, Wick sabe exactamente cuándo trabaja y cuándo te necesita. Con Codex, Gemini, Cursor y los demás, lo nota por su actividad.",
  feat_title="Pequeña, y hace lo que dice",
  feats=[("agents", "Funciona con tus agentes", "Claude Code, Codex, Gemini CLI, Cursor Agent, Copilot CLI, Aider y más. También varios a la vez."),
         ("needs", "Te avisa cuando te necesita", "Si un agente espera tu respuesta, la velita de la barra de menú se pone naranja."),
         ("lid", "Incluso con la tapa cerrada", "Opcional. Cierra el portátil y el agente sigue trabajando. Al terminar, el Mac vuelve a dormir con normalidad."),
         ("private", "Gratis y privada", "Sin cuenta, sin internet, sin rastreo. Open source: cualquiera puede leer el código.")],
  needs_chip="te espera", feat_lid_toggle="También con la tapa cerrada", priv_badges=["MIT", "Sin cuenta", "Sin internet"],
  inst_title="Empieza en un minuto",
  inst_steps=[("Descárgala", f'Abre <a href="{ZIP}">Wick.dmg</a> y arrastra la velita a la carpeta <b>Aplicaciones</b>.'),
              ("Ábrela", "Abre Wick desde Aplicaciones. Si macOS te lo pide, ve a <b>Ajustes del Sistema → Privacidad y seguridad → Abrir igualmente</b>."),
              ("Mira arriba", "Wick no tiene ventana: la velita aparece en tu barra de menú, arriba a la derecha. Si usas Claude Code, acepta la conexión.")],
  inst_term="¿Prefieres la terminal?", inst_copy="Copiar", inst_copied="Copiado", inst_uninstall="Para quitar los hooks de Claude Code antes de borrar la app:",
  faq_title="Preguntas",
  faq=[("La he abierto y no pasa nada. ¿Dónde está?", "Wick no tiene ventana ni icono en el Dock: vive en la barra de menú, como una velita arriba a la derecha, junto al reloj. Si tu barra está llena, macOS la esconde detrás de la cámara: mantén pulsada ⌘ y arrastra otros iconos para hacerle sitio."),
       ("¿Solo funciona con Claude Code?", "No. Con Claude Code usa hooks, así que sabe exactamente cuándo trabaja el agente y cuándo te necesita. Codex, Gemini CLI, Cursor Agent, OpenCode, Aider, Amp, Goose y otros agentes de terminal los nota por su actividad: si están usando el procesador, están trabajando."),
       ("¿Funciona en Windows o Linux?", "Todavía no. Wick es una app para Mac (macOS 13 o posterior, Apple Silicon e Intel)."),
       ("¿Por qué macOS me avisa al abrirla?", "Wick está firmada por Cometa Labs, pero la notarización de Apple aún está en camino. Mientras, la primera vez ve a Ajustes del Sistema → Privacidad y seguridad y pulsa Abrir igualmente."),
       ("¿Por qué me pide la contraseña?", "Solo si activas el modo tapa cerrada. macOS no deja que una app normal evite el reposo al cerrar la tapa, así que Wick necesita permiso una vez. Para nada más."),
       ("¿Es seguro el modo tapa cerrada?", "El reposo normal vuelve cuando el agente termina, al salir de Wick, si se cuelga o con la batería por debajo del 15 %. Deja el Mac donde pueda respirar: un portátil cerrado en una mochila se calienta."),
       ("¿Qué cambia en mi ordenador?", "Para Claude Code añade unos hooks a ~/.claude/settings.json (antes guarda una copia). Solo le cuentan a Wick lo que pasa y nunca cambian lo que hace Claude. Puedes quitarlos desde el menú."),
       ("¿De verdad es gratis?", "Sí. Gratis y open source con licencia MIT, hecha por Cometa Labs. Parte de Caffeinator, de Jon Kraayen.")],
  studio_k="Hecha por Cometa Labs", studio_t="Hacemos producto con agentes cada día.",
  studio_p="Cometa Labs es un estudio de producto digital en Palma de Mallorca. Diseñamos y desarrollamos apps, webs y productos de IA para startups y empresas, y hacemos pequeñas herramientas como Wick cuando las necesitamos nosotros.",
  studio_cta="Trabaja con nosotros", studio_gh="Más open source", studio_url="https://cometalabs.io/",
  studio_list=[("Productos de IA y agentes", "Estudio", "https://cometalabs.io/"), ("Klipp", "Grabador de pantalla", "https://klipp.cometalabs.io/"), ("Wick", "Estás aquí", REPO)],
  end_hand="buenas noches, Mac", end_t="Que tus agentes trabajen toda la noche.", end_p=f"Gratis, open source, {SIZE.replace('.', ',')}.", end_gh="Dale una estrella",
  foot="Palma de Mallorca · Licencia MIT", foot_nav="Pie", releases="Versiones",
  demo=[{"mood": "working", "title": "Trabajando", "sub": "Claude Code trabaja en wick. El Mac no se dormirá.",
         "rows": [["working", "wick", "Claude Code · trabajando · 4 min"], ["working", "api", "Codex · trabajando · 1 min"], ["idle", "landing", "Gemini CLI · en pausa · 12 min"]],
         "term": [["dim", "~/wick $ claude"], ["", "› añade tests al almacén de sesiones"], ["accent", "✻ Escribiendo tests… (3m 12s)"], ["dim", "  ⎿ Sessions.swift, SessionTests.swift"]]},
        {"mood": "waiting", "title": "Te está esperando", "sub": "En wick. Mientras, el Mac puede dormir.",
         "rows": [["waiting", "wick", "Claude Code · te espera · ahora"], ["working", "api", "Codex · trabajando · 3 min"], ["idle", "landing", "Gemini CLI · en pausa · 14 min"]],
         "term": [["dim", "~/wick $ claude"], ["", "¿Ejecutar swift test?"], ["accent", "❯ 1. Sí"], ["dim", "  2. No, dile qué hacer"]]},
        {"mood": "resting", "title": "Descansando", "sub": "Me enciendo sola cuando tu agente se pone a trabajar.",
         "rows": [["idle", "wick", "Claude Code · terminado · 2 min"], ["idle", "api", "Codex · en pausa · 1 min"]],
         "term": [["dim", "~/wick $ claude"], ["ok", "✓ 12 tests en verde"], ["", "Listo. 3 archivos cambiados."], ["dim", "~/wick $ ▍"]]}],
 ),
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def logo(key):
    with open(os.path.join(LOGOS, key + ".svg")) as f:
        return f.read()


def tray(mood):
    return TRAY.replace('data-mood="working"', 'data-mood="' + mood + '"')


def ld(t):
    url = DOMAIN + t["path"]
    graph = [
        {"@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/", "name": "Wick",
         "inLanguage": ["en", "es"], "publisher": {"@id": "https://cometalabs.io/#organization"}},
        {"@type": "SoftwareApplication", "@id": DOMAIN + "/#app", "name": "Wick", "url": url,
         "description": t["desc"], "image": DOMAIN + "/assets/wick-icon-512.png", "screenshot": DOMAIN + "/og.png",
         "applicationCategory": "DeveloperApplication", "operatingSystem": "macOS 13+",
         "softwareVersion": "1.0.3", "fileSize": SIZE, "license": "https://opensource.org/licenses/MIT", "isAccessibleForFree": True,
         "downloadUrl": ZIP, "codeRepository": REPO, "inLanguage": ["en", "es"],
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
         "author": {"@id": "https://cometalabs.io/#organization"}, "publisher": {"@id": "https://cometalabs.io/#organization"}},
        {"@type": "Organization", "@id": "https://cometalabs.io/#organization", "name": "Cometa Labs",
         "url": "https://cometalabs.io", "logo": "https://cometalabs.io/images/brand/cometio.png", "email": "hola@cometalabs.io",
         "description": "Digital product studio in Palma de Mallorca, Spain: apps, websites and AI products.",
         "address": {"@type": "PostalAddress", "addressLocality": "Palma", "addressRegion": "Illes Balears", "addressCountry": "ES"},
         "sameAs": ["https://github.com/CometaLabs", "https://www.linkedin.com/company/cometa-labs/", "https://x.com/CometaLabs"]},
        {"@type": "FAQPage", "@id": url + "#faq", "inLanguage": t["lang"],
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]},
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)


def feature_visual(key, t):
    if key == "agents":
        cells = "".join(f'<span title="{n}">{logo(l)}</span>' for n, l in AGENTS if l)
        return f'<div class="fv logos">{cells}<span class="more">+5</span></div>'
    if key == "needs":
        return (f'<div class="fv needs"><div class="sprite waiting"></div>'
                f'<span class="needs-chip"><span class="dot waiting">●</span>{t["needs_chip"]}</span></div>')
    if key == "lid":
        return (f'<div class="fv lid"><div class="toggle-row"><span>{t["feat_lid_toggle"]}</span>'
                f'<span class="switch on" aria-hidden="true"></span></div></div>')
    return '<div class="fv private">' + "".join(f'<span class="badge">{b}</span>' for b in t["priv_badges"]) + "</div>"


def page(t):
    d0 = t["demo"][0]
    term0 = "".join(f'<div class="{c}">{esc(x)}</div>' for c, x in d0["term"])
    rows0 = "".join(f'<div class="row"><span class="dot {d}">●</span><span>{p}</span><small>{x}</small></div>' for d, p, x in d0["rows"])
    hero_logos = "".join(f'<span class="hl" title="{n}">{logo(l)}</span>' for n, l in AGENTS if l)
    faq = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in t["faq"])
    steps = "".join(f'<li><b>{h}</b><p>{p}</p></li>' for h, p in t["inst_steps"])
    studio_list = "".join(f'<li><a href="{u}?utm_source=wick&amp;utm_medium=site">{a}</a><span>{b}</span></li>' for a, b, u in t["studio_list"])
    segs = [("working", 18), ("waiting", 2), ("working", 21), ("grace", 2), ("sleep", 7)]
    tl_bar = "".join(f'<span class="seg {k}" style="flex:{w}"></span>' for k, w in segs)
    tl_items = ""
    for tm, k, title, agent, mac in t["tl"]:
        mood = "resting" if k in ("sleep", "grace") else k
        mac_on = "on" if k in ("working", "grace") else "off"
        agent_cls = {"working": "busy", "waiting": "asks", "grace": "done", "sleep": "done"}[k]
        tl_items += (f'<li class="{k}"><span class="time">{tm}</span><div class="sprite {mood} tl-wick"></div>'
                     f'<b>{title}</b><dl>'
                     f'<div><dt>{t["tl_agent"]}</dt><dd class="{agent_cls}">{agent}</dd></div>'
                     f'<div><dt>{t["tl_mac"]}</dt><dd class="mac {mac_on}">{mac}</dd></div></dl></li>')
    feats = "".join(f'<article class="card feat">{feature_visual(k, t)}<h3>{h}</h3><p>{p}</p></article>' for k, h, p in t["feats"])
    hreflang = f'<link rel="alternate" hreflang="en" href="{DOMAIN}/">\n<link rel="alternate" hreflang="es" href="{DOMAIN}/es/">\n<link rel="alternate" hreflang="x-default" href="{DOMAIN}/">'
    demo_json = json.dumps(t["demo"], ensure_ascii=False)
    en_cur = ' aria-current="page"' if t["lang"] == "en" else ""
    es_cur = ' aria-current="page"' if t["lang"] == "es" else ""
    other_name = "Español" if t["lang"] == "en" else "English"
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t['title']}</title>
<meta name="description" content="{t['desc']}">
<link rel="canonical" href="{DOMAIN}{t['path']}">
{hreflang}
<meta name="theme-color" content="#f7f3ec">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/Roobert-SemiBold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/Roobert-Regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;600&amp;family=JetBrains+Mono:wght@400;500&amp;display=swap" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;600&amp;family=JetBrains+Mono:wght@400;500&amp;display=swap"></noscript>
<link rel="stylesheet" href="/assets/site.css?v={V}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Wick by Cometa Labs">
<meta property="og:title" content="{t['title']}">
<meta property="og:description" content="{t['og_desc']}">
<meta property="og:url" content="{DOMAIN}{t['path']}">
<meta property="og:image" content="{DOMAIN}/og.png">
<meta property="og:image:width" content="1280">
<meta property="og:image:height" content="640">
<meta property="og:locale" content="{t['locale']}">
<meta property="og:locale:alternate" content="{t['alt_locale']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@CometaLabs">
<script type="application/ld+json">
{ld(t)}
</script>
</head>
<body>
<a class="skip" href="#main">{t['skip']}</a>
<div class="frame" aria-hidden="true"></div>

<header class="nav">
  <div class="wrap">
    <a class="brand" href="{t['path']}"><img src="/apple-touch-icon.png" alt="" width="32" height="32">Wick</a>
    <ul>
      <li><a href="#problem">{t['nav_problem']}</a></li>
      <li><a href="#how">{t['nav_how']}</a></li>
      <li><a href="#install">{t['nav_install']}</a></li>
      <li><a href="#faq">{t['nav_faq']}</a></li>
    </ul>
    <div class="right">
      <div class="langs" role="group" aria-label="Language">
        <a href="/" hreflang="en" lang="en"{en_cur}>EN</a>
        <a href="/es/" hreflang="es" lang="es"{es_cur}>ES</a>
      </div>
      <a class="icon-link" href="{REPO}" aria-label="GitHub">{GITHUB}</a>
      <a class="btn primary small" href="{ZIP}">{APPLE}{t['download']}</a>
    </div>
  </div>
</header>

<main id="main">
  <section class="hero" aria-labelledby="title">
    <div class="wrap center">
      <a class="pill" href="{REPO}/releases/latest"><span class="spark"></span>{t['pill']}</a>
      <h1 id="title">{t['h1']}</h1>
      <p class="lead">{t['lead']}</p>
      <div class="actions">
        <a class="btn primary" href="{ZIP}">{APPLE}{t['cta_dl']}</a>
        <a class="btn ghost" href="{REPO}">{GITHUB}{t['cta_gh']}</a>
      </div>
      <p class="mono">{t['mono']}</p>
      <div class="hero-logos"><span>{t['works_short']}</span>{hero_logos}</div>
    </div>

    <div class="wrap">
      <div class="scene" data-demo data-state="working" role="img" aria-label="{t['demo_label']}">
        <div class="menubar">
          <span class="apple">{APPLE}</span><b>Terminal</b><span class="dim-item">Shell</span><span class="dim-item">Edit</span><span class="dim-item">View</span>
          <span class="spacer"></span>
          <span class="tray"><span class="mb-wick" data-icon data-mood="working"></span></span>
          <span class="dim-item">{t['clock']}</span>
        </div>
        <p class="hand" aria-hidden="true">{t['hand']}<svg viewBox="0 0 80 50" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 40c18 2 44-4 62-30"/><path d="M54 10l12 0 2 12"/></svg></p>
        <div class="terminal">
          <div class="bar"><i></i><i></i><i></i><span>wick — zsh</span></div>
          <div class="lines" data-term>{term0}</div>
        </div>
        <div class="mac-menu">
          <div class="head">
            <div class="sprite working"></div>
            <div><b data-title>{d0['title']}</b><p data-sub>{d0['sub']}</p></div>
          </div>
          <hr>
          <div class="label">{t['agents_label']}</div>
          <div data-rows>{rows0}</div>
          <hr>
          <div class="opt on">{t['opt_hooks']}</div>
          <div class="opt on">{t['opt_others']}</div>
          <div class="opt">{t['opt_lid']}</div>
        </div>
        <div class="sprite big working"></div>
      </div>
    </div>
  </section>

  <section id="problem" aria-labelledby="problem-title">
    <div class="wrap">
      <h2 id="problem-title" class="center">{t['pb_title']}</h2>
      <p class="intro center-intro">{t['pb_intro']}</p>
      <div class="versus">
        <article class="card vs without">
          <p class="vs-label">{t['pb_without']}</p>
          <div class="vs-screen">
            <div class="vs-task"><span>{t['pb_without_task']}</span><b>{t['pb_without_state']}</b></div>
            <div class="vs-bar"><i style="width:38%"></i></div>
            <div class="vs-sleep">{MOON}{t['pb_sleep']}</div>
          </div>
          <p>{t['pb_without_note']}</p>
        </article>
        <article class="card vs with">
          <p class="vs-label">{t['pb_with']}</p>
          <div class="vs-screen">
            <div class="vs-task"><span>{t['pb_without_task']}</span><b class="ok">{CHECK}{t['pb_with_state']}</b></div>
            <div class="vs-bar"><i style="width:100%"></i></div>
            <div class="sprite working vs-wick"></div>
          </div>
          <p>{t['pb_with_note']}</p>
        </article>
      </div>
    </div>
  </section>

  <section id="how" class="tint" aria-labelledby="how-title">
    <div class="wrap">
      <h2 id="how-title" class="center">{t['how_title']}</h2>
      <p class="intro center-intro">{t['how_intro']}</p>
      <div class="timeline-card card">
        <div class="tl-bar" aria-hidden="true">{tl_bar}</div>
        <ol class="timeline">{tl_items}</ol>
      </div>
      <p class="how-note"><span class="mark">{logo('claude')}</span>{t['how_note']}</p>
    </div>
  </section>

  <section aria-labelledby="feat-title">
    <div class="wrap">
      <h2 id="feat-title" class="center">{t['feat_title']}</h2>
      <div class="feats">{feats}</div>
    </div>
  </section>

  <section id="install" class="tint" aria-labelledby="install-title">
    <div class="wrap center">
      <h2 id="install-title">{t['inst_title']}</h2>
      <ol class="steps-big">{steps}</ol>
      <div class="actions"><a class="btn primary" href="{ZIP}">{APPLE}{t['cta_dl']}</a></div>
      <details class="term-details">
        <summary>{t['inst_term']}</summary>
        <div class="code"><pre><code>xattr -dr com.apple.quarantine /Applications/Wick.app</code></pre><button type="button" class="copy" data-copy data-done="{t['inst_copied']}">{COPY_ICON}<span>{t['inst_copy']}</span></button></div>
        <p class="small">{t['inst_uninstall']}</p>
        <div class="code"><pre><code>/Applications/Wick.app/Contents/MacOS/Wick --uninstall-hooks</code></pre><button type="button" class="copy" data-copy data-done="{t['inst_copied']}">{COPY_ICON}<span>{t['inst_copy']}</span></button></div>
      </details>
    </div>
  </section>

  <section id="faq" class="faq" aria-labelledby="faq-title">
    <div class="wrap narrow">
      <h2 id="faq-title" class="center">{t['faq_title']}</h2>
      {faq}
    </div>
  </section>

  <section aria-labelledby="studio-title">
    <div class="wrap">
      <div class="studio">
        <div>
          <p class="mono k">{t['studio_k']}</p>
          <h2 id="studio-title">{t['studio_t']}</h2>
          <p>{t['studio_p']}</p>
          <div class="actions">
            <a class="btn primary" href="{t['studio_url']}?utm_source=wick&amp;utm_medium=site&amp;utm_campaign=wick">{t['studio_cta']}</a>
            <a class="btn ghost" href="https://github.com/CometaLabs">{t['studio_gh']}</a>
          </div>
        </div>
        <ul>{studio_list}</ul>
      </div>
    </div>
  </section>

  <section class="end" aria-labelledby="end-title">
    <div class="wrap center">
      <p class="hand static" aria-hidden="true">{t['end_hand']}</p>
      <div class="sprite resting end-sprite" role="img" aria-label="Wick"></div>
      <h2 id="end-title">{t['end_t']}</h2>
      <p class="intro">{t['end_p']}</p>
      <div class="actions">
        <a class="btn primary" href="{ZIP}">{APPLE}{t['cta_dl']}</a>
        <a class="btn ghost" href="{REPO}">{GITHUB}{t['end_gh']}</a>
      </div>
    </div>
  </section>
</main>

<footer>
  <div class="wrap">
    <span>© 2026 <a href="{t['studio_url']}?utm_source=wick&amp;utm_medium=footer">Cometa Labs</a> · {t['foot']}</span>
    <nav aria-label="{t['foot_nav']}">
      <a href="{REPO}">GitHub</a>
      <a href="{REPO}/releases">{t['releases']}</a>
      <a href="/llms.txt">llms.txt</a>
      <a href="{t['other']}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{other_name}</a>
    </nav>
  </div>
</footer>

<script type="application/json" id="demo-data">{demo_json}</script>
<script src="/assets/site.js?v={V}" defer></script>
</body>
</html>
"""


for key, t in T.items():
    out = os.path.join(HERE, t["path"].strip("/"), "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(page(t))
    print("ok", out)
