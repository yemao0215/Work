import json
import time
from datetime import datetime, timedelta

from HQCHIP_SOO.login import SOOLogin
from common.loguru_logger import logger
from common.my_path import freight_goods_dir, freight_people_dir


class NameProject:
    # 风控中台名单管理-名单项目管理
    def __init__(self, target_rss, rcs_name,projectName):
        self.rcs_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.rcs_name = rcs_name
        self.projectName = projectName


    def name_project_list(self):
        """名单项目管理列表"""
        search_url = "https://uat-rcs.huaqiu.com/api/admin/list_project/page"
        search_body = {"timeStatus": "0", "pageNum": 1, "pageSize": 20}
        search_res = self.rcs_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        logger.info(search_res)
        rcsInfo = search_res["body"]["list"]
        logger.info(len(rcsInfo))
        self.rcs_id = []
        project_name = []
        for i in range(len(rcsInfo)):
            self.rcs_id.append(rcsInfo[i]["projectId"])
            project_name.append(rcsInfo[i]["projectName"])
        for q in range(len(rcsInfo)):
            if self.projectName == project_name[q]:
                self.rcs_id = self.rcs_id[q]
                # self.activity_id.append(self.activity_id[q])
            continue
        logger.info(f"获取名单项目管理名称为{self.projectName}的项目id的list列表为{self.rcs_id}")

        return self

    def name_project_add(self, projectCode):
        """名单项目新增"""
        add_url = "https://uat-rcs.huaqiu.com/api/admin/list_project/add"
        add_body = {"projectName": self.projectName, "projectCode": projectCode}
        add_res = self.rcs_rss.post(url=add_url, json=add_body, headers=self.json_head).json()
        if add_res["suc"] == True:
            logger.info(f"新增名单项目：{self.projectName}")
        return self

if __name__ == '__main__':
    target_rss = SOOLogin("admin", "12345678", "uat-rcs.huaqiu.com", "api").target_login()
    NameProject(target_rss, "111", "积分兑换优惠券项目").name_project_add("exchahge_coupon")
