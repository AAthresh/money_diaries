import os
import pandas as pd
import re
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent='basic_analysis')
pd.options.mode.chained_assignment = None


class Transform:
    """
    Transformer
    """

    def __init__(self):
        self.header = 'raw_header.json'
        self.diary = 'raw_diaries.json'

        self.data_source = '/'.join([os.getcwd(), 'data'])

    def execute(self):
        """

        :return:
        """
        self.transform_header()

    def transform_header(self):
        """

        :return:
        """
        header_df = pd.read_json('/'.join([self.data_source, self.header]))
        header_df = header_df.T

        header_df['Salary'] = header_df['Salary'].combine_first(header_df['My Income'])
        header_df['Occupation'] = header_df['Occupation'].combine_first(header_df['Industry'])
        basic_df = header_df[['Occupation', 'Age', 'Location', 'Salary']]

        basic_df['Income'] = basic_df['Salary'].apply(lambda x: self.normalize_income(x))
        basic_df['Age'] = basic_df['Age'].apply(lambda x: self.normalize_age(x))
        basic_df[['lat', 'long']] = basic_df['Location'].apply(lambda x: pd.Series(self.get_coordinates(x)))

        # TODO : Losing about 400 diaries
        basic_df = basic_df.dropna()
        final_df = basic_df[['Occupation', 'Age', 'Location', 'Income', 'lat', 'long']]

        result_dataset = '/'.join([self.data_source, 'header.csv'])
        final_df.to_csv(result_dataset, encoding='utf-8')
        print(f'Transformed header succesfully')

    @staticmethod
    def normalize_income(x):
        """

        :return:
        """
        match = re.findall(r'\d+,\d+', str(x))
        y = 0
        if match:
            y = int(match[0].replace(',', ''))
        return y

    @staticmethod
    def normalize_age(x):
        """

        :return:
        """
        match = re.findall(r'\d+', str(x))
        y = 0
        if match:
            y = int(match[0])
        return y

    @staticmethod
    def get_coordinates(x):
        """

        :return:
        """
        location = geolocator.geocode(x)
        lat = long = None
        if location is not None:
            lat = location.latitude
            long = location.longitude

        return lat, long

    def transform_body(self):
        return


def main():
    """

    :return:
    """
    transform = Transform()
    transform.execute()


if __name__ == '__main__':
    main()
