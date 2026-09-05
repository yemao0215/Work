import re
import time
from datetime import datetime
import datetime as dt

import requests
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.OpenAPI_Order.pay_order import  PayOrder

# class DateEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, datetime):
#             return obj.strftime('%Y-%m-%d %H:%M:%S')
#         elif isinstance(obj, date):
#             return obj.strftime("%Y-%m-%d")
#         else:
#             return json.JSONEncoder.default(self, obj)

class ErpWanHongOut:


    def __init__(self, rss):
        """
        :param account:  登录ERP账号
        :param psw:  登录ERP密码
        :param order_sn:  前台商城生成订单编号
        :param uesr:    前台商城生成订单编号的用户名称
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.warehouse_type = account["HQCHIP_GOODS"]["warehouse_id"]
        self.vat_type = account["HQCHIP_GOODS"]["vat_type"]
        self.number = account["HQCHIP_GOODS"]["number"]
        # self.password = psw
        self.order_sn = getattr(Data, 'wanhong_order_sn')
        # self.order_sn = "S2023113071444"
        # self.uesr = getattr(Data, 'username')
        self.rss = rss
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }

    def out_order_cancellat(self):
        search_url = '{}/Orderinfo/index'.format(self.ERP_URL)
        search_body = {'keytype': 'order_sn', 'keyword': self.order_sn, 'start_time': '2023-01-01'}
        logger.info(f"搜索订单编号: {self.order_sn}")
        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers,
                                   timeout=1000).text  # 搜索订单，获取order_id
        # print(search_res)
        # logger.info(re.search('(<a href="/Orderinfo/detail\?id=)([0-9]{6})', search_res))
        search_res_excerpt = search_res.split('<tr target="id"')[1].split('<div class="pages">')[0]
        order_id = re.search('(<a href="/Orderinfo/detail\?id=)([0-9]{6})', search_res).group(2)
        logger.info(f"搜索完成,获取到order_id: {order_id}")

    def out_order_queuePush(self):
        self.order_id = "302593"
        out_order_queuePush_url = "{}/Service/ConvertSubject/putConvertRemovalWms".format(self.ERP_URL)
        out_order_queuePush_body = {"order_id": self.order_id}
        out_order_queuePush_res = self.rss.post(url=out_order_queuePush_url,data=out_order_queuePush_body, headers=self.headers).json()
        logger.info(out_order_queuePush_res)


if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
    # rss = ErpLogin().login()
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin

    target_rss = SOOLogin("uat-e.hqchip.com", "AuthLogin").target_login()
    ErpWanHongOut(target_rss).out_order_queuePush()