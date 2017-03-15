'''
Created on Mar 13, 2017

'''
import unittest
import sys
sys.path.append('..')
from geigerfs import GeigerFS


class GeigerFSTest(unittest.TestCase):
    
    def test_getattr_returns_attrs_dict_for_root(self):
        for key in ('st_atime', 'st_ctime',  
                 'st_mode', 'st_mtime', 'st_nlink'):
            self.assertIn(key, self.root_gfs.getattr('/', None).keys())
    
    
    def test_readdir_includes_random_cpm_curr_parent(self):
        for key in ('.', '..', 'random', 'cpm'):
            self.assertIn(key, self.root_gfs.readdir('/', None) )


    def setUp(self):
        self.root_gfs = GeigerFS()


    def tearDown(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()