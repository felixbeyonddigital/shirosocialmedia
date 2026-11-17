"""SHIRO Premium-Reels v5 (17.11.2026): Button JETZT RESERVIEREN ab 1,0 s dauerhaft sichtbar.
Button fix bei y 1108-1208 (Unterkante 62,9 %, Grenze 65 %), weicher Schatten fuer Lesbarkeit auf hellem Bild.
Endkarte ab 11 s ohne eigenen Button, Layout ueber dem Dauer-Button."""
import sys, subprocess
sys.path.insert(0, '/home/claude/work/reels3'); sys.path.insert(0, '/home/claude/work')
import build as b, render_v3 as r3
from PIL import Image, ImageDraw, ImageFilter
W, H = 1080, 1920
OUT = '/home/claude/work/reels5/'
BY, BH = 1108, 100
REELS = [  # key, clip, start, clean, head, sub
    ('R1_Zart', 7, 4.0, None, 'Zart. Saftig.\nBesonders.', 'All you can enjoy · ab 24,90 € pro Person'),
    ('R2_Klar', 17, 2.0, None, 'Klar. Fein.\nUnvergesslich.', 'Sushi & Sashimi · frisch für dich angerichtet'),
    ('R3_Perfektion', 9, 4.5, None, 'Ein Stück\nPerfektion.', 'Mittags Mo bis Fr · 24,90 € pro Person'),
    ('R4_DeinAbend', 8, 0.0, None, 'Dein Tisch.\nDein Abend.', 'Abends · 44,40 € pro Person'),
    ('R5_Ankommen', 14, 1.0, None, 'Ankommen.\nUnd bleiben.', 'All you can enjoy · ab 24,90 € pro Person'),
    ('R6_Gemeinsam', 6, 1.5, None, 'Gemeinsam.\nGenießen.', 'All you can enjoy · ab 24,90 € pro Person'),
    ('R7_Willkommen', 10, 0.0, None, 'Willkommen.\nIm SHIRO.', 'Abends · 44,40 € pro Person'),
    ('R8_Detail', 12, 0.5, None, 'Stil.\nBis ins Detail.', 'All you can enjoy · ab 24,90 € pro Person'),
    ('R9_Handwerk', 26, 0.0, 11.4, 'Handwerk.\nAuf dem Teller.', 'Mittags Mo bis Fr · 24,90 € pro Person'),
    ('R10_DeinPlatz', 15, 0.0, 12.6, 'Dein Platz.\nIst bereit.', 'Abends · 44,40 € pro Person'),
]
def button():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fb = r3.font(r3.SANS, 30, 500); cta = 'JETZT RESERVIEREN'; tr = 30 * 0.4
    bw = round(r3.tlen(d, cta, fb, tr) + 2 * 78); bx = (W - bw) // 2
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    ds.rounded_rectangle([bx - 6, BY + 4, bx + bw + 6, BY + BH + 14], radius=BH // 2, fill=(0, 0, 0, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([bx, BY, bx + bw, BY + BH], radius=BH // 2, fill=b.GOLD)
    asc, desc = fb.getmetrics()
    r3.tdraw(d, bx + 78, BY + (BH - (asc + desc)) / 2 + 2, cta, fb, r3.BG + (255,), tr)
    return im
def endcard(head, sub):
    im = Image.new('RGBA', (W, H), (10, 10, 10, 150)); d = ImageDraw.Draw(im)
    lw = 360
    logo = r3.LOGO.resize((lw, round(r3.LOGO.height * lw / r3.LOGO.width)), Image.LANCZOS)
    im.alpha_composite(logo, ((W - lw) // 2, 470))
    f = r3.font(r3.SER, 112, 300); y = 660
    for ln in head.split('\n'):
        tw = d.textlength(ln, font=f); d.text(((W - tw) / 2, y), ln, font=f, fill=b.CHAMP); y += 120
    fs = r3.font(r3.SANS, 30, 300)
    tw = d.textlength(sub, font=fs); d.text(((W - tw) / 2, 942), sub, font=fs, fill=b.SUBC)
    fa = r3.font(r3.SANS, 21, 500); tra = 21 * 0.32
    aw = r3.tlen(d, b.ADDR, fa, tra); r3.tdraw(d, (W - aw) / 2, 1010, b.ADDR, fa, b.SUBC, tra)
    return im
def build(key, clip, start, clean, head, sub):
    b.hook(head).save(OUT + f'{key}_hook.png'); endcard(head, sub).save(OUT + f'{key}_end.png')
    src = b.SRC + f'{clip} - HD 1080p.mov'
    if clean:
        v0 = f"[0:v]trim=0:{clean},setpts=PTS-STARTPTS,fps=25,tpad=stop_mode=clone:stop_duration=6,trim=0:15,setpts=PTS-STARTPTS,format=yuv420p,split[v1][v2];"
        fo = min(13.6, clean + 1.6)
    else:
        v0 = "[0:v]trim=0:15,setpts=PTS-STARTPTS,fps=25,format=yuv420p,split[v1][v2];"; fo = 13.6
    fc = v0 + (
        "[v2]boxblur=30:3,format=rgba,fade=in:st=11:d=0.7:alpha=1[bl];[v1][bl]overlay=0:0[b1];"
        "[1:v]format=rgba,fade=in:st=0.6:d=0.5:alpha=1,fade=out:st=4.0:d=0.5:alpha=1[hk];[b1][hk]overlay=0:0[b2];"
        "[2:v]format=rgba,fade=out:st=10.9:d=0.5:alpha=1[top];[b2][top]overlay=0:0[b3];"
        "[3:v]format=rgba,fade=in:st=11.2:d=0.6:alpha=1[ec];[b3][ec]overlay=0:0[b4];"
        "[4:v]format=rgba,fade=in:st=0.8:d=0.4:alpha=1[bt];[b4][bt]overlay=0:0,format=yuv420p[v]")
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', str(start), '-t', '15', '-i', src,
           '-loop', '1', '-t', '15', '-i', OUT + f'{key}_hook.png',
           '-loop', '1', '-t', '15', '-i', '/home/claude/work/reels2/ov_full.png',
           '-loop', '1', '-t', '15', '-i', OUT + f'{key}_end.png',
           '-loop', '1', '-t', '15', '-i', OUT + 'button.png',
           '-filter_complex', fc, '-map', '[v]', '-map', '0:a',
           '-af', f'apad,atrim=0:15,afade=t=in:st=0:d=0.3,afade=t=out:st={fo}:d=1.4',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-profile:v', 'high',
           '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', '15', '-movflags', '+faststart',
           OUT + f'SHIRO_{key}_9x16.mp4']
    subprocess.run(cmd, check=True)
if __name__ == '__main__':
    button().save(OUT + 'button.png')
    print('button bottom', BY + BH, 'limit', round(H * 0.65))
    for r in REELS: build(*r); print(r[0])
