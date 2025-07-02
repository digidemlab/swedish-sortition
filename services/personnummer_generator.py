from itertools import cycle
from random import randrange
from datetime import datetime, timedelta
from datetime import date

def get_random_personnummer(
                        start: str = '19000101',
                        end: str = '20221231',
                        gender : int = 0):
    start = _str_to_date(start)
    end = _str_to_date(end)

    date_numbers = _date_to_str(_random_date(start, end))
    random_two_numbers = "{n:02d}".format(n = randrange(0, 100))
    random_gender_number = _random_int(gender)
    eleven_first_numbers = f'{date_numbers}{random_two_numbers}{random_gender_number}'
    control_number = _luhn(eleven_first_numbers[2:])

    return f'{eleven_first_numbers}{control_number}'

def get_age(personnummer):
    today = date.today()
    birthdate = _str_to_date(personnummer[:8])

    age = today.year - birthdate.year

    # Check if the birthdate has occurred this year
    if today.month < birthdate.month or (today.month == birthdate.month
                                         and today.day < birthdate.day):
        age -= 1

    return age

def _luhn(payload):
    calc = [
        p - 9 if p > 9 else p
        for p in [
            int(n) * m for n, m in zip(reversed(payload), cycle([2, 1]))
        ]
    ]
    s = sum(calc)
    return (10 - s) % 10

def _str_to_date(date_string: str):
    return datetime.strptime(date_string, '%Y%m%d')

def _date_to_str(date: str):
    return datetime.strftime(date, '%Y%m%d')

def _random_int(gender):
    return randrange(1, 10, 2) if gender == 'male' else randrange(0, 10, 2)

def _random_date(start, end):
    delta = end - start
    random_day = randrange(delta.days)
    return start + timedelta(days=random_day)
