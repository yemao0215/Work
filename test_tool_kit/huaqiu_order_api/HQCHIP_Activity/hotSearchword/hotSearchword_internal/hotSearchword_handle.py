import csv
import time
from datetime import datetime, timedelta
import hashlib
import os

import jsonpath
import pandas
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, clear_redis_cache_dir, \
    redemption_code_password_dir, hot_word_icon_dir


class HotSearchWordHandle:

    def __init__(self, rss, keyword):
        self.rss = rss
        self.json_head = {"Content-Type": "application/json"}
        self.couponName = "上海PCB嘉宾免单券"
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data["Activity_Center_URL"]
        self.HQCHIP_URL = data["HQCHIP_URL"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.targetType = 2
        self.keyword = keyword

    def hot_Searchword_config(self):
        """热搜词配置列表"""
        hot_word_config_url = "{}/ecmc/hotSearchWords/list".format(self.Activity_Center_URL)
        hot_word_config_body = {"pageNum": 1, "pageSize": 50, "timeStatus": "0"}
        hot_word_config_res = self.rss.post(url=hot_word_config_url,
                                            json=hot_word_config_body, headers=self.json_head).json()
        configId = jsonpath.jsonpath(hot_word_config_res, '$..id')
        keyword = jsonpath.jsonpath(hot_word_config_res, '$..keyword')
        for i in range(len(keyword)):
            if keyword[i] == self.keyword:
                self.config_id = configId[i]
        logger.info(f"获取到config_id：{self.config_id}")

        return self

    def hot_word_icon_file(self):
        """上传icon文件"""
        hot_word_icon_file_url = "{}/ecmc/upload/uploadFile".format(self.Activity_Center_URL)
        file_name = hot_word_icon_dir.split('\\')[-1]
        logger.info(file_name)
        file = [('file', (file_name, open(hot_word_icon_dir, 'rb'),
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
        hot_word_icon_file_res = self.rss.post(url=hot_word_icon_file_url, files=file).json()
        icon_url = hot_word_icon_file_res["result"]["url"]
        logger.info(icon_url)
        return icon_url

    def hotSearchword_config_add(self):
        """热搜词配置新增/复制"""
        icon_url = self.hot_word_icon_file()
        logger.info(f"获取到上传icon文件的服务器url：{icon_url}")
        now_time_one_minutes = str((datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一分钟后的时间：{now_time_one_minutes}")
        time.sleep(1)
        # now_time_one_day = str((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
        # logger.info(f"获取当前时间一天后的时间：{now_time_one_day}")
        now_time_one_hours = str((datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一小时后的时间：{now_time_one_hours}")

        hotSearchword_config_add_url = "{}/ecmc/hotSearchWords/save".format(self.Activity_Center_URL)
        hotSearchword_config_add_body = {"position": 0, "icon": icon_url, "color": "#E72323", "wide": "0", "sort": "1",
                                         "keyword": self.keyword,
                                         "targetType": "", "url": "", "startTime": now_time_one_minutes,
                                         "endTime": now_time_one_hours}
        hotSearchword_config_add_body["targetType"] = self.targetType
        keyword = hotSearchword_config_add_body["keyword"]
        if self.targetType == 0:
            hotSearchword_config_add_body["url"] = "{}/replacement/{}.html".format(self.HQCHIP_URL, keyword)
        elif self.targetType == 1:
            # url自定义为搜索页
            hotSearchword_config_add_body["url"] = "{}/search/{}.html".format(self.HQCHIP_URL, keyword)
        elif self.targetType == 2:
            # url自定义为搜索页
            hotSearchword_config_add_body["url"] = "{}/search/{}.html".format(self.HQCHIP_URL, keyword)
        hot_word_config_res = self.rss.post(url=hotSearchword_config_add_url,
                                            json=hotSearchword_config_add_body, headers=self.json_head).json()
        if hot_word_config_res["result"] == "成功":
            logger.info(f"新增关键词：{keyword}的热搜词配置成功")
        return self

    def hot_Searchword_config_detail(self):
        """热词配置详情"""
        self.hot_Searchword_config()
        hot_Searchword_config_detail_url = "{}/ecmc/hotSearchWords/detail".format(self.Activity_Center_URL)
        hot_Searchword_config_detail_body = {"id": self.config_id}
        hot_Searchword_config_detail_res = self.rss.post(url=hot_Searchword_config_detail_url,
                                                         json=hot_Searchword_config_detail_body,
                                                         headers=self.json_head).json()
        self.resultInfo = hot_Searchword_config_detail_res["result"]
        logger.info(f"获取到详情信息：{self.resultInfo}")
        return self

    def hotSearchword_config_edit(self):
        """热词配置编辑"""
        self.hot_Searchword_config_detail()
        hot_Searchword_config_edit_url = "{}/ecmc/hotSearchWords/edit".format(self.Activity_Center_URL)
        # 修改权重
        self.resultInfo["sort"] = 101
        hot_Searchword_config_edit_body = self.resultInfo
        hot_Searchword_config_edit_res = self.rss.post(url=hot_Searchword_config_edit_url,
                                                       json=hot_Searchword_config_edit_body,
                                                       headers=self.json_head).json()
        if hot_Searchword_config_edit_res["result"] == "成功":
            logger.info(f"修改关键词：{self.keyword}的热搜词配置成功")
        return self

    def hotSearchword_config_end(self):
        """结束热词配置"""
        self.hot_Searchword_config()
        hot_Searchword_config_end_url = "{}/ecmc/hotSearchWords/end".format(self.Activity_Center_URL)
        hot_Searchword_config_end_body = {"id": self.config_id}
        hot_Searchword_config_end_res = self.rss.post(url=hot_Searchword_config_end_url,
                                                       json=hot_Searchword_config_end_body,
                                                       headers=self.json_head)
        if hot_Searchword_config_end_res["result"] == "成功":
            logger.info(f"结束关键词：{self.keyword}的热搜词配置成功")
        return self


if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin

    rss = SOOLogin("uat-activity.hqchip.com", "ecmc").target_login()
    keyword = ["WST3013","CGA2B2X7R1H222K050BA", "WST03P06","6CS25000F20UCG","ABM81-12.000MHz-10-B1U-T", "X3S012000BK1H",
                "7V27000008", "7A08000001", "Q13MC1462000200", "CBM2596DT-3.3", "CBM2596DT-ADJ", "TAJV156K050RNJ"
               ]
    for i in range(len(keyword)):
        HotSearchWordHandle(rss, keyword[i]).hotSearchword_config_add()