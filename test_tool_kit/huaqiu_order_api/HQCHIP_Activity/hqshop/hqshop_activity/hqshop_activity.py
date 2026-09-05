import json

import jsonpath
import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file


class HqshopActivity:

    def __init__(self, target_rss, activity_name, activity_id=None, thematic_name=None, shopThemat_id=None):
        self.activity_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.activity_name = activity_name
        self.activity_id = activity_id
        self.thematicName = thematic_name
        self.shopThemat_id = shopThemat_id
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data['Activity_Center_URL']
        self.HQCHIP_URL = data['HQCHIP_URL']
        self.SMT_HQCHIP = self.HQCHIP_URL.replace("www", "smt")
        self.HQPCB_URL = data['HQPCB_URL']
        self.ELECFANS_URL = data['ELECFANS_URL']

    def hqshop_activity_list(self):
        """专题管理列表"""
        search_url = "{}/ecmc/shop/specialSubjectList".format(self.Activity_Center_URL)
        search_body = {"hasPc": 1, "hasMobile": "", "pageNum": 1, "pageSize": 20, "platformld":"", "activityName": self.activity_name}
        search_res = self.activity_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        activityInfo = search_res["result"]
        actiivty_shopThematic_json = []
        for i in range(len(activityInfo)):
            activity_id = activityInfo[i]["id"]
            activity_name = activityInfo[i]["activityName"]
            shopThematicInfo = activityInfo[i]["shopThematic"]
            shopThemat_id = []
            thematicName = []
            for j in range(len(shopThematicInfo)):
                shopThemat_id.append(shopThematicInfo[j]["id"])
                thematicName .append(shopThematicInfo[j]["thematicName"])
            result = list(zip(thematicName, shopThemat_id))
            k = {"activity_id": activity_id, "activity_name": activity_name, "thematicNameInfo": [{"thematicName": item[0], "thematicId": item[1]} for item in result]}
            actiivty_shopThematic_json.append(k)
        # print(json.dumps(actiivty_shopThematic_json, ensure_ascii=False).replace("'", '"'))
        shopThemat_id = []
        for i in range(len(actiivty_shopThematic_json)):
            if self.activity_name != "":
                if self.activity_name == actiivty_shopThematic_json[i]["activity_name"]:
                    self.activity_id = actiivty_shopThematic_json[i]["activity_id"]
                    for j in range(len(actiivty_shopThematic_json[i]["thematicNameInfo"])):
                        if self.thematicName != "":
                            # 当 self.thematicName 不为空时
                            if self.thematicName == actiivty_shopThematic_json[i]["thematicNameInfo"][j]["thematicName"]:
                                shopThemat_id.append(actiivty_shopThematic_json[i]["thematicNameInfo"][j]["thematicId"])
                        elif self.shopThemat_id != "":
                            # 当 self.thematicName 为空且 self.shopThemat_id 不为空时
                            # 使用列表推导式查找thematicId为"337"的thematicName值
                            self.thematicName = next((item["thematicName"] for item in actiivty_shopThematic_json[i]["thematicNameInfo"] if item["thematicId"] == self.shopThemat_id), None)
                            shopThemat_id = self.shopThemat_id
                            # print(self.thematicName)
                            break
            elif self.activity_id != "":
                if self.activity_id == actiivty_shopThematic_json[i]["activity_id"]:
                    self.activity_name = actiivty_shopThematic_json[i]["activity_name"]
                    for j in range(len(actiivty_shopThematic_json[i]["thematicNameInfo"])):
                        if self.thematicName != "":
                            # 当 self.thematicName 不为空时
                            if self.thematicName == actiivty_shopThematic_json[i]["thematicNameInfo"][j]["thematicName"]:
                                shopThemat_id.append(actiivty_shopThematic_json[i]["thematicNameInfo"][j]["thematicId"])
                        elif self.shopThemat_id != "":
                            # 当 self.thematicName 为空且 self.shopThemat_id 不为空时
                            # 使用列表推导式查找thematicId为"337"的thematicName值
                            self.thematicName = next((item["thematicName"] for item in actiivty_shopThematic_json[i]["thematicNameInfo"] if item["thematicId"] == self.shopThemat_id), None)
                            shopThemat_id = self.shopThemat_id
                            # print(self.thematicName)
                            break
        logger.info(f"获取专题活动名称为{self.activity_name}的活动id的list列表为{self.activity_id}的专题：{self.thematicName}的id：{shopThemat_id}")
        return self.activity_id, self.activity_name, self.thematicName, shopThemat_id

    def hqshop_activity_add(self):
        """专题活动建立"""
        add_url = "{}/ecmc/shop/addSpecialSubject".format(self.Activity_Center_URL)
        add_body = {"activityName": self.activity_name, "activityIntro": "自动化测试", "hasPc": 1, "hasMobile": "1","platformId": 1}
        add_res = self.activity_rss.post(url=add_url, json=add_body, headers=self.json_head).json()
        # logger.info(add_res)
        msg = add_res["retMsg"]
        if msg == "新增成功":
            logger.info(f"专题活动：{self.activity_name} 新增成功")
            return self

    def hqshop_activity_edit(self, activity_name_update):
        """专题活动编辑"""
        edit_url ="{}/ecmc/shop/editSpecialSubject".format(self.Activity_Center_URL)
        edit_body = {"id": self.activity_id, "activityName": activity_name_update, "activityIntro": "自动化测试", "hasPc": 1, "hasMobile": "1","platformId": 1}
        edit_res = self.activity_rss.post(url=edit_url, json=edit_body, headers=self.json_head).json()
        logger.info(edit_res)
    def main_hqshop_activity(self):
        activity_id, activity_name, thematicName, shopThemat_id = self.hqshop_activity_list()
        if activity_id == "":
            self.hqshop_activity_add()
            activity_id, activity_name, thematicName, shopThemat_id = self.hqshop_activity_list()
        if shopThemat_id == []:
            return activity_id, activity_name, thematicName, shopThemat_id
        elif isinstance(shopThemat_id, list):
            return activity_id, activity_name, thematicName, shopThemat_id[0]
        else:
            return activity_id, activity_name, thematicName, shopThemat_id



if __name__ == '__main__':

   target_rss = SOOLogin("uat-activity.hqchip.com", "ecmc").target_login()
   # activity_name_update = "自动化脚本专题测试"
   HqshopActivity(target_rss, "系列活动管理-测试-勿动", "", "", "404").hqshop_activity_list()