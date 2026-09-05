# import requests
#
# url = "http://47.100.4.100/api/protoss/mfg?page=1&size=10&sort=id%2Cdesc"
#
# payload = {}
# headers = {
#   'Accept': 'application/json, text/plain, */*',
#   'Accept-Language': 'zh-CN,zh;q=0.9',
#   'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiIxZTU0NmM4MmY5MjU0ZGM0YjFiZWZlZTM0NWEwYTc5MyIsInVzZXIiOiJhZG1pbiIsInN1YiI6ImFkbWluIn0.5eQg3YtEn6aCFnMU6HL5G5V-x2OlQmD_XVmg5J89-_YdhDumFt1xx7NvENvZ7h0_RZ4CxR5pKKuxQYGquwTEng',
#   'Connection': 'keep-alive',
#   'Referer': 'http://47.100.4.100/metadata/manufacturer',
#   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
#   #'Cookie': 'username=admin; password=Ble2Iqhr2CsxnuMBiwYEBxUSLq3MBRtQAITkfjperIWTqWNrQ9KcteI8Q0G6rI5WO3bosCUHO1tmJAcq+50lYw==; rememberMe=true; ELADMIN-TOEKN=Bearer%20eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiIxZTU0NmM4MmY5MjU0ZGM0YjFiZWZlZTM0NWEwYTc5MyIsInVzZXIiOiJhZG1pbiIsInN1YiI6ImFkbWluIn0.5eQg3YtEn6aCFnMU6HL5G5V-x2OlQmD_XVmg5J89-_YdhDumFt1xx7NvENvZ7h0_RZ4CxR5pKKuxQYGquwTEng',
#   #'Cookie': 'username=admin; password=Ble2Iqhr2CsxnuMBiwYEBxUSLq3MBRtQAITkfjperIWTqWNrQ9KcteI8Q0G6rI5WO3bosCUHO1tmJAcq+50lYw==; rememberMe=true; ELADMIN-TOEKN=Bearer%20eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiIxZTU0NmM4MmY5MjU0ZGM0YjFiZWZlZTM0NWEwYTc5MyIsInVzZXIiOiJhZG1pbiIsInN1YiI6ImFkbWluIn0.5eQg3YtEn6aCFnMU6HL5G5V-x2OlQmD_XVmg5J89-_YdhDumFt1xx7NvENvZ7h0_RZ4CxR5pKKuxQYGquwTEng'
# }
#
# response = requests.request("GET", url, headers=headers, data=payload)
# print(response.text)


import json
import math
import re
import time
from pipes import quote

import pandas as pd
import jsonpath
import requests
import yaml
from bs4 import BeautifulSoup

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, xl_brand_dir


class Means:

    def __init__(self):

        self.rss = requests.Session()
        self.json_head = {
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'zh-CN,zh;q=0.9',
  'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiIxZTU0NmM4MmY5MjU0ZGM0YjFiZWZlZTM0NWEwYTc5MyIsInVzZXIiOiJhZG1pbiIsInN1YiI6ImFkbWluIn0.5eQg3YtEn6aCFnMU6HL5G5V-x2OlQmD_XVmg5J89-_YdhDumFt1xx7NvENvZ7h0_RZ4CxR5pKKuxQYGquwTEng',
  'Connection': 'keep-alive',
  'Referer': 'http://47.100.4.100/metadata/manufacturer',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
  #'Cookie': 'username=admin; password=Ble2Iqhr2CsxnuMBiwYEBxUSLq3MBRtQAITkfjperIWTqWNrQ9KcteI8Q0G6rI5WO3bosCUHO1tmJAcq+50lYw==; rememberMe=true; ELADMIN-TOEKN=Bearer%20eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiIxZTU0NmM4MmY5MjU0ZGM0YjFiZWZlZTM0NWEwYTc5MyIsInVzZXIiOiJhZG1pbiIsInN1YiI6ImFkbWluIn0.5eQg3YtEn6aCFnMU6HL5G5V-x2OlQmD_XVmg5J89-_YdhDumFt1xx7NvENvZ7h0_RZ4CxR5pKKuxQYGquwTEng',
  #'Cookie': 'username=admin; password=Ble2Iqhr2CsxnuMBiwYEBxUSLq3MBRtQAITkfjperIWTqWNrQ9KcteI8Q0G6rI5WO3bosCUHO1tmJAcq+50lYw==; rememberMe=true; ELADMIN-TOEKN=Bearer%20eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiIxZTU0NmM4MmY5MjU0ZGM0YjFiZWZlZTM0NWEwYTc5MyIsInVzZXIiOiJhZG1pbiIsInN1YiI6ImFkbWluIn0.5eQg3YtEn6aCFnMU6HL5G5V-x2OlQmD_XVmg5J89-_YdhDumFt1xx7NvENvZ7h0_RZ4CxR5pKKuxQYGquwTEng'
}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ShangHai_XinLing_URL = data["ShangHai_XinLing_URL"]
        self.courier_number = data["courier_number"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        # self.token = account["ShangHai_XinLing"]["admin_token"]
        # self.json_head['Authorization'] = 'eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiIxZTU0NmM4MmY5MjU0ZGM0YjFiZWZlZTM0NWEwYTc5MyIsInVzZXIiOiJhZG1pbiIsInN1YiI6ImFkbWluIn0.5eQg3YtEn6aCFnMU6HL5G5V-x2OlQmD_XVmg5J89-_YdhDumFt1xx7NvENvZ7h0_RZ4CxR5pKKuxQYGquwTEng',


    def query_url_arguments(self, data):
        """将body参数转换成可拼接至url的参数"""
        lt = []
        for k, v in data.items():
            lt.append(k + '=' + quote(str(v)))
        # 这个是在for循环外面的，就是将列表的元素之间用用&符号连接起来
        query_string = '&'.join(lt)
        return query_string
    def xl_get_brand_code(self):
        # xl_get_brand_url = "{}/api/protoss/mfg".format(self.ShangHai_XinLing_URL)
        xl_get_brand_body = {
            "page": 1,
            "size": 100,
            "sort": "id,desc"
        }
        xl_get_brand_body_conversion = self.query_url_arguments(xl_get_brand_body)
        xl_get_brand_url = "{}/api/protoss/mfg?{}".format(self.ShangHai_XinLing_URL, xl_get_brand_body_conversion)

        xl_get_brand_res = self.rss.get(xl_get_brand_url, headers=self.json_head).json()
        totalElements = xl_get_brand_res["totalElements"]
        brand_name_count = []
        brand_id_count = []
        if int(totalElements) / 100 > 1:
            num = math.ceil(int(totalElements) / 100)
            for i in range(num):
                xl_get_brand_body["page"] = i + 1
                xl_get_brand_body_conversion = self.query_url_arguments(xl_get_brand_body)
                xl_get_brand_url = "{}/api/protoss/mfg?{}".format(self.ShangHai_XinLing_URL,
                                                                  xl_get_brand_body_conversion)
                xl_get_brand_res = self.rss.get(xl_get_brand_url, headers=self.json_head).json()
                brand_name = jsonpath.jsonpath(xl_get_brand_res, '$..displayName')
                brand_id = jsonpath.jsonpath(xl_get_brand_res, '$..id')
                brand_name_count = brand_name_count + brand_name
                brand_id_count = brand_id_count + brand_id
        # 创建一个DataFrame
        df = pd.DataFrame({
            '品牌英文简称': brand_name_count,
            '品牌ID': brand_id_count
        })
        # 将DataFrame写入Excel文件
        df.to_excel(xl_brand_dir, index=False)

        print("数据已成功写入Excel文件")
if __name__ == '__main__':
    rss = Means().xl_get_brand_code()


