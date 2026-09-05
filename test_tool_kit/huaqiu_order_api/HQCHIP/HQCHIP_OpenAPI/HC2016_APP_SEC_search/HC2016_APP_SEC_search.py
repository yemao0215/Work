import math
import re
from collections import ChainMap

import jsonpath
import requests
import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class HC2016APPSECSearch:
    def __init__(self):
        self.rss = requests.Session()
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQCHIP_ADMIN_URL = data['HQCHIP_ADMIN_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.headers_json = {"Content-Type": "application/json; charset=UTF-8",
                             "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                             }
    def hc2016_login(self):
        """HC2016后台登录"""
        login_url = "{}/Admin/Public/checkLogin/".format(self.HQCHIP_ADMIN_URL)
        self.body = {"user_name": "admin", "password": "HQ@uat@666"}
        logger.info(f"开始执行登录账号：{self.body}")
        self.rss.post(url=login_url, data=self.body, headers=self.headers)
        logger.info(f"登录完成")
        return self

    def app_sec_search(self):
        """app_sec获取"""
        APP_KEY = getattr(Data, "APP_KEY", '')
        if APP_KEY == "":
            APP_KEY = "e5e94a32a53f363719106b66969c642f"
        app_sec_search_url = "{}/Admin/Openapi/index".format(self.HQCHIP_ADMIN_URL)
        app_sec_search_body = {"pageNum": 1, "name": "", "user_id": "", "app_key": APP_KEY}
        app_sec_search_res = self.rss.post(url=app_sec_search_url, data=app_sec_search_body, headers=self.headers).text
        APP_ID = re.search('(<a href="/Admin/Openapi/edit/id/)([0-9]*)', app_sec_search_res).group(2)
        screct_id_url = "{}/Admin/Openapi/screct/id/{}".format(self.HQCHIP_ADMIN_URL, APP_ID)
        screct_id_res = self.rss.get(url=screct_id_url).text
        APP_SEC = re.search(r'<label.*?密钥：</label>\s*<span.*?>(.*?)</span>', screct_id_res).group(1)
        return APP_SEC
    def app_key_conf(self):
        """
        app_key详情配置
        配置字段解析：
        app_id  APP ID   自增id
        app_name key对应公司名称
        user_id key对应申请API接口的芯城user_id
        status key对应申请API接口的开放状态
        supplier_limit  key对应申请API接口的开放供应商限制  不限制填0，留空无被允许，填具体的数值对供应商id开放
        supplier_exclude key对应申请API接口的开放排除提供数据的供应商  不限制留空，填具体的数值对供应商id进行过滤
        req_limit  key对应申请API接口的请求频率 不限制填0，留空无被允许
        stock_nolimit key对应申请API接口的无视库存不足 不限制填0 填具体的数值对供应商id开放
        price_nolimit key对应申请API接口的无视无价格 不限制填0 填具体的数值对供应商id开放
        self_cat_limit key对应申请API接口的自营分类限制 不限制填0 填具体的数值对分类id开放
        brand_limit key对应申请API接口的品牌限制 不限制留空，填具体的数值对品牌id进行过滤
        return_url key对应申请API接口的跳转通知 不限制留空
        notice_url key对应申请API接口的异步通知 不限制留空
        app_key 应用KEY
        expressage_type 运费方式 勾选返回对应值，0系统计价  1固定值
        order_bring_delivery_msg 下单带出交期 0否   1是
        permission_order  下单权限 未勾选，不存在app_key_conf_dict字典中
        permission_search  搜索权限 未勾选，不存在app_key_conf_dict字典中
        permission_pay 支付权限 未勾选，不存在app_key_conf_dict字典中
        permission_stocklist 库存列表权限 未勾选，不存在app_key_conf_dict字典中
        permission_vmi_order 下VMI单权限 未勾选，不存在app_key_conf_dict字典中并不可直接用型号名称下单
        """
        APP_KEY = getattr(Data, "APP_KEY", '')
        if APP_KEY == "":
            APP_KEY = "e5e94a32a53f363719106b66969c642f"
        app_sec_search_url = "{}/Admin/Openapi/index".format(self.HQCHIP_ADMIN_URL)
        app_sec_search_body = {"pageNum": 1, "name": "", "user_id": "", "app_key": APP_KEY}
        app_sec_search_res = self.rss.post(url=app_sec_search_url, data=app_sec_search_body, headers=self.headers).text
        APP_ID = re.search('(<a href="/Admin/Openapi/edit/id/)([0-9]*)', app_sec_search_res).group(2)
        app_key_conf_url = "{}/Admin/Openapi/edit/id/{}".format(self.HQCHIP_ADMIN_URL, APP_ID)
        app_key_conf_res = self.rss.post(url=app_key_conf_url, headers=self.headers).text
        matches = re.findall(r'<label>(.*?)：</label>\s*<input[^>]+name="([^"]+)"[^>]+value="([^"]*)"', app_key_conf_res)
        # 将结果存储到字典中
        result = {name: value for label, name, value in matches}

        # 定义一个正则表达式来提取带有 selected 的 radio 输入框的值
        matches_radio_selected = re.findall(r'<select\s+name="([^"]+)">\s*<option\s+value="([^"]+)"\s+selected(?:="selected")?[^>]*>.*?</option>.*?</select>', app_key_conf_res, re.DOTALL)
        result_radio_selected = {name: value for name, value in matches_radio_selected}

        # 定义一个正则表达式来提取带有 checked 的 radio 输入框的值
        matches_radio_checked = re.findall(r'<input[^>]+type="(?:radio|checkbox)"[^>]+name="([^"]+)"[^>]+value="([^"]+)"[^>]*checked', app_key_conf_res)
        # print(matches_radio_checked)
        result_radio_checked = {name: value for name, value in matches_radio_checked}

        # 输出结果
        app_key_conf_dict = dict(ChainMap(result, result_radio_selected, result_radio_checked))
        return app_key_conf_dict

    def mian_app_sec(self):
        self.hc2016_login()
        APP_SEC = self.app_sec_search()
        app_key_conf_dict = self.app_key_conf()
        return APP_SEC, app_key_conf_dict
if __name__ == '__main__':
    HC2016APPSECSearch().mian_app_sec()
