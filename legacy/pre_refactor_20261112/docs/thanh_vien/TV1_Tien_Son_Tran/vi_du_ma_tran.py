"""TV1: teaching example for threshold -> mask -> area -> display integration."""
import numpy as np

def threshold_and_overlay(image, threshold):
    mask=(image.astype(float)<=threshold)
    rgb=np.repeat(image[...,None],3,axis=2).copy()
    rgb[mask]=[255,0,0]  # Illustrate a filled mask, not production boundary overlay.
    return mask.astype(np.uint8)*255, int(mask.sum()), float(mask.mean()*100), rgb

def main():
    a=np.array([[10,10,100,100],[10,10,100,100],
                [100,100,100,100],[100,100,100,100]],dtype=np.uint8)
    expected=np.array([[255,255,0,0],[255,255,0,0],[0,0,0,0],[0,0,0,0]],dtype=np.uint8)
    mask,area,percent,rgb=threshold_and_overlay(a,50)
    np.testing.assert_array_equal(mask,expected)
    import cv2  # Reference only; core above remains NumPy.
    _,reference=cv2.threshold(a,50,255,cv2.THRESH_BINARY_INV)
    np.testing.assert_array_equal(mask,reference)
    assert area==4 and percent==25
    np.testing.assert_array_equal(rgb[0,0],[255,0,0])
    np.testing.assert_array_equal(rgb[3,3],[100,100,100])
    print('Input:\n',a,'\nMask:\n',mask)
    print('Area =',area,'pixels; area_pct =',percent,'; PASS')

if __name__=='__main__':main()
