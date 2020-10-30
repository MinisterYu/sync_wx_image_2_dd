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
        self.ttk = ttk_client.TTKClient()

        # 初始化本地图片目录
        self.init_folder()

        # 同步后是否删除本地图片
        self.delete_pic = delete_pic

    def init_folder(self):
        if not os.path.exists('./images'):
            os.mkdir('images')

    def connect_db(self):
        # sqlite3 设置
        self.conn = sqlite3.connect(global_config.DB_CONFIG, check_same_thread=False)
        return self.conn

    def dis_connect_db(self):
        self.conn.close()

    def insert_log(self, fake_id, img_id, nick_name, pic_url):
        insert_temp = "INSERT INTO mp_sync_log(fake_id, img_id, nick_name, pic_url ,created_at) VALUES ( '{0}', '{1}', '{2}', '{3}', '{4}')"
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            sql = insert_temp.format(fake_id, img_id, nick_name, pic_url, self.now(False))
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            self.logger.info("insert data:" + sql)
        except Exception as e:
            self.logger.error("isnert data met error:" + e)
            raise e
        finally:
            self.dis_connect_db()

    def search_log(self, **kwargs):
        data_list = []
        search_temp = "SELECT * FROM mp_sync_log where 1 =1 "
        if 'fake_id' in kwargs.keys():
            search_temp += " AND fake_id = '{0}'".format(kwargs.get('fake_id'))
        if 'img_id' in kwargs.keys():
            search_temp += " AND img_id = '{0}'".format(kwargs.get('img_id'))
        if 'nick_name' in kwargs.keys():
            search_temp += " AND nick_name = '{0}'".format(kwargs.get('nick_name'))
        if 'pic_url' in kwargs.keys():
            search_temp += " AND pic_url = '{0}'".format(kwargs.get('pic_url'))
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            self.logger.info("search sql:" + search_temp)
            data = cursor.execute(search_temp)
            for i in data.fetchall():
                data_list.append(i[0])
            cursor.close()
            self.logger.info(("search data count = {0}".format(len(data_list))))
            return data_list
        except Exception as e:
            raise e
        finally:
            self.dis_connect_db()

    def update_log(self, id, pic_url):
        update_temp = "UPDATE mp_sync_log SET pic_url = '{1}' WHERE id = {0}"
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            sql = update_temp.format(id, pic_url)
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            self.logger.info("update data:" + sql)
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

    def run(self):
        items = self.get_imgs_info(self.main_url)
        self.logger.info("found mp images count= {0}".format(len(items)))
        for item in items:
            if 'content' in item:
                self.logger.warn("text type msg ignore")
                continue
            img_id = item.get('id')
            fake_id = item.get('fakeid')
            nick_name = item.get('nick_name')
            self.logger.info("start sync image, info, img_id={0}, send_by={1}".format(img_id, nick_name))

            # 记录校验,微信有记录存在则不继续
            find_img_id = self.search_log(img_id=img_id)
            if (len(find_img_id)):
                self.logger.warn("**job skip** find img_id with rowId ={0}".format(find_img_id))
                continue

            # 保存图片
            pic_path = self.save_image_2_local(img_id)

            # 上传图片
            pic_url = self.ttk.upload_file(pic_path)

            # 记录校验,TTK有记录存在则不继续
            find_pic_url = self.search_log(pic_url=pic_url)
            if (len(find_pic_url)):
                self.logger.warn("**job skip** find pic_url with rowId ={0}".format(find_pic_url))
                continue

            # 发送图片
            self.ding_hook.send_image(pic_url)
            self.logger.info("finished sync image, info, pic_path={0}, pic_path={1}".format(pic_path, pic_url))
            # 结果记录
            self.insert_log(fake_id, img_id, nick_name, pic_url)

            # 删除图片节约空间
            if self.delete_pic:
                os.remove(pic_path)


if __name__ == '__main__':
    te = SyncImg2DingTalk()
    te.run()
