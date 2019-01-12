#!/usr/bin/env python
# encoding: utf-8
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
 
"""
File: monitor_order.py
Date: 2019-01-12 16:26
Author: wang.gaofei@alibaba-inc.com 
"""
import sys,os,requests,cookielib,time,re,json,base64
from rk import RClient
from log_config import init_log
from config import *

reload(sys)
sys.setdefaultencoding('utf-8')

file_path = os.path.abspath(os.path.dirname(__file__)) + "/logs/"
log = init_log('12306_monitor',file_path)


class Train():

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.proxies = {'http': 'http://10.125.192.46:65530', 'https': 'http://10.125.192.46:65530'}

        self.headers = {
            'Origin': 'https://www.12306.cn',
            'Accept-Encoding': 'deflate',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Connection': 'keep-alive',
        }

        # 初始化cookie环境
        self.cookie_path = "cookie.txt"
        # 将LWPCookieJar类型的cookie 赋值给 RequestsCookiesJar类型的cookie；也能使用，绝了。
        self.session = requests.Session()
        self.session.cookies = cookielib.LWPCookieJar(self.cookie_path)
        if os.path.exists(self.cookie_path):
            self.session.cookies.load(ignore_discard=True, ignore_expires=True)

    def save_cookie(self):
        self.session.cookies.save(ignore_discard=True, ignore_expires=True)
        return

    def check_login(self):
        print "Check_login"
        log.info("Check_login")
        url = "https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete"
        ret = self.session.post(url,proxies=self.proxies, headers=self.headers)
        if ret.status_code == 200 and 'html' not in ret.content:
            return True
        return False

    def login(self):
        print "bagin login ..."
        log.info("bagin login ...")
        self.headers['Referer'] = 'https://www.12306.cn/index/'

        # 一、访问初始页面，获取cookie
        data = {'appid':'otn'}
        self.session.post('https://kyfw.12306.cn/passport/web/auth/uamtk-static',
                                data=data, proxies=self.proxies, headers=self.headers)

        # 二、获取验证码、提取、转换、识别
        jquery = "jQuery191080472046843172_%s" %int(round(time.time() * 1000))
        url = ("https://kyfw.12306.cn/passport/captcha/captcha-image64?"
               "login_site=E&module=login&rand=sjrand&%s&callback=%s&_=%s" % (
                   int(round(time.time() * 1000)), jquery, int(round(time.time() * 1000))))

        ret = self.session.get(url,proxies=self.proxies, headers=self.headers)

        # 提取转换验证码
        ret_text = re.split("\(|\)",ret.content)[1]
        log.info("verify photo base64: %s" % ret_text)
        ret_json = json.loads(ret_text)
        verify_photo = base64.b64decode(ret_json.get('image'))

        # 识别验证码
        rc = RClient(rk_username, rk_password, '1', 'b40ffbee5c1cf4e38028c197eb2fc751')
        verify_text = rc.rk_create(verify_photo, 6113)
        log.info("verify text: %s" % verify_text)

        # 三、校验验证码
        print "passport/captcha/captcha-check"
        log.info("passport/captcha/captcha-check")
        url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
        get_data = {
            'callback':"%s" %jquery,
            'answer':"%s" %verify_text,
            'rand':"sjrand",
            'login_site':"E",
            '_':"%s" %int(round(time.time() * 1000)),
        }
        ret = self.session.get(url,params=get_data,proxies=self.proxies, headers=self.headers)
        print ret.content
        log.info(ret.content)


        # 四、校验用户名密码
        print "login"
        log.info("login")
        url = "https://kyfw.12306.cn/passport/web/login"
        data = {
            'username':username,
            'password':password,
            'appid':'otn',
            'answer':verify_text,
        }
        ret = self.session.post(url,data=data,proxies=self.proxies, headers=self.headers)
        print ret.content
        log.info(ret.content)


        # 获取用户token
        print "auth/uamtk"
        log.info("auth/uamtk")
        url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
        ret = self.session.post(url,data={"appid":"otn"},proxies=self.proxies, headers=self.headers)
        print ret.content
        log.info(ret.content)

        # 获取权限
        print "uam auth client"
        log.info("uam auth client")
        data = {'tk':ret.json().get('newapptk')}
        url = "https://kyfw.12306.cn/otn/uamauthclient"
        ret = self.session.post(url,data=data,proxies=self.proxies, headers=self.headers)
        print ret.content
        log.info(ret.content)

        return True

    def get_orders(self):
        # 获取票票列表
        print "get piao piao"
        log.info("get piao piao")
        url = "https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete"
        ret = self.session.post(url,proxies=self.proxies, headers=self.headers)
        print ret.content
        log.info(ret.content)
        return ret.json()

if __name__ == '__main__':
    from noticentersdk import send_notify

    train = Train(username,password)
    if not train.check_login():
        train.login()
        train.save_cookie()

    ret_json = train.get_orders()
    if "data" in ret_json.keys():
        print "有订单了"
        send_notify()
    else:
        print "没有订单"




