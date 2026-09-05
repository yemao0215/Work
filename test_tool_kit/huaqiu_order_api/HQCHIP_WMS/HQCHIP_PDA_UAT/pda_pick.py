import time

import jsonpath
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class PdaPick:
    def __init__(self, pda_rss):
        """
        :param sourcebillnumber 预出库单号
        :param distributionLabel 货品标签
        """
        self.pda_rss = pda_rss
        self.json_head = {"Content-Type": "application/json"}
        self.theupper_headers = {"Content-Type": "x-www-from-urlencodeed", "User-Agent":"okhttp/3.14.9", "Connection":"keep-alive"}
        self.pda_json_head = {"Content-Type": "application/json", "User-Agent": "okhttp/3.14.9","Connection": "keep-alive"}
        # self.sourcebillnumber = sourcebillnumber
        self.originalNumber = ''
        # self.distributionLabel = distributionLabel
        self.taskId = ''
        self.label_id = ''
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.WMS_URL = data["WMS_URL"]
        self.sourcebillnumber = getattr(Data, 'sourcebillnumber')
        # self.sourcebillnumber = "DO230914000007"
        # 从Data 提取 distributionLabels 注意distributionLabels为list列表
        self.distributionLabels = getattr(Data, 'distributionLabels')
        # self.distributionLabels = ["LL230830000006"]


    def pda_pick(self):
        for i in range(len(self.distributionLabels)):
            self.distributionLabel = self.distributionLabels[i]
            try:
                # execute_pick_url ='{}/wms/warehouse/pda/worktask/getFinishedPickTask?page=1&billCode={}&labelNumber='.format(self.WMS_URL, self.sourcebillnumber)
                execute_pick_url = '{}/wms/warehouse/pda/worktask/getPickTaskByBillCode?page=1&billCode={}&labelNumber='.format(self.WMS_URL, self.sourcebillnumber)
                logger.info(execute_pick_url)
                pick_res1 = self.pda_rss.get(url=execute_pick_url, headers=self.pda_json_head)  # 执行拣货1
                logger.info(f"执行拣货步骤1,返回结果:{pick_res1.json()}")
                # task_id = jsonpath.jsonpath(pick_res1.json(), '$..taskId')[0]
                # self.taskId = task_id
                # logger.info(f"执行拣货步骤2,获取到taskId:{task_id}")
                result = pick_res1.json()['result']
                task_id = []
                labelNumber = []
                for i in range(len(result)):
                    task_id.append(result[i]["taskId"])
                    labelNumber.append(result[i]["labelNumber"])
                logger.info(task_id)
                for m in range(len(labelNumber)):
                    if labelNumber[m] == self.distributionLabel:
                        self.taskId = task_id[m]
                logger.info(f"执行拣货步骤2,获取到taskId:{self.taskId}")
                time.sleep(1)
            except Exception:
                execute_pick_url2 = self.WMS_URL + f'/wms/warehouse/pda/worktask/getPickTaskByBillCode?billCode={self.sourcebillnumber}&page=1'
                execute_pick_res = self.pda_rss.get(url=execute_pick_url2, headers=self.pda_json_head).json()  # 执行拣货2
                logger.info(f"执行拣货步骤2,返回结果:{execute_pick_res}")
                task_id = jsonpath.jsonpath(execute_pick_res, '$..taskId')[0]
                self.taskId = task_id
                logger.info(f"执行拣货步骤2,获取到taskId:{task_id}")
                time.sleep(1)

            set_label_url = self.WMS_URL + f'/wms/warehouse/pda/worktask/getPickLabelInfoByLabelNumber?labelNumber={self.distributionLabel}'
            logger.info(set_label_url)
            set_label_res = self.pda_rss.get(url=set_label_url, headers=self.pda_json_head).json()  # 输入标签1
            logger.info(f"输入拣货标签:{self.distributionLabel},返回结果:{set_label_res}")
            label_id = jsonpath.jsonpath(set_label_res, '$..id')[0]
            self.label_id = label_id
            logger.info(f"输入拣货标签获取到label_id:{label_id}")
            time.sleep(1)

            set_label_url2 = self.WMS_URL + f'/wms/warehouse/pda/worktask/getFinishedPickTask?page=1&billCode={self.sourcebillnumber}&labelNumber={self.distributionLabel}'
            logger.info(set_label_url2)
            set_label_res2 = self.pda_rss.get(url=set_label_url2, headers=self.pda_json_head)  # 输入标签2
            logger.info(f"输入标签步骤2,返回结果:{set_label_res2.json()}")
            time.sleep(1)

            truncation_url = self.WMS_URL + f'/wms/warehouse/pda/worktask/cutOffTask?taskId={self.taskId}&labelId={self.label_id}'
            logger.info(truncation_url)
            truncation_res = self.pda_rss.get(url=truncation_url, headers=self.pda_json_head)  # 截料
            logger.info(f"操作截料步骤1,返回结果:{truncation_res.json()}")
            time.sleep(1)

            truncation_url2 = self.WMS_URL + f'/wms/warehouse/pda/worktask/getPickTaskByLabelNumber?labelNumber={self.distributionLabel}&billNumber={self.sourcebillnumber}&page=1'
            logger.info(truncation_url2)
            truncation_res2 = self.pda_rss.get(url=truncation_url2, headers=self.pda_json_head)  # 截料2
            logger.info(f"操作截料步骤2,返回结果:{truncation_res2.json()}")
            time.sleep(1)
        logger.debug('=*' * 50)
        return self

if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_login import PdaLogin
    pda_rss = PdaLogin().pda_login()
    PdaPick(pda_rss).pda_pick()   # 预出库单  商品标签


