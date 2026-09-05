import urllib
from typing import Dict, Any

import hashlib
from urllib.parse import urlencode, quote

from cryptography.hazmat.primitives.hashes import SHA1

from huaqiu_order_api.common.loguru_logger import logger

class OpenapiSignature:
    # 签名生成公共方法

    def __init__(self, app_sec):

        self.app_sec = app_sec

        # self.out_order_no = out_order_no


    def binary_type(self, text):

        if isinstance(text, bytes):
            return text.encode('utf-8')
        return text


    def gen_sign(self, secret, params):
        """
        :param secret 密钥 即APP_SEC
        :parman
        """
        secret = self.binary_type(secret)
        if hasattr(params, "items"):
            keys = params.keys()
            # keys.sort()
            keys = sorted(keys)
            # sorted(keys)
            # print(params[key])
            """拼接解析：
            secret 是一个字符串变量，表示密钥或秘密信息。
            keys 是一个列表，包含了需要拼接到URL查询字符串中的参数名。
            self.binary_type() 是一个方法调用，用于将参数值转换为二进制类型。
            urllib.parse.quote() 函数用于对参数值进行URL编码，将特殊字符转换为URL安全的格式。
            str(params[key]).replace(' ', '+') 将参数值转换为字符串，并将空格替换为加号（"+"）。
            safe="+" 指定了在URL编码时，只对加号（"+"）进行编码，其他特殊字符不进行编码。
            '&'.join() 函数用于将多个参数拼接成一个字符串，每个参数之间用"&"符号连接。
            '%s=%s' % (key, ...) 是字符串格式化操作，用于生成形如 "key=value" 的参数字符串。
            secret 被重复两次，作为URL查询字符串的开头和结尾。
            """
            params = '%s%s%s' % (secret,
                                 '&'.join('%s=%s' % (key, self.binary_type(urllib.parse.quote(str(params[key]).replace(' ', '+'), safe="+"))) for key in keys if key not in ('signature',)),
                                 secret)
        print(params)
        # sign = hashlib.md5(params).hexdigest().upper()
        sign = hashlib.md5(params.encode('utf-8')).hexdigest().upper().lower()
        logger.info(sign)
        return sign

    def hqchip_sign_main(self, params, data):
        sys_params = params.copy()
        sys_params.update(data)
        logger.info(sys_params)
        sign = self.gen_sign(self.app_sec, sys_params)

        return sign



if __name__ == '__main__':
    pass
