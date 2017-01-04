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
from matplotlib.pyplot import show

def dependencies():
    loan = a.Loan(200000, 0.0185, name = 'Credit' )
    
    # the class property defines a dependency on loan. When loan
    # decreases, the house-property increases
    house = a.Property(200000, 0, loan, name='House')

    simulation = a.Simulation(loan, house)

    simulation.add_regular('Income', loan, 1000, interval = 'monthly')

    simulation.simulate(delta = timedelta(days=365*20))
    simulation.plt_summary()
    show(block=True)

if __name__ == '__main__':
    dependencies()
