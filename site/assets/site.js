// Wick · web. Sin dependencias.

// Borde de la barra al hacer scroll
const nav = document.querySelector(".nav");
const onScroll = () => nav && nav.classList.toggle("scrolled", window.scrollY > 8);
addEventListener("scroll", onScroll, { passive: true });
onScroll();

// Demo del menú: recorre los tres estados con los textos reales de la app
const stage = document.querySelector("[data-demo]");
const data = document.getElementById("demo-data");
if (stage && data) {
  const states = JSON.parse(data.textContent);
  const sprite = stage.querySelector(".stage > .sprite");
  const mini = stage.querySelector(".mac-menu .sprite");
  const title = stage.querySelector("[data-title]");
  const sub = stage.querySelector("[data-sub]");
  const rows = stage.querySelector("[data-rows]");
  const icon = stage.querySelector("[data-icon]");
  let i = 0;

  const render = (s) => {
    stage.dataset.state = s.mood;
    for (const el of [sprite, mini]) el.className = `sprite ${s.mood}`;
    title.textContent = s.title;
    sub.textContent = s.sub;
    icon.dataset.mood = s.mood;
    rows.replaceChildren(
      ...s.rows.map(([dot, project, detail]) => {
        const row = document.createElement("div");
        row.className = "row";
        row.innerHTML = `<span class="dot ${dot}">●</span><span></span><small></small>`;
        row.children[1].textContent = project;
        row.children[2].textContent = detail;
        return row;
      }),
    );
  };

  render(states[0]);
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce) {
    setInterval(() => {
      i = (i + 1) % states.length;
      render(states[i]);
    }, 4200);
  }
}
