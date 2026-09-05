import json
import re
import time
from datetime import datetime

import jsonpath
import numpy as np
import requests
import yaml
from faker import Faker

from huaqiu_order_api.HQCHIP_Activity.big_data.user_promotion import UserPromotion
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from huaqiu_order_api.project_sqlreview.sql_user_resources import SqlUserResources


class SqlReviewKitTool:
    def __init__(self, rss, data_base=None, source_name=None, source_id=None, sql=None, text=None):
        self.rss = rss
        self.json_head = {"Content-Type": "application/json"}
        self.form_head = {"Content-Type": "application/x-www-form-urlencoded"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Sqlreview_URL = data['Sqlreview_URL']
        sqlreview_token = getattr(Data, "sqlreview_token")
        self.json_head["Autorization"] = "Bearer " + sqlreview_token
        self.data_base = data_base
        self.source_name = source_name
        self.source_id = source_id
        self.sql = sql
        self.text = text
    def  data_base_search(self, source_name_id_dict):
        """数据源下的数据库查询"""
        if self.source_id == None and self.source_name != None:
            for k, v in source_name_id_dict.itmes():
                if k == self.source_name:
                    self.source_id = v
        base_search_url = "{}/api/v2/fetch/base?source_id={}&hide=ture".format(self.Sqlreview_URL, self.source_id)
        base_search_res = self.rss.get(url=base_search_url, headers=self.json_head).json()
        bases = base_search_res["payload"]
        return bases
    def sql_work_subimt(self, source_name_id_dict):
        """工单提交-sql语句修改"""
        bases = self.data_base_search(source_name_id_dict)
        for base in bases:
            if base == self.data_base:
                self.data_base = base
                break
        sql_detection_url = "{}/api/v2/fetch/test".format(self.Sqlreview_URL)
        sql_detection_body = {"data_base": self.data_base, "source_id": self.source_id, "sql": self.sql, "kind": 1}
        sql_detection_res = self.rss.put(url=sql_detection_url, json=sql_detection_body, headers=self.json_head).json()
        print(sql_detection_res)
        sql_work_submit_url = "{}/api/v2/common/post".format(self.Sqlreview_URL)
        for m, n in source_name_id_dict.itmes():
            if n == self.source_id:
                self.source_name = m
                break
        msg = None
        idc = self.source_name.split("-")[0]
        sql_work_submit_body = {"backup": 1, "data_base": self.data_base, "delay": "", "idc": idc, "relevant": ["提交人", "zhangbajun", "admin"],
                                "source": self.source_name, "source_id": self.source_id, "sql": self.sql, "table": "", "text": self.text, "type": 1}
        print(sql_work_submit_body)
        sql_work_submit_res = self.rss.post(url=sql_work_submit_url, json=sql_work_submit_body, headers=self.json_head).json()
        print(sql_work_submit_res)
        msg = sql_work_submit_res['text']
        return msg
    def sql_work_audit(self, word_id, source_name_id_dict):
        """SQL审核"""
        bases = self.data_base_search(source_name_id_dict)
        for base in bases:
            if base == self.data_base:
                self.data_base = base
                break
        # 获取审核详情
        sql_audit_detail_url = "{}/api/v2/fetch/sql?work_id={}".format(self.Sqlreview_URL, word_id)
        sql_audit_detail_res = self.rss.get(url=sql_audit_detail_url, headers=self.json_head).json()
        sqls = sql_audit_detail_res["payload"]["sqls"]
        # sql检测
        sql_detection_url = "{}/api/v2/fetch/test".format(self.Sqlreview_URL)
        sql_detection_body = {"data_base": self.data_base, "source_id": self.source_id, "sql": self.sql, "kind": 1, "word_id": word_id}
        sql_detection_res = self.rss.put(url=sql_detection_url, json=sql_detection_body, headers=self.json_head).json()
        # 使用 any() 和列表推导式检查是否存在"status"的值为"审核失败"的字典，并对结果取反
        result = not any(d["status"] == "审核失败" for d in sql_detection_res["payload"])
        msg = None
        if result == True:
            sql_work_audit_url = "{}/api/v2/audit/order/state".format(self.Sqlreview_URL)
            sql_work_audit_body = {"flag": 1, "source_id": self.source_id, "tp": "agree", "work_id": word_id}
            sql_work_audit_res = self.rss.post(url=sql_work_audit_url, json=sql_work_audit_body, headers=self.json_head).json()
            print(sql_work_audit_res)
            msg = sql_work_audit_res["text"]
        return msg

    def mian_sql_work_submit(self):
        source_name_id_dict = SqlUserResoures(self.rss).sql_user_resources_search()
        msg = self.sql_work_subimt(source_name_id_dict)
        return msg

    def mian_sql_work_audit(self, word_id):
        source_name_id_dict = SqlUserResoures(self.rss).sql_user_resources_search()
        msg = self.sql_work_audit(word_id, source_name_id_dict)
        return msg
