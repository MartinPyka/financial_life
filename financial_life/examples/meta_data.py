'''
Created on 21.12.2016

@author: martin
'''
# standard libraries
from datetime import timedelta

# third-party libraries

# own libraries
from financial_life.financing import accounts as a
from financial_life.tax import germany as tax_ger


def controller_tax(s):
    """ This is a controller function that calculates annual tax rates
    's' is the simulation object
    """
    # perform tax calculation always on 15th of February, just to
    # reflect the fact that tax payments for the previous year are
    # never made on the 1st of January, which has an impact on 
    # interests as well
    if ((s.current_date.month == 2) and 
       (s.current_date.day == 15)):
        # account class for payments
        account = s.accounts[0]
        
        # filter for all transactions that occured in the previous year
        # and of type 'income'
        income_report = s.report.subset(lambda st: (st.date.year == (s.current_date.year-1)) and 
                                                   (st.meta.get('type','') == 'income'))
        
        # using list comprehensions, we can easily calculate a few sums
        #m_income = sum(income.value)  
        m_brutto = sum(payment.meta['tax']['brutto'] for payment in income_report)
        m_paid = sum(payment.meta['tax']['paid'] for payment in income_report)
        
        # get all accounts which have the field tax.outcome == 'yearly_interests'
        loans = [account for account in s.accounts 
                 if account.meta.get('tax', {}).get('outcome','') == 'yearly_interests']
        # get only the reports of last year
        interests_reports = [loan.report.subset(lambda st: st.date.year == (s.current_date.year-1)) 
                             for loan in loans]
        # sum up all interests from all interests reports
        m_interests = sum(sum(report.interest) for report in interests_reports)                
        
        # as interests for loans are negative, we effectively
        # subtract the payed interests from the brutto we earned in the last year
        m_tax_relevant_money = m_brutto + m_interests
        # now, we apply german tax rules from 2016 to the tax-relevant money
        m_tax, m_tax_percentage = tax_ger.tax_to_pay(2016, m_tax_relevant_money)
        # this is the money we either receive from the state (positive value
        # or we need to pay (negative value)
        m_diff = m_paid - m_tax
        
        s.add_unique('State', account, m_diff, 
                     date = s.current_date + timedelta(days=1),
                     name = 'Tax',
                     fixed = True,
                     meta = {
                             'taxpayment': {
                                            'tax_relevant_money': m_tax_relevant_money,
                                            'tax_to_pay': m_tax,
                                            'tax_percentage': m_tax_percentage,
                                            'paid': m_paid,
                                            'difference': m_diff
                                            }
                             }
                     )
        
    
def example_meta_controller(print_it = True):
    """ This example shows, how meta-information for payments and account data could
    be used to calculate annual tax-return """
    account = a.Bank_Account(amount = 1000, interest = 0.001, name = 'Main account', date="01.09.2016")
    
    # define meta-data for accounts. here: some fields that are relevant for 
    # tax calculations 
    loan = a.Loan(amount = 100000, interest = 0.01, name = 'House Credit', date="01.09.2016",
                  meta = {'tax': {
                                  'outcome': 'yearly_interests' 
                                  }
                          }
                  )
    
    # add these accounts to the simulation
    simulation = a.Simulation(account, loan, date='01.09.2016')

    # our employee receives monthly 2000 netto, coming from 2500 brutto,
    # 310 are subtracted directly from the loan, which is less than she
    # needs to pay. 190 are paid for insurance
    simulation.add_regular('Income', account, 2000, 
                           interval = 'monthly', 
                           date_start="01.09.2016", 
                           meta={'type': 'income', 
                                 'tax': {
                                         'brutto': 2500, 
                                         'paid': 310,
                                         'insurance': 190
                                         }
                                }
                           )

    simulation.add_regular(account, loan, lambda: min(1500, -loan.account), 
                           interval = 'monthly', 
                           date_start="01.09.2016")
    simulation.add_controller(controller_tax)

    # simulate for ten years
    simulation.simulate(delta = timedelta(days=365*10))

    # this function is also part of a unittest. Therefore, we want to be able to
    # control, whether we print some information or not
    if print_it:
        # print reports summarized in years
        print(account.report.with_meta())
        #print(loan.report.with_meta())
    return simulation

if __name__ == '__main__':
    example_meta_controller()
