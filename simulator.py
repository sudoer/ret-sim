#!/usr/bin/env python3

import datetime
from copy import deepcopy
from idlelib.runscript import indent_message

from chatgpt import estimate_income_tax, calculate_rmd, get_full_retirement_age
from common import *
from custom import *
from constants import *


# Fixed functions


def clear_transient_values(balances):
    balances[EXPENSES] = 0
    balances[TAXED_INC] = 0
    balances[UNTAXED_INC] = 0
    balances[IRA_WITHDRAWALS] = 0
    balances[TAX_OWED] = 0


def job_income(year, balances):
    for person in family:
        individual_job_income(person, year, balances)


def individual_job_income(person, year, balances):
    if age(person, year) < person["retirement"]:
        gross_salary = person["salary"]
        net_salary = gross_salary
        roth_401k_limit = 23500
        if age(person, year) >= 64:
            roth_401k_limit += 7500
        elif age(person, year) >= 60:
            roth_401k_limit += 11250
        elif age(person, year) >= 50:
            roth_401k_limit += 7500
        if net_salary > roth_401k_limit:
            net_salary -= roth_401k_limit
            balances[EXEMPT_ROTH][person["name"]] += roth_401k_limit
        print(f" - {person['name']} salary = ${gross_salary} -> ${roth_401k_limit} roth + ${net_salary} net")
        balances[TAXED_INC] += net_salary
    elif age(person, year) == person["retirement"]:
        print(f" - {person['name']} retires this year")
    else:
        print(f" - {person['name']} does not work")




def socsec_income(year, balances):

    # common formula, used a few times below
    def benefit(person):
        soc_sec = 0
        if age(person, year) >= person["collect_ss"]:
            soc_sec = person["ss_per_mo"][person["collect_ss"] - 62] * 12
        return soc_sec

    # find the higher benefit among spouses who can collect
    higher_benefit = 0
    for person in family:
        soc_sec = benefit(person)
        if soc_sec > higher_benefit:
            higher_benefit = soc_sec

    # collect benefits, if available
    for person in family:
        retirement_age = person["collect_ss"]
        current_age = age(person, year)
        if current_age >= retirement_age:
            their_benefit = benefit(person)
            collected_benefit = their_benefit
            # special case - spousal benefit
            # lower earning spouse must wait until full retirement age (67-ish)
            if retirement_age >= get_full_retirement_age(birth_year(person)):
                collected_benefit = max(their_benefit, 0.5 * higher_benefit)
            if collected_benefit > their_benefit:
                print(f" - {person['name']} earns 1/2 spouse's social security = ${collected_benefit}")
            else:
                print(f" - {person['name']} earns social security = ${collected_benefit}")
            balances[TAXED_INC] += collected_benefit


def required_minimum_distributions(year, people, balances):
    for person in people:
        person_age = age(person, year)
        if person_age >= 73:
            rmd = calculate_rmd(
                balances[DEFERRED_IRA][person["name"]], person_age
            )
            if rmd > 0:
                print(f" - {person['name']} takes RMD of ${int(rmd)}")
                balances[IRA_WITHDRAWALS] += rmd
                balances[DEFERRED_IRA][person["name"]] -= rmd


def roth_conversions(year, balances):
    if balances[TAXED_INC] > 0:
        return
    for person in family:
        trad_ira_value = balances[DEFERRED_IRA][person["name"]]
        conversion = min(trad_ira_value, 125_000)
        if conversion <= 0:
            continue
        print(
            f" - Roth conversion ${int(conversion)} from {person['name']}'s traditional IRAs"
        )
        balances[DEFERRED_IRA][person["name"]] -= conversion
        balances[EXEMPT_ROTH][person["name"]] += conversion
        # In order for us to pay taxes on this amount, record it again as taxable income.
        balances[IRA_WITHDRAWALS] += conversion
        balances[SAVINGS] -= conversion

def move_from_retirement_accounts(year, balances, ret_acct_type, amount, target_acct, why):
    # Figure out how much we have in the specified type of retirement accounts for people over 60.
    print(
        f" - requesting ${int(amount)} from {ret_acct_type} for {why}"
    )
    all_balances = 0.0
    for person in family:
        if age(person, year) >= 60:
            all_balances += balances[ret_acct_type][person["name"]]
    if all_balances <= 0:
        print(f" - no withdrawable money in {ret_acct_type} accounts")
        return
    # Figure out how much we need to distribute from each person's retirement accounts.
    for person in family:
        if age(person, year) >= 60:
            person_balance = balances[ret_acct_type][person["name"]]
            person_share = min(amount * (person_balance / all_balances), person_balance)
            print(
                f" - distributing ${int(person_share)} from {person['name']}'s {ret_acct_type} for {why}"
            )
            balances[ret_acct_type][person["name"]] -= person_share
            balances[target_acct] += person_share

def voluntary_distributions(year, balances):
    target_int = distribution_percentage(year)
    target_pct = target_int / 100.0
    why = f"{target_int}% voluntary distribution"

    # Figure out how much we need to distribute from Traditional IRAs
    already_distributed_ira = balances[IRA_WITHDRAWALS]
    total_ira_value = sum(balances[DEFERRED_IRA].values())
    target_ira_distribution = total_ira_value * target_pct
    remaining = target_ira_distribution - already_distributed_ira
    if remaining > 0:
        # Distribute from traditional IRAs to the "IRA Withdrawals" account, which keeps track
        # of how much we've taken out of traditional retirement accounts.  At the end of the
        # cycle, we'll sweep this back into the savings account like normal money.
        move_from_retirement_accounts(year, balances, DEFERRED_IRA, remaining, IRA_WITHDRAWALS, why)

    # Figure out how much we need to distribute from Roth IRAs
    already_distributed_roth = 0
    total_roth_value = sum(balances[EXEMPT_ROTH].values())
    target_roth_distribution = total_roth_value * target_pct
    remaining = target_roth_distribution - already_distributed_roth
    if remaining > 0:
        # Distribute from Roth IRAs directly into savings, since we do not have to pay taxes on it.
        move_from_retirement_accounts(year, balances, EXEMPT_ROTH, remaining, SAVINGS, why)


def calculate_taxes(year, balances):
    taxable_income = balances[TAXED_INC] + balances[IRA_WITHDRAWALS]
    tax = estimate_income_tax(taxable_income)
    print(f" - estimated tax on ${taxable_income:,.0f} income is ${tax:,.0f}")
    # Since it's an expense, we'll record it as a negative number.
    balances[TAX_OWED] = 0 - tax


def sweep_category_accounts_into_savings(year, balances):
    for acct in [EXPENSES, TAXED_INC, UNTAXED_INC, IRA_WITHDRAWALS, TAX_OWED]:
        move_amt = balances[acct]
        if int(abs(move_amt)) > 0:
            print(f" - sweeping ${int(move_amt)} from {acct} into savings")
            balances[SAVINGS] += move_amt


def ensure_minimum_savings_balance(year, balances):
    desired_savings = minimum_savings_balance(year)
    for from_acct, to_acct in [(DEFERRED_IRA, IRA_WITHDRAWALS), (EXEMPT_ROTH, SAVINGS)]:
        if balances[SAVINGS] <= desired_savings:
            # Our savings account is running very low.
            # Pull some from retirement accounts to cover the shortfall.
            shortfall = desired_savings - balances[SAVINGS]
            print(f" - savings came up short by ${int(shortfall)}")
            move_from_retirement_accounts(year, balances, from_acct, shortfall, to_acct, "savings shortfall")
    if balances[SAVINGS] <= 0:
        raise ValueError("Out of money")


def total_value(balances):
    value = balances[SAVINGS]
    for acct in [DEFERRED_IRA, EXEMPT_ROTH]:
        value += sum(balances[acct].values())
    return int(value)


def print_year(year, people, balances):
    line = f"YEAR {year}:"
    for person in people:
        line += f"  {person['name']}: {age(person, year)}  "
    for key, value in balances.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                line += f"  {key} ({subkey}): ${int(subvalue)}"
        else:
            line += f"  {key}: ${int(value)}"
    print(line)


def apply_investment_returns_and_inflation(balances):
    ret_pct = return_percentage()
    inf_pct = inflation_percentage()
    print(f" - investment returns = {ret_pct:.1f}%, inflation = {inf_pct:.1f}%")

    def adjust_account(dic, dicname, dkey, ret, inf):
        before = dic[dkey]
        dic[dkey] *= (1.0 + (ret - inf) / 100.0)
        after = dic[dkey]
        pct = 0
        if before > 0:
            pct = ((after / before) - 1) * 100.0
        print(f" - account {dicname} {dkey} : {int(before)} -> {int(after)} = {pct:.2f}%")

    adjust_account(balances, "shared", SAVINGS, ret_pct, inf_pct)
    for person in family:
        adjust_account(balances[DEFERRED_IRA], "IRA", person["name"], ret_pct, inf_pct)
        adjust_account(balances[EXEMPT_ROTH], "Roth", person["name"], ret_pct, inf_pct)


def single_simulation():
    sim_balances = deepcopy(initial_balances)
    print_year(start_year, family, sim_balances)
    year_totals = [total_value(sim_balances)]

    sim_year = start_year
    try:
        for sim_year in range(start_year, start_year + num_years):
            clear_transient_values(sim_balances)
            # earn income
            job_income(sim_year, sim_balances)
            socsec_income(sim_year, sim_balances)
            # spend money
            budget_expenses(sim_year, sim_balances)
            housing_expenses(sim_year, sim_balances)
            healthcare_expenses(sim_year, sim_balances)
            # other adjustments
            other_one_time_adjustments(sim_year, sim_balances)
            # pull money out of retirement accounts
            required_minimum_distributions(sim_year, family, sim_balances)
            roth_conversions(sim_year, sim_balances)
            voluntary_distributions(sim_year, sim_balances)
            calculate_taxes(sim_year, sim_balances)
            # At this point, we have adjusted all of the accounts to show how money was moved around.
            # But we really need to sweep it all back into actual savings accounts.
            sweep_category_accounts_into_savings(sim_year, sim_balances)
            ensure_minimum_savings_balance(sim_year, sim_balances)
            # last step = capital gains and inflation
            apply_investment_returns_and_inflation(sim_balances)
            print_year(sim_year, family, sim_balances)
            year_totals.append(total_value(sim_balances))
    except ValueError as e:
        print(f"ERROR: {e}")
        print_year(sim_year, family, sim_balances)
        for sim_year in range(sim_year, start_year + num_years):
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
    single_sim_data = single_simulation()
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
