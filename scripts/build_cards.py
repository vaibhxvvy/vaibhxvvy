#!/usr/bin/env python3
"""Render the animated SVG cards used by the profile README.

    python scripts/build_cards.py            # animated cards -> cards/
    STATIC=1 python scripts/build_cards.py   # final frame, no animation
                                             #   -> cards-static/ (+ preview.html)

Inputs (refreshed daily by .github/workflows/cards.yml):
    data/contributions.json   {"contributions": [{"date","count","level"}, ...]}
    data/repos.json           {"<repo>": {"description","language",
                                          "stargazers_count","forks_count","pushed_at"}}
    data/featured.txt         one featured repo name per line (keep README in sync)
Optional:
    assets/portrait.(png|jpg|jpeg|webp)   shown in the hero instead of the monogram

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
import textwrap
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
FOCUS = "MACHINE LEARNING / DATA SCIENCE / LOCAL LLMS & AGENTS"

# (label, big text, url, icon)  -- url is used by README.md, not by the card
TILES = [
    ("portfolio", "PORTFOLIO", "vaibhavsurthi.dev", "globe"),
    ("repos", "REPOSITORIES", "github.com/" + USER, "repo"),
    ("linkedin", "LINKEDIN", "Let's connect", "link"),
]

# Colours and font taken from the previous README; retune here.
C = dict(
    bg="#101010", panel="#14191B", edge="#263B43", text="#F7F4EC",
    muted="#8FA3A8", dim="#5B6E73", accent="#58A6FF",
)
FALLBACK_DESC = {  # used only if repos.json has no entry
    "documentation-pro": "Documentation automation and docs-as-code",
    "fcuk-paywalls": "Directory of accessible, open-source web tools",
    "gridmint": "Development project",
    "dsgnr-cli": "Developer tooling",
    "hydrent": "Rental platform",
}
LANG_COLOR = {
    "Python": "#3572A5", "JavaScript": "#F1E05A", "TypeScript": "#3178C6",
    "Rust": "#DEA584", "HTML": "#E34C26", "CSS": "#563D7C", "Go": "#00ADD8",
    "Shell": "#89E051", "Jupyter Notebook": "#DA5B0B", "C++": "#F34B7D",
}
ADV = 0.6  # JetBrains Mono advance width in em: monospace makes layout exact


def mix(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb))


LEVELS = [mix("#1B2327", C["accent"], t) for t in (0, 0.28, 0.52, 0.76, 1.0)]
LEVELS[0] = "#1B2327"


def tw(s, size):
    """Text width in px (monospace)."""
    return len(s) * ADV * size


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


def txt(x, y, s, size, w=4, fill=None, anchor="start", d=None, ls=0, extra=""):
    fill = fill or C["text"]
    lsp = f' letter-spacing="{ls}"' if ls else ""
    anc = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{fill}"{anc}{lsp}{extra}'
            f'{A(f"w{w}", d)}>{esc(s)}</text>')


def dual(motion, still):
    """SMIL content and its reduced-motion/static twin."""
    if STATIC:
        return still
    return f'<g class="motion">{motion}</g><g class="still">{still}</g>'


def panel(w, h, r=18, fill=None):
    return (f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{r}" '
            f'fill="{fill or C["panel"]}" stroke="{C["edge"]}"/>')


def star_points(cx, cy, r):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.42
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}")
    return " ".join(pts)


# ------------------------------------------------------------------ fonts --
_font_cache = {}


def font_b64(weight, chars):
    key = (weight, chars)
    if key in _font_cache:
        return _font_cache[key]
    src = FONTS / f"jetbrains-mono-latin-{weight}-normal.woff"
    cmap = TTFont(str(src)).getBestCmap()
    missing = sorted(c for c in chars if c != " " and ord(c) not in cmap)
    if missing:
        raise SystemExit(f"font {weight} has no glyph for {missing!r}")
    with tempfile.TemporaryDirectory() as td:
        listing = Path(td) / "chars.txt"
        out = Path(td) / "out.woff"
        listing.write_text(chars, encoding="utf-8")
        subset.main([
            str(src), f"--text-file={listing}", f"--output-file={out}",
            "--flavor=woff", "--layout-features=", "--no-hinting",
            "--desubroutinize", "--drop-tables+=DSIG",
        ])
        b64 = base64.b64encode(out.read_bytes()).decode()
    _font_cache[key] = b64
    return b64


def style_block(body):
    texts = re.findall(r"<text[^>]*>(.*?)</text>", body, re.S)
    chars = "".join(sorted(set(html.unescape(re.sub(r"<[^>]+>", "", "".join(texts))))))
    chars = "".join(sorted(set(chars + " 0123456789")))
    used = sorted({int(m) * 100 for m in re.findall(
        r"\bw([458])\b", " ".join(re.findall(r'class="([^"]*)"', body)))})
    css = []
    for wt in used:
        css.append("@font-face{font-family:'JBM';font-weight:%d;font-style:normal;"
                   "src:url(data:font/woff;base64,%s) format('woff')}" % (wt, font_b64(wt, chars)))
    css.append("text{font-family:'JBM','JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,"
               "Consolas,monospace}.w4{font-weight:400}.w5{font-weight:500}.w8{font-weight:800}")
    if not STATIC:
        css.append(
            ".rise{animation:rise .8s cubic-bezier(.2,.7,.2,1) var(--d,0s) both}"
            "@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}"
            ".pop{transform-box:fill-box;transform-origin:center;"
            "animation:pop .55s cubic-bezier(.2,.8,.3,1) var(--d,0s) both}"
            "@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}"
            ".grow{transform-box:fill-box;transform-origin:50% 0;"
            "animation:grow .8s cubic-bezier(.2,.7,.2,1) var(--d,0s) both}"
            "@keyframes grow{from{transform:scaleY(0)}to{transform:none}}"
            ".draw{stroke-dasharray:1;stroke-dashoffset:0;"
            "animation:draw .9s cubic-bezier(.2,.7,.2,1) var(--d,0s) both}"
            "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
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
            raise SystemExit(f"missing {path} - run the 'Profile cards' workflow first")
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
    W, H = 900, 280
    cx, cy = 770, 140
    portrait = next((p for e in ("png", "jpg", "jpeg", "webp")
                     if (p := ROOT / "assets" / f"portrait.{e}").exists()), None)
    defs = (f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{C["bg"]}"/><stop offset="1" stop-color="{C["edge"]}"/>'
            f'</linearGradient>'
            f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
            f'<circle cx="1.5" cy="1.5" r="1" fill="{C["muted"]}" fill-opacity=".28"/></pattern>'
            f'<clipPath id="pc"><circle cx="{cx}" cy="{cy}" r="58"/></clipPath>')
    b = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="url(#g)" '
         f'stroke="{C["edge"]}"/>',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="url(#dots)"/>']
    b.append(txt(56, 66, "@" + USER, 13, 5, C["accent"], ls=2, d=base + 0.1))
    b.append(txt(56, 148, NAME, 58, 8, d=base + 0.25))
    b.append(txt(56, 192, TAGLINE, 19, 4, C["text"], d=base + 0.55))
    cur_x = 56 + tw(TAGLINE, 19) + 6
    cursor = (f'<rect x="{cur_x:.1f}" y="176" width="10" height="20" fill="{C["accent"]}" opacity="0">'
              f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" '
              f'dur="1.1s" begin="{base + 1.2:.2f}s" repeatCount="indefinite"/></rect>')
    b.append(dual(cursor, ""))
    b.append(txt(56, 236, FOCUS, 13, 5, C["accent"], ls=1, d=base + 0.8))
    rings = []
    for i, r in enumerate((92, 76)):
        rings.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{C["edge"]}" '
                     f'stroke-width="1.5"{A("", base + 0.3 + i * 0.12, "pop")}/>')
    b.append("".join(rings))
    ripple = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="60" fill="none" stroke="{C["accent"]}" stroke-width="1.5" opacity="0">'
        f'<animate attributeName="r" values="60;98" dur="4s" begin="{base + 1 + k * 1.33:.2f}s" '
        f'repeatCount="indefinite"/><animate attributeName="opacity" values=".55;0" dur="4s" '
        f'begin="{base + 1 + k * 1.33:.2f}s" repeatCount="indefinite"/></circle>' for k in range(3))
    b.append(dual(ripple, ""))
    if portrait:
        mime = {"jpg": "jpeg"}.get(portrait.suffix[1:], portrait.suffix[1:])
        uri = f"data:image/{mime};base64," + base64.b64encode(portrait.read_bytes()).decode()
        b.append(f'<g{A("", base + 0.4, "pop")}><circle cx="{cx}" cy="{cy}" r="60" '
                 f'fill="{C["panel"]}"/><image href="{uri}" x="{cx - 58}" y="{cy - 58}" '
                 f'width="116" height="116" preserveAspectRatio="xMidYMid slice" '
                 f'clip-path="url(#pc)"/><circle cx="{cx}" cy="{cy}" r="59" fill="none" '
                 f'stroke="{C["accent"]}" stroke-width="2"/></g>')
    else:
        b.append(f'<g{A("", base + 0.4, "pop")}><circle cx="{cx}" cy="{cy}" r="58" '
                 f'fill="{C["panel"]}" stroke="{C["accent"]}" stroke-width="2"/></g>')
        b.append(txt(cx, cy + 14, "VS", 40, 8, C["text"], "middle", base + 0.55))
    return svg_doc(W, H, "".join(b), f"{NAME} - GitHub profile",
                   f"{NAME}. {TAGLINE}", defs)


def icon(kind, x, y, color):
    s = f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "globe":
        return (f'<g {s}><circle cx="{x + 14}" cy="{y + 14}" r="13"/>'
                f'<ellipse cx="{x + 14}" cy="{y + 14}" rx="5.5" ry="13"/>'
                f'<path d="M{x + 1} {y + 14}H{x + 27}"/></g>')
    if kind == "repo":
        return (f'<g {s}><rect x="{x + 3}" y="{y + 1}" width="22" height="26" rx="3"/>'
                f'<path d="M{x + 9} {y + 8}H{x + 19}M{x + 9} {y + 14}H{x + 19}"/></g>')
    return (f'<g {s}><path d="M{x + 12} {y + 17}a6 6 0 0 0 8.5 0l4-4a6 6 0 0 0-8.5-8.5l-1.5 1.5"/>'
            f'<path d="M{x + 16} {y + 11}a6 6 0 0 0-8.5 0l-4 4a6 6 0 0 0 8.5 8.5l1.5-1.5"/></g>')


def card_tile(spec, base):
    _, label, value, ic = spec
    W, H = 290, 120
    b = [panel(W, H, 16)]
    b.append(f'<g{A("", base, "pop")}>{icon(ic, 24, 24, C["accent"])}</g>')
    b.append(txt(24, 84, label, 12, 5, C["muted"], ls=2, d=base + 0.15))
    fs = 16 if tw(value, 16) <= W - 48 - 30 else 13
    b.append(txt(24, 106, value, fs, 8, C["text"], d=base + 0.25))
    ax, ay = W - 38, 30
    arrow = (f'<g fill="none" stroke="{C["accent"]}" stroke-width="2.2" stroke-linecap="round" '
             f'stroke-linejoin="round"><path d="M{ax} {ay + 14}L{ax + 14} {ay}M{ax + 3} {ay}'
             f'H{ax + 14}V{ay + 11}"/></g>')
    b.append(f'<g{A("", base + 0.3)}>{arrow}</g>')
    b.append(f'<path d="M24 62H{W - 24}" stroke="{C["edge"]}" stroke-width="1" pathLength="1"'
             f'{A("", base + 0.2, "draw")}/>')
    return svg_doc(W, H, "".join(b), f"{label.title()} link", f"{label.title()}: {value}")


def card_activity(st, base):
    W, H = 900, 380
    b = [panel(W, H)]
    b.append(txt(40, 52, "CONTRIBUTIONS", 13, 5, C["accent"], ls=2, d=base))
    big = f"{st['total']:,}"
    b.append(txt(40, 98, big, 40, 8, d=base + 0.1))
    b.append(txt(40 + tw(big, 40) + 14, 98, "in the last 12 months", 14, 4, C["muted"], d=base + 0.2))
    x0, slot, bw = 40, 560 / 12, 28
    ybase, ptop = 332, 148
    ph = ybase - ptop - 18
    vmax = max(max(st["per_month"]), 1)
    peak = st["per_month"].index(max(st["per_month"]))
    for frac in (0.5, 1.0):
        gy = ybase - ph * frac
        b.append(f'<line x1="{x0}" x2="{x0 + 560}" y1="{gy:.1f}" y2="{gy:.1f}" '
                 f'stroke="{C["edge"]}" stroke-dasharray="3 5" opacity=".6"/>')
    b.append(f'<line x1="{x0}" x2="{x0 + 560}" y1="{ybase}" y2="{ybase}" stroke="{C["edge"]}"/>')
    mot, still = [], []
    for i, v in enumerate(st["per_month"]):
        h = max(v / vmax * ph, 2 if v else 0)
        x = x0 + slot * i + (slot - bw) / 2
        y = ybase - h
        fill = C["accent"] if i == peak else mix(C["edge"], C["accent"], 0.55)
        dly = base + 0.35 + i * 0.07
        still.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw}" height="{h:.1f}" rx="4" fill="{fill}"/>')
        ease = 'calcMode="spline" keyTimes="0;1" keySplines=".2 .7 .2 1" fill="freeze"'
        mot.append(f'<rect x="{x:.1f}" y="{ybase}" width="{bw}" height="0" rx="4" fill="{fill}">'
                   f'<animate attributeName="height" from="0" to="{h:.1f}" dur=".8s" begin="{dly:.2f}s" {ease}/>'
                   f'<animate attributeName="y" from="{ybase}" to="{y:.1f}" dur=".8s" begin="{dly:.2f}s" {ease}/></rect>')
        lab = txt(x + bw / 2, y - 7, f"{v:,}", 11, 5 if i == peak else 4,
                  C["text"] if i == peak else C["muted"], "middle", dly + 0.5)
        mot.append(lab)
        still.append(txt(x + bw / 2, y - 7, f"{v:,}", 11, 5 if i == peak else 4,
                         C["text"] if i == peak else C["muted"], "middle"))
        b.append(txt(x + bw / 2, ybase + 22, date(*st["months"][i], 1).strftime("%b"), 11, 4,
                     C["muted"], "middle", base + 0.3 + i * 0.04))
    b.append(dual("".join(mot), "".join(still)))
    b.append(f'<line x1="624" x2="624" y1="132" y2="350" stroke="{C["edge"]}"/>')
    blocks = [
        ("CURRENT STREAK", str(st["streak"]), "days", f"longest: {st['longest']} days"),
        ("ACTIVE DAYS", str(st["active"]), "/ 365",
         f"{round(100 * st['active'] / 365)}% of the last year"),
        ("BUSIEST DAY", f"{st['busiest_n']:,}", "contributions", fmt_date(st["busiest"])),
    ]
    for i, (lab, val, unit, sub) in enumerate(blocks):
        y = 156 + i * 78
        d = base + 0.6 + i * 0.18
        b.append(txt(656, y, lab, 11, 5, C["muted"], ls=1.5, d=d))
        b.append(txt(656, y + 32, val, 30, 8, C["accent"] if i == 0 else C["text"], d=d + 0.08))
        b.append(txt(656 + tw(val, 30) + 8, y + 32, unit, 13, 4, C["muted"], d=d + 0.12))
        b.append(txt(656, y + 52, sub, 12, 4, C["dim"], d=d + 0.16))
    return svg_doc(W, H, "".join(b), "Contributions per month",
                   f"{st['total']:,} contributions in the last 12 months. Current streak "
                   f"{st['streak']} days, {st['active']} active days, busiest day "
                   f"{fmt_date(st['busiest'])} with {st['busiest_n']}.")


def rel_time(iso):
    try:
        t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return ""
    days = (datetime.now(timezone.utc) - t).days
    if days < 1:
        return "updated today"
    if days < 30:
        return f"updated {days}d ago"
    if days < 365:
        return f"updated {days // 30}mo ago"
    return f"updated {days // 365}y ago"


def card_repo(name, meta, base):
    desc = meta.get("description") or FALLBACK_DESC.get(name, "")
    lines = textwrap.wrap(desc, 94) or [""]
    if len(lines) > 2:
        lines = [lines[0], lines[1][:91].rstrip() + "..."]
    W, H = 900, 132 + 20 * (len(lines) - 1)
    b = [panel(W, H, 16)]
    b.append(f'<rect x="0.5" y="22" width="4" height="{H - 44}" rx="2" fill="{C["accent"]}"{A("", base, "grow")}/>')
    b.append(f'<g{A("", base + 0.1)}><g fill="none" stroke="{C["accent"]}" stroke-width="2" '
             f'stroke-linejoin="round"><rect x="40" y="28" width="16" height="20" rx="2.5"/>'
             f'<path d="M45 35H51M45 41H51"/></g></g>')
    b.append(txt(70, 44, name, 22, 8, d=base + 0.15))
    ax, ay = W - 52, 28
    b.append(f'<g{A("", base + 0.25)}><path d="M{ax} {ay + 14}L{ax + 14} {ay}M{ax + 3} {ay}H{ax + 14}'
             f'V{ay + 11}" fill="none" stroke="{C["muted"]}" stroke-width="2" stroke-linecap="round" '
             f'stroke-linejoin="round"/></g>')
    for i, ln in enumerate(lines):
        b.append(txt(40, 76 + i * 20, ln, 14, 4, C["muted"], d=base + 0.3 + i * 0.05))
    fy = 76 + (len(lines) - 1) * 20 + 30
    x = 40
    foot = []
    lang = meta.get("language")
    if lang:
        foot.append(f'<circle cx="{x + 5}" cy="{fy - 4}" r="5" fill="{LANG_COLOR.get(lang, C["accent"])}"/>')
        foot.append(txt(x + 18, fy, lang, 12, 5, C["muted"]))
        x += 18 + tw(lang, 12) + 24
    stars, forks = int(meta.get("stargazers_count") or 0), int(meta.get("forks_count") or 0)
    if stars:
        foot.append(f'<polygon points="{star_points(x + 6, fy - 4.5, 7)}" fill="{C["muted"]}"/>')
        foot.append(txt(x + 18, fy, str(stars), 12, 5, C["muted"]))
        x += 18 + tw(str(stars), 12) + 24
    if forks:
        foot.append(f'<g fill="none" stroke="{C["muted"]}" stroke-width="1.6"><circle cx="{x + 2}" '
                    f'cy="{fy - 12}" r="2.2"/><circle cx="{x + 10}" cy="{fy - 12}" r="2.2"/>'
                    f'<circle cx="{x + 6}" cy="{fy - 1}" r="2.2"/><path d="M{x + 2} {fy - 10}v2.5q0 2 '
                    f'4 2q4 0 4-2v-2.5M{x + 6} {fy - 6.5}v3.3"/></g>')
        foot.append(txt(x + 18, fy, str(forks), 12, 5, C["muted"]))
    b.append(f'<g{A("", base + 0.45)}>{"".join(foot)}</g>')
    upd = rel_time(meta.get("pushed_at"))
    if upd:
        b.append(txt(W - 40, fy, upd, 12, 4, C["dim"], "end", base + 0.5))
    return svg_doc(W, H, "".join(b), f"{USER}/{name}", f"{name}: {desc}")


def card_graph(by_day, st, base):
    W, H = 900, 262
    last = st["last"]
    last_sun = last - timedelta(days=(last.weekday() + 1) % 7)
    start = last_sun - timedelta(weeks=52)
    maxc = max(c for c, _ in by_day.values())
    left, top, pitch, cell = 60, 96, 15, 12
    b = [panel(W, H)]
    b.append(txt(40, 52, "CONTRIBUTION GRAPH", 13, 5, C["accent"], ls=2, d=base))
    b.append(txt(W - 40, 52, f"{st['total']:,} in the last year", 13, 4, C["muted"], "end", base + 0.1))
    prev = None
    for col in range(53):
        d0 = start + timedelta(weeks=col)
        if d0.month != prev and not (col == 0 and (start + timedelta(weeks=2)).month != d0.month):
            if col <= 50:
                b.append(txt(left + col * pitch, 84, d0.strftime("%b"), 10, 4, C["muted"], d=base + 0.15))
        prev = d0.month
    for row, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        b.append(txt(24, top + row * pitch + 10, lab, 10, 4, C["muted"], d=base + 0.15))
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
                         f'width="{cell}" height="{cell}" rx="2.5"{sty}/>')
    b.append("".join(cells))
    lc = last - start
    col, row = lc.days // 7, lc.days % 7
    px, py = left + col * pitch + cell / 2, top + row * pitch + cell / 2
    pulse = (f'<rect x="{px - cell / 2 - 1.5}" y="{py - cell / 2 - 1.5}" width="{cell + 3}" height="{cell + 3}" '
             f'rx="3.5" fill="none" stroke="{C["text"]}" stroke-width="1.5" opacity="0"><animate attributeName="opacity" '
             f'values="1;.15;1" dur="2.4s" begin="{base + 2.2:.2f}s" repeatCount="indefinite"/></rect>')
    b.append(dual(pulse, ""))
    ly = top + 7 * pitch + 24
    more_x = W - 40 - tw("More", 10)
    lx = more_x - 8 - (4 * 17 + 12)
    b.append(txt(lx - 8, ly + 9, "Less", 10, 4, C["muted"], "end", base + 0.6))
    b.append(f'<g{A("", base + 0.6)}>' + "".join(
        f'<rect class="l{i}" x="{lx + i * 17}" y="{ly}" width="12" height="12" rx="2.5"/>'
        for i in range(5)) + "</g>")
    b.append(txt(more_x, ly + 9, "More", 10, 4, C["muted"], d=base + 0.6))
    css_levels = "".join(f".l{i}{{fill:{LEVELS[i]}}}" for i in range(5))
    body = f"<style>{css_levels}</style>" + "".join(b)
    return svg_doc(W, H, body, "Contribution graph",
                   f"Contribution graph for the last year: {st['total']:,} contributions.")


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
    featured_file = ROOT / "data" / "featured.txt"  # config, not refreshed data
    featured = [ln.strip() for ln in featured_file.read_text().splitlines() if ln.strip()]
    OUT.mkdir(parents=True, exist_ok=True)
    written = {}

    # staggered start times so the page plays top to bottom
    t_tiles, t_act = 0.9, 1.5
    t_repos = 2.1
    t_graph = t_repos + 0.3 * len(featured) + 0.3

    written["hero.svg"] = card_hero(0.0)
    for i, spec in enumerate(TILES):
        written[f"tile-{spec[0]}.svg"] = card_tile(spec, t_tiles + i * 0.15)
    written["activity.svg"] = card_activity(st, t_act)
    for i, name in enumerate(featured):
        written[f"repo-{name}.svg"] = card_repo(name, repos_meta.get(name, {}), t_repos + i * 0.3)
    written["graph.svg"] = card_graph(by_day, st, t_graph)

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
