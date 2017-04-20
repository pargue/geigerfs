'''
Created on Mar 13, 2017

'''
import unittest
import sys
# from mock import mock_open
sys.path.append('..')
import logging
from geigerfs import GeigerFS
import time
import os

class GeigerFSTest(unittest.TestCase):

    def test_getattr_returns_attrs_dict_for_root(self):
        with open('test.txt', 'w') as tfh:
            tfh.write('')
        for key in ('st_atime', 'st_ctime',  
                 'st_mode', 'st_mtime', 'st_nlink'):
            self.assertIn(key, self.root_gfs.getattr('/', None).keys())
        os.remove('test.txt')


    def test_readdir_includes_random_cpm_curr_parent(self):
        for key in ('.', '..', 'random', 'cpm'):
            self.assertIn(key, self.root_gfs.readdir('/', None) )


    def test_cpm_handles_empty_times_file(self):
        with open('test.txt', 'w') as tfh:
            tfh.write('')

        fh = self.root_gfs.open("/cpm", 0)
        cpm = self.root_gfs.read("/cpm", 256, 0, fh)
        self.assertEqual(cpm, '0\n')
        os.remove('test.txt')


    def test_cpm_returns_1_with_120s_interval(self):
#         mocked_open_function = mock.mock_open(read_data=my_text)
#         with mock.patch("__builtin__.open", mocked_open_function):
#             with open("any_string") as f:
#                 print f.read()
#         open_name = '%s.open' % __name__
#         with patch(open_name, create=True) as mock_open:
#             mock_open.return_value = MagicMock(spec=file)
#
#             with open('test.txt', 'w') as f:
#                 f.readline()
#
        self.make_test_file(120)
        fh = self.root_gfs.open("/cpm", 0)
        cpm = self.root_gfs.read("/cpm", 256, 0, fh)
        self.assertEqual(cpm, '1\n')
        os.remove('test.txt')


    def test_cpm_returns_1_with_60s_interval(self):
        self.make_test_file(60)
        fh = self.root_gfs.open("/cpm", 0)
        cpm = self.root_gfs.read("/cpm", 256, 0, fh)
        self.assertEqual(cpm, '1\n')
        os.remove('test.txt')


    def test_cpm_returns_2_with_30s_intervals(self):
        self.make_test_file(30)
        fh = self.root_gfs.open("/cpm", 0)
        cpm = self.root_gfs.read("/cpm", 256, 0, fh)
        self.assertEqual(cpm, '2\n')
        os.remove('test.txt')


    def test_cpm_returns_60_with_big_file(self):
        self.make_big_test_file(1024)
        fh = self.root_gfs.open("/cpm", 0)
        cpm = self.root_gfs.read("/cpm", 256, 0, fh)
        self.assertEqual(cpm, '60\n')
        os.remove('test.txt')


    def test_pseudoread_new_seed(self):
        self.make_test_pseudo_file()
        self.root_gfs.doPseudoRead("/random", 10, 0)
        f = open('pseudo.txt')
        seed = f.readline()
        self.assertEqual(len(seed), 4)
        f.close()
        os.remove('pseudo.txt')


    def test_pseudoread_bytes_returned(self):
        self.make_test_pseudo_file()
        self.root_gfs.doPseudoRead("/random", 10, 0)
        self.assertEqual(len(self.root_gfs.data["/random"]), 20)
        os.remove ('pseudo.txt')


    def test_random_read(self):
        self.make_random_read_file(400)
        fh = self.root_gfs.open("/random", 0)
        test_val = []
        for i in range(1, 10):
            byte = self.root_gfs.doReadRandom("/random", i, 0, fh)
            self.assertEqual(len(byte), i)
            arr = list(byte)
            test_val.append('\0')
            self.assertEqual(test_val,arr)
        os.remove('test.txt')

    @unittest.skip("not working yet")
    def test_random_read_calls_pseudo(self):
        self.make_random_read_file(33)
        self.make_test_pseudo_file()
        fh = self.root_gfs.open("/random", 0)
        test_val = []
        for i in range(1, 10):
            byte = self.root_gfs.doReadRandom("/random", i, 0, fh)
            self.assertEqual(len(byte), i)
            arr = list(byte)
            test_val.append('\0')
            self.assertEqual(test_val,arr)
        os.remove('test.txt')
        os.remove ('pseudo.txt')


    def setUp(self):
        self.root_gfs = GeigerFS('test.txt', 'pseudo.txt')


    def tearDown(self):
        pass


    def make_test_pseudo_file(self):
        my_text = '1234'   # add 4 bytes
        f = open('pseudo.txt', 'w')
        f.write(my_text)
        f.close()


    def make_test_file(self, interval):
        t = time.time()
        my_text = str(t) + '\n'
        for i in range(60/interval):
            t += interval
            my_text += str(t) + '\n'
        f = open('test.txt', 'w')
        f.write(my_text)
        f.close()


    def make_big_test_file(self, int_count):
        t = time.time()
        my_text = str(t) + '\n'
        for i in range(int_count):
            my_text += str(t + i) + '\n'
        f = open('test.txt', 'w')
        f.write(my_text)
        f.close()


    def make_random_read_file(self, interval): #intervals would be in ascending order
        t = time.time()
        my_text = str(t) + '\n'
        val = 1
        for i in range(interval):
            t += val
            my_text += str(t) + '\n'
            val += 1
        f = open('test.txt', 'w')
        f.write(my_text)
        f.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
