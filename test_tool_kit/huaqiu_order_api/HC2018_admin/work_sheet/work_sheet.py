import ast
import json

import jsonpath
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class WorkSheet:
    """ 审核流程配置 """
    def __init__(self, rss):
        self.rss = rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.auth_token = getattr(Data, 'dos_auth_token')
        self.headers_json["Authorization"] = self.auth_token
        self.work_sheet_type_json = {"备货审批": 1, "补货审批": 2, "定价审批": 3}

    def work_sheet_search(self, worksheet_sn=None, order_tag=None, order_bool_flag=None):
        """流程配置查询"""
        search_url = "{}/v1/authorize/Worksheet/findList".format(self.HC2018_ADMIN_URL)
        search_body = {
            "worksheet_sn": worksheet_sn,
            "status": "1",
            "page": 1,
            "per_page": 20
        }
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
        if search_res["data"] == []:
            # print(1111)
            for key in self.work_sheet_type_json:
                if key == worksheet_sn:
                    search_body["type"] = self.work_sheet_type_json[key]
                    search_body["worksheet_sn"] = ""
                    break
            search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
        self.work_sheet_id = jsonpath.jsonpath(search_res, '$..id')[0]
        user_name = []
        work_sheet_derail_url = "{}/v1/authorize/Worksheet/findDetail".format(self.HC2018_ADMIN_URL)
        work_sheet_derail_body = {"id": self.work_sheet_id}
        work_sheet_derail_res = self.rss.post(url=work_sheet_derail_url, json=work_sheet_derail_body, headers=self.headers_json).json()
        audit_real_name = jsonpath.jsonpath(work_sheet_derail_res, '$..audit_real_name')
        # extend = jsonpath.jsonpath(work_sheet_derail_res, '$..extend')
        start_amount = jsonpath.jsonpath(work_sheet_derail_res, '$..start_amount')
        extend = jsonpath.jsonpath(work_sheet_derail_res, '$..extend')
        # print(extend)
        audit_url_all_url = "{}/v1/authorize/Worksheet/findAuditUser".format(self.HC2018_ADMIN_URL)
        audit_url_all_res = self.rss.post(url=audit_url_all_url, headers=self.headers_json).json()
        audit_url_all_user_id = jsonpath.jsonpath(audit_url_all_res, '$..user_id')
        audit_url_all_real_name = jsonpath.jsonpath(audit_url_all_res, '$..real_name')
        for i in range(len(audit_real_name)):
            if extend[i] != "":
                extend_json = json.loads(extend[i])
                # for k, v in extend_json.items():
                if order_tag == "PCBA":
                        if "pcba_audit_uid" in extend_json:
                            audit_uid = extend_json["pcba_audit_uid"]
                            # print(audit_uid)
                            audit_real_name[i] = \
                            [y for x, y in zip(audit_url_all_user_id, audit_url_all_real_name) if x == str(audit_uid)][0]
                #         print(k, v)
                        if "has_order" in extend_json:
                            start_amount[i] = extend_json["has_order"]
                elif order_tag == "IC":
                    print(extend_json)
                    if "pcba_audit_uid" in extend_json and order_bool_flag == True:
                        if "has_order" in extend_json:
                            start_amount[i] = extend_json["has_order"]
                    else:
                        if "no_order" in extend_json:
                            start_amount[i] = extend_json["no_order"]
            admin_user_url = "{}/v1/authorize/AdminUser/findList".format(self.HC2018_ADMIN_URL)
            admin_user_body = {"field": "real_name", "field_val": audit_real_name[i], "page": 1, "per_page": 100}
            admin_user_res = self.rss.post(url=admin_user_url, json=admin_user_body, headers=self.headers_json).json()
            user_name = user_name + jsonpath.jsonpath(admin_user_res, '$..user_name')
            setattr(Data, 'audit_real_name', audit_real_name)
        setattr(Data, 'user_name', user_name)
        setattr(Data, 'start_amount', start_amount)
        setattr(Data, 'extend', extend)
        print(user_name)
        print(start_amount)
        return self


if __name__ == '__main__':
    from huaqiu_order_api.HC2018_admin.login.login import Login
    target_rss = Login().login()
    WorkSheet(target_rss).work_sheet_search("补货审批", "IC", order_bool_flag=True)