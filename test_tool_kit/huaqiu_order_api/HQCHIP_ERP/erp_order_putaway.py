import re
import time
from datetime import datetime
import datetime as dt

import requests
import yaml
from bs4 import BeautifulSoup

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_login import PdaLogin
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_theupper import PdaTheupper
from huaqiu_order_api.HQCHIP_WMS.wms_in_warehouse import WmsInWarehouse
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

class ErpOrderPutaway:
    # 入库管理
    def __init__(self, rss, keytype_search_name=None):
        """
        :param account:  登录ERP账号
        :param psw:  登录ERP密码
        :param relevance_order_sn:  关联订单号
        :param keytype_search_name:    查询类型名称
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']
        self.relevance_order_sn = getattr(Data, 'relevance_order_sn', '')
        # self.relevance_order_sn = "SP23072080746"
        self.rss = rss
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.keytype_search = {"p.putaway_sn": "入库单号", "p.order_sn": "关联采购单号", "i.goods_name": "商品名称", "s.delivery_sn": "物流号",
                               "bg.declare_order_sn": "代理单号", "s.shipping_name": "物流公司", "bg.agent_delivery_sn": "代理物流单号"}
        self.keytype_search_name = keytype_search_name
    def putaway_order_search(self):
        """根据关联单号查询待入库单号"""
        inn_sn_count = []
        inn_status_count = []
        inn_warehouse_count = []
        inn_sn_status_no = None
        for key, v in self.keytype_search.items():
            if self.keytype_search_name !=None:
                if self.keytype_search_name == v:
                    self.keytype = key
                    break
            else:
                self.keytype = "p.putaway_sn"
        putaway_order_search_url = '{}/putaway'.format(self.ERP_URL)
        putaway_order_search_body = {"pageNum": 1, "numPerPage": 100, "keytype": self.keytype, "keyword": self.relevance_order_sn,
                                     "is_sign": 0, "putaway_type": 0}
        putaway_order_search_res = self.rss.post(putaway_order_search_url, data=putaway_order_search_body, headers=self.headers).text
        putaway_id = re.findall('<tr target="sid_putaway_id" rel="(.*?)"', putaway_order_search_res)
        if putaway_id != []:
            soup = BeautifulSoup(putaway_order_search_res, 'html.parser')
            table = soup.find('tbody')
            rows = table.find_all('tr')
            inn_sn_column = []
            inn_status_column = []
            inn_warehouse_column = []
            # for row in rows[1:]: # 跳过表头
            for row in rows:  # 不跳过表头
                cells = row.find_all('td')
                inn_sn_column.append(cells[2].text)
                inn_status_column.append(cells[-1].text.strip())
                inn_warehouse_column.append(cells[-5].text.strip())
            inn_sn_count = inn_sn_count + inn_sn_column
            inn_status_count = inn_status_count + inn_status_column
            inn_warehouse_count = inn_warehouse_count + inn_warehouse_column
            # 提取待签收和验收中且入库仓库为深圳华秋东莞仓的入库单号
            inn_sn_status_no = [i for i, j, k in zip(inn_sn_count, inn_status_count, inn_warehouse_count) if (j == '待签收' or j == '验收中') and k == '深圳华秋东莞仓']
            print(inn_sn_status_no)
            if len(inn_sn_status_no) >= 1:
                # print(111)
                inn_sn = inn_sn_status_no[0]
            else:
                # print(112)
                inn_sn = inn_sn_status_no
            setattr(Data, 'inn_sn', inn_sn)
            print(inn_sn)
        return inn_sn_status_no
if __name__ == '__main__':

    from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
    rss = ErpLogin().login()
    inn_sn_status_no = ErpOrderPutaway(rss, "关联采购单号").putaway_order_search()
    wms_target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
    if inn_sn_status_no != []:
        for i in inn_sn_status_no:
            if i != "IN00154560":
                setattr(Data, 'inn_sn', i)
                print(f"待入库单: {i}")
                WmsInWarehouse(wms_target_rss).wms_warehousing().wms_theupper_list(theupper_sn='', status='')
                pda_rss = PdaLogin().pda_login()
                PdaTheupper(pda_rss).pda_theupper()

