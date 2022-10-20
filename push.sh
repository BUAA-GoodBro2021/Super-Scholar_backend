#!/bin/bash
pip install pipreqs
pipreqs ./ --encoding=utf8 --force
sed -i '/qcloud_cos==3.3.6/d' requirements.txt