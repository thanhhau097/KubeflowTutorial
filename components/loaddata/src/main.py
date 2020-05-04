"""
Load data from DataPile
"""

import argparse
import logging
import os
import zipfile
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

parser = argparse.ArgumentParser(description='Load data from datapile')
parser.add_argument('--aws_access_key_id', type=str, required=True, help='AWS_ACCESS_KEY')
parser.add_argument('--aws_secret_access_key', type=str, required=True, help='AWS_SECRET_KEY')
# TODO: not sure that can output a folder, need to check
# otherwise, we should return list of file, one param for each file
parser.add_argument('--output_path', type=str, help='output data path, use for other phase')

parser.add_argument('--output_path_file', type=str, help='Path to a local file containing the output model URI. Needed for data passing until the artifact support is checked in.') #TODO: Remove after the team agrees to let me check in artifact support.
args = parser.parse_args()


# When making any requests to DataPile, you must include api key to authenticate your request.
# For example: https://datapile.cinnamon.is/api/datasets/list?api_key={your-api-key-here}
# lionel's key: BgTdTI3bB5WtjjsZf-DBoZESQVjQQNghZ_gMGtDYV6o


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def init_aws_key():
    os.environ['AWS_ACCESS_KEY_ID'] = args.aws_access_key_id
    os.environ['AWS_SECRET_ACCESS_KEY'] = args.aws_secret_access_key


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
    data_folder = 'data'
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(data_folder)

    # current directory have train/, val/, test/ folder
    with zipfile.ZipFile(data_folder + '.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(data_folder, zipf)

    # push to s3
    print("Uploading data to s3")
    bucket = args.output_path[:args.output_path.find('/')]
    object_name = args.output_path[args.output_path.find('/') + 1:]
    upload_file(data_folder + '.zip', bucket, object_name)
    print("Uploaded")

    # for folder in os.listdir(data_folder):
    #     with zipfile.ZipFile(os.path.join(data_folder, folder + '.zip'), 'w', zipfile.ZIP_DEFLATED) as zipf:
    #         zipdir(folder, zipf)

    print('load data done')
    # write train data to data/train.zip
    # write test data to data/test.zip
    # when declare component:
    # file_outputs={
    #             'train': 'data/train.zip',
    #             'val': 'data/val.zip'
    #             'test': 'data/test.zip'
    #         }
    Path(args.output_path_file).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_path_file).write_text(args.output_path)


def process():
    init_aws_key()
    load_data()


process()
