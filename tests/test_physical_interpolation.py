import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from sentinel_calibration_demo import bilinear_numpy
from fetch_scene_wind import wind_vector


class PhysicalInterpolationTests(unittest.TestCase):
    def test_nonuniform_grid_reproduces_bilinear_polynomial_at_edges_and_inside(self):
        y=np.array([0.,3.,10.]); x=np.array([0.,2.,9.])
        f=lambda yy,xx: 2+3*yy-4*xx+0.5*yy*xx
        grid=f(y[:,None],x[None,:])
        rows=np.array([0.,1.,3.,7.,10.]); cols=np.array([0.,1.,2.,5.,9.])
        np.testing.assert_allclose(bilinear_numpy(y,x,grid,rows,cols),
                                   f(rows[:,None],cols[None,:]),atol=1e-12,rtol=0)

    def test_out_of_grid_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'Extrapolation'):
            bilinear_numpy([0,1],[0,1],np.zeros((2,2)),[-1],[0])

    def test_meteorological_direction_and_north_wrap(self):
        np.testing.assert_allclose(wind_vector(5,0),[0,-5],atol=1e-12)
        np.testing.assert_allclose(wind_vector(5,90),[-5,0],atol=1e-12)
        mean=(wind_vector(5,350)+wind_vector(5,10))/2
        self.assertAlmostEqual(mean[0],0)
        self.assertAlmostEqual(mean[1],-5*np.cos(np.deg2rad(10)))


if __name__=='__main__': unittest.main()
