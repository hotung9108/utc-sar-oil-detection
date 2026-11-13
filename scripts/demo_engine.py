"""GUI adapter for the frozen pipelines; ground truth is never an inference input."""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sar_oil.pipeline import candidates, predict
from sar_oil.models import RegionModel
from sar_oil.evaluation import counts, summarize
from sar_oil.provenance import ensure_run

SELECTIONS = {
    'SOS: Otsu + SVM (đã đánh giá test)':ROOT/'results/sos/selected.json',
    'Bổ sung: Niblack + CART (chỉ validation)':ROOT/'results/sos/adaptive/selected.json',
}


def load_image(path):
    with Image.open(path) as source:
        if source.mode not in {'L','RGB','RGBA','P'}:
            raise ValueError('Demo nhận ảnh hiển thị 8-bit. SAR DN 16-bit cần nhánh hiệu chuẩn riêng trong notebook 07.')
        if source.width*source.height>1024*1024 or min(source.size)<2:
            raise ValueError('Chọn ảnh có 2 đến 1.048.576 pixel, mỗi chiều ít nhất 2. Demo không tự resize.')
        return np.asarray(source.convert('L'),dtype=float)/255


def infer(image_path, selection_path):
    ensure_run()
    start=time.perf_counter()
    image_path,selection_path=Path(image_path),Path(selection_path)
    if selection_path.resolve() not in {p.resolve() for p in SELECTIONS.values()}:
        raise ValueError('Chỉ dùng hai cấu hình đã lưu của dự án')
    selection=json.loads(selection_path.read_text(encoding='utf-8'))
    model_path=selection_path.parent/selection['model_file']
    image=load_image(image_path)
    model=RegionModel.load(model_path)
    mask,regions=predict(image,selection['config'],model,backend='numpy')
    filtered,labels=candidates(image,selection['config'],backend='numpy')
    rgb=np.repeat(image[...,None],3,axis=2)
    rgb[mask]=0.5*rgb[mask]+0.5*np.array([1,0,0])
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    metadata={'input_file':str(image_path),'input_sha256':sha(image_path),
        'selection_file':str(selection_path.relative_to(ROOT)),
        'selection_sha256':sha(selection_path),'model_sha256':sha(model_path),
        'config':selection['config'],'backend':'numpy','regions':regions,
        'score_semantics':'decision score, not probability',
        'seconds_including_preview':time.perf_counter()-start,
        'shape':list(image.shape),'ground_truth_used_for_inference':False}
    return {'image':image,'filtered':filtered,'candidates':labels>0,'mask':mask,
            'overlay':rgb,'metadata':metadata}


def assess(result, truth_path):
    """Optional evaluation after inference; does not alter predictions."""
    with Image.open(truth_path) as source:
        if source.size != (result['mask'].shape[1],result['mask'].shape[0]):
            raise ValueError('Mask tham chiếu phải cùng kích thước và căn chỉnh với ảnh; không tự resize')
        if source.mode not in {'L','RGB','RGBA','P'}:
            raise ValueError('Mask tham chiếu phải là ảnh 8-bit, dầu có giá trị >=128')
        truth=np.asarray(source.convert('L'))>=128
    if truth.shape!=result['mask'].shape:
        raise ValueError('Mask tham chiếu phải cùng kích thước và căn chỉnh với ảnh; không tự resize')
    return summarize([counts(result['mask'],truth)])


def export(result, directory, metrics=None, truth_path=None):
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True)
    for name in ('mask.png','overlay.png','regions.json'):
        if (directory/name).exists(): raise FileExistsError('Thư mục đã có kết quả; hãy chọn thư mục mới')
    Image.fromarray((result['mask']*255).astype('uint8')).save(directory/'mask.png')
    Image.fromarray(np.clip(result['overlay']*255,0,255).astype('uint8')).save(directory/'overlay.png')
    payload=dict(result['metadata'])
    if metrics is not None:
        payload['post_inference_evaluation']=metrics
        payload['truth_file']=str(truth_path)
        payload['truth_sha256']=hashlib.sha256(Path(truth_path).read_bytes()).hexdigest()
        payload['truth_threshold']=128
    (directory/'regions.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return directory
