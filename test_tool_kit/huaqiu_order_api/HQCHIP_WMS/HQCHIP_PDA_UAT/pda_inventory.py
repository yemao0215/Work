import json
import time

import jsonpath
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class PdaInventory:
    def __init__(self, pda_rss):
        """
        :param InventoryNo  盘点单号
        """
        self.pda_rss = pda_rss
        self.json_head = {"Content-Type": "application/json"}
        self.theupper_headers = {"Content-Type": "x-www-from-urlencodeed", "User-Agent":"okhttp/3.14.9", "Connection":"keep-alive"}
        self.pda_json_head = {"Content-Type": "application/json", "User-Agent": "okhttp/3.14.9","Connection": "keep-alive"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.WMS_URL = data["WMS_URL"]
        self.InventoryNo = getattr(Data, 'inventory_no', '')
        # self.InventoryNo = "PD240801000003"


    def pda_inventory(self):
        """
        盘点单操作
        :return:
        """
        # 盘点单查询
        search_url = "{}/wms/warehouse/pda/inventoryCheck/selectPdaUnInvRecordPage".format(self.WMS_URL)
        print(search_url)
        search_body = {"inventoryNo": self.InventoryNo}
        search_res = self.pda_rss.post(url=search_url, json=search_body, headers=self.pda_json_head).json()
        print(json.dumps(search_res, ensure_ascii=False).replace("'", '"'))
        msg = None
        if search_res["result"] != []:
            self.labelNumber = jsonpath.jsonpath(search_res, "$..labelNumber")
            self.locationCode = jsonpath.jsonpath(search_res, "$..locationCode")
            self.labelBookQty = jsonpath.jsonpath(search_res, "$..labelBookQty")
            for i in range(len(self.labelNumber)):
                # 根据库位号，标签号查询盘点信息
                print(f"根据库位号，标签号查询盘点信息：{self.locationCode[i]}, {self.labelNumber[i]}")
                label_location_search_url = "{}/wms/warehouse/pda/inventoryCheck/getSingleInvCheckRecord?inventoryNo={}&locationCode={}&labelNumber={}".format(self.WMS_URL, self.InventoryNo, self.locationCode[i], self.labelNumber[i])
                label_location_search_res = self.pda_rss.get(url=label_location_search_url, headers=self.pda_json_head).json()
                self.goodsCode = jsonpath.jsonpath(search_res, "$..goodsCode")[0]
                self.labelNumber = jsonpath.jsonpath(search_res, "$..labelNumber")[0]
                self.labelCheckQty = jsonpath.jsonpath(label_location_search_res, "$..labelCheckQty")[0]
                self.inventorycheckRecordId = jsonpath.jsonpath(label_location_search_res, "$..id")[0]
                # 盘点
                inventoryCheck_url = "{}/wms/warehouse/pda/inventoryCheck/inventoryCheckIn".format(self.WMS_URL)
                inventoryCheck_body = {
                    "inventoryCheckNo": self.InventoryNo,
                    "inventorycheckRecordId": self.inventorycheckRecordId,
                    "labelCheckQty": self.labelCheckQty
                }
                search_res = self.pda_rss.post(url=inventoryCheck_url, json=inventoryCheck_body, headers=self.pda_json_head).json()
                print(json.dumps(search_res, ensure_ascii=False).replace("'", '"'))
                if search_res["errInfo"] == None:
                    logger.info(f"货品编码：{self.goodsCode}的货品标签：{self.labelNumber} 盘点成功")
                else:
                    logger.error(f"货品编码：{self.goodsCode}的货品标签：{self.labelNumber} 盘点失败")
                    msg = f"货品编码：{self.goodsCode}的货品标签：{self.labelNumber} 盘点失败"
        return msg

if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_login import PdaLogin
    pda_rss = PdaLogin().pda_login()
    PdaInventory(pda_rss).pda_inventory()
