import re
import time
import urllib.parse
import requests
import yaml
from datetime import datetime

from bs4 import BeautifulSoup
from faker import Faker

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import smt_order_bom_import_dir, yaml_file, smt_yansuo_dir
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import smt_order_bom_import_dir, yaml_file, account_yaml



class ErpSmtOrderCancellation:


    def __init__(self, rss=None, order_sn=None):
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
        self.factory_updata = account["HQCHIP_ERP"]["factory_updata"]
        # 从Data里面拿去smt订单号
        self.order_sn = getattr(Data, 'smt_order_sn', '')
        if self.order_sn == '' and order_sn!= None:
            self.order_sn = order_sn
        self.rss = rss
        self.login_url = '{}/public/checkLogin/'.format(self.ERP_URL)
        # self.body = {'account': self.account, 'password': self.password}
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.form_headers = {'Content-Type': 'multipart/form-data',
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    def erp_smt_order_cancellation(self):
        """smt订单处理"""
        search_url = '{}/SmtOrder'.format(self.ERP_URL)
        search_body = {'type': '1', 'content': self.order_sn, 'add_time1': str((datetime.now()).year) + "-01-01"}
        print(search_body)
        logger.info(f"搜索订单编号: {self.order_sn}")
        search_res = self.rss.post(url=search_url, data=search_body, headers=self.headers, timeout=1000).text  # 搜索订单，获取order_id
        # logger.info(search_res)
        self.order_id = re.search('(<a href="/SmtOrder/detail/order_id/)([0-9]*)', search_res).group(2)
        logger.info(f"搜索完成,获取到order_id: {self.order_id}")
        setattr(Data, 'smt_erp_order_id', self.order_id)

        # 设置客服
        set_affi_url = '{}/SmtOrder/setAffi/navTabId/SmtOrder'.format(self.ERP_URL)
        set_affi_body = {"ids": self.order_id, "affi_uid": 772, "ajax": 1, "is_iframe": 1}
        logger.info(f"开始设置订单编号: {self.order_sn}的销售客服为贺鹏")
        set_affi_res = self.rss.post(url=set_affi_url, data=set_affi_body, headers=self.headers,timeout=1000).json()
        logger.info(set_affi_res)

        # 设置销售员
        set_sale_url = '{}/SmtOrder/setSale/navTabId/SmtOrder'.format(self.ERP_URL)
        set_sale_body = {"ids": self.order_id, "sale_uid": 772, "ajax": 1, "is_iframe": 1}
        logger.info(f"开始设置订单编号: {self.order_sn}的销售员为贺鹏")
        set_sale_res = self.rss.post(url=set_sale_url, data=set_sale_body, headers=self.headers,timeout=1000).json()
        logger.info(set_sale_res)

        # 设置SMT生产跟单
        set_product_affi_url = '{}/SmtOrder/setproductAffi/navTabId/SmtOrder'.format(self.ERP_URL)
        set_product_affi_body = {"ids": self.order_id, "product_affi_uid": 475, "ajax": 1, "is_iframe": 1}
        logger.info(f"开始设置订单编号: {self.order_sn}的SMT生产跟单为陈凯丽")
        set_product_affi_res = self.rss.post(url=set_product_affi_url, data=set_product_affi_body, headers=self.headers,timeout=1000).json()
        logger.info(set_product_affi_res)

        # 设置BOM工程师
        set_bom_engineer_url = '{}/SmtOrder/setBomEngineerUid/navTabId/SmtOrder'.format(self.ERP_URL)
        set_bom_engineer_body = {"ids": self.order_id, "bom_engineer_uid": 65535, "ajax": 1, "is_iframe": 1}
        logger.info(f"开始设置订单编号: {self.order_sn}的BOM工程师为adss")
        set_bom_engineer_res = self.rss.post(url=set_bom_engineer_url, data=set_bom_engineer_body, headers=self.headers,timeout=1000).json()
        logger.info(set_bom_engineer_res)

        # 设置SMT报价工程师
        set_checker_url = '{}/SmtOrder/setCheckerUid/navTabId/SmtOrder'.format(self.ERP_URL)
        set_checker_body = {"ids": self.order_id, "bom_engineer_uid": 205, "ajax": 1, "is_iframe": 1}
        logger.info(f"开始设置订单编号: {self.order_sn}的SMT报价工程师为蒋霄")
        set_checker_res = self.rss.post(url=set_checker_url, data=set_checker_body, headers=self.headers,timeout=1000).json()
        logger.info(set_checker_res)

        # 设置SMT工艺工程师
        set_technics_url = '{}/SmtOrder/setTechnicsUid/navTabId/SmtOrder'.format(self.ERP_URL)
        set_technics_body = {"ids": self.order_id, "technics_uid": 1, "ajax": 1, "is_iframe": 1}
        logger.info(f"开始设置订单编号: {self.order_sn}的SMT工艺工程师为超级管理员")
        set_technics_res = self.rss.post(url=set_technics_url, data=set_technics_body, headers=self.headers,timeout=1000).json()
        logger.info(set_technics_res)


        if self.factory_updata == 1:
            logger.info(f"更改工厂，模拟走老mes流程")
            self.erp_smt_order_factory_updata()

        # 检索是否项目订单，若存在关联PCB订单则为项目订单
        basicInfo_url= "{}/SmtOrder/basicInfo?smt_order_id={}".format(self.ERP_URL, self.order_id)
        basicInfo_res = self.rss.get(url=basicInfo_url, headers=self.headers, timeout=1000).text
        match = re.compile(r'PCB订单:').search(basicInfo_res)
        if match:
            order_type_msg = True
        else:
            order_type_msg = False
        # 修改信息
        edit_url = "{}/SmtOrder/editPrice/navTabId/SmtOrderEdit".format(self.ERP_URL)
        edit_body = {
            "order[smt_order_id]": self.order_id,
            "params[is_erp_modify][value]": 1,
            "params[number][value]": 4,
            "params[pcb_width][value]": 0,
            "params[pcb_height][value]": 0,
            "params[is_pcb_ban][value]": 0,
            "params[craft_border][value]": 0,
            "params[pcb_ban_x][value]": 1,
            "params[pcb_ban_y][value]": 1,
            "params[pcb_ban_width][value]": 12,
            "params[pcb_ban_height][value]": 12,
            "params[splicing_number][value]": 1,
            "params[is_pcb_soft_board][value]": 0,
            "params[patch_mode][value]": 1,
            "params[single_or_double_technique][value]": 1,
            "params[bom_material_type_number][value]": 1,
            "params[patch_material_type][value]": 0,
            "params[patch_pad_number][value]": 1,
            "params[is_special_ic][value]": 0,
            "params[custom_type][value]": 0,
            "params[steel_type][value]": 0,
            "params[is_steel_follow_delivery][value]": 0,
            "params[patch_fixture_num][value]": 0,
            "params[use_old_fixture][value]": 0,
            "params[use_old_fixture_num][value]": 0,
            "params[is_plug][value]": 1,
            "params[plug_material_type][value]": 1,
            "params[plug_number][value]": 1,
            "params[is_handwork_plug][value]": 0,
            "params[fixture_num_total][value]": 0,
            "params[pcb_soft_board_num][value]": 0,
            "params[split_board_fixture_num][value]": 0,
            "params[crimping_fixture_num][value]": 0,
            "params[x_ray_number][value]": 0,
            "params[x_ray_unit_number][value]": 0,
            "params[need_split][value]": 0,
            "params[need_conformal_coating][value]": 0,
            "params[is_dodge_solder_joint][value]": 0,
            "params[is_assembly_weld][value]": 0,
            "params[is_welding_wire][value]": 0,
            "params[is_assemble][value]": 0,
            "params[is_layout_cleaning][value]": 0,
            "params[solder_paste_type][value]": 1,
            "params[is_material_baking][value]": 0,
            "params[is_increase_tinning][value]": 0,
            "params[assembly_production][value]": 0,
            "params[application_sphere][value]": 1,
            "params[packing_type][value]": 1,
            "params[gain_order_type][value]": 0,
            "params[express][value]": 1,
            "params[express_type][value]": 1,
            "order[gain_name]": "",
            "order[gain_mobile]": "",
            "params[is_test][value]": 0,
            "params[test_duration][value]": 0,
            "params[is_program_burning][value]": 0,
            "params[program_burning_duration][value]": 0,
            "params[is_first_confirm][value]": 0,
            "params[estimate_deliver][value]": 36,
            "params[is_complete_deliver][value]": 1,
            "params[postscript][value]": "",
            "order[remark]": "",
            "params[assembly_weld_fee][value]": 0,
            "params[welding_wire_price][value]": 0,
            "params[assemble_price][value]": 0,
            "params[material_baking_fee][value]": 0,
            "params[not_assembly_production_fee][value]": "",
            "params[jiaji][value]": 0,
            "params[jiaji_price][value]": 0,
            "params[patch_fixture_fee][value]": 0.00,
            "params[pcb_soft_board_fixture_fee][value]": 0.00,
            "params[split_board_fixture_fee][value]": 0.00,
            "params[crimping_fixture_fee][value]": 0.00,
            "params[increase_tinning_fee][value]": 0,
            "order[price_29]": 0.00,
            "params[adjust_remark][value]": "",
            "params[commission_price][value]": 0.00,
            "params[hardware_adjust_price][value]": 0.00,
            "params[other_price][value]": 0.00,
            "params[smt_order_fee_do_or_not_plug][value]": 0,
            "params[not_in_active][value]": 0,
            "ajax": 1,
            "is_iframe": 1
        }
        if order_type_msg == True:
            edit_body["params[bheight][value]"] = 1.60
        edit_res = self.rss.post(url=edit_url, data=edit_body).json()
        logger.info(edit_res)

        # 确认订单
        confirm_url = "{}/SmtOrder/confirm/navTabId/SmtOrderEdit".format(self.ERP_URL)
        confirm_body = {"id": self.order_id, "act": "smt", "remark": "自动化测试验证", "ajax": 1, "is_iframe": 1}
        confirm_res = self.rss.post(url=confirm_url, data=confirm_body).json()
        logger.info(confirm_res)
        # 工艺审核
        self.smt_technics_audit()

        # 审核
        save_check_url = "{}/SmtOrder/saveCheck/navTabId/SmtOrderEdit".format(self.ERP_URL)
        save_check_body = {"order[smt_order_id]": self.order_id, "act": "smt", "order[is_project_order]": 0, "ajax": 1, "is_iframe": 1,
                           "order[referer_sn]": "", "order[status]": 2, "order[audit_msg]": "", "order[application_sphere]": 1
                           }
        save_check_res = self.rss.post(url=save_check_url, data=save_check_body).json()
        logger.info(save_check_res)
        # 钢网文件和工艺文件上传
        smtInfo_url= "{}/SmtOrder/smtInfo?smt_order_id={}&act=smt".format(self.ERP_URL, self.order_id)
        basicInfo_res = self.rss.get(url=smtInfo_url, headers=self.headers, timeout=1000).text
        match_btt_gw = re.compile(r'钢网文件上传').search(basicInfo_res)
        if match_btt_gw:
            logger.info(f"开始设置订单编号: {self.order_sn}的钢网文件上传")
            self.smt_order_file("product_pcb_sn", smt_yansuo_dir)


        # 进入详情页
        order_details_url = '{}/SmtOrder/basicInfo?smt_order_id={}'.format(self.ERP_URL, self.order_id)
        logger.info(f"进入订单明细列表")
        order_detail_res = self.rss.get(url=order_details_url, headers=self.headers).text  # 获取订单明细id
        # logger.info(order_detail_res)

        # print(re.compile(r'<label>收款单:</label>\s*<a[^>]*>[^<]*</a>\s*<span class="info">\((.*?)\)</span>', re.DOTALL).search(order_detail_res))
        match_receipt = re.compile(r'<label>收款单:</label>\s*<a[^>]*>[^<]*</a>\s*<span class="info">\((.*?)\)</span>', re.DOTALL).search(order_detail_res).group(1)
        logger.info(f"订单明细获取完成，拿到收款单状态: {match_receipt}")
        if match_receipt == "待付款":
            receipt_sn = re.search('(<a href="/SmtOrderRecivePay/index/recive_pay_sn/)(SK[0-9]*)', order_detail_res).group(2)
            logger.info(f"订单明细获取完成，拿到收款单号: {receipt_sn}")

            # 收款单操作
            recive_pay_url = "{}/SmtOrderRecivePay".format(self.ERP_URL)
            recive_pay_body = {"recive_pay_sn": receipt_sn, "sn_type": "", "order_sn": "", "pageNum": 1, "status": "", "create_time1": "", "create_time2": ""}
            recive_pay_res = self.rss.post(url=recive_pay_url, data=recive_pay_body).text
            # logger.info(recive_pay_res)
            receipt_id = re.search('(<a href="/SmtOrderRecivePay/loginfo/id/)([0-9]*)', recive_pay_res).group(2)
            logger.info(f"订单明细获取完成，拿到收款单id: {receipt_id}")

            # 核销
            batch_analytic_url = "{}/SmtOrderRecivePay/batch_analytic/navTabId/SmtOrderRecivePay/ids/{}".format(self.ERP_URL, receipt_id)
            batch_analytic_res = self.rss.get(url=batch_analytic_url).text
            # logger.info(batch_analytic_res)
            total_fee = batch_analytic_res.split('<input type="hidden" class="order_money" value="')[1].split('"/>\r\n')[0]
            logger.info(f"订单明细获取完成，拿到收款单待付款金额: {total_fee}")
            write_off_url = "{}/SmtOrderRecivePay/update/navTabId/SmtOrderRecivePay".format(self.ERP_URL)
            write_off_body = {"order[recive_pay_id]": receipt_id, f"order[{receipt_id}][smt_order_id]": self.order_id, "order[pay_money]": total_fee,
                              "order[confirm]": 1, "order[remark]": "自动化测试验证", "ajax": 1, "is_iframe": 1}
            # logger.info(write_off_body)
            write_off_res = self.rss.post(url=write_off_url, data=write_off_body).json()
            info = write_off_res["info"]
            result_receipt = f"{receipt_id}" in info
            if result_receipt == True:
                logger.info(f"收款单号: {receipt_sn}核销成功")
                # 生产文件确认-PCB文件
                self.smt_order_detail_file_confirm(self.order_id, "pcb")
                # 生产文件确认-smt文件
                self.smt_order_detail_file_confirm(self.order_id, "patch")
                # 生产文件确认-钢网文件
                self.smt_order_detail_file_confirm(self.order_id, "pcb_sn")
                # 生产文件上传-工艺文件
                self.smt_order_file("product_technology", smt_order_bom_import_dir)
                # 生产文件确认-工艺文件
                self.smt_order_detail_file_confirm(self.order_id, "technology")

        # 导入bom文件
        smt_order_bomifo_url = "{}/SmtOrder/bomInfo?smt_order_id={}&act=bom".format(self.ERP_URL, self.order_id)
        smt_order_bomifo_res = self.rss.get(url=smt_order_bomifo_url).text
        try:
            product_bom_id = re.search('(<a class="edit" href="/SmtOrder/bomAddItems/product_bom_id/)([0-9]*)', smt_order_bomifo_res).group(2)
        except:
            product_bom_id = re.search('(<a class="edit" href="/SmtOrder/exportProductBom/product_bom_id/)([0-9]*)', smt_order_bomifo_res).group(2)
        logger.info(f"获取到product_bom_id：{product_bom_id}")


        forwardUrl = self.smt_order_file("bom", smt_order_bom_import_dir, product_bom_id)
        content = forwardUrl.split("&")[2].split('=')[1]
        # python urlencode 解码 成 字符串
        content = urllib.parse.unquote(content)
        logger.info(f"urlencode解码生成的content为{content}")
        import_bom_file_confirm_url = "{}/SmtOrder/importProductBomStep2/navTabId/SmtOrderEdit".format(self.ERP_URL)
        import_bom_file_confirm_body = {
                                        "id": product_bom_id,
                                        "source_type": 2,
                                        "content": content,
                                        "match[0]": "customer_goods_name",
                                        "match[1]": "goods_name",
                                        "match[2]": "brand_name",
                                        "match[3]": "dosage",
                                        "match[4]": "proc_number",
                                        "match[5]": "encap",
                                        "match[6]": "goods_desc",
                                        "match[7]": "cat_name",
                                        "match[8]": "bit_number",
                                        "match[9]": "remark",
                                        "ajax": 1,
                                        "is_iframe": 1
                                        }
        import_bom_file_confirm_res = self.rss.post(url=import_bom_file_confirm_url, data=import_bom_file_confirm_body).json()
        info = import_bom_file_confirm_res["info"]
        if info == "保存成功":
            logger.info("上传BOM文件成功")

        bom_audit_submit_url = "{}/SmtOrder/bomApplyAudit/smt_order_id/{}/navTabId/SmtOrderEdit".format(self.ERP_URL, self.order_id)
        bom_audit_submit_res = self.rss.post(url=bom_audit_submit_url, headers=self.headers).text
        logger.info(f"提交bom审核结果：成功")
        # logger.info(f"提交bom审核结果：{bom_audit_submit_res}")
        logger.debug('=*' * 50)
        return self

    def erp_smt_order_factory_updata(self):

        # 反确认委外
        cancel_audit_factory_url = "{}/SmtOrder/cancelAuditFactory".format(self.ERP_URL)
        cancel_audit_factory_body = {"smt_order_ids": self.order_id, "remark": "测试订单", "ajax": 1, "is_iframe": 1}
        cancel_audit_factory_res = self.rss.post(url=cancel_audit_factory_url, data=cancel_audit_factory_body).json()

        # 确认委外  东莞华秋公司
        query_audit_factory_url = "{}/SmtOrder/queryAuditFactory".format(self.ERP_URL)
        query_audit_factory_body = {"smt_order_ids": self.order_id, "factory_id": 3, "remark": "测试订单", "ajax": 1, "is_iframe": 1}
        query_audit_factory_res = self.rss.post(url=query_audit_factory_url, data=query_audit_factory_body).json()
        msg = query_audit_factory_res["info"]
        if msg == "设置成功":
            logger.info(f"确认委外成功，此时加工厂为：东莞华秋电子有限公司")
        return self


    def smt_technics_audit(self):
        """SMT订单工艺审核"""
        # self.order_id = 41610
        logout_url = "{}/Public/logout".format(self.ERP_URL)
        self.rss.get(url=logout_url)
        technics_audit_login_body = {'account': 'admin', 'password': '123456'}
        self.rss.post(url=self.login_url, data=technics_audit_login_body, headers=self.headers)
        logger.info(f"工艺审核人登录完成")

        # # 工艺审核
        technics_audit_url = "{}/SmtOrder/technicsAudit/navTabId/SmtOrderEdit".format(self.ERP_URL)
        technics_audit_body = {"id": self.order_id, "is_product": 1, "is_mj": -1, "is_traced": 2, "act": "smt",
                               "check_remark": "自动化测试验证", "ajax": 1, "is_iframe": 1}
        technics_audit_res = self.rss.post(url=technics_audit_url, data=technics_audit_body).text
        logger.info(technics_audit_res)
        logout_url = "{}/Public/logout".format(self.ERP_URL)
        self.rss.get(url=logout_url)
        self.rss.post(url=self.login_url, data=technics_audit_login_body, headers=self.headers)
        logger.debug('=*' * 50)

        return self


    def smt_order_detail_file_confirm(self,order_id,file_type):
        """smt订单详情里面文件确认"""
        file_comfirm_url = "{}/SmtOrder/confirmfile".format(self.ERP_URL)
        file_comfirm_body = {"id": order_id, "type": file_type, "navTabId": "SmtOrderEdit", "act": "smt"}
        file_comfirm_res = self.rss.post(url=file_comfirm_url, data=file_comfirm_body).json()
        # logger.info(file_comfirm_res)
        info =file_comfirm_res['info']
        if info == "更新文件确认状态成功":
            if file_type == "patch":
                logger.info("确认贴片文件成功")
            else:
                logger.info(f"确认{file_type}文件成功")
        return self
    def smt_order_bom_audit(self):
        """smt生产bom审核 +  """
        smt_order_bom_audit_search_url = "{}/ProduceBomAudit/index".format(self.ERP_URL)
        smt_order_bom_audit_search_body = {"order_sn": self.order_sn, "pageNum": "1", "order_status": 0, "compass": -1}
        smt_order_bom_audit_search_res = self.rss.post(url=smt_order_bom_audit_search_url, data=smt_order_bom_audit_search_body, headers=self.headers).text
        # print(smt_order_bom_audit_search_res)
        bom_audit_id = re.search('(<a href="/ProduceBomAudit/audit/id/)([0-9]*)', smt_order_bom_audit_search_res).group(2)
        bom_audit_url = "{}/ProduceBomAudit/audit/navTabId/ProduceBomAuditAudit".format(self.ERP_URL)
        bom_audit_body = {"id": bom_audit_id, "checked": 1, "msg": "自动化测试验证", "ajax": 1, "is_iframe": 1}
        bom_audit_res = self.rss.post(url=bom_audit_url, data=bom_audit_body, headers=self.headers).text
        logger.info(f"审核结果：成功")
        # logger.info(f"审核结果：{bom_audit_res}")
        return self

    def bom_express_delivery(self):
        """bom快递单号生成与填写"""
        self.order_id = getattr(Data, 'smt_erp_order_id', '')
        self.express_delivery_no = "SF" + datetime.now().strftime("%Y%m%d") + "000" + str(Faker("zh_CN").random_int(1, 10000))
        logger.info(f"生成的快递单号：{self.express_delivery_no}")
        express_delivery_url = "{}/SmtOrder/setexpress/navTabId/SmtOrderEdit/is_save/1".format(self.ERP_URL)
        express_delivery_body = {"smt_order_id": self.order_id, "shipping_no[]": self.express_delivery_no, "shipping_name[]": "顺丰快递",
                                 "file_path[]": "", "file_name[]": "", "ajax": 1, "is_iframe": 1}
        # print(express_delivery_body)
        express_delivery_res = self.rss.post(url=express_delivery_url, data=express_delivery_body, headers=self.headers).text
        logger.info(f"填写结果：{express_delivery_res}")
        return self.express_delivery_no
    def bom_order_push_offer(self):
        """bom订单推送报价"""
        self.order_id = getattr(Data, 'smt_erp_order_id', '')
        bom_order_acquire_url = "{}/SmtOrder/bomInfo?smt_order_id={}&act=bom".format(self.ERP_URL, self.order_id)
        bom_order_acquire_res = self.rss.get(url=bom_order_acquire_url, headers=self.headers).text
        material_match = re.search(r'<label class="unitLabel">是否代购物料：</label>\s*<span>\s*<span>(.*?)</span>',
                                   bom_order_acquire_res)
        # 提取匹配的值
        self.material_value = material_match.group(1).strip() if material_match else None
        if self.material_value != "自己提供":
            bom_order = ''
            soup = BeautifulSoup(bom_order_acquire_res, 'html.parser')
            # 找到含有 BOM SN 的 span 标签
            bom_order_sn_span = soup.find('span', class_='bomOrderSn')
            print(bom_order_sn_span)
            if bom_order_sn_span:
                bom_order = bom_order_sn_span.get_text(strip=True)
                print(bom_order)
                bom_id = re.search(f'(<a class="edit" href="/SmtOrder/bomPushErp/smt_order_id/{self.order_id}/bom_sn/{bom_order}/bom_id/)([0-9]*)', bom_order_acquire_res).group(2)
                bom_order_push_url = "{}/SmtOrder/bomPushErp/smt_order_id/{}/bom_sn/{}/bom_id/{}/navTabId/SmtOrderEdit".format(self.ERP_URL, self.order_id, bom_order, bom_id)
                bom_order_push_body = {"scenes": "project", "is_replace": 1, "is_accept_overseas":1, "postscript": "","ajax": 1, "is_iframe": 1}
                bom_order_push_res = self.rss.post(url=bom_order_push_url, data=bom_order_push_body, headers=self.headers).text
                logger.info(f"推送结果：{bom_order_push_res}")
        else:
            logger.info("未找到 bom单号，跳过执行推送报价")
        return self
    def bom_order_push_mes(self):
        """bom订单推送mes系统"""
        self.order_id = getattr(Data, 'smt_erp_order_id', '')
        search_product_bom_id_url = "{}/SmtOrder/bomInfo?smt_order_id={}&act=bom".format(self.ERP_URL, self.order_id)
        search_product_bom_id_res = self.rss.get(url=search_product_bom_id_url, headers=self.headers).text
        # logger.info(search_product_bom_id_res)
        product_bom_id = re.search('(<a class="edit" href="/SmtOrder/exportProductBom/product_bom_id/)([0-9]*)', search_product_bom_id_res).group(2)
        bom_order_push_mes_url = "{}/SmtOrder/bomPushMes/navTabId/SmtOrderEdit".format(self.ERP_URL)
        bom_order_push_mes_body = {"product_bom_id": product_bom_id}
        n = 0
        while True:
            try:
                bom_order_push_mes_res = self.rss.post(url=bom_order_push_mes_url, data=bom_order_push_mes_body, headers=self.headers).json()
                logger.info(f"推送结果1：{bom_order_push_mes_res}")
                info = bom_order_push_mes_res['info']
                if info == "推送MES成功":
                    logger.info(f"第{n + 1}次推送product_bom_id：{product_bom_id}到mes成功")
                    break
            except Exception as e:
                n += 1
                if n < 6:
                    logger.warning(f"第 {n} 次推送product_bom_id：{product_bom_id}到mes失败,等待10秒后系统自动重试,错误信息:{e}")
                    # 更新订单包---同步mes
                    update_smt_order_url = "{}/SmtOrder/refreshOrder/id/{}/navTabId/SmtOrderEdit/act/smt".format(self.ERP_URL, self.order_id)
                    update_smt_order_res = self.rss.post(url=update_smt_order_url, headers=self.headers).text
                    logger.info(f"更新订单包---同步mes结果：{update_smt_order_res}")
                    time.sleep(10)
                else:
                    logger.error(f"推送product_bom_id：{product_bom_id}到mes失败,请手动检查product_bom_id：{product_bom_id}推送情况")
                    raise ValueError
        autoProductBomUserShipping_url = "{}/Ajax/autoProductBomUserShipping?product_bom_id={}".format(self.ERP_URL, product_bom_id)
        autoProductBomUserShipping_res = self.rss.get(url=autoProductBomUserShipping_url, headers=self.headers).text
        logger.info(f"推送结果2：{autoProductBomUserShipping_res}")
        return self

    def smt_order_file(self, file_type, smt_order_file_dir, product_bom_id=None): #, file_type, smt_order_file_dir
        """文件上传"""
        smt_order_file_url = "{}/SmtOrder/jsupsmtfile".format(self.ERP_URL)
        file_name = smt_order_file_dir.split("/")[-1]
        file = [('file', (file_name, open(smt_order_file_dir, 'rb'),
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
        file_type_body = {"file_type": file_type, "smt_order_id": self.order_id, "is_reup": 1}
        if file_type == "bom":
            smt_order_file_url = "{}/SmtOrder/importProductBomStep1?navTabId=SmtOrderEdit".format(self.ERP_URL)
            file_type_body = {"id": product_bom_id, "source_type": 2, "bom_sn": "", "ajax": 1, "is_iframe": 1}
        smt_order_file_url_res = self.rss.post(url=smt_order_file_url, data=file_type_body, files=file).json()
        if file_type == "bom":
            file_server_url = smt_order_file_url_res["forwardUrl"]
        else:
            file_server_url = smt_order_file_url_res["img"]
        return file_server_url

    def mian_erp_smtorder_run(self, order_sn=None):
        erp_target_rss = SOOLogin(system_name="erp").target_login()
        setattr(Data, 'smt_order_sn', order_sn)
        ErpSmtOrderCancellation(erp_target_rss).erp_smt_order_cancellation()
        ErpSmtOrderCancellation(erp_target_rss).smt_order_bom_audit()
        express_delivery_no = ErpSmtOrderCancellation(erp_target_rss).bom_express_delivery()
        ErpSmtOrderCancellation(erp_target_rss).bom_order_push_offer()
        ErpSmtOrderCancellation(erp_target_rss).bom_order_push_mes()
        # setattr(Data, 'express_sn', express_delivery_no)
        return express_delivery_no




if __name__ == '__main__':
    # rss = SSO_Reception('15912757721', 'a123456', 'https://uat-smt.hqchip.com').login()
    # order_sn = SmtOrder(rss, 15912757721).smt_tmp_save().place_an_order()
    order_sn = "TK24082700237"
    ErpSmtOrderCancellation().mian_erp_smtorder_run(order_sn)