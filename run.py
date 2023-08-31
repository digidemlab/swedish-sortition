from services.fake_data_generator import get_random_people, confirm_certain
import services.writer as writer
import json
from swedish_sortition import Sortition
import pandas as pd

AMOUNT_TO_GENERATE = 1000
AMOUNT_CONFIRMED = 17
AMOUNT_TO_SELECT = 70

fake_people = get_random_people(AMOUNT_TO_GENERATE)
fake_people = confirm_certain(fake_people, AMOUNT_CONFIRMED)

writer.write_csv(fake_people, 'fake_people.csv')

df = pd.read_csv('fake_people.csv')

interested, already_confirmed = [part[1] for part in df.groupby('is_confirmed')]

with open('criteria.json.example') as f:
    criteria = json.load(f)

sortition = Sortition(criteria, AMOUNT_TO_SELECT)
sortition.generate_samples(1000000, 'lottning', interested, already_confirmed)
