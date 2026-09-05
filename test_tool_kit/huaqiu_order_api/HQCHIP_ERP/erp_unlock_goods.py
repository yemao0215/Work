import re
import time
from datetime import datetime
import datetime as dt

import requests
import yaml

from huaqiu_order_api.HQCHIP_SCM.scm_stock.stock_lock.stock_lock import StockLock
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

class ErpUnlockGoods:


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
        # self.order_sn = getattr(Data, 'ic_order_sn')
        self.order_sn = "S2024013029464"
        self.rss = rss
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }

    def erp_order_detail_search(self):
        order_search_url = '{}/Orderinfo/index'.format(self.ERP_URL)
        try:
            logger.info(11)
            search_body = {'keytype': 'order_sn', 'keyword': self.order_sn, 'start_time': '2023-01-01'}
            logger.info(f"搜索订单编号: {self.order_sn}")
            search_res = self.rss.post(url=order_search_url, data=search_body, headers=self.headers,
                                   timeout=1000).text  # 搜索订单，获取order_id
            search_res_excerpt = search_res.split('<tr target="id"')[1].split('<div class="pages">')[0]
            # 修改正则表达式以匹配不指定数字位数的情况，可以将{6}替换为 +
            order_id = re.search('(<a href="/Orderinfo/detail\?id=)([0-9]+)', search_res_excerpt).group(2)
        except IndexError:
            logger.info(12)
            search_body = {'keytype': 'order_sn', 'keyword': self.order_sn, 'company': '2804887'}
            logger.info(f"搜索订单编号: {self.order_sn}")
            search_res = self.rss.post(url=order_search_url, data=search_body, headers=self.headers,
                                   timeout=1000).text  # 搜索订单，获取order_id
            search_res_excerpt = search_res.split('<tr target="id"')[1].split('<div class="pages">')[0]
            # 修改正则表达式以匹配不指定数字位数的情况，可以将{6}替换为 +
            order_id = re.search('(<a href="/Orderinfo/detail\?id=)([0-9]+)', search_res_excerpt).group(2)
        logger.info(f"订单id：{order_id}")
        if order_id != None:
            order_detail_url = "{}/Orderinfo/detail?id={}".format(self.ERP_URL, order_id)
            order_detail_res = self.rss.get(url=order_detail_url, headers=self.headers,timeout=1000).text #获取明细id
            # 使用了Python的列表推导式和正则表达式模块re来提取字符串中的数字。
            # 具体来说，它使用re.findall()函数在字符串order_detail_res中查找所有匹配正则表达式(<tr target="id" rel=")([0-9]+)的子串，
            detail_id_list = [item[1] for item in re.findall('(<tr target="id" rel=")([0-9]+)', order_detail_res)]
            detail_goods_list = [item[1] for item in re.findall('(title="(.+?)关税确认)', order_detail_res)]
            detail_goods_id = [item[1] for item in re.findall('(<a href="/Goods/detail/id/(\d+)/pass/1)', order_detail_res)]

            # 判断list是否存在重复的值
            if len(detail_goods_list) != len(set(detail_goods_list)) and len(detail_goods_id) != len(set(detail_goods_id)):
                print("存在重复值")
                # 使用set数据结构来实现list去重
                detail_goods_list = list(set(detail_goods_list))
                detail_goods_id = list(set(detail_goods_id))
            logger.info(f"明细列表：{detail_id_list}，型号列表：{detail_goods_list}, 型号id列表: {detail_goods_id}")
            setattr(Data, "detail_id_list", detail_id_list)
            setattr(Data, "detail_goods_list", detail_goods_list)
            setattr(Data, "detail_goods_id", detail_goods_id)
        return self
    def erp_unlock_goods(self):
        self.order_item_id = getattr(Data, 'detail_id_list')
        if self.order_item_id != []:
            unlock_goods_url = "{}/test/unlockgoods".format(self.ERP_URL)
            unlock_goods_body = {"type": 4, "id": self.order_item_id}
            unlock_goods_res = self.rss.post(url=unlock_goods_url, data=unlock_goods_body, headers=self.headers,
                                   timeout=1000).text
            print(unlock_goods_res)
        else:
            print(f"order_item_id不满足释放库存要求")
        return self

    def mian_unlock_goods(self):
        self.erp_order_detail_search()
        scm_rss = SOOLogin("uat-scm.huaqiu.com", "hqScm").target_login()
        StockLock(scm_rss).goods_lock_search()
        self.erp_unlock_goods()
        return self



if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
    # rss = ErpLogin().login()
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin

    target_rss = SOOLogin("uat-e.hqchip.com", "AuthLogin").target_login()
    ErpUnlockGoods(target_rss).mian_unlock_goods()



