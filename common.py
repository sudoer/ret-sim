
from dateutil import parser

def age(person, year):
    birthday = parser.parse(person["birthday"])
    return year - birthday.year

def spouse(person, family):
    for member in family:
        if member["name"] == person["spouse"]:
            return member
    return None
