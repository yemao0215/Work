# -* encoding: utf-8 -*-
import jsonpath
import yaml
import time
import json
import hashlib
import requests
import review_order

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import pcb_config_yaml_dir

default_headers = {
    'User-Agent': 'HQPCB OpenAPI Python-SDK/1.0;Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)'
    # 'host': 'debugapi.hqpcb.com'
}


class PcbOrder:
    def __init__(self, rss=None):
        with open(pcb_config_yaml_dir, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.API_KEY = data['API_KEY']
        self.API_SEC = data['API_SEC']
        self.API_URL = data['API_URL']
        self.HQPCB_URL = data['HQJFPCB_URL']
        self.ORDER_ID = ''
        self.rss = rss
        self.headers = {"Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
                        }

    def binary_type(self, text):
        if not isinstance(text, str):
            text = str(text)
        return text

    def gen_sign(self, secret, params):
        secret = self.binary_type(secret)
        if hasattr(params, 'items'):
            keys = list(params.keys())
            keys.sort()

            params = '%s%s%s' % (secret, '&'.join('%s=%s' % (key, self.binary_type(params[key])) for key in keys \
                                                  if key not in ('sign',)), secret)
        params = params.encode('utf-8')
        sign = hashlib.md5(params).hexdigest().upper()
        return sign

    def test_order_detail(self, out_order_no, order_id=None):
        url = '{0}/order/'.format(self.API_URL)
        params = {
            'appid': self.API_KEY,
            'timestamp': int(time.time()),
        }
        if out_order_no:
            params['out_order_no'] = out_order_no
        if order_id:
            params['order_id'] = order_id
        params['signature'] = self.gen_sign(self.API_SEC, params)
        resp = requests.get(url, params=params, headers=default_headers, timeout=10)
        print(resp.content)
        print(json.dumps(json.loads(resp.content), indent=4))

    def test_order_delete(self, out_order_no, order_id=None):
        # API_URL = 'http://192.168.12.26'
        url = '{0}/order/'.format(self.API_URL)
        params = {
            'appid': self.API_KEY,
            'timestamp': int(time.time()),
        }
        if out_order_no:
            params['out_order_no'] = out_order_no
        if order_id:
            params['order_id'] = order_id
        params['signature'] = self.gen_sign(self.API_SEC, params)
        resp = requests.delete(url, params=params, headers=default_headers, timeout=10)
        print(resp.content)
        print(json.dumps(json.loads(resp.content), indent=4))

    def test_order_make(self, order_invoice_json=None):
        # if order_type == 'FPC':
        #     save_order_url = '{0}/quote/save'.format(self.HQPCB_URL)
        #     save_order_body = {
        #         "board_type": "FPC",
        #         "blayer": 2,
        #         "units": 1,
        #         "cross_board": 1,
        #         "pbnum": 1,
        #         "layouty": 1,
        #         "layoutx": 1,
        #         "bwidth": 6,
        #         "blength": 12,
        #         "bcount": 5,
        #         "sidedirection": "无",
        #         "sidewidth": 0,
        #         "material": "有胶电解",
        #         "pi_thickness": 12.5,
        #         "bheight": 0.13,
        #         "copper": 0.33,
        #         "insidecopper": 0,
        #         "lineweight": 6,
        #         "vias": 0.3,
        #         "cover": "覆盖膜双面",
        #         "color": "黄色",
        #         "charcolor": "白色",
        #         "spray": "沉金",
        #         "cjh": "1",
        #         "electrogilding_thickness": "0",
        #         "forming_type": "激光成型",
        #         "back_gum_type": "无",
        #         "electromagnetic_membrane": "0",
        #         "conducting_resin": "0",
        #         "impendance": "0",
        #         "reinforce": "0",
        #         "reinforce_steel": "",
        #         "steel_thickness": "0.1",
        #         "reinforce_aluminium": "",
        #         "aluminium_thickness": "0.3",
        #         "reinforce_fr4": "",
        #         "fr4_thickness": "0.1",
        #         "reinforce_fingerpi": "",
        #         "fingerpi_thickness": "0.1",
        #         "reinforce_otherpi": "",
        #         "otherpi_thickness": "0.05",
        #         "overlay": "[object Object]",
        #         "test": "批量飞测",
        #         "review_file": "0",
        #         "invoice": "不需要",
        #         "report": "",
        #         "report_type": "0",
        #         "province": "6",
        #         "city": "77",
        #         "express": "0",
        #         "expressStr": "",
        #         "type": "2",
        #         "setwidth": "6.00",
        #         "setlength": "12.00",
        #         "deltime": "正常6天",
        #         "weight": "0.01",
        #         "m": "360",
        #         "period_format": "undefined",
        #     }
        #     save_order_res = self.rss.post(url=save_order_url, json=save_order_body, headers=self.headers).json()
        #     print(save_order_res)
        # else:

            url = '{0}/order/make'.format(self.API_URL)
            params = {
                'appid': self.API_KEY,
                'timestamp': int(time.time()),
            }
            data = {
                'out_order_no': '',
                'address': '深圳市宝安区福永街道桥头社区宝安大道6267号世峰大厦807',
                'express': '顺丰寄付',
                'bwidth': '10',  # 板子宽度
                'blength': '10',  # 板子长度
                'blayer': '2',  # 板子层数
                'pcb_file_path': 'http://file.elecfans.net/group1/M00/00/16/wKgUHWKdxkOAQy5sAAEB2H8R-4I608.rar?attname=28033-1869434_%E6%B5%8B%E8%AF%951.2.3.rar',
                # 'pcb_file_path': 'https://space.dev.digipcba.com/ActiveManufacturing/Download/494069d895a44685b960f0ccf958486e',
                # 'pcb_file_path': 'https://smt.hqchip.com/file/5/320954/bd95f7b74c1168ede873f630833791e9/patch.zip',
                # 'pcb_file_path': 'https://space.dev.digipcba.com/ActiveManufacturing/Download/2db9c3ef0e5148658f58171d79ba3ca7',
                'pcb_file_name': 'WIFI digipcba.rar',
                'bcount': '5',  # 板子数量
                'pbnum': '1',
                'bheight': '1.6',
                'color': '绿色',
                'charcolor': '白色',
                'spray': '有铅喷锡',
                'cover': '过孔盖油',
                'sidedirection': '无',
                'sidewidth': '0',
                'copper': '1',
                'layoutx': '2',
                'layouty': '3',
                'cjh': 2,
                'recevman': '测试',
                'recevtel': '13632845795',
                'orderman': '测试',
                'ordertel': '13632845795',
                'note': r"钻带的两个文件夹取\.DRL\ &'+ 即可。",
                'testpoint': '0',
                'vias': '0.3',
                'bankong': '0',
                'blind': '0',
                'impendance': '0',
                'lineweight': '6',
                'invoice_type': '增票',
                'hq_pack': '0',
                'report': '切片报告',
                'report_type': 2,
                'review_file': '0',
                'user_stamp': '1',
                'returnid': [order_invoice_json['order'] if 'order' in order_invoice_json else '' for _ in range(1)][0]
            }
            if isinstance(order_invoice_json, dict) and "invoice" in order_invoice_json:
               # invoice_json = {"invoice_type": '增票', "invoice_title": '测试专用账号', "invoice_number": '12345678'}
               data.update(order_invoice_json['invoice'])
            sys_params = params.copy()
            sys_params.update(data)
            params['signature'] = self.gen_sign(self.API_SEC, sys_params)
            resp = requests.post(url, params=params, data=data, headers=default_headers, timeout=10)
            data = json.loads(resp.content)
            logger.info(json.dumps(data, indent=4))
            logger.info(data['error_message'])
            order_id = jsonpath.jsonpath(data, '$..order_id')[0]
            logger.info(f"成功获取到生成的订单id为：{order_id}")
            setattr(Data, "pcb_order_id", order_id)

            return self

    def test_order_audit(self, dict_obj=None):
        url = '{0}/order/make'.format(self.API_URL)
        params = {
            'appid': self.API_KEY,
            'timestamp': int(time.time()),
        }
        data = {
            'out_order_no': '',
            'address': '深圳市宝安区福永街道桥头社区宝安大道6267号世峰大厦807',
            'express': '顺丰寄付',
            'bwidth': '10',
            'blength': '10',
            'blayer': '6',
            'pcb_file_path': 'http://file.elecfans.net/group1/M00/00/16/wKgUHWKdxkOAQy5sAAEB2H8R-4I608.rar?attname=28033-1869434_%E6%B5%8B%E8%AF%951.2.3.rar',
            # 'pcb_file_path': 'https://space.dev.digipcba.com/ActiveManufacturing/Download/494069d895a44685b960f0ccf958486e',
            # 'pcb_file_path': 'https://smt.hqchip.com/file/5/320954/bd95f7b74c1168ede873f630833791e9/patch.zip',
            # 'pcb_file_path': 'https://space.dev.digipcba.com/ActiveManufacturing/Download/2db9c3ef0e5148658f58171d79ba3ca7',
            'pcb_file_name': 'WIFI digipcba.rar',
            'bcount': '10',
            'pbnum': '1',
            'bheight': '1.6',
            'color': '绿色',
            'charcolor': '白色',
            'spray': '有铅喷锡',
            'cover': '过孔盖油',
            'sidedirection': '无',
            'sidewidth': '0',
            'copper': '1',
            'layoutx': '2',
            'layouty': '3',
            'cjh': 2,
            'recevman': '测试',
            'recevtel': '13632845795',
            'orderman': '测试',
            'ordertel': '13632845795',
            'note': r"钻带的两个文件夹取\.DRL\ &'+ 即可。",
            'testpoint': '0',
            'vias': '0.3',
            'bankong': '0',
            'blind': '0',
            'impendance': '0',
            'lineweight': '6',
            'invoice_type': '增票',
            'hq_pack': '0',
            'report': '切片报告',
            'report_type': 2,
            'review_file': '0',
            'user_stamp': '1',
            # 'returnid': '1672585'
        }
        if dict_obj != None:
            if isinstance(dict_obj, dict):
                for v in data:
                    for k in dict_obj:
                        if k == v:
                            if k == "blayer": # 判断key值是否为板子层数
                                blayer_lst = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
                                if dict_obj[k] in blayer_lst:
                                    data[v] = dict_obj[k]
                                else:
                                    data[v] = ""
                                    print(f"k为blayer，不满足板子层数要求")
                            else:
                                data[v] = dict_obj[k]
                        else:
                            print(f"dict_obj无对应更新字段，此时：k为{k}, v为{v}，dict_obj：{dict_obj}")

        sys_params = params.copy()
        sys_params.update(data)
        params['signature'] = self.gen_sign(self.API_SEC, sys_params)
        resp = requests.post(url, params=params, data=data, headers=default_headers, timeout=10)
        data = json.loads(resp.content)
        print(json.dumps(data, indent=4))
        print(data['error_message'])
        order_id, amount = review_order.ReviewOrder().run(data['response_data']['order_id'])
        print('自动生成的订单ID：' + str(data['response_data']['order_id']))
        return order_id, amount

    def test_order_pay(self, order_id, amount):
        url = '{0}/payment/pay'.format(self.API_URL)
        params = {
            'appid': self.API_KEY,
            'timestamp': int(time.time()),
        }
        data = {
            'order_id': order_id,
            'pay_money': amount,
            'pay_type': 2,
        }
        sys_params = params.copy()
        sys_params.update(data)
        params['signature'] = self.gen_sign(self.API_SEC, sys_params)
        resp = requests.post(url, params=params, data=data, headers=default_headers, timeout=10)
        data = json.loads(resp.content)
        # print(json.dumps(data, indent=4))
        print(data['error_message'])

    def test_sign(self):
        params = {
            'appid': self.API_KEY,
            'timestamp': 1588215487,
        }
        data = {
            'message': '<p>1. 请锣出来 2. 请删除+号 </p >',
            'question_id': 269145,
        }
        sys_params = params.copy()
        sys_params.update(data)
        print(self.gen_sign(self.API_SEC, sys_params))

    def test_order_compute(self):
        url = '{0}/compute/'.format(self.API_URL)
        data = {
            'units': '1',
            'blayer': '2',
            'bheight': '1.6',
            'lineweight': '6',
            'bga': '0',
            'vias': '0.3',
            'bankong': '0',
            'blind': '0',
            'impendance': '0',
            'pressing': '',
            'pbnum': '1',
            'sidewidth': '0',
            'sidedirection': '无',
            'bwidth': '10.00',
            'blength': '10.00',
            'bcount': '500',
            'copper': '1',
            'insidecopper': '0',
            'cover': '过孔盖油',
            'charcolor': '白色',
            'spray': '有铅喷锡',
            'color': '绿色',
            'test': '批量飞测',
            'testpoint': '0',
            'express': '顺丰寄付',
            'invoice': '不需要',
            'cjh': '1',
            'zknum': '0',
            'address': '广东省深圳市福田区',
        }
        params = {
            'appid': self.API_KEY,
            # 'timestamp': int(time.time()),
        }
        sys_params = params.copy()
        sys_params.update(data)
        # params['sign'] = gen_sign(API_SEC, sys_params)
        resp = requests.post(url, params=params, data=data, headers=default_headers, timeout=10)
        data = json.loads(resp.content)
        print(json.dumps(data, indent=4))
        print(data['error_message'])

    def test_parse_address(self):
        url = '{0}/compute/parserAddress/'.format(self.API_URL)
        params = {
            'appid': self.API_KEY,
            'timestamp': int(time.time()),
        }
        data = {
            'address': '福永街道桥头社区宝安大道6267号世峰大厦807'
        }
        sys_params = params.copy()
        sys_params.update(data)
        params['signature'] = self.gen_sign(self.API_SEC, sys_params)
        resp = requests.post(url, params=params, data=data, headers=default_headers, timeout=10)
        print(resp.content)
        print(json.dumps(json.loads(resp.content), indent=4))

    def test_parse_address(self):
        url = '{0}/compute/parseAddress/'.format(self.API_URL)
        params = {
            'appid': self.API_KEY,
            'timestamp': int(time.time()),
            'address': '福田区福永街道桥头社区宝安大道6267号'
        }

        params['signature'] = self.gen_sign(self.API_SEC, params)
        resp = requests.get(url, params=params, headers=default_headers, timeout=10)
        print(resp.content)
        data = json.loads(resp.content)
        print(json.dumps(data, indent=4))
        print(data['error_message'])

    def test_order_payurl(self, order_id):
        url = '{0}/payment/payUrl/'.format(self.API_URL)
        params = {
            'appid': self.API_KEY,
            'timestamp': int(time.time()),
            'order_id': order_id,
            'pay_name': 'alipay',
        }
        # sys_params = params.copy()
        # sys_params.update(data)
        params['signature'] = self.gen_sign(self.API_SEC, params)
        resp = requests.get(url, params=params, headers=default_headers, timeout=10)
        print(resp.content)
        print(json.dumps(json.loads(resp.content), indent=4))

    def test_order_tracking(self, order_id):
        url = '{0}/order/tracking/'.format(self.API_URL)
        params = {
            'appid': self.API_KEY,
            'timestamp': int(time.time()),
            'order_id': order_id,
        }
        # sys_params = params.copy()
        # sys_params.update(data)
        params['signature'] = self.gen_sign(self.API_SEC, params)
        resp = requests.get(url, params=params, headers=default_headers, timeout=10)
        print(resp.content)
        print(json.dumps(json.loads(resp.content), indent=4))

    def test_order_deltimes(self, order_id):
        url = '{0}/order/deltimes/'.format(self.API_URL)
        params = {
            'appid': self.API_KEY,
            'timestamp': int(time.time()),
            'order_id': order_id,
            'debug': 'deltime',
        }
        # sys_params = params.copy()
        # sys_params.update(data)
        params['signature'] = self.gen_sign(self.API_SEC, params)
        resp = requests.get(url, params=params, headers=default_headers, timeout=10)
        print(resp.content)
        print(json.dumps(json.loads(resp.content), indent=4, ensure_ascii=False))

    def test_smd_compute(self):
        data = {
            'stencil_frame': '钢网',
            'elec_tropolishing': '1',
            'stencil_size': '30*40',
            'stencil_side': '2',
            'printing_type': '1',
            'engineering_require': '1',
            'stencil_thickness': '0.12',
            'stencil_num': '5',
            'stencil_type': '红胶网',
            'existing_fiducials': '半刻',
            'province': '广东省',
            'city': '深圳市',
            'ship_name': '顺丰寄付',
            'invoice': '普票',
            'deltime': '24小时'
        }
        params = {
            'appid': self.API_KEY,
            'timestamp': '1656487067',
        }
        sys_params = params.copy()
        sys_params.update(data)

        print(sys_params)
        params['signature'] = self.gen_sign(self.API_SEC, sys_params)
        print(params['sign'])

    def run_order_pay(self):
        order_id, amount = self.test_order_audit()
        self.test_order_pay(order_id, amount)
        return order_id

#     def main(self):
#         # test_smd_compute()
#         # test_order_deltimes('1871865,1871915')
#         # test_order_detail(None, 1783908)
#         self.test_order_make()
#         # test_order_delete('TEST2021012002')
#         # test_order_detail(None, 500407)
#         # test_goods_mquery()
#         # test_order_pay('1672591')
#         # test_order_compute()
#         # test_parse_address()
#         # test_order_payurl(500406)
#         # test_order_tracking(785801)
#
#
if __name__ == '__main__':
    from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
    rss = SSO_Reception('https://uat-www.hqpcb.com').login()
    # PcbOrder(rss).test_order_make(type="FPC")
