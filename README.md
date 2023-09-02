# Swedish sortition

This is the code for the algorithm used to run the civic lottery of the [first citizens' assembly organised in Sweden](https://digidemlab.org/news/livsmedelsverket-gor-sveriges-forsta-nationella-medborgarpanel-en/).
The process took place in the Spring of 2023 and involved around 60 citizens from the whole country. It was lead by [*Livsmedelsverket*](https://www.livsmedelsverket.se) (the Swedish Food Agency), funded by [Vinnova](https://www.vinnova.se) (the Swedish Innovation Agency) and designed, organised and facilitated by [Digidem Lab](https://digidemlab.org).

## How does this work?

In short, this code draws a random subset of panelists among a given list of people and compares its representativeness to an ideal picture. It does that a high number of times (over a hundred per second on a good computer) and saves the best attempts.

After running it for a few hours, the best solution can be opened as an Excel file to see if it is satisfactory.

The logic of the algorithm is contained in the file [swedish_sortition.py](/swedish_sortition.py) and each line has been thoroughly commented to make it as easy as possible to understand, scrutinise. We want it to be fully transparent for both participants and external observers.

## Prerequisites

To run this script, you'll need Python 3 and to install a number of libraries. You can find them in [requirements.txt](/requirements.txt) and install them with the following command:

```bash
pip install -r requirements.txt
```

## Basic usage

You can first use this code to generate fake data.

```python
from services.fake_data_generator import get_random_people, confirm_certain

# This will generate a list of 1000 fake people with
# charasteristics such as a name, an age, an adress...
fake_people = get_random_people(1000)

# This will add a boolean `is_confirmed` to every person
# and set it to True for 23 of them, False for the others
fake_people = confirm_certain(fake_people, 23)
```

You can also use the `Sortition` class to perform a lottery by generating a high number of potential panels

```python
from swedish_sortition import Sortition
import pandas as pd

people = pd.read_csv('fake_people.csv')

# First, initialise the object with your criteria
# and the desired number of panelists
sortition = Sortition(criteria, 70)

# Then generate a million of potential panels
sortition.generate_samples(1000000, 'lottery', people)
```

This will save the panels as Excel files named *lottery - {score}.xslx* with a lower `score` being better.

The format of the criteria to provide is a dictionary defining how many people should ideally belong to each category of each criterium:

```json
{
    "gender": {
        "values": {
            "man": 35,
            "woman": 35
        },
        "weight": 1
    },
    ...
}
```

You can optionally add a `weight` to give more importance to a criterium in the calculation of the representativeness.

An example of criteria is provided in the [criteria.json.example](/criteria.json.example) and can be loaded using:

```python
with open('criteria.json.example') as f:
    criteria = json.load(f)
```

## Complementary recruitment

If you have already done a lottery but need to complement your panel with additional participants, you can provide the method with two DataFrames:

```python
# This splits the people DataFrame in two, one with the confirmed
# participants, the other one with the new ones to sort from
interested, already_confirmed = [part[1] for part in people.groupby('is_confirmed')]

sortition.generate_samples(1000000, 'complementary_lottery', interested, already_confirmed)
```

## Multiprocessing

In [run_parallel.py](/run_parallel.py), the sortition is run in parallel on all but one of the computer's cores. This can significantly speed up the calculations if you are not running a version of Python that supports multiprocessing out of the box.

## License

This code is licensed as AGPLv3. Feel free to use it and don't hesitate to reach out to help us improve it!
