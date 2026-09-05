import time

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_FAT.PDA_login import FATPdaLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class FATPdaTheupper:

    # FAT环境
    def __init__(self, pda_rss):
        """
        :param labels 货品标签
        """
        self.pda_rss = pda_rss
        self.json_head = {"Content-Type": "application/json"}
        self.theupper_headers = {"Content-Type": "x-www-from-urlencodeed", "User-Agent":"okhttp/3.14.9", "Connection":"keep-alive"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.WMS_FAT_URL = data["WMS_FAT_URL"]
        self.labelNumber_sn = getattr(Data, 'labelNumber_sn')
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.warehouse_type = int(account["HQCHIP_GOODS"]["warehouse_id"])

    def pda_theupper(self):
        """
        :param targetLocationCode 上架推荐库位
        """
        retMsg = None
        self.labelNumber_sn_new = []
        for i in range(len(self.labelNumber_sn)):
            #上架步骤1：
            theupper_labelNumber_url = "{}/wms/warehouse/pda/worktask/getShelvesTaskInfoByLabelNumber?labelNumber={}".format(self.WMS_FAT_URL, self.labelNumber_sn[i])
            pda_theupper_res1 = self.pda_rss.get(url=theupper_labelNumber_url,headers=self.theupper_headers).json()
            logger.info(f"扫描商品标签成功，返回结果:{pda_theupper_res1}")
            #上架步骤2：
            try:
                self.targetLocationCode = pda_theupper_res1["result"]["locationCode"]
                logger.info(self.targetLocationCode)
                theupper_LocationCode_url = "{}/wms/warehouse/pda/worktask/confirmShevlesTask?locationCode={}".format(self.WMS_FAT_URL, self.targetLocationCode)
                pda_theupper_res2 = self.pda_rss.get(url=theupper_LocationCode_url,headers=self.theupper_headers).json()
                logger.info(f"扫描储位成功，返回结果:{pda_theupper_res2}")
                if pda_theupper_res2["result"] == None:
                    retMsg = pda_theupper_res2["retMsg"]
                    if retMsg == "项目储位货品只能上架到项目储位或PCBA自营储位":
                        logger.info(f"项目储位货品只能上架到项目储位或PCBA自营储位,库存选择为项目储位或PCBA自营储位")
                        if self.warehouse_type == 2:
                            self.targetLocationCode = "PCBA20001"
                        elif self.warehouse_type == 8:
                            self.targetLocationCode = "PCBA00001"
                        else:
                            pass
                        theupper_LocationCode_url = "{}/wms/warehouse/pda/worktask/confirmShevlesTask?locationCode={}".format(self.WMS_FAT_URL, self.targetLocationCode)
                        pda_theupper_res2 = self.pda_rss.get(url=theupper_LocationCode_url, headers=self.theupper_headers).json()
                        logger.info(f"扫描储位成功，返回结果:{pda_theupper_res2}")
            except TypeError as e:
                print(e)
                if e.args[0] == "'NoneType' object is not subscriptable":
                    self.labelNumber_sn_new.append(self.labelNumber_sn[i])
        if self.labelNumber_sn_new != []:
           retMsg = f"商品标签：{self.labelNumber_sn_new}没有找到，请检查商品标签！！！"
        return retMsg

if __name__ == '__main__':
    pda_rss = FATPdaLogin().pda_login()
    FATPdaTheupper(pda_rss).pda_theupper()