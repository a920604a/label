#!/usr/bin/env python

import argparse
import os
import datetime
import json


class MergeCocoJsonFile(object):
    def __init__(self, **kwargs):
        # self.input_coco_file = kwargs.get('input_coco_file', None)
        # self.labels = kwargs.get('labels', None)
        self.output_coco_file = kwargs.get('output_coco_file', None)
        self.remove_input = kwargs.get('remove_input', None)

        self.merge_data = self.init_json()

    def read_json(self, coco_file_list):
        json_files = []
        for file in coco_file_list:
            json_file = json.load(open(file))
            json_files.append(json_file)
        return json_files

    def init_json(self):

        now = datetime.datetime.now()

        return dict(
            info=dict(
                description=None,
                url=None,
                version=None,
                year=now.year,
                contributor=None,
                date_created=now.strftime("%Y-%m-%d %H:%M:%S.%f"),
            ),
            licenses=[dict(url=None, id=0, name=None,)],

            images=[
                # license, url, file_name, height, width, date_captured, id
            ],
            type="instances",
            annotations=[
                # segmentation, area, iscrowd, image_id, bbox, category_id, id
            ],
            categories=[
                # supercategory, id, name
            ],
        )

    def merge(self, total_json, label_list, coco_file_list):
        id_class = dict()
        for idx, _type in enumerate(label_list):
            id_class[_type] = idx
            self.merge_data['categories'].append(dict(supercategory='null',
                                                      id=idx,
                                                      name=_type))
        licenses_id = 0
        img_num = []
        ann_num = []
        img_counter = 0
        ann_counter = 0
        file_name_set = set()
        for idx, f in enumerate(total_json):
            if f['type'] != self.merge_data['type']:
                print('type in legal')

        print("id_class", id_class)

        for idx, f in enumerate(total_json):
            category_dic = dict()
            for jj in f['categories']:
                category_dic[jj['id']] = jj['name']
            print("category_dic", category_dic)
            img_num.append(len(f['images']))
            ann_num.append(len(f['annotations']))

            if f['licenses']:
                licenses_id = max(licenses_id, f['licenses'][0]['id'])
            if f['annotations']:
                for ann_info in f['annotations']:
                    _ann_info = dict(
                        id=ann_counter,
                        image_id=ann_info['image_id'] + img_counter,
                        category_id=id_class[category_dic[ann_info['category_id']]],
                        segmentation=ann_info['segmentation'],
                        area=ann_info['area'],
                        bbox=ann_info['bbox'],
                        iscrowd=ann_info['iscrowd']
                    )
                    ann_counter += 1
                    self.merge_data['annotations'].append(_ann_info)
            if f['images']:
                for img_info in f['images']:
                    if img_info['license'] == f['licenses'][0]['id'] and img_info['file_name'] not in file_name_set:
                        _img_info = dict(
                            license=licenses_id,
                            url=img_info['url'],
                            file_name=img_info['file_name'],
                            height=img_info['height'],
                            width=img_info['width'],
                            date_captured=img_info['date_captured'],
                            id=img_counter
                        )
                        self.merge_data['images'].append(_img_info)
                        file_name_set.add(img_info['file_name'])
                        img_counter += 1
                    else:
                        print("file :{} is already exists!!! ",
                              img_info['file_name'])
                        print("please delete from annotations'd image id :{} manually".format(
                            img_counter))
            if img_counter == sum(img_num):
                print('add {} to merge filename'.format(coco_file_list[idx]))

            assert len(self.merge_data['images']) == sum(
                img_num), 'lease check the number of {} images is correct!'.format(coco_file_list[idx])
            assert len(self.merge_data['annotations']) == sum(
                ann_num), 'please check the number of {} annotations is correct!'.format(coco_file_list[idx])

            self.merge_data['licenses'][0]['id'] = licenses_id
            print('Merge {} totally'.format(coco_file_list[idx]))

        return self.merge_data

    def save_json(self, data):
        with open(self.output_coco_file, 'w') as f:
            json.dump(data, f)

    def remove_files(self, file_list):
        if self.remove_input:
            [os.remove(f) for f in file_list]


def default_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--input-coco-file', nargs='+', default=[])
    parser.add_argument("--labels", nargs='+', default=[],
                        help="Check wheather json files' labels is legal ")
    parser.add_argument("--output-coco-file", type=str,
                        default='./merge_trainval.json',
                        help="output json file name")
    parser.add_argument('-r', '--remove-input', action='store_true',
                        help='whether remove input files')
    # file_list = ['./D4-result/trainval.json' , './D7-result/trainval.json' , './D8-result/trainval.json']
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = default_argument_parser()
    print(args)
    merge_obj = MergeCocoJsonFile(
        # input_coco_file=args.input_coco_file,
        # labels=args.labels,
        output_coco_file=args.output_coco_file,
        remove_input=args.remove_input,
    )
    total_json = merge_obj.read_json(args.input_coco_file)

    if len(total_json) != 0:
        merge_data = merge_obj.merge(
            total_json, args.labels, args.input_coco_file)
    else:
        print("please input correct json file!!!!! ")
    merge_obj.save_json(merge_data)
    merge_obj.remove_files(args.input_coco_file)
