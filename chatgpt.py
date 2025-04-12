import random


# These functions were generated by OpenAI's GPT-3 model.
# They are not meant to be comprehensive, but just "good enough" for estimates.

def estimate_income_tax(income):
    """
    Estimate U.S. federal income tax owed based on taxable income for single filers (2023 brackets).

    Parameters:
        income (float): Taxable income in dollars.

    Returns:
        float: Estimated federal income tax.
    """
    # 2023 Federal income tax brackets for single filers
    brackets = [
        (0, 11_000, 0.10),  # 10% on income up to $11,000
        (11_001, 44_725, 0.12),  # 12% on income from $11,001 to $44,725
        (44_726, 95_375, 0.22),  # 22% on income from $44,726 to $95,375
        (95_376, 182_100, 0.24),  # 24% on income from $95,376 to $182,100
        (182_101, 231_250, 0.32),  # 32% on income from $182,101 to $231,250
        (231_251, 578_125, 0.35),  # 35% on income from $231,251 to $578,125
        (578_126, float("inf"), 0.37),  # 37% on income over $578,125
    ]

    tax_owed = 0.0

    for lower, upper, rate in brackets:
        if income > lower:
            taxable_amount = min(income, upper) - lower
            tax_owed += taxable_amount * rate
        else:
            break

    return round(tax_owed, 2)


def calculate_rmd(account_balance, age):
    """
    Calculate the Required Minimum Distribution (RMD) for an IRA.

    Parameters:
        account_balance (float): The total balance in the IRA at the end of the previous year.
        age (int): The account holder's age as of December 31 of the current year.

    Returns:
        float: The estimated RMD for the given age and account balance.
    """
    # Uniform Lifetime Table divisor values
    uniform_lifetime_table = {
        72: 25.6,
        73: 24.7,
        74: 23.8,
        75: 22.9,
        76: 22.0,
        77: 21.2,
        78: 20.3,
        79: 19.5,
        80: 18.7,
        81: 17.9,
        82: 17.1,
        83: 16.3,
        84: 15.5,
        85: 14.8,
        86: 14.1,
        87: 13.4,
        88: 12.7,
        89: 12.0,
        90: 11.4,
        91: 10.8,
        92: 10.2,
        93: 9.6,
        94: 9.1,
        95: 8.6,
        96: 8.1,
        97: 7.6,
        98: 7.1,
        99: 6.7,
        100: 6.3,
        101: 5.9,
        102: 5.5,
        103: 5.2,
        104: 4.9,
        105: 4.5,
        106: 4.2,
        107: 3.9,
        108: 3.7,
        109: 3.4,
        110: 3.1,
        111: 2.9,
        112: 2.6,
        113: 2.4,
        114: 2.1,
        115: 1.9,
    }

    # Check if age is in the table
    if age not in uniform_lifetime_table:
        raise ValueError("Age must be between 72 and 115 to calculate RMD.")

    # Get the divisor for the given age
    divisor = uniform_lifetime_table[age]

    # Calculate RMD
    rmd = account_balance / divisor
    return rmd


def random_inflation(mean=3.0, std_dev=2.0, min_value=-2.0, max_value=15.0):
    """
    Generate a random-like inflation value in line with historical trends.

    Parameters:
        mean (float): The average inflation rate (default is 3.0%).
        std_dev (float): The standard deviation for variability (default is 2.0%).
        min_value (float): The minimum inflation rate allowed (default is -2.0%).
        max_value (float): The maximum inflation rate allowed (default is 15.0%).

    Returns:
        float: A random inflation rate, constrained to the given range.
    """
    while True:
        # Generate a value from a normal distribution
        inflation = random.gauss(mean, std_dev)
        # Constrain the value to the specified range
        if min_value <= inflation <= max_value:
            return round(inflation, 2)


def get_full_retirement_age(birth_year: int) -> float:
    """
    Calculate the Full Retirement Age (FRA) for Social Security based on birth year.
    :param birth_year: Year of birth (integer)
    :return: FRA as a floating-point number (years.months/12)
    """
    if birth_year <= 1937:
        return 65.0
    elif 1938 <= birth_year <= 1942:
        months = (birth_year - 1937) * 2
        return 65 + months / 12
    elif 1943 <= birth_year <= 1954:
        return 66.0
    elif 1955 <= birth_year <= 1959:
        months = (birth_year - 1954) * 2
        return 66 + months / 12
    elif birth_year >= 1960:
        return 67.0
    else:
        raise ValueError("Invalid birth year")

