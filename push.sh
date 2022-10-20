#!/bin/bash
pip install pipreqs
pipreqs ./ --encoding=utf8 --force
sed -i '/cos_python_sdk_v5==1.9.20/d' requirements.txt
sed -i '/qcloud_cos==3.3.6/d' requirements.txt