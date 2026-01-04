"""
This is the beginning of a model where you pick a random starting year and
then get actual market return percentages for each subsequent year.  It's not
really fleshed out into a nice interface yet.  But it works.

What I do is in the __init__() function of my custom Simulation class, I
initialized the "starting point" that I will use.  For example, say 1969.


    def __init__(self, start_year, num_years):
        ...
        self.model_year_start = models.random_starting_year()
        ...

And then when getting the market returns for my simulation year, I just
increment the year using a "modulo add" function, which is kind of weird,
since it just wraps around from 2026 to 1926.

    def return_percentage(self):
        simulation_year_index = self.year - self.start_year
        model_year = models.modulo_add(self.model_year_start, simulation_year_index)
        model_return = models.historical_sp500_returns[model_year]
        print(f"    . using return from {model_year} = {model_return:.1f}")
        return model_return

We can make this a little easier to use later.  But for now, it does run
through the sequences of returns that we have actually seen historically,
rather than just rolling the dice using some randomization function.
"""

import random

# https://www.slickcharts.com/sp500/returns
historical_sp500_returns = {
    1926:     11.62,
    1927:     37.49,
    1928:     43.61,
    1929:     -8.42,
    1930:     -24.90,
    1931:     -43.34,
    1932:     -8.19,
    1933:     53.99,
    1934:     -1.44,
    1935:     47.67,
    1936:     33.92,
    1937:     -35.03,
    1938:     31.12,
    1939:     -0.41,
    1940:     -9.78,
    1941:     -11.59,
    1942:     20.34,
    1943:     25.90,
    1944:     19.75,
    1945:     36.44,
    1946:     -8.07,
    1947:     5.71,
    1948:     5.50,
    1949:     18.79,
    1950:     31.71,
    1951:     24.02,
    1952:     18.37,
    1953:     -0.99,
    1954:     52.62,
    1955:     31.56,
    1956:     6.56,
    1957:     -10.78,
    1958:     43.36,
    1959:     11.96,
    1960:     0.47,
    1961:     26.89,
    1962:     -8.73,
    1963:     22.80,
    1964:     16.48,
    1965:     12.45,
    1966:     -10.06,
    1967:     23.98,
    1968:     11.06,
    1969:     -8.50,
    1970:     4.01,
    1971:     14.31,
    1972:     18.98,
    1973:     -14.66,
    1974:     -26.47,
    1975:     37.20,
    1976:     23.84,
    1977:     -7.18,
    1978:     6.56,
    1979:     18.44,
    1980:     32.42,
    1981:     -4.91,
    1982:     21.55,
    1983:     22.56,
    1984:     6.27,
    1985:     31.73,
    1986:     18.67,
    1987:     5.25,
    1988:     16.61,
    1989:     31.69,
    1990:     -3.10,
    1991:     30.47,
    1992:     7.62,
    1993:     10.08,
    1994:     1.32,
    1995:     37.58,
    1996:     22.96,
    1997:     33.36,
    1998:     28.58,
    1999:     21.04,
    2000:     -9.10,
    2001:     -11.89,
    2002:     -22.10,
    2003:     28.68,
    2004:     10.88,
    2005:     4.91,
    2006:     15.79,
    2007:     5.49,
    2008:     -37.00,
    2009:     26.46,
    2010:     15.06,
    2011:     2.11,
    2012:     16.00,
    2013:     32.39,
    2014:     13.69,
    2015:     1.38,
    2016:     11.96,
    2017:     21.83,
    2018:     -4.38,
    2019:     31.49,
    2020:     18.40,
    2021:     28.71,
    2022:     -18.11,
    2023:     26.29,
    2024:     25.02,
    2025:     17.51,
}

def random_starting_year():
    min_year = min(historical_sp500_returns.keys())
    max_year = max(historical_sp500_returns.keys())
    return random.randrange(min_year, max_year)

def modulo_add(starting_year, offset):
    min_year = min(historical_sp500_returns.keys())
    max_year = max(historical_sp500_returns.keys())
    num_years = max_year - min_year
    year = min_year + (starting_year + offset - min_year) % num_years
    return year

