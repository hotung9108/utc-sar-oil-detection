"""Decode the entire demo, check duration/provenance, and extract review frames."""
import argparse
import hashlib
import json
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
import subprocess

import imageio_ffmpeg
from PyQt6.QtCore import QRect,Qt
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import QApplication,QLabel
from demo_qt import configure_app

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video',type=Path,default=ROOT/'deliverables/video/SAR_demo_v1.mp4')
    args=parser.parse_args(); video=args.video.resolve()
    receipt=json.loads(video.with_suffix('.json').read_text(encoding='utf-8'))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(video)==receipt['sha256']
    for name,digest in receipt['sources_sha256'].items(): assert sha(ROOT/name)==digest,name
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    reader=imageio_ffmpeg.read_frames(str(video)); metadata=next(reader); reader.close()
    frames,duration=imageio_ffmpeg.count_frames_and_secs(str(video))
    assert frames==receipt['frames']==720 and duration==360
    assert tuple(metadata['size'])==(1280,960) and metadata['codec']=='h264'
    decoded=subprocess.run([ffmpeg,'-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True,check=True)
    assert not decoded.stderr.strip(),decoded.stderr
    app=QApplication([]); configure_app(app)
    label=QLabel(); label.setStyleSheet('font-size:18px;'); label.ensurePolished()
    font_metrics=QFontMetrics(label.font()); caption_checks=[]
    for i,chapter in enumerate(receipt['timeline']):
        text=f"{i+1:02d}/24 — {chapter['title']}\n{chapter['caption']}"
        rect=font_metrics.boundingRect(QRect(0,0,1230,88),Qt.TextFlag.TextWordWrap,text)
        assert rect.height()<=88,chapter['title']
        caption_checks.append({'chapter':i+1,'measured_text_height':rect.height(),'available_height':88})
    review=ROOT/'.cache/video/review'; review.mkdir(parents=True,exist_ok=True)
    extracts=[]
    for chapter in [1,5,7,12,16,18,19,21,24]:
        timestamp=(chapter-1)*15+7
        target=review/f'chapter-{chapter:02d}.png'
        subprocess.run([ffmpeg,'-v','error','-y','-ss',str(timestamp),'-i',str(video),
                        '-frames:v','1',str(target)],capture_output=True,check=True)
        extracts.append({'chapter':chapter,'second':timestamp,'path':target.relative_to(ROOT).as_posix(),'sha256':sha(target)})
    audit={'video':str(video),'sha256':sha(video),'frames':frames,'duration_seconds':duration,
           'size':metadata['size'],'codec':metadata['codec'],'fps':metadata['fps'],
           'full_decode_passed':True,'source_hashes_match':True,'caption_fit':caption_checks,
           'review_frames':extracts,'visual_review_completed':False,'audio':False,
           'note':'Silent captioned automated app demo; no claim of student presentation or real-time benchmark'}
    (ROOT/'docs/management/video_audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'frames':frames,'seconds':duration,'decode_ok':True,'captions_fit':len(caption_checks)}))


if __name__=='__main__': main()
