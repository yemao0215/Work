# _*encoding: utf-8 -*_

import time
import json
import hashlib
import requests

default_headers = {
    'User-Agent': 'HQCHIP OpenAPI Python-SDK/1.0',
    "X-Request-Version": '1.0',
}
API_URL = 'http://api.hqchip.com'
API_KEY = "44d2eb5fe9db4a41662ca00ddaa5db21"
API_SEC = "b2c453a9c11ab6bf0d79e3905ddb11a1"


def binary_type(text):
    if isinstance(text, bytes):
        return text.decode('utf-8')
    return text


def gen_sign(secret, params):
    secret = binary_type(secret)
    if hasattr(params, 'items'):
        keys = params.keys()
        # keys.sort()
        keys = sorted(keys)
        params = '%s%s%s' % (secret, '&'.join('%s=%s' % (key, binary_type(params[key])) for key in keys if key not in ('sign',)), secret)
    print(params)
    # sign = hashlib.md5(params).hexdigest().upper()
    sign = hashlib.md5(params.encode('utf-8')).hexdigest().upper()
    return sign


def test_order_detail(order_id):
    url = '{0}/order/detail'.format(API_URL)
    params = {
        'app_key': API_KEY,
        'order_id': order_id,
        'timestamp': int(time.time()),
    }
    params['sign'] = gen_sign(API_SEC, params)
    resp = requests.get(url, params=params, headers=default_headers, timeout=10)
    print(resp.content)
    print(json.dumps(json.loads(resp.content), indent=4))


def test_order_make():
    url = "{0}/order/make/".format(API_URL)
    print(url)
    params = {
        'app_key': API_KEY,
        'timestamp': int(time.time()),
        # 'debug': 'hqchip',
    }
    goods_list = [
        {"out_goods_name": "0603L050YR", "qty": 10, "goods_id": 2500265801},
    ]
    invoice = {
        "type": 1,
        "inv_title": "刘权",
    }
    receive = {
        'consignee': '刘权',
        'province': 6,
        'city': 77,
        'district': 705,
        'address': '深圳市福田区梅林街道梅秀璐1号',
        'mobile': '15814783061',
        'tel': '075512345678',
    }
    data = {
        'goods_list': json.dumps(goods_list),
        'invoice': json.dumps(invoice),
        'receive': json.dumps(receive),
        'shipping_type': 1,
        'goods_type': 1,
        'out_order_no': 'YE20230522930010',
        'product_num': '1',
    }
    print(data)
    sys_params = params.copy()
    sys_params.update(data)
    params['sign'] = gen_sign(API_SEC, sys_params)
    print(params['sign'])
    resp = requests.post(url, params=params, data=data, headers=default_headers, timeout=10)
    print(resp.content)
    data = json.loads(resp.content)
    print(json.dumps(data, indent=4))
    print(data['error_message'])


def test_goods_detail(goods_id):
    url = '{0}/goods/detaily'.format(API_URL)
    params = {
        'app_key': API_KEY,
        'goods_id': goods_id,
        'timestamp': int(time.time()),
    }
    params['sign'] = gen_sign(API_SEC, params)
    resp = requests.get(url, params=params, headers=default_headers, timeout=10)
    print(resp.content)
    print(json.dumps(json.loads(resp.content), indent=4))


def test_goods_mquery():
    url = '{0}/goods/mquery/'.format(API_URL)
    params = {
        'app_key': API_KEY,
        'timestamp': int(time.time()),
    }
    data = [{
        'mpn': 'EEE-FK1C100R',
        'qty': 10,
    }]
    resp = requests.post(url, params=params, data=json.dumps(data), headers=default_headers, timeout=10)
    print(resp.content)
    data = json.loads(resp.content)
    print(json.dumps(data, indent=4))
    print(data['error_message'])
    data = json.loads(resp.content)
    print(data['source_data'][0]['goods']['best']['price_list'][0] <= 0)


def test_order_pay():
    url = '{0}/order/pay/'.format(API_URL)
    print(url)
    params = {
        'app_key': API_KEY,
        'timestamp': int(time.time()),
    }
    data = {
        'order_id': 297522,
        'pay_type': 2,
    }
    sys_params = params.copy()
    sys_params.update(data),
    params['sign'] = gen_sign(API_SEC, sys_params)
    resp = requests.post(url, params=params, data=data, headers=default_headers, timeout=10)
    data = json.loads(resp.content)
    print(json.dumps(data, indent=4))
    print(data['error_message'])


def test_order_delete():
    url = '{0}/order/delete/'.format(API_URL)
    params = {
        'app_key': API_KEY,
        'timestamp': int(time.time()),
    }
    data = {
        'order_id': '161452',
        'out_order_no': '462109',
    }
    sys_params = params.copy()
    sys_params.update(data)
    params['sign'] = gen_sign(API_SEC, sys_params)
    resp = requests.post(url, params=params, data=data, headers=default_headers, timeout=10)
    data = json.loads(resp.content)
    print(json.dumps(data, indent=4))
    print(data['error_message'])


def test_sign():
    params = {
        'app_key': API_KEY,
        'timestamp': 1582186869,
    }
    data = {
        'order_id': 127318,
        'out_order_no': 337148,
        'pay_type': 1,
        'pay_cert': '',
    }
    sys_params = params.copy()
    sys_params.update(data)
    print(gen_sign(API_SEC, sys_params))


def main():
    # test order detail(96111)
    test_order_make()
    # test_goods_detail(2500015692)
    # test_goods_mquery)
    # test_order_pay()
    # test_sign()
    # test_order_delete(


if __name__ == '__main__':
    main()
