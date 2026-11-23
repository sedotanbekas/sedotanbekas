#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sedotanbekas · profile lab
==========================
Generates every SVG in ./assets from live GitHub data. No third-party stats
services and no dependencies: Python 3.9+ standard library only.

    python scripts/build.py                            # live (uses $GH_TOKEN / $GITHUB_TOKEN if set)
    python scripts/build.py --snapshot data/snap.json  # offline, from a saved snapshot
    python scripts/build.py --save-snapshot data/snap.json

Edit the CONFIG block to change the copy, featured repos or tools.
"""
import argparse
import base64
import datetime as dt
import hashlib
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"

# ─────────────────────────────── CONFIG ───────────────────────────────
USER = "sedotanbekas"
NAME_FIRST, NAME_LAST = "Rafif Nuraydin", "Adipratama"
ROLE = "Software Engineer · PT Medialab Indonesia"
ORIGIN = "Informatics Eng. · Politeknik Negeri Jakarta"
TZ = ZoneInfo("Asia/Jakarta")
TAGLINES = [
    "builds the LIMS. then tries to break it.",
    "Next.js · Prisma · MariaDB · Nginx · PM2",
    "Bangkit Academy 2024 · Mobile Development",
    "sedotan bekas = a used straw. still sipping.",
]
FEATURED = [  # (repo, short code, description) — description wraps to 2 lines
    ("medialabindonesia/lims-medialab", "LIMS",
     "Laboratory Information Management System for PT Medialab Indonesia's testing lab."),
    ("sedotanbekas/ml-assist", "ASSIST",
     "MediaLab Assist: a TypeScript web helper for day-to-day work at Medialab."),
    ("sedotanbekas/umkm-ez-tax", "BANGKIT",
     "Bangkit Academy 2024 capstone (mobile side): tax made easy for Indonesian UMKM."),
    ("sedotanbekas/sentiment-analysis-web", "NLP",
     "Sentiment analysis in the browser: text in, mood out."),
]
EXTRA_LANG_REPOS = ["medialabindonesia/lims-medialab"]  # counted in the periodic table too
EXCLUDE_LANGS = {"HTML", "TeX", "Jupyter Notebook", "Standard ML", "Makefile"}
MERGE_LANGS = {"SCSS": "CSS", "Less": "CSS", "Sass": "CSS"}
MAX_ELEMENTS = 8
TOOLS = [("Nx", "Next.js"), ("Pr", "Prisma"), ("Mb", "MariaDB"), ("Ng", "Nginx"), ("P2", "PM2"),
         ("Ub", "Ubuntu"), ("Dk", "Docker"), ("Ga", "GH Actions"), ("Cc", "Claude Code")]
SYMBOLS = {"TypeScript": "Ts", "JavaScript": "Js", "Vue": "Vu", "CSS": "Cs", "Go": "Go", "Python": "Py",
           "Kotlin": "Kt", "Java": "Jv", "Shell": "Sh", "Dockerfile": "Df", "PHP": "Ph", "Dart": "Dt",
           "C": "C", "C++": "Cp", "C#": "Cs", "Rust": "Rs", "Swift": "Sw", "Ruby": "Rb", "Svelte": "Sv",
           "PowerShell": "Ps", "Blade": "Bl", "Astro": "As", "Lua": "Lu", "R": "R"}
CHROMA_DAYS = 120

# ─────────────────────────────── PALETTE ──────────────────────────────
PAPER, PAPER2 = "#F3E9D2", "#E9DCBD"
INK, MUTE, LINE = "#1C1714", "#76624E", "#CBB48C"
RED, RED_D = "#D2452F", "#9C2E1F"

MON_ID = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
MON_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

# ─────────────────────────────── DATA ─────────────────────────────────
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


def _get(url, accept="application/vnd.github+json", data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": f"{USER}-profile-lab", "Accept": accept})
    if TOKEN and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def api(path):
    return json.loads(_get("https://api.github.com/" + path.lstrip("/")))


def contributions_scrape():
    """The public contributions calendar, exactly as the profile shows it (incl. private counts if enabled)."""
    html = _get(f"https://github.com/users/{USER}/contributions", accept="text/html")
    tips = {m.group(1): m.group(2).strip() for m in re.finditer(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', html)}
    days = []
    for tag in re.findall(r"<td\b[^>]*ContributionCalendar-day[^>]*>", html):
        date, cid = re.search(r'data-date="([\d-]+)"', tag), re.search(r'\bid="([^"]+)"', tag)
        if not date:
            continue
        m = re.match(r"(No|[\d,]+) contribution", tips.get(cid.group(1) if cid else "", ""))
        days.append({"date": date.group(1), "count": 0 if not m or m.group(1) == "No" else int(m.group(1).replace(",", ""))})
    if len(days) < 300:
        raise RuntimeError("calendar parse failed")
    return sorted(days, key=lambda x: x["date"])


def contributions_graphql():
    q = {"query": "query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}",
         "variables": {"u": USER}}
    res = json.loads(_get("https://api.github.com/graphql", data=json.dumps(q).encode()))
    weeks = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [{"date": d["date"], "count": d["contributionCount"]} for w in weeks for d in w["contributionDays"]]


def fetch_live():
    user = api(f"users/{USER}")
    repos = api(f"users/{USER}/repos?per_page=100&type=owner")
    langs, analyzed = {}, 0
    for full in [r["full_name"] for r in repos if not r["fork"]] + EXTRA_LANG_REPOS:
        try:
            for k, v in api(f"repos/{full}/languages").items():
                langs[k] = langs.get(k, 0) + v
            analyzed += 1
        except urllib.error.HTTPError:
            pass
    featured = {}
    for full, _, _ in FEATURED:
        try:
            r = api(f"repos/{full}")
            featured[full] = {"language": r.get("language"), "pushed_at": r.get("pushed_at"), "homepage": r.get("homepage") or ""}
        except urllib.error.HTTPError:
            featured[full] = {}
    try:
        days = contributions_scrape()
    except Exception as e:  # noqa: BLE001
        print("scrape failed, falling back to GraphQL:", e, file=sys.stderr)
        days = contributions_graphql()
    return {"user": {"created_at": user["created_at"], "public_repos": user["public_repos"], "followers": user["followers"]},
            "days": days, "languages": langs, "repos_analyzed": analyzed, "featured": featured}


# ─────────────────────────────── HELPERS ──────────────────────────────
_M = json.loads((FONTS / "metrics.json").read_text("utf-8"))


def tw(text, size, font="jbm-400"):
    m = _M[font]
    dflt = m["w"].get("n", m["upm"] * 0.55)
    return sum(m["w"].get(c, dflt) for c in text) * size / m["upm"]


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def num(n):  # SI-style thousands: 2 152
    return f"{n:,}".replace(",", " ")


def dec(x, p=1):  # Indonesian decimal comma: 5,9
    return f"{x:.{p}f}".replace(".", ",")


def fmt_id(d):
    return f"{d.day:02d} {MON_ID[d.month - 1]} {d.year}"


def fmt_en(d):
    return f"{d.day:02d} {MON_EN[d.month - 1]} {d.year}"


def _face(family, file, weight, style):
    b64 = base64.b64encode((FONTS / file).read_bytes()).decode()
    return f"@font-face{{font-family:{family};src:url(data:font/woff2;base64,{b64}) format('woff2');font-weight:{weight};font-style:{style}}}"


def style(extra="", serif=True):
    css = [_face("JB", "jbm-400.woff2", 400, "normal"), _face("JB", "jbm-700.woff2", 700, "normal")]
    if serif:
        css += [_face("IS", "is-400.woff2", 400, "normal"), _face("IS", "is-400i.woff2", 400, "italic")]
    css.append(".m{font-family:JB,ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}"
               ".s{font-family:IS,'Times New Roman',Georgia,serif}.i{font-style:italic}.b{font-weight:700}")
    return "<style>" + "".join(css) + extra + "</style>"


GRAIN = ('<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" '
         'numOctaves="3" seed="11" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 .1  0 0 0 0 .08  0 0 0 0 .06  0 0 0 -1.4 .78"/></filter>')
KEY = (f'<pattern id="key" x="30" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M0 18H20M1.6 18V2H16.4V14.4H5.6V5.6H12.4V10.2H9" '
       f'fill="none" stroke="{RED}" stroke-width="2.1"/></pattern>')


def svg(w, h, body, title, defs="", extra_css="", serif=True):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}"><title>{esc(title)}</title>'
            f'<defs>{style(extra_css, serif)}{GRAIN}{defs}</defs>{body}</svg>')


def paper(w, h, rx=12, cid="card", fill=PAPER):
    return (f'<clipPath id="{cid}"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{rx}"/></clipPath>'
            f'<g clip-path="url(#{cid})"><rect width="{w}" height="{h}" fill="{fill}"/>'
            f'<rect width="{w}" height="{h}" filter="url(#grain)" opacity=".55"/></g>')


def border(w, h, rx=12):
    return f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{rx}" fill="none" stroke="{INK}" stroke-width="1.6"/>'


def key_band(y, x0=30, x1=970):
    return (f'<line x1="{x0}" x2="{x1}" y1="{y - 4}" y2="{y - 4}" stroke="{RED}" stroke-width="1.2"/>'
            f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="20" fill="url(#key)"/>'
            f'<line x1="{x0}" x2="{x1}" y1="{y + 24}" y2="{y + 24}" stroke="{RED}" stroke-width="1.2"/>')


def text(x, y, s, size, cls="m", fill=INK, anchor="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'


def barcode(x, y, w, h, seed, color=INK):
    bits = hashlib.sha256(seed.encode()).digest() * 2
    bars, cx, i = [], 0.0, 0
    unit = w / 120
    while cx < w and i < len(bits):
        bw, gap = (1 + bits[i] % 3) * unit, (1 + (bits[i] >> 3) % 2) * unit
        if cx + bw > w:
            break
        bars.append(f'<rect x="{x + cx:.2f}" y="{y}" width="{bw:.2f}" height="{h}"/>')
        cx += bw + gap
        i += 1
    return f'<g fill="{color}">{"".join(bars)}</g>'


def check(x, y, color=RED):
    return f'<path d="M{x} {y}l4.5 4.5 9-10" fill="none" stroke="{color}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'


def cross(x, y, color=RED):
    return f'<path d="M{x} {y - 5}l9 9m0-9-9 9" fill="none" stroke="{color}" stroke-width="2.4" stroke-linecap="round"/>'


# ─────────────────────────────── ANALYSIS ─────────────────────────────
def analyze(d, now):
    days = [x for x in d["days"] if x["date"] <= now.date().isoformat()]
    counts = [x["count"] for x in days]
    total = sum(counts)
    longest = cur = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today not started yet: don't break the streak
        i -= 1
    while i >= 0 and counts[i]:
        cur += 1
        i -= 1
    peak = max(days, key=lambda x: x["count"]) if days else {"date": now.date().isoformat(), "count": 0}
    wk = [0] * 7
    for x in days:
        wk[dt.date.fromisoformat(x["date"]).weekday()] += x["count"]
    langs = {}
    for k, v in d["languages"].items():
        k = MERGE_LANGS.get(k, k)
        if k not in EXCLUDE_LANGS:
            langs[k] = langs.get(k, 0) + v
    lt = sum(langs.values()) or 1
    ranked = sorted(((k, v / lt) for k, v in langs.items()), key=lambda kv: -kv[1])
    return {"days": days, "total": total, "mean": total / max(len(days), 1), "longest": longest, "current": cur,
            "peak": peak, "busiest": DAY_ID[wk.index(max(wk))] if total else "—", "langs": ranked,
            "first": dt.date.fromisoformat(days[0]["date"]) if days else now.date(),
            "created": dt.datetime.fromisoformat(d["user"]["created_at"].replace("Z", "+00:00")).astimezone(TZ).date()}


# ─────────────────────────────── HEADER ───────────────────────────────
def build_header(d, a, now):
    W, H = 1000, 400
    cx, cy, r = 800, 205, 124
    b = [paper(W, H), key_band(20), key_band(360)]
    created = a["created"]
    b.append(text(56, 84, f"FIG. 01 — SPECIMEN SB-{created:%Y%m%d} · RECEIVED {created:%d.%m.%Y}", 11.5, "m b", RED,
                  extra='letter-spacing="2"'))
    size = min(78.0, 560 / max(tw(NAME_FIRST, 1, "is-400"), tw(NAME_LAST + ".", 1, "is-400i")))
    b.append(text(52, 156, NAME_FIRST, round(size, 1), "s", INK))
    b.append(text(52, 228, NAME_LAST, round(size, 1), "s i", RED) )
    b.append(f'<circle cx="{52 + tw(NAME_LAST, size, "is-400i") + size * .1:.1f}" cy="{228 - size * .07:.1f}" r="{size * .07:.1f}" fill="{INK}"/>')

    # typewriter tagline (SMIL, discrete steps)
    fs, x0, ty = 17, 56 + tw("› ", 17), 270
    cw = tw("a", fs)
    slot, n = 4.2, len(TAGLINES)
    T = slot * n
    b.append(text(56, ty, "›", fs, "m b", RED))
    cursor_ev = [(0.0, x0)]
    for k, phrase in enumerate(TAGLINES):
        s0 = k * slot
        ev = [(0.0, 0.0)] if k else []
        ev += [(s0 + 0.001, 0.0)] if k else [(0.0, 0.0)]
        step = min(0.055, 1.6 / len(phrase))
        for j in range(1, len(phrase) + 1):
            ev.append((s0 + 0.15 + j * step, j * cw))
        dstep = 0.35 / len(phrase)
        for j in range(1, len(phrase) + 1):
            ev.append((s0 + slot - 0.45 + j * dstep, (len(phrase) - j) * cw))
        ev = sorted(dict(ev).items())
        cursor_ev += [(t, x0 + w) for t, w in ev if t > 0]
        kt = ";".join(f"{t / T:.5f}" for t, _ in ev)
        vals = ";".join(f"{w:.1f}" for _, w in ev)
        full_w = len(phrase) * cw
        b.append(f'<clipPath id="tp{k}"><rect x="{x0 - 1:.1f}" y="{ty - 20}" width="{full_w if k == 0 else 0:.1f}" height="28">'
                 f'<animate attributeName="width" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{vals}"/>'
                 f'</rect></clipPath>')
        b.append(f'<g clip-path="url(#tp{k})">{text(x0, ty, phrase, fs, "m", INK)}</g>')
    cursor_ev = sorted(dict(cursor_ev).items())
    b.append(f'<rect x="{x0 + len(TAGLINES[0]) * cw:.1f}" y="{ty - 15}" width="{cw * .9:.1f}" height="19" fill="{RED}">'
             f'<animate attributeName="x" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
             f'keyTimes="{";".join(f"{t / T:.5f}" for t, _ in cursor_ev)}" values="{";".join(f"{x:.1f}" for _, x in cursor_ev)}"/>'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/></rect>')

    meta = [("ROLE", ROLE), ("ORIGIN", ORIGIN),
            ("ASSAY", f"{a['total']:,} contributions / 365 d · {d['user']['public_repos']} public repos · since {created.year}")]
    for k, (lab, val) in enumerate(meta):
        y = 302 + k * 20
        b.append(text(56, y, lab, 11.5, "m b", RED, extra='letter-spacing="1.5"'))
        b.append(text(128, y, val, 12.5, "m", INK))

    # sun disc + halftone
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{RED}"/>')
    b.append(f'<g clip-path="url(#disc)" mask="url(#hm)"><rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" fill="url(#dots)"/></g>')
    # ring text
    R = 139
    ring = "SEDOTAN BEKAS · A USED STRAW, STILL SIPPING · " * 2
    b.append(f'<g><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="60s" repeatCount="indefinite"/>'
             f'<text class="m b" font-size="10.5" fill="{INK}" letter-spacing="1"><textPath href="#ring" xlink:href="#ring" '
             f'textLength="{2 * math.pi * R - 6:.1f}" lengthAdjust="spacing">{esc(ring)}</textPath></text></g>')
    # flask
    flask = "M788 132V172L736 278Q730 292 745 292H855Q870 292 864 278L812 172V132Z"
    b.append(f'<path d="{flask}" fill="{PAPER}" opacity=".95"/>')
    wave = "M690 222" + "".join(f"q10 -6 20 0t20 0" for _ in range(9)) + "V300H690Z"
    b.append(f'<g clip-path="url(#flask)"><path d="{wave}" fill="{INK}"><animateTransform attributeName="transform" type="translate" '
             f'from="0 0" to="-40 0" dur="3s" repeatCount="indefinite"/></path>')
    for k, (bx, br, dur, delay) in enumerate([(762, 3.2, 3.4, 0), (778, 2.2, 2.6, .9), (826, 2.8, 3.0, 1.7), (842, 1.8, 2.2, .4), (812, 2.4, 3.8, 2.4)]):
        b.append(f'<circle cx="{bx}" cy="286" r="{br}" fill="none" stroke="{PAPER}" stroke-width="1.3" opacity="0">'
                 f'<animate attributeName="cy" values="286;226" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;.9;.9;0" keyTimes="0;.15;.8;1" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/></circle>')
    b.append("</g>")
    # graduations
    for k, gy in enumerate((240, 258, 276)):
        ex = 788 - (gy - 172) * 52 / 106
        b.append(f'<line x1="{ex + 5:.1f}" x2="{ex + 13:.1f}" y1="{gy}" y2="{gy}" stroke="{PAPER}" stroke-width="1.4" opacity=".85"/>')
        b.append(text(ex + 15.5, gy + 3, ("300", "200", "100")[k], 8, "m", PAPER, extra='opacity=".85"'))
    # straw (striped, bendy) — the used one
    straw = "M794 276L804 104Q805 90 818 87L842 84"
    b.append(f'<path d="{straw}" fill="none" stroke="{INK}" stroke-width="12.6" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(f'<path d="{straw}" fill="none" stroke="{PAPER}" stroke-width="9.6" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(f'<path d="{straw}" fill="none" stroke="{RED}" stroke-width="9.6" stroke-dasharray="6 6" stroke-linejoin="round"/>')
    b.append(f'<path d="M800.5 112l7 1.2M800.9 106.5l7 1.4M801.4 101l6.6 2" stroke="{INK}" stroke-width="1.1"/>')
    b.append(f'<rect x="782" y="124" width="36" height="9" rx="2" fill="{PAPER}" stroke="{INK}" stroke-width="2.6"/>')
    b.append(f'<path d="{flask}" fill="none" stroke="{INK}" stroke-width="2.8" stroke-linejoin="round"/>')
    b.append(border(W, H))
    defs = (KEY + f'<clipPath id="disc"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
            f'<clipPath id="flask"><path d="{flask}"/></clipPath>'
            f'<pattern id="dots" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.45" fill="{INK}"/></pattern>'
            f'<linearGradient id="hg" x1="0" y1="0" x2="1" y2="1"><stop offset=".35" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity=".55"/></linearGradient>'
            f'<mask id="hm"><rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" fill="url(#hg)"/></mask>'
            f'<path id="ring" d="M{cx - R} {cy}a{R} {R} 0 1 1 {2 * R} 0a{R} {R} 0 1 1 {-2 * R} 0"/>')
    return svg(W, H, "".join(b), f"{NAME_FIRST} {NAME_LAST} — {USER}", defs)


# ─────────────────────────────── COA ──────────────────────────────────
def stamp(cx, cy, r, date_s):
    R = r - 9
    ring = "SEDOTANBEKAS LAB · TERVERIFIKASI · VERIFIED · "
    return (f'<g transform="rotate(-13 {cx} {cy})" filter="url(#worn)" opacity=".92">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{RED}" stroke-width="2.6"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r - 17}" fill="none" stroke="{RED}" stroke-width="1.2"/>'
            f'<path id="sring" d="M{cx - R} {cy}a{R} {R} 0 1 1 {2 * R} 0a{R} {R} 0 1 1 {-2 * R} 0" fill="none"/>'
            f'<text class="m b" font-size="8.6" fill="{RED}"><textPath href="#sring" xlink:href="#sring" textLength="{2 * math.pi * R - 4:.1f}" '
            f'lengthAdjust="spacing">{esc(ring)}</textPath></text>'
            + text(cx, cy + 2, "LULUS", 21, "s", RED, "middle")
            + text(cx, cy + 15, date_s, 7.5, "m b", RED, "middle", 'letter-spacing="1"')
            + f'<line x1="{cx - 22}" x2="{cx + 22}" y1="{cy - 17}" y2="{cy - 17}" stroke="{RED}" stroke-width="1"/></g>')


def build_coa(d, a, now):
    W, H = 1000, 728
    b = [paper(W, H)]
    # header
    b.append(f'<circle cx="62" cy="62" r="28" fill="{RED}"/><circle cx="62" cy="62" r="23" fill="none" stroke="{PAPER}" stroke-width="1"/>')
    b.append(text(62, 71, "Sb", 26, "s", PAPER, "middle"))
    b.append(text(106, 62, "Laporan Hasil Uji", 36, "s", INK))
    b.append(text(107, 88, "Certificate of Analysis — specimen: one (1) developer", 18, "s i", RED))
    doc_no = f"LHU/SB/{now:%Y}/{now.timetuple().tm_yday:03d}"
    meta = [("No.", doc_no), ("Tanggal", f"{fmt_id(now)} · {now:%H:%M} WIB"), ("Halaman", "1 dari 1")]
    for k, (lab, val) in enumerate(meta):
        b.append(text(650, 44 + k * 18, lab, 11, "m", MUTE))
        b.append(text(722, 44 + k * 18, val, 11.5, "m b", INK))
    b.append(barcode(650, 92, 300, 14, doc_no))
    b.append(f'<line x1="30" x2="970" y1="124" y2="124" stroke="{INK}" stroke-width="1.6"/>'
             f'<line x1="30" x2="970" y1="128" y2="128" stroke="{INK}" stroke-width=".7"/>')
    # sample info
    info = [[("Nama sampel", f"{NAME_FIRST} {NAME_LAST}"), ("Kode sampel", f"SB-{a['created']:%Y%m%d}"),
             ("Matriks", "Kode, kopi & deadline")],
            [("Diterima", fmt_id(a["created"])), ("Periode uji", f"{fmt_id(a['first'])} – {fmt_id(now)}"),
             ("Sampling", "Komposit 365 hari · GitHub API")]]
    for c, col in enumerate(info):
        for k, (lab, val) in enumerate(col):
            x, y = 36 + c * 480, 156 + k * 22
            b.append(text(x, y, lab, 11.5, "m", MUTE))
            b.append(text(x + 108, y, ":", 11.5, "m", MUTE))
            b.append(text(x + 122, y, val, 12.5, "m b", INK))
    # table
    cols = [(30, 64, "No.", ""), (64, 380, "Parameter", "Parameter"), (380, 520, "Hasil", "Result"),
            (520, 640, "Satuan", "Unit"), (640, 760, "Baku Mutu", "Limit"), (760, 900, "Metode", "Method"), (900, 970, "Ket.", "Remark")]
    ty = 230
    b.append(f'<rect x="30" y="{ty}" width="940" height="42" fill="{INK}"/>')
    for x0, x1, idl, enl in cols:
        left = x0 in (64,)
        tx = x0 + 10 if left else (x0 + x1) / 2
        anc = "start" if left else "middle"
        b.append(text(tx, ty + 19, idl, 11.5, "m b", PAPER, anc))
        if enl:
            b.append(text(tx, ty + 35, enl, 13, "s i", LINE, anc))
    lang, share = (a["langs"][0] if a["langs"] else ("—", 0))
    pk = dt.date.fromisoformat(a["peak"]["date"])
    rows = [
        ("Total kontribusi", "Contributions, rolling 365 days", num(a["total"]), "kontribusi", "≥ 365", "IK-SB/01", a["total"] >= 365),
        ("Rata-rata harian", "Daily mean", dec(a["mean"]), "per hari", "≥ 1,0", "IK-SB/02", a["mean"] >= 1),
        ("Streak saat ini", "Current streak", str(a["current"]), "hari", "—", "IK-SB/03", None),
        ("Streak terpanjang", "Longest streak", str(a["longest"]), "hari", "≥ 7", "IK-SB/03", a["longest"] >= 7),
        ("Puncak harian", "Peak day", num(a["peak"]["count"]), fmt_id(pk), "—", "IK-SB/04", None),
        ("Hari tersibuk", "Busiest weekday", a["busiest"], "—", "—", "IK-SB/05", None),
        ("Senyawa dominan", "Dominant compound (by bytes)", lang, f"{dec(share * 100)} %", "—", "Linguist", None),
        ("Kadar kafein*", "Caffeine level", "∞", "cangkir/hari", "tidak diatur", "Organoleptik", "*"),
        ("Bug lolos uji*", "Escaped bugs, self-pentested", "< LoD", "per rilis", "0", "Pentest mandiri", "*"),
    ]
    y = ty + 42
    for k, (pid, pen, res, unit, lim, met, ok) in enumerate(rows):
        if k % 2:
            b.append(f'<rect x="30" y="{y}" width="940" height="36" fill="{PAPER2}" opacity=".75"/>')
        b.append(text(47, y + 23, str(k + 1), 11.5, "m", MUTE, "middle"))
        b.append(text(74, y + 16, pid, 12.5, "m b", INK))
        b.append(text(74, y + 30, pen, 12.5, "s i", MUTE))
        b.append(text(450, y + 23, res, 14 if len(res) < 9 else 13, "m b", RED if ok == "*" else INK, "middle"))
        b.append(text(580, y + 23, unit, 11, "m", INK, "middle"))
        b.append(text(700, y + 23, lim, 11, "m", INK, "middle"))
        b.append(text(830, y + 23, met, 11, "m", MUTE, "middle"))
        if ok is True:
            b.append(check(928, y + 18))
        elif ok is False:
            b.append(cross(930, y + 19))
        else:
            b.append(text(935, y + 23, ok or "—", 12, "m b", RED if ok else MUTE, "middle"))
        y += 36
    b.append(f'<line x1="30" x2="970" y1="{y}" y2="{y}" stroke="{INK}" stroke-width="1.6"/>')
    for x in (64, 380, 520, 640, 760, 900):
        b.append(f'<line x1="{x}" x2="{x}" y1="{ty + 42}" y2="{y}" stroke="{LINE}" stroke-width=".8"/>')
    # footnotes
    notes = ["* Parameter belum terakreditasi. / Parameter not accredited.",
             "Hasil uji hanya berlaku untuk sampel yang diuji.",
             "These results relate only to the specimen tested.",
             "LoD = limit of detection · IK = instruksi kerja (in-house).",
             "Dianalisis ulang otomatis tiap hari 00:17 WIB oleh github-actions[bot]."]
    for k, n in enumerate(notes):
        b.append(text(36, y + 28 + k * 18, n, 11.5, "m", MUTE))
    # signature + stamp
    sx = 700
    b.append(text(sx, y + 28, "Disahkan oleh / Approved by", 10.5, "m", MUTE))
    b.append(f'<path d="M{sx + 6} {y + 74}c8-26 20-40 26-30s-10 34-2 30 16-30 24-28-6 26 2 24 14-20 22-18-2 16 8 14 22-8 30-6 18 2 40-4" '
             f'fill="none" stroke="{INK}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(f'<line x1="{sx}" x2="{sx + 230}" y1="{y + 86}" y2="{y + 86}" stroke="{INK}" stroke-width="1"/>')
    b.append(text(sx, y + 102, "R. N. Adipratama", 12, "m b", INK))
    b.append(text(sx, y + 118, "Penyelia Teknis · Technical Supervisor", 10, "m", MUTE))
    b.append(stamp(sx + 178, y + 62, 48, f"{now:%d.%m.%Y}"))
    b.append(border(W, H))
    defs = ('<filter id="worn" x="-25%" y="-25%" width="150%" height="150%"><feTurbulence type="fractalNoise" baseFrequency=".75" numOctaves="2" seed="3" result="n"/>'
            '<feDisplacementMap in="SourceGraphic" in2="n" scale="2.4" xChannelSelector="R" yChannelSelector="G" result="d"/>'
            '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.1 0 0 0 1.5" result="m"/>'
            '<feComposite in="d" in2="m" operator="in"/></filter>')
    return svg(W, H, "".join(b), f"Laporan Hasil Uji — {num(a['total'])} contributions, longest streak {a['longest']} days", defs)


# ─────────────────────────────── PERIODIC TABLE ───────────────────────
def build_elements(d, a, now):
    W, H = 1000, 384
    b = [paper(W, H)]
    b.append(text(36, 56, "Tabel Periodik", 32, "s", INK))
    b.append(text(36 + tw("Tabel Periodik ", 32, "is-400"), 56, "Reagen", 32, "s i", RED))
    b.append(text(964, 50, "MASS = % OF CODE (BYTES)", 10.5, "m b", RED, "end", 'letter-spacing="1.5"'))
    b.append(text(964, 66, f"{d.get('repos_analyzed', '?')} repos assayed · markup excluded", 10.5, "m", MUTE, "end"))
    langs = a["langs"][:MAX_ELEMENTS]
    tw_, th, gap = 110, 124, 8
    x = (W - (len(langs) * tw_ + (len(langs) - 1) * gap)) / 2
    top = langs[0][1] if langs else 1
    for k, (name, share) in enumerate(langs):
        lead = k == 0
        fill, fg, sub = (RED, PAPER, PAPER) if lead else (PAPER, INK, MUTE)
        sym = SYMBOLS.get(name, name[:2].title())
        g = [f'<rect x="{x:.1f}" y="92" width="{tw_}" height="{th}" rx="4" fill="{fill}" stroke="{INK}" stroke-width="1.5"/>',
             text(x + 10, 110, str(k + 1), 11, "m b", fg),
             text(x + tw_ - 10, 110, dec(share * 100), 10.5, "m", sub, "end"),
             text(x + tw_ / 2, 166, sym, 50, "s", fg, "middle"),
             text(x + tw_ / 2, 188, name if len(name) <= 13 else name[:12] + "…", 11, "m", fg, "middle"),
             f'<rect x="{x + 10:.1f}" y="200" width="{tw_ - 20}" height="4" fill="{fg}" opacity=".18"/>',
             f'<rect x="{x + 10:.1f}" y="200" width="{max(1.5, (tw_ - 20) * share / top):.1f}" height="4" fill="{PAPER if lead else RED}"/>']
        b.append(f'<g class="el" style="animation-delay:{k * .09:.2f}s">{"".join(g)}</g>')
        x += tw_ + gap
    # tooling series
    b.append(text(36, 252, "* SERI ALAT · TOOLING SERIES", 10.5, "m b", RED, extra='letter-spacing="2"'))
    b.append(f'<line x1="{36 + tw("* SERI ALAT · TOOLING SERIES", 10.5, "jbm-700") + 2 * 28 + 14:.1f}" x2="964" y1="248" y2="248" stroke="{RED}" stroke-width="1" stroke-dasharray="2 4"/>')
    tw2, th2 = 96, 86
    x = (W - (len(TOOLS) * tw2 + (len(TOOLS) - 1) * gap)) / 2
    for k, (sym, name) in enumerate(TOOLS):
        g = [f'<rect x="{x:.1f}" y="264" width="{tw2}" height="{th2}" rx="4" fill="{PAPER2}" stroke="{INK}" stroke-width="1.2" stroke-dasharray="4 2.5"/>',
             text(x + 9, 280, str(len(langs) + k + 1), 10, "m b", INK),
             text(x + tw2 / 2, 318, sym, 34, "s", INK, "middle"),
             text(x + tw2 / 2, 338, name, 10, "m", MUTE, "middle")]
        b.append(f'<g class="el" style="animation-delay:{.75 + k * .06:.2f}s">{"".join(g)}</g>')
        x += tw2 + gap
    b.append(text(964, 372, f"last assay {fmt_en(now)} · {now:%H:%M} WIB", 10, "m", MUTE, "end"))
    b.append(border(W, H))
    css = "@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}.el{animation:rise .7s cubic-bezier(.2,.7,.2,1) both}"
    return svg(W, H, "".join(b), "Periodic table of languages and tools — " + ", ".join(n for n, _ in langs), extra_css=css)


# ─────────────────────────────── CHROMATOGRAM ─────────────────────────
def build_chroma(d, a, now):
    W, H = 1000, 368
    x0, x1, yt, yb = 70, 960, 96, 292
    days = a["days"][-CHROMA_DAYS:]
    N = len(days)
    b = [paper(W, H)]
    b.append(text(36, 56, "Kromatogram", 32, "s", INK))
    b.append(text(36 + tw("Kromatogram ", 32, "is-400"), 56, "commit activity", 32, "s i", RED))
    b.append(text(964, 50, "DETECTOR: UV-GIT @ 254 NM", 10.5, "m b", RED, "end", 'letter-spacing="1.5"'))
    b.append(text(964, 66, f"column: {USER}/* · window: {N} d · 1 analyst", 10.5, "m", MUTE, "end"))
    # grid + axes
    for k in range(1, 5):
        gy = yb - (yb - yt) * k / 4
        b.append(f'<line x1="{x0}" x2="{x1}" y1="{gy:.1f}" y2="{gy:.1f}" stroke="{LINE}" stroke-width=".8" stroke-dasharray="2 5"/>')
    dx = (x1 - x0) / max(N, 1)
    for i, day in enumerate(days):
        dd = dt.date.fromisoformat(day["date"])
        if dd.day in (1, 15):
            xx = x0 + (i + .5) * dx
            b.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{yb}" y2="{yb + 6}" stroke="{INK}" stroke-width="1"/>')
            b.append(text(xx, yb + 20, f"{MON_EN[dd.month - 1]} {dd.day:02d}", 10, "m", MUTE, "middle"))
    b.append(f'<path d="M{x0} {yt - 6}V{yb}H{x1 + 6}" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    b.append(text(x1, yb + 40, "retention time →", 10, "m", MUTE, "end"))
    b.append(text(48, (yt + yb) / 2, "intensity", 10, "m", MUTE, "middle", f'transform="rotate(-90 48 {(yt + yb) / 2})"'))
    # signal: tailing gaussians, power-scaled so small days still register
    S = 8
    hs = [x["count"] ** .75 for x in days]
    mx = max(hs) if hs and max(hs) > 0 else 1
    amp = (yb - yt) * .6 / mx
    pts = []
    for s in range(N * S + 1):
        t = s / S
        v = 0.0
        for i in range(max(0, int(t) - 3), min(N, int(t) + 4)):
            if hs[i]:
                u = t - (i + .5)
                sg = .2 if u < 0 else .34
                v += hs[i] * math.exp(-(u * u) / (2 * sg * sg))
        noise = .55 * math.sin(s * 1.7) * math.sin(s * .37 + 1) + .3 * math.sin(s * 5.3)
        pts.append((x0 + t * dx, yb - 1.5 - v * amp + noise))
    line = "M" + "L".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    area = line + f"L{x1:.1f} {yb}L{x0} {yb}Z"
    b.append(f'<clipPath id="plot"><rect x="{x0 + 1}" y="{yt - 8}" width="{x1 - x0}" height="{yb - yt + 7}"/></clipPath>')
    b.append(f'<g clip-path="url(#plot)"><path d="{area}" fill="{RED}" opacity=".16"><animate attributeName="opacity" values="0;0;.16" keyTimes="0;.6;1" dur="3.6s" fill="freeze"/></path>'
             f'<path d="{line}" fill="none" stroke="{INK}" stroke-width="1.35" stroke-linejoin="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="0">'
             f'<animate attributeName="stroke-dashoffset" values="1000;0" dur="3.2s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".45 0 .25 1"/></path></g>')
    # peak labels
    chosen = []
    for i in sorted(range(N), key=lambda i: -days[i]["count"]):
        if days[i]["count"] <= 0 or len(chosen) >= 7:
            break
        if all(abs(i - j) >= 4 for j in chosen):
            chosen.append(i)
    for i in chosen:
        px = x0 + (i + .5) * dx
        py = yb - 1.5 - hs[i] * amp
        dd = dt.date.fromisoformat(days[i]["date"])
        lab = f"{days[i]['count']} · {MON_EN[dd.month - 1]} {dd.day:02d}"
        b.append(f'<line x1="{px:.1f}" x2="{px:.1f}" y1="{py + 3:.1f}" y2="{yb}" stroke="{RED}" stroke-width=".9" stroke-dasharray="1.5 2.5" opacity=".7"/>')
        b.append(text(px + 3.5, py - 6, lab, 9.5, "m b", RED_D, "start", f'transform="rotate(-90 {px + 3.5:.1f} {py - 6:.1f})"'))
    # scanning detector + REC
    b.append(f'<line x1="{x0}" x2="{x0}" y1="{yt}" y2="{yb}" stroke="{RED}" stroke-width="1.2" opacity=".5">'
             f'<animate attributeName="x1" values="{x0};{x1}" dur="9s" begin="3.4s" repeatCount="indefinite"/>'
             f'<animate attributeName="x2" values="{x0};{x1}" dur="9s" begin="3.4s" repeatCount="indefinite"/></line>')
    b.append(f'<circle cx="{x0 + 14}" cy="{yt + 4}" r="3.6" fill="{RED}"><animate attributeName="opacity" values="1;1;.15;.15" keyTimes="0;.5;.5;1" dur="1.4s" repeatCount="indefinite"/></circle>')
    b.append(text(x0 + 23, yt + 8, "REC", 10, "m b", RED, extra='letter-spacing="1.5"'))
    win = sum(x["count"] for x in days)
    big = sum(1 for x in days if x["count"] >= 20)
    b.append(text(36, H - 18, f"∑ area ({N} d) = {num(win)} · peaks ≥ 20: {big} · max {num(a['peak']['count'])} @ {fmt_en(dt.date.fromisoformat(a['peak']['date']))}", 11.5, "m", INK))
    b.append(border(W, H))
    return svg(W, H, "".join(b), f"Contribution chromatogram, last {N} days: {num(win)} contributions")


# ─────────────────────────────── SAMPLE CARDS ─────────────────────────
def wrap(s, width, size):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(t, size) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines[:2] if len(lines) <= 2 else lines[:1] + [lines[1][: max(1, len(lines[1]) - 1)] + "…"]


def build_sample(k, full, code, desc, info, now):
    W, H = 490, 180
    name = full.split("/")[1]
    b = [paper(W, H, rx=10, cid="c")]
    b.append(f'<g clip-path="url(#c)"><rect width="42" height="{H}" fill="{RED}"/></g>')
    b.append(f'<line x1="42" x2="42" y1="0" y2="{H}" stroke="{INK}" stroke-width="1.4"/>')
    b.append(text(21, H / 2, f"SAMPLE {k + 1:02d}", 11, "m b", PAPER, "middle", f'letter-spacing="3" transform="rotate(-90 21 {H / 2})" dy="4"'))
    b.append(text(62, 34, f"SB-S{k + 1:02d} · {code}", 10.5, "m b", RED, extra='letter-spacing="1.5"'))
    tag = "LIVE ↗" if info.get("homepage") else "REPO ↗"
    tgw = tw(tag, 10, "jbm-700") + 16
    b.append(f'<rect x="{W - 20 - tgw:.1f}" y="20" width="{tgw:.1f}" height="19" rx="9.5" fill="{INK if tag.startswith("LIVE") else "none"}" stroke="{INK}" stroke-width="1.2"/>')
    b.append(text(W - 20 - tgw / 2, 33.5, tag, 10, "m b", PAPER if tag.startswith("LIVE") else INK, "middle"))
    size = min(30, 400 / max(tw(name, 1, "is-400"), 1))
    b.append(text(61, 72, name, round(size, 1), "s", INK))
    for j, ln in enumerate(wrap(desc, 400, 11.5)):
        b.append(text(62, 98 + j * 17, ln, 11.5, "m", INK))
    b.append(f'<line x1="62" x2="{W - 20}" y1="134" y2="134" stroke="{LINE}" stroke-width="1" stroke-dasharray="3 3"/>')
    pushed = info.get("pushed_at")
    last = fmt_en(dt.datetime.fromisoformat(pushed.replace("Z", "+00:00")).astimezone(TZ).date()) if pushed else "—"
    lang = info.get("language") or "—"
    b.append(f'<circle cx="66" cy="155" r="4" fill="{RED}"/>')
    b.append(text(76, 159, lang, 11, "m b", INK))
    lx = 76 + tw(lang, 11, "jbm-700") + 18
    b.append(text(lx, 159, "LAST SAMPLED", 9.5, "m", MUTE, extra='letter-spacing="1"'))
    b.append(text(lx + tw("LAST SAMPLED", 9.5) + 16, 159, last, 11, "m b", INK))
    b.append(barcode(W - 128, 146, 108, 18, full))
    b.append(border(W, H, rx=10))
    return svg(W, H, "".join(b), f"{name}: {desc}")


# ─────────────────────────────── FOOTER ───────────────────────────────
def build_footer(d, a, now):
    W, H = 1000, 96
    b = [paper(W, H), key_band(20)]
    b.append(text(W / 2, 74, f"sedotan bekas — dipakai sekali, masih berguna · used once, still useful · last assay {fmt_en(now)}, {now:%H:%M} WIB",
                  11, "m", INK, "middle"))
    b.append(border(W, H))
    return svg(W, H, "".join(b), "sedotan bekas — used once, still useful", KEY, serif=False)


# ─────────────────────────────── MAIN ─────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", help="build offline from a saved snapshot JSON")
    ap.add_argument("--save-snapshot", help="write the fetched data to this JSON file")
    ap.add_argument("--now", help="override the build time (ISO 8601), for previews")
    args = ap.parse_args()
    d = json.loads(Path(args.snapshot).read_text("utf-8")) if args.snapshot else fetch_live()
    if args.save_snapshot:
        Path(args.save_snapshot).write_text(json.dumps(d, indent=1), "utf-8")
    now = dt.datetime.fromisoformat(args.now).astimezone(TZ) if args.now else dt.datetime.now(TZ)
    a = analyze(d, now)
    (ASSETS / "samples").mkdir(parents=True, exist_ok=True)
    out = {"header.svg": build_header(d, a, now), "coa.svg": build_coa(d, a, now), "elements.svg": build_elements(d, a, now),
           "chromatogram.svg": build_chroma(d, a, now), "footer.svg": build_footer(d, a, now)}
    for k, (full, code, desc) in enumerate(FEATURED):
        out[f"samples/{full.split('/')[1]}.svg"] = build_sample(k, full, code, desc, d.get("featured", {}).get(full, {}), now)
    for name, content in out.items():
        (ASSETS / name).write_text(content, "utf-8")
        print(f"  ✓ assets/{name:<34} {len(content) / 1024:6.1f} KB")
    print(f"total {a['total']} · longest {a['longest']} · current {a['current']} · top {a['langs'][:3]}")


if __name__ == "__main__":
    main()
