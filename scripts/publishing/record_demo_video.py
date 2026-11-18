"""Record a captioned, automated Qt demonstration; no synthetic predictions/audio.

Default: 24 chapters x 15 seconds = six minutes at two frames/second.
Offscreen Qt capture records this app only, not other desktop applications.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "scripts"))

import argparse
import hashlib
import json
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import subprocess
import time
from pathlib import Path

import imageio_ffmpeg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont,QImage
from PyQt6.QtWidgets import QApplication,QLabel
from scripts.desktop.demo_qt import Window,configure_app
import scripts.desktop.demo_engine as engine
ROOT=engine.ROOT


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interval',type=int,default=15,choices=range(3,31))
    parser.add_argument('--output',type=Path,default=ROOT/'deliverables/video/SAR_demo_v1.mp4')
    args=parser.parse_args()
    if args.output.exists(): raise FileExistsError('Choose a new --output filename; preserve reviewed versions')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    preview=ROOT/'.cache/video'/args.output.stem; preview.mkdir(parents=True,exist_ok=True)
    evaluation=json.loads((ROOT/'results/sos/evaluation.json').read_text())
    total=evaluation['test_final']['metrics']
    app=QApplication([]); configure_app(app); app.setFont(QFont(app.font().family(),11))
    window=Window(); window.setFixedSize(1280,960)
    caption=QLabel(); caption.setWordWrap(True); caption.setTextFormat(Qt.TextFormat.PlainText)
    caption.setStyleSheet('background:#123c56;color:white;padding:12px;font-size:18px;')
    caption.setFixedHeight(112); window.centralWidget().layout().insertWidget(0,caption)
    window.show(); app.processEvents()
    export_path=preview/'export'
    if export_path.exists(): raise FileExistsError('Preview export exists; choose a new output basename')

    def sample(identifier=None): window.sample(identifier); window.tabs.setCurrentIndex(0)
    def branch(index): window.choice.setCurrentIndex(index); window.tabs.setCurrentIndex(0)
    def run():
        if window.worker is not None and window.worker.isRunning(): raise RuntimeError('Previous inference is still running')
        window.run_button.click()
    def failure(identifier): branch(0); sample(identifier); run()
    def export():
        assert window.result is not None
        engine.export(window.result,export_path,window.metrics,window.truth_path)
        window.status.setText('Đã xuất mask.png, overlay.png và regions.json qua bộ xử lý dùng chung của GUI.')

    chapters=[
      ('Mục tiêu', 'Demo tự động của ứng dụng PyQt. Chạy mô hình NumPy đã cố định; phụ đề thay lời thuyết minh. Đây không phải ghi hình thao tác của thành viên nhóm.',lambda:None),
      ('Đầu vào', 'Chọn ảnh đầu danh sách test SOS và mask đi kèm. Mask chỉ phục vụ đối chiếu sau suy luận; không truyền vào mô hình.',lambda:sample()),
      ('Chạy Otsu / SVM', 'Bấm chạy phát hiện. Worker xử lý ảnh ở nền; giao diện không huấn luyện lại hoặc chọn tham số theo ảnh đang xem.',run),
      ('Các bước xử lý', 'Ảnh gốc → lọc Lee → vùng tối ứng viên → phân lớp vùng. Overlay đỏ là vùng nghi dầu, không phải xác nhận ngoài hiện trường.',lambda:None),
      ('Đối chiếu nhãn', 'Bên trái là mask tham chiếu. Bên phải: TP pixel xanh lá, FP đỏ, FN lam. Chỉ số đối tượng phía dưới dùng ghép một-một với IoU ≥ 0,5.',lambda:window.tabs.setCurrentIndex(1)),
      ('Tám đặc trưng', 'Bảng vùng gồm hình dạng và cường độ: diện tích, độ thuôn dài, độ lấp đầy, độ phức tạp biên, trung bình, độ lệch chuẩn, gradient và tương phản nền.',lambda:window.tabs.setCurrentIndex(2)),
      ('Điểm phân lớp', 'Điểm quyết định SVM lớn hơn 0 thì giữ vùng. Điểm này không phải xác suất. Bảng đặc trưng chỉ đọc; xuất JSON giữ nguyên số thực.',lambda:None),
      ('Cấu hình có thể truy vết', 'Tab cấu hình lưu lựa chọn, hash ảnh và model. Lựa chọn chính từ validation; ảnh mẫu không được dùng để điều chỉnh mô hình.',lambda:window.tabs.setCurrentIndex(3)),
      ('Lý do chọn thuật toán', '110 cấu hình lọc/ngưỡng và 729 tổ hợp tiếp theo có số liệu lưu trong results/sos. Không khẳng định đã duyệt mọi thuật toán hoặc mọi tham số có thể có.',lambda:None),
      ('Giới hạn bằng chứng Lee', 'Thí nghiệm bổ sung chưa chứng minh Lee vượt Mean 7: khoảng bootstrap của chênh lệch F1 chứa 0. Xem selection_evidence; không chỉ dựa vào lý thuyết để kết luận tốt hơn.',lambda:None),
      ('Nhánh ngưỡng thích nghi', 'Chuyển sang Niblack + CART. Nhánh này được khảo sát bổ sung trên validation; không lấy chỉ số test Otsu để đại diện cho nó.',lambda:branch(1)),
      ('Chạy Niblack / CART', 'Chạy lại trên cùng ảnh và cùng mask. Phân ngưỡng cục bộ thay đổi các vùng ứng viên, do đó kết quả phân lớp có thể khác.',run),
      ('So sánh trực quan', 'Quan sát các vùng nhỏ xuất hiện trong nhánh Niblack. Một ảnh minh họa không đủ kết luận nhánh nào tốt hơn trên toàn tập.',lambda:window.tabs.setCurrentIndex(0)),
      ('Đối chiếu Niblack', 'Đọc TP/FP/FN và F1 của đúng ảnh đang xem. Số liệu validation của nhánh bổ sung được báo riêng trong results/sos/adaptive.',lambda:window.tabs.setCurrentIndex(1)),
      ('Ca thất bại: phân mảnh', 'Chuyển lại Otsu/SVM và chạy sentinel_440. Đây là ca lỗi đã chọn theo tiêu chí công bố, không loại khỏi đánh giá.',lambda:failure('val/sentinel_440')),
      ('Phân mảnh và F1 đối tượng', 'Ground truth phủ patch, nhưng dự đoán bị chia nhỏ: TP=0, FP=35, FN=1. Pixel đúng vẫn có thể nhiều trong khi không ghép được đối tượng ở IoU ≥ 0,5.',lambda:window.tabs.setCurrentIndex(1)),
      ('Ca thất bại: bỏ sót', 'Chạy sentinel_591. Không thay ngưỡng hoặc cấu hình để làm đẹp ảnh minh họa.',lambda:failure('val/sentinel_591')),
      ('Vùng dầu bị loại', 'Classifier loại toàn bộ vùng ứng viên: TP=0, FP=0, FN=1. Precision không xác định khi không dự đoán vùng nào; giao diện ghi N/A.',lambda:window.tabs.setCurrentIndex(1)),
      ('Xuất kết quả thật', 'Video gọi bộ xử lý xuất dùng chung của GUI, không thao tác hộp thoại hệ điều hành. Ba tệp được ghi thật: mask.png, overlay.png, regions.json.',export),
      ('Không có nhãn thì không có độ chính xác', 'Bỏ mask tham chiếu. Dự đoán giữ nguyên, nhưng không còn báo Precision/Recall/F1 cho ảnh này.',window.remove_truth),
      ('Kết quả toàn tập SOS', f"Trên 839 ảnh test: Precision={total['precision']:.5f}, Recall={total['recall']:.5f}, F1 đối tượng={total['f1']:.5f}. TP={total['tp']}, FP={total['fp']}, FN={total['fn']}. Không lấy F1 ảnh mẫu thay số toàn tập.",lambda:None),
      ('Nhánh vật lý riêng', 'Notebook 07 dùng DN Sentinel-1 thật, LUT góc tới/hiệu chuẩn và gió ERA5. Tile đó chưa có nhãn dầu; nhánh này chưa tích hợp vào demo SOS.',lambda:window.tabs.setCurrentIndex(3)),
      ('Phạm vi và giới hạn', 'SOS có dầu/nền, chưa có nhãn riêng mưa, màng sinh học, gió yếu. Chưa kiểm chứng cảnh báo ngoài khơi miền Trung. Tỷ lệ báo nhầm DARTIS chỉ công bố khi đủ dữ liệu.',lambda:None),
      ('Chạy lại và kiểm tra', 'Mở demo: uv run --frozen --extra demo python scripts/desktop/demo_qt.py. Notebook và mã kiểm chứng nằm trong repo; hướng dẫn chi tiết: docs/DEMO_GUI.md.',lambda:None),
    ]
    command=[imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-n',
        '-f','rawvideo','-pixel_format','rgb24','-video_size','1280x960','-framerate','2',
        '-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',
        '-movflags','+faststart',str(args.output)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    timeline=[]; start=time.monotonic(); frame_count=0
    sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
             [Path(__file__).resolve(),ROOT/'scripts/desktop/demo_qt.py',ROOT/'scripts/desktop/demo_engine.py']}
    try:
        for index,(title,text,action) in enumerate(chapters):
            caption.setText(f'{index+1:02d}/24 — {title}\n{text}'); action(); app.processEvents(); window.refresh_previews()
            if index in (15,17):
                expected=(0,35,1) if index==15 else (0,0,1)
                assert window.metrics is not None
                assert tuple(window.metrics[k] for k in ('tp','fp','fn'))==expected
            print(f'Chapter {index+1}/24: {title.encode("ascii",errors="replace").decode()}',flush=True)
            shot=preview/f'chapter-{index+1:02d}.png'; window.grab().save(str(shot))
            timeline.append({'start_seconds':index*args.interval,'title':title,'caption':text,
                             'preview':shot.relative_to(ROOT).as_posix()})
            for _ in range(args.interval*2):
                target=start+frame_count/2
                while time.monotonic()<target:
                    app.processEvents(); time.sleep(max(0,min(0.01,target-time.monotonic())))
                app.processEvents()
                image=window.grab().toImage().convertToFormat(QImage.Format.Format_RGB888)
                assert (image.width(),image.height(),image.bytesPerLine())==(1280,960,3840)
                process.stdin.write(image.constBits().asstring(image.sizeInBytes()))
                frame_count+=1
        if window.worker is not None: window.worker.wait(90000)
        process.stdin.close()
        stderr=process.stderr.read().decode('utf-8',errors='replace')
        if process.wait(timeout=120)!=0: raise RuntimeError(stderr)
    except BaseException:
        process.kill(); process.wait(); raise
    finally:
        window.close(); app.processEvents()
    assert export_path.joinpath('mask.png').exists()
    info={'video':str(args.output),'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
          'frames':frame_count,'fps':2,'expected_duration_seconds':frame_count/2,
          'meets_5_to_7_minutes':300<=frame_count/2<=420,'audio':False,
          'capture':'Automated Qt offscreen application capture; captions; not a student performance recording',
          'wall_clock_seconds':time.monotonic()-start,'sources_sha256':sources,
          'timeline':timeline,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'reviewed':False}
    args.output.with_suffix('.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in info.items() if k!='timeline'},ensure_ascii=True))


if __name__=='__main__': main()
