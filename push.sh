#!/bin/bash
pip install pipreqs
pipreqs ./ --encoding=utf8 --force
sed -i '/cos_python_sdk_v5==1.9.20/d' requirements.txt
sed -i '/qcloud_cos==3.3.6/d' requirements.txt
req='celery==5.2.7\nredis==4.3.4\nPyJWT==2.4.0\nmatplotlib==3.5.2\ndjango-cors-headers==3.13.0\ndjango-redis==5.2.0\nchannels==3.0.5'
echo -e $req >> requirements.txt
