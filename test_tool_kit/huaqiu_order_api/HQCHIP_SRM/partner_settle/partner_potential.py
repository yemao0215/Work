import json
import random
import time
from datetime import datetime, timedelta

import jsonpath
import yaml
from xpinyin import Pinyin

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQCHIP_SRM.partner_audit.partner_audit import PartnerAudit
from huaqiu_order_api.HQCHIP_SRM.pass_partner.pass_partner import PassPartner
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import partner_potential_apply_import_dir, yaml_file, account_yaml
from huaqiu_order_api.common.yaml_handler import write_yaml


class PartnerPotential:
    # 潜在合作商
    def __init__(self, target_rss, supplier_name=None, companyType=None, companyNature=None, intendedType=None,
                 specialDevelopmentType=None, supplierSort=None, socialCreditCode=None, contacts=None, phone=None, supplierBackName=None):
        """
        :param contacts 联系人
        :param phone 联系电话
        :param companyType 公司类型 1集团(关联)公司 2国外原厂 3国内原厂 4代理商(原厂授权) 5混合分销商(代理+贸易) 6授权分销商(贸易商) 7独立分销商(贸易商) 8代购平台 9终端工厂 10供应链公司 11方案商(IDH)
        :param companyNature 公司性质 1私企 2国企 3美资 4台资 5港资 6欧资 7日资 8新资 9其他
        :param intendedType 意向合作类型 0一般采购 1寄售 2代售
        :param specialDevelopmentType 特殊开发类型 0非特殊 1特殊渠道 2特批文件 3客户指定供应商 4客户指定函 5BOM供应商 6临时供应商 7工程师专区供应商
        :param supplierSort 供应商分类 1辅材消耗类 2元器件类 3PCB类 4PCBA类 5PCBA委外加工类 6其他
        :param socialCreditCode 统一信用代码
        :param supplierBackName 后台供应商名
        """
        self.srm_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.supplier_name = supplier_name
        self.companyType = companyType
        self.companyNature = companyNature
        self.intendedType = intendedType
        self.specialDevelopmentType = specialDevelopmentType
        self.supplierSort = supplierSort
        self.socialCreditCode = socialCreditCode
        self.contacts = contacts
        self.phone = phone
        self.supplierBackName = supplierBackName
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.SRM_URL = data['SRM_URL']

    def generate_card_number(self, bin_prefix, length=16):
        """
           生成随机银行卡号
           bin_prefix: 前6位BIN（可少于6位，但推荐6位）
           length: 卡号总长度（通常16或19位）
           """
        # 确定卡号剩余位数（除去BIN和校验位）
        remaining_len = length - len(bin_prefix) - 1
        if remaining_len < 0:
            raise ValueError("长度不足，BIN前缀太长")

        # 随机生成中间部分
        middle = ''.join(str(random.randint(0, 9)) for _ in range(remaining_len))
        # 组成不含校验位的卡号
        without_check = bin_prefix + middle
        # 计算校验位
        digits = [int(d) for d in str(without_check)]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum([[int(d1) for d1 in str(d * 2)]])
        check_digit = (10 - (checksum % 10)) % 10
        # 完整卡号
        full_card = without_check + str(check_digit)
        return full_card

    def potential_partner_list(self):
        """潜在合作商列表"""
        search_url = "{}/partnermanage/partnerPotential/partnerPotentialPage?_query=2".format(self.SRM_URL)
        search_body = {"supplierName": self.supplier_name, "size": 10, "current": 1, "tag": 1}
        search_res = self.srm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        potentialInfo = search_res["body"]["records"]
        supplier_name = None
        supplierCode = None
        manage_id = None
        if potentialInfo != []:
            supplier_name = jsonpath.jsonpath(potentialInfo, "$..supplierName")
            supplierCode = jsonpath.jsonpath(potentialInfo, "$..supplierCode")
            manage_id = jsonpath.jsonpath(potentialInfo, "$..id")
        for i in range(len(supplier_name)):
            if supplier_name[i] == self.supplier_name:
                self.supplierCode = supplierCode[i]
                self.manage_id = manage_id[i]
        logger.info(f"获取合作供应商名称为{self.supplier_name}的供应商编号的list列表为{self.supplierCode}")
        return self


    def potential_partner_add(self):
        """合作商创建
        """
        add_url = "{}/partnermanage/partnerPotential/addSupplier".format(self.SRM_URL)
        add_body = {
            "companyName": self.supplier_name,
            "socialCreditCode": self.socialCreditCode,
            "contacts": "test",
            "phone": 13632845795,
            "businessBrand": "IC",
            "businessType": "元器件",
            "location": "中国-广东-深圳",
             "companyType": self.companyType,
            "companyNature": self.companyNature,
            "intendedType": self.intendedType,
            "specialDevelopmentType": self.specialDevelopmentType,
            "supplierSort": self.supplierSort,
            "channelReq": {"channelFollowerId": 3552, "channelFollower": "陶婷",
                           "channelDepartmentId": "1580548974499528706", "channelDepartment": "渠道资源部"}}
        if self.contacts != '':
            add_body["contacts"] = self.contacts
        if self.phone != '':
            add_body["phone"] = self.phone
        logger.info(add_body)
        add_res = self.srm_rss.post(url=add_url, json=add_body, headers=self.json_head).json()
        logger.info(add_res)
        msg_info = add_res["body"]
        if msg_info["companyName"] == self.supplier_name:
            self.supplierCode = msg_info["supplierCode"]
            self.manage_id = msg_info["id"]
            logger.info(f"新增合作商：{self.supplier_name}成功，其生成的供应商编号为{self.supplierCode}")
        return self


    def potential_partner_apply_import(self):
        """合作商申请引入"""
        apply_import_detail_url = "{}/partnermanage/partnerPotential/applyIn?id={}".format(self.SRM_URL, self.manage_id)
        apply_import_detail_res = self.srm_rss.get(url=apply_import_detail_url, headers=self.json_head).json()
        print(apply_import_detail_res)
        self.bodyInfo = apply_import_detail_res["body"]
        # logger.info(self.bodyInfo)
        apply_import_update_url = "{}/partnermanage/partnerPotential/updatePotentialInfo".format(self.SRM_URL)
        apply_import_update_body = {
            "id": self.bodyInfo["id"],
            "approvalStatus": self.bodyInfo["approvalStatus"],
            "approvedDocumentFile": '',
            "approvedDocumentFileId": self.bodyInfo["approvedDocumentFileId"],
            "businessBrand": self.bodyInfo["businessBrand"],
            "businessType": self.bodyInfo["businessType"],
            "companyName": self.bodyInfo["companyName"],
            "companyNature": self.bodyInfo["companyNature"],
            "companyType": self.bodyInfo["companyType"],
            "contacts": self.bodyInfo["contacts"],
            "ctime": self.bodyInfo["ctime"],
            # "customerType": self.bodyInfo["customerType"],
            "importReasons": "自动化测试引入",
            "intendedType": self.bodyInfo["intendedType"],
            "location": self.bodyInfo['location'],
            "phone": self.bodyInfo["phone"],
            "settlementSource": self.bodyInfo["settlementSource"],
             "socialCreditCode": self.bodyInfo["socialCreditCode"],
            "specialDevelopmentType": self.bodyInfo["specialDevelopmentType"],
            "specialDevelopmentTypeId": self.bodyInfo["specialDevelopmentTypeId"],
            "supplierSort": [self.bodyInfo["supplierSort"]],
             "email": self.bodyInfo["phone"] + "@163.com",
            "qq": "testzidonghua",
            "companyWeb": "{}/huaqiuzidonghuatest.html".format(self.SRM_URL),
            "supplierEvaluationFormId": self.fileId,
            }
        # print(apply_import_update_body)
        apply_import_detail_res = self.srm_rss.post(url=apply_import_update_url, json=apply_import_update_body, headers=self.json_head).json()
        print(apply_import_detail_res)
        body = apply_import_detail_res["body"]
        if body == "更新入驻信息成功":
            logger.info("更新入驻信息成功")
        startprocess_url = "{}/partnermanage/startProcess".format(self.SRM_URL)
        startprocess_body = {"comment": "启动流程", "procDefKey": "supplier_apply_into", "subject": "【合作商引入】", "supplierCode":self.supplierCode}
        startprocess_res = self.srm_rss.post(url=startprocess_url, json=startprocess_body, headers=self.json_head).json()
        logger.info(startprocess_res)
        apply_procInstId = startprocess_res["body"]
        print(f"引入审核id：{apply_procInstId}")
        # logger.debug('=*'*50)
        return apply_procInstId

    def apply_import_auditor_acquire(self, procInstId):
        # # 获取审核人

        approvalrecord_url = "{}/partnermanage/approvalRecord".format(self.SRM_URL)
        approvalrecord_body = {"procInstId": procInstId}
        approvalrecord_res = self.srm_rss.post(url=approvalrecord_url, json=approvalrecord_body, headers=self.json_head).json()
        logger.info(approvalrecord_res)
        if "msg" in approvalrecord_res:
            if "token无效" in approvalrecord_res["msg"]:
                target_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
                self.srm_rss = target_rss
                approvalrecord_res = self.srm_rss.post(url=approvalrecord_url, json=approvalrecord_body, headers=self.json_head).json()
                logger.info(approvalrecord_res)
        approvalInfo = approvalrecord_res["body"]["list"]
        self.uidCreator = None
        if approvalInfo != []:
            creatorDesc = jsonpath.jsonpath(approvalrecord_res, "$..creatorDesc")
            uidCreator = jsonpath.jsonpath(approvalrecord_res, "$..uidCreator")
            applyStatus = jsonpath.jsonpath(approvalrecord_res, "$..applyStatus")
            for i in range(len(creatorDesc)):
                if creatorDesc[i] != "发起人":
                    if applyStatus[i] != "已通过":
                        self.uidCreator = uidCreator[i]
        logger.info(f"此时合作商：{self.supplier_name}的审核节点为{self.uidCreator}")
        logger.info("请转至审核人的审核中心进行操作审核中心")
        return self.uidCreator

    def potential_partner_apply_import_img_file(self):
        """引入所需要需求开发表 图片格式"""
        file_url = "{}/partnermanage/partnerFile/upload".format(self.SRM_URL)
        file = [('file', ("apply_import.png", open(partner_potential_apply_import_dir, 'rb'),'multipart/form-source_data.openxmlformats-officedocument.spreadsheetml.sheet'))]
        applyfile_res = self.srm_rss.post(url=file_url, files=file).json()
        # logger.info(peoplefile_res)
        self.fileId = applyfile_res["body"]["fileId"]
        logger.info(self.fileId)
        return self

    def potential_partner_put_file(self):
        """建档"""
        # 触发建档
        filing_detaill_url = "{}/partnermanage/partnerPotential/newFile?id={}".format(self.SRM_URL, self.manage_id)
        print(filing_detaill_url)
        filing_detaill_res = self.srm_rss.get(url=filing_detaill_url, headers=self.json_head).json()
        print(filing_detaill_res)
        newFile_url = "{}/partnermanage/partnerPotential/newFileBySupplierCode?supplierCode={}".format(self.SRM_URL, self.supplierCode)
        print(newFile_url)
        newFile_res = self.srm_rss.get(url=newFile_url, headers=self.json_head).json()
        print(newFile_res)
        baseDataInfo = newFile_res["body"]["baseData"]
        print(baseDataInfo)
        # 修改基本信息
        baseInfoReq_url = "{}/partnermanage/partnerSupplierBaseData/baseInfoReq".format(self.SRM_URL)
        baseInfoReq_body = {
            "id": baseDataInfo["id"],
            "approvalStatus": baseDataInfo["approvalStatus"],
            "supplierCode": baseDataInfo["supplierCode"],
            "companyType": baseDataInfo["companyType"],
            "companyNature": baseDataInfo["companyNature"],
            "registerCompanyName": baseDataInfo["supplierName"],
            "supplierEnName": "test",
            "socialCreditCode": baseDataInfo["socialCreditCode"],
            "legalRepresentative": baseDataInfo["legalRepresentative"] if baseDataInfo["legalRepresentative"] else self.contacts,
            "registerAddress": "测试",
            "registerCapital": "1000万人民币",
            "incorporationDate": baseDataInfo["incorporationDate"],
            "invoicingCapacity": "5",
            "billingMethod": "",
            "invoiceMode": 3,
            "invoiceModeType": 3,
            "invoiceModeDay": 28,
            "invoiceModeNumber": "",
            "workingLanguage": "2",
            "location": f"{baseDataInfo['location']['country']}-{baseDataInfo['location']['province']}-{baseDataInfo['location']['city']}",
            "supplierSorts": baseDataInfo["supplierSort"], "businessNatures": ["集成电路"], "specialDevelopmentType": baseDataInfo["specialDevelopmentType"],
            "settlementSource": baseDataInfo["settlementSource"], "assessFilePath": baseDataInfo["assessFilePath"], "ctime": baseDataInfo["ctime"],
            "customerLetterFilePath": baseDataInfo["customerLetterFilePath"],
            "customerLetterFileName": baseDataInfo["customerLetterFileName"],
            "assessFileName": baseDataInfo["assessFileName"]
        }
        # print(baseInfoReq_body)
        baseInfoReq_res = self.srm_rss.post(url=baseInfoReq_url, json=baseInfoReq_body, headers=self.json_head).json()
        print(baseInfoReq_res)
        # 附加信息
        baseAdditionalReq_url = "{}/partnermanage/partnerSupplierBaseData/baseAdditionalReq".format(self.SRM_URL)
        baseAdditionalReq_body = {
            "id": baseDataInfo["id"],
            "supplierCode": baseDataInfo["supplierCode"],
            "approvalStatus": baseDataInfo["approvalStatus"],
            "additionalCompanyNumber": baseDataInfo["additionalCompanyNumber"],
            "additionalFax": "",
            "additionalOfficeAddress": "",
            "additionalRemark": "测试",
            "additionalSwitchboard": "",
            "customerZone": [{"zoneKey": "6", "zoneValue": "测试"}],
        }
        baseAdditionalReq_res = self.srm_rss.post(url=baseAdditionalReq_url,json=baseAdditionalReq_body, headers=self.json_head).json()
        print(baseAdditionalReq_res)

        # 资质文件 营业执照、开票资料、供应商调查表
        fileId_list = []
        for i in range(3):
            self.potential_partner_apply_import_img_file()
            fileId_list.append(self.fileId)
        baseCertificatesReq_url = "{}/partnermanage/partnerSupplierBaseData/baseCertificatesReq".format(self.SRM_URL)
        baseCertificatesReq_body = {
            "id": baseDataInfo["id"],
            "supplierCode": baseDataInfo["supplierCode"],
            "approvalStatus": baseDataInfo["approvalStatus"],
            "certificateBillingDataId": fileId_list[0],
            "certificateBusinessLicenseId": fileId_list[1],
            "certificateBusinessRegistrationId": "",
            "certificateCompanyRegistrationId": "",
            "certificateConfidentialityAgreementId": "",
            "certificateSupplierQuestionnaireId": fileId_list[2],
            "certificationNoticeId": "",
            "certificationQualityAssuranceAgreementId": ""
        }
        baseCertificatesReq_res = self.srm_rss.post(url=baseCertificatesReq_url, json=baseCertificatesReq_body, headers=self.json_head).json()
        print(baseCertificatesReq_res)

        # 联系人 legalRepresentative
        saveOrUpdateContacts_url = "{}/partnermanage/partnerSupplierBaseData/saveOrUpdateContacts".format(self.SRM_URL)
        saveOrUpdateContacts_body = [{
            "charge": "待定",
            "supplierCode": baseDataInfo["supplierCode"],
            "direct": baseDataInfo["approvalStatus"],
            # "name": baseDataInfo["legalRepresentative"],
            "name": self.contacts,
            "domesticPhone": "13632845795",
            "email": "13632845795@163.ocm",
            "emailPrefix": Pinyin().get_pinyin(self.contacts, ''),
            "emailSent": "1",
            "enName": Pinyin().get_pinyin(self.contacts, ''),
            "entryDate": "",
            "extension": "",
            "fax": "",
            "functionalScope": "/",
            "id": "11581",
            "job": "1",
            "onJob": "1",
            "other": "",
            "phone": "",
            "qq": "",
            "responsibleBrand": "",
            "sex": "男",
            "switchboard": "",
            "wechat": "",
            "workAddress": "/",
            "workingLanguage": "2"
        }]
        if self.phone != "":
            saveOrUpdateContacts_body[0]["domesticPhone"] = self.phone
            saveOrUpdateContacts_body[0]["email"] = self.phone + "@163.com"
        if self.contacts != "":
            saveOrUpdateContacts_body[0]["name"] = self.contacts
            saveOrUpdateContacts_body[0]["enName"] = Pinyin().get_pinyin(self.contacts, '')
            saveOrUpdateContacts_body[0]["emailPrefix"] = Pinyin().get_pinyin(self.contacts, '')
        saveOrUpdateContacts_res = self.srm_rss.post(url=saveOrUpdateContacts_url, json=saveOrUpdateContacts_body, headers=self.json_head).json()
        print(saveOrUpdateContacts_res)
        # 经营品牌
        # 搜索品牌-模糊
        getBrandByReq_url = "{}/partnermanage/partnerSupplierBaseData/getBrandByReq".format(self.SRM_URL)
        getBrandByReq_body = {"brand_name": "", "pageNum": 1, "pageSize": 50, "vague": "2"}
        getBrandByReq_res = self.srm_rss.post(url=getBrandByReq_url, json=getBrandByReq_body, headers=self.json_head).json()
        brand_id = jsonpath.jsonpath(getBrandByReq_res, "$..brand_id")
        brand_name = jsonpath.jsonpath(getBrandByReq_res, "$..brand_name")
        saveOrUpdateBrand_url = "{}/partnermanage/partnerSupplierBaseData/saveOrUpdateBrand".format(self.SRM_URL)
        saveOrUpdateBrand_body = []
        for m in range(len(brand_id)):
            saveOrUpdateBrand_body.append({
                "brandId": brand_id[m],
                "brandName": brand_name[m],
                "supplierCode": baseDataInfo["supplierCode"]
            })
        saveOrUpdateBrand_res = self.srm_rss.post(url=saveOrUpdateBrand_url, json=saveOrUpdateBrand_body, headers=self.json_head).json()
        print(saveOrUpdateBrand_res)
        # 银行卡信息
        self.potential_partner_apply_import_img_file()
        bankAccount = ''.join(random.choices('0123456789', k=16))
        saveOrUpdateBank_url = "{}/partnermanage/partnerSupplierBaseData/saveOrUpdateBank".format(self.SRM_URL)
        saveOrUpdateBank_body = [{
            "accountHolder": baseDataInfo["supplierName"],
            "bankAccount": bankAccount,
            "bankAddress": "",
            "bankAllName": "中国建设银行股份有限公司深圳沙河支行",
            "bankType": "",
            "depositBank": "广东-深圳",
            "file": "",
            "fileId": self.fileId,
            "flagName": "",
            "id": "",
            "remark": "",
            "standard": "1",
            "supplierCode": baseDataInfo["supplierCode"],
            "swiftCode": ""
        }]
        saveOrUpdateBank_res = self.srm_rss.post(url=saveOrUpdateBank_url, json=saveOrUpdateBank_body, headers=self.json_head).json()
        print(saveOrUpdateBank_res)
        # 业务设置
        InsertpartnerSettleBusinessSet_url = "{}/partnermanage/partnerSettleBusinessSet/InsertpartnerSettleBusinessSet".format(self.SRM_URL)
        InsertpartnerSettleBusinessSet_body = {
            "changeType": 2,
            "channelIntoPer": "",
            "channelIntoTime": None,
            "cooperationBomProfit": 0,
            "cooperationInvalidTime": 0,
            "cooperationPeriodProfit": 0,
            "cooperationReplaceProfit": 10,
            "cooperationType": "5",
            "defaultCurrency": 1,
            "defaultTaxRate": 2,
            "deliveryType": 2,
            "paymentType": 1,
            "prContractType": "1",
            "purCompanys": ["1"],
            "supplierArea": "1",
            "supplierBackName": self.supplierBackName,
            "supplierCode": baseDataInfo["supplierCode"],
            "supplierGrade": 1,
            "supplierType": 1,
            "timeType": 4,
            "timeValue": 30
        }
        InsertpartnerSettleBusinessSet_res = self.srm_rss.post(url=InsertpartnerSettleBusinessSet_url, json=InsertpartnerSettleBusinessSet_body, headers=self.json_head).json()
        print(InsertpartnerSettleBusinessSet_res)
        startprocess_url = "{}/partnermanage/startProcess".format(self.SRM_URL)
        startprocess_body = {"comment": "启动流程", "procDefKey": "supplier_taka_data", "subject": "【合作商建档】", "supplierCode": self.supplierCode}
        startprocess_res = self.srm_rss.post(url=startprocess_url, json=startprocess_body, headers=self.json_head).json()
        logger.info(startprocess_res)
        put_procInstId = startprocess_res["body"]
        print(f"建档审核id：{put_procInstId}")
        return put_procInstId
    def mian_partner_audit(self, audit_type, procInstId, supplier_name=None,supplierCode=None):
        """
        :param audit_type 审核类型  合作商引入审核 合作商建档审核 合作商修改审核
        :param procInstId 启动审核后生成的审核Id
        """
        if supplierCode != None:
            self.supplierCode = supplierCode
        if supplier_name != None:
            self.supplier_name = supplier_name
        i = 0
        while True:
            self.uidCreator = self.apply_import_auditor_acquire(procInstId)
            if self.uidCreator != None:
                if audit_type == "合作商修改审核":
                    self.supplierCode = self.supplierCode[0]
                PartnerAudit(self.srm_rss, self.supplier_name, self.supplierCode, self.uidCreator).mian_parther_audit()
            else:
                print(f"{audit_type} 完成")
                i += 1
                if i >= 1:
                    SOO_user_params = {'admin_name': "admin", "admin_pwd": "HQ@uat@666", "pro_pwd": "auth221313",
                                       "pro_user": "zhangbajun", "pwd": '123456789', "user": "yemao"}
                    user_params = {"HQCHIP_SOO": SOO_user_params}
                    write_yaml(account_yaml, user_params)
                    target_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
                    self.srm_rss = target_rss
                    break
        return self
    def mian_update_follower(self, supplierId, supplierCode, follower_type):
        """修改跟进人员或负责人
        :param supplierId 供应商id列表
        :param supplierCode 供应商编号列表
        """
        self.follower_json = {1: ["采购跟进人", "Procurement", "procurement"], 2: ["备货跟进人", "Stock", "stock"],
                              3: ["新品跟进人", "NewProduct", "newProduct"], 4: ["渠道跟进人", None, "channel"]}
        for k, v in self.follower_json.items():
            if follower_type == k:
                self.follower_target_list = v
        if self.follower_target_list[1] == None:
            self.follower_target_list[1] = ""
        mian_update_follower_url = "{0}/partnermanage/okSupplier/set{1}Follower".format(self.SRM_URL, self.follower_target_list[1])
        print(mian_update_follower_url)
        mian_update_follower_body = {"ids": supplierId, "supplierCode": supplierCode,
                                     "{0}FollowerId".format(self.follower_target_list[2]): "3552",
                                     "{0}Follower".format(self.follower_target_list[2]): "陶婷"}
        print(mian_update_follower_body)
        mian_update_follower_res = self.srm_rss.post(url=mian_update_follower_url, json=mian_update_follower_body, headers=self.json_head).json()
        logger.info("{0}更新结果：{1}".format(self.follower_target_list[0], mian_update_follower_res))
        return self

    def mian_potential_partner_add(self):
        self.potential_partner_add()
        self.potential_partner_list()
        self.potential_partner_apply_import_img_file()
        apply_procInstId = self.potential_partner_apply_import()
        self.mian_partner_audit("合作商引入审核", apply_procInstId)
        put_procInstId = self.potential_partner_put_file()
        self.mian_partner_audit("合作商建档审核", put_procInstId)
        supplierId, supplier_name, self.supplierCode, approveStatus = PassPartner(self.srm_rss, supplier_name=self.supplier_name, cooperationType=None).pass_partner_list()
        if approveStatus[0] == 0:
            # 修改跟进人员或负责人
            for i in range(4):
                i = i + 1
                self.mian_update_follower(supplierId, self.supplierCode, i)
            # 修改+审核，使其审核状态变成审核通过
            # 启用修改
            update_statue_url = "{}/partnermanage/partnerPotential/updateStatue?supplierCode={}".format(self.SRM_URL, self.supplierCode[0])
            update_statue_res = self.srm_rss.get(url=update_statue_url).json()
            logger.info(f"启用修改结果：{update_statue_res}")
            # 启用修改审核
            startprocess_url = "{}/partnermanage/startProcess".format(self.SRM_URL)
            startprocess_body = {"comment": "启动流程", "procDefKey": "supplier_update_data", "subject": "【合作商档案修改】","supplierCode": self.supplierCode[0]}
            startprocess_res = self.srm_rss.post(url=startprocess_url, json=startprocess_body, headers=self.json_head).json()
            logger.info(startprocess_res)
            update_procInstId = startprocess_res["body"]
            print(update_procInstId)
            self.mian_partner_audit("合作商修改审核", update_procInstId)
        return self.supplierCode
    def mian_potential_partner_update(self, type=None):
        supplierId, supplier_name, self.supplierCode, approveStatus = PassPartner(self.srm_rss, supplier_name=self.supplier_name,
                                                                                  cooperationType=None, supplierBackName=self.supplierBackName).pass_partner_list()
        print(supplierId, supplier_name, self.supplierCode, approveStatus)
        # 启用修改
        update_statue_url = "{}/partnermanage/partnerPotential/updateStatue?supplierCode={}".format(self.SRM_URL, self.supplierCode[0])
        update_statue_res = self.srm_rss.get(url=update_statue_url).json()
        logger.info(f"启用修改结果：{update_statue_res}")
        if "token无效" in update_statue_res["msg"]:
            self.srm_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
            update_statue_res = self.srm_rss.get(url=update_statue_url).json()
        if type == "update_Brand":
            search_BankList = "{}/partnermanage/partnerSupplierBaseData/getBankList?supplierCode={}".format(self.SRM_URL, self.supplierCode[0])
            search_BankList_res = self.srm_rss.get(url=search_BankList).json()

            print(search_BankList_res)
            self.bank_id = jsonpath.jsonpath(search_BankList_res, '$..id')[0]
            if search_BankList_res["body"] != []:
                while True:
                    try:
                        self.bankAccount = jsonpath.jsonpath(search_BankList_res, '$..bankAccount')[0]
                        # 假设 search_BankList_res 是类似 {"suc": True, "body": [...]} 的字典
                        self.brand_body = search_BankList_res.get("body", [])
                        print(self.bank_id, self.bankAccount)
                        if self.bankAccount == '' and self.bank_id != "":
                            # 生成随机卡号
                            bankAccount = self.generate_card_number("621785", 16)
                            print("1111: ", bankAccount)

                            # 确保 brand_body 是一个列表
                            if isinstance(self.brand_body, list):
                                for item in self.brand_body:
                                    # 只更新匹配的 id
                                    if str(item.get("id")) != str(self.bank_id):
                                        continue

                                    # 1. 更新 bankAccount
                                    item["bankAccount"] = bankAccount

                                    # 2. 处理 depositBank
                                    deposit = item.get("depositBank")
                                    if isinstance(deposit, dict):
                                        city = deposit.get("city")
                                        province = deposit.get("province")
                                        country = deposit.get("country")

                                        parts = []
                                        # 按顺序添加非空值（None 或空字符串都会跳过）
                                        if city:
                                            parts.append(str(city))
                                        if province:
                                            parts.append(str(province))
                                        if country:
                                            parts.append(str(country))

                                        # 更新 depositBank 为拼接字符串，若无有效值则设为空字符串
                                        item["depositBank"] = "-".join(parts) if parts else ""

                                print(self.brand_body)
                            else:
                                # 如果数据格式异常，可以记录日志或返回
                                print("brand_body 不是列表，无法更新")
                        break
                    except Exception as e:
                        # 银行卡信息
                        if self.bankAccount != '':
                            self.fileId = self.potential_partner_apply_import_img_file()
                            bankAccount = ''.join(random.choices('0123456789', k=16))
                            saveOrUpdateBank_url = "{}/partnermanage/partnerSupplierBaseData/saveOrUpdateBank".format(
                                self.SRM_URL)
                            saveOrUpdateBank_body = [{
                                "accountHolder": supplier_name,
                                "bankAccount": bankAccount,
                                "bankAddress": "",
                                "bankAllName": "中国建设银行股份有限公司深圳沙河支行",
                                "bankType": "",
                                "depositBank": "广东-深圳",
                                "file": "",
                                "fileId": self.fileId,
                                "flagName": "",
                                "id": "",
                                "remark": "",
                                "standard": "1",
                                "supplierCode": self.supplierCode,
                                "swiftCode": ""
                            }]
                            saveOrUpdateBank_res = self.srm_rss.post(url=saveOrUpdateBank_url, json=saveOrUpdateBank_body,
                                                                     headers=self.json_head).json()
                            print(saveOrUpdateBank_res)
                        break

            startprocess_url = "{}/partnermanage/startProcess".format(self.SRM_URL)
            startprocess_body = {"comment": "启动流程", "procDefKey": "supplier_update_data",
                                 "subject": "【合作商档案修改】", "supplierCode": self.supplierCode[0]}
            startprocess_res = self.srm_rss.post(url=startprocess_url, json=startprocess_body,
                                                 headers=self.json_head).json()
            logger.info(startprocess_res)
            update_procInstId = startprocess_res["body"]
            print(update_procInstId)
            self.mian_partner_audit("合作商修改审核", update_procInstId)
            if approveStatus[0] == 0:
                # 修改跟进人员或负责人
                for i in range(4):
                    i = i + 1
                    self.mian_update_follower(supplierId, self.supplierCode, i)
        return self.supplierCode






if __name__ == '__main__':
    supplier_name = "深圳市博赛源科技有限公司"
    companyType = 4
    companyNature = 1
    intendedType = 0
    specialDevelopmentType = 0
    supplierSort = 2
    socialCreditCode = ""
    phone = ''
    contacts = ""
    supplierBackName = "HQCHIP-JBTY"
    target_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
   #  update_procInstId = "4dd12e37-a237-11ef-b52b-525400dd5806"
   #  supplierCode = "SU700194"
   # # PartnerPotential(target_rss, "华秋电子uat新增测试2").potential_partner_add(1, 1, 0, 0, 1, "91440300581577931q")
   # #  PartnerPotential(target_rss, "华秋电子uat新增测试2").potential_partner_apply_import_img_file().potential_partner_apply_import()
    PartnerPotential(target_rss, supplier_name, companyType, companyNature, intendedType, specialDevelopmentType,
                     supplierSort, socialCreditCode, contacts, phone, supplierBackName).mian_potential_partner_add()
   # #  PartnerPotential(target_rss, supplier_name, companyType, companyNature, intendedType, specialDevelopmentType,
   # #                   supplierSort, socialCreditCode, contacts, phone, supplierBackName).apply_import_auditor_acquire("b53dccd5-a1a0-11ef-b52b-525400dd5806")
   # #  PartnerPotential(target_rss, supplier_name, companyType, companyNature, intendedType, specialDevelopmentType,
   # #                   supplierSort, socialCreditCode, contacts, phone, supplierBackName).mian_update_follower(["4049"], ["SU001620"],4)
   # #  PartnerPotential(target_rss, supplier_name, companyType, companyNature, intendedType, specialDevelopmentType,
   # #                   supplierSort, socialCreditCode, contacts, phone, supplierBackName).mian_partner_audit("合作商修改审核", update_procInstId, supplier_name,supplierCode)
    PartnerPotential(target_rss, supplierBackName=supplierBackName).mian_potential_partner_update("update_Brand")