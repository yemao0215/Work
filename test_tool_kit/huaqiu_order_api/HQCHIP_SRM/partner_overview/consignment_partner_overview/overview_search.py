import json
import math
import time
from datetime import datetime, timedelta

import jsonpath
import yaml
from xpinyin import Pinyin

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, partnerYaml_dir
from huaqiu_order_api.common.yaml_handler import write_yaml


class PartnerOverviewSearch:
    # 审核中心操作

    def __init__(self, target_rss):
        """
        :param subject_name 搜索主题名称
        :param passtask_body_supplierCode 审核方法里面请求参数boy的supplierCode参数，不一定是供应商编码
        """
        self.srm_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.SRM_URL = data['SRM_URL']
    def parther_overview_search(self):

        search_url = "{}/partnermanage/sellGoodsCooperate/pageList".format(self.SRM_URL)
        supplierHtName_count = []
        for m in range(0, 2):
            search_body = {"header": {"pageNum": 1, "pageSize": 50},
                           "body": {
                               "transactionTag": m + 1,
                               "supplierName": "",
                               "supplierHtName": "",
                               "supplierSn": "",
                               "industry": "",
                               "qudaoFollower": "",
                               "statisticsStime": "",
                               "statisticsEtime": "",
                               "orderColumn": "",
                               "orderType": ""
                           }}
            search_res = self.srm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
            totalSize = jsonpath.jsonpath(search_res, '$..totalSize')[0]
            supplierHtName_count_list = []
            if totalSize != []:
                if int(totalSize) <= 50:
                    supplierHtName = jsonpath.jsonpath(search_res, '$..supplierHtName')
                    supplierHtName_count_list = supplierHtName
                else:
                    pageCount = math.ceil(int(totalSize) / 50)
                    for i in range(pageCount):
                        print(i)
                        search_body["header"]["pageNum"] = i + 1
                        search_res = self.srm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
                        supplierHtName = jsonpath.jsonpath(search_res, '$..supplierHtName')
                        print(supplierHtName)
                        supplierHtName_count_list = supplierHtName_count_list + supplierHtName
            supplierHtName_count = supplierHtName_count + supplierHtName_count_list
        print(supplierHtName_count)
        with open(partnerYaml_dir, 'w', encoding='utf-8') as file:
            file.write('items:\n')
            for item in supplierHtName_count:
                file.write(f'  - {item}\n')


if __name__ == '__main__':
    target_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
    PartnerOverviewSearch(target_rss).parther_overview_search()

