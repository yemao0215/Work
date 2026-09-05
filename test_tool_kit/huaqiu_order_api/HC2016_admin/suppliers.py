import ast
import json
import math
from urllib.parse import quote
import re

import jsonpath
import requests
import yaml
from bs4 import BeautifulSoup

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, supplier_dir


class Suppliers:
    # 供应商管理
    def __init__(self, rss, real_supplier_sn=None, supplier_sn=None, supplier_name=None):
        self.rss = rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_ADMIN_URL = data['HQCHIP_ADMIN_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_form_data = {"Content-Type": "multipart/form-data",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        with open(supplier_dir, 'r', encoding='utf-8') as yamlfile:
            self.supplier_data = yaml.load(yamlfile, Loader=yaml.FullLoader)
            self.overseas_supplier_data = {key: value for key, value in self.supplier_data.items() if key not in ('supplier', 'szlcsc', 'mouser')}
        self.real_supplier_sn = real_supplier_sn
        self.supplier_sn = supplier_sn
        self.supplier_name = supplier_name
    def supplier_no_completion(self, real_supplier_sn):
        """补齐供应商编号"""
        if real_supplier_sn != None:
            if "SU" in real_supplier_sn:
                real_supplier_sn_nmuber = real_supplier_sn.split("SU")[1]
                if len(real_supplier_sn_nmuber) < 6:
                    # 在字符串前面添加 0 补齐至长度为6
                    real_supplier_sn_nmuber = real_supplier_sn_nmuber.zfill(6)
                    real_supplier_sn = "SU" + real_supplier_sn_nmuber
            # print(self.supplier_no.isdigit())
            elif real_supplier_sn.isdigit() == True:
                if len(real_supplier_sn) < 6:
                    real_supplier_sn = real_supplier_sn.zfill(6)
                real_supplier_sn = "SU" + real_supplier_sn
            # print(real_supplier_sn)
        return real_supplier_sn
    def supplier_search(self):
        """供应商查询"""
        search_url = "{}/Admin/DgkSuppliers/index".format(self.HQCHIP_ADMIN_URL)
        search_body = {"pageNum": 1, "supplier_sn": "", "suppliers_name": "", "real_supplier_sn": "", "is_on_sale": 1,
                       "status": 1, "type": "", "add_user": "", "picking_user": ""}
        real_supplier_sn_count = []
        supplier_sn_count = []
        supplier_name_count = []
        supplier_id_count = []
        if self.real_supplier_sn == None and self.supplier_sn == None and self.supplier_name == None:
            search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers).text
            total = re.search('<div class="pagination" targetType="navTab" totalCount="(.*?)"',
                                     search_res).group(1)
            if int(total) / 20 > 1:
                total_num = math.ceil(int(total) / 20)
                for i in range(total_num):
                    i = i + 1
                    # print(i)
                    search_body["pageNum"] = i
                    search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers).text
                    supplier_id = re.findall('<tr target="sid_supp_id" rel="(.*?)"', search_res)
                    if supplier_id:
                         # 从列表中提取字段供应商编码、展示供应商、实际供应商
                        soup = BeautifulSoup(search_res, 'html.parser')
                        table = soup.find('tbody')
                        rows = table.find_all('tr')
                        real_supplier_sn_column = []
                        supplier_sn_column = []
                        supplier_name_column = []
                        # for row in rows[1:]: # 跳过表头
                        for row in rows:  # 不跳过表头
                            cells = row.find_all('td')
                            real_supplier_sn_column.append(cells[2].text)
                            supplier_sn_column.append(cells[3].text)
                            supplier_name_column.append(cells[4].text)
                        real_supplier_sn_count = real_supplier_sn_count + real_supplier_sn_column
                        supplier_sn_count = supplier_sn_count + supplier_sn_column
                        supplier_name_count = supplier_name_count + supplier_name_column
                        supplier_id_count = supplier_id_count + supplier_id
                    continue

            else:
                supplier_id = re.findall('<tr target="sid_supp_id" rel="(.*?)"', search_res)
                if supplier_id != []:
                    # 从列表中提取字段供应商编码、展示供应商、实际供应商
                    soup = BeautifulSoup(search_res, 'html.parser')
                    table = soup.find('tbody')
                    rows = table.find_all('tr')
                    real_supplier_sn_column = []
                    supplier_sn_column = []
                    supplier_name_column = []
                    # for row in rows[1:]: # 跳过表头
                    for row in rows:  # 不跳过表头
                        cells = row.find_all('td')
                        real_supplier_sn_column.append(cells[2].text)
                        supplier_sn_column.append(cells[3].text)
                        supplier_name_column.append(cells[4].text)
                    real_supplier_sn_count = real_supplier_sn_count + real_supplier_sn_column
                    supplier_sn_count = supplier_sn_count + supplier_sn_column
                    supplier_name_count = supplier_name_count + supplier_name_column
                    supplier_id_count = supplier_id_count + supplier_id
        else:
            if self.real_supplier_sn != None:
                self.real_supplier_sn = self.supplier_no_completion(self.real_supplier_sn)
            completion_body = {"supplier_sn": self.supplier_sn, "suppliers_name": self.supplier_name, "real_supplier_sn": self.real_supplier_sn}
            search_body.update(completion_body)
            # print(search_body)
            search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers).text
            supplier_id = re.findall('<tr target="sid_supp_id" rel="(.*?)"', search_res)
            if supplier_id != []:
                # 从列表中提取字段供应商编码、展示供应商、实际供应商
                soup = BeautifulSoup(search_res, 'html.parser')
                table = soup.find('tbody')
                rows = table.find_all('tr')
                real_supplier_sn_column = []
                supplier_sn_column = []
                supplier_name_column = []
                # for row in rows[1:]: # 跳过表头
                for row in rows:  # 不跳过表头
                    cells = row.find_all('td')
                    real_supplier_sn_column.append(cells[2].text)
                    supplier_sn_column.append(cells[3].text)
                    supplier_name_column.append(cells[4].text)
                real_supplier_sn_count = real_supplier_sn_count + real_supplier_sn_column
                supplier_sn_count = supplier_sn_count + supplier_sn_column
                supplier_name_count = supplier_name_count + supplier_name_column
                supplier_id_count = supplier_id_count + supplier_id
        # 将列表：supplier_id_count、real_supplier_sn_count、supplier_sn_count、supplier_name_count组成新的字典
        supplier_dict = {}
        for key, val1, val2, val3 in zip(supplier_id_count, real_supplier_sn_count, supplier_sn_count, supplier_name_count):
            supplier_dict[key] = [val1, val2, val3]
        print(json.dumps(supplier_dict, ensure_ascii=False).replace("'", '"'))
        return supplier_dict

if __name__ == '__main__':
    real_supplier_sn = None
    supplier_sn = None
    supplier_name = None
    from huaqiu_order_api.HC2016_admin.login import HC2016Login
    rss = HC2016Login().hc2016_login()
    Suppliers(rss, real_supplier_sn, supplier_sn, supplier_name).supplier_search()
