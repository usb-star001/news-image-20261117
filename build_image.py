#!/usr/bin/env python3
"""Compose the entry image: a one-page newspaper front page summing up
Tuesday 17 November 2026's world news.

All text is rendered here with PIL (never by an image model), so every
headline stays crisp and correctly spelled. The four story illustrations
in assets/ were generated separately and contain no text.

Output: entry.png in this directory (1024x1024, <= 1 MiB).
Deterministic: fixed fonts, fixed layout, fixed crop boxes, no randomness,
no timestamps. Run: python3 build_image.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
MARGIN = 30
INK = (17, 17, 17)
PAPER = (248, 244, 236)
RED = (164, 30, 34)
GREY = (90, 86, 78)
RULE = (17, 17, 17)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def cover_crop(img, target_w, target_h, focus_y=0.5):
    """Center-crop to the target aspect ratio (vertical focus adjustable)."""
    tw, th = img.size
    target_ratio = target_w / target_h
    ratio = tw / th
    if ratio > target_ratio:  # too wide: crop sides
        new_w = int(th * target_ratio)
        x0 = (tw - new_w) // 2
        box = (x0, 0, x0 + new_w, th)
    else:  # too tall: crop top/bottom around focus_y
        new_h = int(tw / target_ratio)
        y0 = int((th - new_h) * focus_y)
        box = (0, y0, tw, y0 + new_h)
    return img.crop(box).resize((target_w, target_h), Image.LANCZOS)


def main():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)
    content_w = W - 2 * MARGIN
    x0 = MARGIN

    # ---- Masthead -------------------------------------------------------
    y = 26
    kicker = font(SANS_B, 21)
    d.text((x0, y), "T H E   W O R L D   I N   O N E   D A Y", font=kicker, fill=RED)
    y += 28
    mast = font(SERIF, 54)
    d.text((x0, y), "Tuesday 17 November 2026", font=mast, fill=INK)
    y += 68
    sub = font(SERIF_IT, 23)
    d.text((x0, y), "Four stories that defined the day, as reported around the world.",
           font=sub, fill=GREY)
    y += 34
    d.rectangle([x0, y, W - MARGIN, y + 3], fill=RULE)
    y += 7
    d.rectangle([x0, y, W - MARGIN, y + 1], fill=RULE)
    y += 14

    # ---- Lead story: Hormuz --------------------------------------------
    lead_img = Image.open(os.path.join(HERE, "assets", "hormuz.webp")).convert("RGB")
    lead_h = 180
    page.paste(cover_crop(lead_img, content_w, lead_h, focus_y=0.68),
               (x0, y))
    d.rectangle([x0, y, W - MARGIN, y + lead_h], outline=INK, width=2)
    y += lead_h + 12
    kick = font(SANS_B, 19)
    d.text((x0, y), "MIDDLE EAST  ·  STRAIT OF HORMUZ", font=kick, fill=RED)
    y += 26
    head = font(SERIF, 43)
    lead_headline = ("Third U.S. carrier arrives as tankers "
                     "are hit by mines near Hormuz")
    y = draw_lines(d, wrap(d, lead_headline, head, content_w), x0, y, head, INK, 48)
    y += 4
    deck = font(SANS, 21)
    lead_deck = ("The USS Theodore Roosevelt joins two U.S. carriers in the region as "
                 "oil tankers strike mines near the strait and the U.S.–Iran "
                 "confrontation deepens.")
    y = draw_lines(d, wrap(d, lead_deck, deck, content_w), x0, y, deck, INK, 27)
    y += 12
    d.rectangle([x0, y, W - MARGIN, y + 1], fill=RULE)
    y += 14

    # ---- Three stories in columns ---------------------------------------
    stories = [
        {
            "img": "bridges.webp",
            "kicker": "UKRAINE  ·  RUSSIA",
            "headline": "Bridges under fire on both sides",
            "deck": ("Russian missiles hit two bridges over the Dnipro in Kyiv; "
                     "Ukraine strikes the Kerch Bridge to Crimea for a second "
                     "day, collapsing part of the span."),
        },
        {
            "img": "summit.webp",
            "kicker": "DIPLOMACY  ·  APEC",
            "headline": "Trump, Xi and Putin to meet in Shenzhen",
            "deck": ("China confirms the first three-way meeting of the three "
                     "leaders, set for Thursday at the APEC summit in Shenzhen, "
                     "with nuclear arms and Iran on the agenda."),
        },
        {
            "img": "rwanda.webp",
            "kicker": "EUROPE  ·  MIGRATION",
            "headline": "Five EU states plan Rwanda return hub",
            "deck": ("Germany, Denmark, Austria, Greece and the Netherlands "
                     "announce a joint facility in Rwanda for rejected asylum "
                     "seekers, from next year."),
        },
    ]
    gap = 24
    col_w = (content_w - 2 * gap) // 3
    img_h = 130
    col_head = font(SERIF, 26)
    col_deck = font(SANS, 16)
    col_kick = font(SANS_B, 15)
    top = y
    bottom = top
    for i, s in enumerate(stories):
        cx = x0 + i * (col_w + gap)
        img = Image.open(os.path.join(HERE, "assets", s["img"])).convert("RGB")
        page.paste(cover_crop(img, col_w, img_h, focus_y=0.5), (cx, top))
        d.rectangle([cx, top, cx + col_w, top + img_h], outline=INK, width=2)
        cy = top + img_h + 10
        d.text((cx, cy), s["kicker"], font=col_kick, fill=RED)
        cy += 22
        cy = draw_lines(d, wrap(d, s["headline"], col_head, col_w),
                        cx, cy, col_head, INK, 30)
        cy += 4
        cy = draw_lines(d, wrap(d, s["deck"], col_deck, col_w),
                        cx, cy, col_deck, INK, 20)
        bottom = max(bottom, cy)
    y = bottom + 14

    # ---- Footer: also today + sources -----------------------------------
    d.rectangle([x0, y, W - MARGIN, y + 1], fill=RULE)
    y += 12
    also = font(SANS_B, 17)
    d.text((x0, y), "ALSO TODAY", font=also, fill=RED)
    y += 24
    also_f = font(SANS, 18)
    also_text = ("GTA VI launches Thursday  ·  Pentagon fails its audit for a ninth year  ·  "
                 "JPMorgan glitch disrupts Zelle")
    y = draw_lines(d, wrap(d, also_text, also_f, content_w), x0, y, also_f, INK, 23)
    y += 10
    src = font(SERIF_IT, 15)
    d.text((x0, y), "As reported on 17 November 2026 by Reuters, Al Jazeera, AP, "
                    "Outlook India, Zark News, One Turn and FeedCast.",
           font=src, fill=GREY)

    out = os.path.join(HERE, "entry.png")
    # PNG first; fall back to JPEG bytes (still named entry.png) if over 1 MiB.
    page.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    if size > 1048576:
        for q in (92, 88, 84, 80):
            page.save(out, format="JPEG", quality=q, optimize=True)
            size = os.path.getsize(out)
            if size <= 1048576:
                break
    print(f"entry.png: {page.size[0]}x{page.size[1]} px, {size} bytes")


if __name__ == "__main__":
    main()
