import json

import requests
import yaml

from huaqiu_order_api.common.my_path import yaml_file


class RcsOpenApi:
    # 风控对外接口
    def __init__(self, body, address):
        self.rss = requests.Session()

        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.RCS_URL = data['RCS_URL']
        self.body = body
        if not self.body["nameListData"]:
            key_list = ["icOrderList", "smtOrderList", "pcbOrderList"]
            for key in key_list:
                if key in self.body["sourceData"]:
                    self.body["sourceData"][key]["address"] = address
        else:
            if "address" in self.body["nameListData"]:
                self.body['nameListData']["address"] = address
    def address_rcs_open_api(self):
        address_rcs_open_api_url = "{}/api/query/index".format(self.RCS_URL)
        print(f"请求地址：{address_rcs_open_api_url}")
        address_rcs_open_api_body = self.body
        print(f"请求参数：{address_rcs_open_api_body}")
        address_rcs_open_api_res = self.rss.post(url=address_rcs_open_api_url, json=address_rcs_open_api_body,
                                                headers=self.headers_json).json()
        # print(f"请求结果：{address_rcs_open_api_res}")
        # 代码：replace("'", '"') 将单引号替换为双引号
        res_json = json.dumps(address_rcs_open_api_res, ensure_ascii=False).replace("'", '"')
        print(f"请求结果：{address_rcs_open_api_res}")
if __name__ == '__main__':
    body = {
            "appid": "自己项目名称，例:ic、pcb、smt",
            "strategyId": 21,
            "nameListData": {},
            "sourceData": {
                "smtOrderList": {
                    "engineerPhone": "工程师手机",
                    "address": "收货地址",
                    "activityFlag": "activityFlag",
                    "orderId": "订单ID",
                    "address_ppcvs": "收货地址(省级/地级/县级/乡级/街道)",
                    "engineerEmail": "工程师邮箱",
                    "pickerPhone": "自提人手机号",
                    "consigneePhone": "收货人手机",
                    "orderEmail": "下单人邮箱",
                    "orderPhone": "下单人手机"
                }
            }
        }
    # body = {
    #           "appid": "自己项目名称，例:ic、pcb、smt",
    #           "strategyId": 27,
    #           "nameListData": {},
    #           "sourceData": {
    #             "icOrderList": {
    #               "address_ppcv": "收货地址(省级/地级/县级/乡级)",
    #               "address": "广西壮族自治区防城港市防城区新一代产业园1栋6楼",
    #               "orderSn": "订单编号",
    #               "address_ppc": "收货地址(省级/地级/县级)",
    #               "address_ppcvs": "收货地址(省级/地级/县级/乡级/街道)"
    #             }
    #           }
    #         }
    address = "北京市北京市平谷区楼子"
    RcsOpenApi(body, address).address_rcs_open_api()
