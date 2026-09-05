import json
import re
import jsonpath
import yaml
import urllib.parse


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.HQCHIP_Center.user_center import get_address, get_invoice
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml

from huaqiu_order_api.SSO_Reception.orderSensitiveMsgEncrypt import orderSensitiveMsgEncrypt
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception


class IcOrder:
    def __init__(self, rss):
        """
        :param phone:  登录账号
        :param psw:  登录密码
        :param goods_id:  购买的产品id
        :param numder 下单数量
        :param warehouse_id 下单仓库
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_PC_ITEM_URL = data['HQCHIP_PC_ITEM_URL']
        self.HQCHIP_URL = data['HQCHIP_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.goods_id =account["HQCHIP_GOODS"]["goods_id"]
        self.numder = account["HQCHIP_GOODS"]["number"]
        self.vat_type = account["HQCHIP_GOODS"]["vat_type"]
        self.vat_sub_type = account["HQCHIP_GOODS"]["vat_sub_type"]
        self.warehouse_id = int(account["HQCHIP_GOODS"]["warehouse_id"])
        self.shipping_method = account["HQCHIP_GOODS"]["shipping_method"] if "HQCHIP_GOODS" in account and "shipping_method" in account["HQCHIP_GOODS"] else "0"  # 是否为贴片
        self.relation_smt_order_sn = account["HQCHIP_GOODS"]["relation_smt_order_sn"] if "HQCHIP_GOODS" in account and "shipping_method" in account["HQCHIP_GOODS"] else ""  # SMT订单号
        if self.shipping_method == '':
            self.shipping_method = '1'

        # self.url = 'https://uat-passport.elecfans.com/login/dologin.html'
        # self.body = {'siteid': 12, 'account': self.phone, 'password': "a123456"}
        token = getattr(Data, 'token')
        print(token)
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "Authorization": token,
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {
                             "Content-Type": "application/json;charset=UTF-8",
                             "Authorization": token,
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.rss = rss

    def goods_search(self):
        # goods_search_headers = {"Content-Type": "application/json"}
        goods_search_url = "{}/api/v3/product/detail".format(self.HQCHIP_PC_ITEM_URL)
        goods_search_body = {"stockId": self.goods_id}
        print(goods_search_body)
        goods_search_res = self.rss.post(url=goods_search_url, data=json.dumps(goods_search_body),headers=self.headers_json).json()
        logger.info(goods_search_res)
        # address_id = pay_password(self.rss, self.phone)
        # print(address_id)

    def add_cart(self):
        self.tab = urllib.parse.quote("搜索结果页")
        # self.cart_url = "{}/cart?".format(self.HQCHIP_URL)
        # url = self.cart_url + f'v=pc&step=add_to_cart&goods_id={self.goods_id}&warehouse_item[0][goods_number]={self.numder}&warehouse_item[0][warehouse_id]={self.warehouse_id}&goods_type=1&cart_from={tab}&from_channel=search&source_type= '
        # url = "{}/cart?v=pc&step=add_to_cart&goods_id={}&warehouse_item[0][goods_number]={}&warehouse_item[0][warehouse_id]={}&goods_type=1&cart_from={}&from_channel=search&source_type= ".format(
        #     self.HQCHIP_URL, self.goods_id, self.numder, self.warehouse_id, tab)
        url = "{}/cart?v=pc&step=add_to_cart&goods_id={}&goods_number={}&goods_type=1&cart_from={}&from_channel=search&source_type=".format(
            self.HQCHIP_URL, self.goods_id, self.numder, self.tab)
        # logger.info(url)
        logger.info(f"准备添加商品: {self.goods_id} 到购物车")
        # res = self.rss.get(url=url, headers=self.headers_json).json()
        add_cart_res = self.rss.get(url=url, headers=self.headers_json).json()
        # data = add_cart_res.content.decode("utf-8")
        # logger.info(data)
        if add_cart_res['error_msg'] == '产品信息正确':
            logger.info(f"商品成功加入购物车")
            return self
        else:
            logger.error(f"商品加购失败,加购接口返回信息：{add_cart_res}")
            error_msg = add_cart_res["error_msg"]
            goods_numder = error_msg.split('不符合')[1].split('最小起订量')[0]
            logger.info(f"型号id：{self.goods_id}最小起订量大于实际购买量：{self.numder}，系统将自动修改为其型号的最小起订量进行加入购物车")
            self.numder = goods_numder
            logger.info(f"此时self.numder为：{self.numder}")
            # url = "{}/cart?v=pc&step=add_to_cart&goods_id={}&warehouse_item[0][goods_number]={}&warehouse_item[0][warehouse_id]={}&goods_type=1&cart_from={}&from_channel=search&source_type= ".format(
            #     self.HQCHIP_URL, self.goods_id, self.numder, self.warehouse_id, tab)
            url = "{}/cart?v=pc&step=add_to_cart&goods_id={}&goods_number={}&goods_type=1&cart_from={}&from_channel=search&source_type=".format(self.HQCHIP_URL, self.goods_id, self.numder, self.tab)
            logger.info(f"准备添加商品: {self.goods_id} 到购物车")
            res_min = self.rss.get(url=url, headers=self.headers_json).json()
            if res_min['error_msg'] == '产品信息正确':
                logger.info(f"商品成功加入购物车")
                return self
            else:
                logger.error(f"商品加购失败,加购接口返回信息：{add_cart_res}")
                raise ValueError
            # raise ValueError



    def place_an_order(self):
        """
        vat_type = 1 增值税发票，对应用户中心 invoice_type=1
        vat_type = 0 普通发票，对应用户中心 invoice_type=2
        vat_type = 3 不开发票，对应用户中心 invoice_type=0
        vat_type = 1 且 vat_sub_type == 1 对应用户中心开票类型：纸质增值税（专用）发票 注：为原来的增值税发票
        vat_type = 1 且 vat_sub_type == 2 对应用户中心开票类型：数电增值税（专用）发票
        vat_type = 0 且 vat_sub_type == 3 对应用户中心开票类型：增值税（普通）电子发票，注：为原来的普通发票
        vat_type = 3 且 vat_sub_type == 0 对应用户中心开票类型：不开发票，注：为原来的不开发票
        """
        # user_information(self.rss)
        logger.info(f"开始检查收货地址")
        address_id = get_address(self.rss)
        logger.info(f"拿到收货地址id: {address_id}")
        logger.info(f"开始检查发票信息")
        invoice_type = None
        if self.vat_type == '1' and self.vat_sub_type == '1':
            logger.info("选择发票类型为纸质增值税（专用）发票")
            invoice_type = 1
        elif self.vat_type == '1' and self.vat_sub_type == '2':
            logger.info("选择发票类型为数电增值税（专用）发票")
            invoice_type = 1
        elif self.vat_type == '0' and self.vat_sub_type == '3':
            logger.info("选择发票类型为增值税（普通）电子发票")
            invoice_type = 2
        elif self.vat_type == '3' and self.vat_sub_type == '0':
            logger.info("选择发票类型为不开发票")
            invoice_type = 0
        logger.info(f"对接用户中心的invoice_type：{invoice_type}")
        invoice_id = get_invoice(self.rss, invoice_type, 1)
        if invoice_id == None:
            invoice_id = 0
        logger.info(f"拿到发票id: {invoice_id}")
        url = "{}/cart?v=pc&step=add_to_cart&goods_id={}&goods_number={}&goods_type=1&cart_from={}&from_channel=search&source_type=3".format(self.HQCHIP_URL, self.goods_id, self.numder, self.tab)
        res = self.rss.get(url=url, headers=self.headers_json).json()
        logger.info(f"提交商品到订单确认页结果：{res}")
        rec_id_url = jsonpath.jsonpath(res, '$.url')
        rec_id = re.search('[0-9]{6,7}', rec_id_url[0]).group()
        goods_name = jsonpath.jsonpath(res, '$..goods_name')[0]
        goods_price = jsonpath.jsonpath(res, '$..goods_price')[0]
        goods_number = jsonpath.jsonpath(res, '$..goods_number')[0]
        logger.info(f"订单成功提交到确认页，获取到的rec_id: {rec_id}")
        logger.info(f"购买型号为：{goods_name}，其下单数量为{self.numder}，选择发货仓：{self.warehouse_id}")
        bonusList, freightCouponList, VoucherList = self.coupon_voucher_use(address_id, rec_id)
        finish_url = '{}/cart/finish'.format(self.HQCHIP_URL)
        body = {
                    "shipping_id": 1,
                    "address_id": address_id,
                    "vat_type": self.vat_type,
                    "vat_sub_type": self.vat_sub_type,
                    "shipping_type": 1,
                    "goods_type": 1,
                    "bi_id": 0,
                    "bom_id": 0,
                    "match_id": 0,
                    "stock_id": 0,
                    "source_type": 3,
                    "bonus": bonusList,
                    "order_book": 3,
                    "logistics_method": "336301ff10320ebe94594b4ba92a4f3e",
                    "sensors_url": "{}/cart/checkout.html?type=1&rec_id={}&source_type=3".format(self.HQCHIP_URL, rec_id),
                    "freight_coupon": freightCouponList,
                    "shipping_pay_type": 1,
                    "sensors_referrer":  "{}/search/{}.html".format(self.HQCHIP_URL, goods_name),
                    "imExCommitmentCheckbox": "on",
                    "relation_smt_order_sn": "",
                    "change_supp": 1,
                    "shipping_group":  [["supplier_agency"], ["spot"], ["future"]],
                    "rec_id": rec_id,
                    "shipping_code": "336301ff10320ebe94594b4ba92a4f3e",
                    "shipping_method": self.shipping_method,
                    "vatSubType": self.vat_type,
                    "orderVoucher": VoucherList
                }
        if self.vat_type != 3:
            body["tax_id"] = invoice_id
            body["invoice_email"] = ""
        if self.shipping_method != '1':
            if self.relation_smt_order_sn == '':
                logger.info("未选择关联订单，默认为空,选择近三个月订单里面的第一个")
                relation_smt_order_url = "{}/smtorder/getRelatedSmtOrdersList?dateRangeIndex=1&smtOrderSn=&pageSize=10&page=1".format(self.HQCHIP_URL)
                relation_smt_order_res = self.rss.get(url=relation_smt_order_url, headers=self.headers_json).json()
                if relation_smt_order_res['result']["list"] != []:
                    relation_smt_order_sn = jsonpath.jsonpath(relation_smt_order_res, '$..smt_order_sn')[0]
                else:
                    relation_smt_order_sn = ''
                self.relation_smt_order_sn = relation_smt_order_sn
                body["relation_smt_order_sn"] = self.relation_smt_order_sn
            else:
                body["relation_smt_order_sn"] = self.relation_smt_order_sn
        logger.info(f"开始提交订单，生成订单编号 提交的body：{body}")
        bodyEncrypt = orderSensitiveMsgEncrypt(data=body).encrypt()
        bodyNew = {
            "obfuscatedContent": bodyEncrypt
        }
        finish_res = self.rss.post(url=finish_url, data=bodyNew, headers=self.headers).text
        # logger.info(finish_res)
        order_sn = re.search('(<td class="fc-3">)(S[0-9]{13})', finish_res).group(2)
        order_id = re.search('(orderID=")([0-9]*)', finish_res).group(2)
        logger.info(f"订单生成成功，订单编号: {order_sn}, 订单id：{order_id}")
        logger.debug('=*'*50)
        # 将生成的IC订单号往Data里面作虚拟存储以【ic_order_sn】命名以便后续提取
        setattr(Data, 'ic_order_sn', order_sn)
        setattr(Data, 'numder', self.numder)
        setattr(Data, 'ic_order_id', order_id)
        setattr(Data, 'order_json', {"order_sn": order_sn, "order_id": order_id})
        return self
    def coupon_voucher_use(self,address_id, rec_id):
        """现金券和优惠券使用"""
        order_save_url = "{}/ajax/saveshipping".format(self.HQCHIP_URL)
        order_save_body_json = {
            "bonus": [],
            "freight_coupon": [],
            "orderVoucher": [],
            "shipping_type": 1,
            "shipping_gorup": [["supplier_agency"], ["spot"], ["future"]],
            "version": 2,
            "address_id": address_id,
            "bi_id": "0",
            "bom_id": "0",
            "ap": "",
            "shipping_code": "ee148b0fe2c4cdffc3cac04e85eaa301",
            "shipping_pay_type": "1",
            "source_type": "3",
            "rec_id": rec_id,
            "stock_id": "0",
            "goods_type": "1",
            "shhipping_method": "1",
            "relation_smt_order_sn": "",
            "obfuscation": True
        }
        order_save_bodyEncrypt = orderSensitiveMsgEncrypt(data=order_save_body_json).encrypt()
        order_save_body = {
            "obfuscatedContent": order_save_bodyEncrypt
        }
        order_save_res = self.rss.post(url=order_save_url, data=order_save_body, headers=self.headers).json()
        # print(order_save_res)
        if "result" in order_save_res:
            encryptedResult = order_save_res["result"]
            decodeResultJson = orderSensitiveMsgEncrypt(dencrypt_data=encryptedResult).auto_dencrypt()
            order_save_res["result"] = decodeResultJson
        # print(order_save_res)
        usedCouponIds = []
        bonusList = []
        freightCouponList = []
        VoucherList = []
        usedVoucherIds = []
        if order_save_res["result"] != []:
            orderGroup = jsonpath.jsonpath(order_save_res, "$..order_group")[0]
            if isinstance(orderGroup, list):
                for groupName in orderGroup:
                    groupData = order_save_res["result"][groupName]
                    goodsPrice = groupData['goods_price']
                    shippingFee = groupData['shipping_fee']
                    total = groupData['amount_price']
                    logger.info(f"订单组: {groupName}, 商品价格: {goodsPrice}, 运费: {shippingFee}, 总金额: {total}")
                    # 处理优惠券
                    goodsCouponList = None
                    if order_save_res["couponList"] != []:
                        if order_save_res["couponList"][groupName]["goodsCouponList"] != []:
                            goodsCouponList = order_save_res["couponList"][groupName]["goodsCouponList"]
                    if isinstance(goodsCouponList, list):
                        selectedGoods = None
                        for coupon in goodsCouponList:
                            enabled = coupon.get('enabled') == True  # 或者直接 coupon['enabled']
                            min_amount = coupon.get('orderAmountLimit', 0)
                            is_amount_ok = float(goodsPrice) > min_amount
                            userCouponId  = coupon.get('userCouponDsId')
                            if enabled and is_amount_ok and userCouponId  and userCouponId not in usedCouponIds:
                                selectedGoods = coupon
                                break
                        # logger.info(json.dumps(selectedGoods, ensure_ascii=False))
                        if selectedGoods:
                            bonusList.append({
                                "id": selectedGoods['userCouponDsId'],
                                "source": 3,
                                "order_name": groupName
                            })
                            usedCouponIds.append(selectedGoods['userCouponDsId'])
                            logger.info(
                                f"为订单组 {groupName} 分配商品券: 优惠券id={selectedGoods.get('couponId')}, 用户优惠券分布式id={selectedGoods.get('userCouponDsId')}, "
                                f"门槛={selectedGoods.get('orderAmountLimit')}, 优惠券面额={selectedGoods.get('couponPrice')}")
                        else:
                            logger.info(f"订单组 {groupName} 没有可用的未使用商品券")
                    else:
                        logger.info(f"订单组 {groupName} 没有可用的未使用商品券")
                    # 处理运费券
                    goodsFreightCouponList = None
                    if order_save_res["couponList"] != []:
                        if order_save_res["couponList"][groupName]["freightCouponList"] != []:
                            goodsFreightCouponList = order_save_res["couponList"][groupName]["freightCouponList"]
                    if isinstance(goodsFreightCouponList, list):
                        selectedFreight = None
                        for coupon in goodsFreightCouponList:
                            enabled = coupon.get('enabled') == True  # 或者直接 coupon['enabled']
                            min_amount = coupon.get('orderAmountLimit', 0)
                            is_amount_ok = float(shippingFee) > min_amount
                            userCouponId  = coupon.get('userCouponDsId')
                            if enabled and is_amount_ok and userCouponId  and userCouponId not in usedCouponIds:
                                selectedFreight = coupon
                                break
                        # logger.info(json.dumps(selectedGoods, ensure_ascii=False))
                        if selectedFreight:
                            freightCouponList.append({
                                "user_coupon_id": selectedFreight['userCouponDsId'],
                                "order_name": groupName
                            })
                            usedCouponIds.append(selectedFreight['userCouponDsId'])
                            logger.info(
                                f"为订单组 {groupName} 分配运费券: 优惠券id={selectedFreight.get('couponId')}, 用户运费券分布式id={selectedFreight.get('userCouponDsId')}, "
                                f"门槛={selectedFreight.get('orderAmountLimit')}, 运费券面额={selectedFreight.get('couponPrice')}")
                        else:
                            logger.info(f"订单组 {groupName} 没有可用的未使用运费券")
                    else:
                        logger.info(f"订单组 {groupName} 没有可用的未使用运费券")
                    # 处理现金券
                    goodsVoucherList = None
                    if order_save_res["orderVoucher"] != []:
                        goodsVoucherList = order_save_res["orderVoucher"][groupName]["usableList"]
                    if isinstance(goodsVoucherList, list):
                        selectedVoucher = None
                        for voucher in goodsVoucherList:
                            # 获取 balance，若不存在或为 None 则默认为 0
                            balance = voucher.get('balance', 0)
                            # 转换为数值，确保比较正确（可用 Decimal 或 float）
                            try:
                                balance = float(balance)
                            except (TypeError, ValueError):
                                balance = 0.0
                            user_voucher_id = voucher.get('userVoucherId')
                            # 条件：余额 > 0 且 user_voucher_id 存在且未使用
                            if balance > 0 and user_voucher_id and user_voucher_id not in usedVoucherIds:
                                selectedVoucher = voucher
                                break
                        # logger.info(json.dumps(selectedGoods, ensure_ascii=False))
                        if selectedVoucher:
                            VoucherList.append({
                                "userVoucherId": selectedVoucher['userVoucherId'],
                                "orderName": groupName
                            })
                            usedVoucherIds.append(selectedVoucher['userVoucherId'])
                            logger.info(
                                f"为订单组 {groupName} 分配现金券: 用户现金券分布式id={selectedVoucher.get('userVoucherId')}, "
                                f"现金券面额={selectedVoucher.get('faceValue')}, 现金券余额={selectedVoucher.get('balance')}")
                        else:
                            logger.info(f"订单组 {groupName} 没有可用的未使用现金券")
                    else:
                        logger.info(f"订单组 {groupName} 没有可用的未使用现金券")
            order_update_url = "{}/ajax/ajaxordermoney".format(self.HQCHIP_URL)
            order_update_body_json = {
                "bonus": VoucherList,
                "freight_coupon": freightCouponList,
                "orderVoucher": [],
                "shipping_type": 1,
                "shipping_gorup": [["supplier_agency"], ["spot"], ["future"]],
                "version": 2,
                "address_id": address_id,
                "bi_id": "0",
                "bom_id": "0",
                "ap": "",
                "shipping_code": "ee148b0fe2c4cdffc3cac04e85eaa301",
                "shipping_pay_type": "1",
                "source_type": "3",
                "rec_id": rec_id,
                "stock_id": "0",
                "goods_type": "1",
                "shhipping_method": "1",
                "relation_smt_order_sn": "",
                "obfuscation": True
            }
            order_update_bodyEncrypt = orderSensitiveMsgEncrypt(data=order_update_body_json).encrypt()
            order_update_body = {
                "obfuscatedContent": order_update_bodyEncrypt
            }
            order_update_res = self.rss.post(url=order_update_url, data=order_update_body, headers=self.headers).json()
            # print(order_update_res)
        return bonusList, freightCouponList, VoucherList

    def order_point_comparison(self, order_point, activity_create_point_calculate):
        pass


if __name__ == '__main__':
    # from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
    rss = SSO_Reception('https://uat-www.hqchip.com').login()
    IcOrder(rss).add_cart().place_an_order()
