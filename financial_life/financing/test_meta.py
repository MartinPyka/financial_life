'''
Created on 04.01.2017

@author: martin
'''
# standard libraries
from datetime import datetime, timedelta
import unittest

# own libraries
from financial_life.examples import meta_data

class Test(unittest.TestCase):


    def setUp(self):
        # run a simulation that makes use of meta-information
        self.s = meta_data.example_meta_controller(print_it=False)


    def tearDown(self):
        pass


    def test_account_and_simulation(self):
        """ Test that meta-information are in the account class and
        in the simulation class """
        accounts = self.s.accounts[0]
        s_income_report = self.s.report.subset(
            lambda st: st.meta.get('type','') == 'income')
        a_income_report = accounts.report.subset(
            lambda st: st.meta.get('type','') == 'income')
        
        s_interests = sum(s_income_report.value)
        a_interests = sum(a_income_report.input)
        
        self.assertTrue(len(s_income_report) == len(a_income_report), 
            'Reprots in Simulation and Account class with meta-information have not the same length')
        self.assertTrue(s_interests == a_interests, 
            'Values in the account and simulation class are not the same')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()