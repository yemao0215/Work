import json
import time
from datetime import datetime, timedelta

from xpinyin import Pinyin

# from HQCHIP_SOO.login import SOOLogin
# from common.loguru_logger import logger



class UsersResoruce:
    # 客户资料操作

    def __init__(self, target_rss, users_name):
        self.srm_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.users_name = users_name
        # self.supplierCode = supplierCode
        # self.audit_users = audit_users

    def users_resource_list(self):
        """客户资料列表"""