# financial-life
A framework for analysing financial products in personalized contexts

# Description
financial-life is an opinionated framework written in Python that allows to simulation monetary flows between different types of accounts. These simulations facilitate a deeper and more holistic understanding of financial plans and a better comparison of financial products in personalized contexts.

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
	Date           output    input    interest    account
	----------  ---------  -------  ----------  ---------
	31.12.2016   -3000        4000        0.32    2000.32
	31.12.2017  -18000       24000        5.26    8005.58
	31.12.2018  -18000       24000       11.27   14016.9
	31.12.2019  -18000       24000       17.28   20034.1
	31.12.2020  -18000       24000       23.29   26057.4
	31.12.2021  -18000       24000       29.32   32086.7
	31.12.2022   -9830.65    24000       37.57   46293.7
	31.12.2023     -22.65    24000       59.32   70330.3
	31.12.2024       0       24000       83.36   94413.7
	31.12.2025       0       24000      107.47  118521
	01.10.2026       0       20000        0     138521
	House Credit
	Date          interest    account    payment
	----------  ----------  ---------  ---------
	31.12.2016     -190.22  -97190.2     3000
	31.12.2017     -874.01  -80064.2    18000
	31.12.2018     -702.75  -62767      18000
	31.12.2019     -529.78  -45296.8    18000
	31.12.2020     -355.26  -27652      18000
	31.12.2021     -178.63   -9830.65   18000
	31.12.2022      -22.65     -22.65    9830.65
	31.12.2023        0          0         22.65
	31.12.2024        0          0          0
	31.12.2025        0          0          0
	Interests on bank account: 374.46
	Interests on loan account: -2853.30

# Installation
To get a working environment, simply do

	git clone https://github.com/MartinPyka/financial-life.git
	cd financial-life
	virtualenv venv
	source venv/bin/activate
	pip install -r requirements.txt

A package-based installation is coming soon.

