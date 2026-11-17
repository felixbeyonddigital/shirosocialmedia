"""SHIRO Premium-Reels v3 (17.11.2026) aus dem Rohmaterial 'Videos ohne Logo'.
Aufbau 15 s: 0-11 s Clip (eigener Ton durchgehend), Hook-Headline 0,6-4,4 s,
Logo + Adresse oben bis 11 s; ab 11 s Endkarte über weichgezeichnetem Clip:
Logo, Headline, Preiszeile, Button JETZT RESERVIEREN (Unterkante 60 %), Adresse.
Alles Text zwischen 14 % oben und 65 % unten (Reels-Sperrzonen).
"""
import sys, subprocess
sys.path.insert(0, '/home/claude/work')
import render_v3 as r3
from PIL import Image, ImageDraw
import numpy as np
W, H = 1080, 1920
CHAMP = (201, 189, 166, 255)
SUBC = (205, 201, 188, 240)
GOLD = r3.GOLD + (255,)
SRC = '/mnt/user-data/uploads/SHIRO/Videos ohne Logo/'
OUT = '/home/claude/work/reels3/'

REELS = [
    ('R1_Zart', 7, 4.0, 'Zart. Saftig.\nBesonders.', 'All you can enjoy · ab 24,90 € pro Person'),
    ('R2_Klar', 17, 2.0, 'Klar. Fein.\nUnvergesslich.', 'Sushi & Sashimi · frisch für dich angerichtet'),
    ('R3_Perfektion', 9, 4.5, 'Ein Stück\nPerfektion.', 'Mittags Mo bis Fr · 24,90 € pro Person'),
    ('R4_DeinAbend', 8, 0.0, 'Dein Tisch.\nDein Abend.', 'Abends · 44,40 € pro Person'),
    ('R5_Ankommen', 14, 1.0, 'Ankommen.\nUnd bleiben.', 'All you can enjoy · ab 24,90 € pro Person'),
]
ADDR = 'MÜNCHNER BUNDESSTRASSE 1  ·  SALZBURG'

def vgrad(y0, y1, a0, a1, rgba=(10, 10, 10)):
    g = np.zeros((H,), float)
    for y in range(H):
        if y < y0: g[y] = a0 if y0 > 0 and a0 > a1 else (a0 if y0 == 0 else 0)
    g[:] = 0
    ys = np.arange(H)
    t = np.clip((ys - y0) / max(1, (y1 - y0)), 0, 1)
    g = a0 + (a1 - a0) * t
    img = Image.new('RGBA', (W, H), rgba + (0,))
    img.putalpha(Image.fromarray((np.tile(g[:, None], (1, W)) * 255).astype('uint8')))
    return img

def hook(head):
    from PIL import ImageFilter
    im = vgrad(430, 980, 0.72, 0.0)
    m = np.asarray(im).copy(); m[:430, :, 3] = np.maximum(m[:430, :, 3], 184); im = Image.fromarray(m)
    f = r3.font(r3.SER, 104, 300)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    tx = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(tx)
    for i, ln in enumerate(head.split('\n')):
        ds.text((88, 500 + i * 112), ln, font=f, fill=(0, 0, 0, 200))
        d.text((88, 500 + i * 112), ln, font=f, fill=CHAMP)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    im.alpha_composite(sh); im.alpha_composite(sh); im.alpha_composite(tx)
    return im

def endcard(head, sub):
    im = Image.new('RGBA', (W, H), (10, 10, 10, 150))
    d = ImageDraw.Draw(im)
    lw = 360
    logo = r3.LOGO.resize((lw, round(r3.LOGO.height * lw / r3.LOGO.width)), Image.LANCZOS)
    im.alpha_composite(logo, ((W - lw) // 2, 500))
    f = r3.font(r3.SER, 112, 300)
    y = 690
    for ln in head.split('\n'):
        tw = d.textlength(ln, font=f); d.text(((W - tw) / 2, y), ln, font=f, fill=CHAMP); y += 120
    fs = r3.font(r3.SANS, 30, 300)
    tw = d.textlength(sub, font=fs); d.text(((W - tw) / 2, 970), sub, font=fs, fill=SUBC)
    fb = r3.font(r3.SANS, 30, 500); cta = 'JETZT RESERVIEREN'; tr = 30 * 0.4
    bw = round(r3.tlen(d, cta, fb, tr) + 2 * 78); bh = 100; bx = (W - bw) // 2; by = 1052
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 2, fill=GOLD)
    asc, desc = fb.getmetrics()
    r3.tdraw(d, bx + 78, by + (bh - (asc + desc)) / 2 + 2, cta, fb, r3.BG + (255,), tr)
    fa = r3.font(r3.SANS, 21, 500); tra = 21 * 0.32
    aw = r3.tlen(d, ADDR, fa, tra); r3.tdraw(d, (W - aw) / 2, 1196, ADDR, fa, SUBC, tra)
    return im, by + bh

def build(key, clip, start, head, sub):
    hook(head).save(OUT + f'{key}_hook.png')
    ec, btn_bottom = endcard(head, sub); ec.save(OUT + f'{key}_end.png')
    src = SRC + f'{clip} - HD 1080p.mov'
    fc = (
        "[0:v]trim=0:15,setpts=PTS-STARTPTS,fps=25,format=yuv420p,split[v1][v2];"
        "[v2]boxblur=30:3,format=rgba,fade=in:st=11:d=0.7:alpha=1[bl];"
        "[v1][bl]overlay=0:0[b1];"
        "[1:v]format=rgba,fade=in:st=0.6:d=0.5:alpha=1,fade=out:st=4.0:d=0.5:alpha=1[hk];"
        "[b1][hk]overlay=0:0[b2];"
        "[2:v]format=rgba,fade=out:st=10.9:d=0.5:alpha=1[top];"
        "[b2][top]overlay=0:0[b3];"
        "[3:v]format=rgba,fade=in:st=11.2:d=0.6:alpha=1[ec];"
        "[b3][ec]overlay=0:0,format=yuv420p[v]"
    )
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', str(start), '-t', '15', '-i', src,
           '-loop', '1', '-t', '15', '-i', OUT + f'{key}_hook.png',
           '-loop', '1', '-t', '15', '-i', '/home/claude/work/reels2/ov_full.png',
           '-loop', '1', '-t', '15', '-i', OUT + f'{key}_end.png',
           '-filter_complex', fc, '-map', '[v]', '-map', '0:a',
           '-af', 'apad,atrim=0:15,afade=t=in:st=0:d=0.3,afade=t=out:st=13.6:d=1.4',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-profile:v', 'high',
           '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', '15', '-movflags', '+faststart',
           OUT + f'SHIRO_{key}_9x16.mp4']
    subprocess.run(cmd, check=True)
    return btn_bottom

if __name__ == '__main__':
    only = sys.argv[1:]
    for r in REELS:
        if only and r[0] not in only: continue
        print(r[0], 'button bottom', build(*r), '<=', round(H * 0.65))
