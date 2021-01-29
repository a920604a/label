import os
import argparse
import shutil
import random
import numpy as np
from rename import ImageOperation


def default_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-path',  type=str,
                        help='where file path store')
    parser.add_argument('-sp', '--split-ratio', type=float,
                        help='train : validation ratio')
    parser.add_argument('-ot', '--output-train-path', type=str,
                        help='where rename files put')
    parser.add_argument('-ov', '--output-val-path', type=str,
                        help='where rename files put')
    parser.add_argument('-r', '--remove-input', action='store_true',
                        help='whether remove input files')
    args = parser.parse_args()
    return args


class SplitDatasets(ImageOperation):
    def __init__(self, **kwargs):
        self.input_path = kwargs.get('input_path', None)
        self.split_ratio = kwargs.get('split_ratio', None)
        self.output_train_path = kwargs.get('output_train_path', None)
        self.output_val_path = kwargs.get('output_val_path', None)
        self.remove_input = kwargs.get('remove_input', None)
        os.makedirs(self.output_train_path, exist_ok=True)
        os.makedirs(self.output_val_path, exist_ok=True)

    def train_dev_split(self, X, Y):
        train_len = int(round(len(X)*self.split_ratio))
        return X[0:train_len], Y[0:train_len], X[train_len:None], Y[train_len:None]

    def shuffle(self, X, Y):
        assert len(X) == len(
            Y), 'check length of {} and length of {}'.format(X, Y)
        X = np.array(X)
        Y = np.array(Y)
        randomize = np.arange(len(X))
        np.random.shuffle(randomize)
        print(randomize)
        return X[randomize], Y[randomize]

    def get_json_files(self, folder):
        # res = []
        # for f in os.listdir(folder):
        #     if f.endswith(".json"):
        #         res.append(os.path.join(folder, f))
        # return res
        return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".json")]

    def get_image_files(self, folder):
        res = []
        for f in os.listdir(folder):
            if(f.endswith(".bmp") or f.endswith(".jpg") or f.endswith(".png") or f.endswith(".jpeg")):
                res.append(os.path.join(folder, f))
        return res

    def get_pair_files(self, folder):
        image_list = self.get_image_files(folder)
        json_list = self.get_json_files(folder)
        image_list = sorted(image_list)
        json_list = sorted(json_list)
        # print(image_list)
        # print(json_list)
        for im, js in zip(image_list, json_list):
            # print( os.path.splitext(os.path.split(im)[1]) )
            # print(os.path.splitext(os.path.split(js)[1]))
            if os.path.splitext(os.path.split(im)[1])[0] != os.path.splitext(os.path.split(js)[1])[0]:
                print('{} could not find {}'.format(im, js))

        return image_list, json_list

    def copy_pair(self, image_list, json_list, out_path):

        dst_image_list = [os.path.join(out_path, os.path.split(f)[
            1]) for f in image_list]
        dst_json_list = [os.path.join(out_path, os.path.split(f)[
            1]) for f in json_list]
        # for im, js in zip(image_list, json_list):

        maps = list(map(self.copy_image_file, image_list, dst_image_list))
        maps = list(map(self.copy_image_file, json_list, dst_json_list))


if __name__ == "__main__":
    args = default_argument_parser()
    print(args)

    dataset_obj = SplitDatasets(
        input_path=args.input_path,
        split_ratio=args.split_ratio,
        output_train_path=args.output_train_path,
        output_val_path=args.output_val_path,
        remove_input=args.remove_input,)
    image_list, json_list = dataset_obj.get_pair_files(args.input_path)

    x, y = dataset_obj.shuffle(image_list, json_list)
    # print(x)
    # print(y)
    x_train, y_train, x_val, y_val = dataset_obj.train_dev_split(x, y)
    print(x_train, y_train, x_val, y_val)

    dataset_obj.copy_pair(x_train, y_train, args.output_train_path)
    dataset_obj.copy_pair(x_val, y_val, args.output_val_path)

    dataset_obj.remove_files(image_list)
    dataset_obj.remove_files(json_list)
