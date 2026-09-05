import jsonpath
import yaml

from huaqiu_order_api.HC2018_admin.work_sheet.work_sheet import WorkSheet
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml
from huaqiu_order_api.HC2018_admin.login.login import Login


class SelfOrderStockUp:
    """ 自营补货 """
    def __init__(self, rss):
        self.rss = rss
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.goods_id = account["HQCHIP_GOODS"]["goods_id"]
        # self.goods_id = 2500327784
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
        self.auth_token = getattr(Data, 'dos_auth_token')
        self.order_sn = getattr(Data, 'ic_order_sn')
        # self.order_sn = "S2023112785449"
        self.headers_json["Authorization"] = self.auth_token
        self.user_pwd_json = {"yemao": "12345678", "taoting": "12345678", "admin": "HQ@uat@666"}
    def stock_pricing(self, goods_name=None, provider_name=None):
        """库存定价"""
        if self.goods_id != "":
            stock_pricing_goods_url = "{}/v1/pricing/StockPricing/getStockList".format(self.HC2018_ADMIN_URL)
            stock_pricing_goods_body = {"goods_id": self.goods_id, "erp_type": -1, "hasGuidePrice": "0", "is_on_sale": "0",
                                    "order_sort": 1, "stair_id": -1, "tag_type": -1, "page": 1, "per_page": 100}
            stock_pricing_goods_res = self.rss.post(url=stock_pricing_goods_url, json=stock_pricing_goods_body,
                                                    headers=self.headers_json).json()
            # logger.info(stock_pricing_goods_res)
            self.provider_name = jsonpath.jsonpath(stock_pricing_goods_res, '$..provider_name')[0]
            self.goods_name = jsonpath.jsonpath(stock_pricing_goods_res, '$..goods_name')[0]
        # else:
        #     if goods_name != None or provider_name != None:
        #         if goods_name != None:
        #             goods_msg_url = "{}/v1/pricing/StockPricing/retrieveStockParam".format(self.HC2018_ADMIN_URL)



        logger.info(f"库存id：{self.goods_id}的型号名为：{self.goods_name}，品牌名为：{self.provider_name}")
        return self

    def stockup_list(self):
        """补备货列表"""
        search_url = "{}/v1/stockup/NewStockUp/findList".format(self.HC2018_ADMIN_URL)
        self.search_body = {"goods_name": self.goods_name, "provider_name": self.provider_name, "order_sn":  self.order_sn, "stock_type": "3", "stock_status": ""}
        search_res = self.rss.post(url=search_url, json=self.search_body,
                                                headers=self.headers_json).json()
        self.stockup_id = jsonpath.jsonpath(search_res, '$..id')
        self.origin =  jsonpath.jsonpath(search_res, '$..origin')
        return self
    def stockup_confirm(self):
        """补备货确认"""
        self.stockup_id_str = ",".join(self.stockup_id)
        stockup_confirm_url = "{}/v1/stockup/NewStockUp/confirmStock".format(self.HC2018_ADMIN_URL)
        stockup_confirm_body = {"id": self.stockup_id_str}
        stockup_confirm_res = self.rss.post(url=stockup_confirm_url, json=stockup_confirm_body,
                                                headers=self.headers_json).json()
        if stockup_confirm_res["msg"] == "success":
            logger.info("补备货确认成功")
        return self

    def stockup_inquiry(self):
        """补备货询价"""
        # 更改询价人
        # self.stockup_id = ['276126']
        # self.goods_name = "0022272041"
        # self.provider_name = "Molex"
        logger.info("更改询价人为：叶茂")
        self.stockup_id_str = ",".join(self.stockup_id)
        inquiry_update_url = "{}/v1/stockup/NewStockUp/allotInquiry".format(self.HC2018_ADMIN_URL)
        inquiry_update_body = {"id": self.stockup_id_str, "user_id": "586"}
        inquiry_update_res = self.rss.post(url=inquiry_update_url, json=inquiry_update_body,
                                                headers=self.headers_json).json()
        if inquiry_update_res["msg"] == "success":
            logger.info("更改询价人为：叶茂 成功")
        search_url = "{}/v1/stockup/NewInquiry/findList".format(self.HC2018_ADMIN_URL)
        search_body = {"goods_name": self.goods_name, "provider_name": self.provider_name, "inquiry_status": "1", "is_form_erp": "1"}
        search_res = self.rss.post(url=search_url, json=search_body,
                                                headers=self.headers_json).json()
        logger.info(search_res)
        self.stockup_id = jsonpath.jsonpath(search_res, '$..id')
        logger.info(self.stockup_id)
        supplier_url = "{}/v1/common/BasicService/supList".format(self.HC2018_ADMIN_URL)
        supplier_body = {"supplier_name": "HQCHIP-TTTEST"}
        supplier_res = self.rss.post(url=supplier_url, json=supplier_body,
                                           headers=self.headers_json).json()
        self.supplier_sn = jsonpath.jsonpath(supplier_res, '$..supplier_sn')[0]
        self.cost_price = []
        self.goods_number = []
        for i in range(len(self.stockup_id)):
            inquiry_detail_url = "{}/v1/stockup/NewInquiry/findDetail".format(self.HC2018_ADMIN_URL)
            inquiry_detail_body = {"id": self.stockup_id[i]}
            inquiry_detail_res = self.rss.post(url=inquiry_detail_url, json=inquiry_detail_body,
                                       headers=self.headers_json).json()
            # logger.info(inquiry_detail_res)

            dataInfo = inquiry_detail_res["data"]
            if dataInfo["demand_type"] == "0":
                dataInfo["demand_type"] = "2"
            tax_price = dataInfo["last_price"]
            jiaoqi = dataInfo["jiaoqi"]
            demand_type = dataInfo["demand_type"]
            delivery = dataInfo["demand_type"]
            package_type = dataInfo["package_type"]
            package_number = dataInfo["package_number"]
            number = dataInfo["require_number"]
            if tax_price == "0.00000" or tax_price == "0":
                tax_price = "0.1"
            if jiaoqi == "":
                jiaoqi = "3-7"
            if package_type == "--":
                brand_resource_url  = "{}/v1/goods/DgkGoods/ajaxGetProviderName".format(self.HC2018_ADMIN_URL)
                brand_resource_body = {"provider_name": self.provider_name, "src_type": 1}
                confirm_inquiry_res = self.rss.post(url=brand_resource_url, json=brand_resource_body,
                                                headers=self.headers_json).json()
                brand_id = jsonpath.jsonpath(confirm_inquiry_res, '$..brand_id')
                brand_name = jsonpath.jsonpath(confirm_inquiry_res, '$..brand_name')
                for k in range(len(brand_name)):
                    if brand_name[k] == self.provider_name:
                        self.brand_id = brand_id[k]
                goods_resource_url = "{}//v1/goods/DgkGoods/findList".format(self.HC2018_ADMIN_URL)
                goods_resource_body = {"goods_name": self.goods_name, "brand_id": '', "search_type": "1", "page": 1, "per_page": 100,
                "self_status": "-1",  "src_type":  "-1", "has_stock": "-1", "is_enabled": "-1", "is_on_sale": "-1", "complete_type": "-1"}
                goods_resource_res = self.rss.post(url=goods_resource_url, json=goods_resource_body,
                                                headers=self.headers_json).json()
                goods_resource_id = jsonpath.jsonpath(goods_resource_res, '$..goods_id')[0]
                goods_resource_detail_url = "{}/v1/goods/DgkGoods/viewOriginData".format(self.HC2018_ADMIN_URL)
                goods_resource_detail_body = {"goods_id": goods_resource_id, "origin":  True}
                goods_resource_detail_res = self.rss.post(url=goods_resource_detail_url, json=goods_resource_detail_body,
                                                headers=self.headers_json).json()
                package_type = jsonpath.jsonpath(goods_resource_detail_res, '$..package_info')[0].split('(')[0]
                package_number = jsonpath.jsonpath(goods_resource_detail_res, '$..spq')[0]


            confirm_inquiry_url = "{}/v1/stockup/NewInquiry/confirmInquiry".format(self.HC2018_ADMIN_URL)
            confirm_inquiry_body = {"id": self.stockup_id[i], "dc": "23+", "delivery": delivery, "demand_type": demand_type, "jiaoqi": jiaoqi,
                                    "package_type": package_type, "package_number": package_number, "number": number,
                                    "tax_price": tax_price,"supplier_sn": self.supplier_sn, "transfer_number": "", "warehouse_in": 0}
            confirm_inquiry_res = self.rss.post(url=confirm_inquiry_url, json=confirm_inquiry_body,
                                       headers=self.headers_json).json()
            # logger.info(confirm_inquiry_body)
            logger.info(confirm_inquiry_res)
            if confirm_inquiry_res["msg"] == "success":
                logger.info("_____")
                inquiry_detail_url = "{}/v1/stockup/NewInquiry/findList".format(self.HC2018_ADMIN_URL)
                inquiry_detail_body = {"goods_name": self.goods_name,  "provider_name": self.provider_name, "inquiry_status": "2", "is_form_erp": "1"}
                inquiry_detail_res_finish = self.rss.post(url=inquiry_detail_url, json=inquiry_detail_body, headers=self.headers_json).json()
                logger.info(inquiry_detail_res_finish)
                stock_id_finish = self.cost_price + jsonpath.jsonpath(inquiry_detail_res_finish, '$..id')
                cost_price_finish = self.cost_price + jsonpath.jsonpath(inquiry_detail_res_finish, '$..cost_price')
                goods_number_finish = self.goods_number + jsonpath.jsonpath(inquiry_detail_res_finish, '$..goods_number')
                for m in range(len(stock_id_finish)):
                    if stock_id_finish[m] == self.stockup_id[i]:
                        self.cost_price.append(cost_price_finish[m])
                        self.goods_number.append(goods_number_finish[m])
        logger.info(self.cost_price)
        logger.info("记录询价 成功")
        return self
    def stockup_audit(self, audit_real_name=None):
        """备货审核"""
        self.worksheet_order_id = []
        search_url = "{}/v1/audit/StockUpAudit/page".format(self.HC2018_ADMIN_URL)
        search_body = {"goods_name": self.goods_name, "brand_name": self.provider_name,  "audit_user": audit_real_name, "audit_status": "0"}
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
        if len(search_res["data"]["data"]) != 0:
            self.worksheet_order_id = jsonpath.jsonpath(search_res, '$..worksheet_order_id')
            for i in range(len(self.worksheet_order_id)):
                stockup_audit_url = "{}/v1/audit/StockUpAudit/audit".format(self.HC2018_ADMIN_URL)
                stockup_audit_body = {"worksheet_order_id": self.worksheet_order_id[i], "audit_status": 2}
                stock_up_audit_res = self.rss.post(url=stockup_audit_url, json=stockup_audit_body,headers=self.headers_json).json()
                logger.info(f'审核后msg：{stock_up_audit_res["msg"]}')
        return self
    def replenishment_audit(self, audit_real_name=None):
        """补货审核"""
        self.worksheet_order_id = []
        search_url = "{}/v1/audit/ReplenishmentAudit/page".format(self.HC2018_ADMIN_URL)
        search_body = {"goods_name": self.goods_name, "brand_name": self.provider_name, "audit_user": audit_real_name, "audit_status": "0"}
        logger.info(search_body)
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers_json).json()
        # logger.info(search_res)
        if len(search_res["data"]["data"]) != 0:
            self.worksheet_order_id = jsonpath.jsonpath(search_res, '$..worksheet_order_id')
            for i in range(len(self.worksheet_order_id)):
                stockup_audit_url = "{}/v1/audit/ReplenishmentAudit/audit".format(self.HC2018_ADMIN_URL)
                stockup_audit_body = {"worksheet_order_id": self.worksheet_order_id[i], "audit_status": 2}
                stock_up_audit_res = self.rss.post(url=stockup_audit_url, json=stockup_audit_body,headers=self.headers_json).json()
                logger.info(f'审核后msg：{stock_up_audit_res["msg"]}')
    def mian_self_order_stockup(self):
        self.stock_pricing()
        self.stockup_list()
        self.stockup_confirm()
        self.stockup_inquiry()
        # self.cost_price = ['1.00000']
        # self.goods_number = ["13"]
        for i in range(len(self.stockup_id)):
            if self.origin[i] in ("1", "2", "3", "8", "9", "12", "13"):
                logger.info(f"补备货id为：{self.stockup_id[i]}走备货审核流程")
                WorkSheet(self.rss).work_sheet_search("备货审核")
                self.user_name = getattr(Data, 'user_name')
                self.start_amount = getattr(Data, 'start_amount')
                self.audit_real_name = getattr(Data, 'audit_real_name')
                for m in range(len(self.user_name)):
                   logger.info(f"此时获取启动流程中心配置的审核人为：{self.user_name[m]}的生效金额为：{self.start_amount[m]}，而此时采购金额为：{float(self.cost_price[i]) * float(self.goods_number[i])}")
                   if  float(self.cost_price[i]) * float(self.goods_number[i]) >= float(self.start_amount[m]):
                       if self.user_name[m] in self.user_pwd_json:
                             user_pwd_params = {'admin_name': 'admin', "admin_pwd": 'HQ@uat@666', "user": self.user_name[m], "pwd": self.user_pwd_json[self.user_name[m]]}
                             Hc2018_params = {"Hc2018": user_pwd_params}
                             write_yaml(account_yaml, Hc2018_params)
                             Login().login()
                             self.auth_token = getattr(Data, 'dos_auth_token')
                             self.headers_json["Authorization"] = self.auth_token
                             self.stockup_audit(self.audit_real_name[i])
                       else:
                            logger.error(f'审核人：{self.user_name[i]} 不存在字典：self.user_pwd_json，请补充')
                            break
                       # continue
                   else:
                       break
                continue


            elif self.origin[i] in ("4", "5", "6", "7", "10", "11"):
                WorkSheet(self.rss).work_sheet_search("补货审核")
                logger.info(f"补备货id为：{self.stockup_id[i]}走补货审核流程")
                self.user_name = getattr(Data, 'user_name')
                self.start_amount = getattr(Data, 'start_amount')
                self.audit_real_name = getattr(Data, 'audit_real_name')
                for m in range(len(self.user_name)):
                   logger.info(f"此时获取启动流程中心配置的审核人为：{self.user_name[m]}的生效金额为：{self.start_amount[m]}，而此时采购金额为：{float(self.cost_price[i]) * float(self.goods_number[i])}")
                   if  float(self.cost_price[i]) * float(self.goods_number[i]) >= float(self.start_amount[m]):
                       if self.user_name[m] in self.user_pwd_json:
                       # for k in self.user_pwd_json:
                       #     logger.info(k)
                       #     index = self.user_name[i] == k
                       #     logger.info(index)
                       #     if index == True:
                       #       user_pwd_params = {'admin_name': 'admin', "admin_pwd": 'HQ@uat@666', "user": self.user_name[i], "pwd": self.user_pwd_json[k]}
                             user_pwd_params = {'admin_name': 'admin', "admin_pwd": 'HQ@uat@666', "user": self.user_name[m],
                                          "pwd": self.user_pwd_json[self.user_name[m]]}
                             Hc2018_params = {"Hc2018": user_pwd_params}
                             write_yaml(account_yaml, Hc2018_params)
                             Login().login()
                             self.auth_token = getattr(Data, 'dos_auth_token')
                             self.headers_json["Authorization"] = self.auth_token
                             self.replenishment_audit(self.audit_real_name[i])
                       else:
                            logger.error(f'审核人：{self.user_name[i]} 不存在字典：self.user_pwd_json，请补充')
                            break
                       # continue
                   else:
                       break
                continue
            else:
                logger.error(f"补备货id为：{self.stockup_id[i]}为未知名补备货，请检查")
                break
        return self


if __name__ == '__main__':

    target_rss = Login().login()
    SelfOrderStockUp(target_rss).mian_self_order_stockup()