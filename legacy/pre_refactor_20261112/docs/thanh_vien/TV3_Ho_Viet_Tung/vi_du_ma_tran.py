"""TV3: small Lee and HE implementations; no library in core computation."""
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.filters import custom_lee_filter
from src.enhancement import global_histogram_equalization

def lee_teaching(a,k=3,L=4):
    pad=np.pad(a.astype(float),k//2,mode='reflect');out=np.empty(a.shape,float)
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            patch=pad[y:y+k,x:x+k];mu=patch.mean();v=((patch-mu)**2).mean()
            weight=np.clip(1-mu*mu/L/max(v,1e-8),0,1)
            out[y,x]=mu+weight*(float(a[y,x])-mu)
    return np.clip(np.rint(out),0,255).astype(np.uint8)

def he_teaching(a):
    counts=np.bincount(a.ravel(),minlength=256);cdf=np.cumsum(counts)
    if np.ptp(a)==0:return a.copy()
    cdf_min=cdf[counts>0][0]
    lut=np.clip(np.rint((cdf-cdf_min)/(a.size-cdf_min)*255),0,255).astype(np.uint8)
    return lut[a]

def main():
    a=np.full((5,5),100,np.uint8);a[2,2]=200
    expected=np.array([[100,100,100,100,100],[100,111,111,111,100],
                       [100,111,111,111,100],[100,111,111,111,100],[100,100,100,100,100]],np.uint8)
    out=lee_teaching(a)
    np.testing.assert_array_equal(out,expected)
    np.testing.assert_array_equal(out,custom_lee_filter(a,3,4))
    from scipy.ndimage import uniform_filter  # Moments reference, not a direct Lee API.
    af=a.astype(float);mu=uniform_filter(af,3,mode='mirror')
    var=np.maximum(uniform_filter(af*af,3,mode='mirror')-mu*mu,0)
    weight=np.clip(1-mu*mu/4/np.maximum(var,1e-8),0,1)
    reference=np.clip(np.rint(mu+weight*(af-mu)),0,255).astype(np.uint8)
    np.testing.assert_array_equal(out,reference)
    b=np.array([[0,1,2,3]]*4,np.uint8)
    eq=np.array([[0,85,170,255]]*4,np.uint8)
    np.testing.assert_array_equal(he_teaching(b),eq)
    np.testing.assert_array_equal(global_histogram_equalization(b)[0],eq)
    import cv2
    np.testing.assert_array_equal(cv2.equalizeHist(b),eq)
    print('Lee input:\n',a,'\nLee output:\n',out,'\nHE input:\n',b,'\nHE output:\n',eq,'\nPASS')

if __name__=='__main__':main()
