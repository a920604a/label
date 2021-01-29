import argparse
import base64
import json
import os
import os.path as osp
import imgviz
import PIL.Image
from labelme import utils
import numpy as np
import albumentations as A
import multiprocessing
import glob
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


def default_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-path', type=str)
    parser.add_argument('-I', '--output-image-path',  default='./Image')
    parser.add_argument('-M', '--output-mask-path',  default='./Mask')
    parser.add_argument("-a", "--augm-times", type=int,
                        help="augmentation times")
    parser.add_argument("-p", "--pool-size", type=int,
                        help="process pool size")
    parser.add_argument("-r", "--remove-input", action='store_true',
                        help='whether remove input files')
    args = parser.parse_args()
    return args


class Coco():

    def __init__(self, **kwargs):
        self.input_path = kwargs.get('input_path', None)
        self.output_image_path = kwargs.get('output_image_path', None)
        self.output_mask_path = kwargs.get('output_mask_path', None)
        self.aug = kwargs.get('augm_times', None)
        self.pool_size = kwargs.get('pool_size', None)
        self.remove_input = kwargs.get('remove_input', False)
        self.transform = A.Compose([
            # 随机旋转 90°
            A.RandomRotate90(),
            # 水平、垂直或水平和垂直翻转
            A.Flip(),
        ])
        os.makedirs(self.output_image_path, exist_ok=True)
        os.makedirs(self.output_mask_path, exist_ok=True)
        self.json_files_list = self.get_json_files()

    def get_json_files(self, ):
        return glob.glob(osp.join(self.input_path, "*.json"))

    def augument(self, json_path, img, mask, idx):
        transformed = self.transform(image=img, mask=mask)
        transformed_image = transformed['image']
        transformed_mask = transformed['mask']

        PIL.Image.fromarray(transformed_image).save(
            osp.join(self.output_image_path,  osp.basename(json_path)[:-5]+str(idx)+".jpg"))

        PIL.Image.fromarray(transformed_mask).save(
            osp.join(self.output_mask_path, osp.basename(json_path)[:-5]+str(idx)+".png"))
        return idx

    def convert_image_mask(self, json_files):
        for idx, files in enumerate(tqdm(json_files)):

            data = json.load(open(files))

            imageData = data.get("imageData")

            if not imageData:
                imagePath = osp.join(
                    osp.dirname(files), data["imagePath"])
                with open(imagePath, "rb") as f:
                    imageData = f.read()
                    imageData = base64.b64encode(imageData).decode("utf-8")
            img = utils.img_b64_to_arr(imageData)

            label_name_to_value = {"_background_": 0}

            for shape in sorted(data["shapes"], key=lambda x: x["label"]):
                label_name = shape["label"]
                if label_name in label_name_to_value:
                    label_value = label_name_to_value[label_name]
                else:
                    label_value = len(label_name_to_value)
                    label_name_to_value[label_name] = label_value
            lbl, _ = utils.shapes_to_label(
                img.shape, data["shapes"], label_name_to_value
            )
            if lbl.min() >= -1 and lbl.max() < 255:
                PIL.Image.fromarray(img).save(
                    osp.join(self.output_image_path,  osp.basename(files)[:-5]+".jpg"))
                mask = PIL.Image.fromarray((255*lbl).astype(np.uint8), 'L')
                mask.save(
                    osp.join(self.output_mask_path, osp.basename(files)[:-5]+".png"))
                mask = np.array(mask)

                threads = []
                with ThreadPoolExecutor(max_workers=self.pool_size) as pool:
                    for i in range(args.augm_times-1):
                        t = pool.submit(self.augument,
                                        files, img, mask, i)
                        threads.append(t)

                    for th in as_completed(threads):
                        print("Augmented dataset image id:{}".format(th.result()))
                    pool.shutdown()
                # with multiprocessing.Pool(processes=args.pool_size) as pool:
                #     try:
                #         multi_res = [pool.apply_async(augumentation,
                #                                       (_files, out_img_dir,
                #                                        out_mask_dir, img, mask, i)) for i in range(args.augm_times-1)]

                #         pool.close()
                #         pool.join()
                #     except Exception as e:
                #         print(e)

    def remove_files(self, file_list):
        if self.remove_input:
            [os.remove(f) for f in file_list]


if __name__ == '__main__':

    args = default_argument_parser()
    coco = Coco(
        input_path=args.input_path,
        output_image_path=args.output_image_path,
        output_mask_path=args.output_mask_path,
        aug=args.augm_times,
        pool_size=args.pool_size,
        remove_input=args.remove_input,
    )
    # print(coco.json_files_list)
    coco.convert_image_mask(coco.json_files_list)
    coco.remove_files(coco.json_files_list)
