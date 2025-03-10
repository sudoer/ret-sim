#!/usr/bin/env python3

import datetime
import random
import time

from chatgpt import estimate_income_tax, calculate_rmd
from common import *
from custom import Customizations


class Simulation:
    def __init__(self, custom, start_year, num_years):
        self.custom = custom
        self.start_year = start_year
        self.num_years = num_years
        self.family = self.custom.family
        self.accounts = Accounts(self.custom.initial_balances)
        self.year = None
        random.seed(time.time())

    def __str__(self):
        on_year = ''
        if self.year:
            on_year = f" on {self.year}"
        return f"Simulation{on_year} for {self.num_years} years with balances: {self.accounts}"

    def job_income(self):
        for person in self.family:
            self.individual_job_income(person)

    def individual_job_income(self, person):
        if person.retired(self.year):
            print(f" - {person} does not work")
        else:
            gross_salary = person.salary
            net_salary = gross_salary
            roth_401k_limit = 23500
            age = person.age(self.year)
            if age >= 64:
                roth_401k_limit += 7500
            elif age >= 60:
                roth_401k_limit += 11250
            elif age >= 50:
                roth_401k_limit += 7500
            if net_salary > roth_401k_limit:
                net_salary -= roth_401k_limit
                self.accounts.get(Account.EXEMPT_ROTH, person).add(roth_401k_limit)
            print(f" - {person} salary = ${gross_salary} -> ${roth_401k_limit} roth + ${net_salary} net")
            self.accounts.get(Account.TAXED_INC).add(net_salary)

    def socsec_income(self):

        # common formula, used a few times below
        def benefit(person):
            soc_sec = 0
            if person.claiming_ss(self.year):
                soc_sec = person.ss_amount() * 12
            return soc_sec

        # find the higher benefit among spouses who can collect
        higher_benefit = 0
        for person in self.family:
            soc_sec = benefit(person)
            if soc_sec > higher_benefit:
                higher_benefit = soc_sec

        # collect benefits, if available
        for person in self.family:
            if person.claiming_ss(self.year):
                their_benefit = benefit(person)
                collected_benefit = their_benefit
                # special case - spousal benefit
                # lower earning spouse must wait until full retirement age (67-ish)
                if person.waited_for_full_ss(self.year):
                    collected_benefit = max(their_benefit, 0.5 * higher_benefit)
                if collected_benefit > their_benefit:
                    print(f" - {person} earns 1/2 spouse's social security = ${collected_benefit}")
                else:
                    print(f" - {person} earns social security = ${collected_benefit}")
                self.accounts.get(Account.TAXED_INC).add(collected_benefit)


    def required_minimum_distributions(self):
        for person in self.family:
            person_age = person.age(self.year)
            if person_age >= 73:
                ira_balance = self.accounts.get(Account.DEFERRED_IRA).balance
                rmd = calculate_rmd(ira_balance, person_age)
                if rmd > 0:
                    print(f" - {person} takes RMD of ${int(rmd)}")
                    self.accounts.get(Account.IRA_WITHDRAWALS).add(rmd)
                    self.accounts.get(Account.DEFERRED_IRA, person).subtract(rmd)

    def roth_conversions(self):
        # Only do a Roth conversion if we have no other taxable income.
        if self.accounts.get(Account.TAXED_INC).balance > 0:
            return

        for person in self.family:
            trad_ira_value = self.accounts.get(Account.DEFERRED_IRA, person).balance
            conversion = min(trad_ira_value, 125_000)
            if conversion <= 0:
                continue
            print(
                f" - Roth conversion ${int(conversion)} from {person}'s traditional IRAs"
            )
            self.accounts.get(Account.DEFERRED_IRA, person).subtract(conversion)
            self.accounts.get(Account.EXEMPT_ROTH, person).add(conversion)
            # In order for us to pay taxes on this amount, record it again as taxable income.
            self.accounts.get(Account.IRA_WITHDRAWALS).add(conversion)
            self.accounts.get(Account.SAVINGS).subtract(conversion)

    def move_from_retirement_accounts(self, ret_acct_type, amount, target_acct, why):
        # Figure out how much we have in the specified type of retirement accounts for people over 60.
        # TODO - refactor this into a "take proportionally" function ??
        print(
            f" - requesting ${int(amount)} from {ret_acct_type} for {why}"
        )
        all_balances = 0.0
        for person in self.family:
            if person.age(self.year) >= 59.5:
                all_balances += self.accounts.get(ret_acct_type, person).balance
        if all_balances <= 0:
            print(f" - no withdrawable money in {ret_acct_type} accounts")
            return
        # Figure out how much we need to distribute from each person's retirement accounts.
        for person in self.family:
            if person.age(self.year) >= 59.5:
                person_balance = self.accounts.get(ret_acct_type, person).balance
                person_share = min(amount * (person_balance / all_balances), person_balance)
                print(
                    f" - distributing ${int(person_share)} from {person}'s {ret_acct_type} for {why}"
                )
                self.accounts.get(ret_acct_type, person).subtract(person_share)
                self.accounts.get(target_acct).add(person_share)

    def voluntary_distributions(self):
        target_int = self.custom.distribution_percentage(self.year)
        target_pct = target_int / 100.0
        why = f"{target_int}% voluntary distribution"

        # Figure out how much we need to distribute from Traditional IRAs
        already_distributed_ira = self.accounts.get(Account.IRA_WITHDRAWALS).balance
        total_ira_value = self.accounts.sum(Account.DEFERRED_IRA)
        target_ira_distribution = total_ira_value * target_pct
        remaining = target_ira_distribution - already_distributed_ira
        if remaining > 0:
            # Distribute from traditional IRAs to the "IRA Withdrawals" account, which keeps track
            # of how much we've taken out of traditional retirement accounts.  At the end of the
            # cycle, we'll sweep this back into the savings account like normal money.
            self.move_from_retirement_accounts(Account.DEFERRED_IRA, remaining, Account.IRA_WITHDRAWALS, why)

        # Figure out how much we need to distribute from Roth IRAs
        already_distributed_roth = 0
        total_roth_value = self.accounts.sum(Account.EXEMPT_ROTH)
        target_roth_distribution = total_roth_value * target_pct
        remaining = target_roth_distribution - already_distributed_roth
        if remaining > 0:
            # Distribute from Roth IRAs directly into savings, since we do not have to pay taxes on it.
            self.move_from_retirement_accounts(Account.EXEMPT_ROTH, remaining, Account.SAVINGS, why)

    def calculate_taxes(self):
        taxable_income = self.accounts.get(Account.TAXED_INC).balance + self.accounts.get(Account.IRA_WITHDRAWALS).balance
        tax = estimate_income_tax(taxable_income)
        print(f" - estimated tax on ${taxable_income:,.0f} income is ${tax:,.0f}")
        # Since it's an expense, we'll record it as a negative number.
        self.accounts.get(Account.TAX_OWED).subtract(tax)

    def sweep_category_accounts_into_savings(self):
        for acct in [Account.EXPENSES, Account.TAXED_INC, Account.UNTAXED_INC, Account.IRA_WITHDRAWALS, Account.TAX_OWED]:
            move_amt = self.accounts.get(acct).balance
            if int(abs(move_amt)) > 0:
                print(f" - sweeping ${int(move_amt)} from {acct} into savings")
                self.accounts.get(Account.SAVINGS).add(move_amt)

    def ensure_minimum_savings_balance(self):
        desired_savings = self.custom.minimum_savings_balance(self.year)
        for from_acct, to_acct in [(Account.DEFERRED_IRA, Account.IRA_WITHDRAWALS), (Account.EXEMPT_ROTH, Account.SAVINGS)]:
            savings_balance = self.accounts.get(Account.SAVINGS).balance
            if savings_balance <= desired_savings:
                # Our savings account is running very low.
                # Pull some from retirement accounts to cover the shortfall.
                shortfall = desired_savings - savings_balance
                print(f" - savings came up short by ${int(shortfall)}")
                self.move_from_retirement_accounts(from_acct, shortfall, to_acct, "savings shortfall")
        savings_balance = self.accounts.get(Account.SAVINGS).balance
        if savings_balance <= 0:
            raise ValueError("Out of money")


    def total_value(self):
        value = self.accounts.sum([Account.SAVINGS, Account.DEFERRED_IRA, Account.EXEMPT_ROTH])
        return int(value)


    def print_year(self):
        line = f"YEAR {self.year}:"
        for person in self.family:
            line += f"  {person.name}: {person.age(self.year)}  "
        for account in self.accounts.persistent_accounts() + self.accounts.perennial_accounts():
            line += f"  {account}"
        print(line)


    def apply_investment_returns_and_inflation(self):
        ret_pct = self.custom.return_percentage()
        inf_pct = self.custom.inflation_percentage()
        print(f" - investment returns = {ret_pct:.1f}%, inflation = {inf_pct:.1f}%")

        for account in self.accounts.persistent_accounts():
            before = account.balance
            account.balance *= (1.0 + (ret_pct - inf_pct) / 100.0)
            after = account.balance
            pct = 0
            if before > 0:
                pct = ((after / before) - 1) * 100.0
            print(f" - account {account.label()} : {int(before)} -> {int(after)} = {pct:.2f}%")

    def single_simulation(self):
        # sim_balances = Accounts(initial_balances)

        self.year = self.start_year
        self.print_year()
        year_totals = [self.total_value()]
        try:
            for iteration in range(self.num_years):
                # clear transient values
                for account in self.accounts.perennial_accounts():
                    account.balance = 0
                # earn income
                self.job_income()
                self.socsec_income()
                # spend money
                self.custom.budget_expenses(self.year, self.accounts)
                self.custom.housing_expenses(self.year, self.accounts)
                self.custom.healthcare_expenses(self.year, self.accounts)
                # other adjustments
                self.custom.other_one_time_adjustments(self.year, self.accounts)
                # pull money out of retirement accounts
                self.required_minimum_distributions()
                self.roth_conversions()
                self.voluntary_distributions()
                self.calculate_taxes()
                # At this point, we have adjusted all of the accounts to show how money was moved around.
                # But we really need to sweep it all back into actual savings accounts.
                self.sweep_category_accounts_into_savings()
                self.ensure_minimum_savings_balance()
                # last step = capital gains and inflation
                self.apply_investment_returns_and_inflation()
                # adjust year number, print summary, store total for chart
                self.year += 1
                self.print_year()
                year_totals.append(self.total_value())
        except ValueError as e:
            print(f"ERROR: {e}")
            self.year += 1
            self.print_year()
            while len(year_totals) <= num_years:
                year_totals.append(0)

        return year_totals


# Simulation

import matplotlib.pyplot as plt

start_year = datetime.date.today().year
num_years = 50
year_array = range(start_year, start_year + num_years + 1)
simulations = 100
successes = [0] * (num_years+1)

for sim_num in range(simulations):
    print(f"SIMULATION {sim_num + 1}")
    this_sim = Simulation(Customizations(), start_year, num_years)
    print(f"starting {this_sim}")
    single_sim_data = this_sim.single_simulation()
    plt.plot(year_array, single_sim_data, marker=None, linestyle=None)

    # calculate successes - in this one run, did my money last X years?
    for year in year_array:
        if single_sim_data[year - start_year] > 0:
            successes[year - start_year] += 1

for year in range(start_year, start_year + num_years + 1, 5):
    print(f"{year}, {100 * successes[year - start_year] / simulations : .1f} %")

# plt.title("My Plot")
plt.xlabel("years")
plt.ylabel("money")
plt.ylim(bottom=0, top=5_000_000)

# Format the y-axis (money) to prevent scientific notation
plt.ticklabel_format(axis='y', style='plain')
# Optionally, format the x-axis (years) as well
plt.ticklabel_format(axis='x', style='plain')

plt.show()
