
import hashlib
import json
import re
import sys
import time
from datetime import datetime

import jsonpath
import requests
import yaml
from faker import Faker

from huaqiu_order_api.HQCHIP.Commonly_kit_tool.php_antisequence import PhpAntisequence
from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.Openapi_signature.signature import SignAture
from huaqiu_order_api.HQCHIP_Center.user_center import get_invoice, get_address, get_address_detail
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml


class CreateOrder:
    # 开放接口创建订单

    def __init__(self, env_type=None):

        self.openapi_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.form_head = {'User-Agent': 'HQCHIP OpenAPI Python-SDK/1.0', "X-Request-Version": '1.0'}
        self.out_order_no = "AutoTest" + datetime.now().strftime("%Y%m%d") + "000" + str(Faker("zh_CN").random_int(1, 10000))
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.app_key = data['APP_KEY']
        self.app_sec = data['APP_SEC']
        self.url = data['OPENAPI_UAT_URL']
        self.env_type = env_type
        if self.env_type == "pro":
            self.url = data['OPENAPI_PRO_URL']
        self.GoodsName = data['APIGoodsName']
        self.GoodsType = data['APIGoodsType']
        self.phone = data['APIPhone']
        self.remark = data['APIOderRemark']
        # self.product_num = data['APIProductNum']
        self.partial_order_alloweb = data['APIPartialOrderAlloweb']
        self.center_java_url = data['center_java_url']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.phone = account["PassPort"]["phone"]
        self.goods_id =account["HQCHIP_GOODS"]["goods_id"]
        self.numder = account["HQCHIP_GOODS"]["number"]
        self.vat_type = account["HQCHIP_GOODS"]["vat_type"]
        # self.vat_sub_type = account["HQCHIP_GOODS"]["vat_sub_type"]
        # self.GoodsName = "RC0603JR-074K7L"
        # self.goods_id = '2500368506'
    def openapi_goods_list(self, goods_name):
        """型号搜索"""
        openapi_goods_list_url = '{}/goods/list/'.format(self.url)
        print(openapi_goods_list_url)
        openapi_goods_list_body = {"app_key": self.app_key, "keyword": goods_name}
        print(openapi_goods_list_body)
        openapi_goods_list_res = self.openapi_rss.get(url=openapi_goods_list_url, params=openapi_goods_list_body,
                                                      headers=self.form_head).json()
        logger.info(openapi_goods_list_res)
        return openapi_goods_list_res
    def openapi_goods_detail(self, goods_id):
        openapi_goods_detail_url = '{}/goods/detail/?app_key={}&goods_id={}'.format(self.url, self.app_key, goods_id)
        openapi_goods_detail_res = self.openapi_rss.get(url=openapi_goods_detail_url, headers=self.json_head).json()
        logger.info(openapi_goods_detail_res)
        return openapi_goods_detail_res
    def openapi_search_invoice(self):
        invoice_type = None
        print(self.vat_type)
        if self.vat_type == '0':
            invoice_type = 2
        elif self.vat_type == '2':
            invoice_type = 1
        elif self.vat_type == '1':
            invoice_type = 2
        elif self.vat_type == '3':
            invoice_type = 4
        logger.info(f"对接用户中心的invoice_type：{invoice_type}")
        # sys.exit()
        sso_Rec_url = 'https://uat-www.hqchip.com'
        if 'uat' in sso_Rec_url:
           pass
        else:
           pass_port_user_msg = {"phone": '13632845795', "name": 'qaulau@qq.com', "pwd": 'a123456'}
           user_msg = {'PassPort': pass_port_user_msg}
           write_yaml(account_yaml, user_msg)
           sso_Rec_url = 'https://www.hqchip.com'
        self.openapi_rss = SSO_Reception(sso_Rec_url).login()
        token = getattr(Data, "token")
        self.json_head["Authorization"] = token
        invoice_id = get_invoice(self.openapi_rss, invoice_type, 1)
        url = "{}/web/invoice/query/one?id={}".format(self.center_java_url, invoice_id)
        res = self.openapi_rss.get(url=url, headers=self.json_head).json()
        # logger.info(res)

        return self.openapi_rss, res["body"]
    def openapi_search_address(self, rss):
        address_id = get_address(rss)
        consignee, province, city, district, telMobile, address = get_address_detail(rss, address_id)
        return consignee, province, city, district, telMobile, address

    def openapi_make(self):
        """订单创建"""
        openapi_make_url = '{}/order/make/'.format(self.url)
        self.timestamp = int(time.time())
        params = {'app_key': self.app_key, 'timestamp': self.timestamp}
        #是利用列表推导式 生成一个商品列表 goods_list，每个商品名称的详细信息由 openapi_goods_detail 方法获取
        if self.goods_id != "":
            if re.compile(r'[@_!#$%^&*()<>?/\|}{~:，。、,]').search(self.goods_id) is None:
                goods_list = [{"out_goods_name": self.openapi_goods_detail(self.goods_id).get('data', {}).get('goods_name', None),
                               "out_remark": self.openapi_goods_detail(self.goods_id).get('data', {}).get('desc', None),
                               "qty": self.numder, "goods_id": self.goods_id}]
                if self.GoodsName != "":
                    goods_list[0]["out_goods_name"] = self.GoodsName
                if goods_list[0]["out_remark"] == None:
                    if self.remark != "":
                        goods_list[0]["out_remark"] = self.remark
                    else:
                        goods_list[0]["out_remark"] = "自动化测试"
            else:
                goods_id = self.goods_id.split(",")
                goods_list = [{"out_goods_name": self.openapi_goods_detail(i).get('data', {}).get('goods_name', None),
                               "qty": self.numder, "goods_id": i} for i in goods_id]
                print(goods_list)
                for m in range(len(goods_list)):
                    if "out_remark" not in goods_list[m] or goods_list[m]["out_remark"] is None:
                        if self.remark != "":
                            goods_list[m]["out_remark"] = self.remark
                        else:
                            goods_list[m]["out_remark"] = "自动化测试"
        else:
            if re.compile(r'[@_!#$%^&*()<>?/\|}{~:，。、,]').search(self.GoodsName) is None:
                openapi_goods_list_res = self.openapi_goods_list(self.GoodsName)
                if openapi_goods_list_res['data']['data'] != []:
                    goods_name = jsonpath.jsonpath(openapi_goods_list_res, '$..ModelName')
                    goods_id = jsonpath.jsonpath(openapi_goods_list_res, '$..GoodsId')
                    desc = jsonpath.jsonpath(openapi_goods_list_res, '$..Desc')
                    goods_id_list = []
                    desc_list = []
                    for i in range(len(goods_name)):
                        if goods_name[i] == self.GoodsName:
                            self.goods_id = goods_id[i]
                            self.desc = desc[i]
                            goods_id_list.append(goods_id[i])
                            desc_list.append(desc[i])
                    goods_list = []
                    for a in range(len(goods_id_list)):
                            goods_list.append({"out_goods_name": self.GoodsName, "out_remark": desc_list[a], "qty": self.numder, "goods_id": goods_id_list[a]})
                else:
                    goods_list = [{"out_goods_name": self.GoodsName, "out_remark": '自动化测试', "qty": self.numder, "goods_id": ''}]
            else:
                goods_list = []
                goods_name_list = self.GoodsName.split(",")
                for n in range(len(goods_name_list)):
                    openapi_goods_list_res = self.openapi_goods_list(goods_name_list[n])
                    if openapi_goods_list_res['data']['data'] != []:
                        goods_name = jsonpath.jsonpath(openapi_goods_list_res, '$..ModelName')
                        goods_id = jsonpath.jsonpath(openapi_goods_list_res, '$..GoodsId')
                        desc = jsonpath.jsonpath(openapi_goods_list_res, '$..Desc')
                        goods_id_list = []
                        desc_list = []
                        for b in range(len(goods_name)):
                            if goods_name[b] == goods_name_list[n]:
                                self.goods_id = goods_id[b]
                                self.desc = desc[b]
                                goods_id_list.append(goods_id[b])
                                desc_list.append(desc[b])
                        for c in range(len(goods_id_list)):
                            goods_list.append(
                                {"out_goods_name": goods_name_list[n], "out_remark": desc_list[c], "qty": self.numder,
                                 "goods_id": goods_id_list[c]})
                    else:
                        goods_list.append({"out_goods_name": goods_name_list[n], "out_remark": '自动化测试', "qty": self.numder, "goods_id": ''})
        invoice = {"type": self.vat_type, "inv_title": "刘权"}
        receive = {'consignee': '刘权', 'province': 6, 'city': 77, 'district': 705, 'tel': '075512345678',
                   'address': '深圳市福田区梅林街道梅秀璐1号','mobile': self.phone}
        if self.env_type != "pro":
            print("预发布环境允许走")
            rss, invoice_body = self.openapi_search_invoice()
            print('1111:{}'.format(invoice_body))
            # invoice_body = {
            #     "type": 1,
            #     "inv_title": "刘权",
            # }
            for k in invoice_body:
                if k in ("invoiceRegistration", "busiLicence", "fileName"):
                    # 增值税发票用这个会报错，因为图片信息开放接口还是获取的是商城的，需要进行域名+服务器数据验证
                    # invoice_body[k] = 'http://uat-www.hqchip.com/uploads/invoice/2015/90/90d33d0935ccd1396b8fcac21650a297.png'
                    invoice_body[k] = 'http://www.hqchip.com/uploads/invoice/2015/90/90d33d0935ccd1396b8fcac21650a297.png'
                if invoice_body[k] == '':
                    if k in ['taxTel', 'taxBankAccount', 'taxBank']:
                        if k == 'taxTel':
                            invoice_body[k] = '15070912351'
                        if k == 'taxBankAccount':
                            invoice_body[k] = '755918494010404'
                        if k == 'taxBank':
                            invoice_body[k] = '招商银行深圳梅林支行'
                    else:
                        invoice_body[k] = 'akflaspjjlwsir1'
            print("1;;;：{}".format(invoice_body))
            if self.vat_type == "2" or self.vat_type == "3":
                print(111)
                invoice["vat_company"] = invoice_body["invoiceTitle"]
                invoice["vat_registration"] = invoice_body["invoiceRegistration"]
                invoice["vat_address"] = invoice_body["taxAddr"]
                invoice["vat_tel"] = invoice_body["taxTel"]
                invoice["vat_bank"] = invoice_body["taxBank"]
                invoice["vat_bank_sn"] = invoice_body["taxBankAccount"]
                invoice["vat_code"] = invoice_body["taxCode"]
                invoice["busi_licence"] = invoice_body["busiLicence"]
                invoice["file_name"] = invoice_body["fileName"]
            logger.info(invoice)
            consignee, province, city, district, telMobile, address   = self.openapi_search_address(rss)
            if consignee != None:
                receive["consignee"] = consignee
                receive["province"] = province
                receive["city"] = city
                receive["district"] = district
                receive["mobile"] = telMobile
                receive["address"] = address
        data = {
            'goods_list': json.dumps(goods_list),
            'invoice': json.dumps(invoice),
            'receive': json.dumps(receive),
            'shipping_type': 1,
            'goods_type': int(self.GoodsType),  # goods_type  1为内地订单  2为香港订单
            'out_order_no': self.out_order_no,
            'product_num': '1',  # 套数 2024-10-15修改
            "order_tracking_number": self.out_order_no,  # 订单跟踪号
            "remark": "自动化测试",  # 订单备注 2024-06-21增加
            "partial_order_alloweb": self.partial_order_alloweb  # 订单备注 2024-08-21增加
        }
        if self.remark != '':
            data["remark"] = self.remark
        logger.info(data)
        # 单独的生成签名
        # sys_params = params.copy()
        # sys_params.update(data)
        # params['sign'] = self.gen_sign(self.app_sec, sys_params)

        # 统一封装 签名sign生成方法
        logger.info("params: {}".format(params))
        sgin = SignAture(self.app_sec).hqchip_sign_main(params, data)
        params['sign'] = sgin
        openapi_make_res = self.openapi_rss.post(url=openapi_make_url, params=params, data=data, headers=self.form_head,timeout=10).json()
        logger.info(openapi_make_res)
        error_message = openapi_make_res['error_message']
        logger.info(error_message)
        order_sn = None
        order_id = None
        failed_goods_list = []
        goods_list_new = []
        if error_message == '':
            order_sn = openapi_make_res["data"]["order_sn"]
            order_id = openapi_make_res["data"]["order_id"]
            failed_goods_list = openapi_make_res.get("data", {}).get("failed_goods_list", [])
            goods_list = openapi_make_res["data"]["goods_list"]
            for i in range(len(goods_list)):
                goods_list[i]["delivery_msg"] = PhpAntisequence(goods_list[i]["delivery_msg"]).php_Antisequence()
            openapi_make_res["data"]["goods_list"] = goods_list
            goods_list_new = openapi_make_res["data"]["goods_list"]
            logger.info(f"订单生成成功，订单号为{order_sn},订单id：{order_id}")
            logger.debug('=*' * 50)
            return error_message, order_sn, order_id, self.out_order_no, sgin, failed_goods_list, goods_list_new
        else:
            logger.info('错误信息：'f"{error_message}")
            failed_goods_list = openapi_make_res.get("data", {}).get("failed_goods_list", [])
            return error_message, order_sn, order_id, self.out_order_no, sgin, failed_goods_list, goods_list_new



if __name__ == '__main__':
    # url = "http://debugapi.hqchip.com"
    # app_key = "c11ff533617d2aa45ffd0e1994fb2cd7"
    # app_sec = "7b0594651ce4ab534b3f941e5dc9fe63"
    CreateOrder().openapi_make()
    # goods_name = 'discount20240129'
    # CreateOrder().openapi_goods_list(goods_name)