import json
import time
from datetime import datetime, timedelta

import jsonpath
import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import poseter_img_dir, discount_dir, yaml_file, account_yaml


class DiscountKit:
    def __init__(self, target_rss):
        self.activity_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data["Activity_Center_URL"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.goods_id = "2500319477"


    def discuont_detail(self):
        """折扣活动详情"""
        detail_url = "{}/ecmc/discount/detail".format(self.Activity_Center_URL)
        detail_body = {"activityId": "1655"}
        detail_res = self.activity_rss.post(url=detail_url, json=detail_body, headers=self.json_head).json()
        # logger.info(f"执行结果为：{detail_res}")
        self.activityName = jsonpath.jsonpath(detail_res, '$..activityName')[0]
        self.activityStartTime = jsonpath.jsonpath(detail_res, '$..activityStartTime')[0]
        self.activityEndTime = jsonpath.jsonpath(detail_res, '$..activityEndTime')[0]
        self.openTask = jsonpath.jsonpath(detail_res, '$..openTask')[0]
        self.riskManageId = jsonpath.jsonpath(detail_res, '$..riskManageId')[0]
        return self
    def discount_temp_cache(self):
        """折扣临时缓存"""
        discount_temp_cache_url = "{}/ecmc/discount/getTempGoods".format(self.Activity_Center_URL)
        discount_temp_cache_body = {"actionName": "edit", "activityId": "1655", "goodsId": "",
                                    "isInit": True, "pageNum": 1, "pageSize": 20
                                    }
        discount_temp_cache_res = self.activity_rss.post(url=discount_temp_cache_url, json=discount_temp_cache_body, headers=self.json_head).json()
        # logger.info(discount_temp_cache_res)
        resulInfo = discount_temp_cache_res["result"]
        cacheGoodInfo = None
        for i in range(len(resulInfo)):
            goods_id = resulInfo[i]["goodsId"]
            # logger.info(goods_id)
            if goods_id == self.goods_id:
                cacheGoodInfo = resulInfo[i]
        edit_cache_goods_url = "{}/ecmc/discount/editTempGoods".format(self.Activity_Center_URL)
        # logger.info(cacheGoodInfo)
        cacheGoodInfo["actionName"] = "edit"
        cacheGoodInfo["discountGoodsStatus"] = 2
        edit_cache_goods_body = cacheGoodInfo
        edit_cache_goods_res = self.activity_rss.post(url=edit_cache_goods_url, json=edit_cache_goods_body, headers=self.json_head).json()
        # logger.info(f"执行结果：{edit_cache_goods_res}")
        if edit_cache_goods_res["result"] == "编辑成功":
            discount_temp_cache_res = self.activity_rss.post(url=discount_temp_cache_url, json=discount_temp_cache_body,
                                                             headers=self.json_head).json()
            resulInfo = discount_temp_cache_res["result"]
            # 负利润判断
            negativeProfitCheck_url = "{}/ecmc/discount/negativeProfitCheck".format(self.Activity_Center_URL)
            negativeProfitCheck_body = {"actionName": "edit", "activityName": self.activityName, "activityId": "1655",
                                        "activityStartTime": self.activityStartTime, "activityEndTime": self.activityEndTime,
                                        "data": [resulInfo], "openTask": self.openTask, "riskManageId": self.riskManageId
                                        }
            negativeProfitCheck_res = self.activity_rss.post(url=negativeProfitCheck_url, json=negativeProfitCheck_body,
                                                             headers=self.json_head).json()
            # logger.info(negativeProfitCheck_res)
            serviceNegativeId = negativeProfitCheck_res["retMsg"]
            negativeProfitCheckPage_url = "{}/ecmc/discount/negativeProfitCheckPage".format(self.Activity_Center_URL)
            negativeProfitCheckPage_body = {"uuid": serviceNegativeId, "pageNum": 1, "pageSize": 20}
            negativeProfitCheckPage_res = self.activity_rss.post(url=negativeProfitCheckPage_url, json=negativeProfitCheckPage_body,
                                                             headers=self.json_head).json()
            edit_url = "{}/ecmc/discount/edit".format(self.Activity_Center_URL)
            edit_body = negativeProfitCheck_body
            edit_res = self.activity_rss.post(url=edit_url, json=edit_body,
                                                             headers=self.json_head).json()
            if edit_res["result"] == "编辑折扣活动成功":
                logger.info(f"goods_id：{self.goods_id}在活动id：1655 编辑在开启/关闭按钮为：关闭保存成功")
            edit_cache_goods_url = "{}/ecmc/discount/editTempGoods".format(self.Activity_Center_URL)
            # logger.info(cacheGoodInfo)
            cacheGoodInfo["actionName"] = "edit"
            cacheGoodInfo["discountGoodsStatus"] = 1
            edit_cache_goods_body = cacheGoodInfo
            edit_cache_goods_res = self.activity_rss.post(url=edit_cache_goods_url, json=edit_cache_goods_body,
                                                          headers=self.json_head).json()
            # logger.info(f"执行结果：{edit_cache_goods_res}")
            if edit_cache_goods_res["result"] == "编辑成功":
                discount_temp_cache_res = self.activity_rss.post(url=discount_temp_cache_url,
                                                                 json=discount_temp_cache_body,
                                                                 headers=self.json_head).json()
                resulInfo = discount_temp_cache_res["result"]
                # 负利润判断
                negativeProfitCheck_url = "{}/ecmc/discount/negativeProfitCheck".format(self.Activity_Center_URL)
                negativeProfitCheck_body = {"actionName": "edit", "activityName": self.activityName,
                                            "activityId": "1655",
                                            "activityStartTime": self.activityStartTime,
                                            "activityEndTime": self.activityEndTime,
                                            "data": [resulInfo], "openTask": self.openTask,
                                            "riskManageId": self.riskManageId
                                            }
                negativeProfitCheck_res = self.activity_rss.post(url=negativeProfitCheck_url,
                                                                 json=negativeProfitCheck_body,
                                                                 headers=self.json_head).json()
                # logger.info(negativeProfitCheck_res)
                serviceNegativeId = negativeProfitCheck_res["retMsg"]
                negativeProfitCheckPage_url = "{}/ecmc/discount/negativeProfitCheckPage".format(
                    self.Activity_Center_URL)
                negativeProfitCheckPage_body = {"uuid": serviceNegativeId, "pageNum": 1, "pageSize": 20}
                negativeProfitCheckPage_res = self.activity_rss.post(url=negativeProfitCheckPage_url,
                                                                     json=negativeProfitCheckPage_body,
                                                                     headers=self.json_head).json()
                edit_url = "{}/ecmc/discount/edit".format(self.Activity_Center_URL)
                edit_body = negativeProfitCheck_body
                edit_res = self.activity_rss.post(url=edit_url, json=edit_body,
                                                  headers=self.json_head).json()
                if edit_res["result"] == "编辑折扣活动成功":
                    logger.info(f"goods_id：{self.goods_id}在活动id：1655 编辑在开启/关闭按钮为：开启保存成功")
            return self



    def loop_operate_interface(self):
        pass


if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    rss = SOOLogin("uat-activity.hqchip.com", "ecmc").target_login()
    for i in range(100):
        DiscountKit(rss).discuont_detail().discount_temp_cache()