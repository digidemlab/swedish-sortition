import pandas as pd
import numpy as np

class Sortition(object):
    """
    This class contains a number of rules for a lottery process as well as
    methods to do the lottery according to these rules.

    ...

    Attributes
    ----------
    criteria : dict
        the criteria of sortition, should be provided as a dict with the number of
            people expected in each category of each criterium (see example file)
    size : str
        the number of people to be selected
    max_distance : float
        the max distance above which the generated samples shouldn't be considered

    Methods
    -------
    generate_samples()
        The main method of this class, used to generate a large number of samples
        and write the best ones as Excel files.
    """

    def __init__(self, criteria: dict, size: int, max_distance: float = float('inf')):
        """
        Parameters
        ----------
        criteria : dict
            the criteria of sortition, should be provided as a dict with the number of
            people expected in each category of each criterium (see example file)
        size : str
            the number of people to be selected
        max_distance : float
            the max distance above which the generated samples shouldn't be considered
        """
        self.criteria = criteria
        self.size = size
        self.max_distance = max_distance

    def decompose_for_criterium(self, sample: pd.DataFrame, criterium: str):
        """This function computes and returns 4 series of values for a given criterium

        Parameters
        ----------
        - sample : Pandas.DataFrame
            The sample that some of these series are extracted from
        - criterium : str
            The name of the criterium

        Returns
        -------
        - index: Pandas.Series
            the name of all categories in the given criterium, i.e. for gender, index
            would probably contain 'male', 'female' and other options on the spectrum
        - ideal_values: Pandas.Series
            the values for each category in the ideal goal that is defined in the
            class variable `criteria`, i.e. probably [35, 35] if the categories were
            'male' and 'female' and the gender balance was supposed to be 50%/50%
        - values: Pandas.Series
            the values for each category in the actual sample, i.e. could be [38, 32]
            in the example above
        - difference:
            the difference between the two series above, i.e. [3, -3]
            in the example above
        """

        # The index series is easy to get from the criteria object
        index = list(self.criteria[criterium]['values'].keys())

        # Ideal values as well
        ideal_values = pd.Series(self.criteria[criterium]['values'])

        # To get the values for a specific criterium in the sample DataFrame,
        # we use a groupby and count. In case some categories from the index
        # are not represented, they get filled with 0
        values = pd.Series(0, index=index)
        values = values.add(sample.groupby(criterium)[criterium].count(), fill_value=0)

        # To substract the two series, Pandas supports the '-' operator
        difference = values - ideal_values
        difference = difference.fillna(0)

        return index, ideal_values, values, difference

    def distance(self, sample: pd.DataFrame, criterium: str):
        """This function calculates the algorithmic distance between
        the ideal picture and the actual sample for a given criterium

        Parameters
        ----------
        - sample : Pandas.DataFrame
            The sample of people
        - criterium : str
            The name of the criterium

        Returns
        -------
        - distance: float
            the algorithmic distance
        """

        # In this function, we only need the index and difference
        index, _, _, difference = self.decompose_for_criterium(sample, criterium)

        # Puts a threshold on positive differences
        # to avoid penalising excess of individuals in a given criterium
        # difference = difference.clip(upper=1)

        # The distance is calculated as the sum of all absolute values
        # of the difference series, divided by the number of categories
        return np.linalg.norm(difference) / len(index)

    def get_sample(
                self,
                interested: pd.DataFrame,
                already_lotted: pd.DataFrame = pd.DataFrame()):
        """This function generates a random sample of people, combines it with already
        confirmed participants (if they exist) and calculates the distance between
        this total sample and the ideal picture provided in the `criteria` object

        Parameters
        ----------
        - interested : Pandas.DataFrame
            A list of people who haven't confirmed their participation yet
        - already_lotted : Pandas.DataFrame
            A list of people who have already confirmed their participation

        Returns
        -------
        - sample: Pandas.DataFrame
            the generated sample
        - total_distance: float
            the sum of the distance for all criteria, i.e. the quality of the sample
            in terms of representativeness
        """

        # First, we calculate how many more people are needed based on the amount of
        # people desired (size) and already confirmed (already_lotted)
        remainder_size = self.size - len(already_lotted)

        # The DataFrame.sample(size) function provided by Pandas gives us a random
        # subset of rows from the list of interested people
        new_citizens = interested.sample(remainder_size)

        # This new subset is concatenated with the list of people who have already
        # confirmed. Together, they form the sample.
        sample = pd.concat([already_lotted, new_citizens])

        # We start with a total distance of 0
        total_distance = 0

        # And we add the distance calculated for each criterium
        for criterium in self.criteria:
            # In order to give a higher priority to representativeness along certain
            # criteria, it is possible to provide a weight. A criterium with a weight
            # of 2 would be twice as important as one with a weight of 1. If no weight
            # is provided, the default value will be 1.
            weight = self.criteria[criterium].get('weight', 1)

            total_distance += self.distance(sample, criterium) * weight

            # If the total distance is already bigger than desired, the function will
            # end and an empty sample will be returned
            if total_distance >= self.max_distance:
                return pd.DataFrame(), total_distance

        return sample, total_distance

    def write_sample(self, sample: pd.DataFrame, filename: str):
        """This function writes the calculated data to a structured Excel file

        Parameters
        ----------
        - sample : Pandas.DataFrame
            The sample of people
        - filename : str
            The name of the file the data is written in
        """

        writer = pd.ExcelWriter(filename, engine='xlsxwriter')

        # First, the actual sample is written as a first tab
        sample.to_excel(writer, sheet_name='sample', index=False)

        # For each criterium, a tab is created with a table in it
        for criterium in self.criteria:
            _, ideal_val, val, diff = self.decompose_for_criterium(sample, criterium)

            # This table contains four columns. The first one is the index
            comparison = pd.concat([
                # The second one the number of people in the sample per category
                val.rename('what we have'),
                # The third one the number of people in the ideal picture per category
                ideal_val.rename('what we want'),
                # The fourth one the difference between these two
                diff.rename('difference')], axis=1)
            comparison.to_excel(writer, sheet_name=criterium)

        writer.close()

    def generate_samples(
                    self,
                    amount: int,
                    name: str,
                    interested: pd.DataFrame,
                    already_lotted: pd.DataFrame = pd.DataFrame()):
        """This function generates several random samples in a loop and successively
        saves the ones with a shorter distance than the previous best as an Excel file

        Parameters
        ----------
        - amount : int
            The number of samples to generate
        - name : int
            The beginning of the filename
        - interested : Pandas.DataFrame
            A list of people who haven't confirmed their participation yet
        - already_lotted : Pandas.DataFrame
            A list of people who have already confirmed their participation
        """

        # The loop will run as many times as specified by the amount variable
        for i in range(amount):
            # The sample and its distance are provided by create_sample()
            sample, distance = self.get_sample(interested, already_lotted)

            # If the sample is better than the previous best
            if not sample.empty and distance < self.max_distance:
                # Then the max distance is set to this new minimum
                self.max_distance = distance
                print(f'Sample {i + 1} (distance: {self.max_distance})')

                # And the file is written with this distance in the name
                filename = f'{name} - {str(self.max_distance)[:7]}.xlsx'
                self.write_sample(sample, filename)
