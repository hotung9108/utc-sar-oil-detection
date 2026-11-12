"""Scientific figure of observed ablation outputs; no synthetic SAR evidence."""
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/preprocessing_ablation'
for case in ['class_1_00013','sea_surface_01']:
    fig,axes=plt.subplots(3,4,figsize=(12,9),layout='constrained')
    for c,(key,label) in enumerate([('A_raw','A. Không tiền xử lý'),('B_lee','B. Chỉ Lee'),('C_clahe','C. Chỉ CLAHE'),('D_lee_clahe','D. Lee + CLAHE')]):
        for r,(kind,rowlabel) in enumerate([('enhanced','Ảnh vào bước biên'),('canny','Biên Canny 35/90'),('mask','Mask ứng viên')]):
            im=np.asarray(Image.open(OUT/case/f'{key}_{kind}.png'))
            axes[r,c].imshow(im,cmap='gray',vmin=0,vmax=255,interpolation='nearest')
            axes[r,c].set_xticks([]);axes[r,c].set_yticks([])
            if r==0:axes[r,c].set_title(label,fontsize=13)
            if c==0:axes[r,c].set_ylabel(rowlabel,fontsize=12)
    fig.suptitle(f'{case}: cùng ảnh, cùng tham số phía sau\nMặt nạ ứng viên chưa phải nhãn dầu chuẩn',fontsize=15)
    fig.savefig(OUT/f'{case}_comparison.png',dpi=160)
    plt.close(fig)
print('Saved two paired comparison figures.')
