"""Decode and inspect local video deliverables; save QA under .cache only."""
from pathlib import Path
import sys,json,subprocess,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.cache/video_deps'))
import imageio_ffmpeg
from PIL import Image
OUT=ROOT/'docs/video'; CACHE=ROOT/'.cache/video_demo'
ff=imageio_ffmpeg.get_ffmpeg_exe();video=OUT/'DEMO_BTL_XLA_V2_6_PHUT.mp4'
assert video.exists() and video.stat().st_size>1000000
info=subprocess.run([ff,'-hide_banner','-i',str(video)],capture_output=True,text=True,encoding='utf-8',errors='replace').stderr
(CACHE/'final_media_info.txt').write_text(info,encoding='utf-8')
assert 'Video: h264' in info and '1600x900' in info and '25 fps' in info,info
assert 'Audio:' not in info,'User requested captions only'
match=re.search(r'Duration: (\d+):(\d+):([\d.]+)',info)
duration=int(match[1])*3600+int(match[2])*60+float(match[3])
assert abs(duration-360)<0.15,duration
decoded=subprocess.run([ff,'-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace')
assert decoded.returncode==0 and not decoded.stderr.strip(),decoded.stderr
captions=json.loads((OUT/'demo_captions.json').read_text(encoding='utf-8'))
assert captions[0][0]==0 and captions[-1][1]==360
for i,(a,b,text) in enumerate(captions):
    assert a<b and (i==0 or a==captions[i-1][1])
    assert len(text.splitlines())<=2
result=json.loads((OUT/'demo_exports/class_1_00013_result.json').read_text(encoding='utf-8'))
assert result['stats']['slicks_count']==1 and result['stats']['total_area_px']==3328
assert result['stats']['area_pct']==2.08
assert result['config']['min_contrast']==0.1 and result['config']['clip_limit']==2
im=Image.open(OUT/'demo_exports/class_1_00013_mask.png')
assert im.size==(400,400)
assert sum(v>0 for v in im.getdata())==3328
times=[0,27,45,56,70,82,96,106,124,142,160,169,181,196,215,232,249,274,292,313,340,357]
for sec in times:
    subprocess.run([ff,'-y','-v','error','-ss',str(sec),'-i',str(video),'-frames:v','1',str(CACHE/f'final_{sec:03}.png')],check=True)
audit={'duration_seconds':duration,'resolution':'1600x900','fps':25,'codec':'H.264','audio_streams':0,
       'caption_cues':len(captions),'decoded_without_errors':True,'sample_mask_pixels':3328,
       'review_frames_seconds':times,'visual_review_pending':True,
       'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'size_bytes':video.stat().st_size}
(CACHE/'final_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(audit,ensure_ascii=False))
