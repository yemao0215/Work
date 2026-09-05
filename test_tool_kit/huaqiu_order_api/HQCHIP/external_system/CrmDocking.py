import json

import requests
import yaml

from huaqiu_order_api.common.my_path import yaml_file


class CrmDocking:

    def __init__(self, unionid=None):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.CRM_URL = data['CRM_URL']
        self.rss = requests.session()
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.unionid = unionid

    def addition_fee_tag_determine(self):
        """用户是否CRM加收服务费标识判断"""
        addition_fee_tag_determine_url = "{}/crm/customer/external/getSalespersonInfo".format(self.CRM_URL)
        print(addition_fee_tag_determine_url)
        addition_fee_tag_determine_body = {"hqId": self.unionid}
        addition_fee_tag_determine_res = self.rss.post(url=addition_fee_tag_determine_url, json=addition_fee_tag_determine_body, headers=self.headers_json).json()
        print(addition_fee_tag_determine_res)
        # print(json.dumps(addition_fee_tag_determine_res, ensure_ascii=False).replace("'", '"'))
        return self

if __name__ == '__main__':
    unionid = 5146221
    CrmDocking(unionid).addition_fee_tag_determine()
