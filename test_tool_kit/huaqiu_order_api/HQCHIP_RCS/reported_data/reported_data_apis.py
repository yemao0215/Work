import time

import jsonpath
import requests
import yaml


from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class ReportedData:
    # 风控中台规则管理-数据源列表
    def __init__(self, form):
        self.rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.RCS_URL = data["RCS_URL"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        # self.phone = account["PassPort"]["phone"]
        self.phone = "18240993643"
        self.sourceId = getattr(Data, 'sourceId')
        self.params_dict = getattr(Data, 'params_dict')
        self.tactics_params_dict = getattr(Data, 'tactics_params_dict')
        self.strategyId = getattr(Data, 'strategyId')
        self.phone2 = "18296275548"
        if form == "ic":
            self.order_id = getattr(Data, 'ic_order_id')
        elif form == "pcb":
            self.order_id = getattr(Data, 'pcb_order_id')
    def reported_data(self):
        """数据上报"""
        reported_data_url = "{}/api/dataReport".format(self.RCS_URL)
        timestamp = int(time.time())
        self.params_dict["data"]["engineerPhone"] = self.phone + "::seg::" + self.phone2
        self.params_dict["data"]["engineerEmail"] = self.phone + "@163.com" + "::seg::" + self.phone2 + "@126.com"
        self.params_dict["sourceId"] = self.sourceId
        self.params_dict["id"] = "uatTest-" + str(self.order_id)
        self.params_dict["time"] = timestamp
        reported_data_body = self.params_dict
        logger.info(reported_data_body)
        res = self.rss.post(url=reported_data_url, json=reported_data_body,headers=self.json_head).json()
        logger.info(res)
        return self
    def risk_evaluate(self):
        """风险评估"""
        risk_evaluate_url = "{}/api/query/index".format(self.RCS_URL)
        self.tactics_params_dict["appid"] = "test"
        self.tactics_params_dict["strategyId"] = self.strategyId

        # 单个手机号码
        sourceData_phone = self.tactics_params_dict["sourceData"]
        sourceData_key = list(sourceData_phone.keys())
        key_type_json_phone = sourceData_phone[f"{sourceData_key[0]}"]
        key_type_json_phone["engineerPhone"] = self.phone2
        self.tactics_params_dict["sourceData"] = sourceData_phone
        res = self.rss.post(url=risk_evaluate_url, json=self.tactics_params_dict, headers=self.json_head).json()
        logger.info(f"命中条件手机号码：{self.phone2}，执行结果为：{res}")

        # 多个手机号码
        sourceData_phones = self.tactics_params_dict["sourceData"]
        sourceData_key = list(sourceData_phones.keys())
        key_type_json_phones = sourceData_phone[f"{sourceData_key[0]}"]
        key_type_json_phones["engineerPhone"] = self.phone + "::seg::" + self.phone2
        self.tactics_params_dict["sourceData"] = sourceData_phones
        res = self.rss.post(url=risk_evaluate_url, json=self.tactics_params_dict, headers=self.json_head).json()
        logger.info(f"命中条件手机号码：{self.phone}和{self.phone2}，执行结果为：{res}")

        #单个邮箱
        sourceData_email = self.tactics_params_dict["sourceData"]
        sourceData_key = list(sourceData_email.keys())
        key_type_json_email = sourceData_email[f"{sourceData_key[0]}"]
        engineerEmail_Select = self.phone2 + "@126.com"
        key_type_json_email["engineerPhone"] = ""
        key_type_json_email["engineerEmail"] = engineerEmail_Select
        self.tactics_params_dict["sourceData"] = sourceData_email
        res = self.rss.post(url=risk_evaluate_url, json=self.tactics_params_dict, headers=self.json_head).json()
        logger.info(f"命中条件邮箱：{engineerEmail_Select}，执行结果为：{res}")

        #多个个邮箱
        sourceData_email = self.tactics_params_dict["sourceData"]
        sourceData_key = list(sourceData_email.keys())
        key_type_json_email = sourceData_email[f"{sourceData_key[0]}"]
        engineerEmail_Select = self.phone + "@163.com" + "::seg::" + self.phone2 + "@126.com"
        key_type_json_email["engineerPhone"] = ""
        key_type_json_email["engineerEmail"] = engineerEmail_Select
        self.tactics_params_dict["sourceData"] = sourceData_email
        res = self.rss.post(url=risk_evaluate_url, json=self.tactics_params_dict, headers=self.json_head).json()
        logger.info(f"命中条件邮箱：{self.phone + '@163.com'}和{self.phone2 + '@126.com'}，执行结果为：{res}")

        # 单个手机单个邮箱
        sourceData_phone_email = self.tactics_params_dict["sourceData"]
        sourceData_key = list(sourceData_phone_email.keys())
        key_type_json_phone_email = sourceData_phone_email[f"{sourceData_key[0]}"]
        engineerEmail_Select = self.phone2 + "@126.com"
        key_type_json_phone_email["engineerPhone"] = self.phone2
        key_type_json_phone_email["engineerEmail"] = engineerEmail_Select
        self.tactics_params_dict["sourceData"] = sourceData_email
        res = self.rss.post(url=risk_evaluate_url, json=self.tactics_params_dict, headers=self.json_head).json()
        logger.info(f"命中条件手机号码：{self.phone2} 和邮箱：{engineerEmail_Select}，执行结果为：{res}")

        # 单个手机多个邮箱
        sourceData_phone_email = self.tactics_params_dict["sourceData"]
        sourceData_key = list(sourceData_phone_email.keys())
        key_type_json_phone_email = sourceData_phone_email[f"{sourceData_key[0]}"]
        engineerEmail_Select = self.phone + "@163.com" + "::seg::" + self.phone2 + "@126.com"
        key_type_json_phone_email["engineerPhone"] = self.phone2
        key_type_json_phone_email["engineerEmail"] = engineerEmail_Select
        self.tactics_params_dict["sourceData"] = sourceData_email
        res = self.rss.post(url=risk_evaluate_url, json=self.tactics_params_dict, headers=self.json_head).json()
        logger.info(f"命中条件手机号码：{self.phone2} 和邮箱：{self.phone + '@163.com'}和{self.phone2 + '@126.com'}，执行结果为：{res}")

        # 多个手机单个邮箱
        sourceData_phone_email = self.tactics_params_dict["sourceData"]
        sourceData_key = list(sourceData_phone_email.keys())
        key_type_json_phone_email = sourceData_phone_email[f"{sourceData_key[0]}"]
        engineerEmail_Select = self.phone2 + "@126.com"
        key_type_json_phone_email["engineerPhone"] = self.phone + "::seg::" + self.phone2
        key_type_json_phone_email["engineerEmail"] = engineerEmail_Select
        self.tactics_params_dict["sourceData"] = sourceData_email
        res = self.rss.post(url=risk_evaluate_url, json=self.tactics_params_dict, headers=self.json_head).json()
        logger.info(f"命中条件手机号码：{self.phone}和{self.phone2} 和邮箱：{self.phone2 + '@126.com'}，执行结果为：{res}")

        # 多个手机多个邮箱
        sourceData_phone_email = self.tactics_params_dict["sourceData"]
        sourceData_key = list(sourceData_phone_email.keys())
        key_type_json_phone_email = sourceData_phone_email[f"{sourceData_key[0]}"]
        engineerEmail_Select = self.phone + "@163.com" + "::seg::" + self.phone2 + "@126.com"
        key_type_json_phone_email["engineerPhone"] = self.phone + "::seg::" + self.phone2
        key_type_json_phone_email["engineerEmail"] = engineerEmail_Select
        self.tactics_params_dict["sourceData"] = sourceData_email
        res = self.rss.post(url=risk_evaluate_url, json=self.tactics_params_dict, headers=self.json_head).json()
        logger.info(f"命中条件手机号码：{self.phone}和{self.phone2} 和邮箱：{self.phone + '@163.com'}和{self.phone2 + '@126.com'}，执行结果为：{res}")



if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
    from huaqiu_order_api.HQCHIP.ic_order import IcOrder
    from huaqiu_order_api.HQCHIP_RCS.rule.data_source import DataSource
    from huaqiu_order_api.HQPCB.main_run import RunPcb
    form = "pcb"
    for i in range(1):
        target_rss = SOOLogin("uat-rcs.huaqiu.com", "api").target_login()
        if form == "ic":
            rss = SSO_Reception('https://uat-www.hqchip.com').login()
            IcOrder(rss).add_cart().place_an_order()
            DataSource(target_rss).data_source_list(form).tactics_obtain()
            ReportedData(form).reported_data().risk_evaluate()
        elif form == "pcb":
            RunPcb().main('phpsessid')
            RunPcb().main('mid', 5147236)
            RunPcb().main("orders")
            DataSource(target_rss).data_source_list(form).tactics_obtain()
            ReportedData(form).reported_data().risk_evaluate()
            ReportedData(form).risk_evaluate()
