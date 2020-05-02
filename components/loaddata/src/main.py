"""
Load data from DataPile
"""

import os
import argparse
import zipfile

import boto3


parser = argparse.ArgumentParser(description='Load data from datapile')
parser.add_argument('--input_path', type=str, help='path to data on datapile')
parser.add_argument('--param', type=int, default=100, help='Parameter 1.')
parser.add_argument('--output_path', type=str, help='output data path, use for other phase')
args = parser.parse_args()


# When making any requests to DataPile, you must include api key to authenticate your request.
# For example: https://datapile.cinnamon.is/api/datasets/list?api_key={your-api-key-here}
# lionel's key: BgTdTI3bB5WtjjsZf-DBoZESQVjQQNghZ_gMGtDYV6o


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def load_data():
    """
    Load data from Datapile
    https://datapile.cinnamon.is/api/

    :return:
    """
    file_name = 'data.zip'

    s3 = boto3.client('s3')
    s3.download_file('scsk-data', 'lionel/daiichi4/daiichi.zip', file_name)

    # unzip to data folders
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall('./data/')

    # current directory have train/, val/, test/ folder
    data_folder = './data'
    for folder in os.listdir(data_folder):
        with zipfile.ZipFile(os.path.join(data_folder, folder + '.zip'), 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipdir(folder, zipf)

    print('load data done')
    # write train data to data/train.zip
    # write test data to data/test.zip
    # when declare component:
    # file_outputs={
    #             'train': 'data/train.zip',
    #             'val': 'data/val.zip'
    #             'test': 'data/test.zip'
    #         }


load_data()
