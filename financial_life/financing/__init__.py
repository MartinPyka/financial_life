""" some basic classes for creating financing classes and
reports """

# standard libraries
from datetime import datetime
from calendar import monthrange
import warnings
from copy import deepcopy
from collections import defaultdict
from collections import Callable

# third-party libraries
from tabulate import tabulate
import numpy as np
from numpy.core.numeric import result_type
import pandas as pd

# own libraries
from financial_life.calendar_help import Bank_Date
from financial_life.financing.identity import id_generator
from financial_life.financing import validate

pd.set_option('display.width', 1000)

# degrees of precision. the higher the number the more
# precise is the category
C_precisions = {'year' : 1.,
              'month': 2.,
              'day': 3.,
              }

C_default_payment = {'date': Bank_Date.max,
                     'payment': 0.,
                     'name': 'End reached'}

# semantic of reports. Columns of the report can be assigned
# to one or several of this categories. This allows to
# visualize collection of reports in a semantical meaningful manner
report_semantics = {'input_abs': [],    # money transfered to the financial product as absolute number
                    'input_cum': [],    # ...as increment
                    'output_abs': [],   # money transfered from the financial product
                    'output_cum': [],   # ...as decrement
                    'cost_abs': [],     # created costs by the f.p.
                    'cost_cum': [],     # ...as increment
                    'win_abs': [],      # created win by the f.p.
                    'win_cum': [],      # ...as increment
                    'debt_abs': [],     # debt value
                    'debt_cum': [],     # ...as increment
                    'debtpayment_abs': [], # payment to equalize debts
                    'debtpayment_cum': [], # ...as increment
                    'saving_abs': [],   # saving value
                    'saving_cum': [],   # ...as increment
                    'none': [],         # none of the above things
                    }


def conv_payment_func(x):
    """ converts any payment to what is needed in order to be applicable in
    the simulation process. if it is a number, it is multiplied by 100, if it
    is a function, the function is called and the result is multiplied by 100.
    """
    return Payment_Value(x)


def create_stop_criteria(date_stop):
    """ This is a function that returns a functions, which defines
    a stop criteria for the iterators. If date_stop is a date,
    the resulting functions simply compares date_stop with a given date.
    if date_stop is a callable, it executes the callable """
    if isinstance(date_stop, datetime) or isinstance(date_stop, Bank_Date):
        def compare_dates(cdate):
            return cdate < date_stop
        return compare_dates
    elif isinstance(date_stop, Callable):
        def check_callable(cdate):
            return not date_stop(cdate)
        return check_callable
    else:
        raise ValueError("date_stop is %s but should be either date-type or Callable" % type(date_stop))


def iter_regular_month(regular, date_start = None):
    """ creates an iterator for a regular payment. this function is for example
    used by payment to create iterators for every item in _regular
        regular: item of the structure Payments._regular
        date_start: date the payment generator wants to start the payments,
                    this can be a date after regular['date_start']
    """
    if not date_start:
        date_start = regular['date_start']
    else:
        # determine the greater date
        date_start = max(date_start, regular['date_start'])

    # if day is bigger than start_date.day, than this month is gonna
    # be the first payment
    if date_start.day <= regular['day']:
        i = 0
    # otherwise it will be in the next month
    else:
        i = 1

    date_start = Bank_Date(year = date_start.year,
                           month = date_start.month,
                           day = min(regular['day'], monthrange(date_start.year, date_start.month)[1]),
                           hour = date_start.hour,
                           minute = date_start.minute,
                           second = date_start.second)

    date_stop = regular.get('date_stop', Bank_Date.max)
    stop_criteria = create_stop_criteria(date_stop)

    current_date = date_start.add_month(i)

    while stop_criteria(current_date):
        yield Payment(from_acc = regular['from_acc'],
                      to_acc = regular['to_acc'],
                      date = current_date,
                      name = regular['name'],
                      kind = 'regular',
                      payment = regular['payment'],
                      fixed = regular['fixed'],
                      meta = regular['meta']
                      )
        i += 1
        current_date = date_start.add_month(i)

def iter_regular_year(regular, date_start = None):
    """ creates an iterator for a yearly payment. this function is
    used by payment to create iterators for every item in _regular
    It takes the day and month in regular['date_start'] to schedule the payment
        regular: item of the structure Payments._regular
        date_start: date the payment generator wants to start the payments,
                    this can be a date after regular['date_start']
    """

    if not date_start:
        date_start = regular['date_start']
    else:
        # determine the greater date
        date_start = max(date_start, regular['date_start'])

    current_date = datetime(year=date_start.year,
                            month=regular['date_start'].month,
                            day=regular['date_start'].day)

    if current_date < date_start:
        current_date = datetime(year=date_start.year + 1,
                                month=regular['date_start'].month,
                                day=regular['date_start'].day)

    date_stop = regular.get('date_stop', Bank_Date.max)
    stop_criteria = create_stop_criteria(date_stop)

    while stop_criteria(current_date):
        yield Payment(from_acc = regular['from_acc'],
                      to_acc = regular['to_acc'],
                      date = current_date,
                      name = regular['name'],
                      kind = 'regular',
                      payment = regular['payment'],
                      fixed = regular['fixed'],
                      meta = regular['meta']
                      )

        current_date = datetime(year = current_date.year + 1,
                                month=regular['date_start'].month,
                                day=regular['date_start'].day)


# functions for generating regular payments
C_interval = {
              'monthly': iter_regular_month,
              'yearly': iter_regular_year,
              }



class Status(object):
    """ This class represents the status of a financing product
    at a particular date """

    def __init__(self, date, **kwargs):
        """ Creates a new status object. Note, that all of kwargs
        elements are written to _status, except 'meta', which is
        treated special, as it may contain dict-data again """
        if not isinstance(date, datetime):
            raise TypeError("date must be from type datetime")

        self._date = date
        self._meta = {}

        if 'meta' in kwargs:
            self._meta = kwargs.pop('meta')

        self._status = kwargs
        self._format = "%d.%m.%Y"

    def __str__(self):
        result = "Date: %s" % self._date.strftime(self._format) + '\n'
        for key, value in self._status.items():
            result += ("%s: %s\n" % (key, str(value)))
        return result

    def keys(self):
        """ Returns a list of keys """
        return self._status.keys()

    @property
    def date(self):
        return self._date

    @property
    def strdate(self):
        return self._date.strftime(self._format)

    @property
    def status(self):
        return self._status

    @property
    def meta(self):
        return self._meta

    def __getitem__(self, key):
        if key == 'date':
            return self._date
        return self._status[key]

    def __getattr__(self, name):
        return self.__getitem__(name)
    
    def get(self, attr, default):
        """ Get attribute or default value from data-dictionary """
        if attr == 'date':
            return self._date
        return self._status.get(attr, default)

class Report(object):
    """ A report is a collection of statuses with some additional
    functionallity in order to merge and plot reports. One key
    feature of report is that it can handle heterogenous types of
    statuses
    """

    def __init__(self, name=None,
                 format_date = "%d.%m.%Y",
                 precision = 'daily'
                 ):
        self._statuses = []
        self._keys = []    # list of all keys used so far

        self._format_date = format_date
        # precision for merging statuses with similar date
        self._precision = precision
        self._semantics = deepcopy(report_semantics)

        if not name:
            name = id_generator(8)
        self._name = name

    def add_semantics(self, key, semantics=None):
        """ adds semantic description to the report, important for
        plotting

        usage:
            Single assignments
                .add_semantics('loan', 'debt_abs')

            Group assignments
                .add_semantics(['interest', 'insurence'], 'cost_cum')

            Entire assignments
                .add_semantics({'cost_cum':['interest', 'insurence']})
        """
        if isinstance(key, dict):
            for k, items in key.items():
                if k in self._semantics:
                    self._semantics[k] = items
                else:
                    raise AttributeError('Key %s not in semantics' % k)
            return

        if semantics not in self._semantics:
            raise AttributeError('Semantic "%s" not in semantics' % semantics)

        if isinstance(key, list):
            self._semantics[semantics] = self._semantics[semantics] + key
            self._keys = list(set(self._keys) | set(key))
            return

        if isinstance(key, str):
            self._semantics[semantics].append(key)
            self._keys = list(set(self._keys) | set((key,)))
            return

    def semantics(self, semantic):
        """ returns list of elements in semantic """
        return self._semantics[semantic]

    def semantics_of(self, key):
        """ returns the semantic in which the key appears """
        for semantic, values in self._semantics.items():
            if key in values:
                return semantic
        return ''

    def append(self, status = None, date = None, **kwargs):
        """ adds either an instance of status to the list or
        data given to the append method as keyword arguments """
        assert((status and not date) or (date and not status))

        if date:
            status = Status( Bank_Date.fromtimestamp(date.timestamp()), **kwargs )

        if not isinstance(status, Status):
            raise TypeError("status must be of type Status")

        self._statuses.append(status)
        # add potential new keys to the list
        self._keys = list(set(self._keys) | set(status.keys()))

    @property
    def size(self):
        """ Returns the number of status entries"""
        return len(self._statuses)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def precision(self):
        return self._precision

    def get_from_date(self, date, interval):
        """ help function to make the creation monthly, yearly reports more
        generic. This function returns e.g. month or year from a given date """
        if interval == 'yearly':
            return Bank_Date(date.year, 1, 1)
        if interval == 'monthly':
            return Bank_Date(date.year, date.month, 1)
        if interval == 'daily':
            return date
        raise TypeError("interval has to be either monthly or yearly")

    def monthly(self):
        return self.create_report(interval='monthly')

    def yearly(self):
        return self.create_report(interval='yearly')

    def create_report(self, interval='yearly'):
        """ generic function for returning a report for certain
        intervals """

        def add_data(data, status):
            """ add status data to existing dictionary """
            for key, value in status.status.items():
                # for cumulative data, we need to add, for other we just
                # need to take the latest value
                if "cum" in self.semantics_of(key):
                    data[key] += value
                elif not self.semantics_of(key) is "none":
                    data[key] = value
            return data

        if interval == 'daily':
            return self

        i = 0
        result = Report(name = self._name,
                        format_date = self._format_date,
                        precision = interval
                        )
        result._semantics = deepcopy(self._semantics)

        while (i < len(self._statuses)):
            # get the value of the interval type, e.g. exact month or exact year
            frame = self.get_from_date(self._statuses[i].date, interval)
            # create a new dictionary and add the current status to it
            data = add_data(defaultdict(int), self._statuses[i])
            i += 1
            # iterate to the following statuses as long as frame equals the current value of the
            # the given interval type (e.g. as long as the month is the same)
            while (i < len(self._statuses)) and (frame == self.get_from_date(self._statuses[i].date, interval)):
                data = add_data(data, self._statuses[i])
                i += 1

            # if the while loop ended because of i, we need to correct it again
            if (i == len(self._statuses)):
                result.append(date=self._statuses[i-1].date, **data)
            else:
                result.append(date=self._statuses[i-1].date, **data)

        return result
    
    def subset(self, lambda_func):
        """ creates a subset of report based on lambda-function that is 
        used within a list comprehension. The lambda function gets every
        status element of report and returns either true (to be inlcuded
        in subset) or false (excluded). This is a very generic way of
        applying queries to the report in order to reduce its the report
        to its requsted items.
        Note, that this is not a deepcopy of the report. Therefore, the 
        it is more appropriate to use it for reading data rather than
        writing data.
        """
        if not isinstance(lambda_func, Callable):
            raise TypeError('lambda_func must be of the form lambda status: True <or> False')
        result = Report(name = self._name,
                        format_date = self._format_date,
                        precision = 'custom'
                        )
        result._semantics = self._semantics
        result._keys = self._keys
        result._statuses = [s for s in self._statuses if lambda_func(s)]
        return result

    def table_rows(self):
        """ Creates a list of lists, where each inner list
        represents a row of a table. This is used by the tabulate
        package for plotting tables. """
        records = []
        for s in self._statuses:
            data = [s.date.strftime(self._format_date)] + [s.get(key, '') for key in self._keys]
            records.append(data)
        return records

    def with_meta(self):
        """ Returns the table with meta-information """
        print(self.name)
        records = []
        for s in self._statuses:
            data = [s.date.strftime(self._format_date)] + [s.get(key, '') for key in self._keys] + [str(s._meta)]
            records.append(data)
        return tabulate(records, headers=(['Date'] + self._keys + ['Meta']), floatfmt=".2f")

    def sum_of(self, semantic):
        """
        Returns the sum of a given semantic, e.g.
            .sum_of('cost')
        for all cost_cum and cost_abs items, or
            .sum_of('cost_cum')
        for cost_cum items only
        """
        result = 0
        for sem in self._semantics:
            if semantic in sem:
                # if this is a cumulative list, we need to calculate the sum
                if '_cum' in sem:
                    for key in self._semantics[sem]:
                        result += np.sum(self.get(key, num_only = True))
                # if abs, get only the last element
                if '_abs' in sem:
                    for key in self._semantics[sem]:
                        result += self.get(key, num_only = True)[-1]
        return result

    def __getitem__(self, key):
        result = Report(format_date = self._format_date,
                        precision = self._precision)
        for s in self._statuses:
            if key in s.keys():
                result.append(date = s['date'], **{key: s[key]})
        return result

    def __getattr__(self, name):
        result = [s.get(name, 'None') for s in self._statuses]
        return result
        if (name == 'date'):
            return result
        else:
            return np.array(result)
        
    def __len__(self):
        return len(self._statuses)        

    def get(self, name, num_only = False):
        replace = 0 if num_only else 'None'
        result = [s.get(name, replace) for s in self._statuses]
        return result
        if (name == 'date'):
            return result
        else:
            return np.array(result)

    def __str__(self):
        """ Prints all statuses in table view """
        print(self.name)
        records = self.table_rows()
        return tabulate(records, headers=(['Date'] + self._keys), floatfmt=".2f")
    
    def __iter__(self):
        """ Iteratores through all statuses """
        return self._statuses.__iter__()

    def as_df(self):
        """ Returns the report as pandas.DataFrame """
        dates, data = list(zip(*((s.date, s.status) for s in self._statuses)))
        return pd.DataFrame(list(data), index=dates)

class Payment_Value(object):
    """ This is a class that represents a payment value. If the payment
    is an integer or float it is returned right away, if it is a
    function it is evaluated during runtime. Furthermore, this class
    can return a clear statement, whether it is a payment or not
    to any reporting instance (e.g. html reports)
    """
    def __init__(self, payment):
        """ checks, whether x is a number or a function and
        prepares the reporting variable """
        self._name = "could not be determined"
        self._payment = payment
        if isinstance(payment, int) or isinstance(payment, float):
            self._name = str('%0.2f' % payment)
        if isinstance(payment, Callable):
            self._name = "dynamic"

    @property
    def name(self):
        return self._name

    def __call__(self):
        if isinstance(self._payment, int) or isinstance(self._payment, float):
            return int(self._payment * 100)
        if isinstance(self._payment, Callable):
            return int(self._payment() * 100)

class Payment(object):
    """ Class that describes one specific payment between two accounts
    accounts can here be of type "Account" or str, which is an
    abstract account that always complies """

    def __init__(self, from_acc, to_acc, date, name,
                 kind, payment, fixed=True, meta={}):
        """ Initialization of Payment
        from_acc:      sending account
        to_acc:        receiving account
        date:          due date
        name:          Name of the payment
        payment:       Amount of the payment (money value)
        fixed:         Whether the receiving side needs to take the entire money
                       or can accept less (useful for loans)
        """
        self._data = {
                     'from_acc': from_acc,
                     'to_acc': to_acc,
                     'date': date,
                     'name': name,
                     'kind': kind,
                     'payment': payment,
                     'fixed': fixed,
                     'meta': meta
                     }

    @property
    def from_acc(self):
        return self._data['from_acc']

    @property
    def to_acc(self):
        return self._data['to_acc']

    @property
    def date(self):
        return self._data['date']

    @property
    def name(self):
        return self._data['name']

    @property
    def kind(self):
        return self._data['kind']

    @property
    def payment(self):
        return self._data['payment']

    @property
    def json(self):
        return {'from_acc': self._data['from_acc'].name,
                'to_acc': self._data['to_acc'].name,
                'date': self._data['date'].date(),
                'name': self._data['name'],
                'kind': self._data['kind'],
                'payment': self._data['payment'].name,
                'fixed': self._data['fixed'],
                'meta': self._data['meta'],
                }

    def __getitem__(self, key):
        return self._data[key]


class PaymentList(object):
    """ Hanldes the complexities of payments including unique
    payments and regular payments """

    def __init__(self):
        self._uniques = []
        self._regular = []

    @property
    def uniques(self):
        return self._uniques

    @property
    def regular(self):
        return self._regular

    def check_errors_payment(self, payment):
        """ checks for any errors in the payment variable """
        if (not isinstance(payment, int) and
            not isinstance(payment, float) and
            not isinstance(payment, Callable)):
            raise TypeError("Payment must be int, float or a function")

    def add_unique(self, from_acc, to_acc, payment,
                   date, name = '', fixed = True, meta={}):
        """ adds a one-time payment to the list, optional give it
        a name """
        if not isinstance(date, datetime):
            raise TypeError("Date must be at least from type datetime")

        self.check_errors_payment(payment)

        # converts any input to a function that returns the right value
        conv_payment = conv_payment_func(payment)

        self._uniques.append(
                             Payment(
                                     from_acc = from_acc,
                                     to_acc = to_acc,
                                     date = Bank_Date.fromtimestamp(date.timestamp()),
                                     name = name,
                                     kind = 'unique',
                                     payment = conv_payment,
                                     fixed = fixed,
                                     meta = meta
                                     )
                             )

        # sort the whole list with date as key
        self._uniques = sorted(self._uniques, key = lambda p: p['date'] )

    def add_regular(self, from_acc, to_acc, payment, interval,
                    date_start, day=1, name='', date_stop = None,
                    fixed = False, meta={}):
        """ Adds a regular payment to the list, with a given
        payment: amount to pay
        interval: 'monthly': every month
                  'quarter': every quarter with date_start as start month
                  'quarter_year': every quarter of a year (mar, jun, sep, dec)
                  'yearly': every year
        day: day to start with
        date_start: start date of this payment
        name : optional name
        fixed: only everything or nothing must be transfered (true)
               or depending on the receiving account a smaller amount
               can be transfered (false)
        """
        if not interval in C_interval.keys():
            raise ValueError("interval must be one of '" + '\',\''.join(C_interval))
        if day >= 29:
            warnings.warn(("note that in months which have less days than {} the " +
                           "payment will be transferred earlier").format(day)
                          )
        self.check_errors_payment(payment)

        if not date_stop:
            date_stop = Bank_Date.max
        else:
            date_stop = validate.valid_stop_date(date_stop)

        # converts any payment to a function
        conv_payment = conv_payment_func(payment)

        self._regular.append({'from_acc': from_acc,
                              'to_acc': to_acc,
                              'interval': interval,
                              'day' : day,
                              'date_start': Bank_Date.fromtimestamp(date_start.timestamp()),
                              'date_stop': date_stop,
                              'payment': conv_payment,
                              'name' : name,
                              'fixed': fixed,
                              'meta': meta
                              }
                             )

    def clear_regular(self):
        """ Removes all regular payments """
        self._regular = []

    def payment(self, start_date):
        """ returns an interator that iterates through all
        payments """

        assert isinstance(start_date, datetime), "start_date must be of type datetime"
        # creates for each item an iterator that returns just this
        # item. this list is later on amended by iterators for regular
        # payments
        iters = [iter([u]) for u in self._uniques if u['date']>= start_date]
        for r in self._regular:
            # creates an iterator based on the interval in r
            iters.append(C_interval[r['interval']](r, start_date))

        # list of next dates. this list is inline with the iters list
        # the second parameter in next prevents the command to raise a
        # StopIteration Exception
        dates = [next(iter, C_default_payment) for iter in iters]

        # as long as there is still a date, below infinity
        min_date = min(dates, key = lambda d: d['date'])

        # in this routine, the next command must be called after yield, as there might
        # be some callables which need to be called right after the payments, but not
        # before
        while min_date['date'] != Bank_Date.max:
            # find all indices and payments in the list that have the same daet
            indices, payments = zip(*[(i, d) for (i, d) in enumerate(dates) if (d['date'].date() == min_date['date'].date())])
            yield payments
            for i in indices:
                dates[i] = next(iters[i], C_default_payment)
            min_date = min(dates, key = lambda d: d['date'])

class Currency():
    """ Standard class for currencies to assure correct computing
    of numbers. Right now this class is not in use """
    def __init__(self, value, digits = 2):
        self._value = int(value * (10**digits))
