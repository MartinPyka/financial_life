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
from financial_life.financing.identity import id_generator
from financial_life.calendar_help import Bank_Date


date_formats = [
                '%d.%m.%Y',
                '%d.%m.%y',
                '%m/%d/%Y',
                '%m/%d/%y',
                ]

def parse_datestring(datestr):
    """ Tries to parse the datestring against a few common formats """
    for format in date_formats:
        try:
            date = datetime.strptime(datestr, format)
            return date
        except ValueError:
            pass

def valid_date(date):
    """ routine for making a date out of anything that the user might
    have given to the function """
    if date is None:
        return Bank_Date.today()
    if isinstance(date, Bank_Date):
        return date
    if isinstance(date, datetime):
        return Bank_Date.fromtimestamp(date.timestamp())
    if isinstance(date, str):
        return parse_datestring(date)
    raise TypeError("Date must be at least from type datetime or callable")

def valid_stop_date(date):
    """ routine for makig a date out of anything that the user might
    have given to the function """
    if isinstance(date, Callable):
        return date
    else:
        return valid_date(date)
    raise TypeError("Date must be at least from type datetime or callable")

    
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
