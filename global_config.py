# -*- coding: gbk -*-
# ! /usr/bin/env python
import logging
import os

# 后台轮训时间
INTERVAL_TIME = 30

# 微信公众号配置
# 登录 cookies  -- 每次修改
COOKIES = "ua_id=Ho4hzV3FnR1ZB8DBAAAAAAAuGpEMu1UOgOsf4wmGqao=; pgv_pvi=7355956224; pgv_si=s9599310848; openid2ticket_oY5mC09S3gI6H3tkJng-5UHieeH4=5IzHfMP5rXARynd0gboi+z7JoVpTVRsC+30o0DsMNmM=; mm_lang=zh_CN; ptui_loginuin=173682166@qq.com; uin=o0173682166; skey=@ndxQordgT; RK=gI5syesGOY; ptcz=f8b4b8616467301a9d857022e184852c6c8220aaf5ffe75728d3f52db37197f4; media_ticket=558a0eca40e65b7b69cc18137d1ef547934cfbb1; media_ticket_id=3594344901; sig=h01fe93019a83854831be24877c006d39121dbf06a5108e4ebb85f400664b1d5fbe01a382f8e6419802; uuid=96cc27ad1cbcd1c81d1e5f6eeacccedf; rand_info=CAESIKEIOuB8dQ5AS+QcnL+UP4Sjm5QDx0VtIeOIJloRh9Sv; slave_bizuin=3594344901; data_bizuin=3548551523; bizuin=3594344901; data_ticket=WJrHpoM2C709CK8xJtPWyZZ8VGa2zb9u0tiIz8agEVt32672L+JthUk0wFhT9+FJ; slave_sid=cnhkRkJSU1lrdzJtOUNDR0VUZXlTdnVrWGxtX1RGTnZMang0VFMydHVCeHRtR01ZR0I2R1JHZ2VWTWl1NDl1dEtrMEN3QVdyZDNZWmRyYkNFeEdWVFRVUUdiM1dCXzRZYzJmbGxNcDF3c2RISDI2b1I0OE9yUzJPdzJrR0szd2FGTmxSRnZBZDhJWjN1UGto; slave_user=gh_46235149cb45; xid=16a55d845e2e257dd9e2f701dbc8e73b"

# 登录token  -- 每次修改
MP_TOKEN = '1494544130'

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

WX_BOT_KEY = ''

# ----------------------------------------------------
# 系统配置

# DB数据
DB_CONFIG = os.path.abspath("./sync_log.db")

# 日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
