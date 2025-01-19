
# retirement simulator

This is a simple simulator that runs through a series of "years" and adjusts balances of
savings and retirement accounts to see how long they will last under different conditions
and "loads".  It is designed so it could be run multiple times, perhaps in a Monte Carlo
simulation.

## set up environment
* create a virtual environment `python -m venv .venv`
* use it in your shell `source .venv/bin/activate`
* install dependencies `pip install -r requirements.txt`

## customize your simulation
* copy `custom-example.py` to `custom.py`
* edit the values in the family structure
* edit the values in the initial_balances structure
* edit the functions for rates and stuff

## run application
* run `python simulator.py`
* or get just the summaries with "grep" `python simulator.py | grep YEAR`

## how it works
* The "balances" represent pools of money.  Some are real accounts and some are
  money that is earmarked for a particular purpose for the year.  For example, the
  "ira_withdrawals" balance is money that was withdrawn from an IRA, and thus adds
  to the taxable income for the year, but can be spent on stuff.
* At the end of the cycle, these piles of money (and "negative money" like taxes
  and expenses) are all rolled back into the "savings" balance, which acts as a
  pool of savings and investment accounts.  It's just money.
* The "ira" and "roth" buckets are subdivided into one for each member of the
  family, since each person contributes to them individually.  But when we ask for
  money from those accounts, we just spread the ask among available accounts.


