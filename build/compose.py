#!/usr/bin/env python3
"""Typeset the front page of "The World on Monday" for 23 November 2026.

The page is a single 1024x1024 broadsheet: a masthead with a date box, a
lead story on NATO's emergency session over the missiles found in Poland,
three picture cards (Kerch Bridge, the Seoul sell-off, Dymer), eight short
briefs, a sport strip and a footer.  Four painted illustrations from art/
carry the pictures; every word on the page is set here, from the story list
in STORIES.md.

The render is deterministic: the same inputs always produce the same PNG
bytes, so the file can be checked by hash.  Run from anywhere; it writes
entry/entry.png (the deliverable) and full.png beside this workdir's root.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ paths

WORKDIR = Path(__file__).resolve().parents[2]      # news-image-20261123/
ART_DIR = WORKDIR / "art"
OUT_PNG = WORKDIR / "entry" / "entry.png"
PREVIEW_PNG = WORKDIR / "full.png"

PICTURES = {
    "nato": ART_DIR / "media-generation-nato-council-0-1160fd4d-8c38-4d9b-91de-a9b091bc65df.webp",
    "kerch": ART_DIR / "media-generation-kerch-bridge-0-f561a17f-64eb-4479-ba86-4890514c79c9.webp",
    "markets": ART_DIR / "media-generation-markets-seoul-0-caad4cb3-080c-4a40-8bfe-97b51096b766.webp",
    "dymer": ART_DIR / "media-generation-dymer-rescue-0-3d39146f-22af-48ef-89da-e0b81e979711.webp",
}

# ------------------------------------------------------------------ palette

PAPER = (244, 239, 226)      # newsprint cream
INK = (22, 22, 20)           # near-black type
CRIMSON = (176, 32, 28)      # lead red
NAVY = (20, 36, 76)          # deep navy band
GOLD = (198, 152, 58)        # masthead gold
MUTED = (106, 100, 88)       # grey-brown small type
CREAM_BOX = (235, 227, 205)  # stat-box fill
SLATE = (88, 105, 138)       # REPORTED pill
LEAF = (44, 122, 76)         # CONFIRMED pill
HAIR = (188, 181, 160)       # thin divider
SPORT_LABEL = (168, 180, 202)

# ------------------------------------------------------------------ layout

W, H = 1024, 1024
MARGIN = 24
RIGHT = W - MARGIN            # 1000
CONTENT = RIGHT - MARGIN      # 976

# ------------------------------------------------------------------ fonts

_FONT_FILES = {
    "serif": "LiberationSerif-Regular.ttf",
    "serif-bold": "LiberationSerif-Bold.ttf",
    "serif-italic": "LiberationSerif-Italic.ttf",
    "sans": "LiberationSans-Regular.ttf",
    "sans-bold": "LiberationSans-Bold.ttf",
    "sans-italic": "LiberationSans-Italic.ttf",
}
_FONT_DIRS = (
    Path("/usr/share/fonts/truetype/liberation"),
    Path("/usr/share/fonts/truetype/dejavu"),
)
_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def typeface(kind: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a Liberation face (DejaVu as a stand-in if it is missing)."""
    key = (kind, size)
    if key in _cache:
        return _cache[key]
    wanted = _FONT_FILES[kind]
    fallback = {
        "serif": "DejaVuSerif.ttf",
        "serif-bold": "DejaVuSerif-Bold.ttf",
        "serif-italic": "DejaVuSerif.ttf",
        "sans": "DejaVuSans.ttf",
        "sans-bold": "DejaVuSans-Bold.ttf",
        "sans-italic": "DejaVuSans.ttf",
    }[kind]
    for folder in _FONT_DIRS:
        for name in (wanted, fallback):
            path = folder / name
            if path.exists():
                face = ImageFont.truetype(str(path), size)
                _cache[key] = face
                return face
    face = ImageFont.load_default()
    _cache[key] = face
    return face


def fitted(draw: ImageDraw.ImageDraw, text: str, kind: str,
           start: int, width: int) -> ImageFont.FreeTypeFont:
    """The biggest face of `kind` whose `text` fits inside `width`."""
    size = start
    while size > 8 and draw.textlength(text, font=typeface(kind, size)) > width:
        size -= 1
    return typeface(kind, size)


# ------------------------------------------------------------------ helpers

def wrap(draw: ImageDraw.ImageDraw, text: str,
         face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    """Greedy word wrap measured with the real face."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if not current or draw.textlength(trial, font=face) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def para(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
         face: ImageFont.FreeTypeFont, fill: tuple[int, int, int],
         width: int, leading: int) -> int:
    """Draw wrapped text; return the y just below the last line."""
    for line in wrap(draw, text, face, width):
        draw.text((x, y), line, font=face, fill=fill)
        y += leading
    return y


def chip(draw: ImageDraw.ImageDraw, x: int, y: int, label: str,
         face: ImageFont.FreeTypeFont, bg: tuple[int, int, int],
         fg: tuple[int, int, int] = (255, 255, 255),
         pad_x: int = 7, pad_y: int = 4) -> tuple[int, int]:
    """A solid label tag; returns its (right, bottom) corner."""
    tw = int(draw.textlength(label, font=face))
    th = face.size
    draw.rectangle([x, y, x + tw + 2 * pad_x, y + th + 2 * pad_y], fill=bg)
    draw.text((x + pad_x, y + pad_y - 1), label, font=face, fill=fg)
    return x + tw + 2 * pad_x, y + th + 2 * pad_y


def pill(draw: ImageDraw.ImageDraw, x: int, y: int, label: str,
         face: ImageFont.FreeTypeFont, bg: tuple[int, int, int]) -> int:
    """A small rounded status pill; returns its right edge."""
    tw = int(draw.textlength(label, font=face))
    w = tw + 10
    h = face.size + 5
    draw.rounded_rectangle([x, y, x + w, y + h], radius=2, fill=bg)
    draw.text((x + 5, y + 2), label, font=face, fill=(255, 255, 255))
    return x + w


def rule(draw: ImageDraw.ImageDraw, x0: int, x1: int, y: int,
         weight: int = 1, fill: tuple[int, int, int] = INK) -> None:
    draw.rectangle([x0, y, x1, y + weight - 1], fill=fill)


def fit_crop(picture: Image.Image, w: int, h: int) -> Image.Image:
    """Centre-crop to the target aspect, then scale with Lanczos."""
    tw, th = picture.size
    want = w / h
    if tw / th > want:
        nw = int(th * want)
        x0 = (tw - nw) // 2
        box = (x0, 0, x0 + nw, th)
    else:
        nh = int(tw / want)
        y0 = (th - nh) // 2
        box = (0, y0, tw, y0 + nh)
    return picture.crop(box).resize((w, h), Image.LANCZOS)


def shade(page: Image.Image, box: tuple[int, int, int, int],
          peak: int = 215) -> None:
    """Darken `box` with a black gradient that deepens towards the bottom."""
    x0, y0, x1, y1 = box
    height = y1 - y0
    veil = Image.new("RGBA", (x1 - x0, height), (0, 0, 0, 0))
    veil_draw = ImageDraw.Draw(veil)
    for yy in range(height):
        alpha = int(peak * (yy / height) ** 1.7)
        veil_draw.line([(0, yy), (x1 - x0, yy)], fill=(0, 0, 0, alpha))
    page.alpha_composite(veil, (x0, y0))


# ------------------------------------------------------------------ copy

TAGLINE = ("Three Russian missiles in Poland bring NATO to the table; "
           "the Kerch Bridge is hit again; AI shares slide.")

LEAD_PARAGRAPH = ("All three were Russian Kh-101 cruise missiles, made in late "
                  "2026. They fell during a Russian attack on western Ukraine.")

LEAD_BULLETS = (
    "Poland summons Russia's ambassador; seeks stronger air defences on its eastern border",
    "Tusk calls it a possible deliberate provocation; NATO did not invoke Article 4",
)

DAY_NUMBERS = (
    ("153", "Russian drones at Ukraine overnight"),
    ("134", "drones downed or jammed"),
    ("-3.3%", "Kospi close in Seoul, after -5.8%"),
)

CARDS = (
    {
        "picture": "kerch", "tag": "UKRAINE · KERCH BRIDGE", "tag_bg": NAVY,
        "headline": "Kerch Bridge hit again",
        "body": ("Road to Crimea cut; one rail track left. The 227-m road span "
                 "fell last week. Russia claims ~600 drones downed near Moscow."),
    },
    {
        "picture": "markets", "tag": "MARKETS · SEOUL", "tag_bg": CRIMSON,
        "headline": "AI sell-off deepens",
        "body": ("Kospi closes -3.3% after falling 5.8%; Samsung -3.1%, SK "
                 "Hynix -2.5%. Nasdaq fell 5.3% on Friday; the S&P is in correction."),
    },
    {
        "picture": "dymer", "tag": "UKRAINE · DYMER", "tag_bg": CRIMSON,
        "headline": "Dymer toll rises to 15",
        "body": ("Rescuers dig on through Monday at the collapsed block. "
                 "153 drones launched overnight; 134 downed; hits at 11 sites."),
    },
)

BRIEFS = (
    ("CLIMATE", "CONFIRMED",
     'Guterres voices "profound frustration" as the longest COP ends with '
     "no deal — first collapse since Copenhagen 2009."),
    ("GULF", "REPORTED",
     'Iran says it will use "all available tools" against the US naval '
     "blockade; Trump says its attacks hit a year-long high."),
    ("DIPLOMACY", "REPORTED",
     'Zelenskyy: Ukraine ready for four-way talks with Europe, the US and '
     'Russia "as soon as possible".'),
    ("LEBANON", "REPORTED",
     "Villagers return to southern Lebanon homes after Israeli pullback; "
     "army deploys under pilot ceasefire."),
    ("BANGLADESH", "REPORTED",
     "Dhaka says it will arrest ex-PM Sheikh Hasina if she returns from exile."),
    ("AUSTRALIA", "CONFIRMED",
     'Ian "Molly" Meldrum, the Countdown host who championed AC/DC and '
     "Kylie Minogue, dies aged 83 in Melbourne."),
    ("UNITED STATES", "CONFIRMED",
     "Delta outage resolved after 1,600+ flights delayed out of Atlanta as "
     "Thanksgiving travel began."),
    ("MEXICO", "REPORTED",
     'Cartel leader "El Chapo Isidro" arrested in Sinaloa on Friday.'),
)

SPORT = (
    ("NFL", "Cowboys 51–30 Titans, Prescott 5 TDs — a first-ever 51–30"),
    ("NFL · MEXICO CITY", "49ers 35–10 Vikings, Purdy 3 TDs"),
    ("NBA", "Nuggets 151–145 Bulls (OT), Jokic's 202nd triple-double"),
    ("NWSL", "Kansas City Current win first title, 2–1 vs Washington"),
)

FOOTER = (
    "DATE CHECK: left out as not Monday news: COP31 collapse itself (Sunday); "
    "Skubal's $450M Mets deal (agreed Sunday); the penny's end signed into law (Friday 20 Nov).",
    "Sources: Polish Press Agency / RMF24, Ukrainian Air Force, Al Jazeera, dpa-AFX, "
    "Reuters, ABC, AP, NBA, NFL. Illustrations are artistic, not photographs.",
)

# ------------------------------------------------------------------ sections


def paint_masthead(page: Image.Image, draw: ImageDraw.ImageDraw) -> None:
    """Nameplate, date box and the day's one-line summary."""
    box_x0, box_y0, box_y1 = 782, 12, 72
    draw.rectangle([box_x0, box_y0, RIGHT, box_y1], fill=INK)
    date_face = fitted(draw, "MONDAY 23 NOV 2026", "sans-bold", 19,
                       (RIGHT - box_x0) - 18)
    dw = draw.textlength("MONDAY 23 NOV 2026", font=date_face)
    draw.text(((box_x0 + RIGHT - dw) / 2, box_y0 + 7),
              "MONDAY 23 NOV 2026", font=date_face, fill=(255, 255, 255))
    sub_face = typeface("sans-bold", 13)
    sw = draw.textlength("LATE EDITION · 23 NOVEMBER", font=sub_face)
    draw.text(((box_x0 + RIGHT - sw) / 2, box_y0 + 36),
              "LATE EDITION · 23 NOVEMBER", font=sub_face, fill=GOLD)

    title_face = fitted(draw, "THE WORLD ON MONDAY", "serif-bold", 64,
                        box_x0 - MARGIN - 18)
    draw.text((MARGIN, 12), "THE WORLD ON MONDAY", font=title_face, fill=INK)

    tag_face = fitted(draw, TAGLINE, "serif-italic", 19, CONTENT)
    draw.text((MARGIN, 80), TAGLINE, font=tag_face, fill=CRIMSON)

    rule(draw, MARGIN, RIGHT, 104, weight=3)
    rule(draw, MARGIN, RIGHT, 110, weight=1)


def paint_lead(page: Image.Image, draw: ImageDraw.ImageDraw) -> None:
    """Hero picture with its headline, plus the fact column on the right."""
    hero = Image.open(PICTURES["nato"]).convert("RGB")
    page.paste(fit_crop(hero, 596, 322), (MARGIN, 118))
    shade(page, (MARGIN, 268, MARGIN + 596, 440))
    chip(draw, MARGIN, 118, "LEAD · BRUSSELS", typeface("sans-bold", 12),
         CRIMSON)

    head_face = fitted(draw, "NATO MEETS ON POLAND", "serif-bold", 42, 556)
    draw.text((MARGIN + 16, 338), "NATO MEETS ON POLAND",
              font=head_face, fill=(255, 255, 255))
    draw.text((MARGIN + 16, 384), "Three Russian missiles confirmed in Polish fields",
              font=typeface("serif-bold", 21), fill=GOLD)
    draw.text((MARGIN + 16, 412),
              'Rutte: "We will defend every inch of Polish territory"',
              font=typeface("sans", 15), fill=(255, 255, 255))

    cx, cw = 636, 364
    draw.text((cx, 118), "THE MISSILES, CONFIRMED",
              font=typeface("sans-bold", 16), fill=CRIMSON)
    para(draw, cx, 141, LEAD_PARAGRAPH, typeface("sans", 15), INK, cw, 19)

    # Two cream stat boxes: big figure on the left, caption beside it.
    stats = (("3", "Kh-101 missiles found in Poland", CRIMSON),
             ("32", "allies meet in Brussels", NAVY))
    for i, (figure, caption, colour) in enumerate(stats):
        bx = cx + i * (178 + 8)
        draw.rectangle([bx, 206, bx + 178, 258], fill=CREAM_BOX)
        num_face = typeface("serif-bold", 34)
        draw.text((bx + 11, 214), figure, font=num_face, fill=colour)
        cap_x = bx + 11 + int(draw.textlength(figure, font=num_face)) + 9
        para(draw, cap_x, 214, caption, typeface("sans", 12), INK,
             bx + 178 - cap_x - 8, 15)

    y = 270
    for bullet in LEAD_BULLETS:
        draw.ellipse([cx, y + 6, cx + 7, y + 13], fill=CRIMSON)
        y = para(draw, cx + 16, y, bullet, typeface("sans", 14), INK,
                 cw - 16, 18) + 8

    rule(draw, cx, RIGHT, 356, weight=1, fill=HAIR)
    draw.text((cx, 364), "NUMBERS OF THE DAY",
              font=typeface("sans-bold", 14), fill=INK)
    y = 384
    for figure, label in DAY_NUMBERS:
        draw.text((cx, y), figure, font=typeface("serif-bold", 20), fill=NAVY)
        draw.text((cx + 86, y + 2), label, font=typeface("sans", 14), fill=INK)
        y += 20


def paint_cards(page: Image.Image, draw: ImageDraw.ImageDraw) -> None:
    """Three picture cards in a row, divided by hairlines."""
    rule(draw, MARGIN, RIGHT, 448, weight=1)
    card_w, gap = 316, 14
    for i, card in enumerate(CARDS):
        x = MARGIN + i * (card_w + gap)
        art = Image.open(PICTURES[card["picture"]]).convert("RGB")
        page.paste(fit_crop(art, card_w, 142), (x, 456))
        chip(draw, x, 456, card["tag"], typeface("sans-bold", 11),
             card["tag_bg"])
        draw.text((x, 604), card["headline"],
                  font=typeface("serif-bold", 23), fill=INK)
        para(draw, x, 632, card["body"], typeface("sans", 14), INK,
             card_w, 18)
        if i:
            draw.line([(x - 8, 456), (x - 8, 690)], fill=HAIR, width=1)


def paint_briefs(draw: ImageDraw.ImageDraw) -> None:
    """Black 'also on Monday' bar, then eight briefs in four columns."""
    rule(draw, MARGIN, RIGHT, 700, weight=1)
    draw.rectangle([MARGIN, 708, RIGHT, 734], fill=INK)
    draw.text((MARGIN + 10, 713), "ALSO ON MONDAY",
              font=typeface("sans-bold", 16), fill=(255, 255, 255))
    note = "claims are marked as claims"
    note_face = typeface("sans-italic", 13)
    nw = draw.textlength(note, font=note_face)
    draw.text((RIGHT - 10 - nw, 715), note, font=note_face,
              fill=(150, 150, 150))

    col_w, col_gap = 232, 16
    kicker_face = typeface("sans-bold", 13)
    badge_face = typeface("sans-bold", 10)
    body_face = typeface("sans", 12)
    for i, (kicker, status, text) in enumerate(BRIEFS):
        col = i % 4
        row = i // 4
        x = MARGIN + col * (col_w + col_gap)
        y = 744 + row * 84
        draw.text((x, y), kicker, font=kicker_face, fill=CRIMSON)
        kw = draw.textlength(kicker, font=kicker_face)
        pill(draw, int(x + kw + 6), y + 1, status, badge_face,
             LEAF if status == "CONFIRMED" else SLATE)
        para(draw, x, y + 21, text, body_face, INK, col_w, 15)


def paint_sport(draw: ImageDraw.ImageDraw) -> None:
    """Navy strip with the four overnight results."""
    draw.rectangle([MARGIN, 918, RIGHT, 972], fill=NAVY)
    draw.text((MARGIN + 12, 934), "SPORT",
              font=typeface("sans-bold", 17), fill=GOLD)
    col_w = 202
    for i, (league, result) in enumerate(SPORT):
        x = 128 + i * 220
        draw.text((x, 926), league, font=typeface("sans-bold", 10),
                  fill=SPORT_LABEL)
        para(draw, x, 941, result, typeface("sans-bold", 12),
             (255, 255, 255), col_w, 14)


def paint_footer(draw: ImageDraw.ImageDraw) -> None:
    """Date check and sources, small and out of the way."""
    y = 982
    for line in FOOTER:
        face = fitted(draw, line, "sans", 12, CONTENT)
        draw.text((MARGIN, y), line, font=face, fill=MUTED)
        y += 15


# ------------------------------------------------------------------ build

def build_page() -> Image.Image:
    page = Image.new("RGBA", (W, H), PAPER)
    draw = ImageDraw.Draw(page)
    paint_masthead(page, draw)
    paint_lead(page, draw)
    paint_cards(page, draw)
    paint_briefs(draw)
    paint_sport(draw)
    paint_footer(draw)
    return page.convert("RGB")


def main() -> int:
    page = build_page()
    blob = io.BytesIO()
    page.save(blob, format="PNG")
    data = blob.getvalue()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    OUT_PNG.write_bytes(data)
    PREVIEW_PNG.write_bytes(data)
    print(f"wrote {OUT_PNG} ({len(data)} bytes, {W}x{H})")
    print(f"wrote {PREVIEW_PNG} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
