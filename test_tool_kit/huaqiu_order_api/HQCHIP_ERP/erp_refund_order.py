import json
import re
import yaml
from bs4 import BeautifulSoup

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class ErpRefundOrder:


    def __init__(self, rss):
        """
        :param account:  登录ERP账号
        :param psw:  登录ERP密码
        :param refund_order:  退款编号
        :param uesr:    前台商城生成订单编号的用户名称
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']
        # self.refund_order = getattr(Data, 'refund_sn')
        self.refund_order = "FJ026109"
        self.rss = rss
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }


    def refund_order_search(self):
        """退款订单查询"""
        search_url = "{}/OrderRefund/index".format(self.ERP_URL)
        search_body = {"keytype": "order_refund_sn", "keyword": self.refund_order, "affi_group_id": -1, "affi_uid": -1,
                       "returned_amount_type": "eq"}
        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers, timeout=1000).text  # 搜索订单，获取order_id
        self.order_id = re.search('(<a href="/OrderRefund/detail\?id=)([0-9]*)', search_res).group(2)
        logger.info(f"搜索完成,获取到order_id: {self.order_id}")
        return self

    def refund_order_detail(self):
        """退款订单详情"""
        refund_order_detail_url = "{}/OrderRefund/detail?id={}".format(self.ERP_URL, self.order_id)
        refund_order_detail_res = self.rss.post(url=refund_order_detail_url).text
        salesman = re.search('(<label>销售人员：</label>\s*<span>(.*?)</span>)', refund_order_detail_res).group(2)
        applicant = re.search('(<label>申请人：</label>\s*<span>(.*?)</span>)', refund_order_detail_res).group(2)
        if salesman == applicant:
            reslt = True
            print("销售人员和申请人一致")
        else:
            reslt = False
            print("销售人员和申请人不一致")
        return reslt

    def refund_order_verify(self):
        """退款单确认"""
        refund_order_depart_url = "{}/OrderRefund/confirm/id/{}/navTabId/OrderRefundDetail".format(self.ERP_URL, self.order_id)
        refund_order_depart_res = self.rss.get(url=refund_order_depart_url).text
        depart_id = re.search('(<input required type="radio" name="sale_org_id" value=")([0-9]*)', refund_order_depart_res).group(2)

        refund_order_confirm_url = "{}/OrderRefund/confirm/id/{}/navTabId/OrderRefundDetail".format(self.ERP_URL, self.order_id)
        refund_order_confirm_dody = {"sale_org_id": depart_id, "ajax": 1, "is_iframe": 1}
        refund_order_confirm_res = self.rss.post(url=refund_order_confirm_url, data=refund_order_confirm_dody).text
        # 正则表达式匹配"var response = "的结果提取的字符串转换为JSON格式，并且避免中文乱码
        refund_order_confirm_json = json.loads(json.dumps(json.loads(re.compile(r'var\s+response\s*=\s*({[^;]+);').search(refund_order_confirm_res).group(1)), ensure_ascii=False))
        if refund_order_confirm_json["info"] == "提交确认操作成功!":
            print(f"退款单：{self.refund_order}，确认成功")
        elif refund_order_confirm_json["info"] == "提交确认失败;开户行省份地址不能为空!":
            pass

        return self
    def refund_order_audit(self):
        n = 0
        while True:
            try:
                audit_search_url = "{}/OrderRefundAudit/index".format(self.ERP_URL)
                audit_search_body = {"search_key": "orae.order_refund_sn", "search_value": self.refund_order}
                audit_search_res = self.rss.post(url=audit_search_url, data=audit_search_body, headers=self.headers).text
                # 获取页面列表表格关键字段
                soup = BeautifulSoup(audit_search_res, 'html.parser')
                table = soup.find('tbody')
                rows = table.find_all('tr')
                audit_id_column = []
                audit_status_column = []
                # for row in rows[1:]: # 跳过表头
                for row in rows:  # 不跳过表头
                    cells = row.find_all('td')
                    audit_id_column.append(cells[0].text)
                    audit_status_column.append(cells[12].text)
                audit_id_status_dict = dict(zip(audit_id_column, audit_status_column))
                found = False
                for key in audit_id_status_dict:
                    if audit_id_status_dict[key] == "已通过":
                        print("已审核")
                        found = True
                        break
                if not found:
                    for key in audit_id_status_dict:
                        if audit_id_status_dict[key] == "审核中":
                            refund_order_audit_url = "{}/OrderRefundAudit/audit/navTabId/OrderRefundAuditAudit".format(self.ERP_URL)
                            refund_order_audit_body = {"id": key, "last_audit_user": 1, "checked": 1, "msg": "同意", "ajax": 1, "is_iframe": 1}
                            refund_order_audit_res = self.rss.post(url=refund_order_audit_url, data=refund_order_audit_body).text
                            refund_order_audit_json = json.loads(json.dumps(json.loads(
                                re.compile(r'var\s+response\s*=\s*({[^;]+);').search(refund_order_audit_res).group(
                                    1)), ensure_ascii=False))
                            if refund_order_audit_json["info"] == "审核成功":
                                print(f"退款单：{self.refund_order}，审核成功")
                            break
                if found:  # 如果已通过，则跳出循环
                    break
            except:
                n += 1
                if n > 6:
                    break
        return self

    def refund_order_teller_confirm(self):
        """出纳确认"""





    def mian_refund_order(self):
        self.refund_order_search()
        reslt = self.refund_order_detail()
        if reslt == True:
            self.refund_order_verify()
            self.refund_order_audit()



if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    rss = SOOLogin(system_name="erp").target_login()
    ErpRefundOrder(rss).mian_refund_order()