import time

import jsonpath
import requests

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_login import PdaLogin
from huaqiu_order_api.common.loguru_logger import logger
class PdaPick:

    # FAT环境
    def __init__(self, pda_rss, sourcebillnumber,distributionLabel):
        """
        :param sourcebillnumber 预出库单号
        :param distributionLabel 货品标签
        """
        self.pda_rss = pda_rss
        self.json_head = {"Content-Type": "application/json"}
        self.theupper_headers = {"Content-Type": "x-www-from-urlencodeed", "User-Agent":"okhttp/3.14.9", "Connection":"keep-alive"}
        self.pda_json_head = {"Content-Type": "application/json", "User-Agent": "okhttp/3.14.9","Connection": "keep-alive"}
        self.sourcebillnumber = sourcebillnumber
        self.originalNumber = ''
        self.distributionLabel = distributionLabel
        self.taskId = ''
        self.label_id = ''


    def pda_pick(self):

        try:
            execute_pick_url = f'http://wms-api.elecfans.net/wms/warehouse/pda/worktask/getFinishedPickTask?page=1&billCode={self.sourcebillnumber}&labelNumber='
            pick_res1 = self.pda_rss.get(url=execute_pick_url, headers=self.pda_json_head)  # 执行拣货1
            logger.info(f"执行拣货步骤1,返回结果:{pick_res1.json()}")
            task_id = jsonpath.jsonpath(pick_res1.json(), '$..taskId')[0]
            self.taskId = task_id
            logger.info(f"执行拣货步骤2,获取到taskId:{task_id}")
            time.sleep(1)
        except Exception:
            execute_pick_url2 = f'http://wms-api.elecfans.net/wms/warehouse/pda/worktask/getPickTaskByBillCode?billCode={self.sourcebillnumber}&page=1'
            execute_pick_res = self.pda_rss.get(url=execute_pick_url2, headers=self.pda_json_head).json()  # 执行拣货2
            logger.info(f"执行拣货步骤2,返回结果:{execute_pick_res}")
            labelNumber =  jsonpath.jsonpath(execute_pick_res, '$..labelNumber')[0]
            task_id = jsonpath.jsonpath(execute_pick_res, '$..taskId')[0]
            self.taskId = task_id
            logger.info(f"执行拣货步骤2,获取到taskId:{task_id}")
            time.sleep(1)

        set_label_url = f'http://wms-api.elecfans.net/wms/warehouse/pda/worktask/getPickLabelInfoByLabelNumber?labelNumber={self.distributionLabel}'
        set_label_res = self.pda_rss.get(url=set_label_url, headers=self.pda_json_head).json()  # 输入标签1
        logger.info(f"输入拣货标签:{self.distributionLabel},返回结果:{set_label_res}")
        label_id = jsonpath.jsonpath(set_label_res, '$..id')[0]
        label_id = jsonpath.jsonpath(set_label_res, '$..id')[0]
        self.label_id = label_id
        logger.info(f"输入拣货标签获取到label_id:{label_id}")
        time.sleep(1)

        set_label_url2 = f'http://wms-api.elecfans.net/wms/warehouse/pda/worktask/getFinishedPickTask?page=1&billCode={self.sourcebillnumber}&labelNumber={self.distributionLabel}'
        set_label_res2 = self.pda_rss.get(url=set_label_url2, headers=self.pda_json_head)  # 输入标签2
        logger.info(f"输入标签步骤2,返回结果:{set_label_res2.json()}")
        time.sleep(1)

        truncation_url = f'http://wms-api.elecfans.net/wms/warehouse/pda/worktask/cutOffTask?taskId={self.taskId}&labelId={self.label_id}'
        truncation_res = self.pda_rss.get(url=truncation_url, headers=self.pda_json_head)  # 截料
        logger.info(f"操作截料步骤1,返回结果:{truncation_res.json()}")
        time.sleep(1)

        truncation_url2 = f'http://wms-api.elecfans.net/wms/warehouse/pda/worktask/getPickTaskByLabelNumber?labelNumber={self.distributionLabel}&billNumber={self.sourcebillnumber}&page=1'
        truncation_res2 = self.pda_rss.get(url=truncation_url2, headers=self.pda_json_head)  # 截料2
        logger.info(f"操作截料步骤2,返回结果:{truncation_res2.json()}")
        time.sleep(1)
        logger.debug('=*' * 50)
        return self

if __name__ == '__main__':
    pda_rss = PdaLogin().pda_login()
    PdaPick(pda_rss, "DO240116000001", "LL220714000001").pda_pick()   # 预出库单  商品标签
