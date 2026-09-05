import json

import jsonpath
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class Hc2018StockMange:
    def __init__(self, target_rss):
        self.dos_rss = target_rss
        dos_auth_token = getattr(Data, 'dos_auth_token')
        self.json_head = {"Content-Type": "application/json", "Authorization": dos_auth_token}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.warehouse_type = account["HQCHIP_GOODS"]["warehouse_id"]
        self.dos_goods_id = account["HQCHIP_GOODS"]["goods_id"]
        self.number = account["HQCHIP_GOODS"]["number"]


    def dos_out_goods_decide(self):
        """判断库存是否满足出库"""
        warehouse_name = ''
        if self.warehouse_type == 2:
            warehouse_name = "深圳华秋东莞仓"
        elif self.warehouse_type == 8:
            warehouse_name = "长沙仓"
        inventory_goods_url = "{}/v1/pricing/StockPricing/getStockList".format(self.HC2018_ADMIN_URL)
        inventory_goods_body = {"goods_id": self.dos_goods_id, "erp_type": -1, "hasGuidePrice": "0", "is_on_sale": "0",
                                "order_sort": 1, "stair_id": -1, "tag_type": -1, "page": 1, "per_page": 100}
        inventory_goods_res = self.dos_rss.post(url=inventory_goods_url, json=inventory_goods_body,
                                                headers=self.json_head).json()
        goods_resultInfo = jsonpath.jsonpath(inventory_goods_res, '$..warehouse_info')[0]
        erp_goods_sn = jsonpath.jsonpath(inventory_goods_res, '$..erp_goods_sn')[0]
        logger.info(f"库存id：{self.dos_goods_id}的ERP编码为：{erp_goods_sn}")
        spot_number = []
        warehouse_id = []
        for i in range(len(goods_resultInfo)):
            spot_number.append(goods_resultInfo[i]["spot_number"])
            warehouse_id.append(goods_resultInfo[i]["warehouse_id"])
        spot_number_warehouse = 0
        for m in range(len(warehouse_id)):
            if warehouse_id[m] == str(self.warehouse_type):
                spot_number_warehouse = spot_number_warehouse + int(spot_number[m])
        if spot_number_warehouse >= int(self.number):
            dos_msg = f"库存id：{self.dos_goods_id}，符合dos出库要求，此时库存id：{self.dos_goods_id}的仓库：{warehouse_name}的可用库存为：{spot_number_warehouse}"
            logger.info(dos_msg)
            # 将获取的登录的token往Data里面作虚拟存储以【dos_auth_token】命名以便后续提取
            setattr(Data, 'erp_goods_sn', erp_goods_sn)
        else:
            dos_msg = f"库存id：{self.dos_goods_id}，不符合dos出库要求，此时库存id：{self.dos_goods_id}的仓库：{warehouse_name}的可用库存为：{spot_number_warehouse}"
            logger.error(dos_msg)
        return dos_msg
if __name__ == '__main__':
        target_rss = Login().login()
        Hc2018StockMange(target_rss).dos_out_goods_decide()
