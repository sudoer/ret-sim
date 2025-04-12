#!/usr/bin/env python3
# ENTRY POINT - FOR RUNNING THE SIMULATOR

import argparse
import datetime
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()
parser.add_argument("--simulation", default="example", help="simulation module, contains a class called Simulation")
parser.add_argument("--runs", type=int, default=100, help="number of simulations")
parser.add_argument("--years", type=int, default=50, help="number of years")
parser.add_argument("--debug", default=False, action="store_true", help="print more output")

args = parser.parse_args()


start_year = datetime.date.today().year
num_years = args.years
year_array = range(start_year, start_year + num_years + 1)
num_runs = args.runs
successes = [0] * (num_years + 1)

# Import the custom simulator class based on the command line argument
simulation_module = __import__(args.simulation)

for run_num in range(num_runs):
    print(f"SIMULATION {run_num + 1}")
    this_sim = simulation_module.Simulation(start_year, num_years)
    if args.debug:
        this_sim.debug = True
    print(f"starting {this_sim}")
    single_sim_data = this_sim.single_simulation()
    plt.plot(year_array, single_sim_data, marker=None, linestyle=None)

    # calculate successes - in this one run, did my money last X years?
    for year in year_array:
        if single_sim_data[year - start_year] > 0:
            successes[year - start_year] += 1

for year in range(start_year, start_year + num_years + 1, 5):
    print(f"{year}, {100 * successes[year - start_year] / num_runs : .1f} %")

# plt.title("My Plot")
plt.xlabel("years")
plt.ylabel("money")
plt.ylim(bottom=0, top=5_000_000)

# Format the y-axis (money) to prevent scientific notation
plt.ticklabel_format(axis='y', style='plain')
# Optionally, format the x-axis (years) as well
plt.ticklabel_format(axis='x', style='plain')

plt.show()
