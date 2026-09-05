import datetime
import hashlib

import pandas
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, account_yaml, clear_redis_cache_dir


class RedemptionKit:

    def __init__(self):
        self.rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}

        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data["Activity_Center_URL"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
    def read_data(self):
        logger.info("开始读取表格内容")
        data = pandas.read_csv(clear_redis_cache_dir)
        self.unionid = data["unionid"]
        return self


    def clear_redis_cache(self):
        """清空华秋uid在redis的缓存数据"""
        self.unionid = ["5146221"]
        for i in range(len(self.unionid)):
            unionid = self.unionid[i]
            clear_redis_cache_url = "{}/ecmc/activityapi/test/delRedemptionCodeCache".format(self.Activity_Center_URL)
            clear_redis_cache_body = {"appid": "ic", "unionid": unionid}
            clear_redis_cache_res = self.rss.post(url=clear_redis_cache_url, json=clear_redis_cache_body, headers=self.json_head)
            if clear_redis_cache_res.status_code == 200:
                logger.info(f"执行unionid：{unionid}结果：成功")
        return self

    def redemption_code_exchange(self):
        """兑换码兑换接口---营销中台接口"""
        unionid = "5146221"
        code = "9772441499364968"
        self.json_head["unionid"] = unionid
        redemption_code_exchange_url = "{}/ecmc/activityapi/redemptionCode/exchange".format(self.Activity_Center_URL)
        redemption_code_exchange_body = {"appid": "crm", "redemptionCodeCardSecret": code}
        redemption_code_exchange_res= self.rss.post(url=redemption_code_exchange_url, json=redemption_code_exchange_body, headers=self.json_head).json()
        # logger.info(redemption_code_exchange_res.text)
        logger.info(f"执行unionid：{unionid}结果：{redemption_code_exchange_res}")
        if redemption_code_exchange_res["retMsg"] == "卡密错误，请24小时后重试":
            lockEndTimetimestamp = redemption_code_exchange_res["result"]["lockEndTime"]
            serverNowtimestamp = redemption_code_exchange_res["result"]["times"]
            # 时间差
            time_difference = int(lockEndTimetimestamp) - int(serverNowtimestamp)
            # 以时分秒展示时间差
            hours, remainder = divmod(time_difference, 3600)
            minutes, seconds = divmod(remainder, 60)
            logger.info(f"时间差为：{hours}:{minutes}:{seconds}")
        return self
    def redemption_code_sha256_encipher(self):
        """兑换码卡密SHA256加密"""
        code = "9772441499364968"
        code_obj = hashlib.sha256()
        code_obj.update(code.encode())
        encipher_result = code_obj.hexdigest()
        logger.info(f"兑换码：{code}加密结果为 {encipher_result}")
        return self



if __name__ == '__main__':
    RedemptionKit().redemption_code_exchange()