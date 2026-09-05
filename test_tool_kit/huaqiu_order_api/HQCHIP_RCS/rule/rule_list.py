import json
import time
from datetime import datetime, timedelta

import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import freight_goods_dir, freight_people_dir, yaml_file


class RuleList:
    # 风控中台规则管理-规则列表
    def __init__(self, target_rss, projectName, rule_name):
        self.rcs_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.projectName = projectName
        self.rule_name = rule_name
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.RCS_URL = data["RCS_URL"]

    def rule_project(self):
        """"""
        search_url = "{}/api/admin/list_project/list".format(self.RCS_URL)
        search_body = {"projectName": ""}
        search_res = self.rcs_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        # logger.info(search_res)
        projectInfo = search_res["body"]
        # logger.info(len(rcsInfo))
        self.rcs_id = []
        project_name = []
        for i in range(len(projectInfo)):
            self.rcs_id.append(projectInfo[i]["projectId"])
            project_name.append(projectInfo[i]["projectName"])
        for q in range(len(projectInfo)):
            if self.projectName == project_name[q]:
                self.rcs_id = self.rcs_id[q]
                # self.activity_id.append(self.activity_id[q])
            continue
        logger.info(f"获取名单项目管理名称为{self.projectName}的项目id的list列表为{self.rcs_id}")

        return self

    def rule_source(self, sourceName):

        search_url = "{}/api/admin/source/list".format(self.RCS_URL)
        search_res = self.rcs_rss.post(url=search_url, headers=self.json_head).json()
        sourceInfo = search_res["body"]
        self.sourceId = []
        source_name = []
        for i in range(len(sourceInfo)):
            self.sourceId.append(sourceInfo[i]["projectId"])
            source_name.append(sourceInfo[i]["projectName"])
        for q in range(len(sourceInfo)):
            if sourceName == source_name[q]:
                self.sourceId = self.sourceId[q]
        logger.info(f"获取名单项目管理名称为{self.projectName}的项目id的list列表为{self.sourceId}")
        return self

    def rule_source_field(self):

        search_url = ""


    def rule_list(self):
        """规则列表"""
        search_url = "{}/api/admin/rule/page".format(self.RCS_URL)
        search_body = {"projectName": self.rule_name, "listType": 0}
        search_res = self.rcs_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        ruleIdInfo = search_res["body"]["list"]
        rule_id = []
        rule_name = []
        for i in range(len(ruleIdInfo)):
            rule_id.append(ruleIdInfo[i]["id"])
            rule_name.append(ruleIdInfo[i]["ruleName"])
        for q in range(len(ruleIdInfo)):
                if self.rule_name == rule_name[q]:
                    rule_id = rule_id[q]

        logger.info(f"获取规则名称为{self.rule_name}的规则id的list列表为{rule_id}")
        return self

    def rule_add(self, ruleName,ruleKey, ruleType, fieldType, ruleSymbol, nameListType):
        """规则创建
        :param fieldType 名单参数 1手机号 2邮箱 3uid 4税号 5设备号 6收货地址 7微信 8QQ 9IP地址
        :param ruleSymbol 判断 in在  notin不在 等量关系符号如：>、<、<=
        :param nameListType 名单类型 1黑名单 2白名单

        """
        add_url = "{}/api/admin/rule/add".format(self.RCS_URL)
        add_body = {}
        if ruleType == 1:
            add_body = {}
        if ruleType == 2:
            # 名单型规则
            add_body = {"dataSourceId": self.sourceId[0], "dataSourceInfo": {}, "isEffective": 1, "nameListProject":self.projectName, "threshold": "", "id":"",
                        "ruleField": fieldType, "ruleSymbol": ruleSymbol, "nameListType": nameListType, "ruleTimeInterval": "", "ruleTimeIntervalUnit": "",
                        "ruleDesc": self.projectName, "ruleName": ruleName, "ruleKey": ruleKey
                       }
        add_res = self.rcs_rss.post(url=add_url, json=add_body, headers=self.json_head).json()




if __name__ == '__main__':
    target_rss = SOOLogin("uat-rcs.huaqiu.com", "api").target_login()
    RuleList(target_rss, "111", "单笔订单手机号").rule_project().rule_source("积分订单").rule_add("1111","11111",2,9,"in",1)
