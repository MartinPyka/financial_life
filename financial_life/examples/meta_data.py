'''
Created on 21.12.2016

@author: martin
'''
# standard libraries
from datetime import timedelta, datetime
import os

# third-party libraries
from matplotlib.pyplot import show

# own libraries
from financial_life.financing import accounts as a
from financial_life.reports import html

def example1():
    # create a private bank account and a loan
    account = a.Bank_Account(amount = 1000, interest = 0.001, name = 'Main account', date="01.09.2016")
    loan = a.Loan(amount = 100000, interest = 0.01, name = 'House Credit', date="01.09.2016")

    # add these accounts to the simulation
    simulation = a.Simulation(account, loan, date='01.09.2016')

    # describe single or regular payments between accounts. note, that
    # a string can be used for external accounts that you don't want to model.
    # also note the lambda function for the payments to the loan.
    simulation.add_regular('Income', account, 2000, interval = 'monthly', date_start="01.09.2016")
    # you can also use lambda function to dynamically decide how much money
    # you would like to transfer
    simulation.add_regular(account, loan, lambda: min(1500, -loan.account), interval = 'monthly', date_start="01.09.2016", meta={'tax': 500})

    # simulate for ten years
    simulation.simulate(delta = timedelta(days=365*10))

    # print reports summarized in years
    print(account.report.with_meta())
    #print(simulation.report.with_meta())
    return simulation

if __name__ == '__main__':
    example1()
