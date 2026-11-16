"""SHIRO Meta-Ads Runde 2 (16.11.2026).
Quelle: SHIRO-eigene Instagram-Fotos (1080 x 1350, Text oben weggeschnitten).
4:5 = 1080 x 1350, Foto randabfallend (gleichmaessig skaliert, keine Verzerrung).
9:16 = 1080 x 1920, Foto in voller Breite ohne Hochskalieren, laeuft nach unten in Schwarz aus;
Logo unter der oberen Sperrzone (14 %), Text + Button oberhalb der unteren Sperrzone (35 %).
"""
import sys
sys.path.insert(0, '/home/claude/work')
from PIL import Image, ImageDraw, ImageEnhance
import render_v3 as r3

P = '/home/claude/shirosocialmedia/posts/'


def src_crop(name, top):
    im = Image.open(P + name).convert('RGB')
    im = im.crop((0, int(im.height * top), im.width, im.height))
    im = ImageEnhance.Brightness(im).enhance(1.12)
    return ImageEnhance.Contrast(im).enhance(1.05)


def feed(name, top, out, head, sub, cx=0.5, cy=0.5, zoom=1.0):
    tmp = '/tmp/_src.jpg'
    src_crop(name, top).save(tmp, quality=97)
    return r3.compose(tmp, out, 1080, 1350, dict(cx=cx, cy=cy, zoom=zoom), head, sub)


def story(name, top, out, head, sub, cta='JETZT RESERVIEREN'):
    w, h = 1080, 1920
    s = w / 1440
    ph = src_crop(name, top)
    ph = ph.resize((w, round(ph.height * w / ph.width)), Image.LANCZOS)
    canvas = Image.new('RGB', (w, h), r3.BG)
    y_ph = 0
    canvas.paste(ph, (0, y_ph))
    side = round(w * r3.SAFE['side'])
    x = side + round(24 * s)
    y_bottom = round(h * (1 - r3.SAFE['bottom'])) - round(24 * s)
    fh = r3.font(r3.SER, round(132 * s), 300)
    fs = r3.font(r3.SANS, round(36 * s), 300)
    fb = r3.font(r3.SANS, round(37 * s), 500)
    lines = head.split('\n')
    lh, bh = round(138 * s), round(132 * s)
    y_btn = y_bottom - bh
    y_sub = y_btn - round(108 * s)
    y_head = y_sub - round(36 * s) - lh * len(lines)
    # Verlauf: oben ins Schwarz (Logo), unten ab knapp ueber dem Textblock ins Schwarz
    m = Image.new('L', (1, h)); px = m.load()
    top_end = round(h * 0.14) + round(330 * s)
    fade1 = min(y_head + round(60 * s), y_ph + ph.height)
    fade0 = fade1 - round(440 * s)
    for y in range(h):
        a = 0.0
        if y < top_end:
            t = (top_end - y) / top_end
            a = 0.70 * t * t
        if y > fade0:
            t = min(1.0, (y - fade0) / (fade1 - fade0))
            a = max(a, t ** 1.2)
        if y >= y_ph + ph.height:
            a = 1.0
        px[0, y] = int(255 * a)
    canvas = Image.composite(Image.new('RGB', (w, h), r3.BG), canvas, m.resize((w, h)))
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    logo_w = round(400 * s)
    logo = r3.LOGO.resize((logo_w, round(r3.LOGO.height * logo_w / r3.LOGO.width)), Image.LANCZOS)
    lay.alpha_composite(logo, ((w - logo_w) // 2, round(h * 0.14) + round(40 * s)))
    d = ImageDraw.Draw(lay)
    for i, ln in enumerate(lines):
        d.text((x, y_head + i * lh - round(20 * s)), ln, font=fh, fill=r3.HEAD + (255,))
    d.text((x, y_sub), sub, font=fs, fill=r3.SUB + (255,))
    tr = 37 * s * 0.4
    bw = round(r3.tlen(d, cta, fb, tr) + 2 * 104 * s)
    d.rounded_rectangle([x, y_btn, x + bw, y_btn + bh], radius=bh // 2, fill=r3.GOLD + (255,))
    asc, desc = fb.getmetrics()
    r3.tdraw(d, x + 104 * s, y_btn + (bh - (asc + desc)) / 2 + 2 * s, cta, fb, r3.BG + (255,), tr)
    canvas = Image.alpha_composite(canvas.convert('RGBA'), lay).convert('RGB')
    canvas.save(out, quality=93, subsampling=0)
    right = max(x + bw, x + max(d.textlength(l, font=fh) for l in lines), x + d.textlength(sub, font=fs))
    return dict(right=right, w=w, side=side, btn_bottom=y_bottom)


MOTIVE = [
    ('11_MehrAlsSushi', 'shiro_zart_grid_5.jpg', 0.20, 'Mehr als\nnur Sushi.', 'Sushi, Rolls & warme Gerichte · All you can enjoy', dict(cx=0.45, cy=0.55)),
    ('12_Rolls', 'shiro_klar_grid_5.jpg', 0.18, 'Bestell,\nwas dir schmeckt.', 'Per Tablet am Tisch · frisch für dich gemacht', dict(cx=0.55, cy=0.55)),
    ('13_MittagNigiri', 'shiro_perfektion_grid_5.jpg', 0.25, 'Mittags\nab 24,90 €.', 'Montag bis Freitag · All you can enjoy', dict(cx=0.5, cy=0.5)),
    ('14_Tisch', 'shiro_tisch_grid_5.jpg', 0.22, 'Dein Tisch\nfür heute Abend.', 'Abends 44,40 € · All you can enjoy', dict(cx=0.5, cy=0.5)),
]

if __name__ == '__main__':
    out = '/home/claude/work/r2/'
    for key, f, top, head, sub, crop in MOTIVE:
        a = feed(f, top, out + f'SHIRO_{key}_4x5.jpg', head, sub, **crop)
        b = story(f, top, out + f'SHIRO_{key}_9x16.jpg', head, sub)
        print(key, 'feed right', round(a['right']), '/ 1080', '| story right', round(b['right']), 'max', 1080 - b['side'], 'btn bottom', b['btn_bottom'], '<=', round(1920 * 0.65))
