
from dateutil import parser

def age(person, year):
    birthday = parser.parse(person["birthday"])
    return year - birthday.year

