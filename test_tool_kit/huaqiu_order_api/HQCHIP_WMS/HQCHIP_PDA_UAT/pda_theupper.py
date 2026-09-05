import time

import jsonpath
import requests
import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_login import PdaLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class PdaTheupper:

    # FAT环境
    def __init__(self, pda_rss):
        """
        :param labels 货品标签
        """
        self.pda_rss = pda_rss
        self.json_head = {"Content-Type": "application/json"}
        self.theupper_headers = {"Content-Type": "x-www-from-urlencodeed", "User-Agent":"okhttp/3.14.9", "Connection":"keep-alive"}
        self.labelNumber_sn = getattr(Data, 'labelNumber_sn')
        # self.labelNumber_sn = [ 'LL240319000016']
        self.targetLocationCode = getattr(Data, 'targetLocationCode')
        # self.targetLocationCode = ['2C030307']
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.WMS_URL = data["WMS_URL"]

    def pda_theupper(self):
        """PDA上架操作"""
        retMsg = None
        for i in range(len(self.labelNumber_sn)):
            #上架步骤1：
            theupper_labelNumber_url = "{}/wms/warehouse/pda/worktask/getShelvesTaskInfoByLabelNumber?labelNumber={}".format(self.WMS_URL,self.labelNumber_sn[i])
            pda_theupper_res1 = self.pda_rss.get(url=theupper_labelNumber_url, headers=self.theupper_headers).json()
            logger.info(f"扫描商品标签成功,此时labelNumber为{self.labelNumber_sn[i]}，返回结果:{pda_theupper_res1}")

            if pda_theupper_res1["result"] == None:
                retMsg = pda_theupper_res1["retMsg"]
                # return retMsg
            else:
                #上架步骤2：
                if self.targetLocationCode[i] == None:
                    # 库位为空指定一个库存给商品
                    self.targetLocationCode[i] = "2C030307"
                theupper_LocationCode_url = "{}/wms/warehouse/pda/worktask/confirmShevlesTask?locationCode={}".format(self.WMS_URL, self.targetLocationCode[i])
                pda_theupper_res2 = self.pda_rss.get(url=theupper_LocationCode_url, headers=self.theupper_headers).json()
                logger.info(f"扫描储位成功，返回结果:{pda_theupper_res2}")
        return retMsg

if __name__ == '__main__':
    pda_rss = PdaLogin().pda_login()
    PdaTheupper(pda_rss).pda_theupper()