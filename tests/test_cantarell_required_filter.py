import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from select_cantarell_required_filter import choose


class RequiredFilterTests(unittest.TestCase):
    def row(self, fid, score, filter_name='lee', threshold='niblack', branch='gamma0'):
        return {'eligible':True,'branch':branch,'config_id':fid,'model_id':0,
                'config':{'filter':{'name':filter_name},'threshold':{'name':threshold}},
                'metrics':{'numpy':{'f1':score,'recall':.5}}}

    def test_requirement_constraints_do_not_silently_choose_unfiltered_winner(self):
        rows=[self.row(1,.9,'none'),self.row(2,.8,threshold='otsu'),
              self.row(3,.7,branch='sigma0'),self.row(4,.2),self.row(5,.1)]
        original=list(rows)
        self.assertEqual(choose(rows)['config_id'],4)
        self.assertEqual(rows,original)

    def test_tie_and_missing_compliant_candidate(self):
        self.assertEqual(choose([self.row(5,.2),self.row(4,.2)])['config_id'],4)
        with self.assertRaises(ValueError):
            choose([self.row(1,.9,'none')])


if __name__=='__main__':
    unittest.main()
