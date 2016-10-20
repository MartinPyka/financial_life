''' 

This is a reconstruction of the LBS Bauspar Tarife 

WARNING: This is a manual attempt to simualate some of the LBS products. This is by no means
a reliable and accurate simulation! For a realistic simulation of your financial plans, please
consult a pofessional assistent from the company selling these products.

'''

# standard libraries
from datetime import datetime, timedelta
from calendar import monthrange
from decimal import *

# custom libraries
import numpy as np

# own libraries
from financial_life.financing import Report, Payments
from financial_life.financing import C_default_payment, id_generator
from financial_life.financing.colors import colors
from financial_life.financing import validate
from financial_life.financing.accounts import Account, C_format_date, C_max_time
from financial_life.calendar_help import Bank_Date

flex_l5 = {
           'C_POINT_PER_DAY': 0.0563,
           'C_POINT_PER_EUR': 1 / 750.,
           'C_POINT_LIMIT': 171,
           'guthabenzins' : 0.0025,
           'entgelt' : 7.2,
           'bausparanteil': 0.4,
           'darlehenszins': 0.0215,
           'wartemonate': 4,
           'agio': 0.02,
           'versicherung': 0.003,
           'name' : 'Flex L5',
    }

direkt_10 = {
           'C_POINT_PER_DAY': 0.0403,
           'C_POINT_PER_EUR': 1 / 650.,
           'C_POINT_LIMIT': 176,
           'guthabenzins' : 0.001,
           'entgelt' : 7.2,
           'bausparanteil': 0.4,
           'darlehenszins': 0.0195,
           'wartemonate': 3,
           'agio': 0.02,
           'versicherung': 0.003,
           'name' : 'Direkt 10',
    }

direkt_15 = {
           'C_POINT_PER_DAY': 0.0403,
           'C_POINT_PER_EUR': 1 / 650.,
           'C_POINT_LIMIT': 176,
           'guthabenzins' : 0.001,
           'entgelt' : 7.2,
           'bausparanteil': 0.4,
           'darlehenszins': 0.0175,
           'wartemonate': 3,
           'agio': 0.02,
           'versicherung': 0.003,
           'name' : 'Direkt 15',
    }

alternative = {
           'C_POINT_PER_DAY': 0.0403,
           'C_POINT_PER_EUR': 1 / 650.,
           'C_POINT_LIMIT': 176,
           'guthabenzins' : 0.001,
           'entgelt' : 7.2,
           'bausparanteil': 0.4,
           'darlehenszins': 0.025,
           'wartemonate': 3,
           'agio': 0.02,
           'versicherung': 0.003,
           'name' : 'Direkt 15',
    }

tarife = {
          'flex_l5': flex_l5,
          'direkt_10': direkt_10,
          'direkt_15': direkt_15,
          'alternative': alternative
          }

class Bauspar(Account):
    """ This is a generic class for the german LBS Bauspar product """
    
    def __init__(self, guthaben, bausparsumme, punkte, tarif, date = None, name = None):
        if tarif not in tarife:
            raise TypeError("Contract type not found in contract list: {}".format(tarif))

        self._tarif = tarife[tarif]
        
        self._date_start = self.valid_date(date)
        self._name = self.valid_name(name)
        
        self._report = Report(
            name = self._name + ' - ' + str(self._date_start.strftime(C_format_date)))
        self._report.add_semantics('account', 'saving_abs')
        self._report.add_semantics('loan', 'debt_abs')
        self._report.add_semantics('loan_interest', 'cost_cum')
        self._report.add_semantics('account_interest', 'win_cum')
        self._report.add_semantics('points', 'none')
        self._report.add_semantics('payments', 'debtpayment_cum')
        self._report.add_semantics('agio', 'cost_cum')
        self._report.add_semantics('insurance', 'cost_cum')
        self._report.add_semantics('entgelt', 'cost_cum')
        
        self._guthaben = int(guthaben * 100)
        self._bausparsumme = int(bausparsumme * 100)
        self._darlehen = self._bausparsumme - np.max(
            [
             self._bausparsumme * self._tarif['bausparanteil'],
             self._guthaben
            ]
        )
        self._punkte = punkte
        
        self._payments = Payments()
        self._payments_iter = None
        
        self._sum_interest = 0          # this value is used because it is inherited from account
        self._sum_loan_interest = 0     # but we need an extra variable for the loan interest
        self._sum_loan_insurance = 0
        self._day = -1
        self._current_date = self._date_start
        self._caccount = self._guthaben
        self._cdarlehen = self._darlehen
        self._next_pay = None
        
        self._interest_paydate = {'month': 12, 'day': 31}
        
        # this function determines, in which phase of the product we are
        self._phase = self.saving_phase
        
        # reporting functionality
        self._record = {
                        'loan_interest': 0,
                        'account_interest': 0,
                        'payments' : 0,
                        'entgelt' : 0,
                        'insurance': 0,
                        'agio': 0
                        }
    

    @property
    def loan(self):
        return self._cdarlehen / 100
        
    def get_loan(self):
        """ alternative method to get the current loan value. this method 
        can be used, e.g. in payment-definitions to transfer the amount of 
        money that a specific account has in the moment this payment is done. 
        Instead of using an actual value, this method is called, evaluated and
        the return value is used """
        return self.loan

    def simulate(self, date_stop = None, delta = None, last_report = True):
        """ Simulates the state of the account to the end-date.
        If there is no end_date, the simulation will run until account is either 
        zero or the account continuously increases 10 times in a row
        
            delta:
                Time (e.g. days) to simulate. This argument can be used along
                with date_stop. Whatever comes first, aborts the while-loop
            last_report: 
                if True, after the while-loop a report will be added. For 
                simulations along with other products, this can be omitted by
                setting this argument to False
        """
        date_stop = validate.valid_date_stop(date_stop)
        delta = validate.valid_delta(delta)
        # if this is not the time for this product, abort
        if date_stop < self._current_date:
            return
        
        if (not self._payments_iter):
            self._payments_iter = self._payments.payment(self._current_date)
        
        if (not self._next_pay):
            self._next_pay = next(self._payments_iter, C_default_payment)
        
        self._phase(date_stop, delta, last_report)
        
    def get_credit(self):
        """ Switches to a new modus in this product, in which the loan is given to the 
        customer. Depending on the amount of points and the account, the customer 
        needs to enter the so-called "zwischenfinanzierung"
        """
        self._cdarlehen = self._bausparsumme - self._caccount
        
        if (self._punkte < self._tarif['C_POINT_LIMIT'] or 
            self._caccount < (self._tarif['bausparanteil'] * self._bausparsumme)):
            self._phase = self.zwischen_phase
        else:
            self._phase = self.loan_phase
            agio = self._cdarlehen * self._tarif['agio']
            self._cdarlehen += agio
            self._report.append(date = self._current_date,
                                agio = (agio / 100))
        
    def loan_track_data(self, loan_interest, loan_insurance, payed):
        self._record['loan_interest'] += loan_interest
        self._record['insurance'] += loan_insurance
        self._record['payments'] += payed
    
    def loan_make_report(self):
        self._report.append(date = self._current_date,
                            loan_interest = self._record['loan_interest'] / 100,
                            insurance = self._record['insurance'] / 100,
                            payments = self._record['payments'] / 100,
                            loan = self._cdarlehen / 100,
                            )
        
        # set everything to zero
        self._record = dict.fromkeys(self._record, 0)        
        
    def loan_exec_interest_time(self):
        self._cdarlehen = int(round(self._cdarlehen + self._sum_loan_interest + self._sum_loan_insurance))
        self._sum_loan_interest = 0
        self._sum_loan_insurance = 0
        
    def loan_phase(self, date_stop = None, delta = None, last_report = True):
        """ Routine for the payment of the loan """
        temp_delta = 0
        while ((self._current_date < date_stop) and     # ...stop-date is reached
            (temp_delta < delta.days) and               # and delta has not been exeeded
            ((self._current_date - self._date_start).days < C_max_time) and
            (self._cdarlehen > 0)):  # ...number of simulated days exceeds max
            
            # go to next day
            self._day += 1
            self._current_date = self._date_start + timedelta(days = self._day)
            temp_delta += 1
            
            # calculate the day
            self._cdarlehen, loan_interest, loan_insurance, payed = self.loan_simulate_day()
            
            # store interest for later calculations
            self._sum_loan_interest += loan_interest
            self._sum_loan_insurance += loan_insurance
            
            # if paydate is there, add the summed interest to the account
            if self.interest_time():
                self.loan_exec_interest_time()
            
            # tracking for reports
            self.loan_track_data(loan_interest, loan_insurance, payed)
            
            # make a report
            if self.report_time(self._current_date):
                self.loan_make_report()
                
            
        # create report at the end of the simulation
        if last_report:
            # as the simulation might not end at the end of the year,
            # we need to apply exec_interest_time() one last time
            self.exec_interest_time()
            self.loan_make_report()        
        
    def loan_simulate_day(self):
        days_per_year = self.get_days_per_year()
        
        payed = self.get_payments()
        payed = min(self._cdarlehen + self._sum_loan_interest + self._sum_loan_insurance, payed)
        new_darlehen = int(self._cdarlehen - payed)

        loan_interest = new_darlehen * (self._tarif['darlehenszins'] / days_per_year)
        loan_insurance = new_darlehen * (self._tarif['versicherung'] / days_per_year)
                
        return new_darlehen, loan_interest, loan_insurance, payed        
        
    def zwischen_track_data(self, account_interest, loan_interest, payed, entgelt):
        """ tracks data during saving phase """
        self._record['account_interest'] += account_interest
        self._record['loan_interest'] += loan_interest
        self._record['payments'] += payed
        self._record['entgelt'] += entgelt
        
    def zwischen_make_report(self):
        self._report.append(date = self._current_date,
                            account = self._caccount / 100,
                            account_interest = self._record['account_interest'] / 100,
                            loan_interest = self._record['loan_interest'] / 100,
                            payments = self._record['payments'] / 100,
                            entgelt = self._record['entgelt'] / 100,
                            loan = self._cdarlehen / 100,
                            points = self._punkte
                            )
        
        # set everything to zero
        self._record = dict.fromkeys(self._record, 0)
        
    def zwischen_exec_interest_time(self):
        self._caccount = int(round(self._caccount + self._sum_interest - self._sum_loan_interest))
        self._sum_interest = 0
        self._sum_loan_interest = 0     
        
    def zwischen_phase(self, date_stop = None, delta = None, last_report = True):
        """ Routine for the phase called 'Zwischenfinanzierung' """
        temp_delta = 0
        while ((self._current_date < date_stop) and     # ...stop-date is reached
            (temp_delta < delta.days) and               # and delta has not been exeeded
            ((self._current_date - self._date_start).days < C_max_time) and
            (self._punkte < self._tarif['C_POINT_LIMIT'] or 
             self._caccount < (self._tarif['bausparanteil'] * self._bausparsumme) )):  # ...number of simulated days exceeds max
            
            # go to next day
            self._day += 1
            self._current_date = self._date_start + timedelta(days = self._day)
            temp_delta += 1
            
            # calculate the day
            self._caccount, account_interest, loan_interest, payed, entgelt = self.zwischen_simulate_day()
            
            # store interest for later calculations
            self._sum_interest += account_interest
            self._sum_loan_interest += loan_interest
            
            # if paydate is there, add the summed interest to the account
            if self.interest_time():
                self.zwischen_exec_interest_time()
            
            self._cdarlehen = self._bausparsumme - self._caccount
            
            # tracking for reports
            self.zwischen_track_data(account_interest, loan_interest, payed, entgelt)
            
            # make a report
            if self.report_time(self._current_date):
                self.zwischen_make_report()
                
        # when the while loop ended because the points are above the limit, then we can
        # switch to the next phase
        if (self._punkte >= self._tarif['C_POINT_LIMIT']):
            self.get_credit()            
            
        # if simulation time is not over yet, continue with simulating the loan_phase
        if ((self._current_date < date_stop) and 
            (temp_delta < delta.days) and
            ((self._current_date - self._date_start).days < C_max_time)):
            self.loan_phase(date_stop, delta, last_report)
        else:
            # create report at the end of the simulation
            if last_report:
                # as the simulation might not end at the end of the year,
                # we need to apply exec_interest_time() one last time
                self.exec_interest_time()
                self.zwischen_make_report()
            
    def zwischen_simulate_day(self):
        days_per_year = self.get_days_per_year()
        
        new_account = self._caccount
        entgelt = 0
        
        if (self._current_date.day == 1) and (self._current_date.month == 1):
            entgelt = self._tarif['entgelt'] * 100
            new_account -= entgelt
        
        payed = self.get_payments()            
        new_account = int(new_account + payed)            
        self._punkte += (payed / 100) * self._tarif['C_POINT_PER_EUR']
        
        account_interest = new_account * (self._tarif['guthabenzins'] / days_per_year)
        loan_interest = self._bausparsumme * (self._tarif['darlehenszins'] / days_per_year)
        self._punkte += self._tarif['C_POINT_PER_DAY']
            
        return new_account, account_interest, loan_interest, payed, entgelt                 
        
    def saving_track_data(self, interest, payed, entgelt):
        """ tracks data during saving phase """
        self._record['account_interest'] += interest
        self._record['payments'] += payed
        self._record['entgelt'] += entgelt

    def saving_make_report(self):
        self._report.append(date = self._current_date,
                            account = self._caccount / 100,
                            account_interest = self._record['account_interest'] / 100,
                            payments = self._record['payments'] / 100,
                            entgelt = self._record['entgelt'] / 100,
                            points = self._punkte
                            )
        
        # set everything to zero
        self._record = dict.fromkeys(self._record, 0)

    def saving_phase(self, date_stop = None, delta = None, last_report = True):
        temp_delta = 0
        while ((self._current_date < date_stop) and     # ...stop-date is reached
            (temp_delta < delta.days) and               # and delta has not been exeeded
            ((self._current_date - self._date_start).days < C_max_time)):  # ...number of simulated days exceeds max
            
            # go to next day
            self._day += 1
            self._current_date = self._date_start + timedelta(days = self._day)
            temp_delta += 1
            
            # calculate the day
            self._caccount, interest, payed, entgelt = self.saving_simulate_day()
            
            # store interest for later calculations
            self._sum_interest += interest
            
            # if paydate is there, add the summed interest to the account
            if self.interest_time():
                self.exec_interest_time()
            
            # tracking for reports
            self.saving_track_data(interest, payed, entgelt)
            
            # make a report
            if self.report_time(self._current_date):
                self.saving_make_report()
    
        # create report at the end of the simulation
        if last_report:
            # as the simulation might not end at the end of the year,
            # we need to apply exec_interest_time() one last time
            self.exec_interest_time()
            self.saving_make_report()

    def saving_simulate_day(self):
        days_per_year = self.get_days_per_year()
        
        new_account = self._caccount
        entgelt = 0
        
        if (self._current_date.day == 1) and (self._current_date.month == 1):
            entgelt = self._tarif['entgelt'] * 100
            new_account -= entgelt
                
        payed = self.get_payments()
        new_account = int(new_account + payed)
        self._punkte += (payed / 100) * self._tarif['C_POINT_PER_EUR']
        
        interest = new_account * (self._tarif['guthabenzins'] / days_per_year)
        self._punkte += self._tarif['C_POINT_PER_DAY']
            
        return new_account, interest, payed, entgelt