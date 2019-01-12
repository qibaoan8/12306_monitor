#!/usr/bin/env python
# coding:utf-8

import requests, random
from hashlib import md5

class RClient(object):

    def __init__(self, username, password, soft_id, soft_key):
        self.username = username
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.soft_key = soft_key
        self.base_params = {
            'username': self.username,
            'password': self.password,
            'softid': self.soft_id,
            'softkey': self.soft_key,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }

    def rk_create(self, im, im_type, timeout=60):
        """
        im: 图片字节
        im_type: 题目类型
        """
        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        res = requests.post('http://api.ruokuai.com/create.json', data=params, files=files, headers=self.headers)
        res_json = res.json()
        print res_json
        xys = self.make_xy(res_json.get('Result'))
        return xys

    def rk_report_error(self, im_id):
        """
        im_id:报错题目的ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://api.ruokuai.com/reporterror.json', data=params, headers=self.headers)
        return r.json()

    def make_xy(self,text):
        init_x = 6
        init_y = 12
        one_x = 68
        one_y = 68
        bar = 4
        shift = 15

        xys = []
        for s in text:
            s = int(s)
            if s % 4 == 0 :
                x = 3
            else:
                x = s % 4 - 1

            y = s / 5

            # 坐标 x, y
            xys.append(int(init_x + (x + 0.5) * one_x + x * bar + random.randint(-shift, shift)))
            xys.append(int(init_y + (y + 0.5) * one_y + y * bar + random.randint(-shift, shift)))

        xys = [str(x) for x in xys]
        return ','.join(xys)

if __name__ == '__main__':
    from config import *

    rc = RClient(rk_username, rk_password, '1', 'b40ffbee5c1cf4e38028c197eb2fc751')
    im = open('c.jpg', 'rb').read()
    print rc.rk_create(im, 6113)

