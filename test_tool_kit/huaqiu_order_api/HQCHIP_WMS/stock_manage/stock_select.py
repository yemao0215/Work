import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class StockMange:
    def __init__(self, target_rss):
        self.wms_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.erp_goods_sn = getattr(Data, 'erp_goods_sn')
        # self.number = getattr(Data, 'number')
        # self.out_order = "OUT00263937"
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.WMS_URL = data["WMS_URL"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.warehouse_type = account["HQCHIP_GOODS"]["warehouse_id"]

    def wms_out_goods_decide(self):
        """判断库存是否满足出库"""
        # self.erp_goods_sn = "G0048827"
        self.number = 1
        inventory_goods_url = "{}/wms/warehouse/inventory/queryInventoryPage".format(self.WMS_URL)
        inventory_goods_body = {"goodsInfo": self.erp_goods_sn, "pageNum": 1, "pageSize": 50}
        inventory_goods_res = self.wms_rss.post(url=inventory_goods_url, json=inventory_goods_body,
                                                headers=self.json_head).json()
        result = inventory_goods_res["result"]
        if result != []:
            # labelNumber 商品标签，lockStatus 锁定状态， labelQuantity 库存数量，locationCode库存库位， pickDistributionQtyBu占用量，controlStatus冻结状态
            businessTypeName = []
            labelNumber = []
            lockStatus = []
            labelQuantity = []
            locationCode = []
            pickDistributionQtyBu = []
            controlStatus = []
            for i in range(len(result)):
                businessTypeName.append(result[i]["businessTypeName"])
                labelNumber.append(result[i]["labelNumber"])
                lockStatus.append(result[i]["lockStatus"])
                labelQuantity.append(result[i]["labelQuantity"])
                locationCode.append(result[i]["labelQuantity"])
                pickDistributionQtyBu.append(result[i]["pickDistributionQtyBu"])
                controlStatus.append(result[i]["controlStatus"])
            labelQuantity_count = 0
            pickDistributionQtyBu_count = 0
            for m in range(len(businessTypeName)):
                """判断规则：出库单号商品定位的库存储位，存在商品标签，锁定状态为未锁定、库存数量-占用数量>购买量，冻结状态为未冻结，存在库位"""
                # data_businessTypeName = getattr(Data, 'businessTypeName')
                data_businessTypeName = "自营储位"
                # logger.info(businessTypeName[m])
                if businessTypeName[m] in data_businessTypeName:
                    if labelNumber[m] != "" and lockStatus[m] == "0" and controlStatus[m] == "0" and locationCode[m] != None:
                        # 循环叠加计算【labelQuantity_count】【pickDistributionQtyBu_count】值
                        labelQuantity_count = labelQuantity_count + int(labelQuantity[m])
                        pickDistributionQtyBu_count = pickDistributionQtyBu_count + int(pickDistributionQtyBu[m])
            logger.info(f"获取到库存总量：{labelQuantity_count}和库存占用总量：{pickDistributionQtyBu_count}")
            if labelQuantity_count - pickDistributionQtyBu_count >= int(self.number):
                wms_msg = f"编码：{self.erp_goods_sn}符合WMS出库要求"
                logger.info(wms_msg)
            else:
                wms_msg = f"编码：{self.erp_goods_sn}不符合WMS出库要求，当前库存库存数据的可用数据小于订单量，当前可用数据：{labelQuantity_count - pickDistributionQtyBu_count}"
                logger.error(wms_msg)
        else:
            wms_msg = f"编码：{self.erp_goods_sn}不符合WMS出库要求，不存在编码：{self.erp_goods_sn}的库存数据"
            logger.error(wms_msg)
        return wms_msg

    def goods_tag_create(self):

        """商品标签生成"""
        # self.erp_goods_sn = "G5058914"
        inventory_goods_url = "{}/wms/warehouse/inventory/queryInventoryPage".format(self.WMS_URL)
        inventory_goods_body = {"goodsInfo": self.erp_goods_sn, "pageNum": 1, "pageSize": 50}
        inventory_goods_res = self.wms_rss.post(url=inventory_goods_url, json=inventory_goods_body,
                                                headers=self.json_head).json()
        result_1 = inventory_goods_res["result"]
        # id = []
        if result_1 != []:
            # labelNumber = []# 	G4180931\G4626476\G5058914
            id = []
            for i in range(len(result_1)):
                labelNumber = result_1[i]["labelNumber"]
                if labelNumber == "":
                    logger.info(f"商品编码：{self.erp_goods_sn}存在无商品标签的库存明细")
                    id.append(result_1[i]["id"])
                else:
                    logger.info(f"商品编码：{self.erp_goods_sn}不存在无商品标签的库存明细")
            logger.info(f"获取到id列表为：{id}")
            goods_tag_create_url = "{}/wms/warehouse/inventory/printInventoryLabelByInvId".format(self.WMS_URL)
            # list列表添加转译符，将id =["111", "122"]转译成[\"111\", \"122\"]
            # id = '[' + ', '.join([f'\\"{item}\\"' for item in id]) + ']'
            goods_tag_create_body = id
            self.wms_rss.post(url=goods_tag_create_url, json=goods_tag_create_body, headers=self.json_head).json()
            inventory_goods_url = "{}/wms/warehouse/inventory/queryInventoryPage".format(self.WMS_URL)
            inventory_goods_body = {"goodsInfo": self.erp_goods_sn, "pageNum": 1, "pageSize": 50}
            inventory_goods_res = self.wms_rss.post(url=inventory_goods_url, json=inventory_goods_body,
                                                    headers=self.json_head).json()
            result_2 = inventory_goods_res["result"]
            for m in range(len(result_2)):
                labelNumber = result_2[m]["labelNumber"]
                if labelNumber == "":
                    id_2 = result_2[m]["id"]
                    logger.info(f"商品编码：{self.erp_goods_sn}存在无商品标签的库存明细，此时id为{id_2}")
                    break
                continue

if __name__ == '__main__':
        target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
        # order_sn = IcOrder(15912757721, 'a123456', 2500332898).login().add_cart().place_an_order()
        # out_sn = ErpOrderCancellation().erp_ic_order_cancellation(order_sn)
        StockMange(target_rss).wms_out_goods_decide()
