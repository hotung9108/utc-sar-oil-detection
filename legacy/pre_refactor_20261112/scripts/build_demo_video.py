"""Render the captured Streamlit demo with Vietnamese captions (no voice/audio).

Capture is performed separately by record_demo_video.py. Dependencies are local
to .cache/video_deps and are not runtime dependencies of the image application.
"""
from pathlib import Path
import sys,json,subprocess,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.cache/video_deps'))
import imageio_ffmpeg
OUT=ROOT/'docs/video'; CACHE=ROOT/'.cache/video_demo'
OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True)
def stamp(t,ass=False):
    h=int(t//3600);m=int(t%3600//60);s=t%60
    return f'{h}:{m:02}:{s:05.2f}' if ass else f'{h:02}:{m:02}:{int(s):02},{round((s%1)*1000):03}'
captions=json.loads((OUT/'demo_captions.json').read_text(encoding='utf-8'))
assert captions[0][0]==0 and captions[-1][1]==360
assert all(a<b and (i==0 or a==captions[i-1][1]) for i,(a,b,t) in enumerate(captions))
assert all(len(t.splitlines())<=2 for a,b,t in captions)
srt='\n\n'.join(f'{i}\n{stamp(a)} --> {stamp(b)}\n{t}' for i,(a,b,t) in enumerate(captions,1))+'\n'
(OUT/'DEMO_BTL_XLA_V2.srt').write_text(srt,encoding='utf-8-sig')
(OUT/'LOI_DAN_VA_MOC_THOI_GIAN.txt').write_text('LỜI DẪN VIDEO DEMO BTL XỬ LÝ ẢNH\nThời lượng: 6 phút. Video không có tiếng; nhóm có thể thu giọng theo các mốc này.\n\n'+'\n\n'.join(f'{stamp(a)} – {stamp(b)}\n{t.replace(chr(10)," ")}' for a,b,t in captions),encoding='utf-8')
ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1600
PlayResY: 900
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,29,&H00FFFFFF,&H00FFFFFF,&H00101010,&H00101010,0,0,0,0,100,100,0,0,1,1,0,2,30,30,14,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
for a,b,t in captions: ass+=f'Dialogue: 0,{stamp(a,True)},{stamp(b,True)},Default,,0,0,0,,'+t.replace('\n',r'\N')+'\n'
(CACHE/'captions.ass').write_text(ass,encoding='utf-8-sig')
if '--captions-only' not in sys.argv:
    manifest=json.loads((CACHE/'capture.json').read_text(encoding='utf-8'))
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    # Relative subtitle path avoids Windows drive-colon escaping in FFmpeg filters.
    cmd=[ff,'-y','-hide_banner','-ss',str(manifest['trim_start']),'-i',manifest['raw_video'],
         '-t','360','-vf',"scale=1600:800,pad=1600:900:0:0:color=0x101010,ass=captions.ass",'-r','25',
         '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-an','-movflags','+faststart',
         str(OUT/'DEMO_BTL_XLA_V2_6_PHUT.mp4')]
    with (CACHE/'encode.log').open('w',encoding='utf-8') as log:
        result=subprocess.run(cmd,cwd=CACHE,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode: raise RuntimeError('Encoding failed; inspect .cache/video_demo/encode.log')
    print(OUT/'DEMO_BTL_XLA_V2_6_PHUT.mp4')
else:
    print('Captions and timed reading script written')
