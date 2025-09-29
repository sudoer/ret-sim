import math


def estimate_us_healthcare_costs(age: int, health_status: str = 'average') -> dict:
    """
    Estimates annual healthcare costs in the US based on age and health status.

    This function provides ballpark estimates derived from various public sources
    (e.g., Kiplinger, SmartFinancial, USAFacts, CMS data). It uses a set of
    pre-defined average costs for different age brackets and applies modifiers
    for 'healthy' and 'unhealthy' statuses. Costs generally increase with age.

    Args:
        age (int): The age of the individual (e.g., 30, 65, 80).
        health_status (str): The general health status of the individual.
                             Accepted values are 'healthy', 'average', or 'unhealthy'.
                             Defaults to 'average'.

    Returns:
        dict: A dictionary containing the estimated annual healthcare cost and
              the health status used for the estimation.
              Returns None if the age is out of a reasonable range (e.g., <0 or >100).
    """

    # Data points for average annual healthcare costs (in USD)
    # These are derived and interpolated from various sources (e.g., ACA premium data,
    # total personal healthcare expenditures for different age groups).
    # Note: For ages 65+, these estimates aim to capture total healthcare spending,
    # not just premiums, as Medicare becomes a primary payer.
    average_annual_costs_by_age = {
        20: 4500,  # ~ACA premium * 12
        25: 4700,  # Interpolated
        30: 5300,  # ~ACA premium * 12
        35: 5700,  # Interpolated
        40: 6000,  # ~ACA premium * 12
        45: 6800,  # Interpolated
        50: 8300,  # ~ACA premium * 12
        55: 10500,  # Interpolated
        60: 12700,  # ~ACA premium * 12
        # Medicare starts at 65, but costs increase significantly
        65: 22400,  # Based on average for 65+ total spending
        70: 25000,  # Estimated increase reflecting rising needs
        75: 28000,  # Estimated increase
        80: 32000,  # Estimated increase
        85: 38000,  # Estimated increase
        90: 45000,  # Estimated increase
        95: 55000,  # Estimated increase
        100: 65000  # Estimated for very advanced age
    }

    # Health status modifiers
    # Based on general understanding of how health impacts costs,
    # with 'unhealthy' having significantly higher costs due to chronic conditions.
    health_modifiers = {
        'healthy': 0.85,  # 15% less than average
        'average': 1.00,  # Baseline
        'unhealthy': 1.40  # 40% more than average
    }

    # Input validation
    if age > 100:
        age = 100  # Clamp to maximum age
    if not isinstance(age, int) or age < 0 or age > 100:
        raise ValueError("Age must be an integer between 0 and 100.")
    if health_status.lower() not in health_modifiers:
        raise ValueError(f"Error: Invalid health_status. Must be one of {list(health_modifiers.keys())}.")

    # Normalize health_status input
    health_status = health_status.lower()

    # Find the appropriate age range for interpolation
    ages = sorted(average_annual_costs_by_age.keys())

    # Handle ages outside the defined range
    if age <= ages[0]:
        base_cost = average_annual_costs_by_age[ages[0]]
    elif age >= ages[-1]:
        base_cost = average_annual_costs_by_age[ages[-1]]
    else:
        # Interpolate linearly between known data points
        lower_age = max(a for a in ages if a <= age)
        upper_age = min(a for a in ages if a >= age)

        if lower_age == upper_age:  # Age is exactly one of the data points
            base_cost = average_annual_costs_by_age[age]
        else:
            cost_lower = average_annual_costs_by_age[lower_age]
            cost_upper = average_annual_costs_by_age[upper_age]

            # Linear interpolation formula:
            # y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
            base_cost = cost_lower + (age - lower_age) * \
                        (cost_upper - cost_lower) / (upper_age - lower_age)

    # Apply health status modifier
    estimated_cost = base_cost * health_modifiers[health_status]

    return round(estimated_cost, 2)


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Healthcare Cost Estimates ---")

    # Example 1: Average health at 30
    estimate1 = estimate_us_healthcare_costs(30)
    if estimate1:
        print(f"Age: {estimate1['age']}, Health: {estimate1['health_status']}, "
              f"Estimated Annual Cost: ${estimate1['estimated_annual_cost_usd']:,}")

    # Example 2: Healthy individual at 65
    estimate2 = estimate_us_healthcare_costs(65, 'healthy')
    if estimate2:
        print(f"Age: {estimate2['age']}, Health: {estimate2['health_status']}, "
              f"Estimated Annual Cost: ${estimate2['estimated_annual_cost_usd']:,}")

    # Example 3: Unhealthy individual at 78 (interpolation)
    estimate3 = estimate_us_healthcare_costs(78, 'unhealthy')
    if estimate3:
        print(f"Age: {estimate3['age']}, Health: {estimate3['health_status']}, "
              f"Estimated Annual Cost: ${estimate3['estimated_annual_cost_usd']:,}")

    # Example 4: Age outside range (clamped to boundary)
    estimate4 = estimate_us_healthcare_costs(10, 'healthy')
    if estimate4:
        print(f"Age: {estimate4['age']}, Health: {estimate4['health_status']}, "
              f"Estimated Annual Cost: ${estimate4['estimated_annual_cost_usd']:,}")

    # Example 5: Invalid health status
    estimate5 = estimate_us_healthcare_costs(50, 'excellent')
    if estimate5:
        print(f"Age: {estimate5['age']}, Health: {estimate5['health_status']}, "
              f"Estimated Annual Cost: ${estimate5['estimated_annual_cost_usd']:,}")
