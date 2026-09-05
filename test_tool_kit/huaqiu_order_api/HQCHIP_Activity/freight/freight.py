import json
import time
from datetime import datetime, timedelta

import jsonpath
import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import freight_goods_dir, freight_people_dir, yaml_file


class Freight:
    # 运费促销活动
    def __init__(self, target_rss, activity_name):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data['Activity_Center_URL']
        self.HQCHIP_URL = data['HQCHIP_URL']
        self.activity_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.activity_name = activity_name



    def freight_list(self):
        """运费促销管理列表"""
        search_url = "{}/ecmc/freight/getList".format(self.Activity_Center_URL)
        search_body = {"timeStatus":"0", "pageNum": 1, "pageSize": 20}
        search_res = self.activity_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        # logger.info(search_res)
        activityInfo = search_res["result"]
        logger.info(len(activityInfo))
        # shopThematinfo = activityInfo.get("shopThematic")
        self.activity_id = []
        activity_name = []
        for i in range(len(activityInfo)):
            self.activity_id.append(activityInfo[i]["id"])
            activity_name.append(activityInfo[i]["activityName"])
        # logger.info(self.activity_id)
        # logger.info(activity_name)
        for q in range(len(activityInfo)):
            if self.activity_name == activity_name[q]:
                self.activity_id = self.activity_id[q]
                # self.activity_id.append(self.activity_id[q])
            continue
        logger.info(f"获取运费促销活动名称为{self.activity_name}的活动id的list列表为{self.activity_id}")

        return self
    def freight_erp_express(self):
        """ERP可用快递"""
        search_express_url = "{}/ecmc/freight/getErpShippingInfo".format(self.Activity_Center_URL)
        search_express_res = self.activity_rss.get(url=search_express_url, headers=self.json_head).json()
        shippingCode = jsonpath.jsonpath(search_express_res, "$..shippingCode")
        shippingId = jsonpath.jsonpath(search_express_res, "$..shippingId")
        shippingName = jsonpath.jsonpath(search_express_res, "$..shippingName")
        return shippingCode, shippingId, shippingName

    def freight_add(self, goodsPromotionType, promotionPeopleGroup, shippingCode=None, shippingName=None,
                    miniConsume=None,timeliness=None):
        """创建运费促销活动
        :param goodsPromotionType 促销产品类型 1全部商品 2指定活动 3指定库存
        ：param promotionPeopleGroup 促销人群类型 1所有人群 2仅限元器件新客 3仅限元器件老客 4指定人群包
        """
        now_time_ten_minutes = str((datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间10分钟后的时间：{now_time_ten_minutes}")
        now_time_one_day = str((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一天后的时间：{now_time_one_day}")
        add_url = "{}/ecmc/freight/addFreight".format(self.Activity_Center_URL)
        add_body = None
        if goodsPromotionType == 1 and promotionPeopleGroup == 1:
            add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes, "activityEndTime": now_time_one_day,"deliveryChannels": 2, "miniConsume": 0,
                        "goodsPromotionType": goodsPromotionType, "activityFreightPromotionAlreadyActivity": "", "goodsUploadFileName":"", "goodsUploadFilePath": "",
                        "promotionPeopleGroup": promotionPeopleGroup, "peopleGroupUploadFileName":"","peopleGroupUploadFilePath":"",
                        "provinceFreightJson": {"guangdong": 100, "other": 100, "hunan": 100, "hunanOther": 100}
                        }

        elif goodsPromotionType == 1 and promotionPeopleGroup == 2:
            add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes,"activityEndTime": now_time_one_day, "deliveryChannels": 2, "miniConsume": 0,
                        "goodsPromotionType": goodsPromotionType, "activityFreightPromotionAlreadyActivity": "","goodsUploadFileName": "", "goodsUploadFilePath": "",
                        "promotionPeopleGroup": promotionPeopleGroup, "peopleGroupUploadFileName": "","peopleGroupUploadFilePath": "",
                        "provinceFreightJson": {"guangdong": 100, "other": 50, "hunan": 100, "hunanOther": 50}
                        }

        elif goodsPromotionType == 1 and promotionPeopleGroup == 3:
            add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes,"activityEndTime": now_time_one_day, "deliveryChannels": 2, "miniConsume": 0,
                        "goodsPromotionType": goodsPromotionType, "activityFreightPromotionAlreadyActivity": "", "goodsUploadFileName": "", "goodsUploadFilePath": "",
                        "promotionPeopleGroup": promotionPeopleGroup, "peopleGroupUploadFileName": "","peopleGroupUploadFilePath": "",
                        "provinceFreightJson": {"guangdong": 100, "other": 50, "hunan": 100, "hunanOther": 50}
                        }

        elif goodsPromotionType == 1 and promotionPeopleGroup == 4:
            add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes,"activityEndTime": now_time_one_day, "deliveryChannels": 2, "miniConsume": 0,
                        "goodsPromotionType": goodsPromotionType, "activityFreightPromotionAlreadyActivity": "", "goodsUploadFileName": "", "goodsUploadFilePath": "",
                        "promotionPeopleGroup": promotionPeopleGroup, "peopleGroupUploadFileName": self.freight_people_file_name,"peopleGroupUploadFilePath": self.freight_people_file_url,
                        "provinceFreightJson": {"guangdong": 100, "other": 50, "hunan": 100, "hunanOther": 50}
                        }
        elif goodsPromotionType == 2 and promotionPeopleGroup == 1:
            add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes,"activityEndTime": now_time_one_day, "deliveryChannels": 2, "miniConsume": 0,
                        "goodsPromotionType": goodsPromotionType, "goodsUploadFileName": "", "goodsUploadFilePath": "",
                        "activityFreightPromotionAlreadyActivity": self.activityInfo,
                        "promotionPeopleGroup": promotionPeopleGroup, "peopleGroupUploadFileName": "","peopleGroupUploadFilePath": "",
                        "provinceFreightJson": {"guangdong": 100, "other": 50, "hunan": 100, "hunanOther": 50}
                        }
        elif goodsPromotionType == 2 and promotionPeopleGroup == 2:
            add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes,"activityEndTime": now_time_one_day, "deliveryChannels": 2, "miniConsume": 0,
                        "goodsPromotionType": goodsPromotionType, "goodsUploadFileName": "", "goodsUploadFilePath": "",
                        "activityFreightPromotionAlreadyActivity": self.activityInfo,
                        "promotionPeopleGroup": promotionPeopleGroup, "peopleGroupUploadFileName": "","peopleGroupUploadFilePath": "",
                        "provinceFreightJson": {"guangdong": 100, "other": 50, "hunan": 100, "hunanOther": 50}
                        }
        elif goodsPromotionType == 2 and promotionPeopleGroup == 3:
            add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes,"activityEndTime": now_time_one_day, "deliveryChannels": 2, "miniConsume": 0,
                        "goodsPromotionType": goodsPromotionType, "goodsUploadFileName": "", "goodsUploadFilePath": "",
                        "activityFreightPromotionAlreadyActivity": self.activityInfo,
                        "promotionPeopleGroup": promotionPeopleGroup, "peopleGroupUploadFileName": "","peopleGroupUploadFilePath": "",
                        "provinceFreightJson": {"guangdong": 100, "other": 50, "hunan": 100, "hunanOther": 50}
                        }
        elif goodsPromotionType == 2 and promotionPeopleGroup == 4:
            add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes,"activityEndTime": now_time_one_day, "deliveryChannels": 2, "miniConsume": 0,
                        "goodsPromotionType": goodsPromotionType, "goodsUploadFileName": "", "goodsUploadFilePath": "",
                        "activityFreightPromotionAlreadyActivity": self.activityInfo,
                        "promotionPeopleGroup": promotionPeopleGroup, "peopleGroupUploadFileName": self.freight_people_file_name,"peopleGroupUploadFilePath": self.freight_people_file_url,
                        "provinceFreightJson": {"guangdong": 100, "other": 50, "hunan": 100, "hunanOther": 50}
                        }
        elif goodsPromotionType == 3 and promotionPeopleGroup == 1:
            add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes,"activityEndTime": now_time_one_day, "deliveryChannels": 2, "miniConsume": 0,
                        "goodsPromotionType": goodsPromotionType, "activityFreightPromotionAlreadyActivity": "","goodsUploadFileName": self.freight_goods_file_name, "goodsUploadFilePath": self.freight_goods_file_url,
                        "promotionPeopleGroup": promotionPeopleGroup, "peopleGroupUploadFileName": "","peopleGroupUploadFilePath": "",
                        "provinceFreightJson": {"guangdong": 100, "other": 50, "hunan": 100, "hunanOther": 50}
                        }
        elif goodsPromotionType == 3 and promotionPeopleGroup == 2:
            add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes,"activityEndTime": now_time_one_day, "deliveryChannels": 2, "miniConsume": 0,
                        "goodsPromotionType": goodsPromotionType, "activityFreightPromotionAlreadyActivity": "","goodsUploadFileName": self.freight_goods_file_name, "goodsUploadFilePath": self.freight_goods_file_url,
                        "promotionPeopleGroup": promotionPeopleGroup, "peopleGroupUploadFileName": "","peopleGroupUploadFilePath": "",
                        "provinceFreightJson": {"guangdong": 100, "other": 50, "hunan": 100, "hunanOther": 50}
                        }
        elif goodsPromotionType == 3 and promotionPeopleGroup == 3:
            add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes,"activityEndTime": now_time_one_day, "deliveryChannels": 2, "miniConsume": 0,
                        "goodsPromotionType": goodsPromotionType, "activityFreightPromotionAlreadyActivity": "","goodsUploadFileName": self.freight_goods_file_name, "goodsUploadFilePath": self.freight_goods_file_url,
                        "promotionPeopleGroup": promotionPeopleGroup, "peopleGroupUploadFileName": "","peopleGroupUploadFilePath": "",
                        "provinceFreightJson": {"guangdong": 100, "other": 50, "hunan": 100, "hunanOther": 50}
                        }
        elif goodsPromotionType == 3 and promotionPeopleGroup == 4:
            add_body = {"activityName": self.activity_name, "activityStartTime": now_time_ten_minutes,"activityEndTime": now_time_one_day, "deliveryChannels": 2, "miniConsume": 0,
                        "goodsPromotionType": goodsPromotionType, "activityFreightPromotionAlreadyActivity": "","goodsUploadFileName": self.freight_goods_file_name,"goodsUploadFilePath": self.freight_goods_file_url,
                        "promotionPeopleGroup": promotionPeopleGroup, "peopleGroupUploadFileName": self.freight_people_file_name,"peopleGroupUploadFilePath": self.freight_people_file_url,
                        "provinceFreightJson": {"guangdong": 100, "other": 50, "hunan": 100, "hunanOther": 50}
                        }
        add_body['sendDataSourceType'] = 1
        add_body['shippingCode'] = shippingCode
        if miniConsume !=None and int(miniConsume) > 0:
            add_body["miniConsume"] = int(miniConsume)
        if timeliness != None:
            add_body["activityEndTime"] = "2099-12-31 23:59:59"
        if shippingName != None:
            add_body["activityName"] = self.activity_name + "-" + shippingName
        freight_add_res = self.activity_rss.post(url=add_url, json=add_body, headers=self.json_head).json()
        logger.info(freight_add_res)
        msg = freight_add_res["result"]
        if msg == "新增成功":
            logger.info(f"运费促销活动：{self.activity_name} 创建成功")
            return self

    def promotion_activity(self):
        """获取活动列表"""
        activitygoodslist_url = "{}/ecmc/freight/activityGoodsList".format(self.Activity_Center_URL)
        activitygoodslist_body = {"id":""}
        activitygoodslist_res = self.activity_rss.post(url=activitygoodslist_url, json=activitygoodslist_body, headers=self.json_head).json()
        # logger.info(activitygoodslist_res)
        activityInfo = activitygoodslist_res["result"]
        self.activity_id = []
        activity_name = []
        for i in range(len(activityInfo)):
            self.activity_id.append(activityInfo[i]["relationActivityId"])
            activity_name.append(activityInfo[i]["relationActivityName"])
        self.activityInfo = activityInfo[0]
        for q in range(len(activityInfo)):
            if self.activity_name == activity_name[q]:
                # 当传入的活动名称存在时，对应的self.activityInfo替换成activityInfo[q]
                self.activity_id = self.activity_id[q]
                self.activityInfo = activityInfo[q]
        logger.info(self.activityInfo)
        return self

    def promotion_goods_file(self):
        """库存id上传"""
        file_url = "{}/ecmc/upload/uploadFile".format(self.Activity_Center_URL)
        file = [('file', ("freight_goods.csv", open(freight_goods_dir, 'rb'),'multipart/form-source_data.openxmlformats-officedocument.spreadsheetml.sheet'))]
        goodsfile_res = self.activity_rss.post(url=file_url, files=file).json()
        logger.info(goodsfile_res)
        self.freight_goods_file_name = goodsfile_res["result"]["fileName"]
        self.freight_goods_file_url = goodsfile_res["result"]["url"]
        return self
    def promotion_people_file(self):
        """人群包上传"""
        file_url = "{}/ecmc/upload/uploadFile".format(self.Activity_Center_URL)
        file = [('file', ("freight_people.csv", open(freight_people_dir, 'rb'),'multipart/form-source_data.openxmlformats-officedocument.spreadsheetml.sheet'))]
        peoplefile_res = self.activity_rss.post(url=file_url, files=file).json()
        logger.info(peoplefile_res)
        self.freight_people_file_name = peoplefile_res["result"]["fileName"]
        self.freight_people_file_url = peoplefile_res["result"]["url"]
        return self
    def mian_add_text(self):
        shippingCode, shippingId, shippingName = self.freight_erp_express()
        for i in range(len(shippingCode)):
            self.freight_add(1, 1, shippingCode=shippingCode[i], shippingName=shippingName[i],
                    miniConsume=399, timeliness=1)



if __name__ == '__main__':
   target_rss = SOOLogin("uat-activity.hqchip.com", "ecmc").target_login()
   # Freight(target_rss, "周版本测试").promotion_activity().promotion_goods_file().promotion_people_file().freight_add(2,4)
   Freight(target_rss, "全平台-满300免邮").mian_add_text()