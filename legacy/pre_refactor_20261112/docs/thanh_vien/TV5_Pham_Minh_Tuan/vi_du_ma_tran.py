"""TV5: distinguish changes in contrast, entropy and brightness from accuracy."""
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.metrics import calculate_rms_contrast,calculate_entropy,calculate_ambe,calculate_ssi

def measurements(a,b):
    a=a.astype(float);b=b.astype(float)
    def entropy(x):
        counts=np.bincount(x.astype(np.uint8).ravel(),minlength=256)
        p=counts[counts>0]/x.size
        return float(-(p*np.log2(p)).sum())
    sa=np.sqrt(((a-a.mean())**2).mean());sb=np.sqrt(((b-b.mean())**2).mean())
    return np.array([a.mean(),b.mean(),sa,sb,abs(a.mean()-b.mean()),
                     ((a-b)**2).mean(),entropy(a),entropy(b),(sb/b.mean())/(sa/a.mean())])

def main():
    a=np.array([[0,0,2,2]]*4,np.uint8);b=np.array([[0,1,1,2]]*4,np.uint8)
    expected=np.array([1,1,1,np.sqrt(.5),0,.5,1,1.5,np.sqrt(.5)])
    measured=measurements(a,b);np.testing.assert_allclose(measured,expected,atol=1e-12)
    np.testing.assert_allclose([calculate_rms_contrast(a),calculate_rms_contrast(b),
                               calculate_ambe(a,b),calculate_entropy(a),calculate_entropy(b),calculate_ssi(a,b)],
                              [1,np.sqrt(.5),0,1,1.5,np.sqrt(.5)],atol=1e-12)
    from scipy import stats,ndimage
    from scipy.spatial.distance import sqeuclidean
    reference=[ndimage.mean(a),ndimage.mean(b),stats.tstd(a.ravel(),ddof=0),
               stats.tstd(b.ravel(),ddof=0),abs(ndimage.mean(a)-ndimage.mean(b)),
               sqeuclidean(a.astype(float).ravel(),b.astype(float).ravel())/a.size,
               stats.entropy([8,8],base=2),stats.entropy([4,8,4],base=2),
               stats.variation(b.ravel())/stats.variation(a.ravel())]
    np.testing.assert_allclose(measured,reference,atol=1e-12)
    print('A:\n',a,'\nB:\n',b)
    print('meanA meanB rmsA rmsB AMBE MSE HA HB SSI:\n',measured,'\nPASS')

if __name__=='__main__':main()
