"""TV2: derive Otsu and compare independent NumPy / production / OpenCV."""
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.morphology import custom_otsu_threshold

def otsu_teaching(a):
    hist=np.bincount(a.ravel(),minlength=256).astype(float)
    prob=hist/a.size;best=-1.;chosen=0
    for t in range(256):
        w0=prob[:t+1].sum();w1=1-w0
        if w0==0 or w1==0:continue
        m0=(np.arange(t+1)*prob[:t+1]).sum()/w0
        m1=(np.arange(t+1,256)*prob[t+1:]).sum()/w1
        score=w0*w1*(m0-m1)**2
        if score>best:best=score;chosen=t
    return chosen,best

def main():
    a=np.array([[50,50,200,200]]*4,dtype=np.uint8)
    t,score=otsu_teaching(a)
    assert t==50 and score==5625
    assert custom_otsu_threshold(a)==(50,1.0)
    import cv2  # Reference only, not the teaching implementation.
    t_lib,binary=cv2.threshold(a,0,255,cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)
    expected=np.array([[255,255,0,0]]*4,dtype=np.uint8)
    np.testing.assert_array_equal(binary,expected)
    assert t_lib==t
    print('Input:\n',a,'\nThreshold:',t,'between-class variance:',score)
    print('Mask:\n',binary,'\nNumPy / production / OpenCV: PASS')

if __name__=='__main__':main()
