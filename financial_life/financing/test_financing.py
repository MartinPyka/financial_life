# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 21:40:47 2016

@author: martin
"""

import unittest
import financial_life.financing as financing
from financial_life.calendar_help import Bank_Date
from datetime import datetime

class Test_Create_Stop_Criteria(unittest.TestCase):

    def test_date(self):
        t = datetime(2016,10,15)
        foo = financing.create_stop_criteria(t)
        self.assertTrue(foo(datetime(2016,10,14)))
        self.assertFalse(foo(datetime(2016,10,16)))

    def test_callable(self):
        t = lambda x: x < datetime(2016,11,18)
        foo = financing.create_stop_criteria(t)
        self.assertFalse(foo(datetime(2016,10,14)))
        self.assertFalse(foo(datetime(2016,11,14)))
        self.assertTrue(foo(datetime(2016,11,19)))

class TestRegular_Month_Payment(unittest.TestCase):


    def setUp(self):
        self.regular =  {'from_acc': 'Dummy',
                         'to_acc': 'Dummy',
                         'interval': 'month',
                         'day' : 15,
                         'date_start': Bank_Date(2015, 3, 15),
                         'date_stop': Bank_Date(2015, 6, 15),
                         'payment': 3000,
                         'name' : 'Test',
                         'fixed': True,
                         'meta': {}
                         }
        self.infinite = {'from_acc': 'Dummy',
                         'to_acc': 'Dummy',
                         'interval': 'month',
                         'day' : 15,
                         'date_start': Bank_Date(2015, 3, 15),
                         'date_stop': Bank_Date.max,
                         'payment': 3000,
                         'name' : 'Test',
                         'fixed': True,
                         'meta': {}
                         }
        self.lastcal =  {'from_acc': 'Dummy',
                         'to_acc': 'Dummy',
                         'interval': 'month',
                         'day' : 31,
                         'date_start': Bank_Date(2015, 1, 31),
                         'date_stop': Bank_Date(2015, 6, 15),
                         'payment': 3000,
                         'name' : 'Test',
                         'fixed': True,
                         'meta': {}
                         }

    def test_begin_payment_next_month(self):
        iterator = financing.iter_regular_month(self.regular, date_start = datetime(2015,3, 16))
        payment = next(iterator)
        self.assertEqual(payment['date'], datetime(2015,4,15))

        iterator = financing.iter_regular_month(self.regular, date_start = datetime(2016,3, 16))
        self.assertRaises(StopIteration, next, iterator)

    def test_begin_payment_next_year(self):
        iterator = financing.iter_regular_month(self.infinite, date_start = datetime(2016,3, 16))
        payment = next(iterator)
        self.assertEqual(payment['date'], datetime(2016, 4, 15))

    def test_begin_payment_this_month(self):
        iterator = financing.iter_regular_month(self.regular, date_start = datetime(2015,3, 15))
        payment = next(iterator)
        self.assertEqual(payment['date'], datetime(2015,3,15))

    def test_proper_sequence(self):
        iterator = financing.iter_regular_month(self.regular, date_start = datetime(2015,3, 20))
        payment = next(iterator)
        self.assertEqual(payment['date'], datetime(2015,4,15))
        payment = next(iterator)
        self.assertEqual(payment['date'], datetime(2015,5,15))
        self.assertRaises(StopIteration, next, iterator)

    def test_last_calender_day(self):
        iterator = financing.iter_regular_month(self.lastcal, date_start = datetime(2015,2, 28))
        payment = next(iterator)
        self.assertEqual(payment['date'], datetime(2015,2,28))


class TestRegular_Year_Payment(unittest.TestCase):


    def setUp(self):
        self.regular =  {'from_acc': 'Dummy',
                         'to_acc': 'Dummy',
                         'interval': 'yearly',
                         'day' : 15,
                         'date_start': Bank_Date(2015, 3, 15),
                         'date_stop': Bank_Date(2018, 3, 14),
                         'payment': 3000,
                         'name' : 'Test',
                         'fixed': True,
                         'meta': {}
                         }
        self.infinite = {'from_acc': 'Dummy',
                         'to_acc': 'Dummy',
                         'interval': 'yearly',
                         'day' : 15,
                         'date_start': Bank_Date(2015, 3, 15),
                         'date_stop': Bank_Date.max,
                         'payment': 3000,
                         'name' : 'Test',
                         'fixed': True,
                         'meta': {}
                         }
        self.lastcal =  {'from_acc': 'Dummy',
                         'to_acc': 'Dummy',
                         'interval': 'yearly',
                         'day' : 31,
                         'date_start': Bank_Date(2015, 1, 31),
                         'date_stop': Bank_Date(2017, 6, 15),
                         'payment': 3000,
                         'name' : 'Test',
                         'fixed': True,
                         'meta': {}
                         }

    def test_begin_payment_same_year(self):
        iterator = financing.iter_regular_year(self.regular, date_start = datetime(2015,3, 15))
        payment = next(iterator)
        self.assertEqual(payment['date'], datetime(2015,3,15))


    def test_begin_payment_next_year(self):
        iterator = financing.iter_regular_year(self.infinite, date_start = datetime(2015,3, 16))
        payment = next(iterator)
        self.assertEqual(payment['date'], datetime(2016, 3, 15))

    def test_proper_sequence(self):
        iterator = financing.iter_regular_year(self.regular, date_start = datetime(2015,3, 20))
        payment = next(iterator)
        self.assertEqual(payment['date'], datetime(2016,3,15))
        payment = next(iterator)
        self.assertEqual(payment['date'], datetime(2017,3,15))
        self.assertRaises(StopIteration, next, iterator)

if __name__ == '__main__':
    unittest.main()
