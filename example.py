
from common import Person, Account
import chatgpt
from simulation import SimulationBase


class Simulation(SimulationBase):

    def __init__(self, start_year, num_years):
        self.joe = Person(
            'Joe',
            '1970-01-01',
            125_000,
            65,
            70,
            [2606, 2793, 2998, 3264, 3533, 3804, 3921, 4243, 4767]
        )
        self.jane = Person(
            'Jane',
            '1971-01-01',
            95_000,
            64,
            70,
            [860, 948, 1045, 1170, 1300, 1436, 1548, 1714, 1940],
            self.joe
        )
        super().__init__(start_year, num_years)

    def family(self):
        return [self.joe, self.jane]

    def initial_balances(self):
        return [
            Account(Account.SAVINGS, None, 150_000),
            Account(Account.DEFERRED_IRA, self.joe, 100_000),
            Account(Account.DEFERRED_IRA, self.jane, 75_000),
            Account(Account.EXEMPT_ROTH, self.joe, 125_000),
            Account(Account.EXEMPT_ROTH, self.jane, 105_000),
        ]

    def budget_expenses(self, year, accounts):
        expenses = 75_000
        print(f" - budget expenses = ${expenses}")
        # Expenses are subtracted from the expenses account
        accounts.get(Account.EXPENSES).subtract(expenses)


    def housing_expenses(self, year, accounts):
        # taxes
        expenses = 4000

        # HOA
        expenses += 50 * 12

        # 30-year mortgage, starting in 2015
        if year <= 2015+30:
            expenses += (2500*12)

        print(f" - housing expenses = ${expenses}")
        # Expenses are subtracted from the expenses account
        accounts.get(Account.EXPENSES).subtract(expenses)


    def healthcare_expenses(self, year, accounts):
        for person in self.family():
            expenses = 0
            if person.age(year) >= 80:
                # more health problems
                expenses += 10000
            elif person.age(year) >= 65:
                # medicare
                expenses += 5000
            print(f" - healthcare expenses for {person} = ${int(expenses)}")
            # Expenses are subtracted from the expenses account
            accounts.get(Account.EXPENSES).subtract(expenses)


    def other_one_time_adjustments(self, year, accounts):

        if year % 5 == 0:
            print(" - buying a new car")
            # Expenses are subtracted from the expenses account
            accounts.get(Account.EXPENSES).subtract(40_000)

        # employer shares
        if year == 2034:
            print(" - sell company shares for $100,000")
            accounts.get(Account.TAXED_INC).add(100_000)

        pass


    def return_percentage(self):
        return chatgpt.random_inflation(mean=6.5, std_dev=2.0, min_value=-5.0, max_value=24.0)
        # return chatgpt.random_inflation(mean=6.5, std_dev=8.0, min_value=-5.0, max_value=24.0)


    def inflation_percentage(self):
        # mean=3.0, std_dev=2.0, min_value=-2.0, max_value=15.0
        return chatgpt.random_inflation()


    def distribution_percentage(self, year):
        return 2.0


    def minimum_savings_balance(self, year):
        return 50000
