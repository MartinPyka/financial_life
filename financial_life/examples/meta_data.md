# Meta-Fields and Controller functions

You can attach meta-data to any account class and any payment. These meta-data can be used to facilitate more complex calculations within your simulations, like the correct calculation of tax payments. With the help of controller-functions you can access these information to incorporate them into your simulation.

Meta-data can be attached like this in your simulation definition:

```python
# meta data for account classes, like loans
loan = a.Loan(amount = 100000,
              interest = 0.01,
              name = 'House Credit',
              date="01.09.2016",
              meta = {'tax': {'outcome': 'yearly_interests'}}
              )

# meta data for payments
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
```

financial_life let's you add controller-functions to your simultions, which are executed every day before money is transfered between accounts. The controller-function is called with the simulation-object as argument:

```python
def controller_tax(s):
    """ This is a controller function that calculates annual tax rates
    's' is the simulation object
    """
    # Do something, e.g. check, how much brutto income have been
    # transfered to the account and home much interests from the
    # loan account must be subtracted from it. See meta_data.py
    # for a full example

# add controller function to simulation
simulation.add_controller(controller_tax)
```

With `account.report.with_meta()` or `simulation.report.with_meta()` you can make these information visible, when you print the report.

See the full example [here](meta_data.py).
