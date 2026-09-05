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
            params = '%s%s%s' % (
            secret, '&'.join('%s=%s' % (key, self.binary_type(params[key])) for key in keys if key not in ('sign',)),
            secret)
        print(params)
        # sign = hashlib.md5(params).hexdigest().upper()
        sign = hashlib.md5(params.encode('utf-8')).hexdigest().upper()
        logger.info(sign)
        return sign

    def hqchip_sign_main(self, params, data):
        sys_params = params.copy()
        sys_params.update(data)
        sign = self.gen_sign(self.app_sec, sys_params)

        return sign

if __name__ == '__main__':
    app_sec = "7b0594651ce4ab534b3f941e5dc9fe63"
    params = {'app_key': 'c11ff533617d2aa45ffd0e1994fb2cd7', 'timestamp': 1788492758}
    data = {'goods_list': '[{"out_goods_name": "CESHI260902", "out_remark": "\\u6d4b\\u8bd5", "qty": "100", "goods_id": "1019147090"}]', 'invoice': '{"type": "1", "inv_title": "\\u5218\\u6743"}', 'receive': '{"consignee": "\\u5f20\\u4e09", "province": 3, "city": 36, "district": 398, "tel": "075512345678", "address": "\\u6c11\\u6cbb\\u8857\\u90531114", "mobile": "15070739150"}', 'shipping_type': 1, 'goods_type': 1, 'out_order_no': 'AutoTest202609040001343', 'product_num': '1', 'order_tracking_number': 'AutoTest202609040001343', 'remark': '自动化测试', 'partial_order_alloweb': '0'}

    SignAture().hqchip_sign_main(params,data)
