import re

import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml



class ErpWithdrawManage:


    def __init__(self, rss):
        """
        :param account:  登录ERP账号
        :param psw:  登录ERP密码
        :param order_sn:  前台商城生成订单编号
        :param uesr:    前台商城生成订单编号的用户名称
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.rss = rss
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.uid = getattr(Data, 'uid', "5146221")
        # self.uid =

    def withdraw_order_submit(self):
        """
        提现订单确认订单
        """
        withdraw_order_search_url = "{}/Withdraw/index".format(self.ERP_URL)
        withdraw_order_search_body = {
            "pageNum": 1,
            "picking_group_id": -1,
            "picking_uid": -1,
            "keyword": "",
            "tab_index": 0,
            "type": 3,
            "search_value": self.uid,
            "orderNo": "",
            "salesmanName": "",
            "smtCsName": "",
            "status": 0,
            "bankCardNoType": 0,
            "startTime": "",
            "endTime": "",
        }
        withdraw_order_search_res = self.rss.post(url=withdraw_order_search_url, data=withdraw_order_search_body, headers=self.headers).text
        withdraw_order = re.search('(<a href="/Withdraw/confirm/orderNo/)(W[0-9]*)', withdraw_order_search_res).group(2)
        confirm_detail_url = "{}/Withdraw/confirm/orderNo/{}".format(self.ERP_URL, withdraw_order)
        confirm_detail_res = self.rss.get(url=confirm_detail_url).text
        remark = confirm_detail_res.split('<textarea name="remark" cols="60"  rows="3">')[1].split('</textarea>')[0]
        confirm_url = "{}/Withdraw/confirm&navTabId=Withdraw".format(self.ERP_URL)
        confirm_body = {"orderNo": withdraw_order, "remark": remark, "ajax": 1, "is_iframe": 1}
        confirm_res = self.rss.post(url=confirm_url, data=confirm_body).text
        setattr(Data, "withdraw_order", withdraw_order)
        print(f"确认成功，打印执行结果：{confirm_res}")
        return withdraw_order

if __name__ == '__main__':
    SSO_Reception('https://uat-www.hqchip.com').login()
    rss = SOOLogin("uat-e.hqchip.com", "AuthLogin").target_login()
    ErpWithdrawManage(rss).withdraw_order_submit()