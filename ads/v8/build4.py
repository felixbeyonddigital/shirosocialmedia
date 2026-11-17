"""SHIRO Premium-Reels R6-R10 (17.11.2026), gleicher Aufbau wie reels3/build.py.
Neu: 'clean' = Sekunde im Clip, ab der das eingebrannte Schlusslogo kommt bzw. der Clip endet;
ab dort wird das letzte saubere Bild gehalten (liegt unter der weichgezeichneten Endkarte)."""
import sys, subprocess
sys.path.insert(0, '/home/claude/work/reels3'); sys.path.insert(0, '/home/claude/work')
import build as b
OUT = '/home/claude/work/reels4/'
b.OUT = OUT
REELS = [
    ('R6_Gemeinsam', 6, 1.5, None, 'Gemeinsam.\nGenießen.', 'All you can enjoy · ab 24,90 € pro Person'),
    ('R7_Willkommen', 10, 0.0, None, 'Willkommen.\nIm SHIRO.', 'Abends · 44,40 € pro Person'),
    ('R8_Detail', 12, 0.5, None, 'Stil.\nBis ins Detail.', 'All you can enjoy · ab 24,90 € pro Person'),
    ('R9_Handwerk', 26, 0.0, 11.4, 'Handwerk.\nAuf dem Teller.', 'Mittags Mo bis Fr · 24,90 € pro Person'),
    ('R10_DeinPlatz', 15, 0.0, 12.6, 'Dein Platz.\nIst bereit.', 'Abends · 44,40 € pro Person'),
]
def build(key, clip, start, clean, head, sub):
    b.hook(head).save(OUT + f'{key}_hook.png')
    ec, bb = b.endcard(head, sub); ec.save(OUT + f'{key}_end.png')
    src = b.SRC + f'{clip} - HD 1080p.mov'
    if clean:
        v0 = f"[0:v]trim=0:{clean},setpts=PTS-STARTPTS,fps=25,tpad=stop_mode=clone:stop_duration=6,trim=0:15,setpts=PTS-STARTPTS,format=yuv420p,split[v1][v2];"
        fo = min(13.6, clean + 1.6)
    else:
        v0 = "[0:v]trim=0:15,setpts=PTS-STARTPTS,fps=25,format=yuv420p,split[v1][v2];"
        fo = 13.6
    fc = v0 + (
        "[v2]boxblur=30:3,format=rgba,fade=in:st=11:d=0.7:alpha=1[bl];[v1][bl]overlay=0:0[b1];"
        "[1:v]format=rgba,fade=in:st=0.6:d=0.5:alpha=1,fade=out:st=4.0:d=0.5:alpha=1[hk];[b1][hk]overlay=0:0[b2];"
        "[2:v]format=rgba,fade=out:st=10.9:d=0.5:alpha=1[top];[b2][top]overlay=0:0[b3];"
        "[3:v]format=rgba,fade=in:st=11.2:d=0.6:alpha=1[ec];[b3][ec]overlay=0:0,format=yuv420p[v]")
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', str(start), '-t', '15', '-i', src,
           '-loop', '1', '-t', '15', '-i', OUT + f'{key}_hook.png',
           '-loop', '1', '-t', '15', '-i', '/home/claude/work/reels2/ov_full.png',
           '-loop', '1', '-t', '15', '-i', OUT + f'{key}_end.png',
           '-filter_complex', fc, '-map', '[v]', '-map', '0:a',
           '-af', f'apad,atrim=0:15,afade=t=in:st=0:d=0.3,afade=t=out:st={fo}:d=1.4',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-profile:v', 'high',
           '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', '15', '-movflags', '+faststart',
           OUT + f'SHIRO_{key}_9x16.mp4']
    subprocess.run(cmd, check=True); return bb
if __name__ == '__main__':
    for r in REELS: print(r[0], 'button bottom', build(*r))
