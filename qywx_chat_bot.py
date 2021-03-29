#! /usr/bin/env python
# coding:utf-8
import requests
import base64
import hashlib

def send_images(path, token):
    # 图片base64码
    with open(path, "rb") as f:
        base64_data = base64.b64encode(f.read())
        md = hashlib.md5()
        md.update(f.read())
        md5_ = md.hexdigest()

    # 企业微信机器人发送消息
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + token
    headers = {"Content-Type": "application/json"}
    data = {
        "msgtype": "image",
        "image": {
            "base64": base64_data,
            "md5": md5_
        }
    }
    r = requests.post(url, headers=headers, json=data)
