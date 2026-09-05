import json
import re
import jsonpath
import requests
import yaml
import urllib.parse

# from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.HQCHIP_Center.user_center import get_address, get_invoice
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class SensitiveWordsDetection:
    def __init__(self, title, reply_content, seo_title=None, seo_keyword=None, seo_desc=None):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        :param goods_id:  购买的产品id
        :param numder 下单数量
        :param warehouse_id 下单仓库
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_PC_ITEM_URL = data['HQCHIP_PC_ITEM_URL']
        self.HQCHIP_URL = data['HQCHIP_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.rss = requests.Session()
        self.title = title
        self.reply_content = reply_content
        self.seo_title = seo_title
        self.seo_keyword = seo_keyword
        self.seo_desc = seo_desc


    def sensitive_words_detection(self):
        """
        敏感词检测
        :return:
        """
        sensitive_words_detection_url = "{}/interface/ask/add".format(self.HQCHIP_URL)
        sensitive_words_detection_body = {
            "appid": "spider",
            "title": self.title,  #问题标题
            "seo_title": self.seo_title,  # SEO标题
            "seo_keyword": self.seo_keyword,  # SEO关键词
            "seo_desc": self.seo_desc,  # SEO简介
            "reply_content": self.reply_content,  # 问题答案内容
        }
        sensitive_words_detection_response = self.rss.post(sensitive_words_detection_url, headers=self.headers_json,
                                                            json=sensitive_words_detection_body).json()
        print(sensitive_words_detection_response)
        return sensitive_words_detection_response
if __name__ == '__main__':
    title = "测试敏感词"
    reply_content = "测试敏感词"
    seo_title = "习近平"
    seo_keyword = "测试敏感词"
    seo_desc = "测试敏感词"
    sensitive_words_detection = SensitiveWordsDetection(title="测试敏感词", reply_content="测试敏感词",
                                                        seo_title=seo_title, seo_keyword=seo_keyword, seo_desc=seo_desc).sensitive_words_detection()