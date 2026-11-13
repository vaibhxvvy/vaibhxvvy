#!/usr/bin/env python3
"""Render the animated SVG cards used by the profile README.

    python scripts/build_cards.py            # animated cards -> cards/
    STATIC=1 python scripts/build_cards.py   # final frame, no animation
                                             #   -> cards-static/ (+ preview.html)

Layout (top to bottom): hero, contribution graph, monthly activity, three
badges, "What I'm coding" title, three project cards, "Small stuff" title,
small repo cards.

Inputs (refreshed daily by .github/workflows/ripple-real.yml):
    data/contributions.json   {"contributions": [{"date","count","level"}, ...]}
    data/repos.json           {"<repo>": {"description","language",
                                          "stargazers_count","forks_count","pushed_at"}}
    data/profile.json         {"public_repos": N}
    data/featured.txt         repos to fetch metadata for; every name that is
                              not a PROJECTS repo becomes a small card
Optional:
    assets/portrait.(png|jpg|jpeg|webp)   shown in the hero instead of "VS"

Env: DATA_DIR / OUT_DIR override the data and output folders.

Cards are shown through <img>, so only img-safe features are used: an inline
<style> block (CSS keyframes), SMIL <animate>, and fonts subset with
pyftsubset and embedded as base64 WOFF data URIs. No scripts, no external
requests. CSS animations stop under prefers-reduced-motion; SMIL cannot be
switched off by CSS, so every SMIL element lives in a .motion group that is
hidden there, with a .still twin showing the final frame.
"""
import base64
import html
import json
import math
import os
import re
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"
DATA = Path(os.environ.get("DATA_DIR", ROOT / "data"))
OUT = Path(os.environ.get("OUT_DIR", ROOT / ("cards-static" if STATIC else "cards")))
FONTS = ROOT / "fonts"

# ----------------------------------------------------------------- config --
USER = "vaibhxvvy"
NAME = "Vaibhav Surthi"
TAGLINE = "Building systems that think, adapt and scale."
CHIPS = [("machine learning", "yellow"), ("agents", "pink"),
         ("local LLMs", "mint"), ("indie builder", "cream")]
SITE = "https://vaibhavsurthi.dev"

# key, label, big text, colour, link (link is used by README.md, not the card)
BADGES = [
    ("build", "BUILD", "{repos} public repos", "blue", "https://github.com/" + USER + "?tab=repositories"),
    ("ship", "SHIP", "{contribs} contributions", "yellow", "https://github.com/" + USER),
    ("talk", "TALK", "Say hi", "pink", SITE),
]

# Big project cards. "repo" pulls stars/language from data/repos.json.
PROJECTS = [
    dict(key="brikk", name="brikk", band="blue", lang="Rust",
         desc="A fast native command launcher for Windows and Linux, written in Rust.",
         url="https://brikkapp.vercel.app/"),
    dict(key="paper", name="paper", band="mint",
         desc="New project. Details coming soon.",
         url="https://github.com/" + USER + "/paper"),
    dict(key="opentab", name="opentab", band="pink", lang="TypeScript", repo="fcuk-paywalls",
         desc="An open index of no-signup, in-browser, open-source tools. "
              "No accounts. No emails. No walls.",
         url="https://github.com/" + USER + "/fcuk-paywalls"),
]
TITLE_BIG = "What I'm coding"
TITLE_SMALL = "Small stuff I ship"

# Palette: cream + blue from you, the rest are bright helpers.
C = dict(
    cream="#FFF2E6", blue="#0377FE", ink="#14183B", muted="#5B5F86",
    pink="#FF5C93", yellow="#FFC93C", mint="#3DDC97",
)
LANG_COLOR = {
    "Python": "#3572A5", "JavaScript": "#F1B900", "TypeScript": "#3178C6",
    "Rust": "#C9713E", "HTML": "#E34C26", "CSS": "#563D7C", "Go": "#00ADD8",
    "Shell": "#4EAA25", "Jupyter Notebook": "#DA5B0B", "C++": "#F34B7D",
}


def mix(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb))


L0 = mix(C["cream"], C["ink"], 0.09)
LEVELS = [L0] + [mix(L0, C["blue"], t) for t in (0.3, 0.55, 0.8, 1.0)]

# ------------------------------------------------------------------ fonts --
# css class -> (file, family, weight)
FONT_CLASS = {
    "fb": ("fredoka-latin-500-normal.woff", "Fre", 500),
    "fx": ("fredoka-latin-700-normal.woff", "Fre", 700),
    "fh": ("caveat-latin-700-normal.woff", "Cav", 700),
}
_metrics = {}
_font_cache = {}


def _metric(cls):
    fname = FONT_CLASS[cls][0]
    if fname not in _metrics:
        f = TTFont(str(FONTS / fname))
        _metrics[fname] = (f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm)
    return _metrics[fname]


def tw(s, size, cls="fb", ls=0):
    """Rendered text width in px, from the font's real advance widths."""
    cmap, hmtx, upm = _metric(cls)
    total = 0
    for ch in s:
        g = cmap.get(ord(ch))
        if g is None:
            raise SystemExit(f"font {cls} has no glyph for {ch!r} (in {s!r})")
        total += hmtx[g][0]
    return total / upm * size + ls * len(s)


def fit(s, size, maxw, cls="fx"):
    while size > 10 and tw(s, size, cls) > maxw:
        size -= 1
    return size


def wrap(s, size, cls, maxw, maxlines):
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(trial, size, cls) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > maxlines:
        lines = lines[:maxlines]
        last = lines[-1]
        while last and tw(last + "...", size, cls) > maxw:
            last = last[:-1].rstrip()
        lines[-1] = last + "..."
    return lines


def font_b64(cls, chars):
    key = (cls, chars)
    if key in _font_cache:
        return _font_cache[key]
    src = FONTS / FONT_CLASS[cls][0]
    with tempfile.TemporaryDirectory() as td:
        listing, out = Path(td) / "chars.txt", Path(td) / "out.woff"
        listing.write_text(chars, encoding="utf-8")
        subset.main([
            str(src), f"--text-file={listing}", f"--output-file={out}",
            "--flavor=woff", "--layout-features=kern", "--no-hinting",
            "--desubroutinize", "--drop-tables+=DSIG",
        ])
        b64 = base64.b64encode(out.read_bytes()).decode()
    _font_cache[key] = b64
    return b64


# ------------------------------------------------------------ svg helpers --
def esc(s):
    return html.escape(str(s), quote=True)


def A(cls="", d=None, kind="rise"):
    """class/style attributes; entrance animation only when not STATIC."""
    classes = cls.split()
    style = ""
    if d is not None and not STATIC:
        classes.append(kind)
        style = f' style="--d:{d:.2f}s"'
    return (f' class="{" ".join(classes)}"' if classes else "") + style


def txt(x, y, s, size, cls="fb", fill=None, anchor="start", d=None, ls=0):
    fill = fill or C["ink"]
    lsp = f' letter-spacing="{ls}"' if ls else ""
    anc = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{fill}"{anc}{lsp}'
            f'{A(cls, d)}>{esc(s)}</text>')


def dual(motion, still):
    """SMIL content and its reduced-motion/static twin."""
    if STATIC:
        return still
    return f'<g class="motion">{motion}</g><g class="still">{still}</g>'


def sticker(w, h, fill, shadow=None, r=22, outline=True):
    """Rounded card with a thick ink outline and a hard offset shadow."""
    shadow = shadow or C["ink"]
    s = (f'<rect x="8" y="8" width="{w - 9}" height="{h - 9}" rx="{r}" fill="{shadow}"/>'
         f'<rect x="2" y="2" width="{w - 9}" height="{h - 9}" rx="{r}" fill="{fill}"')
    s += f' stroke="{C["ink"]}" stroke-width="3"/>' if outline else "/>"
    return s


def pill(x, y, label, fill, size=13, d=None, pad=14, h=None, cls="fx", ls=0, tcolor=None):
    w = tw(label, size, cls, ls) + pad * 2
    h = h or size + 17
    g = (f'<rect x="{x:g}" y="{y:g}" width="{w:.1f}" height="{h}" rx="{h / 2:g}" fill="{fill}" '
         f'stroke="{C["ink"]}" stroke-width="2.5"/>')
    g += txt(x + w / 2, y + h / 2 + size * 0.34, label, size, cls, tcolor or C["ink"], "middle", ls=ls)
    return (f'<g{A("", d)}>{g}</g>' if d is not None else g), w


def sparkle(x, y, r, fill, delay=0.0):
    p = ("M0,-1C.15,-.25 .25,-.15 1,0C.25,.15 .15,.25 0,1C-.15,.25 -.25,.15 -1,0C-.25,-.15 -.15,-.25 0,-1Z")
    still = f'<path transform="translate({x} {y}) scale({r})" d="{p}" fill="{fill}"/>'
    motion = (f'<path transform="translate({x} {y}) scale({r})" d="{p}" fill="{fill}">'
              f'<animate attributeName="opacity" values="1;.25;1" dur="2.6s" begin="{delay:.2f}s" '
              f'repeatCount="indefinite"/></path>')
    return motion, still


def star_points(cx, cy, r):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}")
    return " ".join(pts)


def arrow(x, y, color, size=14, sw=2.4):
    return (f'<path d="M{x} {y + size}L{x + size} {y}M{x + 3} {y}H{x + size}V{y + size - 3}" '
            f'fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


def style_block(body):
    texts = re.findall(r"<text[^>]*>(.*?)</text>", body, re.S)
    chars = set(html.unescape(re.sub(r"<[^>]+>", "", "".join(texts)))) | set(" 0123456789")
    chars = "".join(sorted(chars))
    used = sorted({c for grp in re.findall(r'class="([^"]*)"', body) for c in grp.split()
                   if c in FONT_CLASS})
    css = []
    for cls in used:
        _, fam, wt = FONT_CLASS[cls]
        css.append("@font-face{font-family:'%s';font-weight:%d;font-style:normal;"
                   "src:url(data:font/woff;base64,%s) format('woff')}" % (fam, wt, font_b64(cls, chars)))
    css.append("text{font-family:'Fre','Fredoka',ui-rounded,'Nunito',system-ui,sans-serif}"
               ".fb{font-weight:500}.fx{font-weight:700}"
               ".fh{font-family:'Cav','Caveat','Segoe Print','Comic Sans MS',cursive;font-weight:700}")
    if not STATIC:
        css.append(
            ".rise{animation:rise .8s cubic-bezier(.2,.7,.2,1) var(--d,0s) both}"
            "@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}"
            ".pop{transform-box:fill-box;transform-origin:center;"
            "animation:pop .6s cubic-bezier(.3,1.5,.5,1) var(--d,0s) both}"
            "@keyframes pop{from{opacity:0;transform:scale(.3) rotate(-8deg)}to{opacity:1;transform:none}}"
            ".grow{transform-box:fill-box;transform-origin:50% 0;"
            "animation:grow .8s cubic-bezier(.2,.7,.2,1) var(--d,0s) both}"
            "@keyframes grow{from{transform:scaleY(0)}to{transform:none}}"
            ".draw{stroke-dasharray:1;stroke-dashoffset:0;"
            "animation:draw 1s cubic-bezier(.2,.7,.2,1) var(--d,0s) both}"
            "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
            ".bob{animation:bob 5s ease-in-out infinite}"
            "@keyframes bob{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-5px) rotate(2deg)}}"
            ".still{display:none}"
            "@media (prefers-reduced-motion:reduce){*{animation:none!important;"
            "transition:none!important}.motion{display:none}.still{display:inline}}")
    return "<style>" + "".join(css) + "</style>"


def svg_doc(w, h, body, title, desc, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">'
            f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
            f'{style_block(body)}<defs>{defs}</defs>{body}</svg>\n')


# ------------------------------------------------------------------- data --
def load_json(path, required=True):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        if required:
            raise SystemExit(f"missing {path} - run the workflow first")
        return {}


def load_contribs():
    raw = load_json(DATA / "contributions.json")
    rows = raw["contributions"] if isinstance(raw, dict) else raw
    by_day = {}
    for r in rows:
        by_day[date.fromisoformat(r["date"])] = (int(r["count"]), r.get("level"))
    if not by_day:
        raise SystemExit("contributions.json has no days")
    return by_day


def level_for(count, given, maxc):
    if given is not None:
        return max(0, min(4, int(given)))
    if count <= 0:
        return 0
    return min(4, 1 + int(3 * (count - 1) / max(1, maxc - 1) + 0.0001))


def stats(by_day):
    last = max(by_day)
    window = [last - timedelta(days=i) for i in range(365)]
    counts = {d: by_day.get(d, (0, None))[0] for d in window}
    total = sum(counts.values())
    active = sum(1 for v in counts.values() if v > 0)
    busiest = max(counts, key=lambda d: (counts[d], d))
    cur, d = 0, last
    if counts.get(d, 0) == 0:  # today may not be over yet
        d -= timedelta(days=1)
    while counts.get(d, 0) > 0:
        cur += 1
        d -= timedelta(days=1)
    longest = run = 0
    for d in sorted(counts):
        run = run + 1 if counts[d] > 0 else 0
        longest = max(longest, run)
    months = []
    y, m = last.year, last.month
    for _ in range(12):
        months.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    months.reverse()
    per_month = [sum(v for dd, v in counts.items() if (dd.year, dd.month) == ym) for ym in months]
    return dict(last=last, total=total, active=active, busiest=busiest,
                busiest_n=counts[busiest], streak=cur, longest=longest,
                months=months, per_month=per_month)


def fmt_date(d):
    return d.strftime("%b ") + str(d.day) + d.strftime(", %Y")


# ------------------------------------------------------------------ cards --
def card_hero(base):
    W, H = 900, 300
    cx, cy, R = 762, 150, 78
    portrait = next((p for e in ("png", "jpg", "jpeg", "webp")
                     if (p := ROOT / "assets" / f"portrait.{e}").exists()), None)
    defs = (f'<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">'
            f'<circle cx="3" cy="3" r="1.6" fill="{C["cream"]}" fill-opacity=".22"/></pattern>'
            f'<clipPath id="pc"><circle cx="{cx}" cy="{cy}" r="{R - 3}"/></clipPath>')
    b = [sticker(W, H, C["blue"], r=30),
         f'<rect x="2" y="2" width="{W - 9}" height="{H - 9}" rx="30" fill="url(#dots)"/>']
    for k, (sx, sy, sr, col) in enumerate([(640, 64, 17, "pink"), (856, 44, 12, "yellow"),
                                           (872, 256, 18, "mint"), (668, 250, 10, "cream")]):
        m, s = sparkle(sx, sy, sr, C[col], 0.4 * k)
        b.append(dual(m, s))
    b.append(txt(50, 80, "hey, I'm", 42, "fh", C["yellow"], d=base + 0.1))
    b.append(txt(48, 156, NAME, 70, "fx", C["cream"], d=base + 0.25))
    b.append(txt(50, 198, TAGLINE, 22, "fb", C["cream"], d=base + 0.5))
    x = 50
    for i, (label, col) in enumerate(CHIPS):
        g, w = pill(x, 226, label, C[col], 14, d=base + 0.7 + i * 0.1, h=34)
        b.append(g)
        x += w + 10
    ring = (f'<circle cx="{cx + 8}" cy="{cy + 8}" r="{R}" fill="{C["yellow"]}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{C["cream"]}" stroke="{C["ink"]}" stroke-width="3.5"/>')
    if portrait:
        mime = {"jpg": "jpeg"}.get(portrait.suffix[1:], portrait.suffix[1:])
        uri = f"data:image/{mime};base64," + base64.b64encode(portrait.read_bytes()).decode()
        ring += (f'<image href="{uri}" x="{cx - R}" y="{cy - R}" width="{R * 2}" height="{R * 2}" '
                 f'preserveAspectRatio="xMidYMid slice" clip-path="url(#pc)"/>'
                 f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{C["ink"]}" stroke-width="3.5"/>')
    else:
        ring += txt(cx, cy + 22, "VS", 66, "fx", C["blue"], "middle")
    b.append(f'<g{A("", base + 0.35, "pop")}><g class="bob">{ring}</g></g>')
    return svg_doc(W, H, "".join(b), f"{NAME} - GitHub profile", f"{NAME}. {TAGLINE}", defs)


def card_graph(by_day, st, base):
    W, H = 900, 272
    last = st["last"]
    last_sun = last - timedelta(days=(last.weekday() + 1) % 7)
    start = last_sun - timedelta(weeks=52)
    maxc = max(c for c, _ in by_day.values())
    left, top, pitch, cell = 62, 108, 15, 12
    b = [sticker(W, H, C["cream"])]
    b.append(txt(32, 62, "contribution graph", 40, "fh", C["blue"], d=base))
    b.append(txt(W - 34, 58, f"{st['total']:,} in the last year", 16, "fb", C["muted"], "end", base + 0.1))
    prev = None
    for col in range(53):
        d0 = start + timedelta(weeks=col)
        if d0.month != prev and not (col == 0 and (start + timedelta(weeks=2)).month != d0.month):
            if col <= 50:
                b.append(txt(left + col * pitch, 96, d0.strftime("%b"), 12, "fb", C["muted"], d=base + 0.15))
        prev = d0.month
    for row, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        b.append(txt(30, top + row * pitch + 10, lab, 11, "fb", C["muted"], d=base + 0.15))
    cells = []
    for col in range(53):
        for row in range(7):
            d0 = start + timedelta(weeks=col, days=row)
            if d0 > last:
                continue
            count, given = by_day.get(d0, (0, 0))
            lv = level_for(count, given, maxc)
            dly = base + 0.2 + col * 0.016 + row * 0.012
            sty = "" if STATIC else f' style="--d:{dly:.2f}s"'
            cls = f"l{lv}" + ("" if STATIC else " pop")
            cells.append(f'<rect class="{cls}" x="{left + col * pitch}" y="{top + row * pitch}" '
                         f'width="{cell}" height="{cell}" rx="3"{sty}/>')
    b.append("".join(cells))
    # loop 1: a soft shine sweeps across the grid
    gx0, gx1 = left - 6, left + 53 * pitch
    gh = 7 * pitch
    t0 = base + 1.6
    sweep = (f'<g clip-path="url(#gclip)"><rect y="{top - 4}" width="64" height="{gh + 8}" '
             f'fill="url(#shine)" opacity="0">'
             f'<animate attributeName="x" values="{gx0 - 64};{gx1}" dur="3.2s" begin="{t0:.2f};sw.end+2.4s" id="sw" '
             f'fill="remove"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" '
             f'dur="3.2s" begin="{t0:.2f};sw.end+2.4s"/></rect></g>')
    # loop 2: busiest cells twinkle, staggered
    hot = sorted(((c, d0) for d0, (c, _) in by_day.items() if start <= d0 <= last and c > 0),
                 key=lambda t: (-t[0], t[1]))[:24]
    tw_cells = []
    for k, (_, d0) in enumerate(hot):
        dd = (d0 - start).days
        hc, hr = dd // 7, dd % 7
        tw_cells.append(
            f'<rect x="{left + hc * pitch - 1}" y="{top + hr * pitch - 1}" width="{cell + 2}" '
            f'height="{cell + 2}" rx="4" fill="{C["cream"]}" opacity="0">'
            f'<animate attributeName="opacity" values="0;.85;0" dur="1.8s" '
            f'begin="{base + 2.4 + (k * 0.37) % 4:.2f}s" repeatCount="indefinite"/></rect>')
    b.append(dual(sweep + "".join(tw_cells), ""))
    lc = last - start
    col, row = lc.days // 7, lc.days % 7
    px, py = left + col * pitch + cell / 2, top + row * pitch + cell / 2
    pulse = (f'<rect x="{px - cell / 2 - 2:g}" y="{py - cell / 2 - 2:g}" width="{cell + 4}" height="{cell + 4}" '
             f'rx="4.5" fill="none" stroke="{C["ink"]}" stroke-width="2" opacity="0"><animate '
             f'attributeName="opacity" values="1;.1;1" dur="2.4s" begin="{base + 2.2:.2f}s" '
             f'repeatCount="indefinite"/></rect>')
    b.append(dual(pulse, ""))
    ly = top + 7 * pitch + 24
    more_x = W - 34 - tw("More", 12)
    lx = more_x - 10 - (4 * 17 + 12)
    b.append(txt(lx - 8, ly + 10, "Less", 12, "fb", C["muted"], "end", base + 0.6))
    b.append(f'<g{A("", base + 0.6)}>' + "".join(
        f'<rect class="l{i}" x="{lx + i * 17}" y="{ly}" width="12" height="12" rx="3"/>'
        for i in range(5)) + "</g>")
    b.append(txt(more_x, ly + 10, "More", 12, "fb", C["muted"], d=base + 0.6))
    css_levels = "".join(f".l{i}{{fill:{LEVELS[i]}}}" for i in range(5))
    body = f"<style>{css_levels}</style>" + "".join(b)
    defs = (f'<linearGradient id="shine" x1="0" x2="1" y1="0" y2="0">'
            f'<stop offset="0" stop-color="{C["cream"]}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{C["cream"]}" stop-opacity=".7"/>'
            f'<stop offset="1" stop-color="{C["cream"]}" stop-opacity="0"/></linearGradient>'
            f'<clipPath id="gclip"><rect x="{left - 6}" y="{top - 4}" width="{53 * pitch + 6}" '
            f'height="{7 * pitch + 8}"/></clipPath>')
    return svg_doc(W, H, body, "Contribution graph",
                   f"Contribution graph for the last year: {st['total']:,} contributions.", defs)


def card_activity(st, base):
    W, H = 900, 392
    b = [sticker(W, H, C["cream"])]
    b.append(txt(34, 64, "my year, month by month", 40, "fh", C["blue"], d=base))
    big = f"{st['total']:,}"
    b.append(txt(34, 118, big, 46, "fx", d=base + 0.1))
    b.append(txt(34 + tw(big, 46, "fx") + 14, 118, "contributions in the last 12 months", 16, "fb",
                 C["muted"], d=base + 0.2))
    x0, slot, bw = 38, 560 / 12, 30
    ybase = 340
    ph = ybase - 168 - 18
    vmax = max(max(st["per_month"]), 1)
    peak = st["per_month"].index(max(st["per_month"]))
    for frac in (0.5, 1.0):
        gy = ybase - ph * frac
        b.append(f'<line x1="{x0}" x2="{x0 + 560}" y1="{gy:.1f}" y2="{gy:.1f}" '
                 f'stroke="{C["ink"]}" stroke-opacity=".18" stroke-width="2" stroke-dasharray="2 7" '
                 f'stroke-linecap="round"/>')
    b.append(f'<line x1="{x0}" x2="{x0 + 560}" y1="{ybase}" y2="{ybase}" stroke="{C["ink"]}" '
             f'stroke-width="3" stroke-linecap="round"/>')
    mot, still = [], []
    for i, v in enumerate(st["per_month"]):
        h = max(v / vmax * ph, 3 if v else 0)
        x = x0 + slot * i + (slot - bw) / 2
        y = ybase - h
        fill = C["pink"] if i == peak else C["blue"]
        dly = base + 0.35 + i * 0.07
        bar = f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw}" height="{h:.1f}" rx="8" fill="{fill}"/>'
        still.append(bar)
        ease = 'calcMode="spline" keyTimes="0;1" keySplines=".2 .7 .2 1" fill="freeze"'
        mot.append(f'<rect x="{x:.1f}" y="{ybase}" width="{bw}" height="0" rx="8" fill="{fill}">'
                   f'<animate attributeName="height" from="0" to="{h:.1f}" dur=".8s" begin="{dly:.2f}s" {ease}/>'
                   f'<animate attributeName="y" from="{ybase}" to="{y:.1f}" dur=".8s" begin="{dly:.2f}s" {ease}/></rect>')
        cls = "fx" if i == peak else "fb"
        col = C["ink"] if i == peak else C["muted"]
        mot.append(txt(x + bw / 2, y - 8, f"{v:,}", 13, cls, col, "middle", dly + 0.5))
        still.append(txt(x + bw / 2, y - 8, f"{v:,}", 13, cls, col, "middle"))
        b.append(txt(x + bw / 2, ybase + 26, date(*st["months"][i], 1).strftime("%b"), 13, "fb",
                     C["muted"], "middle", base + 0.3 + i * 0.04))
    b.append(dual("".join(mot), "".join(still)))
    b.append(f'<line x1="630" x2="630" y1="150" y2="356" stroke="{C["ink"]}" stroke-opacity=".2" '
             f'stroke-width="2" stroke-dasharray="2 7" stroke-linecap="round"/>')
    blocks = [
        ("CURRENT STREAK", str(st["streak"]), "days", f"longest run: {st['longest']} days", "yellow"),
        ("ACTIVE DAYS", str(st["active"]), "of 365", f"{round(100 * st['active'] / 365)}% of the year", "mint"),
        ("BUSIEST DAY", f"{st['busiest_n']:,}", "contributions", fmt_date(st["busiest"]), "pink"),
    ]
    for i, (lab, val, unit, sub, col) in enumerate(blocks):
        y = 140 + i * 78
        d = base + 0.6 + i * 0.18
        g, _ = pill(660, y, lab, C[col], 11, d=d, pad=12, h=22, ls=1.2)
        b.append(g)
        b.append(txt(662, y + 52, val, 34, "fx", d=d + 0.08))
        b.append(txt(662 + tw(val, 34, "fx") + 8, y + 52, unit, 15, "fb", C["muted"], d=d + 0.12))
        b.append(txt(662, y + 69, sub, 13, "fb", C["muted"], d=d + 0.16))
    return svg_doc(W, H, "".join(b), "Contributions per month",
                   f"{st['total']:,} contributions in the last 12 months. Current streak "
                   f"{st['streak']} days, {st['active']} active days, busiest day "
                   f"{fmt_date(st['busiest'])} with {st['busiest_n']}.")


def card_badge(spec, big, base):
    key, label, _, colname, _ = spec
    W, H = 290, 128
    fill = C[colname]
    tcol = C["cream"] if colname == "blue" else C["ink"]
    b = [sticker(W, H, fill, r=24)]
    b.append(txt(28, 48, label, 14, "fx", tcol, ls=3, d=base + 0.1))
    size = fit(big, 28, W - 9 - 56 - 10)
    b.append(txt(28, 94, big, size, "fx", tcol, d=base + 0.2))
    bx, by = W - 7 - 46, 20
    b.append(f'<g{A("", base, "pop")}><circle cx="{bx + 14}" cy="{by + 20}" r="20" fill="{C["cream"]}" '
             f'stroke="{C["ink"]}" stroke-width="2.5"/>{arrow(bx + 6, by + 12, C["ink"], 16)}</g>')
    return svg_doc(W, H, "".join(b), f"{label}: {big}", f"{label}: {big}")


def card_title(text, base, key):
    W, H = 900, 84
    size = 46
    w = tw(text, size, "fh") + 56
    b = [f'<g{A("", base, "pop")}>'
         f'<rect x="8" y="12" width="{w:.1f}" height="60" rx="30" fill="{C["ink"]}"/>'
         f'<rect x="2" y="6" width="{w:.1f}" height="60" rx="30" fill="{C["cream"]}" '
         f'stroke="{C["ink"]}" stroke-width="3"/></g>',
         txt(30, 50, text, size, "fh", C["blue"], d=base + 0.1)]
    m, s_ = sparkle(w + 36, 30, 16, C["yellow"], base)
    b.append(dual(m, s_))
    return svg_doc(W, H, "".join(b), text, text)


def rel_time(iso):
    try:
        t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return ""
    days = (datetime.now(timezone.utc) - t).days
    if days < 1:
        return "today"
    if days < 30:
        return f"{days}d ago"
    if days < 365:
        return f"{days // 30}mo ago"
    return f"{days // 365}y ago"


def card_project(p, meta, base):
    W, H = 290, 218
    band = C[p["band"]]
    tcol = C["cream"] if p["band"] == "blue" else C["ink"]
    lang = meta.get("language") or p.get("lang")
    stars = int(meta.get("stargazers_count") or 0)
    defs = f'<clipPath id="cp"><rect x="2" y="2" width="{W - 9}" height="{H - 9}" rx="24"/></clipPath>'
    b = [f'<rect x="8" y="8" width="{W - 9}" height="{H - 9}" rx="24" fill="{C["ink"]}"/>',
         f'<rect x="2" y="2" width="{W - 9}" height="{H - 9}" rx="24" fill="{C["cream"]}"/>',
         f'<g clip-path="url(#cp)"><rect x="2" y="2" width="{W - 9}" height="84" fill="{band}"{A("", base, "grow")}/></g>',
         f'<path d="M2 86H{W - 7}" stroke="{C["ink"]}" stroke-width="3"/>',
         f'<rect x="2" y="2" width="{W - 9}" height="{H - 9}" rx="24" fill="none" stroke="{C["ink"]}" stroke-width="3"/>']
    b.append(txt(26, 64, p["name"], fit(p["name"], 34, 160), "fx", tcol, d=base + 0.1))
    if lang:
        g, w = pill(0, 0, lang, C["cream"], 12, pad=10, h=26)
        px = W - 7 - 18 - w
        b.append(f'<g transform="translate({px:.1f} 22)"{A("", base + 0.2)}>{g}</g>' if not STATIC
                 else f'<g transform="translate({px:.1f} 22)">{g}</g>')
    for i, ln in enumerate(wrap(p["desc"], 15, "fb", W - 7 - 26 - 22, 4)):
        b.append(txt(26, 118 + i * 21, ln, 15, "fb", C["ink"], d=base + 0.3 + i * 0.06))
    if stars:
        b.append(f'<g{A("", base + 0.5)}><polygon points="{star_points(36, H - 33, 9)}" fill="{C["yellow"]}" '
                 f'stroke="{C["ink"]}" stroke-width="1.8" stroke-linejoin="round"/>'
                 + txt(52, H - 27, str(stars), 15, "fx") + "</g>")
    bx, by = W - 7 - 24 - 34, H - 7 - 18 - 34
    b.append(f'<g{A("", base + 0.5, "pop")}><circle cx="{bx + 17}" cy="{by + 17}" r="17" fill="{band}" '
             f'stroke="{C["ink"]}" stroke-width="2.5"/>{arrow(bx + 10, by + 10, tcol, 14, 2.4)}</g>')
    return svg_doc(W, H, "".join(b), p["name"], f"{p['name']}: {p['desc']}", defs)


def card_small(name, meta, shadow, base):
    W, H = 290, 140
    desc = meta.get("description") or ""
    lang = meta.get("language")
    stars = int(meta.get("stargazers_count") or 0)
    upd = rel_time(meta.get("pushed_at"))
    b = [sticker(W, H, C["cream"], C[shadow], 20)]
    b.append(txt(24, 44, name, fit(name, 21, W - 7 - 24 - 56), "fx", d=base))
    b.append(f'<g{A("", base + 0.15)}>{arrow(W - 7 - 38, 24, C["ink"], 14, 2.4)}</g>')
    for i, ln in enumerate(wrap(desc, 13.5, "fb", W - 7 - 24 - 20, 2)):
        b.append(txt(24, 68 + i * 18, ln, 13.5, "fb", C["muted"], d=base + 0.25 + i * 0.05))
    foot = []
    x = 24
    if lang:
        foot.append(f'<circle cx="{x + 6}" cy="{H - 31}" r="6" fill="{LANG_COLOR.get(lang, C["blue"])}" '
                    f'stroke="{C["ink"]}" stroke-width="1.8"/>')
        foot.append(txt(x + 18, H - 26, lang, 13, "fx"))
        x += 18 + tw(lang, 13, "fx") + 16
    if stars:
        foot.append(f'<polygon points="{star_points(x + 7, H - 31, 8)}" fill="{C["yellow"]}" '
                    f'stroke="{C["ink"]}" stroke-width="1.6" stroke-linejoin="round"/>')
        foot.append(txt(x + 20, H - 26, str(stars), 13, "fx"))
    if upd:
        foot.append(txt(W - 7 - 20, H - 26, upd, 12, "fb", C["muted"], "end"))
    b.append(f'<g{A("", base + 0.4)}>{"".join(foot)}</g>')
    return svg_doc(W, H, "".join(b), name, f"{name}: {desc}" if desc else name)


# ------------------------------------------------------------------- main --
def preview_html():
    readme = (ROOT / "README.md").read_text(encoding="utf-8").replace("cards/", "./")
    return ("<!doctype html><meta charset=utf-8><title>README preview (STATIC)</title>"
            "<body style='margin:0;background:#0d1117;display:flex;justify-content:center'>"
            "<div style='width:830px;padding:24px 0;color:#c9d1d9;"
            "font:16px -apple-system,Segoe UI,sans-serif'>" + readme + "</div>")


def main():
    by_day = load_contribs()
    st = stats(by_day)
    repos_meta = load_json(DATA / "repos.json", required=False)
    profile = load_json(DATA / "profile.json", required=False)
    featured_file = ROOT / "data" / "featured.txt"  # config, not refreshed data
    featured = [ln.strip() for ln in featured_file.read_text().splitlines() if ln.strip()]
    big_repos = {p.get("repo") or p["key"] for p in PROJECTS}
    small = [r for r in featured if r not in big_repos]
    OUT.mkdir(parents=True, exist_ok=True)
    written = {}

    # staggered start times so the page plays top to bottom
    t_graph, t_act, t_badge = 1.1, 2.0, 3.0
    t_title1, t_proj = 3.6, 3.9
    t_title2 = t_proj + 0.2 * len(PROJECTS) + 0.7
    t_small = t_title2 + 0.3

    written["hero.svg"] = card_hero(0.0)
    written["graph.svg"] = card_graph(by_day, st, t_graph)
    written["activity.svg"] = card_activity(st, t_act)
    repos_n = profile.get("public_repos")
    for i, spec in enumerate(BADGES):
        big = spec[2].format(repos=repos_n if repos_n else "open source",
                             contribs=f"{st['total']:,}")
        if spec[0] == "build" and not repos_n:
            big = "open source"
        written[f"badge-{spec[0]}.svg"] = card_badge(spec, big, t_badge + i * 0.15)
    written["title-coding.svg"] = card_title(TITLE_BIG, t_title1, "coding")
    for i, p in enumerate(PROJECTS):
        meta = repos_meta.get(p.get("repo") or p["key"], {})
        written[f"project-{p['key']}.svg"] = card_project(p, meta, t_proj + i * 0.2)
    written["title-small.svg"] = card_title(TITLE_SMALL, t_title2, "small")
    shadows = ["blue", "pink", "yellow", "mint"]
    for i, name in enumerate(small):
        written[f"small-{name}.svg"] = card_small(name, repos_meta.get(name, {}),
                                                  shadows[i % len(shadows)], t_small + i * 0.12)

    for old in OUT.glob("*.svg"):
        if old.name not in written:
            old.unlink()
    for fname, content in written.items():
        (OUT / fname).write_text(content, encoding="utf-8")
        print(f"{fname:34s}{len(content) / 1024:7.1f} KB")
    if STATIC:
        (OUT / "preview.html").write_text(preview_html(), encoding="utf-8")
        print(f"preview: {OUT / 'preview.html'}")
    print(f"mode={'STATIC' if STATIC else 'animated'} out={OUT}")


if __name__ == "__main__":
    sys.exit(main())
