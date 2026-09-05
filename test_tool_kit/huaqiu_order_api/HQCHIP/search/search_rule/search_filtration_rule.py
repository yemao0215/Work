import json
import re

import jsonpath
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class SearchFiltrstionRule:
    def __init__(self, keyword):
        self.rss = requests.Session()
        # 设置代理ip
        proxy_ip = "http://192.168.20.6:3128"
        # 设置代理
        self.proxies = {"http": proxy_ip, "https": proxy_ip}
        self.supplier_url = "https://api.mouser.com"
        self.appikey = "76f623be-ee57-4ae3-86b6-01e54048fd18"
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_URL = data['HQCHIP_URL']
        self.SEARCH_URL = data['SEARCH_URL']
        self.GO_SEARCH_URL = data['GO_SEARCH_URL']
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        # self.keyword = "0402 191KΩ 1安"
        self.keyword = keyword
        self.goods_id = [1017426139]

    def str_list_remove_blank(self):
        """字符串转化成list列表"""
        # 使用正则表达式匹配数字和字母
        if self.keyword != '':
            result = [tuple(x.split()) for x in self.keyword.split(' ')]
            self.str_list = [x[0] for x in result]
        return self

    def hc2018_search_filtration(self):
        """查询过滤规则"""
        self.dos_rss = Login().login()
        auth_token = getattr(Data, "dos_auth_token")
        for i in range(len(self.str_list)):
            logger.info(self.str_list[i])
            # if self.has_chinese(self.str_list[i]) == True:
            #     list_search = list(self.str_list[i])
            #     for m in range(len(list_search)):
            #             filtration_url = "{}/v1/rule/SegmentRule/index".format(self.HC2018_ADMIN_URL)
            #             filtration_body = {"search_word": list_search[m], "status": "1", "rule_type": "", "page": 1, "per_page": 100}
            #             self.headers["Authorization"] = auth_token
            #             filtration_res = self.dos_rss.post(url=filtration_url, data=filtration_body, headers=self.headers).json()
            #             dataInfo = jsonpath.jsonpath(filtration_res, '$.data.data')[0]
            #             if dataInfo != []:
            #                 name = jsonpath.jsonpath(filtration_res, '$..name')
            #                 action = jsonpath.jsonpath(filtration_res, '$..action')
            #                 replace_str = jsonpath.jsonpath(filtration_res, '$..replace_str')
            #                 for n in range(len(name)):
            #                     if name[n] == list_search[m]:
            #                         action = action[n]
            #                         logger.info(action)
            #                         if action == "1":
            #                             name_replace_str = replace_str[n]
            #                             logger.info(name_replace_str)
            #                             list_search.append(name_replace_str)
            #                             logger.info(list_search)
            #                             list_search_1 = [x + y for x in list_search for y in list_search if x != y]
            #                             # list_search_1 = [x + y for x , y in zip(list_search[0::2], list_search[1::2])]
            #                             logger.info(list_search_1)
            #                             list_search = [x for x in list_search + list_search_1]
            #                             logger.info(list_search)
            # else:
            #     logger.info(f"分词不存在中文")
            #     list_search = list(self.str_list[i])
            #     for m in range(len(list_search)):
            #             filtration_url = "{}/v1/rule/SegmentRule/index".format(self.HC2018_ADMIN_URL)
            #             filtration_body = {"search_word": list_search[m], "status": "1", "rule_type": "", "page": 1, "per_page": 100}
            #             self.headers["Authorization"] = auth_token
            #             filtration_res = self.dos_rss.post(url=filtration_url, data=filtration_body, headers=self.headers).json()
            #             dataInfo = jsonpath.jsonpath(filtration_res, '$.data.data')[0]
            #             if dataInfo != []:
            #                 pass

    def has_chinese(self, string):
        if re.search(r'[\u4e00-\u9fa5]', string):
            return True
        else:
            return False

    def split_chinese(self, input_string):
        # 找到第一个中文字符的位置
        split_point = next((i for i, c in enumerate(input_string) if '\u4e00' <= c <= '\u9fff'), None)
        # 如果找到中文字符，将字符串拆分成两部分
        if split_point is not None:
            lists = []
            part1 = input_string[:split_point]
            part2 = input_string[split_point:]
            lists.append(part1)
            lists.append(part2)
            return lists
        else:
            return input_string, ""

    def hc2018_admin_filtration_rule(self, dos_rss=None, token=None):
        self.dos_rss = dos_rss
        filtration_url = "{}/v1/rule/SegmentRule/index".format(self.HC2018_ADMIN_URL)
        filtration_body = {"search_word": "", "status": "1", "rule_type": "", "page": 1, "per_page": 100}
        self.headers["Authorization"] = token
        filtration_res = self.dos_rss.post(url=filtration_url, data=filtration_body, headers=self.headers).json()
        dataInfo = jsonpath.jsonpath(filtration_res, '$.data.data')
        name = jsonpath.jsonpath(dataInfo, '$..name')
        action = jsonpath.jsonpath(dataInfo, '$..action')
        replace_str = jsonpath.jsonpath(dataInfo, '$..replace_str')
        for i in range(len(replace_str)):
            if replace_str[i] == "空" or replace_str[i] == "空格":
                replace_str_null = replace_str[i] = ""
                replace_str.append(replace_str_null)
        name_replace_str_json = {}
        for key, value in zip(name, replace_str):
            name_replace_str_json[key] = value
        name_replace_str_json = json.dumps(name_replace_str_json)
        name_replace_str_json = json.loads(name_replace_str_json)
        return name_replace_str_json

    def hc2018_search_filtration_new(self, dos_rss=None, token=None):
        keyword_filtration_json = self.hc2018_admin_filtration_rule(dos_rss, token)
        lists = []
        for i in range(len(self.str_list)):
            logger.info(f"此时参与检测第一层分词：{self.str_list[i]}")
            for k in keyword_filtration_json:
                index = self.str_list[i].find(k)
                # 判断是否存在Ω 存在则转化为&&&&  原因是因为Ω，分词在转化成小写ω，此时无法对应换算表
                if "Ω" in self.str_list[i]:
                    logger.info(f'第一层分词：{self.str_list[i]}存在Ω，需要将其转化成特定字符，以防后续换算无法进行')
                    # 转成英文小写
                    self.str_list[i] = self.str_list[i].replace('Ω', '&&&&').lower()
                    # &&&& 转换回 Ω
                    self.str_list[i] = self.str_list[i].replace("&&&&", 'Ω')
                else:
                    logger.info(f'第一层分词：{self.str_list[i]}不存在Ω，直接转化英文小写')
                    self.str_list[i] = self.str_list[i].lower()
                if index > 0:
                    logger.info(f'存在换算内容，在lists写入第一层分词：{self.str_list[i]}原始值：{self.str_list[i]}')
                    lists.append(self.str_list[i])
                    logger.info(f'存在换算内容，在lists写入第一层分词：{self.str_list[i]}转换值：{self.str_list[i].replace(k, keyword_filtration_json[k])}')
                    lists.append(self.str_list[i].replace(k, keyword_filtration_json[k]))
                    if self.has_chinese(k) == True:
                        logger.info(f'存在换算内容，且存在中文字符')
                        logger.info(f'存在换算内容，在lists写入第一层分词：{self.str_list[i]}的中文字符原始值：{k}')
                        lists.append(k)
                        logger.info(f'存在换算内容，在lists写入第一层分词：{self.str_list[i]}的中文字符转换值：{keyword_filtration_json[k]}')
                        lists.append(keyword_filtration_json[k])
                        if self.has_chinese(self.str_list[i]) == True:
                            split_chinese_list = self.split_chinese(self.str_list[i])
                            logger.info(f'存在换算内容，在lists写入第一层分词：{self.str_list[i]}含有的中文字符内容进行切割，得到列表：{split_chinese_list}')
                            lists = [x for x in lists + split_chinese_list]
                    break
                else:
                    logger.info(f'不存在换算内容，在lists写入第一层分词：{self.str_list[i]}原始值：{self.str_list[i]}')
                    lists.append(self.str_list[i])
        lists = list(set(lists))
        logger.info(f"最终得分词总结果为{lists}")
        return lists

if __name__ == '__main__':
    # print(has_chinese(s))
    dos_rss = Login().login()
    auth_token = getattr(Data, "dos_auth_token")
    SearchFiltrstionRule("0402 191KΩ 1安").str_list_remove_blank().hc2018_search_filtration_new(dos_rss, auth_token)
    # input_string1, input_string2 = SearchToolKit().split_chinese("1安")
    # print(input_string1)
