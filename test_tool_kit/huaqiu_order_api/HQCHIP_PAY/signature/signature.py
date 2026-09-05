import hashlib
import json
import time
from huaqiu_order_api.common.loguru_logger import logger

class SignAture:
    # 签名生成公共方法

    def __init__(self, app_sec):

        self.app_sec = app_sec

        # self.out_order_no = out_order_no


    def binary_type(self, text):

        if isinstance(text, bytes):
            return text.encode('utf-8')
        return text