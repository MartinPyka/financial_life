""" help functions for german tax declaration """

def tax_to_pay(year, *args, **kwargs):
    """ generic functions to call the tax-function for any year. 
    This functions simply calls the year-dependent function with 
    the given parameters, but this function don't really care about
    the content of the other arguments """
    return tax_functions[year](*args, **kwargs)

def tax_to_pay_2016(tax_relevant_money, splitting = False):
    """ calculates the tax for year 2016 
    
    Returns the tax and the percentage of the tax """
    if tax_relevant_money <= 0:
        return 0, 0
    
    if splitting:
        trm = tax_relevant_money / 2.
    else:
        trm = tax_relevant_money
    
    if trm > 250730:
        tax = trm * 0.45 - 15783.19
    elif trm > 52881:
        tax = trm * 0.42-8261.29
    elif trm > 13469:
        tax = (trm-13469)*((trm-13469)*0.0000022874+0.2397)+948.68
    elif trm > 8472:
        tax = (trm-8472)*((trm-8472)*0.000009976+0.14)
    else: 
        tax = 0
    
    if splitting:
        return tax*2, ((tax*2) / tax_relevant_money)
    else:
        return float(int(tax*100)/100), (tax / tax_relevant_money)

tax_functions = {2016: tax_to_pay_2016}