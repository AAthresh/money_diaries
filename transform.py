import os
import pandas as pd


class Transform:
    """
    Transformer
    """

    def __init__(self):
        self.file = 'raw_data.json'
        self.data_source = '/'.join([os.getcwd(), 'data'])
        self.df = pd.read_json('/'.join([self.data_source, self.file]))

    def execute(self):
        """

        :return:
        """
