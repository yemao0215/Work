import json
import re
import time

import jsonpath
import yaml

from huaqiu_order_api.HQCHIP_Center.user_center import get_address, get_ic_userId, get_invoice, get_invoice_msg
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import stockup_dir, smt_yansuo_dir, bom_dir, yaml_file, account_yaml


class SmtOrder:
    def __init__(self, rss=None, pcb_bom_sn_dict=None):
        self.rss = rss
        token = getattr(Data, 'token', '')
        self.phone = getattr(Data, 'phone', '')
        self.headers = {"Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                        "Authorization": token
                        }
        self.form_headers = {"Content-Type": "multipart/form-data"}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)

        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.SMT_HQCHIP_URL = data["SMT_HQCHIP_URL"]
        self.application_sphere = account['HQCHIP_SMT']['application_sphere']
        self.is_pcb_soft_board = account['HQCHIP_SMT']['is_pcb_soft_board']
        self.single_or_double_technique = account["HQCHIP_SMT"]["single_or_double_technique"]
        self.pcb_ban_width = account["HQCHIP_SMT"]["pcb_ban_width"]
        self.pcb_ban_height = account["HQCHIP_SMT"]["pcb_ban_height"]
        self.number = account["HQCHIP_SMT"]["number"]
        self.bom_material_type_number = account["HQCHIP_SMT"]["bom_material_type_number"]
        self.splicing_number = account["HQCHIP_SMT"]["splicing_number"]
        self.bom_sn = account["HQCHIP_SMT"]["bom_sn"]
        self.bom_bind_type = account["HQCHIP_SMT"]["bom_bind_type"]
        self.pcb_sn = account["HQCHIP_SMT"]["pcb_sn"]
        self.pcb_bind_type = account["HQCHIP_SMT"]["pcb_bind_type"]
        self.invoice_need = account["HQCHIP_SMT"]["pcbaInvoiceNeed"]
        # self.buid_type_json = [{"buid_type": "0", "value": 2}, {"buid_type": "1", "value": 3}, {"buid_type": "2", "value": 1}]
        self.buid_type_json = {"0": {"Bom": 3, "Pcb": 2}, "1": {"Bom": 2, "Pcb": 3}, "2": {"Bom": 1, "Pcb": 1}}
        if pcb_bom_sn_dict != None and isinstance(pcb_bom_sn_dict, dict):
            if "bom_sn" in pcb_bom_sn_dict:
                self.bom_sn = pcb_bom_sn_dict["bom_sn"]
            if "pcb_sn" in pcb_bom_sn_dict:
                self.pcb_sn = pcb_bom_sn_dict["pcb_sn"]



    def smt_order_file(self, file_type, smt_order_file_dir): #, file_type, smt_order_file_dir
        """文件"""
        smt_order_file_url = "{}/ajax/jsupsmtfile".format(self.SMT_HQCHIP_URL)
        file_name = smt_order_file_dir.split("/")[-1]
        logger.info(file_name)
        file = [('file', (file_name, open(smt_order_file_dir, 'rb'),
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
        file_type_body = {"file_type": file_type}
        smt_order_file_url_res = self.rss.post(url=smt_order_file_url, data=file_type_body, files=file).json()
        # logger.info(smt_order_file_url_res)
        file_server_url = smt_order_file_url_res["img"]
        # old_filename = smt_order_file_url_res["old_filename"]
        # logger.info(file_server_url)
        # logger.info(old_filename)
        return file_server_url

    def smt_tmp_save(self):
        """需求单保存"""
        save_order_url = "{}/smtservice/app/v2/smtTmp/saveSmtTmpOrder".format(self.SMT_HQCHIP_URL)
        save_order_body = {
            "add_user": "",
            "add_user_email": "",
            "add_user_qq": "",
            "add_user_tel": "",
            "address_id": 0,
            "agreen_protocol": False,
            "application_sphere": self.application_sphere,
            "assembly_production": 0,
            "bom_file":"",
            "bom_id": 0,
            "bom_material_type_number": self.bom_material_type_number,
            "bom_order_amount":0,
            "bom_purchase": 0,
            "bom_sn": "",
            "city_id": "77",
            "custom_pcb_ban": 0,
            "estimate_deliver": 36,
            "expressage": 0,
            "fixture_num_total": "",
            "gain_order_type": 0,
            "goods_name": "",
            "invoicefee": 0,
            "is_accurate_price_type": 1,
            "is_assemble": 0,
            "is_assembly_weld": 0,
            "is_dodge_solder_joint": False,
            "is_first_confirm": 0,
            "is_increase_tinning": 0,
            "is_layout_cleaning": 0,
            "is_material_baking": 0,
            "is_pcb_soft_board": self.is_pcb_soft_board,
            "is_plug": 1,
            "is_program_burning": 0,
            "is_steel_follow_delivery": 0,
            "is_test": 0,
            "is_welding_wire": 0,
            "need_conformal_coating": 0,
            "need_gangwang": 1,
            "need_split": 0,
            "number": self.number,
            "old_bom_file": [],
            "old_patch_file": [],
            "old_pcb_file": [],
            "order_id": 0,
            "packing_type":1 ,
            "patch_file": "",
            "patch_pad_number": "1",
            "pcb_ban_height": self.pcb_ban_height,
            "pcb_ban_width": self.pcb_ban_width,
            "pcb_file": "",
            "pcb_order_amount": 0,
            "pcb_send_smt": 1,
            "pcb_sn": "",
            "plug_number": "1",
            "postscript": "",
            "province_id": "6",
            "remark": "",
            "save_type": 1,
            "shipping_id": 1,
            "shipping_pay_type": 1,
            "sidewidth": False,
            "single_or_double_technique": self.single_or_double_technique,
            "smd_order_id": 0,
            "splicing_number": self.splicing_number,
            "steel_type": 0,
            "tax_id": 0,
            "tmp_hash": "",
            "vat_type": 0,
            "weight": ""
        }
        save_order_res = self.rss.post(url=save_order_url, json=save_order_body, headers=self.headers).json()
        logger.info(save_order_res)
        self.smt_tmp_id = save_order_res["body"]["smt_tmp_id"]
        # 接口：/smtservice/app/v2/smtTmp/saveSmtTmpOrder，返回响应报文体变更 删除代码---2023/07/28
        # self.user_id = save_order_res["body"]["user_id"]
        logger.info(f"获取到生成的需求id：{self.smt_tmp_id}")
        return self

    def build_value_search(self, build_type, build_value_name):
        """绑定类型查找"""
        # 初始化变量，用于存储找到的值
        build_value = None
        # 遍历每个字典
        for key, item in self.buid_type_json.items():
            if key == build_type:
                for k, v in item.items():
                    if k == build_value_name:
                        build_value = v
                        # 找到后退出循环
                        break
                break
        return build_value

    def smt_build_order_search(self, order_type, order_sn):
        """关联单号查询"""
        type = order_type.title()
        search_url = "{}/smtservice/app/buildOrder/".format(self.SMT_HQCHIP_URL)
        search_body = {"page_num": 1, "page_size": 10}
        if type == "Bom":
            url_tpye = "get" + type + "Page"
            search_url = "{}/smtservice/app/buildOrder/{}".format(self.SMT_HQCHIP_URL, url_tpye)
            search_body["order_sn_key"] = order_sn
        elif type == "Pcb":
            url_tpye = "get" + order_type.title() + "Page"
            search_url = "{}/smtservice/app/buildOrder/{}".format(self.SMT_HQCHIP_URL, url_tpye)
            search_body["order_id"] = order_sn
            search_body["is_pcb_soft_board"] = 0
        search_res = self.rss.post(url=search_url, json=search_body, headers=self.headers).json()
        if search_res["body"]["list"] != []:
            return search_res["body"]["list"]
    def place_an_order(self):
        logger.info(f"开始检查收货地址")
        address_id = get_address(self.rss)
        logger.info(f"拿到收货地址id: {address_id}")
        self.user_id = get_ic_userId(self.rss)
        logger.info(f"获取到当前账号的芯城用户user_id: {self.user_id}")
        pcb_file = self.smt_order_file("pcb", smt_yansuo_dir)
        bom_file = self.smt_order_file("bom", bom_dir)
        smt_file = self.smt_order_file("patch", smt_yansuo_dir)
        bom_purchase = self.build_value_search(self.bom_bind_type, "Bom")
        custom_pcb_ban = self.build_value_search(self.pcb_bind_type, "Pcb")
        bom_file_name = bom_file.split("/")[-1]
        bom_id = ''
        if self.bom_bind_type == '0':
            bom_search_body = self.smt_build_order_search('bom', self.bom_sn)
            for i in range(len(bom_search_body)):
                bom_file = bom_search_body[i]["file_url"]
                bom_id = bom_search_body[i]["id"]
                bom_file_name = bom_file_name.split("=")[-1]
        if self.pcb_bind_type == '0':
            pcb_search_body = self.smt_build_order_search('pcb', self.pcb_sn)
            for i in range(len(pcb_search_body)):
                pcb_file = pcb_search_body[i]["pcbfile"]
        add_user_email = str(self.phone) + "@163.com"
        place_an_url = "{}/online/finish_new".format(self.SMT_HQCHIP_URL)
        place_an_body = {
            "is_first_confirm": 0,
            "shipping_id": 1,
            "add_user_email": add_user_email,
            "test_duration": 0,
            "adjust_fee": 0,
            "is_dodge_solder_joint": False,
            "custom_pcb_ban": custom_pcb_ban,
            "bom_material_type_number": self.bom_material_type_number,
            "bom_order_amount": 0,
            "is_program_burning": 0,
            "patch_file": smt_file,
            "is_material_baking": 0,
            "number": self.number,
            "gain_order_type": 0,
            "is_assembly_weld": 0,
            "pcb_send_smt": 1,
            "is_plug": 1,
            "splicing_number": self.splicing_number,
            "is_test": 0,
            "old_patch_file": "",
            "bom_purchase": bom_purchase,
            "add_plat_form": 1,
            "goods_name": "自动化测试",
            "is_pcb_ban": 0,
            "pcb_file_name": pcb_file.split('/')[-1],
            "address_id": address_id,
            "is_handwork_plug": 0,
            "plug_number": 1,
            "is_assemble": 0,
            "weight": "",
            "is_pcb_soft_board": self.is_pcb_soft_board,
            "add_user_qq": "",
            "single_or_double_technique": self.single_or_double_technique,
            "jiaji_price": 0,
            "tax_id": "",
            "tmp_hash": "",
            "bom_sn": self.bom_sn,
            "tmp_status": 0,
            "pcb_sn_file": "",
            "user_id": self.user_id,
            "pcb_ban_width": self.pcb_ban_width,
            "old_bom_file":"",
            "patch_pad_number": 1,
            "order_id": 0,
            "application_sphere": self.application_sphere,
            "is_welding_wire": 0,
            "city_id": 77,
            "need_gangwang": 1,
            "save_type": 1,
            "is_steel_follow_delivery": 0,
            "postscript":"",
            "steel_type": 0,
            "jiaji": 0,
            "need_split": 0,
            "is_accurate_price_type": 1,
            "remark": "",
            "shipping_pay_type": 1,
            "invoicefee": 0,
            "old_pcb_file":"",
            "packing_type": 1,
            "pcb_ban_height": self.pcb_ban_height,
            "need_conformal_coating": 0,
            "pcb_width": 0,
            "smd_order_id": 0,
            "add_user_tel": self.phone,
            "x_ray_number": 0,
            "x_ray_unit_number": 0,
            "pcb_file": pcb_file,
            "pcb_height": 0,
            "estimate_deliver": 36,
            "bom_file": bom_file,
            "assembly_production": 0,
            "is_shipping_fee": 0,
            "sidewidth": False,
            "bom_id": bom_id,
            "agreen_protocol": True,
            "expressage": 0,
            "province_id": 6,
            "smt_tmp_id": self.smt_tmp_id,
            "bom_file_name": bom_file_name,
            "pcb_sn_file_name": "",
            "is_layout_cleaning": 0,
            "vat_type": 3,
            "patch_file_name": smt_file.split('/')[-1],
            "add_user": "自动化测试",
            "is_increase_tinning": 0,
            "inv_title": "undefined",
            "shipping_name": "顺丰寄付",
            "consignee_phone": self.phone,
            "pcb_sn": self.pcb_sn
        }
        if self.invoice_need == "需要":  # 默认开启且发票为数电增票
            invoice_id, invoice_title, invoice_code = get_invoice_msg(self.rss, 1, 1)
            invoice = {"tax_id": invoice_id, "inv_title": invoice_title, "vat_type": 4}
            place_an_body.update(invoice)
        # print(place_an_body)
        # print(json.dumps(place_an_body, ensure_ascii=False).replace("'", '"'))
        time.sleep(10)
        save_order_res = self.rss.post(url=place_an_url, data=place_an_body).json()
        # logger.info(save_order_res)
        msg = save_order_res["msg"]
        # order_sn = ""
        if msg == "提交订单成功":

            smt_order_sn = jsonpath.jsonpath(save_order_res, "$..order_sn")[0]
            order_id = jsonpath.jsonpath(save_order_res, "$..order_id")[0]
            logger.info(f"订单生成成功，订单编号: {smt_order_sn}")
            logger.debug('=*' * 50)
            # 将生成的SMT订单号往Data里面作虚拟存储以【smt_order_sn】命名以便后续提取
            setattr(Data, 'smt_order_sn', smt_order_sn)
            setattr(Data, 'smt_order_id', order_id)
            bom_order_search_url = "{}/online/topayinfoshow.html?o={}".format(self.SMT_HQCHIP_URL, order_id)
            bom_order_search_res = self.rss.post(url=bom_order_search_url, headers=self.headers).text
            bom_order_sn = None
            bom_purchase = self.build_value_search(self.bom_bind_type, "Bom")
            if bom_purchase == 3:
                pass
            else:
                # 正则表达式分别匹配BOM订单号和详情页中的ID
                pattern_bom_order_sn = r'BK\d+'
                pattern_bom_order_id = r'detail\?id=(\d+)'

                # 查找BOM订单号
                bom_order_match = re.search(pattern_bom_order_sn, bom_order_search_res)
                if bom_order_match:
                    bom_order_sn = bom_order_match.group()
                else:
                    bom_order_sn = "未找到"

                # 查找详情页ID
                detail_id_match = re.search(pattern_bom_order_id, bom_order_search_res)
                if detail_id_match:
                    bom_order_id = detail_id_match.group(1)
                else:
                    bom_order_id = "未找到"

                print("BOM订单号:", bom_order_sn)
                print("详情页ID:", bom_order_id)
                setattr(Data, 'bom_order_sn', bom_order_sn)
            return smt_order_sn, bom_order_sn
    def mian_smt_order(self, bom_pcb_bind_type_json=None):
        # 读取 YAML 文件
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        # 更新字段
        if 'HQCHIP_SMT' in data:
            data['HQCHIP_SMT']['bom_bind_type'] = '1'  # 将 '新的值' 替换为你想要的值
            data['HQCHIP_SMT']['pcb_bind_type'] = '1'  # 将 '新的值' 替换为你想要的值
        if isinstance(bom_pcb_bind_type_json, dict):
            if 'bom_bind_type' in bom_pcb_bind_type_json:
                data['HQCHIP_SMT']['bom_bind_type'] = bom_pcb_bind_type_json['bom_bind_type']
            if 'pcb_bind_type' in bom_pcb_bind_type_json:
                data['HQCHIP_SMT']['pcb_bind_type'] = bom_pcb_bind_type_json['pcb_bind_type']
            # 将更新后的数据写回 YAML 文件
        with open(account_yaml, 'w') as file:
            yaml.safe_dump(data, file, default_flow_style=False, allow_unicode=True)
        rss = SSO_Reception('https://uat-smt.hqchip.com').login()
        smt_order_sn, bom_order_sn = SmtOrder(rss).smt_tmp_save().place_an_order()
        print({"smt_order_sn": smt_order_sn, "bom_order_sn": bom_order_sn,
               "msg": "SMT订单生成成功"})
        return rss, smt_order_sn, bom_order_sn

if __name__ == '__main__':
    rss = SSO_Reception('https://uat-smt.hqchip.com').login()
    SmtOrder(rss).smt_tmp_save().place_an_order()
    # user_id = get_ic_userId(rss)
    # print(user_id)
    # # address_id = get_address(rss, 15912757721)