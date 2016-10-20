# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 21:27:23 2016

Collection of validation messages

@author: martin
"""
# standard libraries
from datetime import datetime, timedelta
from collections import Callable

# custom libraries

# own libraries
from financial_life.financing.accounts import Account, DummyAccount
from financial_life.financing import id_generator
from financial_life.calendar_help import Bank_Date



def valid_date(date):
    """ routine for makig a date out of anything that the user might
    have given to the function """
    if date is None:
        date = Bank_Date.today()
    if not isinstance(date, Bank_Date) and isinstance(date, datetime):
        date = Bank_Date.fromtimestamp(date.timestamp())
    if not isinstance(date, Bank_Date) and not isinstance(date, datetime) and not  isinstance(date, Callable):
        raise TypeError("Date must be at least from type datetime or callable")
    return date
    
def valid_name(name):
    if not name:
        name = id_generator(8)
    return name
    
def valid_date_stop(date_stop):
    """ checks, whether date_stop has a valid value """
    if not date_stop:
        date_stop = Bank_Date.max
    return date_stop
    
def valid_delta(delta):
    """ converts delta, if necessary, into a timedelta instance """
    if not delta:
        delta = timedelta.max
    if isinstance(delta, int):
        delta = timedelta(days = delta)
    assert isinstance(delta, timedelta), 'delta must be of type timedelta or int'
    assert delta.days > 0, 'delta must be positive'
    return delta

def valid_account_type(*accounts):
    """ Checks whether all accounts given to this function 
    are either from type Account or from type string 
    Accounts of type string are converted to DummyAccount
    The corrected list is returned """
    result = []
    for account in accounts:
        if (isinstance(account, Account)):
            result.append(account)
        elif (isinstance(account, str)):
            result.append(DummyAccount(account))
        else:
            raise TypeError('the given account must be either derived from type Account or of type string')        
    return tuple(result)