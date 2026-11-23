#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dev tool: (re)build the per-script source font subsets in assets/fonts/src/
and their width metrics (assets/fonts/metrics.json).

Run it after changing translations that add new characters:

    npm i jetbrains-mono @fontsource/instrument-serif \
          @expo-google-fonts/{pt-serif,noto-sans-sc,noto-serif-sc,noto-sans-devanagari,tiro-devanagari-hindi} \
          @expo-google-fonts/{noto-sans-bengali,tiro-bangla,noto-sans-arabic,noto-naskh-arabic}
    pip install fonttools brotli uharfbuzz
    python scripts/fonts.py --node-modules ./node_modules

build.py then subsets these again per SVG at build time (when fontTools is
installed), so each image only carries the glyphs it actually shows.
"""
import argparse
import json
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i18n  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "fonts" / "src"

EXPO = "@expo-google-fonts"
# face id -> (path inside node_modules, which languages feed its character set)
FACES = {
    "jb-400": ("jetbrains-mono/fonts/webfonts/JetBrainsMonoNL-Regular.woff2", "all"),
    "jb-700": ("jetbrains-mono/fonts/webfonts/JetBrainsMonoNL-Bold.woff2", "all"),
    "is-400": ("@fontsource/instrument-serif/files/instrument-serif-latin-400-normal.woff2", "all"),
    "is-400i": ("@fontsource/instrument-serif/files/instrument-serif-latin-400-italic.woff2", "all"),
    "ru-s-400": (f"{EXPO}/pt-serif/400Regular/PTSerif_400Regular.ttf", ["ru"]),
    "ru-s-400i": (f"{EXPO}/pt-serif/400Regular_Italic/PTSerif_400Regular_Italic.ttf", ["ru"]),
    "zh-m-400": (f"{EXPO}/noto-sans-sc/400Regular/NotoSansSC_400Regular.ttf", ["zh"]),
    "zh-m-700": (f"{EXPO}/noto-sans-sc/700Bold/NotoSansSC_700Bold.ttf", ["zh"]),
    "zh-s-400": (f"{EXPO}/noto-serif-sc/400Regular/NotoSerifSC_400Regular.ttf", ["zh"]),
    "hi-m-400": (f"{EXPO}/noto-sans-devanagari/400Regular/NotoSansDevanagari_400Regular.ttf", ["hi"]),
    "hi-m-700": (f"{EXPO}/noto-sans-devanagari/700Bold/NotoSansDevanagari_700Bold.ttf", ["hi"]),
    "hi-s-400": (f"{EXPO}/tiro-devanagari-hindi/400Regular/TiroDevanagariHindi_400Regular.ttf", ["hi"]),
    "hi-s-400i": (f"{EXPO}/tiro-devanagari-hindi/400Regular_Italic/TiroDevanagariHindi_400Regular_Italic.ttf", ["hi"]),
    "bn-m-400": (f"{EXPO}/noto-sans-bengali/400Regular/NotoSansBengali_400Regular.ttf", ["bn"]),
    "bn-m-700": (f"{EXPO}/noto-sans-bengali/700Bold/NotoSansBengali_700Bold.ttf", ["bn"]),
    "bn-s-400": (f"{EXPO}/tiro-bangla/400Regular/TiroBangla_400Regular.ttf", ["bn"]),
    "bn-s-400i": (f"{EXPO}/tiro-bangla/400Regular_Italic/TiroBangla_400Regular_Italic.ttf", ["bn"]),
    "ar-m-400": (f"{EXPO}/noto-sans-arabic/400Regular/NotoSansArabic_400Regular.ttf", ["ar"]),
    "ar-m-700": (f"{EXPO}/noto-sans-arabic/700Bold/NotoSansArabic_700Bold.ttf", ["ar"]),
    "ar-s-400": (f"{EXPO}/noto-naskh-arabic/400Regular/NotoNaskhArabic_400Regular.ttf", ["ar"]),
}
ASCII = "".join(chr(c) for c in range(0x20, 0x7F))
SYMBOLS = "·—–→←↑↓↗°×±≥≤µ∞✓✗▲▼…’“”‘■□●◆≈∑Δλ▸▪│─«»№ "
SCRIPT_PUNCT = "  ·—–:;,.()/%*-…"  # kept in script fonts so spaces/punctuation inside script text match it


def is_latin(ch):
    o = ord(ch)
    return o < 0x250 or 0x1E00 <= o < 0x1F00 or 0x2000 <= o < 0x2400 or 0x2500 <= o < 0x27C0


def is_cyr(ch):
    return 0x400 <= ord(ch) < 0x530


def lang_chars(langs):
    chars = set()
    for L in langs:
        chars |= set(i18n.all_text(L)) | set(i18n.T[L]["native"])
    return chars


def words_for(langs):
    out = set()
    for L in langs:
        for w in (i18n.all_text(L) + " " + i18n.T[L]["native"]).split():
            if any(not is_latin(c) for c in w):
                out.add(w)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node-modules", required=True)
    nm = Path(ap.parse_args().node_modules)
    OUT.mkdir(parents=True, exist_ok=True)
    import uharfbuzz as hb
    every = lang_chars(i18n.LANGS) | set(ASCII + SYMBOLS)
    metrics = {}
    for face, (rel, langs) in FACES.items():
        f = TTFont(nm / rel)
        cmap = f.getBestCmap()
        if langs == "all":  # Latin primaries (JetBrains Mono also carries Cyrillic)
            mono = face.startswith("jb")
            chars = {c for c in every if is_latin(c) or (mono and is_cyr(c))}
            gids = set()
        else:
            # pill labels (native names) are rendered in the serif face of their own script
            chars = {c for c in lang_chars(langs) if not is_latin(c)} | set(SCRIPT_PUNCT)
            raw = (nm / rel).read_bytes()
            hf = hb.Font(hb.Face(raw))
            gids = set()
            for w in words_for(langs):
                buf = hb.Buffer()
                buf.add_str(w)
                buf.guess_segment_properties()
                hb.shape(hf, buf, {})
                gids |= {i.codepoint for i in buf.glyph_infos}
        keep = "".join(sorted(c for c in chars if ord(c) in cmap))
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.name_IDs = ["*"]
        opts.notdef_outline = True
        opts.hinting = False
        if gids:
            opts.layout_closure = False
        sub = subset.Subsetter(opts)
        sub.populate(text=keep, gids=sorted(gids))
        sub.subset(f)
        f.save(OUT / f"{face}.woff2")
        cm, hm = f.getBestCmap(), f["hmtx"]
        metrics[face] = {"upm": f["head"].unitsPerEm, "w": {c: hm[cm[ord(c)]][0] for c in keep if ord(c) in cm}}
        print(f"{face:<10} {len(keep):5d} chars {len(f.getGlyphOrder()):5d} glyphs {(OUT / f'{face}.woff2').stat().st_size / 1024:7.1f} KB")
    (ROOT / "assets" / "fonts" / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, separators=(",", ":")), "utf-8")


if __name__ == "__main__":
    main()
