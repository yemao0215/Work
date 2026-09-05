import hashlib
import time
import requests

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger


class UserPromotion:
    def __init__(self, rss):
        self.sign = ''
        self.rss = rss

        self.headers = {'Content-Type': 'application/json'}

    def promotion_list(self, promotion_body_other):
        """推广用户查询列表查询"""
        search_url = "https://uat-activity.hqchip.com/ecmc/bigData/marketing"
        search_body = {"params": promotion_body_other, "url": "/huaqiu-bigdata-interface/promotion"}
        logger.info(search_body)
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers).json()
        logger.info(search_res)
        self.data = search_res["data"]
        return self

    def plan_input_select(self, plan_params):
        """推广计划搜索"""
        plan_input_select_url = "https://uat-activity.hqchip.com/ecmc/bigData/promotion"
        plan_input_select_body = {"params": {"params": plan_params}, "url": "/huaqiu-bigdata-interface/promotion/plan"}
        plan_input_select_res = self.rss.post(url=plan_input_select_url, json=plan_input_select_body, headers=self.headers).json()
        logger.info(f"推广计划搜索关键词：{plan_params} 搜索结果为：{plan_input_select_res}")
        return self

    def unit_input_select(self, unit_params):
        """推广单元搜索"""
        unit_input_select_url = "https://uat-activity.hqchip.com/ecmc/bigData/promotion"
        unit_input_select_body = {"params": {"params": unit_params}, "url": "/huaqiu-bigdata-interface/promotion/unit"}
        unit_input_select_res = self.rss.post(url=unit_input_select_url, json=unit_input_select_body, headers=self.headers).json()
        logger.info(f"推广单元搜索关键词：{unit_params} 搜索结果为：{unit_input_select_res}")
        return self

    def keyword_input_select(self, keyword_params):
        """推广关键词搜索"""
        keyword_input_select_url = "https://uat-activity.hqchip.com/ecmc/bigData/promotion"
        keyword_input_select_body = {"params": {"params": keyword_params}, "url": "/huaqiu-bigdata-interface/promotion/keyword"}
        keyword_input_select_res = self.rss.post(url=keyword_input_select_url, json=keyword_input_select_body, headers=self.headers).json()
        logger.info(f"推广计划搜索关键词：{keyword_params} 搜索结果为：{keyword_input_select_res}")
        self.dataInfo = keyword_input_select_res["data"]
        return self

    def main_user_promotion(self, promotion_body_other, params):

        self.promotion_list(promotion_body_other)
        self.plan_input_select(params)
        self.unit_input_select(params)
        self.keyword_input_select(params)
        return self

    def main_keyword_search(self, promotion_body_other, params):
        self.keyword_input_select(params)
        self.keyword_cs = ''
        # for i in range(2):
        for i in range(len(self.dataInfo)):
            logger.info(f"此时i为{i}")
            self.keyword_cs = self.keyword_cs + self.dataInfo[i]["keyword_name"] + ','
            promotion_body_other["keyword"] = self.keyword_cs[0:-1]
            self.promotion_list(promotion_body_other)
            if self.data == []:
                logger.info(f"数据中心存在问题，请在前台核查数据！！！此时的搜索关键词为：{self.keyword_cs}")

if __name__ == '__main__':
    promotion_body_other = {
        "regdate_stime": "2023-01-01 00:00:00",
        "regdate_etime": "2023-06-28 23:59:59",
        "sem_type": "",
        "sitename": "",
        "unit": "",
        "plan": "",
        "cannal": "",
        "keyword": "",
        "page": 1,
        "pageRow": 50
    }
    target_rss = SOOLogin("uat-activity.hqchip.com", "ecmc").target_login()
    UserPromotion(target_rss).main_keyword_search(promotion_body_other, "")