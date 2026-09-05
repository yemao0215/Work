import csv
from datetime import datetime, timedelta
import hashlib
import os

import jsonpath
import pandas
import requests
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, clear_redis_cache_dir, redemption_code_password_dir


class RedemptionHandle:

    def __init__(self, rss):
        self.rss = rss
        self.json_head = {"Content-Type": "application/json"}
        self.couponName = "上海PCB嘉宾免单券"
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data["Activity_Center_URL"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)

    def redemption_activity(self):
        """兑换活动列表"""
        redemption_code_activity_url = "{}/ecmc/activityRedemptionCode/list".format(self.Activity_Center_URL)
        redemption_code_activity_body = {"pageNum": 1, "pageSize": 50, "timeStatus": "0"}
        redemption_code_activity_res = self.rss.post(url=redemption_code_activity_url,
                                                     json=redemption_code_activity_body, headers=self.json_head).json()
        activityId = jsonpath.jsonpath(redemption_code_activity_res, '$..id')
        activityName = jsonpath.jsonpath(redemption_code_activity_res, '$..activityName')
        for i in range(len(activityName)):
            if activityName[i] == "自动化测试":
                self.activity_id = activityId[i]
        logger.info(f"获取到activityId：{self.activity_id}")
        return self
    def redemption_activity_create(self):
        """兑换活动创建"""
        now_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间：{now_time}")
        now_time_one_day = str((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一天后的时间：{now_time_one_day}")
        now_time_one_hours = str((datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一小时后的时间：{now_time_one_hours}")
        now_time_one_minutes = str((datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一分钟后的时间：{now_time_one_minutes}")
        redemption_activity_create_url = "{}/ecmc/activityRedemptionCode/save".format(self.Activity_Center_URL)
        redemption_activity_create_body = {"activityStartTime": now_time_one_hours, "activityEndTime": now_time_one_day, "activityName": "自动化测试"}
        redemption_activity_create_res = self.rss.post(url=redemption_activity_create_url,
                                                     json=redemption_activity_create_body, headers=self.json_head).json()
        self.activity_id = redemption_activity_create_res["result"]["activityId"]
        logger.info(f"获取到activityId：{self.activity_id}")
        return self


    def redemption_activity_materiel(self):
        """兑换活动兑换物料关联"""
        # self.activity_id = 1683
        # 获取优惠券  获取的是优惠券活动的发放方式为：接口发放的活动所绑定的生效中的优惠券
        redemption_materiel_url = "{}/ecmc/common/getOngoingAndWillCodeCouponList".format(self.Activity_Center_URL)
        redemption_materiel_body = {"couponType": [], "pageNum": 1, "pageSize": 50, "type": 1}  # couponType 目前尚未启用，type 当前默认为1，为优惠券，后续可能扩展到其他类型
        redemption_materiel_res = self.rss.post(url=redemption_materiel_url,
                                                     json=redemption_materiel_body, headers=self.json_head).json()
        couponName = jsonpath.jsonpath(redemption_materiel_res, '$..name')
        couponId = jsonpath.jsonpath(redemption_materiel_res, '$..couponId')
        # logger.info(f"执行结果：{couponId}")
        for i in range(len(couponName)):
            if couponName[i] == self.couponName:
                self.couponId = couponId[i]
        logger.info(f"获取到couponId：{self.couponId}")
        redemption_activity_materiel_url = "{}/ecmc/activityRedemptionCode/exchangeMaterialSettings".format(self.Activity_Center_URL)
        redemption_activity_materiel_body = {"activityId": self.activity_id, "exchangeMaterialType": 1, "exchangeMaterialId": self.couponId}
        redemption_activity_materiel_res = self.rss.post(url=redemption_activity_materiel_url,
                                                     json=redemption_activity_materiel_body, headers=self.json_head).json()
        if redemption_activity_materiel_res["result"] == "兑换物料设置成功":
            logger.info(f"关联物料-优惠券：{self.couponName} 成功")
        return self



    def redemption_code_create(self):
        """兑换活动兑换码生成"""
        # self.activity_id = 1683
        redemption_code_create_url = "{}/ecmc/redemptionCode/save".format(self.Activity_Center_URL)
        redemption_code_create_body = {"activityId": self.activity_id, "individualRedemptionTimes": 1, "number": 1000, "totalRedemptionTimes": 1}
        redemption_code_create_res = self.rss.post(url=redemption_code_create_url,
                                                     json=redemption_code_create_body, headers=self.json_head).json()
        self.serviceCustomizeId = redemption_code_create_res["result"]
        logger.info(f"获取到服务器自定义id：{self.serviceCustomizeId}")
        return self


    def redemption_code_password_download(self):
        """兑换活动兑换码卡密下载"""
        # self.serviceCustomizeId = "29aadf086fa7449a82b118e066d083f0"
        redemption_code_password_download_url = "{}/ecmc/redemptionCode/download".format(self.Activity_Center_URL)
        redemption_code_password_download_body = {"uuid": self.serviceCustomizeId}
        redemption_code_password_download_res = self.rss.post(url=redemption_code_password_download_url,
                                                     json=redemption_code_password_download_body, headers=self.json_head)
        logger.info(f"下载信息为：{redemption_code_password_download_res.text}")
        # 将响应报文 写入csv 文件
        fp = open(redemption_code_password_dir, 'w', encoding='GBK', newline='')
        fp.write(redemption_code_password_download_res.content.decode('GBK'))
        fp.close()
        # 判断csv是否存在数据
        result = os.path.getsize(redemption_code_password_dir)
        if result != 0:
            logger.info(f"数据写入csv成功")
        return self


if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    rss = SOOLogin( "uat-activity.hqchip.com", "ecmc").target_login()
    RedemptionHandle(rss).redemption_activity_create().redemption_activity_materiel().redemption_code_create().redemption_code_password_download()