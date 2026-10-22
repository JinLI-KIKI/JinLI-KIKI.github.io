#!/usr/bin/env python3
"""Build the static site from _src/pages/*.html.

Each page file starts with a header comment:

    <!--
    path: lenovo/excess-inventory/
    title: Excess inventory clean-up
    description: One sentence for search engines and link previews.
    section: lenovo
    -->

and the rest is the page body. Placeholders:

    {{root}}                      relative path to the site root ("../../")
    {{timeline:year}}             Lenovo year chart (all cases)
    {{timeline:year:<slug>}}      same, with one case highlighted
    {{timeline:tariff}}           tariff steps around the pull-in
    {{spectrum}}                  280 nm emission spectrum (interactive)
    {{spectrum:mini}}             small version for the home page
    {{casenav}}                   previous / next links inside a section

Run:  python3 _src/build.py      (from the repository root)
"""
import datetime as dt
import html
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "_src" / "pages"
SITE = "https://jinli-kiki.github.io/"
EMAIL = "lijin201107@outlook.com"
GITHUB = "https://github.com/JinLI-KIKI"

NAV = [
    ("lenovo", "Lenovo", "lenovo/"),
    ("research", "Research", "research/"),
    ("projects", "Projects", "projects/"),
    ("publications", "Publications", "publications/"),
    ("cv", "Résumé", "cv/"),
]

# Ordered case lists drive previous/next links and the footer site map.
SECTIONS = {
    "lenovo": [
        ("lenovo/", "Overview"),
        ("lenovo/planning-role/", "North America master planning"),
        ("lenovo/excess-inventory/", "Excess inventory clean-up"),
        ("lenovo/tariff-pull-in/", "Tariff pull-in"),
        ("lenovo/vietnam-transition/", "China to Vietnam motherboards"),
        ("lenovo/commit-automation/", "Parts-to-box commit tool"),
    ],
    "research": [
        ("research/", "Overview"),
        ("research/reactive-species/", "Reactive species"),
        ("research/taste-and-odour/", "Taste and odour in cold water"),
        ("research/real-water/", "Real water at the dosing point"),
        ("research/dalhousie/", "Partner projects in Canada"),
    ],
    "more": [
        ("projects/", "Projects"),
        ("publications/", "Publications"),
        ("experience/", "Earlier experience"),
        ("cv/", "Résumé"),
    ],
}

# ---------------------------------------------------------------- timeline


def D(s):
    return dt.date.fromisoformat(s)


YEAR = dict(
    start=D("2024-09-01"),
    end=D("2025-09-01"),
    rows=[
        ("planning-role", "North America master planning", "2024-09-01", "2025-08-31"),
        ("excess-inventory", "Excess inventory clean-up", "2024-09-01", "2025-08-31"),
        ("tariff-pull-in", "Tariff pull-in", "2024-12-01", "2025-02-28"),
        ("vietnam-transition", "China to Vietnam motherboards", "2025-01-01", "2025-07-31"),
        ("commit-automation", "Parts-to-box commit tool", "2025-02-01", "2025-05-31"),
    ],
    events=[
        ("2024-11-05", "Election", 1),
        ("2025-01-20", "Inauguration", 2),
        ("2025-02-04", "+10%", 3),
        ("2025-03-04", "+20%", 1),
        ("2025-04-11", "PCs exempted", 2),
        ("2025-05-12", "Geneva truce", 3),
    ],
    step=[("2024-09-01", 0), ("2025-02-04", 10), ("2025-03-04", 20)],
    step_max=25,
)

TARIFF = dict(
    start=D("2024-10-01"),
    end=D("2025-07-01"),
    events=[
        ("2024-11-05", "Election", 1),
        ("2024-11-25", "+10% pledged", 2, "minor"),
        ("2025-01-20", "Inauguration", 1, "minor"),
        ("2025-02-04", "+10% in force", 2),
        ("2025-03-04", "+20%", 3),
        ("2025-04-11", "PCs exempted", 1),
        ("2025-05-12", "Geneva truce", 2, "minor"),
    ],
    step=[("2024-10-01", 0), ("2025-02-04", 10), ("2025-03-04", 20)],
    step_max=30,
    window=("2024-12-01", "2025-03-01", "Pull-in window"),
)


def frac(d, a, b):
    return max(0.0, min(1.0, (d - a).days / (b - a).days))


def month_ticks(a, b):
    out, d = [], a
    while d < b:
        out.append(d)
        d = dt.date(d.year + (d.month // 12), d.month % 12 + 1, 1)
    return out


def step_path(spec, h=100):
    a, b, top = spec["start"], spec["end"], spec["step_max"]
    pts = [(frac(D(s), a, b), v) for s, v in spec["step"]]
    y = lambda v: h - v / top * (h - 4) - 2
    d = f"M0,{y(pts[0][1]):.1f}"
    for i, (f, v) in enumerate(pts[1:], 1):
        d += f" H{f * 1000:.1f} V{y(v):.1f}"
    d += " H1000"
    return d, y


def axis_html(a, b, compact_years=True):
    parts = []
    for m in month_ticks(a, b):
        f = frac(m, a, b)
        label = m.strftime("%b")
        cls = "tl-m"
        if m.month == 1 or m == a:
            label += f" <b>{m.year}</b>"
            cls += " tl-m-year"
        parts.append(f'<span class="{cls}" style="--f:{f:.4f}">{label}</span>')
    return "".join(parts)


def events_html(spec):
    a, b = spec["start"], spec["end"]
    out = []
    for ev in spec["events"]:
        s, label, tier = ev[:3]
        f = frac(D(s), a, b)
        side = " tl-ev-r" if f > 0.8 else ""
        if len(ev) > 3:
            side += " tl-ev-minor"
        when = D(s).strftime("%-d %b %Y")
        out.append(
            f'<span class="tl-ev t{tier}{side}" style="--f:{f:.4f}" title="{html.escape(label)}, {when}">'
            f'<span class="tl-ev-label">{html.escape(label)}</span></span>'
        )
    return "".join(out)


def timeline_year(root, highlight=None):
    spec = YEAR
    a, b = spec["start"], spec["end"]
    rows = []
    for slug, name, s, e in spec["rows"]:
        fa, fb = frac(D(s), a, b), frac(D(e) + dt.timedelta(days=1), a, b)
        cur = ""
        if highlight:
            cur = " is-current" if slug == highlight else " is-dim"
        when = f'{D(s).strftime("%b %Y")} – {D(e).strftime("%b %Y")}'
        aria = ' aria-current="page"' if slug == highlight else ""
        rows.append(
            f'<a class="tl-row{cur}" href="{root}lenovo/{slug}/"{aria}>'
            f'<span class="tl-name">{name}<span class="tl-when">{when}</span></span>'
            f'<span class="tl-track"><span class="tl-bar" style="--a:{fa:.4f};--b:{fb:.4f}"></span></span></a>'
        )
    d, y = step_path(spec)
    levels = f'<span class="tl-lvl" style="--y:{y(20):.1f}">20%</span>'
    step = (
        '<div class="tl-row tl-steprow"><span class="tl-name">Extra US duty on China-made laptops'
        '<span class="tl-when">on top of normal duty</span></span>'
        '<span class="tl-track"><svg viewBox="0 0 1000 100" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
        f'<path class="tl-step-area" d="{d} V100 H0 Z"/><path class="tl-step" d="{d}"/></svg>{levels}</span></div>'
    )
    return f"""<figure class="tl tl-year" aria-label="Timeline of my year at Lenovo against the 2025 US tariff steps">
  <div class="tl-plot">
    <div class="tl-head"><span class="tl-name"></span><span class="tl-track tl-axis">{axis_html(a, b)}</span></div>
    <div class="tl-body">
      <div class="tl-events" aria-hidden="true">{events_html(spec)}</div>
      {''.join(rows)}
      {step}
    </div>
  </div>
  <figcaption>My year at Lenovo against the US tariff steps on China-made goods. Election and inauguration: November 2024 and 20 January 2025. An extra 10% applied from 4 February 2025 and 20% from 4 March. On 11 April computers were exempted from the new reciprocal tariffs, but the 20% stayed. The Geneva truce on 12 May cut the reciprocal rate on other Chinese goods.</figcaption>
</figure>"""


def timeline_tariff(root):
    spec = TARIFF
    a, b = spec["start"], spec["end"]
    d, y = step_path(spec)
    ws, we, wl = spec["window"]
    fa, fb = frac(D(ws), a, b), frac(D(we), a, b)
    grid = "".join(
        f'<span class="tl-grid" style="--y:{y(v):.1f}"><span>{v}%</span></span>' for v in (0, 10, 20)
    )
    return f"""<figure class="tl tl-tariff" aria-label="Extra US duty on China-made laptops, October 2024 to June 2025, with the pull-in window">
  <div class="tl-plot">
    <div class="tl-head"><span class="tl-track tl-axis">{axis_html(a, b)}</span></div>
    <div class="tl-body">
      <div class="tl-events" aria-hidden="true">{events_html(spec)}</div>
      <div class="tl-chart">
        <span class="tl-window" style="--a:{fa:.4f};--b:{fb:.4f}"><span>{wl}</span></span>
        {grid}
        <svg viewBox="0 0 1000 100" preserveAspectRatio="none" aria-hidden="true" focusable="false">
          <path class="tl-step-area" d="{d} V100 H0 Z"/><path class="tl-step" d="{d}"/></svg>
      </div>
    </div>
  </div>
  <figcaption>The extra US duty on China-made laptops (line) and the window in which I pulled North American supply forward (shaded). The duty went from 0 to 10% on 4 February 2025 and to 20% on 4 March. Reciprocal tariffs on other Chinese goods rose to 125% in April, but computers were exempted from them on 11 April, so laptops stayed at 20%. The Geneva truce on 12 May cut the reciprocal rate on other goods to 10%.</figcaption>
</figure>"""


# ---------------------------------------------------------------- spectrum


def spectrum_path():
    W, base, amp = 1200, 228, 200
    pts = []
    for i in range(0, 1001, 5):
        lam = 230 + i * 0.1
        s = 4.7 if lam < 280 else 5.6
        I = math.exp(-0.5 * ((lam - 280) / s) ** 2) + 0.035 * math.exp(-0.5 * ((lam - 300) / 9) ** 2)
        pts.append(((lam - 230) / 100 * W, base - amp * I))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def spectrum(mini=False):
    p = spectrum_path()
    if mini:
        return f"""<svg class="spec-mini" viewBox="0 0 1200 240" preserveAspectRatio="none" aria-hidden="true" focusable="false">
  <path class="area" d="{p} L1200,228 L0,228 Z"/><path class="curve" d="{p}"/>
  <line class="peak" x1="600" y1="20" x2="600" y2="228"/><line class="baseline" x1="0" y1="228" x2="1200" y2="228"/></svg>"""
    ticks = "".join(
        f'<line x1="{x}" y1="228" x2="{x}" y2="{240 if x % 240 == 0 else 236}"/>'
        for x in range(120, 1200, 120)
    )
    return f"""<figure class="spectrum" aria-labelledby="spectrum-cap">
  <div class="spectrum-plot">
    <svg viewBox="0 0 1200 240" preserveAspectRatio="none" aria-hidden="true" focusable="false">
      <line class="edge" x1="1020" y1="40" x2="1020" y2="228"/>
      <path class="area" d="{p} L1200,228 L0,228 Z"/>
      <path class="curve" d="{p}" pathLength="1"/>
      <line class="baseline" x1="0" y1="228" x2="1200" y2="228"/>
      <line class="peak" x1="600" y1="20" x2="600" y2="228"/>
      <g class="ticks">{ticks}</g>
      <line class="probe" x1="0" y1="0" x2="0" y2="228"/>
    </svg>
    <span class="peak-label">280&nbsp;nm</span>
    <span class="band-label" style="left:2px">UV-C</span>
    <span class="band-label" style="left:calc(70% - 14px)">UV-B</span>
    <span class="band-label" style="left:calc(85% + 10px)">UV-A</span>
    <output class="readout"></output>
  </div>
  <div class="axis" aria-hidden="true">
    <span style="left:20%">250</span><span style="left:40%">270</span><span style="left:50%">280</span><span style="left:60%">290</span><span style="left:80%">310</span><span class="unit">nm</span>
  </div>
  <figcaption id="spectrum-cap">Emission of a 280&nbsp;nm UV-LED, the light source in most of my experiments. It sits where UV-C meets UV-B: short enough to damage microbial DNA, long enough to be absorbed well by free chlorine. Move across the curve to read the relative intensity.</figcaption>
</figure>"""


# ---------------------------------------------------------------- chrome


def rel_root(path):
    if path.endswith(".html"):
        return "/"
    depth = len([p for p in path.strip("/").split("/") if p])
    return "../" * depth


def header(root, section):
    links = []
    for key, label, href in NAV:
        cur = ' aria-current="page"' if key == section else ""
        links.append(f'<a href="{root}{href}"{cur}>{label}</a>')
    menu = []
    for key in ("lenovo", "research", "more"):
        title = {"lenovo": "Lenovo", "research": "Research", "more": "More"}[key]
        items = "".join(f'<a href="{root}{h}">{t}</a>' for h, t in SECTIONS[key])
        menu.append(f'<div><p>{title}</p>{items}</div>')
    return f"""<header class="bar" id="bar">
  <div class="bar-inner">
    <a class="bar-name" href="{root}">Jin Li</a>
    <nav class="bar-nav" aria-label="Main">{''.join(links)}</nav>
    <a class="bar-cta" href="mailto:{EMAIL}">Email me</a>
    <details class="menu">
      <summary aria-label="Open menu"><span></span><span></span></summary>
      <nav class="menu-panel" aria-label="All pages"><a class="menu-home" href="{root}">Home</a>{''.join(menu)}<a class="menu-mail" href="mailto:{EMAIL}">{EMAIL}</a></nav>
    </details>
  </div>
</header>"""


def footer(root):
    cols = []
    for key, title in (("lenovo", "Lenovo"), ("research", "Research"), ("more", "More")):
        items = "".join(f'<li><a href="{root}{h}">{t}</a></li>' for h, t in SECTIONS[key])
        cols.append(f'<div><h3>{title}</h3><ul>{items}</ul></div>')
    return f"""<footer class="foot band band-supply" id="contact">
  <div class="wrap foot-grid">
    <div class="foot-contact">
      <h2>Get in touch</h2>
      <p>Email is the fastest way to reach me.</p>
      <a class="foot-email" href="mailto:{EMAIL}">{EMAIL}</a>
      <p class="foot-small">Tokyo, Japan (JST, UTC+9). Code on <a href="{GITHUB}" rel="me">GitHub</a>.</p>
    </div>
    <nav class="foot-map" aria-label="Site map">{''.join(cols)}</nav>
  </div>
  <div class="wrap foot-base"><p>© 2026 Jin Li. Updated October 2026.</p><p>Set in Archivo. Hosted on GitHub Pages.</p></div>
</footer>"""


def casenav(root, path):
    for key, items in SECTIONS.items():
        hrefs = [h for h, _ in items]
        if path in hrefs and key in ("lenovo", "research"):
            i = hrefs.index(path)
            prev = items[i - 1] if i > 1 else None
            nxt = items[i + 1] if i + 1 < len(items) else None
            hub = items[0]
            out = ['<nav class="casenav wrap" aria-label="More cases">']
            out.append(
                f'<a class="cn-prev" href="{root}{prev[0]}"><span>Previous</span>{prev[1]}</a>' if prev
                else f'<a class="cn-prev" href="{root}{hub[0]}"><span>Back to</span>{"Lenovo overview" if key == "lenovo" else "Research overview"}</a>'
            )
            out.append(
                f'<a class="cn-next" href="{root}{nxt[0]}"><span>Next</span>{nxt[1]}</a>' if nxt
                else f'<a class="cn-next" href="{root}{hub[0]}"><span>Back to</span>{"Lenovo overview" if key == "lenovo" else "Research overview"}</a>'
            )
            out.append("</nav>")
            return "".join(out)
    return ""


def lenovo_note(root):
    return f"""<aside class="wrap case-note" aria-label="About this case">
  <p><b>About this page.</b> A personal account of my own work, not reviewed or endorsed by Lenovo. Results are the figures on my résumé; charts are schematic and examples use made-up numbers; no internal data, supplier or customer names. <a href="{root}lenovo/#boundary">What these pages share</a>.</p>
</aside>"""


def page(meta, body):
    path = meta["path"]
    root = rel_root(path)
    section = meta.get("section", "home")
    slug = path.strip("/").replace("/", "-") or "home"
    title = meta["title"]
    full_title = "Jin Li" if path == "" else f"{title} | Jin Li"
    if path == "":
        full_title = "Jin Li | Supply chain planning and UV-LED water treatment"
    desc = html.escape(meta["description"], quote=True)

    def sub(m):
        key = m.group(1)
        if key == "root":
            return root
        if key == "casenav":
            return casenav(root, path)
        if key == "lenovo-note":
            return lenovo_note(root)
        if key == "spectrum":
            return spectrum()
        if key == "spectrum:mini":
            return spectrum(mini=True)
        if key == "timeline:tariff":
            return timeline_tariff(root)
        if key.startswith("timeline:year"):
            parts = key.split(":")
            return timeline_year(root, parts[2] if len(parts) > 2 else None)
        raise KeyError(key)

    body = re.sub(r"\{\{([a-z:\-]+)\}\}", sub, body)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Jin Li">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}assets/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{root}assets/fonts/archivo-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{root}assets/css/style.css">
<script>document.documentElement.classList.add('js');</script>
</head>
<body class="sec-{section} page-{slug}">
<a class="skip" href="#main">Skip to content</a>
{header(root, section)}
<main id="main">
{body.strip()}
</main>
{footer(root)}
<script src="{root}assets/js/main.js" defer></script>
</body>
</html>
"""


def parse(text):
    m = re.match(r"\s*<!--(.*?)-->", text, re.S)
    meta = {}
    for line in m.group(1).strip().splitlines():
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    if meta.get("path") == "/":
        meta["path"] = ""
    return meta, text[m.end():]


def main():
    built = []
    for f in sorted(PAGES.glob("*.html")):
        meta, body = parse(f.read_text(encoding="utf-8"))
        out = ROOT / meta["path"] if meta["path"].endswith(".html") else ROOT / meta["path"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(meta, body), encoding="utf-8")
        built.append(meta["path"] or "/")
    print(f"built {len(built)} pages:", ", ".join(built))


if __name__ == "__main__":
    main()
