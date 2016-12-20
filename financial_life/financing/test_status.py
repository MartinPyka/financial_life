'''
Created on 15.12.2016

@author: martin
'''
# standard libraries
from datetime import datetime, timedelta
import unittest

# own libraries
from financial_life.financing import accounts as a
from financial_life.financing import Status


class Test(unittest.TestCase):


    def setUp(self):
        """ Create setup for making sure that meta-data are
        transfered to the status of payments """
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
                               name = 'Savings',
                               meta = {'tax': 100})

        simulation.simulate(delta=timedelta(days=2000))
        self.simulation = simulation


    def test_InitStatus(self):
        # initialize without data field
        s = Status(datetime(2016,9,1), a=2, b=3, ceta=4)
        self.assertDictEqual(s._status, {'a':2, 'b':3, 'ceta':4})
        self.assertDictEqual(s._meta, {})

        # initialize with data field
        s = Status(datetime(2016,9,1), a=2, b=3, meta={'test': 3})
        self.assertDictEqual(s._status, {'a':2, 'b':3})
        self.assertDictEqual(s._meta, {'test': 3})

    def test_str(self):
        s = Status(datetime(2016,9,1), a=2, b=3, ceta=4)
        str(s)

    def test_SimulationReport(self):
        # the report of the simulation-class itself should be displayable
        status1 = self.simulation.report._statuses[0]
        status2 = self.simulation.report._statuses[1]
        self.assertDictEqual(status1._meta, {})
        print(status2._meta)
        self.assertDictEqual(status2._meta, {'tax': 100})


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
