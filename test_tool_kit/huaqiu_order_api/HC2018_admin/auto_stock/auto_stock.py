import hashlib
import json
import math
import re
import time
import datetime

import jsonpath
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, autoStockYaml_dir
from huaqiu_order_api.common.yaml_handler import read_yaml
from huaqiu_order_api.project_sqlreview.mysql_connection import MySQLConnection


class AutoStock:
    def __init__(self, goods_id=None, goods_name=None, goods_no=None, provider_name=None):
        self.goods_id = int(goods_id) - 1 if goods_id not in (None, '') else ""
        self.goods_name = goods_name
        self.goods_no = goods_no
        self.provider_name = provider_name
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.headers_json = {"Content-Type": "application/json; charset=utf-8"}


    def MD5_encryption(self, str):
        """MD5加密"""
        md5 = hashlib.md5()
        md5.update(str.encode("utf-8"))
        str_md5 = md5.hexdigest()
        return str_md5

    def token_ceate(self):
        """密钥token生成"""
        # 获取当前时间戳
        timestamp = time.mktime(time.localtime(time.time()))
        timestamp_str = str(int(timestamp))
        token_encryption = self.sign + timestamp_str
        token = self.MD5_encryption(token_encryption)
        return timestamp, token

    def auto_stock(self, execution_type=None):
        """自动补货接口"""
        if "uat" in self.HC2018_ADMIN_URL:
            self.sign = "eTGDt6NkOmNLJ94WayOLIaYJZPzEbrCL"
        if "fat" in self.HC2018_ADMIN_URL:
            self.sign = "klsjdflfe&&(#02jjYY"
        timestamp, self.sign_encryption = self.token_ceate()
        # 时间戳为10位转换成时间格式
        timestamp_zh = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        logger.info(f"转换成时间格式：{timestamp_zh}")
        logger.info(f"参与加密时间戳：{int(timestamp)}，密钥：{self.sign}，md5加密：{self.sign_encryption}")
        auto_stock_url = "{}/sync/Stock/cronCreateReplenishment".format(self.HC2018_ADMIN_URL)
        auto_stock_body = {"id": self.goods_id, "sign": self.sign_encryption}
        auto_stock_res = self.rss.post(url=auto_stock_url, data=auto_stock_body, headers=self.headers).json()
        goods_id = ""
        dataInfo = auto_stock_res["data"]
        if dataInfo == []:
            logger.error(f"请检查！！！接口响应为：{auto_stock_res}")
        else:
            if execution_type == None:
                # 建立一个简单无限循环器
                int_list = [1]
                goods_id = self.goods_id
                for _ in int_list:
                    self.sign_encryption = self.token_ceate()[1]
                    # 普通自动补货
                    routine_auto_stock_url = "{}/sync/Stock/cronCreateReplenishment".format(self.HC2018_ADMIN_URL)
                    routine_auto_stock_body = {"id": goods_id, "sign": self.sign_encryption}
                    print("普通自动补货入参：{}".format(routine_auto_stock_body))
                    routine_auto_stock_res = self.rss.post(url=routine_auto_stock_url, data=routine_auto_stock_body, headers=self.headers).json()
                    print("普通自动补货执行结果：{}".format(routine_auto_stock_res))

                    # 新品自动补货
                    newProduct_auto_stock_url = "{}/sync/Stock/cronCreateNewStockUp".format(self.HC2018_ADMIN_URL)
                    newProduct_auto_stock_body = {"id": goods_id, "sign": self.sign_encryption}
                    print("新品自动补货入参：{}".format(newProduct_auto_stock_body))
                    newProduct_auto_stock_res = self.rss.post(url=newProduct_auto_stock_url, data=newProduct_auto_stock_body, headers=self.headers).json()
                    print("新品自动补货执行结果：{}".format(newProduct_auto_stock_res))

                    # 安全库存自营自动补货
                    safetyStockSelf_auto_stock_url = "{}/sync/Stock/cronCreateSafetyStockSelfStockUp".format(self.HC2018_ADMIN_URL)
                    safetyStockSelf_auto_stock_body = {"id": goods_id, "sign": self.sign_encryption}
                    print("安全库存自营自动补货入参：{}".format(safetyStockSelf_auto_stock_body))
                    safetyStockSelf_auto_stock_res = self.rss.post(url=safetyStockSelf_auto_stock_url, data=safetyStockSelf_auto_stock_body, headers=self.headers).json()
                    print("安全库存自营自动补货执行结果：{}".format(safetyStockSelf_auto_stock_res))

                    # 安全库存寄售自动补货
                    safetyStockConsign_auto_stock_url = "{}/sync/Stock/cronCreateSafetyStockJsStockUp".format(self.HC2018_ADMIN_URL)
                    safetyStockConsign_auto_stock_body = {"id": goods_id, "sign": self.sign_encryption}
                    print("安全库存寄售自动补货入参：{}".format(safetyStockConsign_auto_stock_body))
                    safetyStockConsign_auto_stock_res = self.rss.post(url=safetyStockConsign_auto_stock_url, data=safetyStockConsign_auto_stock_body, headers=self.headers).json()
                    print("安全库存寄售自动补货执行结果：{}".format(safetyStockConsign_auto_stock_res))
                    dataInfo = routine_auto_stock_res["data"]
                    if goods_id == 0:
                        logger.info("接口请求完毕,跳出循环")
                        break
                    else:
                        # logger.info(auto_stock_res)
                        goods_id = dataInfo[0]
                        logger.info(f"继续请求接口:此时获取到接口响应报文goods_id: {goods_id}")
                        int_list.append(1)
                    continue
            else:
                goods_id = self.goods_id
                self.sign_encryption = self.token_ceate()[1]
                # 普通自动补货
                routine_auto_stock_url = "{}/sync/Stock/cronCreateReplenishment".format(self.HC2018_ADMIN_URL)
                routine_auto_stock_body = {"id": goods_id, "sign": self.sign_encryption}
                print("普通自动补货入参：{}".format(routine_auto_stock_body))
                routine_auto_stock_res = self.rss.post(url=routine_auto_stock_url, data=routine_auto_stock_body,
                                                       headers=self.headers).json()
                print("普通自动补货执行结果：{}".format(routine_auto_stock_res))

                # 新品自动补货
                newProduct_auto_stock_url = "{}/sync/Stock/cronCreateNewStockUp".format(self.HC2018_ADMIN_URL)
                newProduct_auto_stock_body = {"id": goods_id, "sign": self.sign_encryption}
                print("新品自动补货入参：{}".format(newProduct_auto_stock_body))
                newProduct_auto_stock_res = self.rss.post(url=newProduct_auto_stock_url,
                                                          data=newProduct_auto_stock_body, headers=self.headers).json()
                print("新品自动补货执行结果：{}".format(newProduct_auto_stock_res))

                # 安全库存自营自动补货
                safetyStockSelf_auto_stock_url = "{}/sync/Stock/cronCreateSafetyStockSelfStockUp".format(
                    self.HC2018_ADMIN_URL)
                safetyStockSelf_auto_stock_body = {"id": goods_id, "sign": self.sign_encryption}
                print("安全库存自营自动补货入参：{}".format(safetyStockSelf_auto_stock_body))
                safetyStockSelf_auto_stock_res = self.rss.post(url=safetyStockSelf_auto_stock_url,
                                                               data=safetyStockSelf_auto_stock_body,
                                                               headers=self.headers).json()
                print("安全库存自营自动补货执行结果：{}".format(safetyStockSelf_auto_stock_res))

                # 安全库存寄售自动补货
                safetyStockConsign_auto_stock_url = "{}/sync/Stock/cronCreateSafetyStockJsStockUp".format(
                    self.HC2018_ADMIN_URL)
                safetyStockConsign_auto_stock_body = {"id": goods_id, "sign": self.sign_encryption}
                print("安全库存寄售自动补货入参：{}".format(safetyStockConsign_auto_stock_body))
                safetyStockConsign_auto_stock_res = self.rss.post(url=safetyStockConsign_auto_stock_url,
                                                                  data=safetyStockConsign_auto_stock_body,
                                                                  headers=self.headers).json()
                print("安全库存寄售自动补货执行结果：{}".format(safetyStockConsign_auto_stock_res))
                status = routine_auto_stock_res["status"]

                # 大数据优选补货自动补货
                preferredStockConsign_auto_stock_url = "{}/sync/Stock/cronCreatePreferredStockUp".format(
                    self.HC2018_ADMIN_URL)
                preferredStockConsign_auto_stock_body = {"id": goods_id, "sign": self.sign_encryption}
                print("大数据优选自动补货入参：{}".format(preferredStockConsign_auto_stock_body))
                preferredStockConsign_auto_stock_res = self.rss.post(url=preferredStockConsign_auto_stock_url,
                                                                  data=preferredStockConsign_auto_stock_body,
                                                                  headers=self.headers).json()
                print("大数据优选自动补货执行结果：{}".format(preferredStockConsign_auto_stock_res))
                status = routine_auto_stock_res["status"]
                # print(status, type(status))
                if status == "200":
                    logger.info("接口请求完毕,跳出循环")
                    goods_id = 0
        return goods_id

    def auto_stock_search(self):
        """自动补货逻辑符合判定"""
        auto_stock_search_url = "{}/v1/stockup/NewStockUp/cronCreateReplenishmentTest".format(self.HC2018_ADMIN_URL)
        auto_stock_search_body = {"goods_no": self.goods_no, "goods_name": self.goods_name, "provider_name": self.provider_name}
        auto_stock_search_res = self.rss.post(url=auto_stock_search_url, json=auto_stock_search_body, headers=self.headers_json).json()
        # 构建文本-商品ID映射
        result = ""
        msgInfo = jsonpath.jsonpath(auto_stock_search_res, "$..title")
        pt_auto_rule = jsonpath.jsonpath(auto_stock_search_res, "$..auto_stockup_info.info")[0]
        new_auto_rule = jsonpath.jsonpath(auto_stock_search_res, "$..new_stockup_info.info")[0]
        pt_has_fail = any("不通过" in item for item in [item for item in pt_auto_rule if "可用库存的可销售天数" not in item])
        new_has_fail = any("不通过" in item for item in (new_auto_rule if new_auto_rule else [])) if (new_auto_rule if new_auto_rule else []) else False
        miss_hit_rule_information = None
        auto_stock_type = []
        # 普通自动补货、动销补货、LC成交单数补货 取值ecs_goods_ic_count
        # 新品补货、LC成交单数备货 取值ecs_new_product_stockup
        # 安全库存补货 取值库存定价
        # 大数据优选备货 取值ecs_preferred_stockup
        for i in range(len(msgInfo)):
            if "自动补货条件是否通过：通过" in msgInfo and "90天成交客户数补货选项：不通过" in msgInfo:
                result = False
                miss_hit_rule_information = "自动补货条件是否通过：通过"
                print("普通自动补货规则已命中，继续检索")
                for a in range(len(auto_stock_search_res["data"])):
                    self_new_system_heat_info = auto_stock_search_res["data"][a]["auto_stockup_info"]
                    if not any("不通过" in item for item in self_new_system_heat_info["info"]):
                        setattr(Data, "self_new_system_heat_info", self_new_system_heat_info)
                stock_type = "self"
                auto_stock_type.append(stock_type)
            elif "动销补货条件是否通过：通过" in msgInfo:
                if pt_has_fail:
                    print("动销补货规则已命中但是普通自动补货规则存在不通过，继续检索")
                else:
                    # 自动补货条件基本条件（排除可用库存的可销售天数）+ 动销补货条件通过
                    result = False
                    miss_hit_rule_information = "动销补货条件是否通过：通过"
                    print("动销补货规则已命中，继续检索")
                    stock_type = "self_moving"
                    auto_stock_type.append(stock_type)
            elif "LC成交单数补货选项：通过" in msgInfo:
                # 条件：普通补货规则没有不通过，且动销补货条件不通过
                if not pt_has_fail and "动销补货条件是否通过：不通过" in msgInfo:
                    result = False
                    miss_hit_rule_information = "LC成交单数补货选项：通过"
                    print("LC成交单数补货规则已命中，继续检索")
                    stock_type = "self_lc"
                    auto_stock_type.append(stock_type)
                elif pt_has_fail:
                    print("LC成交单数补货选项但是普通自动补货规则存在不通过，继续检索")
                else:
                    print("LC成交单数补货规则已命中但条件不满足，继续检索")
            elif "90天成交客户数补货选项：通过" in msgInfo:
                # 条件：普通补货规则没有不通过，且动销补货条件不通过
                if not pt_has_fail and "动销补货条件是否通过：不通过" in msgInfo:
                    result = False
                    miss_hit_rule_information = "90天成交客户数补货选项：通过"
                    print("90天成交客户数补货选项规则已命中，继续检索")
                    for a in range(len(auto_stock_search_res["data"])):
                        self_lc_90_system_heat_info = auto_stock_search_res["data"][a]["customer_deal_stockup_info"]
                        if not any("不通过" in item for item in self_lc_90_system_heat_info["info"]):
                            setattr(Data, "self_lc_90_system_heat_info", self_lc_90_system_heat_info)
                            break
                    stock_type = "self_lc_90"
                    auto_stock_type.append(stock_type)
                elif pt_has_fail:
                    print("90天成交客户数补货选项但是普通自动补货规则存在不通过，继续检索")
                else:
                    print("90天成交客户数补货规则已命中但条件不满足，继续检索")
            elif "LC成交单数备货选项：通过" in msgInfo:
                # 排除包含"近7天购买"的规则
                exclude_keyword = "近7天购买"

                if new_auto_rule:
                    # 过滤掉包含排除关键词的规则
                    filtered_new_rule = [
                        item for item in new_auto_rule
                        if exclude_keyword not in item
                    ]
                    print(f"过滤后的规则: {filtered_new_rule}")

                    # 检查过滤后的规则是否有"不通过"
                    has_fail_after_exclude = any("不通过" in item for item in filtered_new_rule)
                    print(f"过滤后是否存在不通过: {has_fail_after_exclude}")
                else:
                    has_fail_after_exclude = True  # 没有数据时认为失败

                if has_fail_after_exclude:
                    print("LC成交单数备货规则已命中但是新品补货条件规则存在不通过（排除近7天购买量后），继续检索")
                else:
                    result = False
                    miss_hit_rule_information = "LC成交单数备货选项：通过"
                    print("LC成交单数备货规则已命中，继续检索")
                    stock_type = "new_lc"
                    auto_stock_type.append(stock_type)
            elif "LC近90天成交单数备货选项：通过" in msgInfo:
                # 排除包含"近7天购买"的规则
                exclude_keyword = "近7天购买"

                if new_auto_rule:
                    # 过滤掉包含排除关键词的规则
                    filtered_new_rule = [
                        item for item in new_auto_rule
                        if exclude_keyword not in item
                    ]
                    print(f"过滤后的规则: {filtered_new_rule}")

                    # 检查过滤后的规则是否有"不通过"
                    has_fail_after_exclude = any("不通过" in item for item in filtered_new_rule)
                    print(f"过滤后是否存在不通过: {has_fail_after_exclude}")
                else:
                    has_fail_after_exclude = True  # 没有数据时认为失败

                if has_fail_after_exclude:
                    print("LC近90天成交单数备货规则已命中但是新品补货条件规则存在不通过（排除近7天购买量后），继续检索")
                else:
                    result = False
                    miss_hit_rule_information = "LC成交单数备货选项：通过"
                    print("LC近90天成交单数备货规则已命中，继续检索")
                    for a in range(len(auto_stock_search_res["data"])):
                        new_lc_90_system_heat_info = auto_stock_search_res["data"][a]["new_lc_deal_order_main_info"]
                        if not any("不通过" in item for item in new_lc_90_system_heat_info["info"]):
                            setattr(Data, "new_lc_90_system_heat_info", new_lc_90_system_heat_info)
                            break
                    stock_type = "new_lc_90"
                    auto_stock_type.append(stock_type)
            elif "新品补货条件是否通过：通过" in msgInfo:
                result = False
                miss_hit_rule_information = "新品补货条件是否通过：通过"
                print("普通自动补货规则未命中但新品补货已命中，继续检索")
                stock_type = "new"
                auto_stock_type.append(stock_type)
            elif "安全库存补货选项：通过" in msgInfo:
                result = False
                miss_hit_rule_information = "安全库存补货选项：通过"
                print("普通自动补货规则未命中且新品补货未命中但安全库存补货已命中，继续检索")
                stock_type = "safety"
                auto_stock_type.append(stock_type)
            elif "大数据优选备货选项：通过" in msgInfo:
                result = False
                miss_hit_rule_information = "大数据优选备货选项：通过"
                print("普通自动补货规则未命中且新品补货未命中且安全库存补货未命中但优选补货已命中，继续检索")
                for a in range(len(auto_stock_search_res["data"])):
                    preferred_system_heat_info = auto_stock_search_res["data"][a]["preferred_stockup_info"]
                    if preferred_system_heat_info['info'] != []:
                        setattr(Data, "preferred_system_heat_info", preferred_system_heat_info)
                        break
                stock_type = "preferred"
                auto_stock_type.append(stock_type)
            else:
                result = True
                logger.info(f"规则未命中信息: {msgInfo[i]}")
        print(f"未去重-auto_stock_type: {auto_stock_type}")
        auto_stock_type = list(set(auto_stock_type))
        print(f"去重-auto_stock_type: {auto_stock_type}")
        if result == True:
            if auto_stock_search_res["data"] != []:
                for i in range(len(auto_stock_search_res["data"])):
                    if int(auto_stock_search_res["data"][i]["goods_id"]) == self.goods_id + 1:
                        print("存在goods_id：{}".format(self.goods_id + 1))
                        miss_hit_rule_information = auto_stock_search_res["data"][i]
                        break
                if miss_hit_rule_information == None:
                    miss_hit_rule_information = auto_stock_search_res["data"][0]
        return result, miss_hit_rule_information, auto_stock_type
    def system_heat_info(self):
        """获取系统配置里面的各类型补货上限"""
        # self.rss = Login().login()
        # self.headers_json["Authorization"] = getattr(Data, "dos_auth_token")
        StockupParam_url = "{}/v1/authorize/StockupParam/getParamInfo".format(self.HC2018_ADMIN_URL)
        StockupParam_res = self.rss.post(url=StockupParam_url, headers=self.headers_json).json()
        self_system_heat_info = StockupParam_res['data']["system_heat_info"]  # 自营补货-系统热度-旧
        if "new_system_heat_info" in StockupParam_res['data']:
            self_new_system_heat_info = StockupParam_res['data']["new_system_heat_info"]  # 自营补货-系统热度-新
        else:
            self_new_system_heat_info = {}
        self_moving_system_heat_info = StockupParam_res['data']["moving_stockup_info"]  # 自营补货-动销
        self_lc_system_heat_info = StockupParam_res['data']["lc_deal_order_info"]  # 自营补货-LC成交补货
        self_lc_90_system_heat_info = getattr(Data, "self_lc_90_system_heat_info", {})  # 新品补货-90天成交客户数补货
        new_system_heat_info = StockupParam_res['data']["new_other_info"]  # 新品补货
        new_lc_system_heat_info = StockupParam_res['data']["new_lc_deal_order_info"]  # 新品补货-LC成交备货
        new_lc_90_system_heat_info = getattr(Data, "new_lc_90_system_heat_info", {})  # 新品补货-LC近90天成交备货
        safety_system_heat_info = StockupParam_res['data']["safety_stock_other_info"]  # 安全补货
        preferred_system_heat_info = getattr(Data, "preferred_system_heat_info", {})  # 安全补货
        # print(json.dumps(system_heat_info, ensure_ascii=False))
        if isinstance(self_new_system_heat_info, dict) and self_new_system_heat_info:
            self_system_heat_info = self_new_system_heat_info
        # 资料下的品类
        search_goods_url = "{}/v1/goods/DgkGoods/findList".format(self.HC2018_ADMIN_URL)
        search_goods_body = {
                        "goods_name": self.goods_name,
                        "goods_no": self.goods_no,
                        "search_type": "1",
                        "brand_type": "1",
                        "code_search_type": "1",
                        "complete_type": -1,
                        "has_stock": "-1",
                        "is_enabled": "-1",
                        "is_on_sale": "-1",
                        "self_status": "-1",
                        "type": "0",
                        "is_need_real_count": True
                    }
        search_goods_res = self.rss.post(url=search_goods_url, json=search_goods_body, headers=self.headers_json).json()
        self.big_category_id = jsonpath.jsonpath(search_goods_res, '$..big_category_id')[0]
        self.big_category_name = jsonpath.jsonpath(search_goods_res, '$..big_category_name')[0]
        logger.info(f"获取到资料编码：{self.goods_no}的资料型号：{self.goods_name}的品类为：{self.big_category_name}")

        # 构建三者关系字典
        self_heat_stockup_limit = {}
        for item in self_system_heat_info["system_heat_value"]:
            heat = item["system_heat"]
            # 判断 self_new_system_heat_info 是否为字典
            if isinstance(self_new_system_heat_info, dict):
                # 如果是字典，从列表中查找匹配项
                stockup_limit = 1  # 默认值
                for ind in item["stockup_limit_index"]:
                    if ind["big_category_id"] == int(self.big_category_id):
                        stockup_limit = ind["stockup_limit"]
                        break
            else:
                # 如果不是字典，直接使用 item 中的 stockup_limit
                stockup_limit = item["stockup_limit"]
            self_heat_stockup_limit[heat] = {
                "system_heat_cn": item["system_heat_cn"],
                "stockup_limit": stockup_limit
            }
            if 'price_index' in item:
                self_heat_stockup_limit[heat]['price_rules'] = item['price_index']
            if 'turnover_index' in item:
                self_heat_stockup_limit[heat]['turnover_rules'] = item['turnover_index']
            if 'margin_index' in item:
                self_heat_stockup_limit[heat]['margin_rules'] = item['margin_index']
            if 'customer_index' in item:
                self_heat_stockup_limit[heat]['customer_rules'] = item['customer_index']

        self_moving_stockup_limit = {}
        for item in self_moving_system_heat_info["moving_stockup_value"]:
            heat = 1
            self_moving_stockup_limit[heat] = {
                "system_heat_cn": "自营补货-动销",
                "stockup_limit": item["stockup_limit"]
            }

        self_lc_stockup_limit = {}
        for item in self_lc_system_heat_info["lc_deal_order_value"]:
            heat = 1
            self_lc_stockup_limit[heat] = {
                "system_heat_cn": "自营补货-LC成交补货",
                "stockup_limit": item["stockup_limit"]
            }
        self_lc_90_stockup_limit = {}
        if self_lc_90_system_heat_info != {}:
            heat = 1
            stockup_limit = None
            stockup_limit_rate = None
            for item in self_lc_90_system_heat_info["info"]:
                match = re.search(r'最终补货数量：.*?=(\d+)', item)
                match_rate = re.search(r'最终补货系数：.*?=(\d+)；', item)
                if match:
                    stockup_limit = match.group(1)
                if match_rate:
                    stockup_limit_rate = match_rate.group(1)
                    break
            if stockup_limit is not None:
                self_lc_90_stockup_limit[heat] = {
                    "system_heat_cn": "自营补货-90天成交客户数补货",
                    "stockup_limit": stockup_limit,
                    "stockup_limit_rate": stockup_limit_rate
                }
        new_heat_stockup_limit = {}
        for item in new_system_heat_info["daigou_stockup_value"]:
            heat = 1
            new_heat_stockup_limit[heat] = {
                "system_heat_cn": item["stock_type_cn"],
                "stockup_limit": item["stockup_limit"]
            }
        new_lc_stockup_limit = {}
        for item in new_lc_system_heat_info["lc_deal_order_value"]:
            heat = 1
            new_lc_stockup_limit[heat] = {
                "system_heat_cn": "新品补货-LC成交备货",
                "stockup_limit": item["stockup_limit"]
            }
        new_lc_90_stockup_limit = {}
        if new_lc_90_system_heat_info !={}:
            heat = 1
            stockup_limit = None
            for item in new_lc_90_system_heat_info["info"]:
                match = re.search(r'=(\d+)', item)
                if match:
                    stockup_limit = match.group(1)
                    break
            if stockup_limit is not None:
                new_lc_90_stockup_limit[heat] = {
                    "system_heat_cn": "新品补货-LC近90天成交备货",
                    "stockup_limit": stockup_limit
                }
        safety_heat_stockup_limit = {}
        for item in safety_system_heat_info["safety_stock_value"]:
            heat = item["system_heat"]
            safety_heat_stockup_limit[heat] = {
                "system_heat_cn": item["system_heat_cn"],
                "stockup_limit": item["stockup_limit"]
            }
        preferred_heat_stockup_limit = {}
        if preferred_system_heat_info !={}:
            heat = 1
            stockup_limit = None
            for item in preferred_system_heat_info["info"]:
                match = re.search(r'优选需求数量：(\d+)', item)
                if match:
                    stockup_limit = match.group(1)
                    break
            if stockup_limit is not None:
                preferred_heat_stockup_limit[heat] = {
                    "system_heat_cn": "大数据优选",
                    "stockup_limit": stockup_limit
                }
        # 整合成一个嵌套字典
        heat_stockup_mapping = {
            "self": self_heat_stockup_limit,
            "self_moving": self_moving_stockup_limit,
            "self_lc": self_lc_stockup_limit,
            "self_lc_90": self_lc_90_stockup_limit,
            "new": new_heat_stockup_limit,
            "new_lc": new_lc_stockup_limit,
            "new_lc_90": new_lc_90_stockup_limit,
            "safety": safety_heat_stockup_limit,
            "preferred": preferred_heat_stockup_limit
        }
        # 输出最终字典
        # print(json.dumps(self_heat_stockup_limit, ensure_ascii=False))
        return heat_stockup_mapping

    # 通用区间匹配函数：根据实际值匹配对应系数
    def get_match_coefficient(self, real_val, rule_list):
        """
        real_val: 指标实际数值 float/int
        rule_list: 对应指标的区间规则数组
        return: 匹配到的coefficient
        """
        for rule in rule_list:
            min_str = rule["min_value"]
            max_str = rule["max_value"]
            coeff = rule["coefficient"]

            # 转换边界值，空字符串代表无边界
            min_val = float(min_str) if min_str != "" else None
            max_val = float(max_str) if max_str != "" else None

            # 判断区间命中
            hit = True
            if min_val is not None:
                hit = hit and real_val >= min_val
            if max_val is not None:
                hit = hit and real_val <= max_val
            if hit:
                return coeff
        # 兜底返回1（理论上不会走到这里，配置全覆盖）
        return 1
   # 计算修正后备货上限函数
    # 3. 计算修正后备货上限函数
    def calc_real_stockup_limit(self, heat_full_config, price_real, turnover_real, margin_real, customer_real):
        """
        heat_code: 商品热度编码 3/4/5/6/7/8
        price_real: 价格波动绝对值
        turnover_real: 周转系数
        margin_real: 毛利率数值
        customer_real: 客户数量
        return: 修正后的实际备货上限
        """
        cfg = heat_full_config
        base = cfg["stockup_limit"]

        # 分别获取四类指标系数
        coeff_price = self.get_match_coefficient(price_real, cfg["price_rules"])
        coeff_turnover = self.get_match_coefficient(turnover_real, cfg["turnover_rules"])
        coeff_margin = self.get_match_coefficient(margin_real, cfg["margin_rules"])
        coeff_customer = self.get_match_coefficient(customer_real, cfg["customer_rules"])

        # 计算公式：基础值 * 四个系数相乘
        # real_limit = base * coeff_price * coeff_turnover * coeff_margin * coeff_customer
        # print(f"real_limit : {real_limit} = base: {base} * coeff_price: {coeff_price} * coeff_turnover: {coeff_turnover} * coeff_margin: {coeff_margin} * coeff_customer: {coeff_customer}")

        real_limit = base * coeff_turnover * coeff_margin * coeff_customer
        print(f"real_limit : {real_limit} = base: {base} * coeff_turnover: {coeff_turnover} * coeff_margin: {coeff_margin} * coeff_customer: {coeff_customer}")
        return real_limit

    def get_stock_limit_by_priority(self, auto_stock_type, system_heat, default_price_real=None,
                                    default_turnover_real=None,default_margin_real=None,default_customer_real=None):
        """从多个补货类型中获取所有补货上限"""
        heat_stockup_mapping = self.system_heat_info()
        system_heat_int = int(system_heat)

        # 定义不需要匹配热度的类型
        no_match_types = ['self_moving', 'self_lc', 'self_lc_90', 'new', 'new_lc', 'new_lc_90', 'preferred']

        all_results = []  # 存储所有结果
        for stock_type in auto_stock_type:
            type_dict = heat_stockup_mapping.get(stock_type, {})

            if not type_dict:
                print(f"类型 {stock_type} 无数据")
                continue

            # 特殊类型：不需要匹配热度
            if stock_type in no_match_types:
                # print("type_dict: ", type_dict)
                first_heat = next(iter(type_dict))
                stock_limit = type_dict[first_heat]['stockup_limit']
                append_result = {
                    'stock_limit': stock_limit,
                    'matched_type': stock_type,
                    'matched_heat': first_heat
                }
                all_results.append(append_result)
                if stock_type == "self_lc_90":
                    append_result["stockup_limit_rate"] = type_dict[first_heat]['stockup_limit_rate']
                    print(f"在类型 {stock_type} 中找到补货上限（固定值）: {stock_limit}, 补货上限系数为{type_dict[first_heat]['stockup_limit_rate']}")
                else:
                    print(f"在类型 {stock_type} 中找到补货上限（固定值）: {stock_limit}")

            # 普通类型：需要匹配热度
            else:
                # 尝试整数匹配

                if system_heat_int in type_dict:
                    stock_limit = type_dict[system_heat_int]['stockup_limit']
                    if stock_type == "self":
                        if "price_rules" in type_dict[system_heat_int]:
                            self_new_system_heat_info = getattr(Data, "self_new_system_heat_info", {})  # 新系统热度补货
                            price_real = turnover_real = margin_real = customer_real = None
                            for item in self_new_system_heat_info["info"]:
                                match_price = re.search(r'价格指数：(\d+)', item)
                                match_turnover = re.search(r'90天年化存货周转率：(\d+)', item)
                                match_margin = re.search(r'90天平均毛利率：(\d+)', item)
                                match_customer = re.search(r'90天销售客户数量：(\d+)', item)

                                if match_price:
                                    price_real = match_price.group(1)
                                    break
                                if match_turnover:
                                    turnover_real = match_turnover.group(1)
                                    break
                                if match_turnover:
                                    margin_real = match_margin.group(1)
                                    break
                                if match_turnover:
                                    customer_real = match_customer.group(1)
                                    break
                            print(f"price_real: {price_real}，turnover_real: {turnover_real}，margin_real: {margin_real}，customer_real: {customer_real}")
                            if price_real == None  or turnover_real == None  or margin_real == None  or customer_real == None:
                                try:
                                    price_real, turnover_real, margin_real,  customer_real =MySQLConnection(table_name="ecs_goods_ic_count", where_field_name="goods_name",
                                                    where_field_value=self.goods_name,
                                                    orderby_field_name="c_time").mysql_select_main()
                                    print("mySQL数据库查询price_real, turnover_real, margin_real,  customer_real分别为：", price_real, turnover_real, margin_real,  customer_real)
                                except Exception as e:
                                    logger.info(f"数据库查询失败：{e}")
                                    logger.info(f"默认定义相关数据")
                                    price_real = default_price_real
                                    turnover_real = default_turnover_real
                                    margin_real = default_margin_real
                                    customer_real = default_customer_real
                            real_limit = self.calc_real_stockup_limit(type_dict[system_heat_int], price_real, turnover_real, margin_real, customer_real)
                            stock_limit = real_limit
                    all_results.append({
                        'stock_limit': stock_limit,
                        'matched_type': stock_type,
                        'matched_heat': system_heat_int
                    })

                    print(f"在类型 {stock_type} 中找到热度 {system_heat} 的补货上限: {stock_limit}")

                # 尝试字符串匹配
                elif str(system_heat_int) in type_dict:
                    stock_limit = type_dict[str(system_heat_int)]['stockup_limit']
                    if stock_type == "self":
                        if "price_rules" in type_dict[system_heat_int]:
                            self_new_system_heat_info = getattr(Data, "self_new_system_heat_info", {})  # 新系统热度补货
                            price_real = turnover_real = margin_real = customer_real = None
                            for item in self_new_system_heat_info["info"]:
                                match_price = re.search(r'价格指数：(\d+)', item)
                                match_turnover = re.search(r'90天年化存货周转率：(\d+)', item)
                                match_margin = re.search(r'90天平均毛利率：(\d+)', item)
                                match_customer = re.search(r'90天销售客户数量：(\d+)', item)

                                if match_price:
                                    price_real = match_price.group(1)
                                    break
                                if match_turnover:
                                    turnover_real = match_turnover.group(1)
                                    break
                                if match_turnover:
                                    margin_real = match_margin.group(1)
                                    break
                                if match_turnover:
                                    customer_real = match_customer.group(1)
                                    break
                            print(f"price_real: {price_real}，turnover_real: {turnover_real}，margin_real: {margin_real}，customer_real: {customer_real}")
                            if price_real == None  or turnover_real == None  or margin_real == None  or customer_real == None:
                                try:
                                    price_real, turnover_real, margin_real,  customer_real =MySQLConnection(table_name="ecs_goods_ic_count", where_field_name="goods_name",
                                                    where_field_value=self.goods_name,
                                                    orderby_field_name="c_time").mysql_select_main()
                                    print("mySQL数据库查询price_real, turnover_real, margin_real,  customer_real分别为：", price_real, turnover_real, margin_real,  customer_real)
                                except Exception as e:
                                    logger.info(f"数据库查询失败：{e}")
                                    logger.info(f"默认定义相关数据")
                                    price_real = default_price_real
                                    turnover_real = default_turnover_real
                                    margin_real = default_margin_real
                                    customer_real = default_customer_real
                            real_limit = self.calc_real_stockup_limit(type_dict[system_heat_int], price_real, turnover_real, margin_real, customer_real)
                            stock_limit = real_limit
                    all_results.append({
                        'stock_limit': stock_limit,
                        'matched_type': stock_type,
                        'matched_heat': str(system_heat_int)
                    })
                    print(f"在类型 {stock_type} 中找到热度 {system_heat} 的补货上限: {stock_limit}")

                else:
                    print(f"在类型 {stock_type} 中未找到热度 {system_heat}")

        if all_results:
            # 可以选择返回所有结果
            return all_results
            # 或者返回第一个（按优先级）
            # return all_results[0]

        print(f"在类型列表 {auto_stock_type} 中未找到补货上限")
        return []

    def auto_stock_create(self, auto_stock_type=None, default_price_real=None,
                                    default_turnover_real=None,default_margin_real=None, default_customer_real=None):
        """自动补货生成逻辑判断"""
        now_day = str(datetime.datetime.now().date())
        logger.info(f"获取当前时间:{now_day}")
        restock_list_url = "{}/v1/stockup/NewStockUp/findList".format(self.HC2018_ADMIN_URL)
        restock_list_body = {"goods_no": self.goods_no,"goods_name": self.goods_name, "from_user": "系统", "start_add_time": now_day,
                             "end_add_time": now_day, "stock_status": 5, "page": 1, "per_page": 20}
        restock_list_res = self.rss.post(url=restock_list_url, json=restock_list_body,
                                       headers=self.headers_json).json()
        dataInfo = restock_list_res["data"]["data"]
        if dataInfo == []:
            logger.error("生成失败,请检查")
        else:
            logger.info("生成成功")
            require_number_list = jsonpath.jsonpath(dataInfo, '$..require_number')
            auto_stockup_type_cn_list = jsonpath.jsonpath(dataInfo, '$..auto_stockup_type_cn')
            month_avg_sale_pay_list = jsonpath.jsonpath(dataInfo, '$..six_month_avg_sale_pay')
            avg_month_removal_number_list = jsonpath.jsonpath(dataInfo, '$..avg_month_removal_number')
            system_heat_list = jsonpath.jsonpath(dataInfo, '$..system_heat')
            spot_number_list = jsonpath.jsonpath(dataInfo, '$..spot_number')
            transfer_number_list = jsonpath.jsonpath(dataInfo, '$..transfer_number')
            # 通过资料拿取包装数量
            information_url = "{}/v1/goods/DgkGoods/findList".format(self.HC2018_ADMIN_URL)
            information_body = {"goods_name": self.goods_name, "search_type": "1"}
            information_res = self.rss.post(url=information_url, json=information_body,
                                             headers=self.headers_json).json()
            # logger.info(require_number_list)
            # 资料id： goods_id
            goods_id = information_res["data"]["data"][0]["goods_id"]
            information_detail_url = "{}/v1/goods/DgkGoods/goodsEdit".format(self.HC2018_ADMIN_URL)
            information_detail_body = {"goods_id": goods_id}
            information_detail_res = self.rss.post(url=information_detail_url, json=information_detail_body,
                                             headers=self.headers_json).json()
            # logger.info(information_detail_res)
            package_number = next((item.get("spq") for item in information_detail_res.get("data", {}).get("package_list", [])), '')
            # print(f"package_number: {package_number}")
            # 存储匹配结果
            matched_results = []
            # 系统热度【1:商品资料、2:新品、3:异常冷门、4:非常冷门、5:冷门、6∶常规、7:热门、8:非常热门】
            StockupParam_url = "{}/v1/authorize/StockupParam/getParamInfo".format(self.HC2018_ADMIN_URL)
            StockupParam_res = self.rss.post(url=StockupParam_url, headers=self.headers_json).json()
            new_system_heat_rule_status = StockupParam_res['data']["new_system_heat_info"]["system_heat_status"]
            stock_type_auto_json = {
                "self": ["补货-系统热度"],
                "self_moving": ["补货-动销"],
                "self_lc": ["补货-LC成交单据"],
                "self_lc_90": ["90天成交客户数补货"],
                "new": ["备货-代购"],
                "new_lc": ["备货-LC成交单据"],
                "new_lc_90": ["LC近90天成交单数备货"],
                "safety": ["安全库存补货"],
                "preferred": ["大数据优选"]
            }
            if not isinstance(auto_stock_type, list):
                auto_stock_type = [auto_stock_type]  # 转换为单元素列表
            for stock_type in auto_stock_type:
                # 修复：使用 stock_type 作为 key，而不是字符串 "stock_type"
                stock_type_auto_cn_list = stock_type_auto_json.get(stock_type, [])
                if not stock_type_auto_cn_list:
                    logger.warning(f"未找到类型 {stock_type} 的配置")
                    continue
                for i, stockup_type_cn in enumerate(auto_stockup_type_cn_list):
                    if stockup_type_cn in stock_type_auto_cn_list:
                        # 当 stock_type == "self_lc_90" 时，无论 new_system_heat_rule_status 为何值，都使用 avg_month_removal_number。
                        # 当 stock_type == "self" 时，仅当 new_system_heat_rule_status == 1 时使用 avg_month_removal_number，否则使用 month_avg_sale_pay_list。
                        # 获取 新热度规则开启状态
                        if (stock_type == "self_lc_90") or (stock_type == "self" and new_system_heat_rule_status == 1):
                            logger.info("月均销用新字段avg_month_removal_number")
                            month_val = avg_month_removal_number_list[i] if i < len(avg_month_removal_number_list) else 0
                        else:
                            logger.info("月均销用原字段month_avg_sale_pay")
                            month_val = month_avg_sale_pay_list[i] if i < len(month_avg_sale_pay_list) else 0
                        # 获取对应的值
                        matched_result = {
                            'stock_type': stock_type,
                            'auto_stockup_type_cn': stockup_type_cn,
                            'require_number': require_number_list[i] if i < len(require_number_list) else None,
                            'month_avg_sale_pay': month_val,
                            'system_heat': system_heat_list[i] if i < len(system_heat_list) else None,
                            'spot_number': spot_number_list[i] if i < len(spot_number_list) else None,
                            'transfer_number': transfer_number_list[i] if i < len(transfer_number_list) else None,
                        }


                        type_heat_stockup_mapping = self.get_stock_limit_by_priority([stock_type], matched_result['system_heat'],
                                                                                    default_price_real=default_price_real,
                                                                                     default_turnover_real=default_turnover_real,
                                                                                     default_margin_real= default_margin_real,
                                                                                     default_customer_real=default_customer_real)
                        # print("type_heat_stockup_mapping: ", type_heat_stockup_mapping)
                        stock_limit = next((item['stock_limit'] for item in type_heat_stockup_mapping if
                                            item['matched_type'] == stock_type), 2)
                        stock_limit_rate = next((item['stockup_limit_rate'] for item in type_heat_stockup_mapping if
                                            item['matched_type'] == "self_lc_90"), None)
                        matched_result["stock_limit"] = stock_limit
                        matched_result["stock_limit_rate"] = stock_limit_rate
                        matched_results.append(matched_result)
                # if system_heat in ("1", "2", "3", "4", "5", "6"):
                #     if int(month_avg_sale_pay) >= int(spot_number) + int(transfer_number) and int(math.ceil(float(month_avg_sale_pay) * 2 / float(package_number)))*int(package_number) == int(require_number):
                #         logger.info("生成需求数里准确")
                #     else:
                #         logger.error("生成需求数里不准确，请检查!!")
                # if system_heat in ("7", "8"):
                #     if int(month_avg_sale_pay) >= int(spot_number) * 1.5 and int(math.ceil(float(month_avg_sale_pay) * 2 / float(package_number))) * int(package_number) == int(require_number):
                #         logger.info("生成需求数里准确")
                #     else:
                #         logger.error("生成需求数里不准确，请检查!!")
                stock_type_auto_name = {
                    "self": "自营补货",
                    # "self_lc_90": "自营补货-90天成交客户数补货",
                    "new": "新品补货",
                    "new_lc_90": "新品补货-LC近90天成交单数备货",
                    "safety": "安全库存补货",
                    "preferred": "优选补货"
                }
                for matched_result in matched_results:
                    stock_auto_name = stock_type_auto_name.get(matched_result['stock_type'], '')
                    logger.info(
                        f"自动补货类型：{stock_auto_name}：{matched_result['auto_stockup_type_cn']}，生成的需求数量: {matched_result['require_number']}，月均销: {matched_result['month_avg_sale_pay']}，现货库存: {matched_result['spot_number']}，"
                        f"调拨在途库存: {matched_result['transfer_number']}，包装数量: {package_number}")

                    # if int(matched_result['month_avg_sale_pay']) >= int(matched_result['spot_number']) + int(matched_result['transfer_number']):
                    if package_number != '':
                        if stock_auto_name in ["优选补货", "新品补货-LC近90天成交单数备货"]:
                            logger.info("计算方式：补货需求数量 = 大数据同步的需求数量")
                            if int(matched_result['stock_limit']) == int(matched_result['require_number']):
                                logger.info(f"生成需求数里准确, 计算值：{int(matched_result['stock_limit'])}, 生成值：{matched_result['require_number']}")
                            else:
                                logger.error(f"生成需求数里不准确，请检查!!,计算值：{int(matched_result['stock_limit'])}, 生成值：{matched_result['require_number']}")
                        else:
                            logger.info("计算方式：补货需求数量=月均销*补货倍数/最小包装量，结果做四舍五入再乘以最小包装数量（最低值为1倍最小包装数量）") # 最小包装取商品资料中，默认的最小包装数量
                            stock_limit = matched_result['stock_limit']
                            if matched_result['stock_type'] == "self_lc_90":
                                stock_limit = matched_result['stock_limit_rate']
                            logger.info(
                                f"stock_limit: {matched_result['stock_limit']}, "
                                f"month_avg_sale_pay: {matched_result['month_avg_sale_pay']},"
                                f"package_number: {package_number}")
                            final_num = 1 if (float(matched_result['month_avg_sale_pay']) * float(stock_limit) / float(package_number)) < 1 else round(float(matched_result['month_avg_sale_pay']) * float(stock_limit) / float(package_number))
                            if int(final_num) * int(package_number) == int(matched_result['require_number']):
                                logger.info(f"生成需求数里准确, 计算值：{int(final_num) * int(package_number)}, 生成值：{matched_result['require_number']}")
                            else:
                                logger.error(f"生成需求数里不准确，请检查!!,计算值：{int(final_num) * int(package_number)}, 生成值：{matched_result['require_number']}")
                    else:
                        if stock_auto_name in ["优选补货", "新品补货-LC近90天成交单数备货"]:
                            logger.info("计算方式：补货需求数量= 大数据同步的需求数量")
                            if int(matched_result['stock_limit']) == int(matched_result['require_number']):
                                logger.info(f"生成需求数里准确, 计算值：{int(matched_result['stock_limit'])}, 生成值：{matched_result['require_number']}")
                            else:
                                logger.error(
                                    f"生成需求数里不准确，请检查!!,计算值：{int(matched_result['stock_limit'])}, 生成值：{matched_result['require_number']}")
                        else:
                            logger.info("计算方式：按现有规则执行，补货需求数量=月均销*补货倍数，向上取整")
                            stock_limit = matched_result['stock_limit']
                            if matched_result['stock_type'] == "self_lc_90":
                                stock_limit = matched_result['stock_limit_rate']
                            if int(math.ceil(float(matched_result['month_avg_sale_pay']) * float(stock_limit))) == int(matched_result['require_number']):
                                logger.info(f"生成需求数里准确,  计算值：{int(math.ceil(float(matched_result['month_avg_sale_pay']) * float(stock_limit)))}, 生成值：{matched_result['require_number']}")
                            else:
                                logger.error(f"生成需求数里不准确，请检查!!,计算值：{int(math.ceil(float(matched_result['month_avg_sale_pay']) * float(stock_limit)))}, 生成值：{matched_result['require_number']}")
                    # else:
                    #     logger.error("不满足生成规则，请检查!!")


        return self

    def auto_stock_mian(self, target_type, execution_type=None):
        # print(self.goods_id)
        info = self.get_goods_info(target_type)
        default_price_real = None
        default_turnover_real = None
        default_margin_real = None
        default_customer_real = None
        if target_type == "self":
            # 新热度补货启用
            default_price_real = 0.15
            default_turnover_real = 2.26
            default_margin_real = 15.0
            default_customer_real = 15
        if info:
            self.goods_name = info['goods_name']
            self.goods_no = info['goods_no']
            self.goods_id = int(info['goods_id']) - 1 if info['goods_id'] not in (None, '') else ""
            logger.info(f"类型:{target_type}匹配到的商品名称: {self.goods_name}，商品编号: {self.goods_no}，商品ID: { int(self.goods_id) + 1 }")
        else:
            print("不存在该类型")
        self.rss = Login().login()
        self.headers_json["Authorization"] = getattr(Data, "dos_auth_token")
        result, miss_rule_information, auto_stock_type = self.auto_stock_search()
        # print(miss_rule_information)
        if result == False:
            logger.info("型号符合自动补货规则")
            goods_id = self.auto_stock(execution_type=execution_type)
            # goods_id = 0
            if goods_id == 0:
                print("已执行完成")
                self.auto_stock_create(auto_stock_type=auto_stock_type, default_price_real=default_price_real,
                                    default_turnover_real=default_turnover_real, default_margin_real=default_margin_real, default_customer_real=default_customer_real)
        return result, miss_rule_information, auto_stock_type
    def debug(self):
        if "uat" in self.HC2018_ADMIN_URL:
            self.sign = "eTGDt6NkOmNLJ94WayOLIaYJZPzEbrCL"
        if "fat" in self.HC2018_ADMIN_URL:
            self.sign = "klsjdflfe&&(#02jjYWY"
        timestamp, self.sign_encryption = self.token_ceate()
        self.rss = Login().login()
        self.headers_json["Authorization"] = getattr(Data, "dos_auth_token")
        logger.info(f"参与加密时间戳：{int(timestamp)}，密钥：{self.sign}，md5加密：{self.sign_encryption}")
        auto_stock_search_url = "{}/v1/stockup/NewStockUp/cronCreateReplenishmentTest".format(self.HC2018_ADMIN_URL)
        auto_stock_search_body = {"goods_no": self.goods_no, "goods_name": self.goods_name, "provider_name": self.provider_name}
        auto_stock_search_res = self.rss.post(url=auto_stock_search_url, json=auto_stock_search_body, headers=self.headers_json).json()
        # print(auto_stock_search_res)

        # 构建文本-商品ID映射
        data_list = auto_stock_search_res["data"]
        msg_id_map = {}
        for d in data_list:
            gid = d["goods_id"]
            title_list = jsonpath.jsonpath(d, "$..title") or []
            for text in title_list:
                # 不存在则初始化空列表，不覆盖原有数据
                if text not in msg_id_map:
                    msg_id_map[text] = []
                # 追加当前goods_id
                msg_id_map[text].append(gid)
        print(msg_id_map)

    def get_goods_info(self, goods_type):
        """
        根据类型匹配商品信息
        :param goods_type: 类型字符串：self / self_moving / new / safety / preferred 等
        :param config: yaml加载后的字典
        :return: 对应商品dict；不存在返回None
        """
        config = read_yaml(autoStockYaml_dir)
        return config.get(goods_type)
if __name__ == '__main__':
    target_type = "new_lc_90"
    # info = AutoStock().get_goods_info(goods_type=target_type)
    AutoStock().auto_stock_mian(target_type=target_type, execution_type=1)
    # all_results = AutoStock(goods_id, goods_name, goods_no, "").get_stock_limit_by_priority(['self', 'new', 'safety'], "4")
    # print(all_results)
    # AutoStock(goods_id, goods_name, goods_no, "").debug()

