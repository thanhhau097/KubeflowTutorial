import argparse

parser = argparse.ArgumentParser(description='Preprocessing data for OCR')
parser.add_argument('--input_path', type=str, help='input path to data path, including training set and validation set')
parser.add_argument('--output_path', type=str, help='path to store text lines and labels')

args = parser.parse_args()

import os
import json
import glob
import cv2
from tqdm import tqdm


def get_data(image_dir, label_dir, save_dir='train', color=True):
    label_files = glob.glob(os.path.join(label_dir, "*"))
    data = list()

    phase_dir = os.path.join(args.output_dir, save_dir)
    text_lines_dir = os.path.join(phase_dir, 'textlines')
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

        with open(os.path.join(phase_dir, 'data.json'), 'w') as f:
            json.dump(data, f)

    print('Parse data for phase {} successfully')


def preprocess(dataset_type='train'):
    """

    :param dataset_type: train/val
    :return:
    """
    # with zipfile.ZipFile(os.path.join(args.input_path, dataset_type + '.zip'), 'r') as zip_ref:
    #     zip_ref.extractall(args.output_path)
    print("start preprocessing data for ocr")
    print(os.listdir(args.input_path))


preprocess()
