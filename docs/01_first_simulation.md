# The first simulation

In this chapter, we are going to introduce the basic concepts of creating a simulation in order to analyse monetary flows and growth on bank accounts.

In the following, financial_life will be abbreviated with fl.

Each simulation setup can be devided into three different steps:

1. Define the accounts involved in the simulation
2. Define monetary flows between these accounts
3. Simulate

After that you have several options to explore the outcome of your simulation.

## 1. Define the accounts involved in the simulation

The module `financial_life.financing.accounts` features some basic accounts like a normal bank account with yearly interests and a loan account that does not allow to be in the positive value range and only permits money transferd to the account but not from the account.

The package also contains a Property account that establishes a dependency to a loan account. We will come to that later.

Lets start with creating an ordinary bank account, which you would use to receive your salary and pay your bills. This account is called `Bank_Account` and it is defined in the following way:

```python
class Bank_Account(Account):
    """ This is a normal bank account that can be used to manage income and
    outgoings within a normal household """
    def __init__(self, amount, interest, date = None, name = None):
```
<table>
  <tr>
    <th>
      Keyword Argument
    </th>
    <th>
      Description
    </th>
  </tr>
  <tr>
    <td>
      amount
    </td>
    <td>
      The amount of money to start with
    </td>
  </tr>
  <tr>
    <td>
      interest
    </td>
    <td>
      The yearly interest rate for this account. 1% correspond to 0.01 as argument value
    </td>
  </tr>
  <tr>
    <td>
      date
    </td>
    <td>
      The date, when this account should exist. Before this date, the account will not be simulated. For quick simulation, where this nuance is not relevant, this field can be left empty. As date, datetime and strings in the format '%d.%m.%y', '%m/%d/%Y' are accepted.
    </td>
  </tr>
  <tr>
    <td>
      name
    </td>
    <td>
      Simply a string representation of the account id. If empty, fl will create a random string sequence.
    </td>
  </tr>
</table>

So an ordinary bank account with a volume of 1000 and an interest rate of 0.1% is defined like this.

```python
from financial_life.financing import accounts as a

account = a.Bank_Account(amount = 1000,
                         interest = 0.001,
                         name = 'Main account')
```

A `loan` account, although its behavior is slightly different, is defined in the same manner. For a loan of 100,000 you would create a `loan` account like this:

```python
loan = a.Loan(amount = 100000, interest = 0.01, name = 'House Credit')
```

Last but not least, you need to assign these accounts to a simulation. This is a one-liner as well.

```python
simulation = a.Simulation(account, loan)
```

## 2. Define monetary flows between these accounts

Next. we define monetary flows between these accounts. Here, we will introduce the methods for regular and unique payments but we will cover only a part of it. In later chapters, we will dig deeper into the kind of stuff that you can create with it.

The simulation class is also defined in `financial_life.financing.accounts` and looks like this

```python
def add_regular(self, from_acc, to_acc, payment, interval,
                date_start=datetime.min,
                day=1,
                name = '',
                date_stop = None,
                fixed = False):

def add_unique(self, from_acc, to_acc, payment,
               date,
               name = '',
               fixed = False):             
```
<table>
  <tr>
    <th>
      Keyword Argument
    </th>
    <th>
      Description
    </th>
  </tr>
  <tr>
    <td>
      from_acc,
      to_acc
    </td>
    <td>
      The account objects that define from where money flows and to which account money flows. For money transfers that involve accounts outside of the simulation, a string can be used.
    </td>
  </tr>
  <tr>
    <td>
      payment
    </td>
    <td>
      The amount of money that is transfered.
    </td>
  </tr>
  <tr>
    <td>
      interval
    </td>
    <td>
      'monthly' or 'yearly' are possible currently.
    </td>
  </tr>
  <tr>
    <td>
      date_start / date
    </td>
    <td>
      The start date of this regular payments. It can be either a datetime object or a string. It has also a default value, so it does not need to be used for quick simulations.
    </td>
  </tr>
  <tr>
    <td>
      day
    </td>
    <td>
      The day in a month on which this transfer should be initiated.
    </td>
  </tr>
  <tr>
    <td>
      name
    </td>
    <td>
      Name of the money transfer. Corresponds to the subject in a normal money transfer.
    </td>
  </tr>
  <tr>
    <td>
      date_stop
    </td>
    <td>
      Stop date of regular payments. Can be either datetime, string or even a callable. We will cover this later.
    </td>
  </tr>
  <tr>
    <td>
      fixed
    </td>
    <td>
      Whether sender and receiver of the money should insist of the full money transfer. If, for example, a loan has only 100 to be payed, but the transfer defines 150, this would cause an error, when `fixed` is true. If it is false, the rest money is transfered back.
    </td>
  </tr>
</table>

Here are two examples of how money flows can be defined. The first one describes the salary, coming from an account outside of this simulation. The second one is a money transfer within our simulation.

```python
simulation.add_regular('Income', account, 2000, interval = 'monthly')
simulation.add_regular(account, loan, 1500, interval = 'monthly')
```

## 3. Simulate

The simulation is started for a given amount of time. This period is either defined through a give stop date or by a delta value.

```python
def simulate(self, date_stop = None, delta = None)
```

<table>
  <tr>
    <th>
      Keyword Argument
    </th>
    <th>
      Description
    </th>
  </tr>
  <tr>
    <td>
      date_stop
    </td>
    <td>
      Stop date of the simulation
    </td>
  </tr>
  <tr>
    <td>
      delta
    </td>
    <td>
      Number of days to simulate.
    </td>
  </tr>
</table>

In order to simulate our model for 10 years, the code could look like this.

```python
simulation.simulate(delta = timedelta(days=365*10))
```

## Explore the simulation

Here are some examples of exploring the outcome of your data.

```python
# use matplotlib for a graphical summary of the simulation
simulation.plt_summary()

# print reports summarized in years
print(account.report.yearly())
print(loan.report.yearly())

# analyze data
print("Interests on bank account: %.2f" % sum(account.report.interest))
print("Interests on loan account: %.2f" % sum(loan.report.interest))

# create html report
cwd = os.path.dirname(os.path.realpath(__file__))
result_folder = cwd + '/example2'
html.report(simulation, style="standard", output_dir = result_folder)
```

## Code snippet

And here is the code for the simulation again as a whole

```python
account = a.Bank_Account(amount = 1000, interest = 0.001, name = 'Main account')
loan = a.Loan(amount = 100000, interest = 0.01, name = 'House Credit')

simulation = a.Simulation(account, loan)

simulation.add_regular('Income', account, 2000, interval = 'monthly')
simulation.add_regular(account, loan, lambda: min(1500, -loan.account), interval = 'monthly')

simulation.simulate(delta = timedelta(days=365*10))
simulation.plt_summary()
```
