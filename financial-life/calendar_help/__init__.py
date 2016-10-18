from calendar import monthrange
from datetime import date
from datetime import timedelta
from datetime import datetime

class Bank_Date(datetime):
    """ This is a helper class that adds some additional functionality
    to the datetime class, like adding months to the date or calculating
    the difference between two dates in months    
    """
    def is_end_of_month(self):
        """ returns true, if the current day is the end of month """
        return monthrange(self.year, self.month)[1] == self.day
    
    def add_month(self, months):
        """ introduces calculation with months """
        new_year = self.year + int((self.month + months - 1)/12)
        new_month = ((self.month + months - 1) % 12) + 1
        new_day = min(self.day, monthrange(new_year, new_month)[1])
        return Bank_Date(year = new_year, month = new_month, day = new_day)
                   
    def diff_months(self, sub2):
        """ calculates the differences in months between two dates """
        if not isinstance(sub2, datetime):
            raise NotImplementedError
                        
        years = 0
        months = 0
        if (sub2.year > self.year):
            years = max(0, sub2.year - (self.year + 1))
            months = (12 - self._month + 1) + sub2.month
        elif (sub2.year == self.year):
            months = sub2.month - self.month
        elif sub2.year < self.year:
            years = min(0, sub2.year + 1 - self.year)
            months = -(12 - sub2.month + 1) - self.month
            
        return years * 12 + months


def get_days_per_year(year):
    # returns the number of days per year
    return 365 if monthrange(year, 2)[1] == 28 else 366

# deprecated, old methods for maniuplating datetime

def add_month(start_date, months):
    """ introduces calculation with months """
    new_year = start_date.year + int((start_date.month + months - 1)/12)
    new_month = ((start_date.month + months - 1) % 12) + 1
    new_day = min(start_date.day, monthrange(new_year, new_month)[1])
    new_date = date(new_year, new_month, new_day)
    return new_date
                   
def diff_months(sub1, sub2):
    """ calculates the differences in months between two dates """
    years = 0
    months = 0
    if (sub2.year > sub1.year):
        years = max(0, sub2.year - (sub1.year + 1))
        months = (12 - sub1.month + 1) + sub2.month
    elif (sub2.year == sub1.year):
        months = sub2.month - sub1.month
    elif sub2.year < sub1.year:
        years = min(0, sub2.year + 1 - sub1.year)
        months = -(12 - sub2.month + 1) - sub1.month
        
    return years * 12 + months