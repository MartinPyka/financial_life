'''
Created on 12.12.2016

@author: martin
'''
# standard libraries
from datetime import timedelta, datetime
import os
import unittest

# own libraries
from financial_life.financing import accounts as a
from financial_life.reports import html


class Test(unittest.TestCase):


    def setUp(self):
        """ Mostly taken from examples/simple_example.py """
        account = a.Bank_Account(amount = 1000, interest = 0.001, name = 'Main account', date=datetime(2016,9, 1))
        savings = a.Bank_Account(amount = 5000, interest = 0.013, name = 'Savings', date=datetime(2016,9, 1))
        loan = a.Loan(amount = 100000, interest = 0.01, name = 'House Credit', date=datetime(2016,9, 1))
    
        simulation = a.Simulation(account, savings, loan, name = 'Testsimulation', date=datetime(2016,9, 1))
        simulation.add_regular(from_acc = 'Income',
                               to_acc = account,
                               payment = 2000,
                               interval = 'monthly',
                               date_start = datetime(2016,9,15),
                               day = 15,
                               name = 'Income')
    
        simulation.add_regular(from_acc = account,
                               to_acc = savings,
                               payment = 500,
                               interval = 'monthly',
                               date_start = datetime(2016,9,30),
                               day = 30,
                               name = 'Savings')
    
        simulation.add_regular(from_acc = account,
                               to_acc= loan,
                               payment = 1000,
                               interval = 'monthly',
                               date_start = datetime(2016,9,15),
                               day = 15,
                               name = 'Debts',
                               fixed = False,
                               date_stop = lambda cdate: loan.is_finished())
    
        simulation.add_regular(from_acc = account,
                               to_acc= loan,
                               payment = lambda : min(8000, max(0,account.get_account()-4000)),
                               interval = 'yearly',
                               date_start = datetime(2016,11,20),
                               day = 20,
                               name = 'Debts',
                               fixed = False,
                               date_stop = lambda cdate: loan.is_finished())
    
        simulation.simulate(delta=timedelta(days=2000))
    
        self.simulation = simulation
        self.account = account
        self.loan = loan


    def tearDown(self):
        pass


    def testGeneral(self):
        interests = sum(self.account.report.yearly().interest)+sum(self.loan.report.yearly().interest)
        self.assertTrue(abs(interests - (-3086.08)) < 0.00001)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()