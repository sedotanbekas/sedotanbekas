#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sedotanbekas · profile lab
==========================
Generates every SVG in ./assets (one set per language) and the README files
from live GitHub data. No third-party stats services.

    python scripts/build.py                            # live (uses $GH_TOKEN / $GITHUB_TOKEN if set)
    python scripts/build.py --snapshot data/snap.json  # offline, from a saved snapshot
    python scripts/build.py --langs en,ar              # only some languages

Runs on the standard library alone. With `pip install fonttools brotli uharfbuzz`
(what the workflow does) every SVG embeds only the glyphs it shows and text is
measured with real shaping; without them the whole per-script font is embedded.

Copy lives in scripts/i18n.py; profile data in the CONFIG block below.
"""
import argparse
import base64
import datetime as dt
import hashlib
import io
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import LANGS, T, coa_strings  # noqa: E402

try:
    from fontTools import subset as ftsubset
    from fontTools.ttLib import TTFont
    HAVE_FT = True
except ImportError:
    HAVE_FT = False
try:
    import uharfbuzz as hb
    HAVE_HB = HAVE_FT
except ImportError:
    HAVE_HB = False

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"

# ─────────────────────────────── CONFIG ───────────────────────────────
USER = "sedotanbekas"
NAME_FIRST, NAME_LAST = "Rafif Nuraydin", "Adipratama"
TZ = ZoneInfo("Asia/Jakarta")
FEATURED = [  # (repo, short code, link) — descriptions are in i18n.py ("s_desc")
    ("medialabindonesia/lims-medialab", "LIMS", "https://github.com/medialabindonesia/lims-medialab"),
    ("sedotanbekas/ml-assist", "ASSIST", "https://ml-assist.vercel.app"),
    ("sedotanbekas/umkm-ez-tax", "BANGKIT", "https://github.com/sedotanbekas/umkm-ez-tax"),
    ("sedotanbekas/sentiment-analysis-web", "NLP", "https://github.com/sedotanbekas/sentiment-analysis-web"),
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


# ─────────────────────────────── FONTS ────────────────────────────────
_METRICS = json.loads((FONTS / "metrics.json").read_text("utf-8"))


def is_latin(ch):
    o = ord(ch)
    return o < 0x250 or 0x1E00 <= o < 0x1F00 or 0x2000 <= o < 0x2400 or 0x2500 <= o < 0x27C0


def nonlatin(s):
    return any(not is_latin(c) for c in s if not c.isspace())


def is_arabic(s):
    return any(0x600 <= ord(c) < 0x700 or 0xFB50 <= ord(c) < 0xFF00 for c in s)


def is_complex(s):  # scripts whose shaping breaks under letter-spacing
    return any(0x600 <= ord(c) < 0x700 or 0x900 <= ord(c) < 0xA00 or 0xFB50 <= ord(c) < 0xFF00 for c in s)


class Face:
    def __init__(self, fid):
        self.id, self.path = fid, FONTS / "src" / f"{fid}.woff2"
        m = _METRICS.get(fid)
        self.ok = bool(m) and self.path.exists()
        self.upm, self.adv = (m["upm"], m["w"]) if m else (1000, {})
        self._hb = None

    def has(self, ch):
        return ch in self.adv

    def hbfont(self):
        if self._hb is None:
            self._hb = False
            if HAVE_HB:
                f = TTFont(self.path)
                f.flavor = None
                b = io.BytesIO()
                f.save(b)
                self._hb = hb.Font(hb.Face(b.getvalue()))
        return self._hb or None

    def shape(self, s):
        f = self.hbfont()
        if not f:
            return sum(self.adv.get(c, self.upm * .55) for c in s), None
        buf = hb.Buffer()
        buf.add_str(s)
        buf.guess_segment_properties()
        hb.shape(f, buf, {})
        return sum(p.x_advance for p in buf.glyph_positions), [g.codepoint for g in buf.glyph_infos]


_FACES = {}


def face(fid):
    if fid not in _FACES:
        _FACES[fid] = Face(fid)
    return _FACES[fid] if _FACES[fid].ok else None


def stack(lang, fam, bold, italic, script_first):
    if fam == "m":
        base, x = face("jb-700" if bold else "jb-400"), face(f"{lang}-m-{'700' if bold else '400'}")
    else:
        base = face("is-400i" if italic else "is-400")
        x = (face(f"{lang}-s-400i") if italic else None) or face(f"{lang}-s-400")
    return [f for f in ((x, base) if script_first else (base, x)) if f]


def runs(text, faces):
    out = []
    for ch in text:
        f = next((f for f in faces if f.has(ch)), faces[0])
        if out and out[-1][0] is f:
            out[-1][1].append(ch)
        else:
            out.append([f, [ch]])
    return [(f, "".join(cs)) for f, cs in out]


def font_css(lang, uses):
    """@font-face rules for exactly the glyphs this SVG renders."""
    need = {}
    for fam, bold, italic, s in uses:
        for f, sub in runs(s, stack(lang, fam, bold, italic, nonlatin(s))):
            need.setdefault(f.id, set()).add(sub)
    rules = []
    for fid, subs in sorted(need.items()):
        f = _FACES[fid]
        family = "JB" if fid.startswith("jb") else "IS" if fid.startswith("is") else ("XM" if "-m-" in fid else "XS")
        weight = 700 if fid.endswith("700") else 400
        fstyle = "italic" if fid.endswith("i") else "normal"
        data = f.path.read_bytes()
        if HAVE_FT:
            text = "".join(subs)
            gids = set()
            if HAVE_HB:
                for sub in subs:
                    for w in re.split(r"(\s+)", sub):
                        if w:
                            gids |= set(f.shape(w)[1] or [])
            opts = ftsubset.Options()
            opts.flavor, opts.notdef_outline, opts.hinting, opts.name_IDs = "woff2", True, False, ["*"]
            if gids:
                opts.layout_closure = False
            tt = TTFont(f.path)
            sb = ftsubset.Subsetter(opts)
            sb.populate(text=text, gids=sorted(gids))
            sb.subset(tt)
            buf = io.BytesIO()
            tt.save(buf)
            data = buf.getvalue()
        b64 = base64.b64encode(data).decode()
        rules.append(f"@font-face{{font-family:{family};src:url(data:font/woff2;base64,{b64}) format('woff2');"
                     f"font-weight:{weight};font-style:{fstyle}}}")
    return "".join(rules)


# ─────────────────────────────── CANVAS ───────────────────────────────
def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def attrs(a):
    return "".join(f' {k.rstrip("_").replace("_", "-")}="{v}"' for k, v in a.items() if v is not None)


GRAIN = ('<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" '
         'numOctaves="3" seed="11" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 .1  0 0 0 0 .08  0 0 0 0 .06  0 0 0 -1.4 .78"/></filter>')
KEY = (f'<pattern id="key" x="30" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M0 18H20M1.6 18V2H16.4V14.4H5.6V5.6H12.4V10.2H9" '
       f'fill="none" stroke="{RED}" stroke-width="2.1"/></pattern>')
BASE_CSS = (".m{font-family:JB,XM,ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}"
            ".mx{font-family:XM,JB,ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}"
            ".s{font-family:IS,XS,'Times New Roman',Georgia,serif}.sx{font-family:XS,IS,'Times New Roman',Georgia,serif}"
            ".i{font-style:italic}.b{font-weight:700}text{font-synthesis:weight}")


class Canvas:
    """SVG builder that mirrors its layout for right-to-left languages."""

    def __init__(self, W, H, lang, mirror=True):
        self.W, self.H, self.L = W, H, lang
        self.rtl = T[lang]["dir"] == "rtl" and mirror
        self.parts, self.uses, self.defs, self.css = [], [], [], ""

    # geometry
    def X(self, x):
        return self.W - x if self.rtl else x

    def RX(self, x, w):
        return self.W - x - w if self.rtl else x

    def add(self, *s):
        self.parts.extend(s)

    def rect(self, x, y, w, h, mirror=True, **a):
        self.add(f'<rect x="{self.RX(x, w) if mirror else x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"{attrs(a)}/>')

    def line(self, x1, y1, x2, y2, mirror=True, **a):
        if mirror:
            x1, x2 = self.X(x1), self.X(x2)
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"{attrs(a)}/>')

    def circle(self, cx, cy, r, mirror=True, inner="", **a):
        self.add(f'<circle cx="{self.X(cx) if mirror else cx:.1f}" cy="{cy:.1f}" r="{r:.1f}"{attrs(a)}>{inner}</circle>')

    def mirrored(self, inner):  # absolute-coordinate artwork that should flip with the layout
        return f'<g transform="translate({self.W} 0) scale(-1 1)">{inner}</g>' if self.rtl else inner

    # text
    @staticmethod
    def _parse(cls):
        t = cls.split()
        return ("s" if "s" in t else "m"), "b" in t, "i" in t

    def measure(self, s, size, cls="m", ls=0):
        fam, bold, italic = self._parse(cls)
        faces = stack(self.L, fam, bold, italic, nonlatin(s))
        if not faces:
            return len(s) * size * .6
        w = sum(f.shape(sub)[0] / f.upm * size for f, sub in runs(s, faces))
        return w + (0 if is_complex(s) else ls * len(s))

    def fit(self, s, size, maxw, cls="m", ls=0, floor=6.5):
        w = self.measure(s, size, cls, ls)
        return size if w <= maxw else max(floor, round(size * maxw / w, 2))

    def use(self, cls, s):
        fam, bold, italic = self._parse(cls)
        self.uses.append((fam, bold, italic, s))

    def _cls(self, cls, s):
        fam, bold, italic = self._parse(cls)
        return " ".join([fam + ("x" if nonlatin(s) else "")] + (["b"] if bold else []) + (["i"] if italic else []))

    def _align(self, x, anchor, rtl_text, mirror):
        vis = {"start": "L", "end": "R", "middle": "C"}[anchor]
        if self.rtl and mirror:
            x, vis = self.W - x, {"L": "R", "R": "L", "C": "C"}[vis]
        if rtl_text:
            return x, {"L": "end", "R": "start", "C": "middle"}[vis], "rtl"
        return x, {"L": "start", "R": "end", "C": "middle"}[vis], "ltr"

    def text(self, x, y, s, size, cls="m", fill=INK, anchor="start", ls=0, mirror=True, rot=None, extra="", inner=""):
        self.use(cls, s)
        x, anc, d = self._align(x, anchor, is_arabic(s), mirror)
        lsa = f' letter-spacing="{ls}"' if ls and not is_complex(s) else ""
        tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" class="{self._cls(cls, s)}" font-size="{size}" fill="{fill}" '
                 f'text-anchor="{anc}" direction="{d}"{lsa}{tr} {extra}>{esc(s)}{inner}</text>')

    def rich(self, x, y, parts, anchor="start", mirror=True):
        """parts: [(text, size, cls, fill)] in one line, letting the browser do the bidi layout."""
        full = "".join(p[0] for p in parts)
        x, anc, d = self._align(x, anchor, is_arabic(full), mirror)
        spans = []
        for s, size, cls, fill in parts:
            self.use(cls, s)
            spans.append(f'<tspan class="{self._cls(cls, s)}" font-size="{size}" fill="{fill}">{esc(s)}</tspan>')
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anc}" direction="{d}" xml:space="preserve">{"".join(spans)}</text>')

    # chrome
    def paper(self, rx=12, cid="card"):
        W, H = self.W, self.H
        self.add(f'<clipPath id="{cid}"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{rx}"/></clipPath>'
                 f'<g clip-path="url(#{cid})"><rect width="{W}" height="{H}" fill="{PAPER}"/>'
                 f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity=".55"/></g>')

    def border(self, rx=12):
        self.add(f'<rect x="1" y="1" width="{self.W - 2}" height="{self.H - 2}" rx="{rx}" fill="none" stroke="{INK}" stroke-width="1.6"/>')

    def key_band(self, y, x0=30, x1=970):
        if "key" not in "".join(self.defs):
            self.defs.append(KEY)
        self.add(f'<line x1="{x0}" x2="{x1}" y1="{y - 4}" y2="{y - 4}" stroke="{RED}" stroke-width="1.2"/>'
                 f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="20" fill="url(#key)"/>'
                 f'<line x1="{x0}" x2="{x1}" y1="{y + 24}" y2="{y + 24}" stroke="{RED}" stroke-width="1.2"/>')

    def barcode(self, x, y, w, h, seed, color=INK):
        bits = hashlib.sha256(seed.encode()).digest() * 2
        bars, cx, i, unit = [], 0.0, 0, w / 120
        x0 = self.RX(x, w)
        while cx < w and i < len(bits):
            bw, gap = (1 + bits[i] % 3) * unit, (1 + (bits[i] >> 3) % 2) * unit
            if cx + bw > w:
                break
            bars.append(f'<rect x="{x0 + cx:.2f}" y="{y}" width="{bw:.2f}" height="{h}"/>')
            cx += bw + gap
            i += 1
        self.add(f'<g fill="{color}">{"".join(bars)}</g>')

    def check(self, x, y, color=RED):
        x = self.RX(x, 13.5)
        self.add(f'<path d="M{x:.1f} {y}l4.5 4.5 9-10" fill="none" stroke="{color}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')

    def cross(self, x, y, color=RED):
        x = self.RX(x, 9)
        self.add(f'<path d="M{x:.1f} {y - 5}l9 9m0-9-9 9" fill="none" stroke="{color}" stroke-width="2.4" stroke-linecap="round"/>')

    def render(self, title, grain=True):
        css = BASE_CSS + self.css
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{self.W}" height="{self.H}" '
                f'viewBox="0 0 {self.W} {self.H}" role="img" aria-label="{esc(title)}"><title>{esc(title)}</title>'
                f'<defs><style>{font_css(self.L, self.uses)}{css}</style>{GRAIN if grain else ""}{"".join(self.defs)}</defs>'
                f'{"".join(self.parts)}</svg>')


# ─────────────────────────────── FORMAT ───────────────────────────────
def num(n, lang=None):  # SI-style thousands (2 152); commas in RTL text, where bidi would split "2 152"
    return f"{n:,}" if lang and T[lang]["dir"] == "rtl" else f"{n:,}".replace(",", " ")


def grouped(lang, n):
    sep = {"es": ".", "pt": ".", "id": ".", "fr": " ", "ru": " "}.get(lang, ",")
    return f"{n:,}".replace(",", sep)


def dec(lang, x, p=1):
    return f"{x:.{p}f}".replace(".", T[lang]["dec"])


def fdate(lang, d, short=False):
    t = T[lang]
    return t["short" if short else "date"].format(d=d.day, dd=f"{d.day:02d}", m=d.month, mon=t["months"][d.month - 1], y=d.year)


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
            "peak": peak, "busiest": wk.index(max(wk)) if total else None, "langs": ranked,
            "first": dt.date.fromisoformat(days[0]["date"]) if days else now.date(),
            "created": dt.datetime.fromisoformat(d["user"]["created_at"].replace("Z", "+00:00")).astimezone(TZ).date()}


# ─────────────────────────────── HEADER ───────────────────────────────
def build_header(d, a, now, L):
    t = T[L]
    c = Canvas(1000, 400, L)
    W = c.W
    cx, cy, r = 800, 205, 124
    c.paper()
    c.key_band(20)
    c.key_band(360)
    created = a["created"]
    fig = t["fig"].format(code=f"SB-{created:%Y%m%d}", date=f"{created:%d.%m.%Y}")
    c.text(56, 84, fig, c.fit(fig, 11.5, 580, "m b", 2), "m b", RED, ls=2)

    size = min(78.0, 560 / max(c.measure(NAME_FIRST, 1, "s"), c.measure(NAME_LAST + ".", 1, "s i")))
    size = round(size, 1)
    dot_r = size * .07
    c.text(52, 156, NAME_FIRST, size, "s", INK)
    wl = c.measure(NAME_LAST, size, "s i")
    if c.rtl:
        gap = size * .1 + 2 * dot_r
        c.text(52 + gap, 228, NAME_LAST, size, "s i", RED)
        c.add(f'<circle cx="{W - 52 - dot_r:.1f}" cy="{228 - dot_r:.1f}" r="{dot_r:.1f}" fill="{INK}"/>')
    else:
        c.text(52, 228, NAME_LAST, size, "s i", RED)
        c.add(f'<circle cx="{52 + wl + size * .1:.1f}" cy="{228 - dot_r:.1f}" r="{dot_r:.1f}" fill="{INK}"/>')

    # typewriter tagline (SMIL, discrete steps; grows leftwards for RTL)
    fs, ty = 17, 270
    prompt = "‹" if c.rtl else "›"
    x0 = 56 + c.measure("› ", fs)
    c.text(56, ty, prompt, fs, "m b", RED)
    slot, n = 4.2, len(t["taglines"])
    Tt = slot * n
    cur_w = c.measure("a", fs) * .9
    edge = c.X(x0)
    cursor_ev = []
    for k, phrase in enumerate(t["taglines"]):
        size_k = c.fit(phrase, fs, 600 - x0, "m")
        full = c.measure(phrase, size_k)
        steps = max(1, len(phrase))
        s0 = k * slot
        ev = [(0.0, 0.0)] + ([(s0 + .001, 0.0)] if k else [])
        step = min(.055, 1.6 / steps)
        for j in range(1, steps + 1):
            ev.append((s0 + .15 + j * step, full * j / steps))
        dstep = .35 / steps
        for j in range(1, steps + 1):
            ev.append((s0 + slot - .45 + j * dstep, full * (steps - j) / steps))
        ev = sorted(dict(ev).items())
        cursor_ev += [(tm, w) for tm, w in ev if tm > 0 or k == 0]
        kt = ";".join(f"{tm / Tt:.5f}" for tm, _ in ev)
        widths = ";".join(f"{w + 2:.1f}" for _, w in ev)
        init = full + 2 if k == 0 else 0
        if c.rtl:
            xs = ";".join(f"{edge + 1 - w - 2:.1f}" for _, w in ev)
            anim = (f'<animate attributeName="width" dur="{Tt}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{widths}"/>'
                    f'<animate attributeName="x" dur="{Tt}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{xs}"/>')
            rx = edge + 1 - init
        else:
            anim = f'<animate attributeName="width" dur="{Tt}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{widths}"/>'
            rx = x0 - 1
        c.add(f'<clipPath id="tp{k}"><rect x="{rx:.1f}" y="{ty - 22}" width="{init:.1f}" height="30">{anim}</rect></clipPath>')
        c.add(f'<g clip-path="url(#tp{k})">')
        c.text(x0, ty, phrase, size_k, "m", INK)
        c.add("</g>")
    cursor_ev = sorted(dict(cursor_ev).items())
    cx_of = (lambda w: edge - w - cur_w - 1) if c.rtl else (lambda w: x0 + w + 1)
    first_full = c.measure(t["taglines"][0], c.fit(t["taglines"][0], fs, 600 - x0, "m"))
    c.add(f'<rect x="{cx_of(first_full):.1f}" y="{ty - 15}" width="{cur_w:.1f}" height="19" fill="{RED}">'
          f'<animate attributeName="x" dur="{Tt}s" repeatCount="indefinite" calcMode="discrete" '
          f'keyTimes="{";".join(f"{tm / Tt:.5f}" for tm, _ in cursor_ev)}" values="{";".join(f"{cx_of(w):.1f}" for _, w in cursor_ev)}"/>'
          f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/></rect>')

    meta = list(zip(t["labels"], [t["role_v"], t["origin_v"],
                                  t["assay_v"].format(n=grouped(L, a["total"]), r=d["user"]["public_repos"], y=created.year)]))
    labw = max(72, max(c.measure(lab, 11.5, "m b", 1.5) for lab, _ in meta) + 16)
    for k, (lab, val) in enumerate(meta):
        y = 302 + k * 20
        c.text(56, y, lab, 11.5, "m b", RED, ls=1.5)
        c.text(56 + labw, y, val, c.fit(val, 12.5, 640 - 56 - labw, "m"), "m", INK)

    # artwork: sun disc, halftone, rotating ring, flask of coffee with the used straw
    R = 139
    ring = "SEDOTAN BEKAS · A USED STRAW, STILL SIPPING · " * 2
    c.use("m b", ring)
    flask = "M788 132V172L736 278Q730 292 745 292H855Q870 292 864 278L812 172V132Z"
    wave = "M690 222" + "q10 -6 20 0t20 0" * 9 + "V300H690Z"
    art = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{RED}"/>',
           f'<g clip-path="url(#disc)" mask="url(#hm)"><rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" fill="url(#dots)"/></g>',
           f'<g><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="60s" repeatCount="indefinite"/>'
           f'<text class="m b" font-size="10.5" fill="{INK}" letter-spacing="1" direction="ltr"><textPath href="#ring" xlink:href="#ring" '
           f'textLength="{2 * math.pi * R - 6:.1f}" lengthAdjust="spacing">{esc(ring)}</textPath></text></g>',
           f'<path d="{flask}" fill="{PAPER}" opacity=".95"/>',
           f'<g clip-path="url(#flask)"><path d="{wave}" fill="{INK}"><animateTransform attributeName="transform" type="translate" '
           f'from="0 0" to="-40 0" dur="3s" repeatCount="indefinite"/></path>']
    for bx, br, dur, delay in [(762, 3.2, 3.4, 0), (778, 2.2, 2.6, .9), (826, 2.8, 3.0, 1.7), (842, 1.8, 2.2, .4), (812, 2.4, 3.8, 2.4)]:
        art.append(f'<circle cx="{bx}" cy="286" r="{br}" fill="none" stroke="{PAPER}" stroke-width="1.3" opacity="0">'
                   f'<animate attributeName="cy" values="286;226" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0;.9;.9;0" keyTimes="0;.15;.8;1" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/></circle>')
    art.append("</g>")
    for k, gy in enumerate((240, 258, 276)):
        ex = 788 - (gy - 172) * 52 / 106
        art.append(f'<line x1="{ex + 5:.1f}" x2="{ex + 13:.1f}" y1="{gy}" y2="{gy}" stroke="{PAPER}" stroke-width="1.4" opacity=".85"/>')
        art.append(f'<text x="{ex + 15.5:.1f}" y="{gy + 3}" class="m" font-size="8" fill="{PAPER}" opacity=".85">{("300", "200", "100")[k]}</text>')
        c.use("m", "300200100")
    straw = "M794 276L804 104Q805 90 818 87L842 84"
    art += [f'<path d="{straw}" fill="none" stroke="{INK}" stroke-width="12.6" stroke-linecap="round" stroke-linejoin="round"/>',
            f'<path d="{straw}" fill="none" stroke="{PAPER}" stroke-width="9.6" stroke-linecap="round" stroke-linejoin="round"/>',
            f'<path d="{straw}" fill="none" stroke="{RED}" stroke-width="9.6" stroke-dasharray="6 6" stroke-linejoin="round"/>',
            f'<path d="M800.5 112l7 1.2M800.9 106.5l7 1.4M801.4 101l6.6 2" stroke="{INK}" stroke-width="1.1"/>',
            f'<rect x="782" y="124" width="36" height="9" rx="2" fill="{PAPER}" stroke="{INK}" stroke-width="2.6"/>',
            f'<path d="{flask}" fill="none" stroke="{INK}" stroke-width="2.8" stroke-linejoin="round"/>']
    c.add(f'<g transform="translate(-600 0)">' if c.rtl else "<g>", *art, "</g>")
    c.border()
    c.defs.append(f'<clipPath id="disc"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath><clipPath id="flask"><path d="{flask}"/></clipPath>'
                  f'<pattern id="dots" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.45" fill="{INK}"/></pattern>'
                  f'<linearGradient id="hg" x1="0" y1="0" x2="1" y2="1"><stop offset=".35" stop-color="#fff" stop-opacity="0"/>'
                  f'<stop offset="1" stop-color="#fff" stop-opacity=".55"/></linearGradient>'
                  f'<mask id="hm"><rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" fill="url(#hg)"/></mask>'
                  f'<path id="ring" d="M{cx - R} {cy}a{R} {R} 0 1 1 {2 * R} 0a{R} {R} 0 1 1 {-2 * R} 0"/>')
    return c.render(f"{NAME_FIRST} {NAME_LAST} — {USER}")


# ─────────────────────────────── COA ──────────────────────────────────
def stamp(c, cx, cy, r, date_s):
    R = r - 9
    ring = "SEDOTANBEKAS LAB · TERVERIFIKASI · VERIFIED · "
    c.use("m b", ring + date_s)
    c.use("s", "LULUS")
    c.add(f'<g transform="rotate(-13 {cx} {cy})" filter="url(#worn)" opacity=".92">'
          f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{RED}" stroke-width="2.6"/>'
          f'<circle cx="{cx}" cy="{cy}" r="{r - 17}" fill="none" stroke="{RED}" stroke-width="1.2"/>'
          f'<path id="sring" d="M{cx - R} {cy}a{R} {R} 0 1 1 {2 * R} 0a{R} {R} 0 1 1 {-2 * R} 0" fill="none"/>'
          f'<text class="m b" font-size="8.6" fill="{RED}" direction="ltr"><textPath href="#sring" xlink:href="#sring" '
          f'textLength="{2 * math.pi * R - 4:.1f}" lengthAdjust="spacing">{esc(ring)}</textPath></text>'
          f'<text x="{cx}" y="{cy + 2}" class="s" font-size="21" fill="{RED}" text-anchor="middle">LULUS</text>'
          f'<text x="{cx}" y="{cy + 15}" class="m b" font-size="7.5" fill="{RED}" text-anchor="middle" letter-spacing="1">{date_s}</text>'
          f'<line x1="{cx - 22}" x2="{cx + 22}" y1="{cy - 17}" y2="{cy - 17}" stroke="{RED}" stroke-width="1"/></g>')


def build_coa(d, a, now, L):
    t = T[L]
    P, S = coa_strings(L)
    cl = "id" if L in ("en", "id") else L  # language of dates/decimals inside the report
    days = T["id"]["days"] if L in ("en", "id") else t["days"]
    c = Canvas(1000, 728, L)
    c.paper()
    c.circle(62, 62, 28, fill=RED)
    c.circle(62, 62, 23, fill="none", stroke=PAPER, stroke_width=1)
    c.text(62, 71, "Sb", 26, "s", PAPER, "middle")
    c.text(106, 62, "Laporan Hasil Uji", 36, "s", INK)
    c.text(107, 88, t["coa_sub"], c.fit(t["coa_sub"], 18, 520, "s i"), "s i", RED)
    doc_no = f"LHU/SB/{now:%Y}/{now.timetuple().tm_yday:03d}"
    if L not in ("en", "id"):
        tag = f"SALINAN TERJEMAHAN · {t['native']}"
        c.text(650, 24, tag, 9.5, "m b", RED, ls=1.5)
    meta = list(zip(P["meta_l"], [doc_no, f"{fdate(cl, now)} · {now:%H:%M} WIB", P["page_v"]]))
    mlw = max(72, max(c.measure(lab, 11, "m") for lab, _ in meta) + 12)
    for k, (lab, val) in enumerate(meta):
        c.text(650, 44 + k * 18, lab, 11, "m", MUTE)
        c.text(650 + mlw, 44 + k * 18, val, c.fit(val, 11.5, 320 - mlw, "m b"), "m b", INK)
    c.barcode(650, 92, 300, 14, doc_no)
    c.line(30, 124, 970, 124, stroke=INK, stroke_width=1.6)
    c.line(30, 128, 970, 128, stroke=INK, stroke_width=.7)
    vals = [f"{NAME_FIRST} {NAME_LAST}", f"SB-{a['created']:%Y%m%d}", P["matrix_v"],
            fdate(cl, a["created"]), f"{fdate(cl, a['first'])} – {fdate(cl, now)}", P["sampling_v"]]
    ilw = max(108, max(c.measure(lab, 11.5, "m") for lab in P["info_l"]) + 8)
    for k, (lab, val) in enumerate(zip(P["info_l"], vals)):
        col, row = divmod(k, 3)
        x, y = 36 + col * 480, 156 + row * 22
        c.text(x, y, lab, 11.5, "m", MUTE)
        c.text(x + ilw, y, ":", 11.5, "m", MUTE)
        c.text(x + ilw + 14, y, val, c.fit(val, 12.5, 456 - ilw - 14, "m b"), "m b", INK)
    cols = [(30, 64), (64, 380), (380, 520), (520, 640), (640, 760), (760, 900), (900, 970)]
    ty = 230
    c.rect(30, ty, 940, 42, fill=INK)
    for (x0, x1), pl, sl in zip(cols, P["cols"], S["cols"]):
        left = x0 == 64
        tx, anc = (x0 + 10, "start") if left else ((x0 + x1) / 2, "middle")
        mw = x1 - x0 - 12
        c.text(tx, ty + 19, pl, c.fit(pl, 11.5, mw, "m b"), "m b", PAPER, anc)
        if sl:
            c.text(tx, ty + 35, sl, c.fit(sl, 13, mw, "s i"), "s i", LINE, anc)
    lang, share = (a["langs"][0] if a["langs"] else ("—", 0))
    pk = dt.date.fromisoformat(a["peak"]["date"])
    u = P["u"]
    vals = [
        (num(a["total"]), u["contrib"], "≥ 365", "IK-SB/01", a["total"] >= 365),
        (dec(cl, a["mean"]), u["perday"], f"≥ {dec(cl, 1.0)}", "IK-SB/02", a["mean"] >= 1),
        (str(a["current"]), u["days"], "—", "IK-SB/03", None),
        (str(a["longest"]), u["days"], "≥ 7", "IK-SB/03", a["longest"] >= 7),
        (num(a["peak"]["count"]), fdate(cl, pk), "—", "IK-SB/04", None),
        (days[a["busiest"]] if a["busiest"] is not None else "—", "—", "—", "IK-SB/05", None),
        (lang, f"{dec(cl, share * 100)} %", "—", "Linguist", None),
        ("∞", u["cups"], P["l_notreg"], P["m_organo"], "*"),
        ("< LoD", u["release"], "0", P["m_pentest"], "*"),
    ]
    y = ty + 42
    sec = [r.rstrip("*") if L not in ("en", "id") else r for r in S["rows"]]
    for k, (pname, sname, (res, unit, lim, met, ok)) in enumerate(zip(P["rows"], sec, vals)):
        if k % 2:
            c.rect(30, y, 940, 36, fill=PAPER2, opacity=".75")
        c.text(47, y + 23, str(k + 1), 11.5, "m", MUTE, "middle")
        c.text(74, y + 16, pname, c.fit(pname, 12.5, 296, "m b"), "m b", INK)
        c.text(74, y + 31, sname, c.fit(sname, 12.5, 296, "s i"), "s i", MUTE)
        c.text(450, y + 23, res, c.fit(res, 14 if len(res) < 9 else 13, 128, "m b"), "m b", RED if ok == "*" else INK, "middle")
        c.text(580, y + 23, unit, c.fit(unit, 11, 112, "m"), "m", INK, "middle")
        c.text(700, y + 23, lim, c.fit(lim, 11, 112, "m"), "m", INK, "middle")
        c.text(830, y + 23, met, c.fit(met, 11, 132, "m"), "m", MUTE, "middle")
        if ok is True:
            c.check(928, y + 18)
        elif ok is False:
            c.cross(930, y + 19)
        else:
            c.text(935, y + 23, ok or "—", 12, "m b", RED if ok else MUTE, "middle")
        y += 36
    c.line(30, y, 970, y, stroke=INK, stroke_width=1.6)
    for x in (64, 380, 520, 640, 760, 900):
        c.line(x, ty + 42, x, y, stroke=LINE, stroke_width=.8)
    for k, n in enumerate(t["notes"]):
        c.text(36, y + 28 + k * 18, n, c.fit(n, 11.5, 630, "m"), "m", MUTE)
    sx = 700
    c.text(sx, y + 28, t["approved"], c.fit(t["approved"], 10.5, 260, "m"), "m", MUTE)
    c.add(c.mirrored(f'<path d="M{sx + 6} {y + 74}c8-26 20-40 26-30s-10 34-2 30 16-30 24-28-6 26 2 24 14-20 22-18-2 16 8 14 22-8 30-6 18 2 40-4" '
                     f'fill="none" stroke="{INK}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>'))
    c.line(sx, y + 86, sx + 230, y + 86, stroke=INK, stroke_width=1)
    c.text(sx, y + 102, "R. N. Adipratama", 12, "m b", INK)
    c.text(sx, y + 118, t["sig_title"], c.fit(t["sig_title"], 10, 262, "m"), "m", MUTE)
    stamp(c, c.X(sx + 178), y + 62, 48, f"{now:%d.%m.%Y}")
    c.border()
    c.defs.append('<filter id="worn" x="-25%" y="-25%" width="150%" height="150%"><feTurbulence type="fractalNoise" baseFrequency=".75" numOctaves="2" seed="3" result="n"/>'
                  '<feDisplacementMap in="SourceGraphic" in2="n" scale="2.4" xChannelSelector="R" yChannelSelector="G" result="d"/>'
                  '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.1 0 0 0 1.5" result="m"/>'
                  '<feComposite in="d" in2="m" operator="in"/></filter>')
    return c.render(f"Laporan Hasil Uji — {num(a['total'])} · {a['longest']}")


# ─────────────────────────────── PERIODIC TABLE ───────────────────────
def build_elements(d, a, now, L):
    t = T[L]
    c = Canvas(1000, 384, L)
    c.paper()
    c.rich(36, 56, [("Tabel Periodik ", 32, "s", INK), ("Reagen", 32, "s i", RED)])
    c.text(964, 50, t["el_mass"], c.fit(t["el_mass"], 10.5, 520, "m b", 1.5), "m b", RED, "end", ls=1.5)
    sub = t["el_assayed"].format(n=d.get("repos_analyzed", "?"))
    c.text(964, 66, sub, c.fit(sub, 10.5, 520, "m"), "m", MUTE, "end")
    langs = a["langs"][:MAX_ELEMENTS]
    tw_, th, gap = 110, 124, 8
    x = (c.W - (len(langs) * tw_ + (len(langs) - 1) * gap)) / 2
    top = langs[0][1] if langs else 1
    for k, (name, share) in enumerate(langs):
        lead = k == 0
        fill, fg, sub_c = (RED, PAPER, PAPER) if lead else (PAPER, INK, MUTE)
        sym = SYMBOLS.get(name, name[:2].title())
        c.add(f'<g class="el" style="animation-delay:{k * .09:.2f}s">')
        c.rect(x, 92, tw_, th, rx=4, fill=fill, stroke=INK, stroke_width=1.5)
        c.text(x + 10, 110, str(k + 1), 11, "m b", fg)
        c.text(x + tw_ - 10, 110, dec(L, share * 100), 10.5, "m", sub_c, "end")
        c.text(x + tw_ / 2, 166, sym, 50, "s", fg, "middle")
        c.text(x + tw_ / 2, 188, name if len(name) <= 13 else name[:12] + "…", 11, "m", fg, "middle")
        c.rect(x + 10, 200, tw_ - 20, 4, fill=fg, opacity=".18")
        c.rect(x + 10, 200, max(1.5, (tw_ - 20) * share / top), 4, fill=PAPER if lead else RED)
        c.add("</g>")
        x += tw_ + gap
    label = t["el_tools"]
    lw = c.measure(label, 10.5, "m b", 2)
    c.text(36, 252, label, 10.5, "m b", RED, ls=2)
    c.line(36 + lw + 14, 248, 964, 248, stroke=RED, stroke_width=1, stroke_dasharray="2 4")
    tw2, th2 = 96, 86
    x = (c.W - (len(TOOLS) * tw2 + (len(TOOLS) - 1) * gap)) / 2
    for k, (sym, name) in enumerate(TOOLS):
        c.add(f'<g class="el" style="animation-delay:{.75 + k * .06:.2f}s">')
        c.rect(x, 264, tw2, th2, rx=4, fill=PAPER2, stroke=INK, stroke_width=1.2, stroke_dasharray="4 2.5")
        c.text(x + 9, 280, str(len(langs) + k + 1), 10, "m b", INK)
        c.text(x + tw2 / 2, 318, sym, 34, "s", INK, "middle")
        c.text(x + tw2 / 2, 338, name, 10, "m", MUTE, "middle")
        c.add("</g>")
        x += tw2 + gap
    last = t["last_assay"].format(date=fdate(L, now), time=f"{now:%H:%M}")
    c.text(964, 372, last, c.fit(last, 10, 600, "m"), "m", MUTE, "end")
    c.border()
    c.css = "@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}.el{animation:rise .7s cubic-bezier(.2,.7,.2,1) both}"
    return c.render("Tabel Periodik Reagen — " + ", ".join(n for n, _ in langs))


# ─────────────────────────────── CHROMATOGRAM ─────────────────────────
def build_chroma(d, a, now, L):
    t = T[L]
    c = Canvas(1000, 368, L)
    x0, x1, yt, yb = 70, 960, 96, 292
    days = a["days"][-CHROMA_DAYS:]
    N = len(days)
    c.paper()
    c.rich(36, 56, [("Kromatogram ", 32, "s", INK), (t["ch_sub"], 32, "s i", RED)])
    c.text(964, 50, t["ch_det"], c.fit(t["ch_det"], 10.5, 420, "m b", 1.5), "m b", RED, "end", ls=1.5)
    col = t["ch_col"].format(user=USER, n=N)
    c.text(964, 66, col, c.fit(col, 10.5, 460, "m"), "m", MUTE, "end")
    for k in range(1, 5):
        gy = yb - (yb - yt) * k / 4
        c.line(x0, gy, x1, gy, mirror=False, stroke=LINE, stroke_width=.8, stroke_dasharray="2 5")
    dx = (x1 - x0) / max(N, 1)
    for i, day in enumerate(days):
        dd = dt.date.fromisoformat(day["date"])
        if dd.day in (1, 15):
            xx = x0 + (i + .5) * dx
            c.line(xx, yb, xx, yb + 6, mirror=False, stroke=INK, stroke_width=1)
            lab = fdate(L, dd, short=True)
            c.text(xx, yb + 20, lab, c.fit(lab, 10, 56, "m"), "m", MUTE, "middle", mirror=False)
    c.add(f'<path d="M{x0} {yt - 6}V{yb}H{x1 + 6}" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    c.text(x1, yb + 40, t["ch_x"], 10, "m", MUTE, "end", mirror=False)
    c.text(48, (yt + yb) / 2, t["ch_y"], 10, "m", MUTE, "middle", mirror=False, rot=-90)
    S = 8
    hs = [x["count"] ** .75 for x in days]
    mx = max(hs) if hs and max(hs) > 0 else 1
    amp = (yb - yt) * .6 / mx
    pts = []
    for s in range(N * S + 1):
        tt = s / S
        v = 0.0
        for i in range(max(0, int(tt) - 3), min(N, int(tt) + 4)):
            if hs[i]:
                u = tt - (i + .5)
                sg = .2 if u < 0 else .34
                v += hs[i] * math.exp(-(u * u) / (2 * sg * sg))
        noise = .55 * math.sin(s * 1.7) * math.sin(s * .37 + 1) + .3 * math.sin(s * 5.3)
        pts.append((x0 + tt * dx, yb - 1.5 - v * amp + noise))
    line = "M" + "L".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    area = line + f"L{x1:.1f} {yb}L{x0} {yb}Z"
    c.add(f'<clipPath id="plot"><rect x="{x0 + 1}" y="{yt - 8}" width="{x1 - x0}" height="{yb - yt + 7}"/></clipPath>'
          f'<g clip-path="url(#plot)"><path d="{area}" fill="{RED}" opacity=".16"><animate attributeName="opacity" values="0;0;.16" keyTimes="0;.6;1" dur="3.6s" fill="freeze"/></path>'
          f'<path d="{line}" fill="none" stroke="{INK}" stroke-width="1.35" stroke-linejoin="round" pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="0">'
          f'<animate attributeName="stroke-dashoffset" values="1000;0" dur="3.2s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".45 0 .25 1"/></path></g>')
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
        lab = f"{days[i]['count']} · {fdate(L, dd, short=True)}"
        c.line(px, py + 3, px, yb, mirror=False, stroke=RED, stroke_width=.9, stroke_dasharray="1.5 2.5", opacity=".7")
        c.text(px + 3.5, py - 6, lab, c.fit(lab, 9.5, py - 6 - yt + 4, "m b"), "m b", RED_D, "start", mirror=False, rot=-90)
    c.add(f'<line x1="{x0}" x2="{x0}" y1="{yt}" y2="{yb}" stroke="{RED}" stroke-width="1.2" opacity=".5">'
          f'<animate attributeName="x1" values="{x0};{x1}" dur="9s" begin="3.4s" repeatCount="indefinite"/>'
          f'<animate attributeName="x2" values="{x0};{x1}" dur="9s" begin="3.4s" repeatCount="indefinite"/></line>')
    c.circle(x0 + 14, yt + 4, 3.6, mirror=False, fill=RED,
             inner='<animate attributeName="opacity" values="1;1;.15;.15" keyTimes="0;.5;.5;1" dur="1.4s" repeatCount="indefinite"/>')
    c.text(x0 + 23, yt + 8, "REC", 10, "m b", RED, ls=1.5, mirror=False)
    win = sum(x["count"] for x in days)
    big = sum(1 for x in days if x["count"] >= 20)
    summ = t["ch_sum"].format(n=N, win=num(win, L), big=big, max=num(a["peak"]["count"], L),
                              date=fdate(L, dt.date.fromisoformat(a["peak"]["date"])))
    c.text(36, c.H - 18, summ, c.fit(summ, 11.5, 928, "m"), "m", INK)
    c.border()
    return c.render(f"Kromatogram — {N} d: {num(win)}")


# ─────────────────────────────── SAMPLE CARDS ─────────────────────────
def wrap(c, s, width, size, lines=2):
    toks = re.findall(r"\s+|[^\s　-鿿＀-￯]+|[　-鿿＀-￯]", s)
    out, cur = [], ""
    for tok in toks:
        cand = cur + tok
        if tok in "，。：；！？）」』、”’" or not cur.strip():  # never start a line with closing punctuation
            cur = cand
        elif c.measure(cand.strip(), size) > width:
            out.append(cur.strip())
            cur = tok.lstrip()
        else:
            cur = cand
    out.append(cur.strip())
    if len(out) > lines:
        out = out[:lines]
        out[-1] = out[-1].rstrip(" .,。") + "…"
    return out


def build_sample(k, full, code, desc, info, L):
    c = Canvas(490, 180, L)
    W, H = c.W, c.H
    name = full.split("/")[1]
    c.paper(rx=10, cid="c")
    c.add(f'<g clip-path="url(#c)"><rect x="{c.RX(0, 42)}" y="0" width="42" height="{H}" fill="{RED}"/></g>')
    c.line(42, 0, 42, H, stroke=INK, stroke_width=1.4)
    band = f"{T[L]['s_sample']} {k + 1:02d}"
    c.text(21, H / 2 + 4, band, c.fit(band, 11, 160, "m b", 3), "m b", PAPER, "middle", ls=3, rot=-90)
    c.text(62, 34, f"SB-S{k + 1:02d} · {code}", 10.5, "m b", RED, ls=1.5)
    tag = "LIVE ↗" if info.get("homepage") else "REPO ↗"
    tgw = c.measure(tag, 10, "m b") + 16
    live = tag.startswith("LIVE")
    c.rect(W - 20 - tgw, 20, tgw, 19, rx=9.5, fill=INK if live else "none", stroke=INK, stroke_width=1.2)
    c.text(W - 20 - tgw / 2, 33.5, tag, 10, "m b", PAPER if live else INK, "middle")
    c.text(61, 72, name, round(min(30, 400 / max(c.measure(name, 1, "s"), 1)), 1), "s", INK)
    for j, ln in enumerate(wrap(c, desc, 404, 11.5)):
        c.text(62, 98 + j * 17, ln, c.fit(ln, 11.5, 410), "m", INK)
    c.line(62, 134, W - 20, 134, stroke=LINE, stroke_width=1, stroke_dasharray="3 3")
    pushed = info.get("pushed_at")
    last = fdate(L, dt.datetime.fromisoformat(pushed.replace("Z", "+00:00")).astimezone(TZ).date()) if pushed else "—"
    lang = info.get("language") or "—"
    c.circle(66, 155, 4, fill=RED)
    c.text(76, 159, lang, 11, "m b", INK)
    lx = 76 + c.measure(lang, 11, "m b") + 16
    lab = T[L]["s_last"]
    avail = W - 140 - lx  # room before the barcode
    date_size = c.fit(last, 11, avail * .55, "m b")
    lab_size = c.fit(lab, 9.5, avail - c.measure(last, date_size, "m b") - 10, "m", 1)
    c.text(lx, 159, lab, lab_size, "m", MUTE, ls=1)
    c.text(lx + c.measure(lab, lab_size, "m", 1) + 10, 159, last, date_size, "m b", INK)
    c.barcode(W - 128, 146, 108, 18, full)
    c.border(rx=10)
    return c.render(f"{name}: {desc}")


# ─────────────────────────────── FOOTER & PILLS ───────────────────────
def build_footer(d, a, now, L):
    c = Canvas(1000, 96, L)
    c.paper()
    c.key_band(20)
    s = T[L]["footer"].format(date=fdate(L, now), time=f"{now:%H:%M}")
    c.text(500, 74, s, c.fit(s, 11, 930, "m"), "m", INK, "middle")
    c.border()
    return c.render("sedotan bekas")


def build_pill(L, on):
    c = Canvas(400, 34, L, mirror=False)
    code, native = L.upper(), T[L]["native"]
    wc, wn = c.measure(code, 11, "m b", 1.5), c.measure(native, 16, "s")
    W = math.ceil(14 + wc + 9 + wn + 16)
    c.W = W
    bg, fg, accent = (RED, PAPER, PAPER) if on else (PAPER, INK, RED)
    c.add(f'<rect x="1" y="1" width="{W - 2}" height="32" rx="16" fill="{bg}" stroke="{INK}" stroke-width="1.4"/>')
    c.text(14, 21, code, 11, "m b", accent, ls=1.5)
    c.text(14 + wc + 9, 23, native, 16, "s", fg)
    return c.render(native, grain=False)


# ─────────────────────────────── README ───────────────────────────────
def readme(L):
    t = T[L]
    root = L == "en"
    pre = "" if root else "../"
    link = (lambda o: ("README.md" if o == "en" else f"i18n/README.{o}.md")) if root else \
           (lambda o: ("../README.md" if o == "en" else f"README.{o}.md"))
    pills = "\n".join(f'  <a href="{link(o)}"><img src="{pre}assets/lang/{o}{"-on" if o == L else ""}.svg" height="25" alt="{t_native(o)}"></a>'
                      for o in LANGS)
    img = lambda f, alt, w="100%": f'<img src="{pre}assets/{L}/{f}" width="{w}" alt="{esc(alt)}">'  # noqa: E731
    cards = []
    for k, (full, _, url) in enumerate(FEATURED):
        repo = full.split("/")[1]
        cards.append(f'  <a href="{url}">' + img(f"samples/{repo}.svg", repo + ": " + t["s_desc"][k], "49%") + "</a>")
    cards = "\n".join(cards)
    body = f"""<p align="center">
  {img("header.svg", f"{NAME_FIRST} {NAME_LAST} — {t['role_v']}")}
</p>

<p align="center">
  <sub>{t['md_caption']}</sub>
</p>

### `{t['md_abs_h']}`

{t['md_abs']}

<p align="center">
  {img("coa.svg", "Laporan Hasil Uji — " + t['coa_sub'])}
</p>

<p align="center">
  {img("elements.svg", t['alt_el'])}
</p>

<p align="center">
  {img("chromatogram.svg", t['alt_ch'])}
</p>

### `{t['md_samples_h']}`

<p align="center">
{cards}
</p>

<p align="center">
  {img("footer.svg", "sedotan bekas")}
</p>
"""
    if t["dir"] == "rtl":
        body = f'<div dir="rtl">\n\n{body}\n</div>\n'
    return (f"<!--\n  LAPORAN HASIL UJI · sedotanbekas · {t['native']}\n"
            f"  Generated by scripts/build.py — edit scripts/i18n.py (copy) or the CONFIG block in build.py, not this file.\n-->\n\n"
            f'<p align="center">\n{pills}\n</p>\n\n{body}')


def t_native(o):
    return T[o]["native"]


# ─────────────────────────────── MAIN ─────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", help="build offline from a saved snapshot JSON")
    ap.add_argument("--save-snapshot", help="write the fetched data to this JSON file")
    ap.add_argument("--now", help="override the build time (ISO 8601), for previews")
    ap.add_argument("--langs", help="comma-separated subset of: " + ",".join(LANGS))
    ap.add_argument("--no-readme", action="store_true", help="don't (re)write the README files")
    args = ap.parse_args()
    if not (HAVE_FT and HAVE_HB):
        print("note: fonttools/uharfbuzz not installed — embedding whole fonts, estimating widths", file=sys.stderr)
    d = json.loads(Path(args.snapshot).read_text("utf-8")) if args.snapshot else fetch_live()
    if args.save_snapshot:
        Path(args.save_snapshot).write_text(json.dumps(d, indent=1), "utf-8")
    now = dt.datetime.fromisoformat(args.now).astimezone(TZ) if args.now else dt.datetime.now(TZ)
    a = analyze(d, now)
    langs = args.langs.split(",") if args.langs else LANGS
    total = 0
    for L in langs:
        out = {"header.svg": build_header(d, a, now, L), "coa.svg": build_coa(d, a, now, L),
               "elements.svg": build_elements(d, a, now, L), "chromatogram.svg": build_chroma(d, a, now, L),
               "footer.svg": build_footer(d, a, now, L)}
        for k, (full, code, _) in enumerate(FEATURED):
            out[f"samples/{full.split('/')[1]}.svg"] = build_sample(k, full, code, T[L]["s_desc"][k], d.get("featured", {}).get(full, {}), L)
        (ASSETS / L / "samples").mkdir(parents=True, exist_ok=True)
        size = 0
        for name, content in out.items():
            (ASSETS / L / name).write_text(content, "utf-8")
            size += len(content.encode())
        total += size
        print(f"  ✓ assets/{L}/  {len(out)} SVGs  {size / 1024:7.1f} KB")
    (ASSETS / "lang").mkdir(parents=True, exist_ok=True)
    for L in LANGS:
        (ASSETS / "lang" / f"{L}.svg").write_text(build_pill(L, False), "utf-8")
        (ASSETS / "lang" / f"{L}-on.svg").write_text(build_pill(L, True), "utf-8")
    if not args.no_readme:
        (ROOT / "i18n").mkdir(exist_ok=True)
        for L in LANGS:
            (ROOT / ("README.md" if L == "en" else f"i18n/README.{L}.md")).write_text(readme(L), "utf-8")
    print(f"total {total / 1024:.0f} KB · contributions {a['total']} · longest {a['longest']} · current {a['current']} · top {a['langs'][:2]}")


if __name__ == "__main__":
    main()
