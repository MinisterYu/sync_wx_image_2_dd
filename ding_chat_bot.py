# -*- coding: gb2312 -*-
# ! /usr/bin/env python

import re
import sys
import json
import time
import logging
import requests
import urllib
import hmac
import base64
import hashlib
import queue
import global_config

_ver = sys.version_info
is_py3 = (_ver[0] == 3)

try:
    quote_plus = urllib.parse.quote_plus
except AttributeError:
    quote_plus = urllib.quote_plus

try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError


def is_not_null_and_blank_str(content):
    """
    �ǿ��ַ���
    :param content: �ַ���
    :return: �ǿ� - True���� - False

    >>> is_not_null_and_blank_str('')
    False
    >>> is_not_null_and_blank_str(' ')
    False
    >>> is_not_null_and_blank_str('  ')
    False
    >>> is_not_null_and_blank_str('123')
    True
    """
    if content and content.strip():
        return True
    else:
        return False


class DingtalkChatbot(object):
    """
    ����Ⱥ�Զ�������ˣ�ÿ��������ÿ������෢��20������֧���ı���text�������ӣ�link����markdown������Ϣ���ͣ�
    """

    def __init__(self, webhook=None, secret=None, pc_slide=False, fail_notice=False):
        """
        �����˳�ʼ��
        :param webhook: ����Ⱥ�Զ��������webhook��ַ
        :param secret: �����˰�ȫ����ҳ�湴ѡ����ǩ��ʱ��Ҫ�������Կ
        :param pc_slide: ��Ϣ���Ӵ򿪷�ʽ��Ĭ��FalseΪ������򿪣�����ΪTrueʱΪPC�˲������
        :param fail_notice: ��Ϣ����ʧ�����ѣ�Ĭ��ΪFalse�����ѣ������߿��Ը��ݷ��ص���Ϣ���ͽ�������жϺʹ���
        """
        super(DingtalkChatbot, self).__init__()
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.queue = queue.Queue(20)  # �����ٷ�����ÿ���ӷ���20����Ϣ
        # ��ʼ���趨���������衷Ⱥ������siri����
        self.webhook = global_config.DING_WEBHOOK
        self.secret = global_config.DING_SECRET

        self.pc_slide = pc_slide
        self.fail_notice = fail_notice
        self.start_time = time.time()  # ��ǩʱ������ʱ���������ʱ�䲻�ܳ���1Сʱ�����ڶ�ʱ����ǩ��
        if self.secret is not None and self.secret.startswith('SEC'):
            self.update_webhook()

    def update_webhook(self):
        """
        ����Ⱥ�Զ�������˰�ȫ���ü�ǩʱ��ǩ���е�ʱ���������ʱ���ܳ���һ��Сʱ������ÿ��1Сʱ��Ҫ����ǩ��
        """
        if is_py3:
            timestamp = round(self.start_time * 1000)
            string_to_sign = '{}\n{}'.format(timestamp, self.secret)
            hmac_code = hmac.new(self.secret.encode(), string_to_sign.encode(), digestmod=hashlib.sha256).digest()
        else:
            timestamp = long(round(self.start_time * 1000))
            secret_enc = bytes(self.secret).encode('utf-8')
            string_to_sign = '{}\n{}'.format(timestamp, self.secret)
            string_to_sign_enc = bytes(string_to_sign).encode('utf-8')
            hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()

        sign = quote_plus(base64.b64encode(hmac_code))
        self.webhook = '{}&timestamp={}&sign={}'.format(self.webhook, str(timestamp), sign)

    def msg_open_type(self, url):
        """
        ��Ϣ���ӵĴ򿪷�ʽ
        1��Ĭ�ϻ�����ʱ��Ϊ������򿪣�pc_slide=False
        2����PC�˲�����򿪣�pc_slide=True
        """
        encode_url = quote_plus(url)
        if self.pc_slide:
            final_link = 'dingtalk://dingtalkclient/page/link?url={}&pc_slide=true'.format(encode_url)
        else:
            final_link = 'dingtalk://dingtalkclient/page/link?url={}&pc_slide=false'.format(encode_url)
        return final_link

    def send_text(self, msg, is_at_all=False, at_mobiles=[], at_dingtalk_ids=[], is_auto_at=True):
        """
        text����
        :param msg: ��Ϣ����
        :param is_at_all: @������ʱ��true������Ϊfalse����ѡ��
        :param at_mobiles: ��@�˵��ֻ��ţ�ע�⣺������msg�������Զ���@�ֻ��ŵ�λ�ã�Ҳ֧��ͬʱ@����ֻ��ţ���ѡ��
        :param at_dingtalk_ids: ��@�˵�dingtalkId����ѡ��
        :param is_auto_at: �Ƿ��Զ���msg����ĩβ���@�ֻ��ţ�Ĭ���Զ���ӣ�������ΪFalseȡ������ѡ��
        :return: ������Ϣ���ͽ��
        """
        data = {"msgtype": "text", "at": {}}
        if is_not_null_and_blank_str(msg):
            data["text"] = {"content": msg}
        else:
            logging.error("text���ͣ���Ϣ���ݲ���Ϊ�գ�")
            raise ValueError("text���ͣ���Ϣ���ݲ���Ϊ�գ�")

        if is_at_all:
            data["at"]["isAtAll"] = is_at_all

        if at_mobiles:
            at_mobiles = list(map(str, at_mobiles))
            data["at"]["atMobiles"] = at_mobiles
            if is_auto_at:
                mobiles_text = '\n@' + '@'.join(at_mobiles)
                data["text"]["content"] = msg + mobiles_text

        if at_dingtalk_ids:
            at_dingtalk_ids = list(map(str, at_dingtalk_ids))
            data["at"]["atDingtalkIds"] = at_dingtalk_ids

        logging.debug('text���ͣ�%s' % data)
        return self.post(data)

    def send_image(self, pic_url):
        """
        image���ͣ����飩
        :param pic_url: ͼƬ����
        :return: ������Ϣ���ͽ��
        """
        if is_not_null_and_blank_str(pic_url):
            data = {
                "msgtype": "image",
                "image": {
                    "picURL": pic_url
                }
            }
            logging.debug('image���ͣ�%s' % data)
            return self.post(data)
        else:
            logging.error("image������ͼƬ���Ӳ���Ϊ�գ�")
            raise ValueError("image������ͼƬ���Ӳ���Ϊ�գ�")

    def send_link(self, title, text, message_url, pic_url=''):
        """
        link����
        :param title: ��Ϣ����
        :param text: ��Ϣ���ݣ����̫���Զ�ʡ����ʾ��
        :param message_url: �����Ϣ������URL
        :param pic_url: ͼƬURL����ѡ��
        :return: ������Ϣ���ͽ��

        """
        if all(map(is_not_null_and_blank_str, [title, text, message_url])):
            data = {
                "msgtype": "link",
                "link": {
                    "text": text,
                    "title": title,
                    "picUrl": pic_url,
                    "messageUrl": self.msg_open_type(message_url)
                }
            }
            logging.debug('link���ͣ�%s' % data)
            return self.post(data)
        else:
            logging.error("link��������Ϣ��������ݻ����Ӳ���Ϊ�գ�")
            raise ValueError("link��������Ϣ��������ݻ����Ӳ���Ϊ�գ�")

    def send_markdown(self, title, text, is_at_all=False, at_mobiles=[], at_dingtalk_ids=[], is_auto_at=True):
        """
        markdown����
        :param title: �����Ự͸����չʾ����
        :param text: markdown��ʽ����Ϣ����
        :param is_at_all: @������ʱ��true������Ϊ��false����ѡ��
        :param at_mobiles: ��@�˵��ֻ��ţ�Ĭ���Զ������text����ĩβ����ȡ���Զ�����Ӹ�Ϊ�Զ������ã���ѡ��
        :param at_dingtalk_ids: ��@�˵�dingtalkId����ѡ��
        :param is_auto_at: �Ƿ��Զ���text����ĩβ���@�ֻ��ţ�Ĭ���Զ���ӣ�������ΪFalseȡ������ѡ��        
        :return: ������Ϣ���ͽ��
        """
        if all(map(is_not_null_and_blank_str, [title, text])):
            # ��Mardown�ı���Ϣ�е���ת�����������ת��ʽ
            text = re.sub(r'(?<!!)\[.*?\]\((.*?)\)',
                          lambda m: m.group(0).replace(m.group(1), self.msg_open_type(m.group(1))), text)
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": text
                },
                "at": {}
            }
            if is_at_all:
                data["at"]["isAtAll"] = is_at_all

            if at_mobiles:
                at_mobiles = list(map(str, at_mobiles))
                data["at"]["atMobiles"] = at_mobiles
                if is_auto_at:
                    mobiles_text = '\n@' + '@'.join(at_mobiles)
                    data["markdown"]["text"] = text + mobiles_text

            if at_dingtalk_ids:
                at_dingtalk_ids = list(map(str, at_dingtalk_ids))
                data["at"]["atDingtalkIds"] = at_dingtalk_ids

            logging.debug("markdown���ͣ�%s" % data)
            return self.post(data)
        else:
            logging.error("markdown��������Ϣ��������ݲ���Ϊ�գ�")
            raise ValueError("markdown��������Ϣ��������ݲ���Ϊ�գ�")

    def send_action_card(self, action_card):
        """
        ActionCard����
        :param action_card: ������תActionCard����ʵ���������תActionCard����ʵ��
        :return: ������Ϣ���ͽ��
        """
        if isinstance(action_card, ActionCard):
            data = action_card.get_data()

            if "singleURL" in data["actionCard"]:
                data["actionCard"]["singleURL"] = self.msg_open_type(data["actionCard"]["singleURL"])
            elif "btns" in data["actionCard"]:
                for btn in data["actionCard"]["btns"]:
                    btn["actionURL"] = self.msg_open_type(btn["actionURL"])

            logging.debug("ActionCard���ͣ�%s" % data)
            return self.post(data)
        else:
            logging.error("ActionCard���ͣ������ʵ�����Ͳ���ȷ������Ϊ��{}".format(str(action_card)))
            raise TypeError("ActionCard���ͣ������ʵ�����Ͳ���ȷ������Ϊ��{}".format(str(action_card)))

    def send_feed_card(self, links):
        """
        FeedCard����
        :param links: FeedLinkʵ���б� or CardItemʵ���б�
        :return: ������Ϣ���ͽ��
        """
        if not isinstance(links, list):
            logging.error("FeedLink���ͣ���������ݸ�ʽ����ȷ������Ϊ��{}".format(str(links)))
            raise ValueError("FeedLink���ͣ���������ݸ�ʽ����ȷ������Ϊ��{}".format(str(links)))

        link_list = []
        for link in links:
            # ���ݣ�1������FeedLinkʵ���б�2��CardItemʵ���б�
            if isinstance(link, FeedLink) or isinstance(link, CardItem):
                link = link.get_data()
                link['messageURL'] = self.msg_open_type(link['messageURL'])
                link_list.append(link)
            else:
                logging.error("FeedLink���ͣ���������ݸ�ʽ����ȷ������Ϊ��{}".format(str(link)))
                raise ValueError("FeedLink���ͣ���������ݸ�ʽ����ȷ������Ϊ��{}".format(str(link)))

        data = {"msgtype": "feedCard", "feedCard": {"links": link_list}}
        logging.debug("FeedCard���ͣ�%s" % data)
        return self.post(data)

    def post(self, data):
        """
        ������Ϣ������UTF-8���룩
        :param data: ��Ϣ���ݣ��ֵ䣩
        :return: ������Ϣ���ͽ��
        """
        now = time.time()

        # �����Զ�������˰�ȫ���ü�ǩʱ��ǩ���е�ʱ���������ʱ���ܳ���һ��Сʱ������ÿ��1Сʱ��Ҫ����ǩ��
        if now - self.start_time >= 3600 and self.secret is not None and self.secret.startswith('SEC'):
            self.start_time = now
            self.update_webhook()

        # �����Զ������������ÿ������෢��20����Ϣ
        self.queue.put(now)
        if self.queue.full():
            elapse_time = now - self.queue.get()
            if elapse_time < 60:
                sleep_time = int(60 - elapse_time) + 1
                logging.debug('�����ٷ����ƻ�����ÿ������෢��20������ǰ����Ƶ���Ѵ��������������� {}s'.format(str(sleep_time)))
                time.sleep(sleep_time)

        try:
            post_data = json.dumps(data)
            response = requests.post(self.webhook, headers=self.headers, data=post_data)
        except requests.exceptions.HTTPError as exc:
            logging.error("��Ϣ����ʧ�ܣ� HTTP error: %d, reason: %s" % (exc.response.status_code, exc.response.reason))
            raise
        except requests.exceptions.ConnectionError:
            logging.error("��Ϣ����ʧ�ܣ�HTTP connection error!")
            raise
        except requests.exceptions.Timeout:
            logging.error("��Ϣ����ʧ�ܣ�Timeout error!")
            raise
        except requests.exceptions.RequestException:
            logging.error("��Ϣ����ʧ��, Request Exception!")
            raise
        else:
            try:
                result = response.json()
            except JSONDecodeError:
                logging.error("��������Ӧ�쳣��״̬�룺%s����Ӧ���ݣ�%s" % (response.status_code, response.text))
                return {'errcode': 500, 'errmsg': '��������Ӧ�쳣'}
            else:
                logging.debug('���ͽ����%s' % result)
                # ��Ϣ����ʧ�����ѣ�errcode ��Ϊ 0����ʾ��Ϣ�����쳣����Ĭ�ϲ����ѣ������߿��Ը��ݷ��ص���Ϣ���ͽ�������жϺʹ���
                if self.fail_notice and result.get('errcode', True):
                    time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    error_data = {
                        "msgtype": "text",
                        "text": {
                            "content": "[ע��-�Զ�֪ͨ]������������Ϣ����ʧ�ܣ�ʱ�䣺%s��ԭ��%s���뼰ʱ������лл!" % (
                                time_now, result['errmsg'] if result.get('errmsg', False) else 'δ֪�쳣')
                        },
                        "at": {
                            "isAtAll": False
                        }
                    }
                    logging.error("��Ϣ����ʧ�ܣ��Զ�֪ͨ��%s" % error_data)
                    requests.post(self.webhook, headers=self.headers, data=json.dumps(error_data))
                return result


class ActionCard(object):
    """
    ActionCard������Ϣ��ʽ��������ת��������ת��
    """

    def __init__(self, title, text, btns, btn_orientation=0, hide_avatar=0):
        """
        ActionCard��ʼ��
        :param title: �����Ự͸����չʾ����
        :param text: markdown��ʽ����Ϣ
        :param btns: ��ť�б���1����ť����Ϊ1ʱ��������תActionCard���ͣ���2����ť��������1ʱ��������תActionCard���ͣ�
        :param btn_orientation: 0����ť��ֱ���У�1����ť�������У���ѡ��
        :param hide_avatar: 0����������Ϣ��ͷ��1�����ط���Ϣ��ͷ�񣨿�ѡ��
        """
        super(ActionCard, self).__init__()
        self.title = title
        self.text = text
        self.btn_orientation = btn_orientation
        self.hide_avatar = hide_avatar
        btn_list = []
        for btn in btns:
            if isinstance(btn, CardItem):
                btn_list.append(btn.get_data())
        if btn_list:
            btns = btn_list  # ���ݣ�1������CardItemʾ���б�2�����������ֵ��б�
        self.btns = btns

    def get_data(self):
        """
        ��ȡActionCard������Ϣ���ݣ��ֵ䣩
        :return: ����ActionCard����
        """
        if all(map(is_not_null_and_blank_str, [self.title, self.text])) and len(self.btns):
            if len(self.btns) == 1:
                # ������תActionCard����
                data = {
                    "msgtype": "actionCard",
                    "actionCard": {
                        "title": self.title,
                        "text": self.text,
                        "hideAvatar": self.hide_avatar,
                        "btnOrientation": self.btn_orientation,
                        "singleTitle": self.btns[0]["title"],
                        "singleURL": self.btns[0]["actionURL"]
                    }
                }
                return data
            else:
                # ������תActionCard����
                data = {
                    "msgtype": "actionCard",
                    "actionCard": {
                        "title": self.title,
                        "text": self.text,
                        "hideAvatar": self.hide_avatar,
                        "btnOrientation": self.btn_orientation,
                        "btns": self.btns
                    }
                }
                return data
        else:
            logging.error("ActionCard���ͣ���Ϣ��������ݻ�ť��������Ϊ�գ�")
            raise ValueError("ActionCard���ͣ���Ϣ��������ݻ�ť��������Ϊ�գ�")


class FeedLink(object):
    """
    FeedCard���͵�����Ϣ��ʽ
    """

    def __init__(self, title, message_url, pic_url):
        """
        ��ʼ��������Ϣ�ı�
        :param title: ������Ϣ�ı�
        :param message_url: ���������Ϣ�󴥷���URL
        :param pic_url: ���������Ϣ����ͼƬ������URL
        """
        super(FeedLink, self).__init__()
        self.title = title
        self.message_url = message_url
        self.pic_url = pic_url

    def get_data(self):
        """
        ��ȡFeedLink��Ϣ���ݣ��ֵ䣩
        :return: ��FeedLink��Ϣ������
        """
        if all(map(is_not_null_and_blank_str, [self.title, self.message_url, self.pic_url])):
            data = {
                "title": self.title,
                "messageURL": self.message_url,
                "picURL": self.pic_url
            }
            return data
        else:
            logging.error("FeedCard���͵�����Ϣ�ı�����Ϣ���ӡ�ͼƬ���Ӳ���Ϊ�գ�")
            raise ValueError("FeedCard���͵�����Ϣ�ı�����Ϣ���ӡ�ͼƬ���Ӳ���Ϊ�գ�")


class CardItem(object):
    """
    ActionCard��FeedCard��Ϣ�����е��ӿؼ�
    """

    def __init__(self, title, url, pic_url=None):
        """
        CardItem��ʼ��
        @param title: �ӿؼ�����
        @param url: ����ӿؼ�ʱ������URL
        @param pic_url: FeedCard��ͼƬ��ַ��ActionCardʱ����Ҫ����Ĭ��ΪNone
        """
        super(CardItem, self).__init__()
        self.title = title
        self.url = url
        self.pic_url = pic_url

    def get_data(self):
        """
        ��ȡCardItem�ӿؼ����ݣ��ֵ䣩
        @return: �ӿؼ�������
        """
        if all(map(is_not_null_and_blank_str, [self.title, self.url, self.pic_url])):
            # FeedCard����
            data = {
                "title": self.title,
                "messageURL": self.url,
                "picURL": self.pic_url
            }
            return data
        elif all(map(is_not_null_and_blank_str, [self.title, self.url])):
            # ActionCard����
            data = {
                "title": self.title,
                "actionURL": self.url
            }
            return data
        else:
            logging.error("CardItem��ActionCard���ӿؼ�ʱ��title��url����Ϊ�գ���FeedCard���ӿؼ�ʱ��title��url��pic_url����Ϊ�գ�")
            raise ValueError("CardItem��ActionCard���ӿؼ�ʱ��title��url����Ϊ�գ���FeedCard���ӿؼ�ʱ��title��url��pic_url����Ϊ�գ�")
