import json
import os
import re
import subprocess
from functools import partial

import yaml

from huaqiu_order_api.common.loguru_logger import logger

subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')

import execjs
from huaqiu_order_api.common.my_path import encryption_order_dir, encryption_order_new_dir, encryptConfYaml_dir


class orderSensitiveMsgEncrypt:
    # 订单敏感信息加解密
    def __init__(self, data=None, dataStr=None, dencrypt_data=None, encrypt_data=None):
        """
        :param data 加密的信息
        :param dataStr 需要解密信息
        :param auto_data 自动解密的json数据
        """
        self.data = data
        self.dataStr = dataStr
        self.dencrypt_data = dencrypt_data
        self.encrypt_data = encrypt_data

    def remove_non_bmp(self, text):
        return re.sub(r'[^\u0000-\uFFFF]', '', text)
    def encrypt(self):
        """前置js加密"""
        # # 读取JavaScript文件内容
        with open(encryption_order_dir, "r", encoding="utf-8") as f:
            js_content = f.read()
        # 编译JavaScript代码
        js_runtime = execjs.compile(js_content)
        # 调用JavaScript函数
        dataStr = js_runtime.call("encryptData", self.data)
        logger.info("加密结果: {}", dataStr)
        return dataStr

    def dencrypt(self):
        """前置js解密"""
        # # 读取JavaScript文件内容
        with open(encryption_order_dir, "r", encoding="utf-8") as f:
            js_content = f.read()
        # 编译JavaScript代码
        js_runtime = execjs.compile(js_content)
        # 调用JavaScript函数
        dataJSON = js_runtime.call("decodeData", self.dataStr)
        logger.info("解密结果: {}", dataJSON)
        return dataJSON
    def auto_dencrypt(self):
        """前置js解密"""
        # # 读取JavaScript文件内容
        with open(encryption_order_dir, "r", encoding="utf-8") as f:
            js_content = f.read()
        # 编译JavaScript代码
        js_runtime = execjs.compile(js_content)
        # 调用JavaScript函数
        dataJSON = js_runtime.call("autoDecodeData", self.dencrypt_data)
        logger.info("自动解密结果: {}", json.dumps(dataJSON, ensure_ascii=False))
        return dataJSON
    def auto_encrypt(self):
        """前置根据YAML文件敏感字段自动加密"""
        # 1. Python 读取 YAML
        with open(encryptConfYaml_dir, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)

        white_list = yaml_config["whiteList"]
        sensitive_keys = yaml_config["sensitiveKeys"]
        # # 读取JavaScript文件内容
        with open(encryption_order_new_dir, "r", encoding="utf-8") as f:
            js_content = f.read()
        # 编译JavaScript代码
        js_runtime = execjs.compile(js_content)
        # 调用JavaScript函数
        dataJSON = js_runtime.call(
            "autoEncryptData",
            self.encrypt_data,   # 你的数据
            white_list,          # 白名单
            sensitive_keys       # 敏感字段
        )
        logger.info("自动加密结果: {}", json.dumps(dataJSON, ensure_ascii=False))
        return dataJSON
if __name__ == '__main__':
    data = {
        "id": 4040
    }
    dataStr = orderSensitiveMsgEncrypt(data=data).encrypt()
    print("加密结果:", dataStr, type(dataStr))
    dataStr = "bVhJbl3WdFOHXNXd1td"
    orderSensitiveMsgEncrypt(dataStr=dataStr).dencrypt()
    auto_data = {'suc': True, 'body': 'V3kVJoIbNG0dUF5YnsKCSJiaXJ0aGRheSI6bnVsbCwKCSJlbWFpbCI6IiIsCgkiaGVhZFBvcnRyYWl0IjpudWxsLAoJImluZHVzdHJ5IjpudWxsLAoJImluZHVzdHJ5TGlzdCI6W10sCgkiaW5kdXN0cnlPdGhlciI6IiIsCgkiaW5kdXN0cnlWYWx1ZSI6bnVsbCwKCSJpc0xvZ291dCI6MCwKCSJsb2dpbnRpbWUiOiIyMDI2LTA0LTIwIDE5OjQwOjM1IiwKCSJsb2dvdXRUaW1lIjowLAoJIm5pY2tuYW1lIjpudWxsLAoJIm9yZ0Zvcm0iOiIiLAoJIm9yZ0Zvcm1PdGhlciI6IiIsCgkib3JnRm9ybVZhbHVlIjoiIiwKCSJwY2J1aWQiOiI2MDYxMzM3IiwKCSJwaG9uZSI6IjE1MDcwNzM5MTI0IiwKCSJwb3NpdGlvbiI6IiIsCgkicG9zaXRpb25PdGhlciI6IiIsCgkicG9zaXRpb25WYWx1ZSI6IiIsCgkicXEiOiIiLAoJInJlZ1RpbWUiOiIxNzUzODQzMDk4IiwKCSJzZXgiOm51bGwsCgkidWlkIjoiNjA2MTI1MSIsCgkidXNlcm5hbWUiOiJqZl82OTU2MDIyNiIsCgkid2VjaGF0IjoiamZfNjk1NjAyMjYiCn0='}
    print(json.dumps(auto_data, ensure_ascii=False))
    auto_dataJSON = orderSensitiveMsgEncrypt(dencrypt_data=auto_data).auto_dencrypt()
    auto_data_encrypt_JSON = orderSensitiveMsgEncrypt(encrypt_data=auto_dataJSON).auto_encrypt()


