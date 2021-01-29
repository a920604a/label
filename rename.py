import os
import argparse
import shutil


def default_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-path',  type=str,
                        help='where file path store')
    parser.add_argument('-s', '--start_index', type=int,
                        help='begin file name')
    parser.add_argument('-o', '--output-path', type=str,
                        help='where rename files put')
    parser.add_argument('-r', '--remove-input', action='store_true',
                        help='whether remove input files')
    args = parser.parse_args()
    return args


class ImageOperation:
    def __init__(self, **kwargs):
        self.input_path = kwargs.get('input_path', None)
        self.start_index = kwargs.get('start_index', None)
        self.output_path = kwargs.get('output_path', None)
        self.remove_input = kwargs.get('remove_input', None)
        # self.platform = platform.system()
        os.makedirs(self.output_path, exist_ok=True)

    def get_image_files(self, file_list):
        image_files = []
        for root, _, files in os.walk(file_list):
            for f in files:
                if(f.endswith(".bmp") or f.endswith(".jpg") or f.endswith(".png") or f.endswith(".jpeg")):
                    image_files.append(os.path.join(root, f))
        return image_files

    def copy_image_file(self, src, dst):
        shutil.copy(src, dst)

    def copy_image_files(self, file_list):
        # for f in files_list:
        #     self.copy_image_file(f, os.path.join(
        #         self.output_path, os.path.split(f)[1]))

        dst_list = [os.path.join(self.output_path, os.path.split(f)[
                                 1]) for f in file_list]
        maps = list(map(self.copy_image_file, file_list, dst_list))

    def rename_image_fiels(self, file_list):
        for c, f in enumerate(file_list):
            dst_file_name = os.path.join(self.output_path, '{:07d}{}'.format(
                self.start_index+c, os.path.splitext(f)[1]))
            os.rename(f, dst_file_name)

    def remove_files(self, file_list):
        if self.remove_input:
            [os.remove(f) for f in file_list]


if __name__ == '__main__':
    args = default_argument_parser()
    image_obj = ImageOperation(input_path=args.input_path,
                               output_path=args.output_path,
                               start_index=args.start_index,
                               remove_input=args.remove_input
                               )
    image_files = image_obj.get_image_files(args.input_path)
    print('length of image list', len(image_files))
    image_obj.copy_image_files(image_files)
    output_files = image_obj.get_image_files(args.output_path)
    print("number of output_files", len(output_files))
    image_obj.rename_image_fiels(output_files)
    image_obj.remove_image_files(image_files)
