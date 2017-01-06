# Examples

In this folder, you find a list of examples that will help you getting started.

### simple_examples.py

[simple_examples.py](simple_examples.py) shows three beginner examples that are also highlighted on the [front-page](../../README.md) of this repository.

### dependencies.py

[dependencies.py](dependencies.py) showcases the account-class `Property`, which uses access to a loan class to determine, how much value of a given property has been transfered to the owner, when the loan is decreased. The key lines are:

```python
loan = a.Loan(200000, 0.0185, name = 'Credit' )
# the class property defines a dependency on loan. When loan
# decreases, the house-property increases
house = a.Property(200000, 0, loan, name='House')
```

The value of `house` will becomes bigger when the value of `loan` decreases. See also more information about this construct in the [documentation](../../docs/03_dependencies_between_accounts.md).

### meta_data.py

[meta_data.py](meta_data.py) demonstrates the usage of meta-data and controllers, in order to model tax returns. A full explanation of this example can be found [here](meta_data.md).
