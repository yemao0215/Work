from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import freight_goods_dir, freight_people_dir, partner_potential_apply_import_dir


class UsersPasswordReset:
    # 合作商账号重置
    def __init__(self, target_rss, supplier_name):
        self.srm_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.supplier_name = supplier_name


    def password_reset(self):
        """门户登录密码重置"""
        search_url = "https://uat-srm.huaqiu.com/partnermanage/partnerUserAdmin/partnerUserAdminPage"
        search_body = {"current": 1, " available": "", "startTime": "", "endTime": "", "size": 10,
                       "input": self.supplier_name, "keyword": self.supplier_name, "option": "keyword"}
        search_res = self.srm_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        # logger.info(search_res)
        recordsInfo = search_res["body"]["records"]
        username = []
        supplier_name = []
        for i in range(len(recordsInfo)):
            username.append(recordsInfo[i]["username"])
            supplier_name.append(recordsInfo[i]["supplierName"])
        for q in range(len(recordsInfo)):
            if self.supplier_name == supplier_name[q]:
                username = username[q]
        logger.info(f"获取到供应商：{self.supplier_name}在门户网站的登录用户名为{username}")
        reset_url = "https://uat-srm.huaqiu.com/partnermanage/partnerUserAdmin/updatePassword"
        reset_body = {"username": username, "newPassword": "666888"}
        reset_res = self.srm_rss.post(url=reset_url, json=reset_body, headers=self.json_head).json()
        logger.info(reset_res)
        return self