
from dateutil import parser
from chatgpt import get_full_retirement_age, random_inflation

class Person:

    def __init__(self, name, birthday_str, salary, retirement_age, ss_age, ss_benefits, spouse=None):
        self.name = name
        self.birthday = parser.parse(birthday_str)
        self.salary = salary
        self.retirement_age = retirement_age
        self.ss_start_age = ss_age
        self.ss_benefits = ss_benefits
        self.spouse = spouse
        if self.spouse and self.spouse.spouse != self:
            self.spouse.spouse = self

    def __str__(self):
        return self.name

    def age(self, year):
        birthday = self.birthday
        return year - birthday.year

    def birth_year(self):
        return self.birthday.year

    def retired(self, year):
        return self.age(year) >= self.retirement_age

    def claiming_ss(self, year):
        return self.age(year) >= self.ss_start_age

    def ss_amount(self):
        return self.ss_benefits[self.ss_start_age - 62]

    def waited_for_full_ss(self, year):
        age = self.age(year)
        return age >= self.ss_start_age and age >= get_full_retirement_age(year)


class Account:
    # assigned values, used within a single year
    EXPENSES = "expenses"
    TAXED_INC = "taxed_income"
    UNTAXED_INC = "untaxed_income"
    # computed values, used within a single year
    TAX_OWED = "tax_owed"
    IRA_WITHDRAWALS = "ira_withdrawals"
    # persistent running balances
    SAVINGS = "savings"
    DEFERRED_IRA = "ira"
    EXEMPT_ROTH = "roth"

    def __init__(self, acct_type, owner, balance):
        self.type = acct_type
        self.owner = owner
        self.balance = balance

    def add(self, amount):
        before = self.balance
        after = self.balance + amount
        ownership = f"{self.owner}'s" if self.owner else "shared"
        add = "+" if amount >= 0 else "-"
        print(
            f"    . account {ownership} {self.type} : ${int(before)} {add} {abs(amount)} -> ${int(after)}"
        )
        self.balance = after

    def subtract(self, amount):
        self.add(0 - amount)

    def clean_balance(self):
        if abs(self.balance) < 0.1:
            return 0
        return self.balance

    def persistent(self):
        return self.type in [Account.SAVINGS, Account.DEFERRED_IRA, Account.EXEMPT_ROTH]

    def label(self):
        if self.owner:
            return f"{self.owner.name}'s {self.type}"
        return f"{self.type}"

    def __str__(self):
        return f"{self.label()}: ${int(self.clean_balance())}"

class Accounts:
    def __init__(self, initial_accounts=None):
        self.accounts = {}
        # add COPIES of initial accounts
        for account in initial_accounts:
            self.add(Account(account.type, account.owner, account.balance))

    def add(self, account):
        acct_type = account.type
        owner = account.owner
        # TODO - COPY here instead of reference
        self.accounts[(acct_type, owner)] = account

    def get(self, acct_type, owner=None):
        acct = self.accounts.get((acct_type, owner))
        if not acct:
            acct = Account(acct_type, owner, 0)
            self.add(acct)
        return acct

    def sum(self, acct_types):
        if not hasattr(acct_types, '__iter__'):
            acct_types = [acct_types]
        return sum([a.balance for a in self.accounts.values() if a.type in acct_types])

    def all(self):
        return list(self.accounts.values())

    def persistent_accounts(self):
        return [a for a in self.accounts.values() if a.persistent()]

    def perennial_accounts(self):
        return [a for a in self.accounts.values() if not a.persistent()]

    def __str__(self):
        return "\n".join([str(a) for a in self.accounts.values()])

