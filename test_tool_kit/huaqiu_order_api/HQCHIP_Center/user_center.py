import calendar
import json
import re
import time
from datetime import datetime

import jsonpath
import requests
import yaml

from huaqiu_order_api.SSO_Reception.orderSensitiveMsgEncrypt import orderSensitiveMsgEncrypt
# from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
# from huaqiu_order_-api.common.my_data import Data
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file

with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)
passport_url = data['PassPort_URL']
center_java_url = data['center_java_url']
center_php_url = data['center_php_url']
HQCHIP_URL = data['HQCHIP_URL']
Assets_Center_url = data['Assets_Center_url']



def get_center_push():
    pass


def get_invoice(rss, invoice_type, plain_type, type=None):

    """获取用户中心发票信息ID
    :param invoice_type 发票类型 1增值税 2普票
    :param plain_type 普票类型 1公司  2 个人/政府
    """
    url = '{}/web/invoice/query/list?invoiceType={}&type={}'.format(center_java_url, invoice_type, plain_type)
    # print(url)
    token = getattr(Data, 'token')
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Authorization': token}
    if invoice_type != 0:
        if type != None:
            url = '{}/web/encodeDecode/invoice/query/list?invoiceType={}&type={}'.format(center_java_url, invoice_type, plain_type)
        while True:
            i = 0
            res = rss.get(url=url,  headers=headers).json()
            # 获取字典的键值（名称）并且以list汇总输出
            if type != None:
                res = orderSensitiveMsgEncrypt(encrypt_data=res).auto_dencrypt()
            res_key = list(res.keys())
            if "body" in res_key:
                invoice = jsonpath.jsonpath(res, '$.body')
                for k in invoice[0]:
                    if k['status'] == 1:
                        return k['id']
            else:
                if invoice_type != 0:
                    print("开始新建发票信息")
                    insert_invoice_url = '{}/web/invoice/insert'.format(center_java_url)
                    insert_invoice_body = None
                    if invoice_type == 2:
                        insert_invoice_body = {"invoiceTitle": "测试发票", "taxCode": "12345678", "invoiceType": invoice_type, "type": plain_type}
                    elif invoice_type == 1:
                        insert_invoice_body = {"invoiceTitle": "深圳华秋电子有限公司", "taxCode": "91440300581577931W", "invoiceType": invoice_type, "type": plain_type,
                                               "taxAddr": "广东省深圳市福田区中康路新一代产业园1栋5楼", "taxBankAccount": "755918494010404", "taxTel": "0755-25324881",
                                               "taxBank": "招商银行深圳分行"
                                               }
                    rss.post(url=insert_invoice_url, json=insert_invoice_body, headers=headers)
                    print("新建发票信息成功")
                    i += 1
                    if i > 1:
                        break
def get_invoice_msg(rss, invoice_type, plain_type):
    """获取用户中心发票id、发票抬头、税号
    :param invoice_type 发票类型 1增值税 2普票
    :param plain_type 普票类型 1公司  2 个人/政府
    """
    url = '{}/web/invoice/query/list?invoiceType={}&type={}'.format(center_java_url, invoice_type, plain_type)
    token = getattr(Data, 'token')
    headers = {'Content-Type': 'application/json;charset=UTF-8', 'Authorization': token}
    if invoice_type != 0:
        while True:
            i = 0
            res = rss.post(url=url,  headers=headers).json()
            # 获取字典的键值（名称）并且以list汇总输出
            res_key = list(res.keys())
            if "body" in res_key:
                invoice = jsonpath.jsonpath(res, '$.body')
                # print(address)
                for k in invoice[0]:
                    if k['status'] == 1:
                        return k['id'], k['invoiceTitle'], k['taxCode']
            else:
                if invoice_type != 0:
                    print("开始新建发票信息")
                    insert_invoice_url = '{}/web/invoice/insert'.format(center_java_url)
                    insert_invoice_body = None
                    if invoice_type == 2:
                        insert_invoice_body = {"invoiceTitle": "测试发票", "taxCode": "12345678", "invoiceType": invoice_type, "type": plain_type}
                    elif invoice_type == 1:
                        insert_invoice_body = {"invoiceTitle": "深圳华秋电子有限公司", "taxCode": "91440300581577931W", "invoiceType": invoice_type, "type": plain_type,
                                               "taxAddr": "广东省深圳市福田区中康路新一代产业园1栋5楼", "taxBankAccount": "755918494010404", "taxTel": "0755-25324881",
                                               "taxBank": "招商银行深圳分行"
                                               }
                    if type != None:
                        insert_invoice_url = '{}/web/encodeDecode/invoice/insert'.format(center_java_url)
                        insert_invoice_body_encrypt = orderSensitiveMsgEncrypt(data=insert_invoice_body).encrypt()
                        insert_invoice_body = {"encodeParam": insert_invoice_body_encrypt}
                    res = rss.post(url=insert_invoice_url, json=insert_invoice_body, headers=headers).json()
                    print(res)
                    i += 1
                    if i > 1:
                        break
def get_address(rss):
    """获取用户中心收货地址"""
    url = '{}/web/index/user/address/list'.format(center_java_url)
    body = {"pageNum": 1, "pageSize": 10}
    token = getattr(Data, 'token')
    phone = getattr(Data, 'phone')
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    while True:
        i = 0
        res = rss.post(url=url, json=body, headers=headers).json()
        # print(res)
        # print(res)
        add_num = jsonpath.jsonpath(res, '$..totalSize')
        # print(add_num)
        if int(add_num[0]) > 0:
            address = jsonpath.jsonpath(res, '$.body')
            # print(address)
            for k in address[0]:
                if k['isDefault'] == 1:
                    return k['id']
                elif k['isDefault'] == 0 and int(add_num[0]) == 1:
                    return k['id']

        else:
            insert_address_url = '{}/web/index/user/address/insert'.format(center_java_url)
            insert_address_body = {"consignee": "测试订单", "telMobile": phone, "ssq": [6, 77, 705],
                                   "addr": "新一代产业园1栋5楼", "position": "测试工程师", "tag": "测试订单", "province": 6, "city": 77,
                                   "district": 705}
            if type != None:
                insert_address_url = '{}/web/encodeDecode/index/user/address/insert'.format(center_java_url)
                insert_address_body_encrypt = orderSensitiveMsgEncrypt(data=insert_address_body).encrypt()
                insert_address_body = {"encodeParam": insert_address_body_encrypt}
            rss.post(url=insert_address_url, json=insert_address_body, headers=headers)

            i += 1
            if i > 1:
                break
def get_address_detail(rss, address_id=None, type=None):
    """获取指定收货地址id的详情"""
    if address_id !=None:
        url = '{}/web/index/user/address/detail'.format(center_java_url)
        body = {"id": address_id}
        if type != None:
            url = '{}/web/encodeDecode/index/user/address/detail'.format(center_java_url)
            bodyStr = orderSensitiveMsgEncrypt(data=body).encrypt()
            body = {"encodeParam": bodyStr}
        token = getattr(Data, 'token')
        phone = getattr(Data, 'phone')
        headers = {'Content-Type': 'application/json', 'Authorization': token}
        res = rss.post(url=url, json=body, headers=headers).json()
        if type != None:
            # print(res)
            res = orderSensitiveMsgEncrypt(auto_data=res).auto_dencrypt()
        if "body" in res:
            body_data = res['body']
            # print(body_data)
            if body_data.get('isDefault') == 1:
                # 默认地址
                print("指定地址id的收货人为：{}，省份id为：{}，城市1d为：{}，区/县ID为：{}，收货电话为：{}，收货地址街道楼栋信息为：{}".format(
                    body_data.get('consignee'), body_data.get('province'), body_data.get('city'),
                    body_data.get('district'), body_data.get("telMobile"),body_data.get('addr')))
                return (body_data.get('consignee'), body_data.get('province'), body_data.get('city'),
                        body_data.get('district'), body_data.get("telMobile"),body_data.get('addr'))
            elif body_data.get('isDefault') == 0:
                    # 非默认地址
                print(
                    "指定地址id的收货人为：{}，省份id为：{}，城市1d为：{}，区/县ID为：{}，收货电话为：{}，收货地址街道楼栋信息为：{}".format(
                        body_data.get('consignee'), body_data.get('province'), body_data.get('city'),
                        body_data.get('district'), body_data.get("telMobile"), body_data.get('addr')))
                return (body_data.get('consignee'), body_data.get('province'), body_data.get('city'),
                        body_data.get('district'), body_data.get("telMobile"),body_data.get('addr'))

    else:
        pass

def get_man(rss, type=None):
    """下单人信息获取"""
    url = '{}/web/order/man/query/page?pageNum=1&pageSize=10'.format(center_java_url)
    token = getattr(Data, 'token')
    phone = getattr(Data, 'phone')
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    if type != None:
        url = '{}/web/encodeDecode/order/man/query/page?pageNum=1&pageSize=10'.format(center_java_url)
    while True:
        i = 0
        res = rss.get(url=url, headers=headers).json()
        if type != None:
            res = orderSensitiveMsgEncrypt(dencrypt_data=res).auto_dencrypt()
        # print(res)
        add_num = jsonpath.jsonpath(res, '$..totalSize')
        # print(add_num)
        if int(add_num[0]) > 0:
            man = jsonpath.jsonpath(res, '$.body')
            for k in man[0]:
                if k['isDefault'] == 1:
                    print("默认的下单人信息为：下单人信息id：{}，下单人姓名：{}，下单人电话：{}".format( k['id'], k['orderMan'], k['orderTel']))
                    return k['id'], k['orderMan'], k['orderTel']
        else:
            insert_address_url = '{}/web/order/man/insert'.format(center_java_url)
            username, phone, uid, pcbuid = user_information(rss)
            insert_address_body = {"orderMan": username, "orderTel": phone}
            rss.post(url=insert_address_url, json=insert_address_body, headers=headers)
            i += 1
            if i > 1:
                break
def get_engineer(rss, type=None):
    """工程师信息获取"""
    url = '{}/web/engineer/getListByHqId'.format(center_java_url)
    token = getattr(Data, 'token')
    phone = getattr(Data, 'phone')
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    if type != None:
        url = '{}/web/encodeDecode/engineer/getListByHqId'.format(center_java_url)
    while True:
        res = rss.get(url=url, headers=headers).json()
        print(res)
        if type != None:
            res = orderSensitiveMsgEncrypt(dencrypt_data=res).auto_dencrypt()
        print(res)
        man = jsonpath.jsonpath(res, '$.body')

        for k in man[0]:
            if k['isDef'] == 1:
                print("默认的工程师信息为：工程师信息id：{}，工程师姓名：{}，工程师电话：{}，工程师邮箱：{}".format( k['id'], k['name'], k['tel'], k['email']))
                return k['id'], k['name'], k['tel'], k['email']



def set_defaults_address(rss, address_id, rec_id):
    """
    设置为默认地址，订单提交页面设置
    :param rss: res请求对象
    :param address_id: 收货地址id
    :param rec_id: 提交到订单确认页，返回的一个参数 从订单确认页返回接口获取
    :return:
    """
    set_defaults_url = '{}/ajax/saveshipping'.format(HQCHIP_URL)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    set_defaults_data = {'shipping_type':1, 'shipping_group[0][]':'spot', 'version':2, 'shipping_id':1, 'address_id': address_id, 'bom_id':0, 'ap':'', 'source_type':3, 'rec_id':rec_id, 'stock_id':0, 'goods_type':1}
    rss.post(url=set_defaults_url, data=set_defaults_data, headers=headers)
def get_ic_userId(rss):
    """获取芯城的user_id"""
    token = getattr(Data, 'token')
    headers = {"Authorization": token,
                    "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                    }
    get_ic_userId_url = "{}/ajax/getcustomerinfo.html?v=pc".format(HQCHIP_URL)
    res = rss.get(url=get_ic_userId_url, headers=headers).json()
    status = jsonpath.jsonpath(res, '$.status')
    if status[0] == 'successed':
        loing_data = jsonpath.jsonpath(res, '$..login')
        for k in loing_data:
            if k['pushcrm'] == True:
                return k['user_id']


def pay_password(rss, new_pay_pass_word):
    """修改支付密码"""
    token = getattr(Data, 'token', "a71893fa-ee24-5703-b2ff-d978795998f8-68fee319")
    uid = getattr(Data, 'uid', "6061319")
    phone = getattr(Data, 'phone', "17512054898")
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    # headers = {"Content-Type": "application/json", "Authorization": token}
    center_user_info_url = "{}/index/user/profile/info".format(center_php_url)
    center_user_info_res = rss.get(url=center_user_info_url, headers=headers).json()
    assets_mobile_token =center_user_info_res["result"]["assets_mobile_token"]
    send_code_url = "{}/assets/api/service/account/sendAuthCode".format(Assets_Center_url)
    send_code_body = {"appid":90169, "assetsMobileToken": assets_mobile_token,"scene":"login",
                      "sessionId":"test","sig":"test","token":"test", "type": 1, "value": phone}
    send_code_res = rss.post(url=send_code_url,json=send_code_body,headers=headers).json()
    obtain_code_url = "{}/assets/account/getCodeByUserId?userId={}".format(Assets_Center_url, uid)
    send_code_res = rss.get(url=obtain_code_url).json()
    code =send_code_res["result"]
    current_GMT = time.gmtime()
    time_stamp = calendar.timegm(current_GMT)

    pay_passowrd_update_url1 = "{}/assets/api/service/account/verificationCode".format(Assets_Center_url)
    pay_passowrd_update_body1 = {"appid":90169,"code":code,"timestamp":time_stamp}
    pay_passowrd_update_res1 = rss.post(url=pay_passowrd_update_url1, json=pay_passowrd_update_body1, headers=headers).json()
    verifyCodeToken = pay_passowrd_update_res1["result"]["verifyCodeToken"]
    pay_passowrd_update_url2 = "{}/assets/api/service/account/resetPassword".format(Assets_Center_url)
    pay_passowrd_update_body2 = {"appid":90169,"timestamp":time_stamp, "verifyCodeToken":verifyCodeToken,"new_password":new_pay_pass_word,"password":new_pay_pass_word}
    pay_passowrd_update_res = rss.post(url=pay_passowrd_update_url2, json=pay_passowrd_update_body2, headers=headers).json()
    print(pay_passowrd_update_res)
def login_code_obtain(phone):
    # 获取手机号码验证码
    rss = requests.session()
    obtain_code_url = "{}/lookcode".format(passport_url)
    obtain_code_res = rss.get(url=obtain_code_url).text
    # print(obtain_code_res)
    # print(re.split(phone + '：', obtain_code_res))
    code = re.split(phone + '：', obtain_code_res)[1].split("<br>")[0]
    print(f"获取到code：{code}")
    return code
def pay_code_obtain(uid):
    # 获取支付密码验证码
    rss = requests.session()
    obtain_code_url = "{}/assets/account/getCodeByUserId?userId={}".format(Assets_Center_url, uid)
    send_code_res = rss.get(url=obtain_code_url).json()
    code =send_code_res["result"]
    print(f"获取到code：{code}")
    return code

def login_password_update(rss, new_password, old_password=None):
    """修改登录密码"""
    token = getattr(Data, 'token')
    phone = getattr(Data, 'phone')
    headers = {"Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Mozilla/5.0 (iPhone;CPU iPhone OS 13 2 3like Mac OS X) AppleWebKit/605.1.15(KHTML like Gecko) Version/13.03 Mobile/15E148 Safari/604.1",
                    "Authorization": token
               }
    if old_password == None or old_password == '0':
        if old_password == None:
            print('无历史密码')
        elif old_password == '0':
            print('忘记历史密码')
        # 发送验证码
        send_code_url = "{}/register/regsms".format(passport_url)
        send_code_body = {"account": phone, "areacode": "0086"}
        # print(send_code_body)
        send_code_res = rss.post(url=send_code_url, data=send_code_body, headers=headers).json()
        # print(send_code_res)

        # 获取手机号码验证码
        obtain_code_url = "{}/lookcode".format(passport_url)
        obtain_code_res = rss.get(url=obtain_code_url).text
        # print(obtain_code_res)
        # print(re.split(phone + '：', obtain_code_res))
        code = re.split(phone + '：', obtain_code_res)[1].split("<br>")[0]
        print(f"获取到code：{code}")

        # 验证验证码是否有效
        verification_url = "{}/password/modifyPasswordPreVerifyByPhone".format(passport_url)
        verification_body = {"phone": phone, "code": code, "siteid": 12, "areacode":"0086"}
        verification_res = rss.post(url=verification_url, data=verification_body, headers=headers).json()
        # print(verification_res)
        verification_token = verification_res["data"]["token"]
        verification_uid = verification_res["data"]["uid"]
        print(f"获取到verification_token：{verification_token}，verification_uid：{verification_uid}")

        # 设置密码
        login_password_update_headers = {"Content-Type": "application/json", "Authorization": token}
        login_password_update_url = "{}/password/resetPassword".format(passport_url)
        login_password_update_body = {"password": new_password, "uid": verification_uid, "token":verification_token}
        # print(login_password_update_body)
        login_password_update_res = rss.post(url=login_password_update_url, json=login_password_update_body, headers=login_password_update_headers).json()
        # print(login_password_update_res)
        uid = login_password_update_res["data"]["uid"]
        print(uid)
    else:
        print('知晓历史密码')
        login_password_update_headers = {"Content-Type": "application/json", "Authorization": token}
        login_password_update_url = "{}/password/changepwd".format(passport_url)
        login_password_update_body = {"password": new_password, "newpassword": new_password, "oldpassword": old_password, "siteid": 12}
        login_password_update_res = rss.post(url=login_password_update_url, json=login_password_update_body,
                                             headers=login_password_update_headers).json()
        # print(login_password_update_res)
        uid = login_password_update_res["data"]["uid"]
        print(uid)
    return uid
def enterprise_certification_code(phone):
    """企业认证验证码"""
    rss = requests.session()
    enterprise_certification_code_url = "{}/web/common/querySendAuthCode".format(center_java_url)
    res = rss.get(url=enterprise_certification_code_url).json()
    # print(res)
    bodyInfo = res["body"]
    mobile = []
    code = []
    for i in range(len(bodyInfo)):
        mobile.append(json.loads(bodyInfo[i])["mobile"])
        code.append(json.loads(bodyInfo[i])["code"])
    for m in range(len(mobile)):
        # print(mobile[m])
        if mobile[m] == phone:
            code = code[m]
    # print(code)
    return code
def logout_code_obtain(phone):
    # 获取用户注销验证码
    rss = requests.session()
    obtain_code_url = "{}/web/common/querySendAuthCode".format(center_java_url)
    send_code_res = rss.get(url=obtain_code_url).json()
    print(send_code_res)
    if not send_code_res.get("suc") or "body" not in send_code_res:
        return {}

    latest_records = {}

    for item in send_code_res["body"]:
        try:
            record = json.loads(item)
        except json.JSONDecodeError:
            continue

        mobile = record.get("mobile")
        code = record.get("code")
        las_time_str = record.get("lastTime")

        if not all([mobile, code, las_time_str]):
            continue

        # 直接比较时间字符串（ISO格式字符串可直接比较）
        if mobile not in latest_records or las_time_str > latest_records[mobile]["las_time"]:
            latest_records[mobile] = {
                "code": code,
                "las_time": las_time_str
            }

    # 返回手机号到最新验证码的映射
    result = {mobile: info["code"] for mobile, info in latest_records.items()}
    logout_code = None
    if result != {}:
        for k, v in result.items():
            if k == str(phone):
                logout_code = v
    return logout_code


def user_information(rss, type=None):
    """获取用户中心的用户名和手机号码"""
    token = getattr(Data, 'token')
    headers = {'Content-Type': 'application/json;charset=UTF-8',
               'Authorization': token,
               "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
               }
    url = "{}/web/index/user/profile/info".format(center_java_url)
    if type != None:
        url = '{}/web/encodeDecode/index/user/profile/info'.format(center_java_url)
    res = rss.get(url=url, headers=headers).json()
    if type != None:
        res = orderSensitiveMsgEncrypt(dencrypt_data=res).auto_dencrypt()
    print(res)
    username = res["body"]["username"]
    phone = res["body"]["phone"]
    uid = res["body"]["uid"]
    pcbuid = res["body"]["pcbuid"]
    return username, phone, uid, pcbuid
def get_ic_order_pay(rss, order_sn):
    """订单推送到支付后台"""
    token = getattr(Data, 'token')
    headers = {"Content-Type": "application/json, text/javascript, */*; q=0.01",
               'Authorization': token,
               "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
               }
    get_ic_order_url = "{}/hqapi/usericorder/getlistinfoV2?page=1&orderReferer=&order_keyword={}&order_goods_keyword=&otime=0&ostatus=&statusList[]=".format(HQCHIP_URL, order_sn)
    get_ic_order_res = rss.get(url=get_ic_order_url, headers=headers).json()
    order_id = get_ic_order_res["result"]["order_list"][0]["order_id"]
    get_ic_order_detaill_url = "{}/hqapi/usericorder/getICOrderDetail?order_id={}".format(HQCHIP_URL, order_id)
    rss.get(url=get_ic_order_detaill_url, headers=headers).json()
    # 进入收银台
    verify_icoder_pay_url = "{}/hqapi/usericorder/verifyIcOrderPay".format(HQCHIP_URL)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    verify_icoder_pay_body = {"order_id": order_id}
    rss.post(url=verify_icoder_pay_url, data=verify_icoder_pay_body, headers=headers).json()
    user_icoder_pay_url = "{}/hqapi/usericorder/pay.html".format(HQCHIP_URL)
    user_icoder_pay_body = {"o": order_id}
    user_icoder_pay_res = rss.post(url=user_icoder_pay_url, data=user_icoder_pay_body, headers=headers).json()
    return user_icoder_pay_res



if __name__ == '__main__':
    from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
    rss = SSO_Reception('https://uat-www.hqchip.com').login()
    # pay_password(rss, '123456')
    # address_id = get_address(rss)
    # print(address_id)
    # get_address_detail(rss, address_id)
    # invoice_id = get_invoice(rss, 2, 1,)
    # print(invoice_id)
    # get_address_detail(rss, address_id)
    # id, orderMan, orderTel = get_man(rss, 1)
    # get_engineer(rss, 1)
    username, phone, uid, pcbuid = user_information(rss, "NEW")
    # print(address_id)
    # print(id, orderMan, orderTel)
    # print(username)
    # login_code_obtain("15912757721")
    # get_ic_order_pay(rss=rss, order_sn="S2026070779876")