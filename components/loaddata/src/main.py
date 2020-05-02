"""
Load data from DataPile
"""

import argparse

parser = argparse.ArgumentParser(description='Load data from datapile')
parser.add_argument('--input_path', type=str, help='path to data on datapile')
parser.add_argument('--param', type=int, default=100, help='Parameter 1.')
parser.add_argument('--output_path', type=str, help='output data path, use for other phase')
args = parser.parse_args()


# When making any requests to DataPile, you must include api key to authenticate your request.
# For example: https://datapile.cinnamon.is/api/datasets/list?api_key={your-api-key-here}
# lionel's key: BgTdTI3bB5WtjjsZf-DBoZESQVjQQNghZ_gMGtDYV6o


def load_data():
    """
    Load data from Datapile
    https://datapile.cinnamon.is/api/

    :return:
    """
    print('load data done')
    # write train data to data/train.zip
    # write test data to data/test.zip
    # when declare component:
    # file_outputs={
    #             'train': 'data/train.zip',
    #             'test': 'data/test.zip'
    #         }

load_data()
