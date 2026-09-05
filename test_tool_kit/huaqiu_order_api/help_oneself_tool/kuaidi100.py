import hashlib
import json
import random
import re
import time
from datetime import datetime, timedelta

import jsonpath
import requests
import yaml
from xpinyin import Pinyin

from huaqiu_order_api.common.my_path import yaml_file


class KuaiDi100:
    # 潜在合作商
    def __init__(self, express_number):
        self.rss = requests.session()
        self.express_number = express_number
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.KuaiDi100_URL = data['help_oneself']['kauidi100']
        self.json_head = {"Content-Type": "application/json",
                          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}
        self.data_head = {"Content-Type": "multipart/form-data"}


    def kuaidi100_comCode(self):
        """
        快递100快递公司编码
        :return:
        """
        comCode_list = None
        if bool(re.match(r'^(?:[A-Z]{3}|[A-Z]{2})\d{9,15}$', self.express_number, re.IGNORECASE)) == True:
            comCode_url = "{}/autonumber/autoComNum?text={}".format(self.KuaiDi100_URL, self.express_number)
            print(comCode_url)
            comCode_res = self.rss.post(url=comCode_url, headers=self.json_head).json()
            print(comCode_res)
            comCode_list = jsonpath.jsonpath(comCode_res, '$..comCode')
        return comCode_list
    def kuaidi100_query(self, comCode):
        phone = '9124'
        for i in range(len(comCode)):
            temp = random.random()
            print(temp)
            query_url = "{}/query?type={}&postid={}&temp={}&phone={}".format(self.KuaiDi100_URL, comCode[i], self.express_number,temp, phone)
            print(query_url)
            query_res = self.rss.get(query_url, headers=self.json_head).json()
            print(query_res)
    def mian_kuaidi100(self):
        comCode_list = self.kuaidi100_comCode()
        self.kuaidi100_query(comCode_list)


    def cesit(self):
        uname = "15070739124@163.com"
        key = "af307ec51e992df2a9eaf68425754d92"
        md5 = hashlib.md5()
        md5.update((uname + key).encode('utf-8'))
        keysign = md5.hexdigest()
        url = "http://send.wxbus163.cn/express/getLogistics"
        body = {"express_number": self.express_number, "phone": "15070739124", "keySecret": keysign, "uname": uname}
        print(body)
        res = self.rss.post(url=url, data=body, headers=self.data_head).json()
        print(res)




if __name__ == '__main__':
    KuaiDi100("SF3115735409515").mian_kuaidi100()
