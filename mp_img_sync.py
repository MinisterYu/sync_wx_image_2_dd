# -*- coding: gb2312 -*-
# ! /usr/bin/env python
import requests
import re
import json
import time
import sqlite3
import os
import ding_chat_bot
import ttk_client
import global_config
import base64
import hashlib
import sys


class SyncImg2DingTalk:

    def __init__(self, delete_pic=False):
        self.logger = global_config.logger

        # 微信公众号后台设置
        self.main_url = global_config.MP_URL
        self.headers = global_config.MP_HEADERS
        self.img_url_temp = 'https://mp.weixin.qq.com/cgi-bin/getimgdata?token=' + global_config.MP_TOKEN + '&msgid={0}&mode=small&source=&fileId=0&ow=-1'

        # ding hook 设置
        self.ding_hook = ding_chat_bot.DingtalkChatbot()

        # 贴图库 设置
        self.oss = ttk_client.TTKClient()

        # 同步后是否删除本地图片
        self.delete_pic = delete_pic

        # 本地缓存加速
        self.cache = {}

        # 初始化本地图片目录
        self.init_folder()

        # 初始化缓存
        self.init_cache()

    def init_cache(self):
        search_temp = "SELECT id, img_id, encode FROM mp_sync_log  "
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            data = cursor.execute(search_temp)
            for i in data.fetchall():
                self.cache[i[1]] = i[2]
            cursor.close()
        except Exception as e:
            raise e
        finally:
            self.dis_connect_db()

    def init_folder(self):
        if not os.path.exists('./images'):
            os.mkdir('images')

    def connect_db(self):
        # sqlite3 设置
        self.conn = sqlite3.connect(global_config.DB_CONFIG, check_same_thread=False)
        return self.conn

    def dis_connect_db(self):
        self.conn.close()

    def insert_log(self, fake_id, img_id, nick_name, pic_url, encode):
        insert_temp = "INSERT INTO mp_sync_log(fake_id, img_id, nick_name, pic_url, encode ,created_at) VALUES ( '{0}', '{1}', '{2}', '{3}', '{4}', '{5}')"
        try:
            sql = insert_temp.format(fake_id, img_id, nick_name, pic_url, encode, self.now(False))
            self.logger.info("insert sql:" + sql)
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            self.cache[img_id] = encode
            self.logger.warning(
                "send new img successfully, img_id = {1}, cache was updated! size = {0} bytes"
                    .format(sys.getsizeof(self.cache), img_id))
        except Exception as e:
            self.logger.error("insert data met error:" + e)
            raise e
        finally:
            self.dis_connect_db()

    def is_exist(self, **kwargs):

        if 'img_id' in kwargs.keys() and str(kwargs.get('img_id')) in self.cache.keys():
            return True

        if 'encode' in kwargs.keys() and kwargs.get('encode') in self.cache.keys():
            return True

        search_temp = "SELECT id, img_id, encode FROM mp_sync_log where 1 =1 "

        if 'img_id' in kwargs.keys():
            search_temp += " AND img_id = '{0}'".format(kwargs.get('img_id'))
        if 'encode' in kwargs.keys():
            search_temp += " AND encode = '{0}'".format(kwargs.get('encode'))
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            self.logger.info("search sql:" + search_temp)
            data = cursor.execute(search_temp)
            found = True if len(data.fetchall()) else False
            cursor.close()
            return found
        except Exception as e:
            raise e
        finally:
            self.dis_connect_db()

    def update_log(self, img_id, pic_url):
        update_temp = "UPDATE mp_sync_log SET pic_url = '{1}' WHERE img_id = {0}"
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            sql = update_temp.format(img_id, pic_url)
            self.logger.info("update sql:" + sql)
            cursor.execute(sql)
            conn.commit()
            cursor.close()
        except Exception as e:
            self.logger.error("update data met error:" + e)
            raise e
        finally:
            self.dis_connect_db()

    def load_image_from_mp(self, img_id):
        pic_url = self.img_url_temp.format(img_id)
        self.logger.info("get pic from url={0}".format(pic_url))
        response = requests.get(pic_url, headers=self.headers)
        data = response.content
        return data

    def save_image_2_local(self, img_id):
        data = self.load_image_from_mp(img_id)
        folder = './images/{0}'.format(self.now(True))
        if not os.path.exists(folder):
            os.mkdir(folder)
        file_path = folder + '/{0}.jpeg'.format(img_id)
        with open(file_path, 'wb') as fb:
            fb.write(data)
        return file_path

    def get_imgs_info(self, url):
        page_content = requests.get(url, headers=self.headers)
        match = re.search('(?<=msg_item":).*?(?=}\)\.msg_item)', page_content.text)
        img_data_json = json.loads(match.group())
        return img_data_json

    def now(self, is_date=True):
        if is_date:
            return time.strftime("%Y-%m-%d", time.localtime())
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def encode_file(self, file_path):
        m = hashlib.md5()
        with open(file_path, 'rb') as f:
            b641 = base64.b64encode(f.read())
            return hashlib.md5(b641.decode().encode('utf-8')).hexdigest()

    def run(self):
        items = self.get_imgs_info(self.main_url)
        # self.logger.info("found mp images count= {0}".format(len(items)))
        for item in items:
            self.logger.info("-*-" * 20 + '\n')
            if 'content' in item:
                self.logger.info("** syn skip ** 'text' type msg ignore")
                continue
            img_id = item.get('id')
            fake_id = item.get('fakeid')
            nick_name = item.get('nick_name')
            self.logger.info("start sync image: img_id={0}, send_by={1}".format(img_id, nick_name))

            # 记录校验,微信有记录存在则不继续
            if (self.is_exist(img_id=img_id)):
                self.logger.info("sync process skipped,  find img_id  = {0} in sync_log".format(img_id))
                continue

            # 保存图片
            pic_path = self.save_image_2_local(img_id)

            # 记录校验,本地表情存在则不继续
            encode_ = self.encode_file(pic_path)
            if (self.is_exist(encode=encode_)):
                self.logger.info(
                    "found collision when try to save img, img_id = {1},  md5 value = {0}".format(encode_, img_id))
                os.remove(pic_path)
                continue

            # 上传图片
            pic_url = self.oss.upload_file(pic_path)
            # 发送图片
            self.ding_hook.send_image(pic_url)
            self.logger.info("finished sync image, info, pic_path={0}, pic_path={1}".format(pic_path, pic_url))
            # 结果记录
            self.insert_log(fake_id, img_id, nick_name, pic_url, encode_)

            # 删除图片节约空间
            if self.delete_pic:
                os.remove(pic_path)


if __name__ == '__main__':
    sy = SyncImg2DingTalk()
    # print(sy.encode_file('./images/2020-10-31/500616174.jpeg'))
    # print(sy.encode_file('./images/2020-10-31/500616174.jpeg'))
    # print(sy.encode_file('./images/2020-10-31/500616174.jpeg'))
    # print(sy.search_log(base64=sy.encode_file('./images/2020-10-31/500616174.jpeg')))
    sy.run()
