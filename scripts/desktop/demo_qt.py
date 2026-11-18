"""Desktop demo: uv run --extra demo python scripts/desktop/demo_qt.py."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import numpy as np
from PIL import Image
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QFont, QFontDatabase
from PyQt6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,
    QGridLayout,QLabel,QPushButton,QComboBox,QFileDialog,QMessageBox,QTabWidget,
    QTableWidget,QTableWidgetItem,QPlainTextEdit,QGroupBox,QMenu,QAbstractItemView)
import scripts.desktop.demo_engine as engine
def configure_app(app):
    app.setStyle('Fusion')
    # Qt offscreen has no platform font discovery on some Windows installs.
    font_file=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/segoeui.ttf'
    if font_file.exists():
        font_id=QFontDatabase.addApplicationFont(str(font_file))
        if font_id<0: raise RuntimeError('Không nạp được font Segoe UI')
        app.setFont(QFont(QFontDatabase.applicationFontFamilies(font_id)[0],10))


class Worker(QThread):
    result_ready=pyqtSignal(object)
    failed=pyqtSignal(str)
    def __init__(self,image,selection):
        super().__init__(); self.image=image; self.selection=selection
    def run(self):
        try: self.result_ready.emit(engine.infer(self.image,self.selection))
        except Exception as exc: self.failed.emit(str(exc))


def pixmap(values):
    if values.ndim==2: values=np.repeat(values[...,None],3,axis=2)
    array=np.ascontiguousarray(np.clip(values*255,0,255).astype(np.uint8))
    h,w,_=array.shape
    image=QImage(array.data,w,h,array.strides[0],QImage.Format.Format_RGB888).copy()
    return QPixmap.fromImage(image)


class Window(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('SAR — Phát hiện vùng nghi dầu'); self.resize(1120,850)
        self.image_path=None; self.truth_path=None; self.result=None; self.metrics=None; self.worker=None
        self.reference_arrays=None
        root=QWidget(); layout=QVBoxLayout(root); self.setCentralWidget(root)
        intro=QLabel('Demo mô hình SOS • NumPy • Chỉ phân biệt dầu/nền; chưa xác nhận từng loại tương tự dầu.')
        intro.setWordWrap(True); layout.addWidget(intro)
        controls=QHBoxLayout(); layout.addLayout(controls)
        self.open_button=QPushButton('Mở ảnh SAR 8-bit'); self.open_button.clicked.connect(self.open_image); controls.addWidget(self.open_button)
        self.sample_button=QPushButton('Ảnh mẫu SOS'); controls.addWidget(self.sample_button)
        samples=QMenu(self.sample_button)
        for caption,identifier in [('Ảnh đầu danh sách test',None),('Ca phân mảnh: sentinel_440','val/sentinel_440'),('Ca bỏ sót: sentinel_591','val/sentinel_591')]:
            action=samples.addAction(caption); action.triggered.connect(lambda checked=False,key=identifier:self.sample(key))
        self.sample_button.setMenu(samples)
        self.truth_button=QPushButton('Mask tham chiếu (tùy chọn)'); self.truth_button.clicked.connect(self.open_truth); controls.addWidget(self.truth_button)
        self.clear_truth=QPushButton('Bỏ mask'); self.clear_truth.clicked.connect(self.remove_truth); controls.addWidget(self.clear_truth)
        row=QHBoxLayout(); layout.addLayout(row)
        self.choice=QComboBox(); self.choice.addItems(list(engine.SELECTIONS)); self.choice.currentIndexChanged.connect(self.invalidate); row.addWidget(self.choice,1)
        self.run_button=QPushButton('Chạy phát hiện'); self.run_button.clicked.connect(self.run_inference); row.addWidget(self.run_button)
        self.save_button=QPushButton('Xuất kết quả'); self.save_button.clicked.connect(self.save); self.save_button.setEnabled(False); row.addWidget(self.save_button)
        self.paths=QLabel('Chưa chọn ảnh.'); self.paths.setWordWrap(True); self.paths.setTextFormat(Qt.TextFormat.PlainText); layout.addWidget(self.paths)
        self.tabs=QTabWidget(); layout.addWidget(self.tabs,1)
        visual=QWidget(); grid=QGridLayout(visual); self.views={}
        for i,(key,title) in enumerate([('image','Ảnh đầu vào'),('filtered','Sau lọc Lee'),('candidates','Vùng tối ứng viên'),('overlay','Đỏ: vùng được giữ là nghi dầu')]):
            box=QGroupBox(title); box_layout=QVBoxLayout(box); label=QLabel('Chưa chạy'); label.setAlignment(Qt.AlignmentFlag.AlignCenter); label.setMinimumSize(260,200); box_layout.addWidget(label)
            grid.addWidget(box,i//2,i%2); self.views[key]=label
        self.tabs.addTab(visual,'Ảnh và kết quả')
        reference_view=QWidget(); reference_layout=QHBoxLayout(reference_view); self.reference_views=[]
        for title in ['Mask tham chiếu: trắng là dầu (>=128)', 'Sai số pixel: TP xanh lá, FP đỏ, FN lam']:
            box=QGroupBox(title); box_layout=QVBoxLayout(box); label=QLabel('Chưa có mask tham chiếu')
            label.setAlignment(Qt.AlignmentFlag.AlignCenter); label.setMinimumSize(260,200)
            box_layout.addWidget(label); reference_layout.addWidget(box); self.reference_views.append(label)
        self.tabs.addTab(reference_view,'Đối chiếu nhãn')
        self.table=QTableWidget(); self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabs.addTab(self.table,'Đặc trưng vùng')
        self.details=QPlainTextEdit(); self.details.setReadOnly(True); self.tabs.addTab(self.details,'Cấu hình và giới hạn')
        self.status=QLabel('Chọn ảnh hoặc dùng ảnh mẫu. Mask chỉ dùng để đánh giá sau suy luận.'); self.status.setWordWrap(True); self.status.setTextFormat(Qt.TextFormat.PlainText); layout.addWidget(self.status)
        self.tabs.currentChanged.connect(lambda:QTimer.singleShot(0,self.refresh_previews))

    def refresh_previews(self):
        if self.result is None: return
        for key,label in self.views.items():
            label.setPixmap(pixmap(self.result[key]).scaled(label.size(),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        if self.reference_arrays is not None:
            for label,array in zip(self.reference_views,self.reference_arrays):
                label.setPixmap(pixmap(array).scaled(label.size(),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if getattr(self,'result',None) is not None: QTimer.singleShot(0,self.refresh_previews)

    def update_paths(self):
        self.paths.setText(f'Ảnh: {self.image_path or "chưa chọn"}\nMask: {self.truth_path or "không dùng"}')

    def invalidate(self):
        self.result=None; self.metrics=None; self.reference_arrays=None; self.save_button.setEnabled(False); self.table.setRowCount(0)
        for label in self.views.values(): label.clear(); label.setText('Chưa chạy')
        for label in self.reference_views: label.clear(); label.setText('Chưa có mask tham chiếu')
        self.details.clear(); self.status.setText('Cấu hình/ảnh đã đổi. Chạy lại để xem kết quả.'); self.update_paths()

    def open_image(self):
        path,_=QFileDialog.getOpenFileName(self,'Chọn ảnh SAR','','Ảnh (*.png *.jpg *.jpeg *.tif *.tiff)')
        if path:
            self.image_path=Path(path); self.truth_path=None; self.invalidate()

    def sample(self,identifier=None):
        try:
            from sar_oil.data import records
            rows=records('test'); row=rows[0] if identifier is None else next(r for r in rows if r['id']==identifier)
            self.image_path=engine.ROOT/row['image']; self.truth_path=engine.ROOT/row['mask']; self.invalidate()
        except Exception as exc: self.error(str(exc))

    def open_truth(self):
        path,_=QFileDialog.getOpenFileName(self,'Chọn mask đã căn chỉnh (>=128 là dầu)','','Ảnh (*.png *.jpg *.tif *.tiff)')
        if path:
            self.truth_path=Path(path); self.update_paths()
            if self.result is not None: self.assess()

    def remove_truth(self):
        self.truth_path=None; self.metrics=None; self.update_paths()
        if self.result is not None: self.assess()

    def busy(self,value):
        for control in [self.open_button,self.sample_button,self.truth_button,self.clear_truth,self.choice,self.run_button]: control.setEnabled(not value)

    def run_inference(self):
        if self.image_path is None:
            self.status.setText('Hãy chọn ảnh trước khi chạy.'); return
        self.invalidate(); self.busy(True); self.status.setText('Đang chạy NumPy…')
        self.worker=Worker(self.image_path,engine.SELECTIONS[self.choice.currentText()])
        self.worker.result_ready.connect(self.show_result); self.worker.failed.connect(self.error)
        self.worker.finished.connect(lambda:self.busy(False)); self.worker.start()

    def error(self,message):
        self.status.setText('Không thể xử lý: '+message); self.save_button.setEnabled(False)

    def show_result(self,result):
        self.result=result; self.save_button.setEnabled(True)
        for key,label in self.views.items():
            label.setPixmap(pixmap(result[key]).scaled(label.size(),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        regions=result['metadata']['regions']
        from sar_oil.core import FEATURES
        headers=['ID','Nghi dầu','Điểm quyết định']+list(FEATURES)
        self.table.setColumnCount(len(headers)); self.table.setHorizontalHeaderLabels(headers); self.table.setRowCount(len(regions))
        for r,region in enumerate(regions):
            values=[region['id'],'Có' if region['oil'] else 'Không',f"{region['score']:.6f}"]+[f"{region['features'][key]:.6g}" for key in FEATURES]
            for c,value in enumerate(values): self.table.setItem(r,c,QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()
        self.details.setPlainText('Điểm quyết định không phải xác suất. Ảnh khác SOS có thể lệch miền.\n'
            'Chia 255 không phải chuẩn hóa góc tới. Nhánh góc tới/gió thật nằm ở notebook 07.\n'
            'Niblack chỉ được đánh giá validation; không dùng số test của Otsu cho nhánh đó.\n\n'+json.dumps(result['metadata'],ensure_ascii=False,indent=2))
        self.assess()

    def assess(self):
        self.metrics=None; self.reference_arrays=None
        for label in self.reference_views: label.clear(); label.setText('Chưa có mask tham chiếu hợp lệ')
        regions=self.result['metadata']['regions']
        summary=f"{len(regions)} vùng ứng viên; {sum(r['oil'] for r in regions)} vùng nghi dầu."
        if self.truth_path:
            try:
                self.metrics=engine.assess(self.result,self.truth_path)
                with Image.open(self.truth_path) as source: truth=np.asarray(source.convert('L'))>=128
                prediction=self.result['mask']; errors=np.zeros((*truth.shape,3))
                errors[prediction & truth]=[0,1,0]; errors[prediction & ~truth]=[1,0,0]; errors[~prediction & truth]=[0,0,1]
                self.reference_arrays=[truth,errors]
                for label,array in zip(self.reference_views,[truth,errors]):
                    label.setPixmap(pixmap(array).scaled(label.size(),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
                fmt=lambda x:'N/A' if x is None else f'{x:.4f}'
                m=self.metrics
                summary+=f" Đánh giá ảnh này: TP={m['tp']}, FP={m['fp']}, FN={m['fn']}; P={fmt(m['precision'])}, R={fmt(m['recall'])}, F1={fmt(m['f1'])}."
                summary+=' Đây không phải chỉ số toàn tập test.'
            except Exception as exc: summary+=' Không đánh giá được mask: '+str(exc)
        else: summary+=' Chưa có mask tham chiếu để tính độ chính xác.'
        self.status.setText(summary)

    def save(self):
        if self.result is None: return
        folder=QFileDialog.getExistingDirectory(self,'Chọn nơi lưu thư mục kết quả mới')
        if folder:
            destination=Path(folder)/('prediction_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid4().hex[:6])
            try:
                engine.export(self.result,destination,self.metrics,self.truth_path)
                self.status.setText('Đã lưu mask.png, overlay.png, regions.json tại '+str(destination))
            except Exception as exc: self.error(str(exc))

    def closeEvent(self,event):
        if self.worker is not None and self.worker.isRunning():
            self.status.setText('Đang tính toán; hãy đóng cửa sổ sau khi có kết quả.'); event.ignore()
        else: event.accept()


if __name__=='__main__':
    app=QApplication(sys.argv); configure_app(app)
    window=Window(); window.show(); sys.exit(app.exec())
