# -*- coding: gb2312 -*-
# ! /usr/bin/env python

import requests_toolbelt
import requests
import json
import global_config


class TTKClient:

    def __init__(self):
        # 上传接口
        self.url = global_config.TTK_URL
        # token
        self.token = global_config.TTK_TOKEN
        # header
        self.headers = global_config.TTK_HEADERS

    def upload_file(self, file_path):
        file_payload = {
            'Token': self.token,
            'file': (file_path.split('/')[-1], open(file_path, 'rb'), 'image/jpeg')
        }
        multipartEncoder = requests_toolbelt.MultipartEncoder(file_payload)
        self.headers['Content-Type'] = multipartEncoder.content_type
        resp = requests.post(self.url, headers=self.headers, data=multipartEncoder, timeout=10)
        resp_j = json.loads(resp.text)
        if resp_j and 'code' in resp_j:
            raise Exception('error code <{0}>: {1}'.format(resp_j['code'], resp_j['info']))
        return resp_j['linkurl']
