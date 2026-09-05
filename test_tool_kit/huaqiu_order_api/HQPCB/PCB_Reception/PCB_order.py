import json
import os
import re
import time
from urllib.parse import quote

import jsonpath
import yaml

from huaqiu_order_api.HQCHIP_Center.user_center import get_address, get_ic_userId, user_information, get_man, \
    get_invoice_msg
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import stockup_dir, smt_yansuo_dir, bom_dir, yaml_file, account_yaml


class PCBOrder:
    def __init__(self, rss, smt_order_id=None, dict_obj=None):
        """
        :param dict_obj 更新save_order_body的字典参数
        """
        self.rss = rss
        self.smt_order_id = smt_order_id
        token = getattr(Data, 'token')
        self.phone = getattr(Data, 'phone')
        self.headers = {"Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)",
                        "Authorization": token
                        }
        self.form_headers = {"Content-Type": "multipart/form-data"}
        self.urlencoded__headers = {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                  "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)",
                  "Authorization": token}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HQPCB_URL = data["HQPCB_URL"]
        self.invoice_need = account["HQCHIP_SMT"]["pcbaInvoiceNeed"]
        self.dict_obj = dict_obj

    def pcb_order_file(self):
        """文件"""
        pcb_order_file_url = "{}/upfile".format(self.HQPCB_URL)
        head = {"User-Agent": "HQPCB Crawler DFM Push Tools"}
        data = {'type': 'pcbfile'}
        fp = open(smt_yansuo_dir, 'rb')
        files = {'file': (os.path.basename(smt_yansuo_dir), fp)}
        pcb_order_file_url_res = self.rss.post(url=pcb_order_file_url, data=data, files=files,
                                               headers=head).json()
        return pcb_order_file_url_res['url']


    def pcb_tmp_save(self):
        """PCB需求保存"""
        save_order_url = "{}/quote/save".format(self.HQPCB_URL)
        save_order_body = {
                "type": 1,
                "board_type": "FR-4",
                "board_brand": "无要求",
                "file_type": -1,
                "blayer": 2,
                "board_tg": "",
                "units": 1,  # 1 = pcs, 2 = set
                "cross_board": 1,
                "pbnum": 1,
                "layouty": 1,
                "layoutx": 1,
                "bwidth": 12,
                "blength": 12,
                "bcount": 5,  # 板子数量
                "sidedirection": "无",
                "sidewidth": 0,
                "bheight": 1.6,
                "copper": 1,
                "insidecopper": 0,
                "lineweight": 6,
                "vias": 0.3,
                "color": "绿色",
                "charcolor": "白色",
                "cover": "过孔盖油",
                "via_in_pad": "无",
                "spray": "有铅喷锡",
                 "cjh": 1,
                "overlay": "[object Object]",
                "impendance": 0,
                "impendance_report": 0,
                "beveledge": 0,
                "bankong": 0,
                "baobian": 0,
                "blind": 0,
                "hdi_process_type": "",
                "test": "样品免费测试",
                "testpoint": 0,
                "produce_file": None,
                "invoice": "不需要",
                "price": "91",
                "report": "",
                "report_type": 0,
                "deltime": "正常72小时",
                "bga": 0,
                "zknum": 0,
                "insurance_type": 0,
                "insurance": "",
                "pressing": "",
                "pressing_computer_id": "",
                "province": 14,
                "city": 197,
                "express": 9,
                "note": "",
                "label_remark": "",
                "heat_factor": "1.0W",
                "stiffeners": "无",
                "coverlay": "黄色",
                "pcbfile": "",
                "quote_type": 2,
                "email": "",
                "setwidth": 0,
                "setlength": 0,
                "need_smd": 0,
                "is_need_smt": 1,
                "smd_quote_id": 0,
                "hq_pack": 1,
                "fhp": 0,
                "fhd_title": "",
                "has_period": 2,
                "period_format": 1,
                "sh": 1,
                "fh": 1,
                "review_file": 0,
                "quoteid": 0,
                "paper": 1,
                "user_stamp": 1,
                "deduct_type": 2,
                "deduct_limit": "",
                "site": "",
                "weight": 0.23,
                "m": 720,
                "source": "smtstep",
                "smt_order_id": self.smt_order_id}
        if self.dict_obj != None:
            if isinstance(self.dict_obj, dict):
                for v in save_order_body:
                    for k in self.dict_obj:
                        if k == v:
                            if k == "blayer":  # 判断key值是否为板子层数
                                # blayer_lst = ["4", "6", "8", "10", "12", "14", "16", "18", "20"]
                                if self.dict_obj[k] in ["4", "6", "8"]:
                                    # 根据板子层数替换TG值
                                    save_order_body[v] = self.dict_obj[k]
                                    save_order_body["board_tg"] = "TG150"
                                elif self.dict_obj[k] in ["10", "12", "14", "16", "18", "20"]:
                                    # 根据板子层数替换TG值
                                    save_order_body[v] = self.dict_obj[k]
                                    save_order_body["board_tg"] = "TG170"
                                else:
                                    save_order_body[v] = self.dict_obj[k]
                                    save_order_body["board_tg"] = ""
                                    # print(f"k为blayer，不满足板子层数要求")
                            else:
                                save_order_body[v] = self.dict_obj[k]
                        else:
                            print(f"dict_obj无对应更新字段，此时：k为{k}, v为{v}，dict_obj：{self.dict_obj}")
        save_order_res = self.rss.post(url=save_order_url, data=save_order_body, headers=self.urlencoded__headers)
        logger.info(save_order_res)
        self.pcb_tmp_id = jsonpath.jsonpath(save_order_res.json(), "$..id")[0]
        logger.info(f"获取到生成的需求id：{self.pcb_tmp_id}")
        return self
    def place_an_order(self):
        """pcb提交订单
        """
        place_an_order_url = "{}/account/online/save".format(self.HQPCB_URL)
        # 获取smt订单提交的pcb文件路径信息
        pcbfile_obtain_url = "{}/order/submit?quoteid={}".format(self.HQPCB_URL, self.pcb_tmp_id)
        pcbfile_obtain_res = self.rss.get(url=pcbfile_obtain_url, headers=self.headers).text
        place_an_order_body = json.loads(json.dumps(json.loads(
                                re.compile(r'var\s+quoteAllData\s*=\s*({[^;]+);').search(pcbfile_obtain_res).group(
                                    1)), ensure_ascii=False))
        # print(place_an_order_body)
        # 将extend层级剔除，extend里面的key与外部key相等时比较value值大小保留比较大的value，外部相同key的value为空是直接用extend里面的key的value
        # 获取 extend 字典
        extend_dict = place_an_order_body.pop('extend', {})

        for k, v in extend_dict.items():
            if k in place_an_order_body:
                if isinstance(place_an_order_body[k], (int, float)) and isinstance(v, (int, float)):
                    place_an_order_body[k] = max(place_an_order_body[k], v)
                elif isinstance(place_an_order_body[k], str) and place_an_order_body[k] == '':
                    place_an_order_body[k] = v
            else:
                place_an_order_body[k] = v
        # 获取下单人信息
        id, orderMan, orderTel = get_man(self.rss)
        place_an_order_body_replenish = {
                "quoteid": place_an_order_body['id'],
                "produce_file": 0,
                "stencil_note": "",
                "order_note": "",
                "heat_factor": "",
                "stiffeners": "",
                "solder": "绿油",
                "coverlay": "白色",
                "aid": "",
                "stencil_aid": 0,
                "shipping_id": 9,
                "stencil_express": "",
                "invoicetop": "",
                "taxnumber": "",
                "invoice_kind": 1,
                "fhp": 0,
                "fhd_title": "",
                "sh": 1,
                "fh": 1,
                "product_type": "",
                "eq_notice": 1,
                "engineer_id": 1,
                "laminatType": 2,
                "laminatTypeValue": "",
                "site_content": "",
                "period_format": 1,
                "expressStr": "德邦陆运寄付",
                "orderman_id": id,
                "orderman": orderMan,
                 "ordertel": orderTel,
                "isframe": 0,
                "overlay[email]": "",
                "overlay[contact]": "",
                "overlay[name]": ""}
        del place_an_order_body['id']
        if self.smt_order_id == None:
            pcfile = self.pcb_order_file()
            if place_an_order_body['pcbfile'] == '':
                # print(1111)
                place_an_order_body['pcbfile'] = pcfile
                username, phone, sso_uid, pcbuid = user_information(self.rss)
                address_id = get_address(self.rss)
                place_an_order_body_replenish["aid"] = address_id
                place_an_order_body_replenish["stencil_aid"] = address_id
        place_an_order_body.update(place_an_order_body_replenish)
        if self.invoice_need == "需要":  # 默认开启且发票为数电增票
            invoice_id, invoice_title, invoice_code = get_invoice_msg(self.rss, 1, 1)
            invoice = {"bill_id": invoice_id, "invoice": "增票全电", "invoicetop": invoice_title, "taxnumber": invoice_code}
            place_an_order_body.update(invoice)
        place_an_order_res = self.rss.post(url=place_an_order_url, data=place_an_order_body, headers=self.urlencoded__headers).text
        # print(place_an_order_res)
        try:  # 异常处理
            json_msg = re.search('<em class="cur">(.*?)</em>', place_an_order_res).group(1)
        except AttributeError:
            json_msg = re.search('<h3 class="ui-tipbox-title">(.*?)</h3>', place_an_order_res).group(1)
            print(json_msg)
            place_an_order_body["deltime"] = json_msg.split("交期数据不正确，应为")[1]
            place_an_order_res = self.rss.post(url=place_an_order_url, data=place_an_order_body, headers=self.urlencoded__headers).text
            json_msg = re.search('<em class="cur">(.*?)</em>', place_an_order_res).group(1)
        if "提交成功" == json_msg:
            orderId = re.search(r'"orderId"\s*:\s*"([^"]+)"', place_an_order_res).group(1)
            logger.info(f"订单生成成功，订单号: {orderId}")
            logger.debug('=*' * 50)
            # 将生成的pcb订单号往Data里面作虚拟存储以【pcb_order_id】命名以便后续提取
            setattr(Data, 'pcb_order_id', orderId)
            return orderId
    def run_pcb_order(self):
        """pcb订单生成
        """
        orderId = self.pcb_tmp_save().place_an_order()
        return orderId






if __name__ == '__main__':
    rss = SSO_Reception('https://uat-www.hqpcb.com').login()
    PCBOrder(rss).pcb_tmp_save().place_an_order()
    # PCBOrder(rss, 42911).pcb_order_file()