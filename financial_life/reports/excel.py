'''
Created on 29.05.2017

@author: martin
'''
# standard libraries
import os

# third-party libraries
import pandas as pd

# own libraries
from financial_life.reports import sl

def report(simulation, filename='report.xls'):
    """ This function generates a report as an excel sheet.
    
    simulation      the simualation that should be exported to excel
    filename        filename of the excel file
    """
    
    writer = pd.ExcelWriter(filename)
    for account in simulation.accounts:
        df = account.report.as_df()
        df.to_excel(writer, sheet_name=account.name)
    writer.save()