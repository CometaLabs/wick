# Wick · genera la web en inglés (/) y castellano (/es/) desde una sola plantilla.
#   python3 site/build.py
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
V = "8"  # súbelo al cambiar CSS/JS (los assets llevan caché inmutable)
DOMAIN = "https://wick.cometalabs.io"
ZIP = "https://github.com/CometaLabs/wick/releases/latest/download/Wick.zip"
REPO = "https://github.com/CometaLabs/wick"
AGENTS = ["Claude Code", "Codex", "Gemini CLI", "Cursor Agent", "OpenCode", "Aider", "Amp", "Goose",
          "Qwen Code", "Copilot CLI", "Crush", "Factory Droid"]

APPLE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.6c0-2.5 2-3.6 2.1-3.7-1.2-1.7-3-1.9-3.6-2-1.5-.2-3 .9-3.8.9s-2-.9-3.3-.9C6.1 7 4.5 8 3.6 9.6c-1.8 3.2-.5 7.8 1.3 10.4.9 1.3 1.9 2.7 3.2 2.6 1.3 0 1.8-.8 3.3-.8s2 .8 3.3.8c1.4 0 2.2-1.3 3.1-2.6 1-1.5 1.4-2.9 1.4-3-.1 0-2.8-1.1-2.8-4.4zM14 5.1c.7-.9 1.2-2 1.1-3.2-1 0-2.3.7-3 1.6-.7.8-1.2 2-1.1 3.1 1.1.1 2.3-.6 3-1.5z"/></svg>'
GITHUB = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .5a11.5 11.5 0 0 0-3.6 22.4c.6.1.8-.3.8-.6v-2c-3.2.7-3.9-1.5-3.9-1.5-.5-1.3-1.3-1.7-1.3-1.7-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.7-1.6-2.6-.3-5.3-1.3-5.3-5.7 0-1.3.5-2.3 1.2-3.1-.1-.3-.5-1.5.1-3.1 0 0 1-.3 3.2 1.2a11 11 0 0 1 5.8 0c2.2-1.5 3.2-1.2 3.2-1.2.6 1.6.2 2.8.1 3.1.8.8 1.2 1.9 1.2 3.1 0 4.4-2.7 5.4-5.3 5.7.4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6A11.5 11.5 0 0 0 12 .5z"/></svg>'
# Icono de la barra de menú, el mismo dibujo vectorial que la app (Icons.swift)
TRAY = ('<svg class="tray-icon" data-icon data-mood="working" viewBox="0 0 18 18" aria-hidden="true"><g transform="translate(0 18) scale(1 -1)">'
        '<rect x="4.5" y="1.5" width="9" height="9.2" rx="2.6"/><rect x="4.5" y="6.6" width="1.7" height="3.8" rx=".85"/>'
        '<rect x="11.2" y="5.4" width="1.7" height="4.8" rx=".85"/><rect x="8.55" y="10.2" width=".9" height="1.9" rx=".45"/>'
        '<path class="flame" d="M10.85 13.6a1.85 1.85 0 0 1-3.7 0C7.15 14.7 8.5 16 9 18c.5-2 1.85-3.3 1.85-4.4z"/>'
        '<circle class="eye" cx="7.1" cy="6.15" r="1"/><circle class="eye" cx="10.9" cy="6.15" r="1"/></g></svg>')
COPY_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>'

T = {
 "en": dict(
  lang="en", path="/", other="/es/", other_lang="es", other_label="ES", this_label="EN", locale="en_US", alt_locale="es_ES",
  title="Wick · Keep your Mac awake while AI agents work",
  desc="Wick is a free, open-source macOS menu bar app that keeps your Mac awake while Claude Code, Codex, Gemini CLI and other AI agents work, and lets it sleep when they're done.",
  og_desc="A tiny clay candle in your menu bar. It lights up when your agent starts working and lets your Mac sleep when it's done. Free and open source.",
  skip="Skip to content", nav_how="How it works", nav_features="Features", nav_install="Install", nav_faq="FAQ", download="Download",
  pill="New · v1.0 · free and open source",
  h1='Your agents work.<br>Your Mac <em>stays awake.</em>',
  lead="Wick is a little clay candle that lives in your menu bar. It lights up when an AI agent starts a long task, keeps your Mac from sleeping halfway through, and blows itself out when the work is done.",
  cta_dl="Download for macOS", cta_gh="View on GitHub",
  mono="v1.0.0 · macOS 13+ · Apple Silicon &amp; Intel · MIT",
  hand="lights up on its own", demo_label="Live demo: Wick follows an agent in the terminal",
  clock="Fri 10:42", agents_label="Agents", opt_hooks="Claude Code (hooks)", opt_others="Other agents (Codex, Gemini…)", opt_lid="Also with the lid closed",
  works_with="Works with the agents you already use",
  how_title="It follows your agent, not a timer.",
  how_intro="If your Mac sleeps halfway through a long run, the agent stops. With a classic keep-awake app you pick “2 hours” and hope you guessed right. Wick watches what your agents are actually doing.",
  s1_t="Your agent starts", s1_p="Claude Code tells Wick through hooks. Codex, Gemini CLI and the rest are spotted by their process.",
  s2_t="Wick lights up", s2_p="The flame comes on and macOS won't idle-sleep while there's real work going on.", s2_chip="Mac awake",
  s3_t="It finishes, the Mac rests", s3_p="Two more minutes in case the agent picks up again, then your Mac sleeps as usual.", s3_chip="Sleeps in",
  feat_title="Small, careful, yours.", feat_intro="Built for people who leave agents running and walk away.",
  f_lid_t="Close the lid, keep working", f_lid_p="Optional. One password, then lid sleep is disabled only while an agent works.",
  f_lid_back="Normal sleep comes back when", f_lid_items=["the work ends", "you quit Wick", "the app crashes", "battery drops below 15%"],
  f_wait_t="Knows when it needs you", f_wait_p="The candle turns orange when a Claude Code session waits for your approval. Meanwhile, your Mac can rest.",
  f_wait_row=("wick", "Claude Code · needs you · now"),
  f_list_t="Every agent at a glance", f_list_p="Each agent with its project and how long it's been at it. Click one to open its folder.",
  f_fix_t="Heals after a restart", f_fix_p="If your Mac went down with lid mode on, macOS would keep ignoring the lid. Wick spots it and fixes it.",
  f_fix_row="Your Mac won't sleep when closed", f_fix_btn="Fix",
  f_manual_t="Manual mode", f_manual_p="Not using an agent? Keep it awake for a while, or until you stop it.",
  f_manual_items=["15 minutes", "1 hour", "4 hours", "Until I stop it"],
  f_priv_t="Nothing leaves your Mac", f_priv_p="No network, no analytics, no account. Same power assertions as caffeinate.", f_priv_k="network requests",
  cmp_title="Wick vs. a keep-awake timer", cmp_head=("", "Classic timer", "Wick"),
  cmp_rows=[("Turns on", "When you pick a duration", "By itself, when an agent starts"), ("Turns off", "When the timer runs out", "2 min after the agent finishes"),
            ("Agent needs approval", "Keeps burning battery", "Lets the Mac rest"), ("Several sessions", "Can't see them", "Lists each one by project"),
            ("Lid closed", "All the time", "Only while an agent works")],
  inst_title="Install in a minute.",
  inst_steps=[f'<a href="{ZIP}">Download Wick.zip</a>, unzip it and drag <b>Wick.app</b> into Applications.',
              "Open it. Wick isn't signed with an Apple Developer ID yet, so the first time go to <b>System Settings → Privacy &amp; Security</b> and click <b>Open Anyway</b>.",
              "If you use Claude Code, accept the hooks for exact tracking. Other agents work right away."],
  inst_term="Or from the terminal", inst_copy="Copy", inst_copied="Copied", inst_uninstall="To remove the Claude Code hooks before deleting the app:",
  faq_title="Questions",
  faq=[("Does Wick only work with Claude Code?", "No. Claude Code is followed through hooks, which is the most precise. Codex, Gemini CLI, Cursor Agent, OpenCode, Aider, Amp, Goose and other terminal agents are detected by their process: if the agent or what it just launched is using CPU, Wick treats it as working."),
       ("Why does macOS warn me when I open it?", "Wick isn't signed with an Apple Developer ID yet. Open it once, then go to System Settings → Privacy & Security and click Open Anyway. Or run xattr -dr com.apple.quarantine /Applications/Wick.app."),
       ("Why does it ask for my password?", "Only for lid-closed mode. macOS doesn't let a normal app stop lid sleep, so Wick starts a small helper with administrator rights that turns it on and off with your agent. It never asks otherwise."),
       ("Is lid-closed mode safe?", "Wick restores normal sleep when the agent finishes, when you quit, if the app crashes and below 15% battery. Keep your Mac somewhere it can breathe: a closed laptop in a bag gets warm."),
       ("What does it change in my Claude Code settings?", "It adds a few hooks to ~/.claude/settings.json that call ~/.wick/hook. The hook saves the session state and exits in milliseconds; it never blocks Claude Code or changes what it does. Your other hooks stay untouched, and turning the option off removes Wick's."),
       ("Does Wick collect any data?", "No. No network, no analytics, no account. Session state lives in ~/.wick on your Mac."),
       ("Is it free?", "Yes, free and open source under the MIT license. It started from Caffeinator by Jon Kraayen and is made by Cometa Labs.")],
  studio_k="Made by Cometa Labs", studio_t="We build products with agents every day.",
  studio_p="Cometa Labs is a digital product studio in Palma de Mallorca. We design and build apps, websites and AI products for startups and companies, and we make small tools like Wick when we need them ourselves.",
  studio_cta="Work with us", studio_gh="More open source", studio_url="https://cometalabs.io/en",
  studio_list=[("AI products and agents", "Studio", "https://cometalabs.io/en"), ("Klipp", "Screen recorder", "https://klipp.cometalabs.io/"), ("Wick", "You are here", REPO)],
  end_hand="good night, Mac", end_t="Let your agents work through the night.", end_p="Free, open source, 3 MB.", end_gh="Star on GitHub",
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
  faq_ld_intro="",
 ),
 "es": dict(
  lang="es", path="/es/", other="/", other_lang="en", other_label="EN", this_label="ES", locale="es_ES", alt_locale="en_US",
  title="Wick · Tu Mac despierto mientras trabajan tus agentes de IA",
  desc="Wick es una app gratuita y open source para la barra de menú de macOS que mantiene el Mac despierto mientras Claude Code, Codex, Gemini CLI y otros agentes de IA trabajan, y lo deja dormir cuando terminan.",
  og_desc="Una velita de plastilina en tu barra de menú. Se enciende cuando tu agente se pone a trabajar y deja dormir al Mac cuando termina. Gratis y open source.",
  skip="Ir al contenido", nav_how="Cómo funciona", nav_features="Funciones", nav_install="Instalar", nav_faq="Preguntas", download="Descargar",
  pill="Nuevo · v1.0 · gratis y open source",
  h1='Tus agentes trabajan.<br>Tu Mac <em>no se duerme.</em>',
  lead="Wick es una velita de plastilina que vive en tu barra de menú. Se enciende cuando un agente de IA empieza una tarea larga, evita que el Mac se duerma a mitad y se apaga sola cuando termina.",
  cta_dl="Descargar para macOS", cta_gh="Ver en GitHub",
  mono="v1.0.0 · macOS 13+ · Apple Silicon e Intel · MIT",
  hand="se enciende sola", demo_label="Demo en vivo: Wick sigue a un agente en la terminal",
  clock="vie 10:42", agents_label="Agentes", opt_hooks="Claude Code (hooks)", opt_others="Otros agentes (Codex, Gemini…)", opt_lid="También con la tapa cerrada",
  works_with="Funciona con los agentes que ya usas",
  how_title="Sigue a tu agente, no a un temporizador.",
  how_intro="Si el Mac se duerme a mitad de una tarea larga, el agente se para. Con las apps de siempre eliges «2 horas» y esperas haber acertado. Wick mira lo que tus agentes hacen de verdad.",
  s1_t="Tu agente empieza", s1_p="Claude Code avisa a Wick con hooks. A Codex, Gemini CLI y los demás los reconoce por su proceso.",
  s2_t="Wick se enciende", s2_p="Se enciende la llama y macOS no se duerme mientras hay trabajo de verdad.", s2_chip="Mac despierto",
  s3_t="Termina y el Mac descansa", s3_p="Dos minutos más por si el agente sigue, y luego el Mac duerme como siempre.", s3_chip="Duerme en",
  feat_title="Pequeña, cuidada y tuya.", feat_intro="Para quien deja a sus agentes trabajando y se va a por un café.",
  f_lid_t="Cierra la tapa, que siga trabajando", f_lid_p="Opcional. Una contraseña y el reposo al cerrar la tapa se desactiva solo mientras un agente trabaja.",
  f_lid_back="El reposo normal vuelve cuando", f_lid_items=["termina el trabajo", "sales de Wick", "la app se cuelga", "la batería baja del 15 %"],
  f_wait_t="Sabe cuándo te necesita", f_wait_p="La velita se pone naranja cuando una sesión de Claude Code espera tu OK. Mientras, el Mac puede descansar.",
  f_wait_row=("wick", "Claude Code · te espera · ahora"),
  f_list_t="Todos tus agentes a la vista", f_list_p="Cada agente con su proyecto y cuánto lleva. Haz clic en uno para abrir su carpeta.",
  f_fix_t="Se arregla tras un reinicio", f_fix_p="Si el Mac se apagó con el modo tapa activo, macOS seguiría ignorando la tapa. Wick lo detecta y lo arregla.",
  f_fix_row="El Mac no se duerme al cerrar la tapa", f_fix_btn="Arreglar",
  f_manual_t="Modo manual", f_manual_p="¿Sin agentes? Mantenlo despierto un rato o hasta que lo pares.",
  f_manual_items=["15 minutos", "1 hora", "4 horas", "Hasta que la pare"],
  f_priv_t="Nada sale de tu Mac", f_priv_p="Sin red, sin analíticas, sin cuenta. Las mismas aserciones de energía que caffeinate.", f_priv_k="peticiones de red",
  cmp_title="Wick frente a un temporizador", cmp_head=("", "Temporizador clásico", "Wick"),
  cmp_rows=[("Se enciende", "Cuando eliges una duración", "Sola, cuando un agente empieza"), ("Se apaga", "Cuando acaba el tiempo", "2 min después de que el agente termine"),
            ("El agente te pide permiso", "Sigue gastando batería", "Deja descansar al Mac"), ("Varias sesiones", "No las ve", "Las lista por proyecto"),
            ("Tapa cerrada", "Todo el rato", "Solo mientras un agente trabaja")],
  inst_title="Se instala en un minuto.",
  inst_steps=[f'<a href="{ZIP}">Descarga Wick.zip</a>, descomprímela y arrastra <b>Wick.app</b> a Aplicaciones.',
              "Ábrela. Todavía no está firmada con un Developer ID de Apple, así que la primera vez ve a <b>Ajustes del Sistema → Privacidad y seguridad</b> y pulsa <b>Abrir igualmente</b>.",
              "Si usas Claude Code, acepta los hooks para seguirlo al detalle. Los demás agentes funcionan al momento."],
  inst_term="O desde la terminal", inst_copy="Copiar", inst_copied="Copiado", inst_uninstall="Para quitar los hooks de Claude Code antes de borrar la app:",
  faq_title="Preguntas",
  faq=[("¿Solo funciona con Claude Code?", "No. A Claude Code lo sigue con hooks, que es lo más preciso. Codex, Gemini CLI, Cursor Agent, OpenCode, Aider, Amp, Goose y otros agentes de terminal se detectan por su proceso: si el agente o lo que acaba de lanzar gasta CPU, Wick lo da por trabajando."),
       ("¿Por qué macOS me avisa al abrirla?", "Todavía no está firmada con un Developer ID de Apple. Ábrela una vez, ve a Ajustes del Sistema → Privacidad y seguridad y pulsa Abrir igualmente. O ejecuta xattr -dr com.apple.quarantine /Applications/Wick.app."),
       ("¿Por qué me pide la contraseña?", "Solo para el modo tapa cerrada. macOS no deja que una app normal evite el reposo al cerrar la tapa, así que Wick arranca un pequeño ayudante con permisos de administrador que lo enciende y apaga con tu agente. Para nada más."),
       ("¿Es seguro el modo tapa cerrada?", "Wick devuelve el reposo normal cuando el agente termina, al salir, si la app se cuelga y con la batería por debajo del 15 %. Deja el Mac donde pueda respirar: un portátil cerrado dentro de una mochila se calienta."),
       ("¿Qué cambia en mi configuración de Claude Code?", "Añade unos hooks a ~/.claude/settings.json que llaman a ~/.wick/hook. El hook guarda el estado de la sesión y sale en milisegundos; nunca bloquea a Claude Code ni cambia lo que hace. Tus otros hooks no se tocan, y al desactivar la opción se quitan los de Wick."),
       ("¿Recoge algún dato?", "No. Sin red, sin analíticas, sin cuenta. El estado de las sesiones vive en ~/.wick, en tu Mac."),
       ("¿Es gratis?", "Sí, gratis y open source con licencia MIT. Parte de Caffeinator, de Jon Kraayen, y la hace Cometa Labs.")],
  studio_k="Hecha por Cometa Labs", studio_t="Hacemos producto con agentes cada día.",
  studio_p="Cometa Labs es un estudio de producto digital en Palma de Mallorca. Diseñamos y desarrollamos apps, webs y productos de IA para startups y empresas, y hacemos pequeñas herramientas como Wick cuando las necesitamos nosotros.",
  studio_cta="Trabaja con nosotros", studio_gh="Más open source", studio_url="https://cometalabs.io/",
  studio_list=[("Productos de IA y agentes", "Estudio", "https://cometalabs.io/"), ("Klipp", "Grabador de pantalla", "https://klipp.cometalabs.io/"), ("Wick", "Estás aquí", REPO)],
  end_hand="buenas noches, Mac", end_t="Que tus agentes trabajen toda la noche.", end_p="Gratis, open source, 3 MB.", end_gh="Dale una estrella",
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


def ld(t):
    url = DOMAIN + t["path"]
    graph = [
        {"@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/", "name": "Wick",
         "inLanguage": ["en", "es"], "publisher": {"@id": "https://cometalabs.io/#organization"}},
        {"@type": "SoftwareApplication", "@id": DOMAIN + "/#app", "name": "Wick", "url": url,
         "description": t["desc"], "image": DOMAIN + "/assets/wick-icon-512.png", "screenshot": DOMAIN + "/og.png",
         "applicationCategory": "DeveloperApplication", "operatingSystem": "macOS 13+",
         "softwareVersion": "1.0.0", "license": "https://opensource.org/licenses/MIT", "isAccessibleForFree": True,
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


def page(t):
    d0 = t["demo"][0]
    term0 = "".join(f'<div class="{c}">{esc(x)}</div>' for c, x in d0["term"])
    marquee = "".join(f"<li>{a}</li>" for a in AGENTS)
    faq = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in t["faq"])
    cmp = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td><td class="win">{c}</td></tr>' for a, b, c in t["cmp_rows"])
    steps = "".join(f"<li>{s}</li>" for s in t["inst_steps"])
    lid_items = "".join(f"<li>{x}</li>" for x in t["f_lid_items"])
    manual = "".join(('<li class="sel">' if i == 1 else "<li>") + x + "</li>" for i, x in enumerate(t["f_manual_items"]))
    wait_tray = TRAY.replace('data-mood="working"', 'data-mood="waiting"')
    studio_list = "".join(f'<li><a href="{u}?utm_source=wick&amp;utm_medium=site">{a}</a><span>{b}</span></li>' for a, b, u in t["studio_list"])
    rows0 = "".join(f'<div class="row"><span class="dot {d}">●</span><span>{p}</span><small>{x}</small></div>' for d, p, x in d0["rows"])
    hreflang = f'<link rel="alternate" hreflang="en" href="{DOMAIN}/">\n<link rel="alternate" hreflang="es" href="{DOMAIN}/es/">\n<link rel="alternate" hreflang="x-default" href="{DOMAIN}/">'
    demo_json = json.dumps(t["demo"], ensure_ascii=False)
    s1_term = "".join(f'<div class="{c}">{esc(x)}</div>' for c, x in t["demo"][0]["term"][:3])
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t['title']}</title>
<meta name="description" content="{t['desc']}">
<link rel="canonical" href="{DOMAIN}{t['path']}">
{hreflang}
<meta name="theme-color" content="#efe7da">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/Roobert-SemiBold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/wick-working.webp" as="image" fetchpriority="high">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;600&amp;family=JetBrains+Mono:wght@400;500&amp;display=swap">
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
      <li><a href="#how">{t['nav_how']}</a></li>
      <li><a href="#features">{t['nav_features']}</a></li>
      <li><a href="#install">{t['nav_install']}</a></li>
      <li><a href="#faq">{t['nav_faq']}</a></li>
    </ul>
    <div class="right">
      <div class="langs" role="group" aria-label="Language">
        <a href="/" hreflang="en" lang="en"{' aria-current="page"' if t['lang'] == 'en' else ''}>EN</a>
        <a href="/es/" hreflang="es" lang="es"{' aria-current="page"' if t['lang'] == 'es' else ''}>ES</a>
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
    </div>

    <div class="wrap">
      <div class="scene" data-demo data-state="working" role="img" aria-label="{t['demo_label']}">
        <div class="menubar">
          <span class="apple">{APPLE}</span><b>Terminal</b><span class="dim-item">Shell</span><span class="dim-item">Edit</span><span class="dim-item">View</span>
          <span class="spacer"></span>
          <span class="tray">{TRAY}</span>
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

  <section class="marquee-wrap" aria-label="{t['works_with']}">
    <p class="mono center">{t['works_with']}</p>
    <div class="marquee"><ul>{marquee}</ul><ul aria-hidden="true">{marquee}</ul></div>
  </section>

  <section id="how" aria-labelledby="how-title">
    <div class="wrap">
      <h2 id="how-title">{t['how_title']}</h2>
      <p class="intro">{t['how_intro']}</p>
      <ol class="steps3">
        <li class="card">
          <div class="mini mini-term">{s1_term}</div>
          <span class="num">1</span><h3>{t['s1_t']}</h3><p>{t['s1_p']}</p>
        </li>
        <li class="card">
          <div class="mini mini-wick"><div class="sprite working"></div><span class="chip on">{t['s2_chip']}</span></div>
          <span class="num">2</span><h3>{t['s2_t']}</h3><p>{t['s2_p']}</p>
        </li>
        <li class="card">
          <div class="mini mini-wick off"><div class="sprite resting"></div><span class="chip">{t['s3_chip']} <b class="countdown" data-countdown>2:00</b></span></div>
          <span class="num">3</span><h3>{t['s3_t']}</h3><p>{t['s3_p']}</p>
        </li>
      </ol>
    </div>
  </section>

  <section id="features" class="tint" aria-labelledby="features-title">
    <div class="wrap">
      <h2 id="features-title">{t['feat_title']}</h2>
      <p class="intro">{t['feat_intro']}</p>
      <div class="bento">
        <article class="card wide lid">
          <div class="text"><h3>{t['f_lid_t']}</h3><p>{t['f_lid_p']}</p></div>
          <div class="mini">
            <div class="toggle-row"><span>{t['opt_lid']}</span><span class="switch on" aria-hidden="true"></span></div>
            <p class="mini-k">{t['f_lid_back']}</p>
            <ul class="checks">{lid_items}</ul>
          </div>
        </article>
        <article class="card">
          <div class="mini center-mini"><span class="tray big-tray">{wait_tray}</span>
            <div class="row solo"><span class="dot waiting">●</span><span>{t['f_wait_row'][0]}</span><small>{t['f_wait_row'][1]}</small></div></div>
          <h3>{t['f_wait_t']}</h3><p>{t['f_wait_p']}</p>
        </article>
        <article class="card">
          <div class="mini list-mini">{rows0}</div>
          <h3>{t['f_list_t']}</h3><p>{t['f_list_p']}</p>
        </article>
        <article class="card">
          <div class="mini center-mini"><div class="warn-row"><span>⚠︎ {t['f_fix_row']}</span><button type="button" tabindex="-1">{t['f_fix_btn']}</button></div></div>
          <h3>{t['f_fix_t']}</h3><p>{t['f_fix_p']}</p>
        </article>
        <article class="card">
          <div class="mini"><ul class="submenu">{manual}</ul></div>
          <h3>{t['f_manual_t']}</h3><p>{t['f_manual_p']}</p>
        </article>
        <article class="card warm full">
          <div class="mini center-mini"><span class="zero">0</span><span class="mono">{t['f_priv_k']}</span></div>
          <div><h3>{t['f_priv_t']}</h3><p>{t['f_priv_p']}</p></div>
        </article>
      </div>
    </div>
  </section>

  <section aria-labelledby="cmp-title">
    <div class="wrap narrow">
      <h2 id="cmp-title" class="center">{t['cmp_title']}</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th scope="col"><span class="sr">—</span></th><th scope="col">{t['cmp_head'][1]}</th><th scope="col">{t['cmp_head'][2]}</th></tr></thead>
          <tbody>{cmp}</tbody>
        </table>
      </div>
    </div>
  </section>

  <section id="install" class="tint" aria-labelledby="install-title">
    <div class="wrap install">
      <div>
        <h2 id="install-title">{t['inst_title']}</h2>
        <ol class="steps">{steps}</ol>
      </div>
      <div>
        <p class="mono">{t['inst_term']}</p>
        <div class="code"><pre><code>xattr -dr com.apple.quarantine /Applications/Wick.app</code></pre><button type="button" class="copy" data-copy data-done="{t['inst_copied']}">{COPY_ICON}<span>{t['inst_copy']}</span></button></div>
        <p class="small">{t['inst_uninstall']}</p>
        <div class="code"><pre><code>/Applications/Wick.app/Contents/MacOS/Wick --uninstall-hooks</code></pre><button type="button" class="copy" data-copy data-done="{t['inst_copied']}">{COPY_ICON}<span>{t['inst_copy']}</span></button></div>
      </div>
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
      <a href="{t['other']}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{'Español' if t['lang'] == 'en' else 'English'}</a>
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
