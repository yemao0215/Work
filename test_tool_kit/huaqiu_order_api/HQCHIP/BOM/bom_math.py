import json
import re

import numpy as np
import pandas
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, bom_math_dir


class BomMmath:
    def __init__(self):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        :param goods_id:  购买的产品id
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.BOM_MATH_URL = data['BOM_MATH_URL']
        self.rss = requests.Session()
        self.headers = {"Content-Type": "application/json;charset=UTF-8"}
    def read_data(self):
        logger.info("开始读取表格内容")
        data = pandas.read_csv(bom_math_dir)
        self.serial_number = data["序号"]
        self.goods_category = data["产品分类"]
        self.goods_provider = data["品牌"]
        self.goods_name = data["型号*"]
        self.goods_encap = data["封装*"]
        self.goods_desc = data["规格参数描述*"]
        self.goods_bit = data["位号*"]
        self.goods_with_number = data["单机用量*"]
        self.goods_remark = data["备注"]
        return self
    def math_param_split(self):
        """参数拼接"""
        data = []
        for i in range(len(self.goods_name)):
            body = {"confirmId": i+1, "catName": self.goods_category[i], "brandName": self.goods_provider[i], "goodsName": self.goods_name[i],
                    "encap": self.goods_encap[i], "goodsOtherName": self.goods_desc[i], "localtion": self.goods_bit[i], "dosage":self.goods_with_number[i],
                    "number": self.goods_with_number[i]}
            data.append(body)

        print(data)

        print(json.dumps(data, indent=4, ensure_ascii=False, default=self.json_serial).replace("'", '"'))
        json_data = json.dumps(data, default=self.json_serial)
        return json_data

    def bom_math(self):
        url = "{}/spi/bomSearch/vagueMatchGoods?system=hqchip".format(self.BOM_MATH_URL)
        print(url)
        data = self.read_data().math_param_split()
        try:
            res = self.rss.post(url=url, json=data, headers=self.headers).json()
            print(res)
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")

    # 自定义序列化函数
    def json_serial(self, obj):
        if isinstance(obj, np.int64):  # 处理 int64 类型
            return int(obj)  # 转换为 Python 内置的 int 类型
        raise TypeError("Type not serializable")
if __name__ == '__main__':
    BomMmath().bom_math()

