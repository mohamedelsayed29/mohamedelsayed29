#!/usr/bin/env python3
"""Generate the 8-bit SVG assets used by README.md.

Everything is drawn with a hand-made 5x7 bitmap font as plain SVG rects,
so it renders identically on GitHub (no web fonts, no external requests).

    python3 assets/build.py [path/to/photo.jpg]

The photo is optional; it is turned into a pixel-art avatar for the header.
"""
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# ── palette ────────────────────────────────────────────────────────────────
BG = "#0f0e1f"
INK = "#1d2b53"
PURPLE = "#7e2553"
RED = "#ff004d"
ORANGE = "#ffa300"
YELLOW = "#ffec27"
GREEN = "#00e436"
BLUE = "#29adff"
LAV = "#83769c"
PINK = "#ff77a8"
WHITE = "#fff1e8"
GRAY = "#c2c3c7"
DIM = "#5f574f"

# ── 5x7 bitmap font ────────────────────────────────────────────────────────
F = {
    "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#",
    "B": "####.|#...#|#...#|####.|#...#|#...#|####.",
    "C": ".###.|#...#|#....|#....|#....|#...#|.###.",
    "D": "####.|#...#|#...#|#...#|#...#|#...#|####.",
    "E": "#####|#....|#....|####.|#....|#....|#####",
    "F": "#####|#....|#....|####.|#....|#....|#....",
    "G": ".###.|#...#|#....|#.###|#...#|#...#|.####",
    "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    "I": "###|.#.|.#.|.#.|.#.|.#.|###",
    "J": "....#|....#|....#|....#|#...#|#...#|.###.",
    "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#",
    "L": "#....|#....|#....|#....|#....|#....|#####",
    "M": "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#",
    "N": "#...#|#...#|##..#|#.#.#|#..##|#...#|#...#",
    "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.",
    "P": "####.|#...#|#...#|####.|#....|#....|#....",
    "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#",
    "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    "S": ".####|#....|#....|.###.|....#|....#|####.",
    "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.",
    "V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
    "W": "#...#|#...#|#...#|#.#.#|#.#.#|#.#.#|.#.#.",
    "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..",
    "Z": "#####|....#|...#.|..#..|.#...|#....|#####",
    "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.",
    "1": "..#..|.##..|..#..|..#..|..#..|..#..|.###.",
    "2": ".###.|#...#|....#|...#.|..#..|.#...|#####",
    "3": "####.|....#|....#|.###.|....#|....#|####.",
    "4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.",
    "5": "#####|#....|####.|....#|....#|#...#|.###.",
    "6": "..##.|.#...|#....|####.|#...#|#...#|.###.",
    "7": "#####|....#|...#.|..#..|.#...|.#...|.#...",
    "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.",
    "9": ".###.|#...#|#...#|.####|....#|...#.|.##..",
    " ": "...|...|...|...|...|...|...",
    ".": "..|..|..|..|..|##|##",
    ",": "..|..|..|..|##|.#|#.",
    ":": "..|##|##|..|##|##|..",
    "-": "....|....|....|####|....|....|....",
    "+": ".....|..#..|..#..|#####|..#..|..#..|.....",
    "=": ".....|.....|#####|.....|#####|.....|.....",
    "/": "....#|....#|...#.|..#..|.#...|#....|#....",
    "%": "##..#|##..#|...#.|..#..|.#...|#..##|#..##",
    "!": "##|##|##|##|##|..|##",
    "?": ".###.|#...#|....#|...#.|..#..|.....|..#..",
    "'": "#|#|.|.|.|.|.",
    "(": ".#|#.|#.|#.|#.|#.|.#",
    ")": "#.|.#|.#|.#|.#|.#|#.",
    ">": "#...|.#..|..#.|...#|..#.|.#..|#...",
    "<": "...#|..#.|.#..|#...|.#..|..#.|...#",
    "·": "..|..|##|##|..|..|..",
    "→": "......|...#..|....#.|######|....#.|...#..|......",
    "▶": "#...|##..|###.|####|###.|##..|#...",
    "▼": ".......|#######|.#####.|..###..|...#...|.......|.......",
    "★": "...#...|...#...|#######|.#####.|..###..|.##.##.|##...##",
    "♥": ".##.##.|#######|#######|.#####.|..###..|...#...|.......",
    "✔": "......|.....#|....##|#..##.|####..|.##...|......",
    "_": ".....|.....|.....|.....|.....|.....|#####",
}
GLYPH = {k: v.split("|") for k, v in F.items()}


def text_width(s, scale=1, gap=1):
    cols = sum(len(GLYPH[c][0]) + gap for c in s) - gap
    return cols * scale


def text_path(s, x, y, scale, fill, gap=1, cls="", extra=""):
    """Render string `s` as one <path>; (x, y) is the top-left corner."""
    d = []
    cx = x
    for ch in s:
        rows = GLYPH[ch]
        for r, row in enumerate(rows):
            c = 0
            while c < len(row):
                if row[c] == "#":
                    start = c
                    while c < len(row) and row[c] == "#":
                        c += 1
                    w = (c - start) * scale
                    d.append(f"M{cx + start * scale} {y + r * scale}h{w}v{scale}h-{w}z")
                else:
                    c += 1
        cx += (len(rows[0]) + gap) * scale
    c = f' class="{cls}"' if cls else ""
    return f'<path{c} fill="{fill}" d="{"".join(d)}"{extra}/>'


def shadow_text(s, x, y, scale, fill, shadow, off=None, cls=""):
    off = scale if off is None else off
    return text_path(s, x + off, y + off, scale, shadow) + text_path(s, x, y, scale, fill, cls=cls)


def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{extra}/>'


def pixel_box(x, y, w, h, fill, border, bw=4):
    """A box with a pixel border and notched (cut) corners."""
    return (
        rect(x + bw, y, w - 2 * bw, h, border)
        + rect(x, y + bw, w, h - 2 * bw, border)
        + rect(x + bw, y + bw, w - 2 * bw, h - 2 * bw, fill)
    )


STYLE = """<style>
  .blink { animation: blink 1.1s steps(1) infinite; }
  .tw    { animation: tw 2.6s steps(2) infinite; }
  .tw2   { animation: tw 3.4s steps(2) infinite; animation-delay: -1.3s; }
  .float { animation: float 1.2s steps(1) infinite; }
  .fa    { animation: fa .5s steps(1) infinite; }
  .fb    { animation: fb .5s steps(1) infinite; }
  .walk  { animation: walk 16s steps(330) infinite; }
  .spin  { animation: spin .9s steps(1) infinite; transform-box: fill-box; transform-origin: center; }
  .shoot { animation: shoot 7s steps(24) infinite; opacity: 0; }
  .xp    { animation: xp 4s steps(9) infinite; }
  @keyframes blink { 50% { opacity: 0; } }
  @keyframes tw    { 50% { opacity: .15; } }
  @keyframes float { 50% { transform: translateY(-4px); } }
  @keyframes fa    { 50% { opacity: 0; } }
  @keyframes fb    { 0% { opacity: 0; } 50% { opacity: 1; } }
  @keyframes walk  { from { transform: translateX(-60px); } to { transform: translateX(1260px); } }
  @keyframes spin  { 25% { transform: scaleX(.6); } 50% { transform: scaleX(.2); } 75% { transform: scaleX(.6); } }
  @keyframes shoot { 0% { opacity: 1; transform: translate(0, 0); } 14% { opacity: 1; transform: translate(-336px, 168px); }
                     14.1%, 100% { opacity: 0; transform: translate(-336px, 168px); } }
  @keyframes xp    { from { transform: scaleX(.1); } to { transform: scaleX(1); } }
  @media (prefers-reduced-motion: reduce) { * { animation: none !important; } .shoot { opacity: 0; } }
</style>"""

SCANLINES = (
    '<defs><pattern id="sl" width="4" height="4" patternUnits="userSpaceOnUse">'
    '<rect width="4" height="2" fill="#000" fill-opacity=".22"/></pattern></defs>'
)


def scanlines(w, h):
    return SCANLINES + f'<rect width="{w}" height="{h}" fill="url(#sl)" pointer-events="none"/>'


def svg(w, h, body, title, desc=""):
    d = f"<desc>{desc}</desc>" if desc else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" shape-rendering="crispEdges" role="img">'
        f"<title>{title}</title>{d}{STYLE}{body}</svg>\n"
    )


def write(name, content):
    (HERE / name).write_text(content)
    print(f"  wrote assets/{name}  ({len(content) / 1024:.1f} KB)")


# ── sprites ────────────────────────────────────────────────────────────────
def sprite(rows, x, y, px, pal):
    """Draw a sprite from rows of palette keys ('.' = transparent)."""
    by = {}
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            k = row[c]
            start = c
            while c < len(row) and row[c] == k:
                c += 1
            if k != ".":
                w = (c - start) * px
                by.setdefault(k, []).append(f"M{x + start * px} {y + r * px}h{w}v{px}h-{w}z")
    return "".join(f'<path fill="{pal[k]}" d="{"".join(d)}"/>' for k, d in by.items())


HERO_PAL = {
    "H": "#24142c", "S": "#ffccaa", "s": "#e09a7a", "E": "#1d1020", "B": "#3a2418",
    "R": "#b0204a", "r": "#7e2553", "W": WHITE, "P": "#29366f", "K": "#111018",
}
HERO_TOP = [
    "....HHHH....",
    "..HHHHHHHH..",
    ".HHHHHHHHHH.",
    ".HHHHSSSSH..",
    ".HHHSSSESS..",
    ".HHHSSSSSSs.",
    "..HHBSSSBB..",
    "..HBBBBBBB..",
    "...BBBBBB...",
    "..rRRWRRRr..",
    ".rRRRWRRRRSS",
    ".rRRRRRRRr..",
    "..rRRRRRRr..",
]
HERO_A = HERO_TOP + ["..PPPP.PPP..", ".PPP....PPP.", ".KKK....KKKK"]
HERO_B = HERO_TOP + ["...PPPPPP...", "....PPPP....", "...KKKKKK..."]

COIN_PAL = {"Y": YELLOW, "W": WHITE, "O": ORANGE}
COIN = [".YYYY.", "YWYYYO", "YWYYYO", "YWYYYO", "YWYYYO", "YYYYOO", ".OOOO."]


def coin(x, y, px=4, delay=0.0):
    return (f'<g class="spin" style="animation-delay:{delay}s">'
            f"{sprite(COIN, x, y, px, COIN_PAL)}</g>")


MONSTER = [
    "....MMMMMM....",
    "..MMMMMMMMMM..",
    ".MMMMMMMMMMMM.",
    ".MMXMXMMXMXMM.",
    "MMMMXMMMMXMMMM",
    "MMMXMXMMXMXMMM",
    "MMMMMMMMMMMMMM",
    "MMDWDWDWDWDWMM",
    "MMMMMMMMMMMMMM",
    ".MMMMMMMMMMMM.",
    ".MM.MM..MM.MM.",
    ".M..M....M..M.",
]


# ── pixel avatar from photo ────────────────────────────────────────────────
def avatar(photo, x, y, px=5, n=40, colors=20):
    from PIL import Image, ImageEnhance

    img = Image.open(photo).convert("RGB")
    img = img.crop((55, 25, 385, 355))  # head + shoulders
    img = img.point(lambda v: int(255 * (v / 255) ** (1 / 1.35)))  # lift shadows
    img = ImageEnhance.Contrast(img).enhance(1.2)
    img = ImageEnhance.Color(img).enhance(1.25)
    img = img.resize((n, n), Image.Resampling.BOX)
    img = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = img.getpalette()
    by_color = {}
    for r in range(n):
        c = 0
        while c < n:
            idx = img.getpixel((c, r))
            start = c
            while c < n and img.getpixel((c, r)) == idx:
                c += 1
            w = (c - start) * px
            by_color.setdefault(idx, []).append(f"M{x + start * px} {y + r * px}h{w}v{px}h-{w}z")
    out = []
    for idx, d in by_color.items():
        rgb = pal[idx * 3: idx * 3 + 3]
        out.append(f'<path fill="#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}" d="{"".join(d)}"/>')
    return "".join(out)


# ── header: title screen ───────────────────────────────────────────────────
def header(photo):
    W, H = 1200, 440
    GROUND = 424
    rnd = random.Random(29)
    b = [
        '<defs><linearGradient id="t" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset=".5" stop-color="{YELLOW}"/><stop offset=".5" stop-color="{ORANGE}"/>'
        '</linearGradient><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG}"/><stop offset=".6" stop-color="{BG}"/>'
        '<stop offset=".6" stop-color="#14112a"/><stop offset=".8" stop-color="#14112a"/>'
        '<stop offset=".8" stop-color="#1b1535"/></linearGradient></defs>',
        rect(0, 0, W, H, "url(#sky)"),
    ]

    # stars
    for _ in range(80):
        sx, sy = rnd.randrange(0, W // 4) * 4, rnd.randrange(14, 90) * 4
        size = 4 if rnd.random() < 0.25 else 2
        col = rnd.choice([WHITE, WHITE, GRAY, LAV, BLUE])
        cls = rnd.choice(["", "", "tw", "tw2"])
        b.append(rect(sx, sy, size, size, col, f' class="{cls}"' if cls else ""))

    # shooting star
    trail = "".join(rect(980 + i * 8, 70 - i * 4, 4 - (i > 1) * 2, 4 - (i > 1) * 2,
                         [WHITE, YELLOW, ORANGE, RED][i]) for i in range(4))
    b.append(f'<g class="shoot">{trail}</g>')

    # moon
    moon = [
        "..#####...", ".####.....", "####......", "###.......", "###.......",
        "###.......", "###.......", "####......", ".####.....", "..#####...",
    ]
    for r, row in enumerate(moon):
        for c, ch in enumerate(row):
            if ch == "#":
                b.append(rect(1100 + c * 7, 70 + r * 7, 7, 7, YELLOW if c > 0 else ORANGE))

    # pyramids (Cairo!) — stepped triangles
    def pyramid(cx, base_y, steps, step_w, step_h, light, dark):
        for i in range(steps):
            w = (steps - i) * step_w * 2
            yy = base_y - (i + 1) * step_h
            b.append(rect(cx - w // 2, yy, w // 2, step_h, light))
            b.append(rect(cx, yy, w // 2, step_h, dark))

    pyramid(1010, GROUND, 13, 8, 8, "#4a3670", "#2e2250")
    pyramid(1135, GROUND, 8, 8, 8, "#4a3670", "#2e2250")
    pyramid(885, GROUND, 6, 8, 8, "#3a2b5c", "#271d44")

    # coins in an arc
    for i, (cx, cy) in enumerate([(820, 268), (868, 244), (916, 232), (964, 244), (1012, 268)]):
        b.append(coin(cx, cy, 4, delay=-i * 0.18))

    # ground: checker bricks
    b.append(rect(0, GROUND, W, H - GROUND, INK))
    b.append(rect(0, GROUND, W, 4, "#3b5dc9"))
    for gx in range(0, W, 16):
        b.append(rect(gx, GROUND + 4, 8, 4, "#2b3d6e"))
        b.append(rect(gx + 8, GROUND + 8, 8, 4, "#16213f"))

    # HUD
    b.append(text_path("1UP", 40, 24, 3, RED, cls="blink"))
    b.append(text_path("MOHAMED", 40 + text_width("1UP ", 3), 24, 3, WHITE))
    hud_mid = "WORLD EG-CAIRO"
    b.append(text_path(hud_mid, (W - text_width(hud_mid, 3)) // 2, 24, 3, WHITE))
    hud_r = "CREDIT 01"
    b.append(text_path(hud_r, W - 40 - text_width(hud_r, 3), 24, 3, WHITE))

    # avatar + frame
    ax, ay = 60, 96
    b.append(pixel_box(ax - 12, ay - 12, 224, 224, BG, WHITE, 4))
    b.append(rect(ax - 4, ay - 4, 208, 208, BLUE))
    b.append(avatar(photo, ax, ay) if photo else rect(ax, ay, 200, 200, INK))
    # lives
    b.append(text_path("♥♥♥", ax, ay + 228, 3, RED))
    b.append(text_path("P1", ax + 200 - text_width("P1", 3), ay + 228, 3, GREEN, cls="blink"))

    # title
    tx = 316
    for word, wy in (("MOHAMED", 86), ("ELSAYED", 166)):
        b.append(text_path(word, tx + 9, wy + 9, 9, INK))
        b.append(text_path(word, tx + 5, wy + 5, 9, PURPLE))
        b.append(text_path(word, tx, wy, 9, "url(#t)"))

    b.append(shadow_text("FULL STACK ENGINEER", tx, 252, 4, BLUE, INK))
    b.append(text_path("REACT · NODE · NESTJS · TYPESCRIPT", tx, 298, 2, GRAY))
    b.append(text_path("▶ PRESS START", tx, 336, 3, WHITE, cls="blink"))

    # walking hero
    hy = GROUND - 15 * 4 - 4
    b.append(
        f'<g class="walk"><g class="fa">{sprite(HERO_A, 0, hy, 4, HERO_PAL)}</g>'
        f'<g class="fb">{sprite(HERO_B, 0, hy, 4, HERO_PAL)}</g></g>'
    )

    b.append(scanlines(W, H))
    write("header.svg", svg(W, H, "".join(b),
                            "Mohamed Elsayed, Full Stack Engineer",
                            "8-bit title screen: React, Node.js, NestJS, TypeScript. Cairo, Egypt."))


# ── player stats card ──────────────────────────────────────────────────────
def player_card():
    W, H = 840, 260
    b = [pixel_box(0, 0, W, H, BG, WHITE, 4), pixel_box(10, 10, W - 20, H - 20, BG, INK, 4)]
    # hero on a pedestal
    px = 7
    sx, sy = 52, 40
    b.append(f'<g class="float">{sprite(HERO_B, sx, sy, px, HERO_PAL)}</g>')
    b.append(rect(sx - 8, sy + 16 * px + 4, 12 * px + 16, 8, "#3b5dc9"))
    b.append(rect(sx - 8, sy + 16 * px + 12, 12 * px + 16, 8, INK))
    # bars
    by = 186
    b.append(text_path("HP", 36, by, 2, RED))
    for i in range(9):
        b.append(rect(66 + i * 10, by, 8, 14, RED))
    b.append(text_path("XP", 36, by + 24, 2, BLUE))
    b.append(rect(66, by + 24, 88, 14, INK))
    b.append(f'<g class="xp" style="transform-origin:66px 0">{rect(66, by + 24, 88, 14, BLUE)}</g>')
    # stats
    lx, vx = 200, 200 + text_width("STATUS  ", 3)
    lines = [
        ("NAME", "MOHAMED ELSAYED", WHITE),
        ("CLASS", "FULL STACK ENGINEER", YELLOW),
        ("HOME", "CAIRO, EGYPT", WHITE),
        ("MAIN", "REACT · NODE · NESTJS · TS", BLUE),
        ("STATUS", "OPEN TO WORK", GREEN),
    ]
    y = 40
    for label, val, col in lines:
        b.append(text_path(label, lx, y, 3, LAV))
        b.append(text_path(val, vx, y, 3, col))
        y += 38
    b.append(text_path("▶", vx + text_width("OPEN TO WORK ", 3), y - 38, 3, GREEN, cls="blink"))
    b.append(scanlines(W, H))
    write("player.svg", svg(W, H, "".join(b), "Player 1",
                            "Name: Mohamed Elsayed. Class: Full Stack Engineer. Home: Cairo, Egypt. "
                            "Main: React, Node.js, NestJS, TypeScript. Status: open to work."))


# ── career world map ───────────────────────────────────────────────────────
STAGES = [
    ("1-1", "CYPARTA", ("BACKEND DEV", "INTERN"), "JUN-AUG 2025", False),
    ("1-2", "QOWA", ("JUNIOR SOFTWARE", "ENGINEER"), "FEB-OCT 2026", False),
    ("1-3", "HAMMERLOAD", ("FULL STACK", "ENGINEER"), "AUG 2026-NOW", True),
    ("1-4", "RYVOR", ("SOFTWARE", "ENGINEER"), "OCT 2026-NOW", True),
]


def world_map():
    W, H = 840, 320
    b = [pixel_box(0, 0, W, H, BG, WHITE, 4), pixel_box(10, 10, W - 20, H - 20, BG, INK, 4)]
    b.append(text_path("WORLD 1 · CAREER MODE", 30, 28, 2, BLUE))
    top = 124  # mound top
    centers = [105 + i * 210 for i in range(4)]
    # dotted path
    for i in range(3):
        for x in range(centers[i] + 56, centers[i + 1] - 52, 16):
            b.append(rect(x, top + 12, 8, 8, YELLOW if not STAGES[i + 1][4] or i == 1 else DIM))
    for (stage, name, role, dates, current), cx in zip(STAGES, centers):
        # mound
        for k, (w, col) in enumerate(((56, "#3b5dc9"), (80, "#2b3d6e"), (104, INK))):
            b.append(rect(cx - w // 2, top + k * 8, w, 8, col))
        # flag (two waving frames)
        if name != "RYVOR":
            fcol = YELLOW if current else GREEN
            b.append(rect(cx - 2, top - 44, 4, 44, WHITE))
            f1 = "".join(rect(cx + 2, top - 44 + r * 4, w, 4, fcol) for r, w in enumerate((24, 20, 16, 12, 8, 4)))
            f2 = "".join(rect(cx + 2, top - 44 + r * 4, w, 4, fcol) for r, w in enumerate((20, 24, 20, 12, 8, 4)))
            b.append(f'<g class="fa">{f1}</g><g class="fb">{f2}</g>')
        else:
            b.append(f'<g class="float">{sprite(HERO_B, cx - 24, top - 64, 4, HERO_PAL)}</g>')
            b.append(text_path("▼", cx - 7, top - 92, 2, GREEN, cls="blink") if "▼" in GLYPH else "")
        # labels
        def center(s, y, scale, col, cls=""):
            b.append(text_path(s, cx - text_width(s, scale) // 2, y, scale, col, cls=cls))
        center("STAGE " + stage, top + 36, 2, LAV)
        center(name, top + 58, 3, WHITE)
        center(role[0], top + 90, 2, GRAY)
        center(role[1], top + 108, 2, GRAY)
        center(dates, top + 134, 2, YELLOW if current else LAV)
        if current:
            center("NOW PLAYING", top + 160, 2, ORANGE, cls="blink")
        else:
            center("CLEARED ✔", top + 160, 2, GREEN)
    b.append(scanlines(W, H))
    write("map.svg", svg(W, H, "".join(b), "Career world map",
                         "Stage 1-1 Cyparta, Backend Developer Intern, Jun-Aug 2025, cleared. "
                         "Stage 1-2 Qowa, Junior Software Engineer, Feb-Oct 2026, cleared. "
                         "Stage 1-3 HammerLoad, Full Stack Engineer, Aug 2026-now. "
                         "Stage 1-4 RYVOR, Software Engineer, Oct 2026-now."))


# ── boss cards (projects) ──────────────────────────────────────────────────
BOSSES = {
    "bioreza": ("BOSS 01", "BIOREZA", "E-COMMERCE · SKINCARE", PINK),
    "social": ("BOSS 02", "SOCIAL MEDIA API", "REAL-TIME BACKEND", GREEN),
}


def boss(key, tag, name, sub, col):
    W, H = 420, 150
    b = [pixel_box(0, 0, W, H, BG, WHITE, 4), pixel_box(8, 8, W - 16, H - 16, BG, INK, 4)]
    b.append(text_path(tag, 24, 22, 2, RED))
    b.append(text_path("K.O.!", 24 + text_width(tag + "  ", 2), 22, 2, YELLOW, cls="blink"))
    scale = 4 if text_width(name, 4) <= 280 else 3
    b.append(shadow_text(name, 24, 46, scale, WHITE, PURPLE, off=3))
    b.append(text_path(sub, 24, 46 + 7 * scale + 14, 2, LAV))
    # empty HP bar
    hy = 112
    b.append(text_path("HP", 24, hy, 2, RED))
    b.append(rect(54, hy - 2, 210, 18, WHITE))
    b.append(rect(58, hy + 2, 202, 10, "#2a1020"))
    b.append(rect(58, hy + 2, 4, 10, RED, ' class="blink"'))
    b.append(text_path("0/999", 274, hy, 2, GRAY))
    # defeated monster
    mpal = {"M": col, "X": BG, "D": BG, "W": WHITE}
    b.append(f'<g class="float">{sprite(MONSTER, W - 24 - 14 * 5, 34, 5, mpal)}</g>')
    b.append(scanlines(W, H))
    write(f"boss-{key}.svg", svg(W, H, "".join(b), f"{tag}: {name.title()}", f"{sub.title()}. Defeated."))


# ── section title bars ─────────────────────────────────────────────────────
SECTIONS = {
    "player": ("▶", GREEN, "PLAYER 1"),
    "quests": ("★", YELLOW, "QUEST LOG"),
    "bosses": ("♥", RED, "BOSS LEVELS"),
    "inventory": ("+", BLUE, "INVENTORY"),
    "side": ("★", PINK, "SIDE QUESTS"),
    "training": ("▶", ORANGE, "TRAINING ARC"),
}


def section(key, icon, icol, label):
    scale = 4
    pad = 20
    iw = text_width(icon, scale)
    tw = text_width(label, scale)
    W = pad + iw + 16 + tw + pad
    H = 64
    b = [pixel_box(0, 0, W, H, BG, WHITE, 4), rect(4, H - 8, W - 8, 4, INK)]
    b.append(text_path(icon, pad, (H - 28) // 2 - 2, scale, icol, cls="blink"))
    b.append(shadow_text(label, pad + iw + 16, (H - 28) // 2 - 2, scale, WHITE, PURPLE, off=4))
    write(f"sec-{key}.svg", svg(W, H, "".join(b), label.title()))


# ── link buttons ───────────────────────────────────────────────────────────
BUTTONS = {
    "linkedin": ("LINKEDIN", BLUE, "#1a5f9e", WHITE),
    "email": ("EMAIL", RED, "#a8003a", WHITE),
    "portfolio": ("PORTFOLIO", GREEN, "#008751", INK),
    "resume": ("RESUME", YELLOW, "#c79a00", INK),
}


def button(key, label, face, edge, ink):
    scale = 3
    tw = text_width(label, scale)
    W, H = tw + 40, 52
    b = [
        pixel_box(0, 0, W, H, edge, BG, 4),
        rect(4, 4, W - 8, H - 14, face),
        rect(8, 8, W - 20, 4, WHITE, ' opacity=".55"'),
        text_path(label, (W - tw) // 2, 15, scale, ink),
    ]
    write(f"btn-{key}.svg", svg(W, H, "".join(b), label.title()))


# ── high score board ───────────────────────────────────────────────────────
def scores():
    W, H = 840, 330
    b = [pixel_box(0, 0, W, H, BG, WHITE, 4), pixel_box(10, 10, W - 20, H - 20, BG, INK, 4)]
    title = "HIGH SCORES"
    tx = (W - text_width(title, 5)) // 2
    b.append(shadow_text(title, tx, 34, 5, RED, INK, off=5))
    b.append(coin(tx - 52, 36, 4))
    b.append(coin(tx + text_width(title, 5) + 28, 36, 4, delay=-0.45))
    cols = (60, 190, 370)
    for x, h in zip(cols, ("RANK", "SCORE", "RECORD")):
        b.append(text_path(h, x, 98, 2, BLUE))
    rows = [
        ("1ST", "96%", "PAYMENT SUCCESS", "UP FROM 82% · STRIPE FLOW AT QOWA", YELLOW),
        ("2ND", "-40%", "CHECKOUT TICKETS", "FAILED-CHECKOUT SUPPORT TICKETS", GREEN),
        ("3RD", "15+", "STUDENTS TRAINED", "NODE.JS + REST APIS · IEEE MTI", PINK),
    ]
    y = 130
    for rank, score, rec, note, col in rows:
        b.append(text_path(rank, cols[0], y, 3, col))
        b.append(text_path(score, cols[1], y, 3, col))
        b.append(text_path(rec, cols[2], y, 3, WHITE))
        b.append(text_path(note, cols[2], y + 30, 2, LAV))
        y += 62
    b.append(text_path("▶", cols[0] - 26, 130, 3, YELLOW, cls="blink"))
    b.append(scanlines(W, H))
    write("scores.svg", svg(W, H, "".join(b), "High scores",
                            "1st: payment success 96% (up from 82%). 2nd: failed-checkout tickets -40%. "
                            "3rd: 15+ students trained."))


# ── continue screen ────────────────────────────────────────────────────────
def continue_screen():
    W, H = 840, 250
    b = [pixel_box(0, 0, W, H, BG, WHITE, 4)]
    t = "CONTINUE?"
    tw = text_width(t, 7)
    tx = (W - tw - 70) // 2
    b.append(shadow_text(t, tx, 40, 7, WHITE, PURPLE, off=6))
    b.append("<style>@keyframes cd{0%{opacity:1}10%,100%{opacity:0}}"
             "@media (prefers-reduced-motion: reduce){g[style]{opacity:0!important}}</style>")
    for i, d in enumerate("9876543210"):
        b.append(
            f'<g style="opacity:0;animation:cd 10s steps(1) infinite;animation-delay:{i}s">'
            f"{text_path(d, tx + tw + 35, 40, 7, YELLOW)}</g>"
        )
    s1 = "INSERT COIN TO START A PROJECT"
    s1x = (W - text_width(s1, 3)) // 2
    b.append(text_path(s1, s1x, 124, 3, YELLOW, cls="blink"))
    b.append(coin(s1x - 44, 122, 4))
    b.append(coin(s1x + text_width(s1, 3) + 20, 122, 4, delay=-0.45))
    s2 = "OPEN TO FULL-TIME + REMOTE ROLES"
    b.append(text_path(s2, (W - text_width(s2, 2)) // 2, 172, 2, GRAY))
    s3 = "▶ YES     NO"
    b.append(text_path(s3, (W - text_width(s3, 3)) // 2, 204, 3, WHITE))
    b.append(scanlines(W, H))
    write("continue.svg", svg(W, H, "".join(b), "Continue? Insert coin to start a project",
                              "Open to full-time and remote roles."))


if __name__ == "__main__":
    photo = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "168994391.jpeg"
    if not photo.exists():
        photo = HERE / "avatar.jpg"
    header(photo if photo.exists() else None)
    player_card()
    world_map()
    for k, v in BOSSES.items():
        boss(k, *v)
    for k, v in SECTIONS.items():
        section(k, *v)
    for k, v in BUTTONS.items():
        button(k, *v)
    scores()
    continue_screen()
