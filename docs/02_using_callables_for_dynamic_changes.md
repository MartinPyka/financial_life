# Using callables for dynamic changes

Sometimes, parameters like the amount of money to be transfered or the stop date cannot be statically defined at the beginning of your simulation. Instead, they depend on the current state of your simulation.

Therefore, fl supports callables as arguments for some keywords, in order to cover more complex modeling scenarios.

## Dynamic payments

Callables can be used to determine the amount of money to be transfered from one account to the other. This means, instead of writing

```python
simulation.add_regular(from_acc=account,
                       to_acc=loan,
                       payment=1500,
                       interval='monthly')
```

we can make sure, that we transfer only the amount of money to the loan account that is necessary: either 1500 or what is left. We can achieve this with a simple lambda-function.

The loan account provide the property `loan.account`, which returns the debts we still need to pay. This is a negative number, therefore, we must put a minus-sign in front of it:

```python
simulation.add_regular(from_acc=account,
                       to_acc=loan,
                       payment=lambda: min(1500, -loan.account),
                       interval='monthly')
```

Let's go a step further and say we want to transfer at maximum 1500 but also make sure that we always have 2000 on our account and that we transfer only the money that is really need on the loan account.

```python
simulation.add_regular(from_acc=account,
                       to_acc=loan,
                       payment=lambda: min(
                                          max(
                                              min(1500, account.account-2000),
                                              0),
                                          -loan.account),
                       interval='monthly')
```

The max-statement in this lambda-function is included to make sure that when `account.account - 2000` is a negative number, we won't initiate a negative transfer to the loan-account (which would be captured by the loan-account anyway).

These callables are executed in each simulation cycle (which is every day within the simulation) and therefore decide depending on the simulation state how much money is transfered to the loan account.
