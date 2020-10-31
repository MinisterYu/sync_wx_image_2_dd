# -*- coding: gb2312 -*-
# ! /usr/bin/env python
import logging
import os

# 微信公众号配置
# 登录 cookies  -- 每次修改
COOKIES = "ua_id=Ho4hzV3FnR1ZB8DBAAAAAAAuGpEMu1UOgOsf4wmGqao=; pgv_pvi=7355956224; pgv_si=s9599310848; openid2ticket_oY5mC09S3gI6H3tkJng-5UHieeH4=5IzHfMP5rXARynd0gboi+z7JoVpTVRsC+30o0DsMNmM=; mm_lang=zh_CN; ptui_loginuin=173682166@qq.com; uin=o0173682166; skey=@ndxQordgT; RK=gI5syesGOY; ptcz=f8b4b8616467301a9d857022e184852c6c8220aaf5ffe75728d3f52db37197f4; uuid=e46620edefc79d640e731afd89e8174d; rand_info=CAESIGSTV/kdwaKQZ+NqGKzuJB4/xkQE9LYkaHBgBeA5yUpB; slave_bizuin=3594344901; data_bizuin=3548551523; bizuin=3594344901; data_ticket=o6g3vGFPtSLYO4AB78Ij+JMdfoY5DjY50cZS8iZg07cZOHfb42w1KlK9rh0kxsG4; slave_sid=V1ltMTFaWVRpdEUyR1pUVEk4SEtPcnRzcnlBVE9NTGp5b0ZRVW5vMzcxbTNpRzB1eU1tZEdMZEx2b2RDM1NBbHRiYmY3SzZ2amhDSDR1d2JUOGllZ191RFJvTG9FRjlqOTJ5WGxlRXBsODlkRXc0aU9xNXgzN0l1dVp3dW5hcjJIQk9ORW9IWm9CR2MxU1B3; slave_user=gh_46235149cb45; xid=d9eeef70d4628b5e41c7d31092c6ba02"

# 登录token  -- 每次修改
MP_TOKEN = '1463668875'

# 后台地址
MP_URL = "https://mp.weixin.qq.com/cgi-bin/message?t=message/list&count={0}&day={1}&filtertype=0&filterivrmsg=1&filterspammsg=1&token={2}&lang=zh_CN" \
    .format(20, 5, MP_TOKEN)  # 第一个参数是每页读取数， 第二个是查近 X 天,  第三个是token

# 请求header
MP_HEADERS = {'authority': 'mp.weixin.qq.com',
              'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
              'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
              'referer': 'https://mp.weixin.qq.com/cgi-bin/message?t=message/list&count=20&day=1&token={0}&lang=zh_CN'.format(
                  MP_TOKEN),
              'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
              'cookie': COOKIES
              }

# ----------------------------------------------------

# TTK 配置
# 上传接口
TTK_URL = "http://up.imgapi.com/"

# 上传图册的TOKEN，参考 http://www.tietuku.com/manager/createtoken
TTK_TOKEN = "9c7bf21edf08008e7cdb146aaba373de53c1fa74:K8CuBPEMlao_k3x1YOP9vOoWiMg=:eyJkZWFkbGluZSI6MTYwNDA3MDIwNiwiYWN0aW9uIjoiZ2V0IiwidWlkIjoiNzI5MDAzIiwiYWlkIjoiMTcyNjg1NiIsImZyb20iOiJmaWxlIn0="

# 请求header
TTK_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
}

# ----------------------------------------------------

# 钉钉机器人配置
# 初始化设定《不如跳舞》群机器人siri配置
# ding hook
DING_WEBHOOK = 'https://oapi.dingtalk.com/robot/send?access_token=18fd9aaede1ca56cf868993ae3352e49c3e73062a0d6bce7f4944031fcc84bdd'

# 加签秘钥
DING_SECRET = 'SEC4d8e90ce12b9e3d9dc7b496200c857d4dd065d2008ece7254c5b799b8b8808c2'

# ----------------------------------------------------

# 系统配置

# DB数据
DB_CONFIG = os.path.abspath("./sync_log.db")

# 日志
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
