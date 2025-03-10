
from chatgpt import random_inflation

class CustomizationsTemplate:
    family = None
    initial_balances = None

    def budget_expenses(self, year, accounts):
        raise NotImplementedError

    def housing_expenses(self, year, accounts):
        raise NotImplementedError

    def healthcare_expenses(self, year, accounts):
        raise NotImplementedError

    def other_one_time_adjustments(self, year, accounts):
        raise NotImplementedError

    def return_percentage(self):
        raise NotImplementedError

    def inflation_percentage(self):
        # mean=3.0, std_dev=2.0, min_value=-2.0, max_value=15.0
        return random_inflation()

    def distribution_percentage(self, year):
        raise NotImplementedError

    def minimum_savings_balance(self, year):
        raise NotImplementedError

