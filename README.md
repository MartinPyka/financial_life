# financial-life
A framework for analysing financial products in personalized contexts

# Description
financial-life is an opinionated framework written in Python that allows to simulation monetary flows between different types of accounts. These simulations facilitate a deeper and more holistic understanding of financial plans and a better comparison of financial products in personalized contexts.

# Usage
Say you want to model an account with regular income and payments to a loan

```python
from datetime import timedelta
from financial_life.financing import accounts as a
    
account = a.Bank_Account(amount = 1000, interest = 0.001, name = 'Main account')
loan = a.Loan(amount = 100000, interest = 0.01, name = 'House Credit')

simulation = a.Simulation(account, loan)
    
simulation.add_regular('Income', account, 2000, interval = 'monthly')
simulation.add_regular(account, loan, 1500, interval= 'monthly')
    
simulation.simulate(delta = timedelta(days=365*10))
simulation.plt_summary()

print(account.report.yearly())
print(loan.report.yearly())
```  

The output of will look similar to this one:


    Date          input    account  foreign_account      output  description                   interest  kind
    ----------  -------  ---------  -----------------  --------  --------------------------  ----------  ---------------
    31.12.2016   4000      2000.33                        -3000                                    0.33  yearly interest
    31.12.2017  24000      8005.59                       -18000                                    5.26  yearly interest
    31.12.2018  24000     14016.9                        -18000                                   11.27  yearly interest
    31.12.2019  24000     20034.1                        -18000                                   17.28  yearly interest
    31.12.2020  24000     26057.4                        -18000                                   23.29  yearly interest
    31.12.2021  24000     32086.8                        -18000                                   29.32  yearly interest
    31.12.2022  32140.9   46265.2                        -18000                                   37.56  yearly interest
    31.12.2023  42000     70324.5                        -18000                                   59.32  yearly interest
    31.12.2024  42000     94407.9                        -18000                                   83.35  yearly interest
    31.12.2025  42000    118515                          -18000                                  107.46  yearly interest
    01.10.2026  35000    138515                          -15000                                    0     storno
    Date          account    payment  foreign_account    description      interest  kind
    ----------  ---------  ---------  -----------------  -------------  ----------  ---------------
    31.12.2016  -97195.7     3000                                          -195.68  yearly interest
    31.12.2017  -80069.8    18000                                          -874.07  yearly interest
    31.12.2018  -62772.6    18000                                          -702.81  yearly interest
    31.12.2019  -45302.4    18000                                          -529.84  yearly interest
    31.12.2020  -27657.7    18000                                          -355.32  yearly interest
    31.12.2021   -9836.41   18000                                          -178.69  yearly interest
    31.12.2022       0       9859.09                                        -22.68  yearly interest
    31.12.2023       0          0                                             0     yearly interest
    31.12.2024       0          0                                             0     yearly interest
    31.12.2025       0          0                                             0     yearly interest


# Installation
To get a working environment, simply do

	git clone https://github.com/MartinPyka/financial-life.git
	cd financial-life
	virtualenv venv
	source venv/bin/activate
	pip install -r requirements.txt

A package-based installation is coming soon.

