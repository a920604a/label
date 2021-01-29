#! /bin/bash
# python3 rename.py -i ./data/images\
#                   -s 0 \
#                   -o ./result \
#                   -r

# python3 split_shuffle_images.py -i ./data/images \
#                                -sp 0.8 \
#                                -ot ./result/train \
#                                -ov ./result/valid \
#                                -r

# python3 merge2coco.py --input-coco-file ./data/result-4/trainval.json ./data/result-7/trainval.json ./data/result-8/trainval.json \
#                       --labels 4 7 8 \
#                       --output-coco-file ./result/merge.json \
#                       -r

python3 label2mask.py  --input-path ./data/images\
                       --output-image-path ./result/Image \
                       --output-mask-path ./result/Mask \
                       --augm-times 50 \
                       --pool-size 80
#                        -r

