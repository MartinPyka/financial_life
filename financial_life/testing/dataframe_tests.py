'''
Created on 14.08.2016

@author: martin
'''
# standard libraries
from datetime import timedelta, datetime
import os

# third-party libraries

# own libraries
from financial_life.financing import accounts as a
from financial_life.reports import html

def dataframe_test():
    # create a private bank account and a loan 
    account = a.Bank_Account(amount = 1000, interest = 0.001, name = 'Main account')
    #loan = a.Loan(amount = 100000, interest = 0.01, name = 'House Credit')

    # add these accounts to the simulation
    simulation = a.Simulation(account)
    
    # describe single or regular payments between accounts. note, that
    # a string can be used for external accounts that you don't want to model.
    # also note the lambda function for the payments to the loan. 
    simulation.add_regular('Income', account, 2000, interval = 'monthly')
    # you can also use lambda function to dynamically decide how much money
    # you would like to transfer
    simulation.add_regular(account, 'loan', 1500, interval = 'monthly')
    
    # simulate for ten years
    simulation.simulate(delta = timedelta(days=10))
    # plot the data
    #simulation.plt_summary()
    
    # print reports summarized in years
    #print(account.report['interest'].dtype)
    print(account.report)
    #print(account.report.yearly())
    #print(loan.report)
    
    # analyze data
    #print("Interests on bank account: %.2f" % sum(account.report.yearly().interest))
    #print("Interests on loan account: %.2f" % sum(loan.report.yearly().interest))
    


if __name__ == '__main__':
    dataframe_test()