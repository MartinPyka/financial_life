# financial-life
A framework for analysing financial products in personalized contexts

# Description
financial-life is an opinionated framework written in Python that allows to simulate monetary flows between different types of accounts. These simulations facilitate a deeper and more holistic understanding of financial plans and a better comparison of financial products in personalized contexts.

# Usage
Say you want to model an account with regular income and payments to a loan

```python
account = a.Bank_Account(amount = 1000, interest = 0.001, name = 'Main account')
loan = a.Loan(amount = 100000, interest = 0.01, name = 'House Credit')

simulation = a.Simulation(account, loan)

simulation.add_regular('Income', account, 2000, interval = 'monthly')
simulation.add_regular(account, loan, lambda: min(1500, -loan.account), interval = 'monthly')

simulation.simulate(delta = timedelta(days=365*10))
simulation.plt_summary()

print(account.report.yearly())
print(loan.report.yearly())

print("Interests on bank account: %.2f" % sum(account.report.yearly().interest))
print("Interests on loan account: %.2f" % sum(loan.report.yearly().interest))
```  

The output of will look similar to this one:

	Main account
	Date          account     output     input    interest
	----------  ---------  ---------  --------  ----------
	31.12.2016    2000.32   -3000.00   4000.00        0.32
	31.12.2017    8005.58  -18000.00  24000.00        5.26
	31.12.2018   14016.85  -18000.00  24000.00       11.27
	31.12.2019   20034.13  -18000.00  24000.00       17.28
	31.12.2020   26057.42  -18000.00  24000.00       23.29
	31.12.2021   32086.74  -18000.00  24000.00       29.32
	31.12.2022   46271.00   -9853.30  24000.00       37.56
	31.12.2023   70330.32       0.00  24000.00       59.32
	31.12.2024   94413.68       0.00  24000.00       83.36
	31.12.2025  118521.15       0.00  24000.00      107.47
	01.10.2026  138521.15       0.00  20000.00        0.00
	House Credit
	Date          account    interest    payment
	----------  ---------  ----------  ---------
	31.12.2016  -97190.22     -190.22    3000.00
	31.12.2017  -80064.23     -874.01   18000.00
	31.12.2018  -62766.98     -702.75   18000.00
	31.12.2019  -45296.76     -529.78   18000.00
	31.12.2020  -27652.02     -355.26   18000.00
	31.12.2021   -9830.65     -178.63   18000.00
	31.12.2022       0.00      -22.65    9853.30
	31.12.2023       0.00        0.00       0.00
	31.12.2024       0.00        0.00       0.00
	31.12.2025       0.00        0.00       0.00
	Interests on bank account: 374.45
	Interests on loan account: -2853.30

# Installation
To get a working environment, simply do

	git clone https://github.com/MartinPyka/financial_life.git
	cd financial_life
	virtualenv venv
	source venv/bin/activate
	pip install -r requirements.txt

A package-based installation is coming soon.

