from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import freight_goods_dir, freight_people_dir, partner_potential_apply_import_dir


class PartnerUsers:
    # 合作商账号管理
    def __init__(self, target_rss):
        self.srm_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        # self.supplier_name = supplier_name


    def partner_users_list(self):
        """合作商账号管理列表"""
        search_url = "https://uat-srm.huaqiu.com/partnermanage/partnerUserAdmin/partnerUserAdminPage"
        search_body = {"current": 10, " available": "", "startTime": "", "endTime": "", "size":5,
                       "input": "", "keyword": "", "option": "keyword"}
        search_res = self.srm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        # logger.info(search_res)
        recordsInfo = search_res["body"]["records"]
        username = []
        self.supplier_name = []
        for i in range(len(recordsInfo)):
            username.append(recordsInfo[i]["username"])
            self.supplier_name.append(recordsInfo[i]["supplierName"])
        logger.info(f"获取到合作商名称列表：{self.supplier_name}，供应商登录门户用户名list：{username}")
        return self.supplier_name

    def partner_users_list_keyword(self, keyword):
        """合作商账号管理列表"""
        search_url = "https://uat-srm.huaqiu.com/partnermanage/partnerUserAdmin/partnerUserAdminPage"
        search_body = {"current": 1, " available": "", "startTime": "", "endTime": "", "size": 10,
                       "input": keyword, "keyword": keyword, "option": "keyword"}
        search_res = self.srm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        logger.info(search_res)
        recordsInfo = search_res["body"]["records"]
        username = []
        supplier_name = []
        for i in range(len(recordsInfo)):
            username.append(recordsInfo[i]["username"])
            supplier_name.append(recordsInfo[i]["supplierName"])
        for q in range(len(recordsInfo)):
            if keyword == supplier_name[q]:
                self.username = username[q]
        logger.info(f"获取到供应商：{keyword}在门户网站的登录用户名为{self.username}")
        return self.username