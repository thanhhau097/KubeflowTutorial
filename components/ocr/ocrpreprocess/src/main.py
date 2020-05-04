import argparse
import glob
import json
import logging
import os
import zipfile
from pathlib import Path

import boto3
import cv2
from botocore.exceptions import ClientError
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Preprocessing data for OCR')
parser.add_argument('--aws_access_key_id', type=str, required=True, help='AWS_ACCESS_KEY')
parser.add_argument('--aws_secret_access_key', type=str, required=True, help='AWS_SECRET_KEY')
parser.add_argument('--data_path', type=str,
                    help='input path to data path, including training set and validation set')
parser.add_argument('--output_path', type=str, help='path to store text lines and labels')

parser.add_argument('--output_path_file', type=str,
                    help='Path to a local file containing the output model URI. Needed for data passing until the artifact support is checked in.')  # TODO: Remove after the team agrees to let me check in artifact support.
args = parser.parse_args()


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


def download_file(s3_path, file_name):
    bucket = s3_path[:s3_path.find('/')]
    object_name = s3_path[s3_path.find('/') + 1:]
    s3 = boto3.client('s3')
    s3.download_file(bucket, object_name, file_name)


def init_aws_key():
    os.environ['AWS_ACCESS_KEY_ID'] = args.aws_access_key_id
    os.environ['AWS_SECRET_ACCESS_KEY'] = args.aws_secret_access_key


def get_data(image_dir, label_dir, save_dir, color=True):
    label_files = glob.glob(os.path.join(label_dir, "*"))
    data = list()

    text_lines_dir = os.path.join(save_dir, 'textlines')
    if not os.path.exists(text_lines_dir):
        os.makedirs(text_lines_dir)

    for label_path in tqdm(label_files):
        with open(label_path, encoding='utf-8') as f:
            data_dict = json.load(f)
            image_name = data_dict.get("file_name", None)
            attributes = data_dict.get("attributes", None)

            if image_name is None or attributes is None:
                continue

            if color == True:
                image = cv2.imread(os.path.join(image_dir, image_name), cv2.IMREAD_COLOR)
            else:
                image = cv2.imread(os.path.join(image_dir, image_name), cv2.IMREAD_GRAYSCALE)

            _via_img_metadata = attributes.get("_via_img_metadata", None)
            if _via_img_metadata is None:
                continue
            regions = _via_img_metadata.get("regions", None)
            if regions is None:
                continue

            for i, r in enumerate(regions):
                shape_attributes = r.get("shape_attributes", None)
                region_attributes = r.get("region_attributes", None)
                if shape_attributes is None or region_attributes is None:
                    continue

                x = shape_attributes.get("x", None)
                y = shape_attributes.get("y", None)
                width = shape_attributes.get("width", None)
                height = shape_attributes.get("height", None)
                label = region_attributes.get("label", None)

                if any(v is None for v in [x, y, width, height]):
                    continue

                img_cell = image[y: y + height, x: x + width]

                image_name = os.path.join(text_lines_dir, label_path.split('.')[0] + '_' + str(i) + '.png')
                cv2.imwrite(image_name, img_cell)

                data.append({'image': image_name, 'label': label})

        with open(os.path.join(save_dir, 'data.json'), 'w') as f:
            json.dump(data, f)

    print('Parse data for phase {} successfully')
    return


def preprocess(root_folder, dataset_type):
    """

    :param dataset_type: train/val
    :return:
    """
    print("preprocess for {}".format(dataset_type))
    images_folder = os.path.join(root_folder, dataset_type, 'images')
    labels_folder = os.path.join(root_folder, dataset_type, 'images')
    get_data(images_folder, labels_folder, save_dir=dataset_type)


def process():
    print("Init AWS Key")
    init_aws_key()

    file_name = 'data.zip'
    unzip_folder = 'data'

    print("Downloading data from s3")
    download_file(args.data_path, file_name)

    print("Unzip files ...")
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(unzip_folder)

    print("start preprocessing data for ocr")
    for folder in os.listdir(unzip_folder):
        preprocess(unzip_folder, dataset_type=folder)

    # zip folder and upload
    print("Zip folder and upload to s3")
    # current directory have train/, val/, test/ folder
    with zipfile.ZipFile(unzip_folder + '.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(unzip_folder, zipf)
    print("Uploading data to s3")
    bucket = args.output_path[:args.output_path.find('/')]
    object_name = args.output_path[args.output_path.find('/') + 1:]
    upload_file(unzip_folder + '.zip', bucket, object_name)
    print("Upload successfully")

    Path(args.output_path_file).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_path_file).write_text(args.output_path)


process()
