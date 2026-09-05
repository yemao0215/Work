import json
import re
import time
import yaml
import requests
import review_order
from huaqiu_order_api.common.my_path import pcb_config_yaml_dir


class NextPcb:

    def __init__(self):
        with open(pcb_config_yaml_dir, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
            self.NEXT_URL = data['NEXT_URL']
            self.HEADERS = {'cookie': 'PHPSESSID={}'.format(data['NEXT_COOKIE']), "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://uat-www.huaqiu.com)"}

    # 外贸下单
    def addcart(self):
        url = '{}/order/addcart'.format(self.NEXT_URL)
        data = {'region_id': '211',
                'service': 'pcb',
                'express': '45',
                'expresstime': '3-5',
                'country': '211',
                'calc_type': '0',
                'deltime': '5 days',
                'activity_code': '',
                'gerber_file_id': '84274',
                'gerber_file': '/uploads/pcbfile/202307/07/4层gerber.zip',
                'active': '',
                'history_pcb_order_sn': '0',
                'blind': '0',
                'pbnum': '1',
                'isgerber': '1',
                'plate_type': 'Fr-4',
                'thermalc': '',
                'rogers': '',
                'board_tg': 'TG130',
                'units': '1',
                'blayer': '4',
                'bwidth': '10',
                'blength': '10',
                'layoutx': '1',
                'layouty': '1',
                'sidedirection': 'N/A',
                'sidewidth': '0',
                'bheight': '1.6',
                'color': 'Green',
                'charcolor': 'White',
                'copper': '1',
                'insidecopper': '0.5',
                'lineweight': '6',
                'vias': '0.3',
                'cover': 'Tenting Vias',
                'spray': 'HASL',
                'cjh': '',
                'beveledge': '0',
                'impendance': '0',
                'via_in_pad': 'N/A',
                'testpoint': '0',
                'test': 'Batch Flying Probe Test',
                'zknum': '0',
                'bankong': '',
                'baobian': '',
                'pressing': '',
                'bcount': '100',
                'pcscount': '2',
                'slice_report': '0',
                'shipment_report': '0',
                'report_type': '0',
                'has_period': '2',
                'pcb_po_number': '',
                'pcb_note': '',
                'review_file': '0',
                'fid': '84274'}
        resp = requests.post(url, data=data, headers=self.HEADERS)
        data = json.loads(resp.content)
        print(json.dumps(data, indent=4))
        return data['data']['order_id']

    def paymentTotal(self):
        order_id = NextPcb().addcart()
        url = '{}/member/ajax/paymentTotal'.format(self.NEXT_URL)
        data = f'order_id={order_id}&pay_name=balance&express=38&user_ship_account=&address_id=9430' \
               f'&discount_order%5B0%5D%5Bdiscount_order_id%5D={order_id}&discount_order%5B0%5D%5Bdiscount_key' \
               f'%5D=&confirm=1&type=&rel_id=&secret_key=&billing_type=1'
        resp = requests.post(url, data=data, headers=self.HEADERS)
        data = json.loads(resp.content)
        print(json.dumps(data, indent=4))
        group_id = (data['data']['group']['group_id'])
        url2 = '{}/order/makepay'.format(self.NEXT_URL)
        data2 = f'group_id={group_id}&pay_name=balance&express=38&address_id=9430&secret_key='
        resp2 = requests.post(url2, data=data2, headers=self.HEADERS)
        data2 = json.loads(resp2.content)
        print(json.dumps(data2, indent=4))
        if data2['msg'] == 'success':
            print('\033[91m' + data2['data']['group']['orderList'][0]['pcb_order_sn'] + '    付款成功\033[00m')
        return data2['data']['group']['orderList'][0]['pcb_order_sn']

    def review_order(self):
        next_order_id = NextPcb().paymentTotal()
        url = '{}/admin/PcbOrder/index'.format(self.NEXT_URL)
        data = {'pageNum': 1, 'pcb_order_sn': next_order_id, 'timetype': 'order'}
        time.sleep(3.5)
        resp = requests.post(url, data=data, headers=self.HEADERS)
        order_id = re.findall('<td>([^<>]+)</td>', resp.text)[1]
        print('\033[91mPCB订单号：' + order_id + '\033[00m')
        review_order.ReviewOrder().run(int(order_id))
