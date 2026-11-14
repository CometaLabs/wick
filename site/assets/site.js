// Wick · web. Sin dependencias.
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

// Borde de la barra al hacer scroll
const nav = document.querySelector(".nav");
const onScroll = () => nav?.classList.toggle("scrolled", window.scrollY > 8);
addEventListener("scroll", onScroll, { passive: true });
onScroll();

// Demo: terminal + menú de Wick recorren los tres estados con textos reales de la app
const scene = document.querySelector("[data-demo]");
const data = document.getElementById("demo-data");
if (scene && data) {
  const states = JSON.parse(data.textContent);
  const sprites = scene.querySelectorAll(".sprite");
  const title = scene.querySelector("[data-title]");
  const sub = scene.querySelector("[data-sub]");
  const rows = scene.querySelector("[data-rows]");
  const term = scene.querySelector("[data-term]");
  const icon = scene.querySelector("[data-icon]");

  const line = (cls, text, tag = "div") => {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    el.textContent = text;
    return el;
  };

  const render = (s) => {
    scene.dataset.state = s.mood;
    for (const el of sprites) el.className = el.className.replace(/\b(working|waiting|resting)\b/, s.mood);
    title.textContent = s.title;
    sub.textContent = s.sub;
    icon.dataset.mood = s.mood;
    term.replaceChildren(...s.term.map(([c, t]) => line(c, t)));
    rows.replaceChildren(
      ...s.rows.map(([dot, project, detail]) => {
        const row = line("row", "");
        row.append(line(`dot ${dot}`, "●", "span"), line("", project, "span"), line("", detail, "small"));
        return row;
      }),
    );
  };

  let i = 0;
  if (!reduce) {
    setInterval(() => {
      if (document.hidden) return;
      i = (i + 1) % states.length;
      render(states[i]);
    }, 4600);
  }
}

// Cuenta atrás del paso 3 (2:00 → 0:00, en bucle)
const countdown = document.querySelector("[data-countdown]");
if (countdown && !reduce) {
  let left = 120;
  setInterval(() => {
    left = left <= 0 ? 120 : left - 1;
    countdown.textContent = `${Math.floor(left / 60)}:${String(left % 60).padStart(2, "0")}`;
  }, 1000);
}

// Copiar comandos
for (const button of document.querySelectorAll("[data-copy]")) {
  button.addEventListener("click", async () => {
    const code = button.parentElement.querySelector("code").textContent;
    const label = button.querySelector("span");
    const original = label.textContent;
    try {
      await navigator.clipboard.writeText(code);
      label.textContent = button.dataset.done;
    } catch {
      label.textContent = "⌘C";
    }
    setTimeout(() => (label.textContent = original), 1600);
  });
}
