import re
import time

import yaml

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file


class ErpOrderStock:
    # 合作和代购库存不足走补货流程

    def __init__(self, rss):
        """
        :param account:  登录ERP账号
        :param psw:  登录ERP密码
        :param order_sn:  前台商城生成订单编号
        :param uesr:    前台商城生成订单编号的用户名称
        """
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.ERP_URL = data['ERP_URL']
        self.order_sn = getattr(Data, 'ic_order_sn')
        # self.order_sn = "S2023091293733"
        # self.uesr = getattr(Data, 'username')
        self.rss = rss
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }
        self.json_head = {"Content-Type": "application/json",
                          "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                          }

    def need_order_cancellation(self):
        """需求单生成采购订单号"""
        n = 0
        while True:
            try:
                search_url = "{}/Procurement/index".format(self.ERP_URL)
                search_body = {"keytype": "order_sn", "keyword": self.order_sn, "proc_type": 1, "warehouse_id": 0, "pageNum": 1,
                               "_search_likes": "*", "jump": "", "status": "", "order_grade": "", "lable_type": ""
                               }
                search_need_res = self.rss.post(url=search_url, data=search_body, headers=self.headers).text  # 搜索订单，获取need_id
                # logger.info(search_need_res)
                need_id = re.search(r'(<a href="/Procurement/detail\?id=)([0-9]*)', search_need_res).group(2)
                logger.info(f"搜索完成,获取到need_id: {need_id}")
                # 生成采购单号
                create_purchase_order_url = "{}/Procurement/compute/navTabId/Procurement".format(self.ERP_URL)
                create_purchase_order_body = {"id": need_id}
                create_purchase_order_res = self.rss.post(url=create_purchase_order_url,
                                                          data=create_purchase_order_body,
                                                          headers=self.headers).json()
                logger.info(f"执行结果为{create_purchase_order_res}")
                break
            except Exception as e:
                n += 1
                if n < 20:
                    logger.warning(
                        f"第 {n} 次,需求单列表没有找到销售单号:{self.order_sn},等待30秒后系统自动重试,错误信息:{e}")
                    time.sleep(30)

                else:
                    logger.error(f"需求单列表查找销售单号:{self.order_sn} 出错,请手动检查入库单是否存在")
                    raise ValueError
        time.sleep(2)


        # 获取生成的采购单号
        search_url = "{}/Procurement/index".format(self.ERP_URL)
        search_body = {"keytype": "order_sn", "keyword": self.order_sn, "proc_type": 1, "warehouse_id": 0, "pageNum": 1}
        search_need_res = self.rss.post(url=search_url, data=search_body, headers=self.headers,
                                   timeout=1000).text  # 搜索订单，获取purchase_id、purchase_sn
        purchase_id = re.search(r'(<a href="/purchase/detail\?id=)([0-9]*)', search_need_res).group(2)
        purchase_sn = \
        search_need_res.split(f'<a href="/purchase/detail?id={purchase_id}" target="navTab" title="')[1].split("明细")[0]
        logger.info(f"搜索完成,获取到生成的采购单号: {purchase_sn}，采购单号id为{purchase_id}")
        # 将生成的IC采购单号和id往Data里面作虚拟存储以【purchase_sn、purchase_id】命名以便后续提取
        setattr(Data, 'purchase_sn', purchase_sn)
        setattr(Data, 'purchase_id', purchase_id)
        logger.debug('=*' * 50)
        return self



if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
    rss = ErpLogin().login()
    ErpOrderStock(rss).need_order_cancellation()
