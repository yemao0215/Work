import hashlib
import time
from urllib.parse import quote

import requests

from huaqiu_order_api.common.loguru_logger import logger


class UserPromotion:
    def __init__(self, sign):
        self.sign = sign
        self.rss = requests.Session()

    def MD5_encryption(self, str):
        """MD5加密"""
        md5 = hashlib.md5()
        md5.update(str.encode("utf-8"))
        str_md5 = md5.hexdigest()
        return str_md5

    def big_data_token_ceate(self):
        """密钥token生成"""
        # 获取当前时间戳
        timestamp = str(time.mktime(time.localtime(time.time())))
        token_encryption = timestamp + self.sign
        token = self.MD5_encryption(token_encryption)
        return timestamp, token

    def query_url_arguments(self, data):
        """将body参数转换成可拼接至url的参数"""
        lt = []
        for k, v in data.items():
            lt.append(k + '=' + quote(str(v)))
        # 这个是在for循环外面的，就是将列表的元素之间用用&符号连接起来
        query_string = '&'.join(lt)
        return query_string

    def promotion_list(self, token, timestamp, promotion_body_other):
        """推广用户查询列表查询"""
        promotion_body = {"token": token, "time": timestamp}
        sys_params = promotion_body_other.copy()
        sys_params.update(promotion_body)
        logger.info(f"查询条件为：{sys_params}")
        promotion_url_arguments = '?' + self.query_url_arguments(sys_params)
        promotion_url = "http://192.168.20.42:9090/huaqiu-bigdata-interface/promotion{}".format(promotion_url_arguments)
        promotion_res = self.rss.post(url=promotion_url, data=promotion_body).json()
        logger.info(promotion_res)
        return self

    def plan_input_select(self, token, timestamp, plan_params):
        """推广计划搜索"""
        plan_input_select_body = {"params": plan_params}
        plan_input_select_body["token"] = token
        plan_input_select_body["time"] = timestamp
        plan_input_select_url_arguments = '?' + self.query_url_arguments(plan_input_select_body)
        plan_input_select_url = "http://192.168.20.42:9090/huaqiu-bigdata-interface/promotion/plan{}".format(plan_input_select_url_arguments)
        plan_input_select_res = self.rss.post(url=plan_input_select_url).json()
        logger.info(f"推广计划搜索关键词：{plan_params} 搜索结果为：{plan_input_select_res}")
        return self

    def unit_input_select(self, token, timestamp, unit_params):
        """推广计划搜索"""
        unit_input_select_body = {"params": unit_params}
        unit_input_select_body["token"] = token
        unit_input_select_body["time"] = timestamp
        unit_input_select_url_arguments = '?' + self.query_url_arguments(unit_input_select_body)
        unit_input_select_url = "http://192.168.20.42:9090/huaqiu-bigdata-interface/promotion/plan{}".format(unit_input_select_url_arguments)
        unit_input_select_res = self.rss.post(url=unit_input_select_url).json()
        logger.info(f"推广计划搜索关键词：{unit_params} 搜索结果为：{unit_input_select_res}")
        return self

    def main_user_promotion(self, promotion_body_other, params):
        timestamp = self.big_data_token_ceate()[0]
        token = self.big_data_token_ceate()[1]
        self.promotion_list(token, timestamp, promotion_body_other)
        self.plan_input_select(token, timestamp, params)
        self.unit_input_select(token, timestamp, params)
        return self

if __name__ == '__main__':
    sign = "27819cfe72583a34d13a40bb7415c91"
    promotion_body_other = {
        "regdate_stime": "2023-06-01 00:00:00", # 注册起始时间"
        "regdate_etime": "2023-06-28 23:59:59", # 注册结束时间
        "add_stime": "", # 下单开始时间
        "add_etime": "", # 下单结束时间
        "gap": "", # 下单注册时间差
        "order_sgmv": "", # 起始下单金额
        "order_egmv": "", # 结束下单金额
        "order-cnt": "", # 下单次数
        "cannal": "百度,百度品专", # 推广渠道
        "plan": "", # 推厂计划
        "unit": "", # 推广单元
        "keyword": "", # 推广关键词
        "sitename": "", # 注册站点
        "first_product": "", # 注册站点
        "url_mark": "", # 推广标识码
        "ad_site": "", # 广告站点
        "sem_type": "", # 归因来源
        "order_type": "",# 排序字段
        "order_value": "",# 排序方式
        "page ": 1,
        "pageRow": 20
    }
    UserPromotion(sign).main_user_promotion(promotion_body_other, "OP")
