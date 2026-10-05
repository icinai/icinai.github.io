#!/usr/bin/env python3
"""Build the ICINAi logo assets.

Text is converted to outlines, so the SVGs do not depend on any installed font.
Requires: numpy, fonttools, playwright (for PNG renders), Pillow (for favicon.ico).
Font: Manrope (SIL OFL), e.g. `npm pack @fontsource/manrope`;
pass the folder holding manrope-latin-{500,800}-normal.woff as argv[1].
"""
import os, sys, json
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT_DIR = sys.argv[1] if len(sys.argv) > 1 else 'font'
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# ---------------------------------------------------------------- palette
NAVY, WHITE, BLACK = '#0F172A', '#FFFFFF', '#000000'
P1, P2, P3 = '#B875B1', '#838CC1', '#4EA3D1'          # NDIF brand gradient
TAG_ON_DARK, TAG_ON_LIGHT = '#94A3B8', '#475569'

# ---------------------------------------------------------------- geometry
# Units: font size 100, baseline y=100. All geometry is derived from the font's metrics, so the
# wordmark can be rebuilt in another typeface by changing WORD_FONT.
from fontTools.pens.boundsPen import BoundsPen

WORD_FONT = os.path.join(FONT_DIR, 'manrope-latin-800-normal.woff')   # wordmark: Manrope ExtraBold
TAG_FONT = os.path.join(FONT_DIR, 'manrope-latin-500-normal.woff')    # tagline: Manrope Medium
SPACING = -3

def comet(cx, cy, rx, ry, xs, R, c1, c2, D, w0, wpk, wend, n=110, m=34):
    """Tapered orbit: elliptical arc from above the A, counterclockwise round the
    word, then a cubic curl that joins the top of the head ring tangentially."""
    phiS = np.arccos((xs - cx) / rx)
    phi = np.linspace(phiS, 2 * np.pi, n)
    A = np.c_[cx + rx * np.cos(phi), cy - ry * np.sin(phi)]
    t = np.linspace(0, 1, m)[1:]
    P0, P1_, P2_, P3_ = map(np.array, (R, c1, c2, D))
    B = (((1 - t) ** 3)[:, None] * P0 + (3 * (1 - t) ** 2 * t)[:, None] * P1_
         + (3 * (1 - t) * t ** 2)[:, None] * P2_ + (t ** 3)[:, None] * P3_)
    P = np.concatenate([A, B])
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    s /= s[-1]
    grow = w0 + (wpk - w0) * np.clip(s / 0.8, 0, 1) ** 1.6
    k = np.clip((s - 0.8) / 0.2, 0, 1)
    k = k * k * (3 - 2 * k)
    w = grow * (1 - k) + wend * k
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1)[:, None]
    N = np.c_[-T[:, 1], T[:, 0]]
    pts = np.concatenate([P + N * (w / 2)[:, None], (P - N * (w / 2)[:, None])[::-1]])
    return 'M' + ' '.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'


def text_path(fontfile, text, size, x0, baseline, spacing):
    f = TTFont(fontfile)
    upem = f['head'].unitsPerEm
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f['hmtx']
    sc = size / upem
    x, d = x0, []
    for ch in text:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, x, baseline)))
        d.append(pen.getCommands())
        x += hmtx[g][0] * sc + spacing
    return ' '.join(d), x - spacing - x0



def _metrics(fontfile, text, spacing):
    f = TTFont(fontfile)
    sc = 100 / f['head'].unitsPerEm
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f['hmtx']
    x, inks = 0, []
    for ch in text:
        g = cmap[ord(ch)]
        bp = BoundsPen(gs)
        gs[g].draw(bp)
        inks.append((x + bp.bounds[0] * sc, x + bp.bounds[2] * sc))
        x += hmtx[g][0] * sc + spacing
    bp = BoundsPen(gs)
    gs[cmap[ord('I')]].draw(bp)
    stem_w = (bp.bounds[2] - bp.bounds[0]) * sc
    return inks, stem_w, f['OS/2'].sxHeight * sc


WORD, _ = text_path(WORD_FONT, 'ICINA', 100, 0, 100, SPACING)
_INKS, SW, XH = _metrics(WORD_FONT, 'ICINA', SPACING)
WORD_L, (A_L, A_R) = _INKS[0][0], _INKS[4]

# The i: a stem the weight of the I, ~35% shorter than a normal i so it reads as a small figure
# beside the A, topped by an eye (ring + pupil) that looks down and to the left at the A.
U = SW / 10.8                          # scale relative to the original design
SX0 = A_R + 5
SX1 = SX0 + SW
HX = (SX0 + SX1) / 2
STEM_TOP = 100 - 0.65 * XH
STEM = f'M{SX0:.1f} 100 V{STEM_TOP + SW / 2:.1f} A{SW / 2:.1f} {SW / 2:.1f} 0 0 1 {SX1:.1f} {STEM_TOP + SW / 2:.1f} V100 Z'
HY = STEM_TOP - 16 * U
HEAD = (round(HX, 2), round(HY, 2), 0.83 * SW, 0.22 * SW, 0.43 * SW)   # cx, cy, ring r, ring stroke, core r
GAZE = (-2.4 * U, 1.4 * U)

# Orbit: from above the A, counterclockwise round the word, curling into the top of the eye.
OCX = (WORD_L + SX1) / 2
ORX = (SX1 - WORD_L) / 2 + 45.5
_TOP = HY - HEAD[2]
ORBIT = comet(OCX, 66, ORX, 72, (A_L + A_R) / 2 - 5, (OCX + ORX, 66), (OCX + ORX, 48),
              (HX + 25.4, _TOP), (HX, _TOP), 0.5, 7.5, HEAD[3])
GRAD_X = (OCX - ORX, OCX + ORX)        # brand gradient spans the orbit
FADE_X = (0, SX0)                      # letters fade into the gradient toward the i

LOGO_VB = (round(OCX - ORX - 14), -12, round(2 * ORX + 28), 158)
LOCKUP_VB = (LOGO_VB[0], -12, LOGO_VB[2], 196)

TAGLINE = 'International Consortium for Interpretable AI'
TAG_SIZE = 12.5
_, tw = text_path(TAG_FONT, TAGLINE, TAG_SIZE, 0, 0, TAG_SIZE * 0.04)
TAG, _ = text_path(TAG_FONT, TAGLINE, TAG_SIZE, (WORD_L + SX1) / 2 - tw / 2, 170, TAG_SIZE * 0.04)

# App icon: the i from the logo (eye and short body) with no orbit, centred in the tile.
_IB = 100                              # same proportions as the i in the logo
ICON_STEM = f'M{SX0:.1f} {_IB:.1f} V{STEM_TOP + SW / 2:.1f} A{SW / 2:.1f} {SW / 2:.1f} 0 0 1 {SX1:.1f} {STEM_TOP + SW / 2:.1f} V{_IB:.1f} Z'
ICON_HEAD = (HEAD[0], HEAD[1], HEAD[2], 0.24 * SW, HEAD[4])
_FW = SW * 1.2
FAV_STEM = f'M{HX - _FW / 2:.1f} {_IB:.1f} V{STEM_TOP + _FW / 2 + 1:.1f} A{_FW / 2:.1f} {_FW / 2:.1f} 0 0 1 {HX + _FW / 2:.1f} {STEM_TOP + _FW / 2 + 1:.1f} V{_IB:.1f} Z'
FAV_HEAD = (HEAD[0], HEAD[1] - 0.5, HEAD[2] * 1.07, 0.37 * SW, HEAD[4] * 1.06)
ICON_CY = ((HY - HEAD[2]) + _IB) / 2   # vertical centre of the figure
ICON_H = _IB - (HY - HEAD[2])


# ---------------------------------------------------------------- svg helpers
def grad(id_, x1, x2, stops, y1=0, y2=0):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return (f'<linearGradient id="{id_}" gradientUnits="userSpaceOnUse" '
            f'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>')

BRAND = [(0, P1), (0.5, P2), (1, P3)]


def head(h, fill, gaze=GAZE):
    cx, cy, r, sw, core = h
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{fill}" stroke-width="{sw}"/>'
            f'<circle cx="{cx + gaze[0]}" cy="{cy + gaze[1]}" r="{core}" fill="{fill}"/>')


def svg(viewbox, body, title):
    vb = ' '.join(str(v) for v in viewbox)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{body}</svg>\n')



# variant -> (letters fill, mark fill, tagline fill, defs)
VARIANTS = {
    'color-on-dark': ('url(#fade)', 'url(#brand)', TAG_ON_DARK,
                      grad('brand', *GRAD_X, BRAND) +
                      grad('fade', *FADE_X, [(0, WHITE), (0.45, WHITE), (0.85, P1), (1, P2)])),
    'color-on-light': ('url(#fade)', 'url(#brand)', TAG_ON_LIGHT,
                       grad('brand', *GRAD_X, BRAND) +
                       grad('fade', *FADE_X, [(0, NAVY), (0.45, NAVY), (0.85, '#9A5C95'), (1, '#6E78B0')])),
    'gradient': ('url(#brand)', 'url(#brand)', P2, grad('brand', *GRAD_X, BRAND)),
    'black': (BLACK, BLACK, BLACK, ''),
    'white': (WHITE, WHITE, WHITE, ''),
}


def logo(variant, tagline=False):
    letters, mark, tag, defs = VARIANTS[variant]
    # unique gradient ids so several logos can be inlined in one HTML page
    pre = f'icinai-{variant}-{"lockup" if tagline else "logo"}-'
    letters, mark, defs = (x.replace('#fade', f'#{pre}fade').replace('#brand', f'#{pre}brand')
                           .replace('id="fade"', f'id="{pre}fade"').replace('id="brand"', f'id="{pre}brand"')
                           for x in (letters, mark, defs))
    body = (f'<defs>{defs}</defs>' if defs else '')
    body += (f'<path d="{ORBIT}" fill="{mark}"/>'
             f'<path d="{WORD}" fill="{letters}"/>'
             f'<path d="{STEM}" fill="{mark}"/>' + head(HEAD, mark))
    if tagline:
        body += f'<path d="{TAG}" fill="{tag}"/>'
    return svg(LOCKUP_VB if tagline else LOGO_VB, body,
               'ICINAi: International Consortium for Interpretable AI' if tagline else 'ICINAi')


def figure(fill, small=False):
    s = (68 if small else 62) / ICON_H
    stem, hd = (FAV_STEM, FAV_HEAD) if small else (ICON_STEM, ICON_HEAD)
    return (f'<g transform="translate(50 50) scale({s:.4f}) translate({-HX:.2f} {-ICON_CY:.2f})">'
            f'<path d="{stem}" fill="{fill}"/>{head(hd, fill, (GAZE[0], GAZE[1]))}</g>')


def app_icon(tile, fig, defs=''):
    body = (f'<defs>{defs}</defs>' if defs else '') + \
        f'<rect width="100" height="100" rx="24" fill="{tile}"/>' + figure(fig)
    return svg((0, 0, 100, 100), body, 'ICINAi')


def mark(fill, defs=''):
    body = (f'<defs>{defs}</defs>' if defs else '') + figure(fill)
    return svg((15, 15, 70, 70), body, 'ICINAi')


def favicon(tile, fig, defs=''):
    body = ((f'<defs>{defs}</defs>' if defs else '') +
            f'<rect width="100" height="100" rx="24" fill="{tile}"/>' + figure(fig, small=True))
    return svg((0, 0, 100, 100), body, 'ICINAi')


TILE_GRAD = grad('icinai-tile', 0, 100, BRAND, 0, 100)
MARK_GRAD = grad('icinai-mark', 30, 70, BRAND, 15, 85)

FILES = {}
for v in VARIANTS:
    FILES[f'logo/icinai-logo-{v}.svg'] = logo(v)
    FILES[f'logo/icinai-lockup-{v}.svg'] = logo(v, tagline=True)
FILES['icon/icinai-app-icon.svg'] = app_icon('url(#icinai-tile)', WHITE, TILE_GRAD)
FILES['icon/icinai-app-icon-navy.svg'] = app_icon(NAVY, WHITE)
FILES['icon/icinai-app-icon-black.svg'] = app_icon(BLACK, WHITE)
FILES['icon/icinai-app-icon-white.svg'] = app_icon(WHITE, BLACK)
FILES['icon/icinai-mark-gradient.svg'] = mark('url(#icinai-mark)', MARK_GRAD)
FILES['icon/icinai-mark-black.svg'] = mark(BLACK)
FILES['icon/icinai-mark-white.svg'] = mark(WHITE)
FILES['icon/favicon.svg'] = favicon('url(#icinai-tile)', WHITE, TILE_GRAD)
FILES['icon/favicon-black.svg'] = favicon(BLACK, WHITE)

for path, content in FILES.items():
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w').write(content)
print(f'wrote {len(FILES)} svg files')

# ---------------------------------------------------------------- PNG renders
if '--no-png' in sys.argv:
    sys.exit()
from playwright.sync_api import sync_playwright

RENDERS = []  # (svg path, png path, width px, background or None)
for v in VARIANTS:
    for kind in ('logo', 'lockup'):
        for w in (1200, 600):
            RENDERS.append((f'logo/icinai-{kind}-{v}.svg', f'png/icinai-{kind}-{v}-{w}.png', w, None))
for name in ('app-icon', 'app-icon-navy', 'app-icon-black', 'app-icon-white'):
    for w in (1024, 512, 192):
        RENDERS.append((f'icon/icinai-{name}.svg', f'png/icinai-{name}-{w}.png', w, None))
RENDERS.append(('icon/icinai-app-icon.svg', 'png/apple-touch-icon.png', 180, None))
for name in ('mark-gradient', 'mark-black', 'mark-white'):
    RENDERS.append((f'icon/icinai-{name}.svg', f'png/icinai-{name}-512.png', 512, None))
for w in (16, 32, 48):
    src = 'icon/favicon.svg' if w <= 32 else 'icon/icinai-app-icon.svg'
    RENDERS.append((src, f'png/favicon-{w}.png', w, None))

os.makedirs(os.path.join(OUT, 'png'), exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    for src, dst, w, bg in RENDERS:
        content = open(os.path.join(OUT, src)).read()
        vb = [float(x) for x in content.split('viewBox="')[1].split('"')[0].split()]
        h = round(w * vb[3] / vb[2])
        pg.set_viewport_size({'width': w, 'height': h})
        pg.set_content(f'<html><body style="margin:0;background:transparent">'
                       f'<div style="width:{w}px;height:{h}px">{content.replace("<svg ", f"<svg width=\"{w}\" height=\"{h}\" ", 1)}</div></body></html>')
        pg.screenshot(path=os.path.join(OUT, dst), omit_background=True,
                      clip={'x': 0, 'y': 0, 'width': w, 'height': h})

    # contact sheet for the README
    cells = []
    for v, bg in [('color-on-dark', NAVY), ('color-on-light', '#F8FAFC'), ('gradient', '#F8FAFC'),
                  ('gradient', NAVY), ('black', '#FFFFFF'), ('white', '#111111')]:
        cells.append(f'<div style="background:{bg};padding:28px;display:flex;align-items:center;'
                     f'justify-content:center;height:190px">'
                     f'{open(os.path.join(OUT, f"logo/icinai-lockup-{v}.svg")).read().replace("<svg ", "<svg height=\"170\" ", 1)}</div>')
    icons = ''.join(
        f'<div style="padding:10px">{open(os.path.join(OUT, f)).read().replace("<svg ", f"<svg width=\"{s}\" height=\"{s}\" ", 1)}</div>'
        for f, s in [('icon/icinai-app-icon.svg', 120), ('icon/icinai-app-icon-navy.svg', 120),
                     ('icon/icinai-app-icon-black.svg', 120), ('icon/icinai-app-icon-white.svg', 120),
                     ('icon/icinai-app-icon.svg', 48), ('icon/favicon.svg', 32), ('icon/favicon.svg', 16)])
    sheet = (f'<html><body style="margin:0;font-family:sans-serif;background:#E2E8F0">'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;width:1200px">{"".join(cells)}</div>'
             f'<div style="display:flex;align-items:center;justify-content:center;gap:24px;padding:24px;width:1152px">{icons}</div>'
             f'</body></html>')
    pg.set_viewport_size({'width': 1200, 'height': 900})
    pg.set_content(sheet)
    pg.wait_for_timeout(200)
    hgt = pg.evaluate('document.body.scrollHeight')
    pg.screenshot(path=os.path.join(OUT, 'preview.png'), clip={'x': 0, 'y': 0, 'width': 1200, 'height': hgt})
    b.close()

from PIL import Image
imgs = [Image.open(os.path.join(OUT, f'png/favicon-{s}.png')) for s in (16, 32, 48)]
imgs[2].save(os.path.join(OUT, 'icon/favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)], append_images=imgs[:2])
print(f'rendered {len(RENDERS)} png files, preview.png, favicon.ico')
