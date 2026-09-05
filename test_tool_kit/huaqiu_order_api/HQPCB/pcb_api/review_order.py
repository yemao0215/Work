import time
import json
import hashlib
import requests
import pprint
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import pcb_config_yaml_dir

default_headers = {
    'User-Agent': 'HQPCB OpenAPI Python-SDK/1.0;Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)'
}


class ReviewOrder:
    def __init__(self):
        with open(pcb_config_yaml_dir, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HEADERS = {"Cookie": "PHPSESSID={}".format(data['PHPSESSID']), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}
        self.API_KEY = data['API_KEY']
        self.API_SEC = data['API_SEC']
        self.API_URL = data['API_URL']
        self.HQJFPCB_URL = data['HQJFPCB_URL']
        self.ORDER_ID = ''

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

    # 查询订单详情
    def get_order(self):
        url = '{}/order'.format(self.API_URL)
        params = {
            'appid': self.API_KEY,
            'timestamp': int(time.time()),
            'order_id': self.ORDER_ID
        }
        sys_params = params.copy()
        params['signature'] = self.gen_sign(self.API_SEC, sys_params)
        resp = requests.get(url, params=params, headers=default_headers, timeout=10)
        return_data = json.loads(resp.content)
        # print('\033[91m获取订单信息\033[00m')
        # pprint.pprint(return_data)
        return return_data

    # 获取订单信息并切片
    def split_order(self):
        get_data = self.get_order()
        order = get_data['response_data']['order_craft']['order']
        detail = get_data['response_data']['order_detail']
        fee = get_data['response_data']['order_fee']
        receive = get_data['response_data']['receive']
        data = get_data['response_data']
        return order, detail, fee, receive, data

    # PCB后台预审修改订单
    def update_order(self):
        url = '{}/hqjfpcb/order/updateorder/navTabId'.format(self.HQJFPCB_URL)
        order, detail, fee, receive, data = self.split_order()
        print(order)
        data = {
            'id': data['order_id'],
            'returnid': detail['returnid'],
            'pack_id': '0',  # 是否合并发货
            'schemeid': '0',
            'is_vip': '1',
            'order_special_status': '1',
            'blayer': order['blayer'],
            'bheight': order['bheight'],
            'bga': order['bga'],
            'bcount': order['bcount'],
            'units': order['units'],
            'blength': order['blength'],
            'color': order['color'],
            'impendance': order['impendance'],
            'layoutx': order['layoutx'],
            'layouty': order['layouty'],
            'bwidth': order['bwidth'],
            'charcolor': order['charcolor'],
            'insidecopper': order['insidecopper'],
            'sidewidth': order['sidewidth'],
            'sidedirection': detail['sidedirection'],
            'lineweight': detail['lineweight'],
            'spray': detail['spray'],
            'copper': detail['copper'],
            'pbnum': detail['pbnum'],
            'vias': detail['vias'],
            'cover': detail['cover'],
            'deltime': detail['deltime'],
            'bankong': detail['bankong'],
            'tongkong': '1',  # PTH孔 '1' 小于等于6.0mm  '6.1' 大于6.0mm
            'test': detail['test'], 'testid': '0',
            'area': detail['area'],
            'baobian': detail['baobian'],
            'konghuan': '4',  # 孔环
            'pressing': detail['pressing'],
            'blind': detail['blind'],
            'hdi_jgzk': detail['hdi_jgzk'],
            'hdi_tk': detail['hdi_tk'],
            'hdi_szsk': detail['hdi_szsk'],
            'hdi_vop': detail['hdi_vop'],
            'hdi_yahe': detail['hdi_yahe'],
            'board_brand': detail['board_brand'],
            'board_tg': detail['board_tg'],
            'has_period': detail['has_period'],
            'period_format': detail['period_format'],
            'heat_factor': '1.0W',
            'coverlay': '黄色',
            'stiffeners': '无',
            'via_in_pad': detail['via_in_pad'],
            'board_type': detail['board_type'],
            'pnl_usage_rate': '88',  # 开料利用率
            'hqimpe_url': '',
            'cjarea': detail['cjarea'] + '%',
            'cjh': detail['cjh'],
            'luocao': detail['luocao'],
            'zknum': detail['zknum'],
            'zknum_density': '0万/㎡',
            'vcut': '2',  # V割  1是 2否
            'cutnum': detail['cutnum'],
            'luocheng': detail['luocheng'],
            'total_luocheng': '0',
            'overlay[seq]': '',
            'testpoint': detail['testpoint'],
            'total_testpoint': '0',
            'beveledge': detail['beveledge'],
            'pad_width': '0.1',  # 焊盘宽度
            'file_standard': '2',  # 资料类别 0请选择 1标准 2非标准
            'invoice': '不需要',
            'shipping_id': '1',  # 快递id 默认顺丰
            'standardfee': '6956',
            'change_fee': '0.0',
            'inv_change_fee': '0.00',
            'boardfee': fee['boardfee'],
            'expressage': fee['expressage'],
            '_expressage': fee['expressage'],
            'extra_urgent_fee': fee['extraurgentfee'],
            '_webpay': '6956',
            'discount': '1',
            'note': detail['note'],
            'iste': '0',
            'marketremark': '',
            'spraydemand': '1',
            'label_remark': '',
            'result': '',
            'sensitive': '0',
            'cid': detail['cid'],
            'user_order_sn': '',
            'user_panel_sn': '',
            'specification': '',
            'fhd_title': '',
            'report_type': detail['report_type'],
            'report_email': detail['report_email'],
            'hq_pack': order['hq_pack'],
            'sh': order['sh'],
            'fh': order['fh'],
            'review_file': order['review_file'],
            'inner_box_label': order['inner_box_label'],
            'outer_box_label': order['outer_box_label'],
            'order_wetcard': '0',
            # 'paper': detail['paper'],
            # 'user_stamp': detail['user_stamp'],
            'insurance_type': order['insurance_type'],
            'insurance': order['insurance'],
            'passfield[idcard][a:2:{s:1:"m";s:12:"OrderProfile";s:1:"p";s:7:"1672106";}]': '',
            'recevman': receive['recevman'],
            'recevtel': receive['recevtel'],
            'passfield[address][a:2:{s: 1: "m";s: 5:"Order";s: 1:"p";s: 7:"1672106";}]': receive['address'],
            'address': receive['address'],
            'orderman': receive['orderman'],
            'passfield[ordertel][a:2:{s: 1: "m";s: 5:"Order";s: 1:"p";s: 7:"1672106";}]': receive['ordertel'],
            'overlay[email]': '',
            'overlay[contact]': '',
            'invoice_kind': '',
            'bill_id': '',
            'invoicetop': '',
            'taxnumber': '',
            'inv_bank': '',
            'inv_account': '',
            'inv_address': '',
            'inv_tel': '',
            'orderstyle': data['order_style'],
            'ajax': '1',
            'is_iframe': '1',
            'iframe_confirm': 'false'
        }
        for i in range(len(detail['hdi_process_types'].split(','))):
            data.update({'hdi_process_types[]': detail['hdi_process_types'].split(',')[i]})
        header = default_headers.copy()
        header.update(self.HEADERS)
        resp = requests.post(url, data=data, headers=header, timeout=10)
        return_data = json.loads(resp.content)
        logger.info('\033[91m后台修改订单\033[00m')
        # logger.info(return_data)
        if "confirmMsg" in return_data:
            if return_data["confirmMsg"] == "PCBA订单请沟通添加华秋UL":
                data["has_period"] = "华秋UL+周期"
                resp = requests.post(url, data=data, headers=header, timeout=10)
                return_data = json.loads(resp.content)
        logger.info(return_data)
        order_id, amount = self.passorder()
        return order_id, amount

    # PCB后台审核
    def passorder(self):
        url = '{}/hqjfpcb/order/passorder/navTabId/'.format(self.HQJFPCB_URL)
        order, detail, fee, receive, data = self.split_order()
        data = {
            'id': data['order_id'],
            'webpay': data['total_amount'],
            'blayer': detail['blayer'],
            'area': detail['area'],
            'pack_id': '0',
            'cjh': detail['cjh'],
            'returnid': detail['returnid'],
            'spray': detail['spray'],
            'copper': detail['copper'],
            'zknum': detail['zknum'],
            # 'zknum_density': '0万/㎡',
            'luocheng': detail['luocheng'],
            # 'total_luocheng': '0',
            'testpoint': detail['testpoint'],
            # 'total_testpoint': '0',
            'note': '',
            'iste': '0',
            'marketremark': '',
            'spraydemand': '1',
            'order_special_status': '1',
            'result': '',
            'sensitive': '0',
            'modifyfile': '0',
            'passfield[idcard][a:2:{s: 1: "m";s: 12:"OrderProfile";s: 1:"p";s: 7:"1672194";}]': '',
            'recevman': receive['recevman'],
            'passfield[recevtel][a:2:{s: 1: "m";s: 5:"Order";s: 1:"p";s: 7:"1672194";}]': receive['recevtel'],
            'passfield[address][a:2:{s: 1: "m";s: 5:"Order";s: 1:"p";s: 7:"1672194";}]': receive['address'],
            'address': receive['address'],
            'orderman': receive['orderman'],
            'passfield[ordertel][a:2:{s: 1: "m";s: 5:"Order";s: 1:"p";s: 7:"1672194";}]': receive['ordertel'],
            'passfield[taxnumber][a:2:{s: 1: "m";s: 5:"Order";s: 1:"p";s: 7:"1672194";}]': '',
            'ajax': 1,
            'is_iframe': 1,
            'iframe_confirm': 'false'
        }
        header = default_headers.copy()
        header.update(self.HEADERS)
        resp = requests.post(url, data=data, headers=header)
        return_data = json.loads(resp.content)
        logger.info('\033[91m审核订单\033[00m')
        logger.info(return_data)
        return data['id'], data['webpay']

    def run(self, order_id):
        self.ORDER_ID = order_id
        order_id, amount = self.update_order()
        return order_id, amount

    def run_get_order(self, order_id):
        self.ORDER_ID = order_id
        pprint.pprint(self.get_order())

