
from common import age
from constants import *
import chatgpt
import random
import time

family = [
    {
        "name": "Bob",
        "birthday": "1970-01-01",
        "salary": 125000,
        "retirement": 62,
        "collect_ss": 70,
        # taken from the social security statement: monthly payments if retirement at age 62-70.
        "ss_per_mo": [2606, 2793, 2998, 3264, 3533, 3804, 3921, 4243, 4767],
        "spouse": "Jane",
    },
    {
        "name": "Jane",
        "birthday": "1971-02-02",
        "salary": 95000,
        "retirement": 64,
        "collect_ss": 70,
        # taken from the social security statement: monthly payments if retirement at age 62-70.
        "ss_per_mo": [860, 948, 1045, 1170, 1300, 1436, 1548, 1714, 1940],
        "spouse": "Bob",
    },
]

initial_balances = {
    "savings": 300000,
    "ira": {"Bob": 100000, "Jane": 75000},
    "roth": {"Bob": 125000, "Jane": 105000},
}

random.seed(time.time())

def budget_expenses(year, balances):
    expenses = 75000
    print(f" - budget expenses = ${expenses}")
    balances[EXPENSES] -= expenses


def housing_expenses(year, balances):
    expenses = 60000
    print(f" - housing expenses = ${expenses}")
    balances[EXPENSES] -= expenses


def return_percentage():
    return chatgpt.random_inflation(mean=6.0, std_dev=2.0, min_value=-2.0, max_value=15.0)


def inflation_percentage():
    return chatgpt.random_inflation()


def distribution_percentage(year):
    return 4.0


def minimum_savings_balance(year):
    return 50000


def healthcare_expenses(year, balances):
    for person in family:
        expenses = 0
        if age(person, year) >= 80:
            # more health problems
            expenses += 10000
        elif age(person, year) >= 65:
            # medicare
            expenses += 5000
        else:
            # Obamacare
            expenses += 12 * 1707 / 2
        print(f" - healthcare expenses for {person['name']} = ${int(expenses)}")
        balances[EXPENSES] -= expenses


def other_one_time_adjustments(year, balances):
    # company stock options
    if year == 2034:
        print(" - sell company options for $100,000")
        balances[TAXED_INC] += 100000
