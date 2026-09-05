import re
import yaml
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml


class ErpStockSelect:


    def __init__(self, rss):
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.warehouse_type = int(account["HQCHIP_GOODS"]["warehouse_id"])
        self.number = int(account["HQCHIP_GOODS"]["number"])
        # self.goods_no = getattr(Data, 'erp_goods_sn')
        self.goods_no = "G5058257"
        self.erp_rss = rss
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
    def erp_out_goods_decide(self):
        """判断库存是否满足出库"""
        warehouse_name = ''
        if self.warehouse_type == 2:
            warehouse_name = "深圳华秋东莞仓"
        elif self.warehouse_type == 8:
            warehouse_name = "长沙仓"
        search_url = "{}/WmsLocationGoods/index".format(self.ERP_URL)
        search_body = {"keytype": "goods_sn", "keyword": self.goods_no, "warehouse_id": self.warehouse_type}
        search_res = self.erp_rss.post(url=search_url, data=search_body, headers=self.headers, timeout=1000).text
        # re.findall 匹配多个定位值并且打印出成一个list列表形式
        # (<!--<td>Array</td>-->)\s*(<td>(.*?)</td>)\s*(<td>)([0-9]*) 表示的意思为搜索获取片段<!--<td></td>-->的之后前两个td标签区域
        goods_stock_match = re.findall(r'(<!--<td></td>-->)\s*(<td>(.*?)</td>)\s*(<td>)([0-9]*)', search_res, re.DOTALL)
        logger.info(goods_stock_match)
        goods_stock_sale_num = []
        for i in range(len(goods_stock_match)):
            goods_stock_sale_num.append(goods_stock_match[i][-1])
        logger.info(f"获取到可用库存list列表为：{goods_stock_sale_num}")
        stock_sale_count = 0
        for m in range(len(goods_stock_sale_num)):
            stock_sale_count = stock_sale_count + int(goods_stock_sale_num[m])
        logger.info(f"循环计算得出可用库存总量为：{stock_sale_count}")
        if stock_sale_count >= int(self.number):
            erp_msg = f"商品编码：{self.goods_no}，符合ERP出库要求，此时商品编码：{self.goods_no}的仓库：{warehouse_name}的可用库存为：{stock_sale_count}"
            logger.info(erp_msg)
        else:
            erp_msg = f"商品编码：{self.goods_no}，不符合ERP出库要求，此时商品编码：{self.goods_no}的仓库：{warehouse_name}的可用库存为：{stock_sale_count}"
            logger.error(erp_msg)
        return erp_msg


if __name__ == '__main__':

    from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
    rss = ErpLogin().login()
    ErpStockSelect(rss).erp_out_goods_decide()

