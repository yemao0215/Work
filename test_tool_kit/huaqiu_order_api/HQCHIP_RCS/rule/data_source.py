import json

import jsonpath
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class DataSource:
    # 风控中台规则管理-数据源列表
    def __init__(self, target_rss):
        self.rcs_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.RCS_URL = data["RCS_URL"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.phone = account["PassPort"]["phone"]
        self.keyword = "多个值判断"

    def data_source_list(self, form=None):
        """数据源列表"""
        data_source_list_url = "{}/api/admin/source/page".format(self.RCS_URL)
        data_source_list_body = {"keyword": "", "pageNum": 1, "pageSize": 50}
        data_source_list_res = self.rcs_rss.post(url=data_source_list_url, json=data_source_list_body, headers=self.json_head).json()
        sourceId = jsonpath.jsonpath(data_source_list_res, '$..sourceId')
        sourcekey = jsonpath.jsonpath(data_source_list_res, '$..sourceKey')

        for i in range(len(sourcekey)):
            if str(form) in sourcekey[i]:
                source_id = sourceId[i]
                logger.info("数据源类型：" + str(form) + ",获取数据源id成功，获取的数据源id为：" + str(source_id))
                # 获取参数
                params_url = "{}/api/admin/source/params".format(self.RCS_URL)
                params_body = {"sourceId": source_id}
                params_res = self.rcs_rss.post(url=params_url, json=params_body, headers=self.json_head).json()
                params = json.loads(jsonpath.jsonpath(params_res, '$.body')[0])
                params_dict = {k: '' for k in params}
                params_dict['data'] = {k: '' for k in params['data']}
                setattr(Data, 'sourceId', source_id)
                setattr(Data, 'params_dict', params_dict)
                self.sourcekey = sourcekey[i]
                break
            else:
                logger.error("数据源类型：" + str(form) + ",获取数据源id异常\033[00m")
        return self
    def tactics_obtain(self):
        """策略获取"""
        # self.sourcekey = "smtOrderList"
        tactics_obtain_url = "{}/api/admin/strategy/page".format(self.RCS_URL)
        tactics_obtain_body = {"keyword": self.keyword, "status": 0, "pageNum": 1, "pageSize": 50}
        tactics_obtain_res = self.rcs_rss.post(url=tactics_obtain_url, json=tactics_obtain_body, headers=self.json_head).json()
        strategyId = jsonpath.jsonpath(tactics_obtain_res, '$..strategyId')[0]
        logger.info(f"获取到策略：{self.keyword}的策略id：{strategyId}")
        tactics_obtain_params_url = "{}/api/admin/strategy/getParam".format(self.RCS_URL)
        tactics_obtain_params_body = {"strategyId": strategyId}
        tactics_obtain_params_res = self.rcs_rss.post(url=tactics_obtain_params_url, json=tactics_obtain_params_body,headers=self.json_head).json()
        tactics_obtain_params = jsonpath.jsonpath(tactics_obtain_params_res, '$.body')[0]
        sourceData = tactics_obtain_params["sourceData"]
        params_dict = {k: '' for k in tactics_obtain_params}
        sourceData_key = list(sourceData.keys())
        sourceData[f'{sourceData_key[0]}'] = {k: '' for k in sourceData[f'{sourceData_key[0]}']}
        params_dict["sourceData"] = sourceData
        setattr(Data, 'strategyId', strategyId)
        setattr(Data, 'tactics_params_dict', params_dict)
        return self
if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    target_rss = SOOLogin("uat-rcs.huaqiu.com", "api").target_login()
    DataSource(target_rss).data_source_list("ic").tactics_obtain()