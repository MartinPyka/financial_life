'''
Created on 15.12.2016

@author: martin
'''
# standard libraries
from datetime import datetime
import unittest

# own libraries
from financial_life.financing import Status


class Test(unittest.TestCase):


    def test_InitStatus(self):
        # initialize without data field
        s = Status(datetime(2016,9,1), a=2, b=3, cata=4)
        self.assertDictEqual(s._status, {'a':2, 'b':3, 'cata':4})
        self.assertDictEqual(s._data, {})
        
        # initialize with data field
        s = Status(datetime(2016,9,1), a=2, b=3, data={'test': 3})
        self.assertDictEqual(s._status, {'a':2, 'b':3})
        self.assertDictEqual(s._data, {'test': 3})


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()