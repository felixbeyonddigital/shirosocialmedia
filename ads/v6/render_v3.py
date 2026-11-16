"""SHIRO Meta-Ads Runde 1, Fassung 3.

Foto im Vollformat: gleichmaessig skaliert (keine Verzerrung) und beschnitten, laeuft bis an alle Kanten.
Oben das echte SHIRO-Logo (Wortmarke), unten Headline, Infozeile und Button wie auf shiro-restaurant.at.
9:16 haelt die Reels-Sperrzonen ein: oben 14 %, unten 35 %, seitlich je 6 %.
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps

F = '/home/claude/fonts/'
SER = F + 'CormorantGaramond-Italic%5Bwght%5D.ttf'
SANS = F + 'Sora%5Bwght%5D.ttf'
LOGO = Image.open('/home/claude/fbpage/wm_cream.png').convert('RGBA')
BG = (10, 10, 10)
GOLD = (134, 133, 118)
HEAD = (236, 232, 220)
SUB = (205, 201, 188)
SAFE = dict(top=0.14, bottom=0.35, side=0.06)


def font(path, size, wght):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def tdraw(d, x, y, s, f, fill, tr):
    for c in s:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + tr


def tlen(d, s, f, tr):
    return sum(d.textlength(c, font=f) + tr for c in s) - tr


def cover(src, w, h, cx=0.5, cy=0.5, zoom=1.0):
    """Gleichmaessig skalieren und beschneiden. cx/cy = Bildmitte des Ausschnitts (0..1), zoom >= 1."""
    img = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
    s = max(w / img.width, h / img.height) * zoom
    cw, ch = w / s, h / s
    x0 = min(max(cx * img.width - cw / 2, 0), img.width - cw)
    y0 = min(max(cy * img.height - ch / 2, 0), img.height - ch)
    x0, y0 = max(0.0, x0), max(0.0, y0)
    cw, ch = min(cw, img.width - x0), min(ch, img.height - y0)
    return img.resize((w, h), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def shade(w, h, top_end, bot_start, top_a=0.70, bot_a=0.92):
    """Alpha-Maske: oben weicher Verlauf fuers Logo, unten fuer Text."""
    m = Image.new('L', (1, h))
    px = m.load()
    for y in range(h):
        a = 0.0
        if y < top_end:
            t = 1 - y / top_end
            a = top_a * t * t
        if y > bot_start:
            t = (y - bot_start) / (h - bot_start)
            a = max(a, bot_a * min(1, t * 1.35) ** 1.3)
        px[0, y] = int(255 * a)
    return m.resize((w, h))


def compose(src, out, w, h, crop, head, sub, cta='JETZT RESERVIEREN', story=False):
    s = w / 1440
    img = cover(src, w, h, **crop)
    if story:
        side = round(w * SAFE['side'])
        logo_y = round(h * SAFE['top']) + round(40 * s)
        y_bottom = round(h * (1 - SAFE['bottom'])) - round(24 * s)
    else:
        side = round(w * 0.075)
        logo_y = round(96 * s)
        y_bottom = h - round(110 * s)
    x = side + round(24 * s)

    fh = font(SER, round(132 * s), 300)
    fs = font(SANS, round(36 * s), 300)
    fb = font(SANS, round(37 * s), 500)
    lines = head.split('\n')
    lh = round(138 * s)
    bh = round(132 * s)
    y_btn = y_bottom - bh
    y_sub = y_btn - round(64 * s) - round(44 * s) if sub else y_btn - round(20 * s)
    y_head = y_sub - round(36 * s) - lh * len(lines)
    block_top = y_head - round(40 * s)

    logo_w = round(400 * s)
    logo = LOGO.resize((logo_w, round(LOGO.height * logo_w / LOGO.width)), Image.LANCZOS)
    top_end = logo_y + logo.height + round(260 * s)
    bot_start = max(block_top - round(420 * s), round(h * 0.35))
    m = shade(w, h, top_end, bot_start)
    img = Image.composite(Image.new('RGB', (w, h), BG), img, m)

    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    lay.alpha_composite(logo, ((w - logo_w) // 2, logo_y))
    d = ImageDraw.Draw(lay)
    for i, ln in enumerate(lines):
        d.text((x, y_head + i * lh - round(20 * s)), ln, font=fh, fill=HEAD + (255,))
    if sub:
        d.text((x, y_sub), sub, font=fs, fill=SUB + (255,))
    tr = 37 * s * 0.4
    bw = round(tlen(d, cta, fb, tr) + 2 * 104 * s)
    d.rounded_rectangle([x, y_btn, x + bw, y_btn + bh], radius=bh // 2, fill=GOLD + (255,))
    asc, desc = fb.getmetrics()
    tdraw(d, x + 104 * s, y_btn + (bh - (asc + desc)) / 2 + 2 * s, cta, fb, BG + (255,), tr)
    img = Image.alpha_composite(img.convert('RGBA'), lay).convert('RGB')
    img.save(out, quality=93, subsampling=0)
    right = max(x + bw, x + max(d.textlength(l, font=fh) for l in lines), x + (d.textlength(sub, font=fs) if sub else 0))
    return dict(logo=(logo_y, logo_y + logo.height), text_top=y_head, bottom=y_bottom, right=right, side=side)
