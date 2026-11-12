"""TV4: Sobel on valid interior and morphology on a 5x5 matrix."""
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.edges import custom_sobel
from src.morphology import custom_erosion,custom_morphological_boundary

def sobel_valid(a):
    kx=np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
    gx=np.empty((3,3));gy=np.empty((3,3))
    for y in range(3):
        for x in range(3):
            patch=a[y:y+3,x:x+3].astype(float)
            gx[y,x]=(patch*kx).sum();gy[y,x]=(patch*kx.T).sum()
    return gx,gy

def erode3(a):
    p=np.pad(a>0,1,constant_values=True)
    return np.array([[255 if p[y:y+3,x:x+3].all() else 0
                      for x in range(5)] for y in range(5)],np.uint8)

def main():
    a=np.array([[0,0,100,100,100]]*5,np.uint8)
    gx,gy=sobel_valid(a)
    expected=np.array([[400,400,0]]*3,float)
    np.testing.assert_array_equal(gx,expected);np.testing.assert_array_equal(gy,np.zeros((3,3)))
    px,py,_,_=custom_sobel(a)
    np.testing.assert_array_equal(px[1:-1,1:-1],gx);np.testing.assert_array_equal(py[1:-1,1:-1],gy)
    b=np.zeros((5,5),np.uint8);b[1:4,1:4]=255
    expected_erode=np.zeros((5,5),np.uint8);expected_erode[2,2]=255
    eroded=erode3(b);boundary=b-eroded
    np.testing.assert_array_equal(eroded,expected_erode)
    np.testing.assert_array_equal(eroded,custom_erosion(b,np.ones((3,3),np.uint8)))
    np.testing.assert_array_equal(boundary,custom_morphological_boundary(b))
    assert np.count_nonzero(boundary)==8
    import cv2  # Independent library reference with matching kernel and padding.
    np.testing.assert_array_equal(gx,cv2.Sobel(a,cv2.CV_64F,1,0,ksize=3)[1:-1,1:-1])
    np.testing.assert_array_equal(gy,cv2.Sobel(a,cv2.CV_64F,0,1,ksize=3)[1:-1,1:-1])
    ref_erode=cv2.erode(b,np.ones((3,3),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=255)
    np.testing.assert_array_equal(eroded,ref_erode)
    np.testing.assert_array_equal(boundary,b-ref_erode)
    print('Sobel input:\n',a,'\nGx interior:\n',gx,'\nGy interior:\n',gy)
    print('Mask:\n',b,'\nEroded:\n',eroded,'\nBoundary:\n',boundary,'\nPASS')

if __name__=='__main__':main()
