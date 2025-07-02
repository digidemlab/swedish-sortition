from services.personnummer_generator import get_random_personnummer, get_age
from random import randint, choice, sample
from pgeocode import Nominatim
from mimesis import Person, Address
from mimesis.locales import Locale

MEDIAN_INCOME = (100000, 600000)
INCOME_INDICATOR = (5, 95)

HOUSING_TYPES = ['apartment', 'house', 'shared', 'other']
EDUCATION_TYPES = ['No education', 'High school', 'University']

def get_random_person():
    fake_person = Person(Locale.SV)

    gender = fake_person.gender_code()
    # In this version, we only support generation of binary people :/
    if gender == 1:
        gender = 'man'
    elif gender == 2:
        gender = 'woman'
    else:
        gender = choice(['man', 'woman'])

    personnummer = get_random_personnummer('19231231', '20080101', gender = gender)

    age = get_age(personnummer)

    age_group = _get_age_group(age, min = 15)

    phone_numbers = []
    for _ in range(0, randint(0, 3)):
        phone_numbers.append(fake_person.telephone())

    address_info = _generate_real_postcode()
    street = Address(Locale.SV).address()
    postcode = address_info.postal_code
    city = address_info.place_name

    address = ' '.join([street, postcode, city])

    housing_type = choice(HOUSING_TYPES)

    area_median_income = randint(MEDIAN_INCOME[0], MEDIAN_INCOME[1])
    income_indicator = (5 + (area_median_income - MEDIAN_INCOME[0]) * (INCOME_INDICATOR[1] - INCOME_INDICATOR[0]) / (MEDIAN_INCOME[1] - MEDIAN_INCOME[0]))

    education = choice(EDUCATION_TYPES)

    return {
            'first_name': fake_person.first_name(),
            'last_name': fake_person.last_name(),
            'personnummer': personnummer,
            'age': age,
            'age_group': age_group,
            'gender': gender,
            'address': address,
            'phone_numbers': phone_numbers,
            'latitude': address_info.latitude,
            'longitude': address_info.longitude,
            'street': street,
            'postcode': postcode,
            'city': city,
            'region': address_info.state_name,
            'housing_type': housing_type,
            'area_median_income': area_median_income,
            'income_indicator': income_indicator,
            'education': education
        }

def get_random_people(amount):
    people = []

    if amount >= 1000:
        one_percent = amount / 1000

    for i in range(0, amount):
        if amount >= 1000 and i % one_percent == 0:
            print(f'Created {i} people so far ({i / (one_percent * 10)}%)')
        people.append(get_random_person())

    print(f'Created {len(people)} people.')
    return people

def confirm_certain(people, amount_to_confirm):
    amount = len(people)
    confirmed_ids = sample(range(amount), amount_to_confirm)

    for i in range(amount):
        people[i]['is_confirmed'] = i in confirmed_ids

    return people

def _generate_real_postcode():
    nomi = Nominatim('SE')
    data = nomi._get_data('SE')[1]

    return data.iloc[randint(0, len(data))]

def _get_age_group(age, min  = 0, max = 75, step = 10):
    if age >= max:
        return f'{max}+'
    else:
        low = ((age - 15) // step) * step + min
        return f'{low}-{low + step - 1}'


