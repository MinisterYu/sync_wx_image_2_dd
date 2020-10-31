# -*- coding: gb2312 -*-
# ! /usr/bin/env python

import requests_toolbelt
import requests
import json
import global_config
import db_client


# API 文档：https://doc.sm.ms/
class OSSClient:

    def __init__(self):

        self.logger = global_config.logger
        # 上传接口
        self.url = global_config.MS_BASE_URL
        # token
        self.token = global_config.MS_TOKEN
        # header
        self.headers = global_config.MS_HEADERS

        self.sql = db_client.DBClient()

        self.insert_sql = '''INSERT INTO ms_upload_log(file_id, filename, hash, pic_url, delete_url ,page) 
        VALUES ( '{0}', '{1}', '{2}', '{3}', '{4}', '{5}')
        '''

    def upload(self, file_path):
        file_payload = {
            'format': 'json',
            'smfile': (file_path.split('/')[-1], open(file_path, 'rb'), 'image/jpeg')
        }
        multipartEncoder = requests_toolbelt.MultipartEncoder(file_payload)
        self.headers['Content-Type'] = multipartEncoder.content_type
        try:
            resp = requests.post(self.url + 'upload', headers=self.headers, data=multipartEncoder, timeout=10)
            resp_j = json.loads(resp.text)
            if 200 != resp.status_code:
                raise Exception(resp.text)
            if resp_j['success']:
                self.sql.do_insert(self.insert_sql.format(resp_j['data']['file_id'],
                                                          resp_j['data']['filename'],
                                                          resp_j['data']['hash'],
                                                          resp_j['data']['url'],
                                                          resp_j['data']['delete'],
                                                          resp_j['data']['page']))
                return resp_j['data']['url']
            else:
                if resp_j['code'] == 'image_repeated':
                    self.logger.warning('found repeated pic on oss, url=' + resp_j['images'])
                    return resp_j['images']
            self.logger.error('meet unknown error= ' + resp_j['message'])
            return None
        except Exception as e:
            self.logger.error('meet unknown Exception= ' + e)
            raise Exception(e)
