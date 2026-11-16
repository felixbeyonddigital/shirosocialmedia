"""SHIRO Meta-Ads Runde 3 (16.11.2026): Premium-Linie wie die Instagram-Grids.
Originalfotos (5F8A....JPG), Headline zweizeilig im Apple-Stil, Champagner #C9BDA6,
Button immer JETZT RESERVIEREN. Basis render_v3 (Vollformat, keine Verzerrung, Safe Zones).
"""
import sys
sys.path.insert(0, '/home/claude/work')
import render_v3 as r3
r3.HEAD = (201, 189, 166)
U = '/mnt/user-data/uploads/SHIRO/'
MOTIVE = [
    # key, file, head, sub, crop 4:5, crop 9:16
    ('20_Zart', 'Speisen/5F8A3624.JPG', 'Zart. Saftig.\nBesonders.', 'All you can enjoy · ab 24,90 € pro Person', dict(cx=0.5, cy=0.9, zoom=1.12), dict(cx=0.5, cy=0.72, zoom=1.1)),
    ('21_Klar', 'Speisen/5F8A3669.JPG', 'Klar. Fein.\nUnvergesslich.', 'Münchner Bundesstraße 1 · Salzburg', dict(cx=0.5, cy=0.8, zoom=1.15), dict(cx=0.5, cy=0.55)),
    ('22_Perfektion', 'Speisen/5F8A3586.JPG', 'Ein Stück\nPerfektion.', 'Mittags Mo bis Fr · 24,90 € pro Person', dict(cx=0.5, cy=0.85, zoom=1.2), dict(cx=0.5, cy=0.62, zoom=1.15)),
    ('23_DeinAbend', 'Interieur/5F8A3814.JPG', 'Dein Tisch.\nDein Abend.', 'Abends · 44,40 € pro Person', dict(cx=0.5, cy=0.5), dict(cx=0.5, cy=0.5)),
    ('24_Ankommen', 'Interieur/5F8A3770.JPG', 'Ankommen.\nUnd bleiben.', 'Münchner Bundesstraße 1 · Salzburg', dict(cx=0.5, cy=0.4), dict(cx=0.5, cy=0.4)),
]
from PIL import Image, ImageDraw
def story(src, out, crop, head, sub, cta='JETZT RESERVIEREN'):
    w, h = 1440, 2560; s = 1.0
    PY, PH = 560, 1180
    ph = r3.cover(src, 1440, PH, **crop)
    canvas = Image.new('RGB', (w, h), r3.BG); canvas.paste(ph, (0, PY))
    side = round(w * r3.SAFE['side']); x = side + 24
    y_bottom = round(h * (1 - r3.SAFE['bottom'])) - 24
    fh = r3.font(r3.SER, 132, 300); fs = r3.font(r3.SANS, 36, 300); fb = r3.font(r3.SANS, 37, 500)
    lines = head.split('\n'); lh, bh = 138, 132
    y_btn = y_bottom - bh; y_sub = y_btn - 108; y_head = y_sub - 36 - lh * len(lines)
    m = Image.new('L', (1, h)); px = m.load()
    top_end = PY + 160
    fade1 = PY + PH; fade0 = y_head - 380
    for y in range(h):
        a = 0.0
        if y < top_end:
            t = min(1.0, (top_end - y) / (top_end - PY)); a = 0.75 * t ** 1.6 if y >= PY else 1.0
        if y > fade0:
            t = min(1.0, (y - fade0) / (fade1 - fade0)); a = max(a, min(1.0, 0.92 * min(1.0, t * 1.6) ** 1.2 + (0.08 if t >= 1 else 0)))
        px[0, y] = int(255 * a)
    canvas = Image.composite(Image.new('RGB', (w, h), r3.BG), canvas, m.resize((w, h)))
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    lw = 400; logo = r3.LOGO.resize((lw, round(r3.LOGO.height * lw / r3.LOGO.width)), Image.LANCZOS)
    lay.alpha_composite(logo, ((w - lw) // 2, round(h * 0.14) + 40))
    d = ImageDraw.Draw(lay)
    for i, ln in enumerate(lines):
        d.text((x, y_head + i * lh - 20), ln, font=fh, fill=r3.HEAD + (255,))
    d.text((x, y_sub), sub, font=fs, fill=r3.SUB + (255,))
    tr = 37 * 0.4; bw = round(r3.tlen(d, cta, fb, tr) + 208)
    d.rounded_rectangle([x, y_btn, x + bw, y_btn + bh], radius=bh // 2, fill=r3.GOLD + (255,))
    asc, desc = fb.getmetrics()
    r3.tdraw(d, x + 104, y_btn + (bh - (asc + desc)) / 2 + 2, cta, fb, r3.BG + (255,), tr)
    canvas = Image.alpha_composite(canvas.convert('RGBA'), lay).convert('RGB')
    canvas.save(out, quality=93, subsampling=0)
    right = max(x + bw, x + max(d.textlength(l, font=fh) for l in lines), x + d.textlength(sub, font=fs))
    return dict(right=right, side=side, bottom=y_bottom)

if __name__ == '__main__':
    out = '/home/claude/work/r3/'
    only = sys.argv[1:]
    for key, f, head, sub, c45, c916 in MOTIVE:
        if only and key not in only: continue
        a = r3.compose(U + f, out + f'SHIRO_{key}_4x5.jpg', 1440, 1800, c45, head, sub)
        b = story(U + f, out + f'SHIRO_{key}_9x16.jpg', c916, head, sub)
        print(key, 'feed right', round(a['right']), '| story right', round(b['right']), 'max', 1440 - b['side'], 'bottom', b['bottom'], '<=', round(2560 * 0.65))
