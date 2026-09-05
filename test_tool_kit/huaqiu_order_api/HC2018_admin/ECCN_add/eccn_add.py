import pandas
import requests
import yaml

from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, eccn_dir


class EccnAdd:
    def __init__(self):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.HC2018_ADMIN_URL = data['HC2018_ADMIN_URL']
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}

    def read_data(self):
        logger.info("开始读取表格内容")
        data = pandas.read_csv(eccn_dir)
        self.eccn_code = data["ECCN编码"]
        self.is_forbid = data["禁/是/否受限"]
        self.forbid_scene = data["受限场景说明"]
        self.applied_area = data["应用领域"]
        self.description = data["说明"]
        self.web_display = data["前端显示文本"]
        return self

    def eccn_code_add(self,rss, auth_token):
        self.rss = rss

        for i in range(len(self.eccn_code)):
            self.eccn_code_sn = self.eccn_code[i]
            self.is_forbid_sn = self.is_forbid[i]
            self.forbid_scene_sn = self.forbid_scene[i]
            self.applied_area_sn = self.applied_area[i]
            self.description_sn = self.description[i]
            self.web_display_sn = self.web_display[i]
            if self.is_forbid_sn == "是":
                self.is_forbid_id = "1"
            elif self.is_forbid_sn == "否":
                self.is_forbid_id = "2"
            elif self.is_forbid_sn == "禁":
                self.is_forbid_id = "3"
            logger.info(f"获取到第{i + 2}行的is_forbid：{self.is_forbid_id}")
            if self.applied_area_sn == "民用":
                self.applied_area_id = "1"
            elif self.applied_area_sn == "/":
                self.applied_area_id = "2"
            logger.info(f"获取到第{i + 2}行的applied_area：{self.applied_area_id}")
            if self.forbid_scene_sn == "必须有出口许可证":
                self.forbid_scene_id = "1"
            elif self.forbid_scene_sn == "客户需提供出口许可证及终端客户信息":
                self.forbid_scene_id = "2"
            elif self.forbid_scene_sn == "香港进口需有进口许可证":
                self.forbid_scene_id = "3"
            elif self.forbid_scene_sn == "须由客户签订民用声明":
                self.forbid_scene_id = "4"
            elif self.forbid_scene_sn == "需要终端用户和项目信息；须由客户签订民用声明":
                self.forbid_scene_id = "5"
            elif self.forbid_scene_sn == "需终端用户声明，可以发到香港":
                self.forbid_scene_id = "6"
            elif self.forbid_scene_sn == "/":
                self.forbid_scene_id = "7"
            logger.info(f"获取到第{i + 2}行的forbid_scene：{self.forbid_scene_id}")
            eccn_code_add_url = "{}/v1/goods/EccnCode/insertEccnCode".format(self.HC2018_ADMIN_URL)
            eccn_code_add_body = {
                "eccn_code": self.eccn_code_sn,
                "is_forbid": self.is_forbid_id,
                "forbid_scene": self.forbid_scene_id,
                "applied_area": self.applied_area_id,
                "web_display": self.web_display_sn,
                "description": self.description_sn

            }
            self.headers["Authorization"] = auth_token
            eccn_code_add_res = self.rss.post(url=eccn_code_add_url, data=eccn_code_add_body, headers=self.headers).json()
            code = eccn_code_add_res["code"]
            if code == 0:
                logger.info(f"ECCN编码：{self.eccn_code_sn}新增成功")
            else:
                msg = eccn_code_add_res["msg"]
                if msg == f"eccn编码：{self.eccn_code_sn}已存在":
                    logger.info(f"ECCN编码：{self.eccn_code_sn}已存在")
                else:
                    logger.error(f"ECCN编码：{self.eccn_code_sn}新增失败，请检查传参，此时参数：{eccn_code_add_body}")
            continue
        return self
    def eccn_add_mian(self):
        self.rss, self.login_headers, self.auth_token = Login().login()
        EccnAdd().read_data().eccn_code_add(self.rss, self.auth_token)
        return self

if __name__ == '__main__':
    EccnAdd().eccn_add_mian()



