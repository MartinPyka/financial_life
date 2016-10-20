'''
Created on 14.08.2016

@author: martin
'''
# standard libraries
import logging
from datetime import datetime

# third-party libraries

# own libraries
from financial-life.financing import accounts as a
from financial-life.reports import html as h



def example1():
    account = a.Bank_Account(amount = 1000, interest = 0.001, name = 'Main account')
    loan = a.Loan(amount = 100000, interest = 0.01, name = 'House Credit')

    simulation = a.Simulation(account, loan, name = 'Testsimulation')
    simulation.add_regular(from_acc = 'Income', 
                           to_acc = account, 
                           payment = 2000, 
                           interval = 'monthly', 
                           date_start = datetime(2016,9,15), 
                           day = 15, 
                           name = 'Income')
    
    simulation.add_regular(from_acc = account, 
                           to_acc= loan, 
                           payment = 1500, 
                           interval = 'monthly', 
                           date_start = datetime(2016,9,15), 
                           day = 15, 
                           name = 'Debts',
                           fixed = False,
                           date_stop = lambda cdate: loan.is_finished())
    
    simulation.simulate(date_stop = datetime(2030,2, 17))
    
    simulation.plt_summary()
    #print(simulation.report)
    print(account.report.yearly())
    print(loan.report.yearly())
    #print(account.get_account())

def example2():
    account = a.Bank_Account(amount = 1000, interest = 0.001, name = 'Main account')
    savings = a.Bank_Account(amount = 5000, interest = 0.013, name = 'Savings')
    loan = a.Loan(amount = 100000, interest = 0.01, name = 'House Credit')

    simulation = a.Simulation(account, savings, loan, name = 'Testsimulation')
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
    
    simulation.simulate(date_stop = datetime(2018,2, 17))
    
    simulation.plt_summary()
    #print(simulation.report)
    print(account.report)
    print(loan.report)
    #print(savings.report.yearly())
    #print(account.get_account())
    
def html_export():
    h.report(1)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    #example2()
    html_export()