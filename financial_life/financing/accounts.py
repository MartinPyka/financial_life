'''
Created on 24.03.2016

@author: martin
'''

# standard libraries
from datetime import datetime, timedelta
from collections import Callable
import warnings
import logging

# third-party libraries

# own libraries
from financial_life.financing import PaymentList
from financial_life.financing import Report
from financial_life.financing import C_default_payment
from financial_life.calendar_help import Bank_Date, get_days_per_year
from financial_life.financing import plotting as plt
from financial_life.financing import validate

logger = logging.getLogger(__name__)


# maximal time span that will be simulated
C_max_time = 365 * 100
# format for dates
C_format_date = '%d.%m.%Y'

# generic transfer codes
C_transfer_OK = 0           # transfer confirmed
C_transfer_NA = 1           # transfer not allowed
C_transfer_NEM = 2          # not enough money on the account
C_transfer_ERR = 3          # general transfer error
C_transfer_codes = {C_transfer_OK: 'OK',
                    C_transfer_NA: 'Not allowed',
                    C_transfer_NEM: 'Not enough money',
                    C_transfer_ERR: 'ERROR'}

def neg_func(func):
    """ negates the outcome of func. this function is used as a wrapper
    to negate the output of payments which are determined at runtime. This
    wrapper is used e.g. by the class Transfers
    """
    def foo():
        result = func()
        return -result
    return foo

def valid_account_type(*accounts):
    """ Checks whether all accounts given to this function
    are either from type Account or from type string
    Accounts of type string are converted to DummyAccount
    The corrected list is returned

    The only reason this method is not in the validate module
    is because it would create an import loop
    """
    result = []
    for account in accounts:
        if (isinstance(account, Account)):
            result.append(account)
        elif (isinstance(account, str)):
            result.append(DummyAccount(account))
        else:
            raise TypeError('the given account must be either derived from type Account or of type string')
    return tuple(result)




class TransferMessage(object):
    """ Message returned by a transfer function with some information about
    the success or failure of the money transfer """
    def __init__(self, code, money, message = ''):
        if code in C_transfer_codes:
            self._code = code
        else:
            raise ValueError("Transfercode is not in C_transfer_codes")

        self._message = message
        self._money = money

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    @property
    def money(self):
        return self._money


class Simulation(object):
    """ This class simulates the interaction between different accounts. It
    provides the framework in which dependencies between accounts and state-
    dependent changes of account-modi can be managed """

    def __init__(self, *accounts, name = None, date = None, meta = None):
        """ Simulations can be initialized with names, to make differentiate
        between different simulations """
        # check for errors in the input of accounts
        for account in accounts:
            if not isinstance(account, Account):
                raise TypeError(str(account) + " is not of type or subtype Account")

        if name is None:
            self._name = 'Simulation ' + str(datetime.now())
        else:
            self._name = name
            
        # a simuation can also store meta information 
        self._meta = meta

        self._report = Report(self._name)
        self._report.add_semantics('from_acc', 'none')
        self._report.add_semantics('to_acc', 'none')
        self._report.add_semantics('value', 'input_cum')
        self._report.add_semantics('kind', 'none')
        self._report.add_semantics('name', 'none')
        self._report.add_semantics('code', 'none')
        self._report.add_semantics('message', 'none')

        self._payments = PaymentList()
        self._payments_iter = None
        self._next_pay = None

        self._date_start = validate.valid_date(date)
        self._day = 0
        self._current_date = self._date_start

        # list of accounts to manage
        self._accounts = list(accounts)

        # list of controller-functions executed before day-simulation.
        # controller functions are executed before the day to check custom
        # states of the accounts and perform actions
        self._controller = []


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        
    @property
    def meta(self):
        return self._meta

    @property
    def accounts(self):
        return self._accounts
    
    @property
    def current_date(self):
        return self._current_date

    @property
    def report(self):
        return self._report

    def as_df(self):
        df = self.report.as_df()
        df = df[['from_acc', 'to_acc', 'value', 'kind', 'name', ]]
        return df

    def get_report_jinja(self, interval="yearly"):
        """ creates a data-structure of the report data that can be used for
        displaying the report as table in html files (in jinja2 templates)
        interval can be one of the common intervals of the report class (e.g.
        yearly or monthly) or None. In this case the raw data are exported """
        if interval is None:
            report = self._report
        else:
            report = self._report.create_report(interval)

        header = ['date', 'from', 'to', 'value', 'kind', 'name', 'code', 'message']
        rows = []
        for status in report._statuses:
            item = [status.strdate,
                    status._data['from_acc'].name,
                    status._data['to_acc'].name,
                    '%.02f EUR' % status._data['value'],
                    status._data['kind'],
                    status._data['name'],
                    status._data['code'],
                    status._data['message'],
                    ]
            rows.append(item)
        return {'header': header, 'rows': rows}

    def get_payments_unique_json(self):
        """ returns a list of all unique payments in json format for
        html rendering """
        return {'payments_unique': [u.json for u in self._payments.uniques]}

    def get_payments_regular_json(self):
        """ returns a list of all unique payments in json format for
        html rendering """
        return {'payments_regular': [
                                     {
                                      'from_acc': r['from_acc'].name,
                                      'to_acc': r['to_acc'].name,
                                      'interval': r['interval'],
                                      'day': r['day'],
                                      'date_start': r['date_start'].date(),
                                      'date_stop': r['date_stop'].date() if isinstance(r['date_stop'], datetime) else '',
                                      'payment': r['payment'].name,
                                      'name': r['name'],
                                      'fixed': r['fixed'],
                                      } for r in self._payments.regular]
                }

    def get_accounts_json(self):
        return {'accounts': [
                             {
                              'index': i,
                              'name': a.name,
                              'type': a.__class__.__name__,
                              'start_value': a._account / 100.,
                              'start_date': a.date_start.date()
                              }
                             for i, a in enumerate(self.accounts)]
                }

    def add_unique(self, from_acc, to_acc, payment,
                   date, name = '',
                   fixed = False,
                   meta = {}
                   ):
        """ Transfers money from one account to the other """
        from_acc, to_acc = valid_account_type(from_acc, to_acc)
        date = validate.valid_date(date)
        self._payments.add_unique(
            from_acc, to_acc, payment, date, name, fixed, meta)
        self.update_payment_iterators()

    def add_regular(self, from_acc, to_acc, payment, interval,
                    date_start=datetime(1971,1,1),
                    day=1, name = '',
                    date_stop = None,
                    fixed = False,
                    meta = {}
                    ):
        """ Transfers money from one account to the other on regular basis
        date_stop can be a function of the form lambda x: x > datetime(...)
        If it returns true, the payment is stopped
        """
        from_acc, to_acc = valid_account_type(from_acc, to_acc)
        date_start = validate.valid_date(date_start)
        if date_stop is not None:
            date_stop = validate.valid_stop_date(date_stop)
        self._payments.add_regular(
            from_acc, to_acc, payment, interval,
            date_start, day, name, date_stop, fixed, meta)
        self.update_payment_iterators()
        
    def update_payment_iterators(self):
        """ Whenever a new payment is added via add_unique or add_regular,
        this function is triggered to update the payment iterator. This is 
        necessary, as payments could be dynamically added during the 
        simulation as well """
        self._payments_iter = self._payments.payment(self._current_date)

        try:
            self._next_pay = next(self._payments_iter, C_default_payment)
        except StopIteration:
            # if there are no payments, create a date for a payment
            # that lies in the distant future
            self._next_pay = [{'date': Bank_Date.max}]

    def add_account(self, account):
        """ adds an account to the simulation and returns it to the
        user so that he/she can proceed with it """
        if isinstance(account, Account):
            self._accounts.append(account)
        else:
            raise TypeError(("account must be of type Account but is of type " +
                            str(type(account))))
        return account

    def add_controller(self, controller):
        if isinstance(controller, Callable):
            self._controller.append(controller)
        else:
            raise TypeError(("controller must be of type Callable but is of type " +
                            str(type(controller))))

    def get_payment(self, payment):
        """ functions that returns the amount of payment for the current day.
        it handles the distinction between variables that represent just numbers
        and variables that represent functions to be executed """
        payed = 0
        if isinstance(payment['payment'], int) or isinstance(payment['payment'], float):
            payed = payment['payment']
        elif isinstance(payment['payment'], Callable):
            payed = payment['payment']()
        else:
            raise TypeError("payment must be int, float or Callable but is " + str(type(payment['payment'])))
        return payed

    def make_report(self, from_acc, to_acc, value, kind,
                    name, code, message, meta):
        self._report.append(
                            date = self._current_date,
                            from_acc = from_acc,
                            to_acc = to_acc,
                            value = value / 100,
                            kind = kind,
                            name = name,
                            code = code,
                            message = message,
                            meta = meta
                            )

    def make_transfer(self, payment):
        """ Transfers money from one account to the other and tries to assure
        full consistency.

        The idea is that a payments gets started by the sender. If this succeeds,
        the money is tried to move on the account of the receiver. If this fails,
        the money is transfered back to the sender.

        If the money to be transfered is zero, no payment procedure will be
        initiated
        """
        if not (isinstance(payment['from_acc'], DummyAccount)):
            assert payment['from_acc']._date_start <= self._current_date, (str(payment['from_acc']) + ' has a later creation date than the payment ' + payment['name'])
        if not (isinstance(payment['to_acc'], DummyAccount)):
            assert payment['to_acc']._date_start <= self._current_date, (str(payment['to_acc']) + ' has a later creation date than the payment ' + payment['name'])
        try:
            # this is now the money that will be transfered, if there is
            # a receiver. this amount of money remains fixed for the transfer
            money = self.get_payment(payment)
            if money == 0:
                self.make_report(
                                from_acc = payment['from_acc'],
                                to_acc = payment['to_acc'],
                                value = 0,
                                kind = payment['kind'],
                                name = payment['name'],
                                code = C_transfer_NA,
                                message = "Transfer with zero money will not be initiated",
                                meta = payment['meta']
                                )
                return False
        except TypeError as e:
            logger.debug("make_transfer: money of wrong type")
            self.make_report(
                                from_acc = payment['from_acc'],
                                to_acc = payment['to_acc'],
                                value = 0,
                                kind = payment['kind'],
                                name = payment['name'],
                                code = C_transfer_ERR,
                                message = e.message(),
                                meta = payment['meta']
                                )
            return False

        # first, try to get the money from the sender account, tm = TransferMessage()
        tm_sender = payment['from_acc'].payment_output(
                                                       account_str = payment['to_acc'].name,
                                                       payment = -money,
                                                       kind = payment['kind'],
                                                       description = payment['name'],
                                                       meta = payment['meta']
                                                       )

        # if sending money succeeded, try the receiver side
        if tm_sender.code == C_transfer_OK:
            logger.debug("make_transfer: sender code is OK")
            # in the wired case that money is less than what has been returned by the sender,
            # throw an error message
            if money < (-tm_sender.money):
                raise ValueError("%f was requested from account '%s' but %f returned" % (money,
                                                                                         payment['from_acc'].name,
                                                                                         -tm_sender.money))
            if money > (-tm_sender.money):
                # if payment is fixed, throw an error, otherwise proceed
                if payment['fixed']:
                    raise ValueError("%f was requested from account '%s' but %f returned" % (money,
                                                                                         payment['from_acc'].name,
                                                                                         -tm_sender.money))
                else:
                    money = -tm_sender.money

            tm_receiver = payment['to_acc'].payment_input(
                                                          account_str = payment['from_acc'].name,
                                                          payment = money,
                                                          kind = payment['kind'],
                                                          description = payment['name'],
                                                          meta = payment['meta']
                                                          )
            # if receiving succeeded, return success
            if tm_receiver.code == C_transfer_OK:
                # in the wired case that money is less than what has been returned by the sender,
                # throw an error message
                if money < tm_receiver.money:
                    raise ValueError("%f was submitted to account '%s' but %f returned" % (money,
                                                                                           payment['to_acc'].name,
                                                                                           tm_receiver.money))
                # if the receiver does not accept the entir money
                if money > tm_receiver.money:
                    # check, whether payment is fixed
                    if payment['fixed']:
                        raise ValueError("%f was submitted to account '%s' but %f returned because it is fixed" % (money,
                                                                                               payment['to_acc'].name,
                                                                                               tm_receiver.money))
                    else:
                        # if payment is not fixed, we need to transfer the difference back to
                        # the sender account
                        payment['from_acc'].return_money( money - tm_receiver.money)

                logger.debug("make_transfer: receiver code is OK")
                self.make_report(
                                    from_acc = payment['from_acc'],
                                    to_acc = payment['to_acc'],
                                    value = tm_receiver.money,
                                    kind = payment['kind'],
                                    name = payment['name'],
                                    code = C_transfer_OK,
                                    message = '',
                                    meta = payment['meta']
                                    )
                return True
            else:
                # if an error on the receiver side happened,
                # return the money back and report that
                logger.debug("make_transfer: receiver code is not ok")
                payment['from_acc'].return_money(money)
                self.make_report(
                                    from_acc = payment['from_acc'],
                                    to_acc = payment['to_acc'],
                                    value = tm_sender.money,
                                    kind = payment['kind'],
                                    name = payment['name'],
                                    code = tm_receiver.code,
                                    message = tm_receiver.message,
                                    meta = payment['meta']
                                    )
                return False
        else:
            # if an error occured on the sending side, report this and return false
            logger.debug("make_transfer: sending code is not OK")
            self.make_report(
                                date = self._current_date,
                                from_acc = payment['from_acc'],
                                to_acc = payment['to_acc'],
                                value = money,
                                kind = payment['kind'],
                                name = payment['name'],
                                code = tm_sender.code,
                                message = tm_sender.message,
                                meta = payment['meta']
                                )
            return False


    def simulate(self, date_stop = None, delta = None, last_report = True):
        """ Simulation routine for the entire simulation """
        # Initialization
        date_stop = validate.valid_date_stop(date_stop)

        if (not self._payments_iter):
            self._payments_iter = self._payments.payment(self._current_date)

        if (not self._next_pay):
            try:
                self._next_pay = next(self._payments_iter, C_default_payment)
            except StopIteration:
                # if there are no payments, create a date for a payment
                # that lies in the distant future
                self._next_pay = [{'date': Bank_Date.max}]

        delta = validate.valid_delta(delta)

        temp_delta = 0

        while ((self._current_date < date_stop) and     # ...stop-date is reached
            (temp_delta < delta.days) and           # and delta has not been exeeded
            ((self._current_date - self._date_start).days < C_max_time)):  # ...number of simulated days exceeds max

            # 0. set the current day
            for account in self._accounts:
                if account._date_start <= self._current_date:
                    account.set_date(self._current_date)

            # 1. execute start-of-day function
            # everything that should happen before the money transfer
            for account in self._accounts:
                if account._date_start <= self._current_date:
                    account.start_of_day()

            # 2. execute all controller functions
            for controller in self._controller:
                controller(self)

            # 3. apply all payments for the day in correct temporal order
            if self._next_pay[0]['date'].date() == self._current_date.date():
                for payment in self._next_pay:
                    self.make_transfer(payment)
                self._next_pay = next(self._payments_iter, C_default_payment)

            # 4. execute end-of-day function
            # everything that should happen after the money transfer
            for account in self._accounts:
                if account._date_start <= self._current_date:
                    account.end_of_day()

            # go to the next day within the simulation
            self._day += 1
            self._current_date = self._date_start + timedelta(days = self._day)
            temp_delta += 1

    def reports(self, interval='yearly'):
        """ Returns a tuple of reports for a given interval """
        return (account.report.create_report(interval) for account in self._accounts)

    def plt_summary(self, interval='yearly'):
        """ plots a summary of the simulation """
        reports = self.reports(interval=interval)
        plt.summary(*reports)

    def report_sum_of(self, semantic):
        """ creates the sum for every report.sum_of(semantic) of each account """
        return sum([a.report.sum_of(semantic) for a in self._accounts])

    def print_reports(self, interval):
        """ Creates for every account a report for a given interval """
        for a in self._accounts:
            print(a.name)
            print(a.report.create_report(interval))
            print(' ')


class Account(object):
    """ Basic class for all types of accounts with reporting and simulation
    functionality

    obligatory methods for each account to be part of a simulation
    - set_date
    - start_of_day
    - end_of_day
    - payment_output
    - payment_input
    - return_money
    """

    def __init__(self, amount, interest, date=None, name = None, meta = {}):

        self._date_start = validate.valid_date(date)
        self._name = validate.valid_name(name)
        self._meta = meta
        
        # check for problems
        assert((isinstance(amount, int) or (isinstance(amount, float))))
        if interest > 1.:
            interest = interest / 100.

        # setting up the report and the semantics
        self._report = Report(name = self._name)

        self._account = int(amount * 100)
        self._interest = interest

        self._sum_interest = 0
        self._day = -1
        self._current_date = self._date_start
        self._caccount = self._account
        self._next_pay = None

    def __str__(self):
        return self._name

    @property
    def date(self):
        return self._date
    

    @property
    def date_start(self):
        return self._date_start

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self._report.name = self._name + ' - ' + str(self._date_start.strftime(C_format_date))
        
    @property
    def meta(self):
        return self._meta        

    @property
    def account(self):
        return self._caccount / 100

    def get_account(self):
        """ alternative method to get the current account value. this method
        can be used, e.g. in payment-definitions to transfer the amount of
        money that a specific account has in the moment this payment is done.
        Instead of using an actual value, this method is called, evaluated and
        the return value is used """
        return self.account

    @property
    def interest(self):
        return self._interest / 100

    @property
    def payments(self):
        return self._payments

    @property
    def current_date(self):
        return self._current_date

    @property
    def report(self):
        return self._report

    def as_df(self):
        return self.report.as_df()

    def report_time(self, date):
        """ returns true, if the requirements for a report are met """
        return True

    def get_table_json(self, report):
        """ Creates a table for a given report """
        return {'header': [], 'rows': []}

    def get_all_tables_json(self):
        """ Creates tables for all intervals in report """
        # create all intervals
        daily = self._report
        monthly = daily.create_report(interval='monthly')
        yearly = monthly.create_report(interval='yearly')
        return [{'category': 'Yearly',
                 'data': self.get_table_json(yearly)},
                {'category': 'Monthly',
                 'data': self.get_table_json(monthly)},
                {'category': 'Daily',
                 'data': self.get_table_json(daily)} ]

    def get_report_json(self, interval="yearly"):
        """ creates a data-structure of the report data that can be used for
        displaying the report as table in html files (in jinja2 templates).
        interval can be one of the common intervals of the report class (e.g.
        yearly, monthly, daily) or None. If None, thee raw data are exported.

        If interval is 'all', all intervals will be returned with a
        different json structure """
        if interval is 'all':
            # create all intervals
            return self.get_all_tables_json()
        else:
            if interval is None:
                report = self._report
            else:
                report = self._report.create_report(interval)

            return self.get_table_json(report)


    def payment_input(self, account_str, payment, kind, description, meta):
        """ Input function for payments. This account is the receiver
        of a transfer. This function, if derived from,
        can account for special checks for input operations """
        return TransferMessage(C_transfer_OK, money = payment)

    def payment_output(self, account_str, payment, kind, description, meta):
        """ Output function for payments. This account is the sender
        of a transfer. This function, if derived from,
        can account for special checks for output operations """
        return TransferMessage(C_transfer_OK, money = payment)

    def return_money(self, money):
        """ this is a hard return of transfer-money, in case the receiving side
        rejected the transfer """
        pass

    def set_date(self, date):
        """ This function is called by the simulation class to set the current date
        for the simulation """
        # if there is an inconsistency in the date progression, report
        # a warning on the command line
        delta = (date - self._current_date).days
        if delta != 1:
            warnings.warn('Difference between current date and next date is %i and not 1' % delta)
        if date < self._date_start:
            warnings.warn('Date is before start date of account.')

        self._current_date = date

    def start_of_day(self):
        """ Things that should happen on the start of the day, before any money
        transfer happens """
        pass

    def end_of_day(self):
        """ Things that should happen at the end of the day, after all money
        transfers have been accomplished """
        pass


class DummyAccount(Account):
    """ This account is used when the user creates a Transfer using a
    String as the from-account or to-account. This account basically agrees
    to everything. It can be used to create payments for loans or for
    outgoing costs """

    def __init__(self, name):
        """ Creates a dummy account class """
        self._name = validate.valid_name(name)



# now the implementation of the real, usable classes begins. In contrast to the account class,
# in these classes, report gets some semantic information about how to handle different
# properties of the class

class Bank_Account(Account):
    """ This is a normal bank account that can be used to manage income and
    outgoings within a normal household """

    def __init__(self, amount, interest, date = None, name = None, meta = {}):
        """ Creates a bank account class """
        # call inherited method __init__
        super().__init__(
            amount = amount, interest = interest, date = date, name = name, meta = meta)

        self._report_input = 0
        self._report_output = 0

        self._report.add_semantics('account', 'saving_abs')
        self._report.add_semantics('interest', 'win_cum')
        self._report.add_semantics('input', 'input_cum')
        self._report.add_semantics('output', 'output_cum')
        self._report.add_semantics('foreign_account', 'none')
        self._report.add_semantics('kind', 'none')
        self._report.add_semantics('description', 'none')

        self._interest_paydate = {'month': 12, 'day': 31}
        # reporting functionality
        self._report_interest = 0

        self.make_report()


    # overwriting function
    def make_report(self, interest=0, input=0, output=0,
                    foreign_account = '', kind = '', description = '',
                    meta = {}):
        """ creates a report entry and resets some variables """
        self._report.append(date = self._current_date,
                            account = self._caccount / 100,
                            interest = float('%.2f' % (interest / 100)),
                            input = input / 100,
                            output = output / 100,
                            foreign_account = foreign_account,
                            kind = kind,
                            description = description,
                            meta = meta
                            )

    def exec_interest_time(self):
        """ Does all things, when self.interest_time() returns true (like adding
        interests to the account """
        self._caccount = int(round(self._caccount + self._sum_interest))
        self.make_report(
                         interest = self._sum_interest,
                         kind = 'yearly interest'
                         )
        self._sum_interest = 0

    def as_df(self):
        df = self.report.as_df()
        df = df[['foreign_account', 'description', 'input', 'output', 'interest', 'account']]
        return df

    def get_table_json(self, report):
        """ Creates a table for a given report """
        rows = []
        if report.precision is 'daily':
            header = ['date', 'from', 'description', 'input', 'output', 'interest', 'account']

            for status in report._statuses:
                item = [status.strdate, status._status['foreign_account'],
                    status._status['description'],
                    '%.02f EUR' % status._status['input'],
                    '%.02f EUR' % status._status['output'],
                    '%.02f EUR' % status._status['interest'],
                    '%.02f EUR' % status._status['account']]
                rows.append(item)
        else:
            header = ['date', 'input', 'output', 'interest', 'account']

            for status in report._statuses:
                item = [status.strdate,
                    '%.02f EUR' % status._status['input'],
                    '%.02f EUR' % status._status['output'],
                    '%.02f EUR' % status._status['interest'],
                    '%.02f EUR' % status._status['account']]
                rows.append(item)

        return {'header': header, 'rows': rows}

    def interest_time(self):
        """ Checks, whether it is time to book the interests to the account """
        return ((self._current_date.day == self._interest_paydate['day']) and
                (self._current_date.month == self._interest_paydate['month']))

    def payment_input(self, account_str, payment, kind, description, meta):
        """ Input function for payments. This account is the receiver
        of a transfer. This function, if derived from,
        can account for special checks for input operations """
        return self.payment_move(account_str, payment, kind, description, meta)

    def payment_output(self, account_str, payment, kind, description, meta):
        """ Output function for payments. This account is the sender
        of a transfer. This function, if derived from,
        can account for special checks for output operations """
        return self.payment_move(account_str, payment, kind, description, meta)

    def payment_move(self, account_str, payment, kind, description, meta):
        """ in the base class, payment_input and payment_output have almost
        the same behavior. Only the type of reporting differs

        account_str : the opposite account, sender or receiver
        payment : the int or function which includes the payment
        kind : whether this is a regular payment or a unique one
        description: description of the payment (usually its name)
        move_type: "input" or "output" for indicating the direction of movement """

        move_type = 'input'
        if payment < 0:
            move_type = 'output'

        self._caccount = int(self._caccount + payment)
        report = {'foreign_account': account_str,
                  move_type: payment,
                  'kind': kind,
                  'description': description,
                  'meta': meta}
        self.make_report(**report)
        return TransferMessage(C_transfer_OK, money = payment)

    def return_money(self, money):
        """ this is a hard return of transfer-money, in case the receiving side
        rejected the transfer """
        self._caccount = int(self._caccount + money)
        report = {
                  'input': money,
                  'kind': 'storno',
                  'description': 'transfer did not succeeded'}
        self.make_report(**report)


    def start_of_day(self):
        """ Things that should happen on the start of the day, before any money
        transfer happens """
        pass

    def end_of_day(self):
        """ Things that should happen at the end of the day, after all money
        transfers have been accomplished """
        # TODO: needs to be replaced by a mechanism that checks not every day
        days_per_year = get_days_per_year(self._current_date.year)

        # calculate interest for this day
        interest = self._caccount * (self._interest / days_per_year)

        # store interest for later calculations
        self._sum_interest += interest

        # if paydate is there, add the summed interest to the account
        if self.interest_time():
            self.exec_interest_time()


class Loan(Account):
    """
    This is the default account class that should capture the essential
    functionalities of account models
    """

    def __init__(self, amount, interest, date = None, name = None, meta = {}):
        """
        Creates the data for a basic account model
        """
        # call inherited method __init__
        super().__init__(
            amount = -amount, interest = interest, date = date, name = name, meta = meta)

        # reporting functionality
        self._report_payment = 0

        self._report.add_semantics('account', 'debt_abs')
        self._report.add_semantics('interest', 'cost_cum')
        self._report.add_semantics('payment', 'debtpayment_cum')
        self._report.add_semantics('foreign_account', 'none')
        self._report.add_semantics('kind', 'none')
        self._report.add_semantics('description', 'none')

        self._interest_paydate = {'month': 12, 'day': 31}

        self.make_report()

    def as_df(self):
        df = self.report.as_df()
        df = df[['foreign_account', 'description', 'payment', 'interest', 'account']]
        return df

    def get_table_json(self, report):
        rows = []
        if report.precision is 'daily':
            header = ['date', 'from', 'description', 'payment', 'interest', 'account']
            for status in report._statuses:
                item = [status.strdate,
                        status._status['foreign_account'],
                        status._status['description'],
                        '%.02f EUR' % status._status['payment'],
                        '%.02f EUR' % status._status['interest'],
                        '%.02f EUR' % status._status['account']]
                rows.append(item)
        else:
            header = ['date', 'payment', 'interest', 'account']
            for status in report._statuses:
                item = [status.strdate,
                        '%.02f EUR' % status._status['payment'],
                        '%.02f EUR' % status._status['interest'],
                        '%.02f EUR' % status._status['account']]
                rows.append(item)
        return {'header': header, 'rows': rows}

    def is_finished(self):
        """ Returns true, if the loan has been payed back, including
        interest for the current year """
        return (self._caccount + self._sum_interest) >= 0.

    def make_report(self, payment = 0, interest = 0,
                    foreign_account = '', kind = '', description = '',
                    meta = {}):
        """ creates a report entry and resets some variables """
        self._report.append(
                            date = self._current_date,
                            account = self._caccount / 100,
                            payment = payment / 100,
                            interest = float('%.2f' % (interest / 100)),
                            foreign_account = foreign_account,
                            kind = kind,
                            description = description,
                            meta = meta
                            )

    @property
    def account(self):
        return (self._caccount + self._sum_interest) / 100

    def get_account(self):
        return self.account

    def exec_interest_time(self):
        """ Does all things, when self.interest_time() returns true (like adding
        interests to the account """
        self._caccount = int(round(self._caccount + self._sum_interest))
        self.make_report(
                         interest = self._sum_interest,
                         kind = 'yearly interest'
                         )
        self._sum_interest = 0

    def interest_time(self):
        """ Checks, whether it is time to book the interests to the account """
        return (((self._current_date.day == self._interest_paydate['day']) and
                (self._current_date.month == self._interest_paydate['month'])) or
                (self._caccount > 0))

    def payment_input(self, account_str, payment, kind, description, meta):
        """ Input function for payments. This account is the receiver
        of a transfer. This function, if derived from,
        can account for special checks for input operations """
        if ((self._caccount + self._sum_interest) >= 0):
            return TransferMessage(C_transfer_NA, money = 0, message = "No credit to pay for")

        payed = min(-(self._caccount + self._sum_interest), payment)
        if payed == payment:
            self._caccount = int(self._caccount + payed)
            report = {'payment': payed,
                      'foreign_account': account_str,
                      'kind': kind,
                      'description': description,
                      'meta': meta}
            self.make_report(**report)
        else:
            self._caccount = int(self._caccount + self._sum_interest + payed)
            report = {'payment': payed,
                      'interest': self._sum_interest,
                      'foreign_account': account_str,
                      'kind': kind,
                      'description': description + ' + Interests',
                      'meta': meta}
            self.make_report(**report)
            self._sum_interest = 0
        return TransferMessage(C_transfer_OK, money = payed)

    def payment_output(self, account_str, payment, kind, description, meta):
        """ Output function for payments. This account is the sender
        of a transfer. This function, if derived from,
        can account for special checks for output operations """
        return TransferMessage(C_transfer_NA, money = 0, message = "Credit cannot be increased")

    def return_money(self, money):
        """ this is a hard return of transfer-money, in case the receiving side
        rejected the transfer """
        self._caccount = int(self._caccount + money)
        report = {'date': self._current_date,
                  'account': self._caccount,
                  'payment': money,
                  'kind': 'storno',
                  'description': 'transfer did not succeeded'}
        self._report.append(**report)

    def start_of_day(self):
        """ Things that should happen on the start of the day, before any money
        transfer happens """
        pass

    def end_of_day(self):
        """ Things that should happen at the end of the day, after all money
        transfers have been accomplished """
        # TODO: needs to be replaced by a mechanism that checks not every day
        days_per_year = get_days_per_year(self._current_date.year)

        # calculate interest for this day
        interest = self._caccount * (self._interest / days_per_year)

        # store interest for later calculations
        self._sum_interest += interest

        # if paydate is there, add the summed interest to the account
        if self.interest_time():
            self.exec_interest_time()

class Property(Account):
    """
    This class can be used to reflect the amount of property that is gained
    from filling up a loan. This account does nothing else than adjusting the
    amount of property depending on the payments transfered to the loan class
    """

    def __init__(self, property_value, amount, loan, date = None, name = None, meta = {}):
        """
        For a property with a given value (property_value), the current amount
        that is transfered to the owner (amount) is reflected by the amount of
        money that has been transfered to the loan. Loan must here of class
        loan
        """
        assert isinstance(loan, Loan), 'loan must be of type Loan, but is in fact of type ' + str(type(loan))
        assert property_value > amount, 'property_value must be greater than amount'

        self._name = validate.valid_name(name)
        self._date_start = validate.valid_date(date)
        self._meta = meta

        self._property_value = int(property_value * 100)
        self._account = int(amount*100)     # amount of money already invested
        self._caccount = self._account
        self._loan = loan

        # setting up the report and the semantics
        self._report = Report(name = self._name)

        self._report.add_semantics('account', 'saving_abs')
        self._report.add_semantics('property_value', 'none')
        #self._report.add_semantics('interest', 'cost_cum')
        #self._report.add_semantics('payment', 'debtpayment_cum')
        #self._report.add_semantics('foreign_account', 'none')
        #self._report.add_semantics('kind', 'none')
        #self._report.add_semantics('description', 'none')

        self._current_date = self._date_start

        self.make_report()

    def make_report(self):
        """ creates a report entry and resets some variables """
        self._report.append(
                            date = self._current_date,
                            account = self._caccount / 100,
                            property_value = self._property_value / 100
                            )

    def get_table_json(self, report):
        """ Creates a table for a given report """
        header = ['date', 'account']
        rows = []
        for status in report._statuses:
            item = [status.strdate,
                    '%.02f' % status._status['account']
                    ]
            rows.append(item)

        return {'header': header, 'rows': rows}

    def get_account(self):
        return self._caccount / 100


    def payment_input(self, account_str, payment, kind, description, meta):
        """ Input function for payments. This account is the receiver
        of a transfer. This function, if derived from,
        can account for special checks for input operations """
        return TransferMessage(C_transfer_ERR, money = payment, message="Properties cannot be involved in transfers")

    def payment_output(self, account_str, payment, kind, description, meta):
        """ Output function for payments. This account is the sender
        of a transfer. This function, if derived from,
        can account for special checks for output operations """
        return TransferMessage(C_transfer_ERR, money = payment, message="Properties cannot be involved in transfers")

    def return_money(self, money):
        """ this is a hard return of transfer-money, in case the receiving side
        rejected the transfer """
        pass

    def end_of_day(self):
        """ Things that should happen at the end of the day, after all money
        transfers have been accomplished """
        new_caccount = self._account + (1- (self._loan._caccount / self._loan._account)) * (self._property_value - self._account)
        # this if-clause is included to avoid daily reporting. Reports are
        # just updates, if account volume changes or if if is the end of a year
        if ((new_caccount != self._caccount) or
           ((self._current_date.day == 31) and
             (self._current_date.month == 12))):
            self._caccount = new_caccount
            self.make_report()
