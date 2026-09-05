import re
import time
from datetime import datetime
import datetime as dt

import requests
import yaml


from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.OpenAPI_Order.pay_order import  PayOrder

# class DateEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, datetime):
#             return obj.strftime('%Y-%m-%d %H:%M:%S')
#         elif isinstance(obj, date):
#             return obj.strftime("%Y-%m-%d")
#         else:
#             return json.JSONEncoder.default(self, obj)

class ErpOrderHandle:


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
        # self.order_sn = "S2024011994169"
        self.rss = rss
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
                        }

    def order_handle(self):
        order_search_url = '{}/Orderinfo/index'.format(self.ERP_URL)
        try:
            logger.info(11)
            search_body = {'keytype': 'order_sn', 'keyword': self.order_sn, 'start_time': '2023-01-01'}
            logger.info(f"搜索订单编号: {self.order_sn}")
            search_res = self.rss.post(url=order_search_url, data=search_body, headers=self.headers,
                                   timeout=1000).text  # 搜索订单，获取order_id
            # print(search_res)
            # logger.info(re.search('(<a href="/Orderinfo/detail\?id=)([0-9]{6})', search_res))
            search_res_excerpt = search_res.split('<tr target="id"')[1].split('<div class="pages">')[0]
            order_id = re.search('(<a href="/Orderinfo/detail\?id=)([0-9]*)', search_res).group(2)
        except IndexError:
            logger.info(12)
            search_body = {'keytype': 'order_sn', 'keyword': self.order_sn, 'company': '2804887'}
            logger.info(f"搜索订单编号: {self.order_sn}")
            search_res = self.rss.post(url=order_search_url, data=search_body, headers=self.headers,
                                   timeout=1000).text  # 搜索订单，获取order_id
            # print(search_res)
            # logger.info(re.search('(<a href="/Orderinfo/detail\?id=)([0-9]{6})', search_res))
            search_res_excerpt = search_res.split('<tr target="id"')[1].split('<div class="pages">')[0]
            order_id = re.search('(<a href="/Orderinfo/detail\?id=)([0-9]*)', search_res).group(2)
        print(order_id)
        # 新增销售
        add_sale_url = "{}/Orderinfo/editFollowUserMore/navTabId/Orderinfo".format(self.ERP_URL)
        add_sale_body = {"id": order_id, f"sale_uid[{order_id}]": 704, "sale_list_all": 0}
        self.rss.post(url=add_sale_url, data=add_sale_body, timeout=1000)
        # logger.info(f"执行结果：{add_sale_res}")
        order_details_url = self.ERP_URL + f'/Orderinfo/detail?id={order_id}'
        logger.info(f"进入订单明细列表")
        order_detail_res = self.rss.get(url=order_details_url, headers=self.headers).text  # 获取订单明细id
        order_detail_match = re.compile('(<span><a href="/RecivePay/detail\?id=)([0-9]*)').search(order_detail_res)
        order_detail_id = ""
        if order_detail_match:
            order_detail_id = re.search('(<span><a href="/RecivePay/detail\?id=)([0-9]*)', order_detail_res).group(2)
        elif order_detail_match == None:
            logger.info("执行添加货期备注")
        logger.info(f"订单明细获取完成，拿到订单明细id: {order_detail_id}")
        if "待确认" in search_res_excerpt:
            logger.info(f"订单号：{self.order_sn}状态存在待确认状态")
            order_status_match = re.compile('(<li><a class="edit" href="/Orderinfo/confirm/id/{}/navTabId/SaleOrderDetail/ordertype/1\?type=org" target="dialog" title="选择部门"  width="450"><span>)([\u4e00-\u9fa5]*)(</span>)'.format(order_id)).search(
                order_detail_res)
            if order_status_match:
                order_status = re.search('(<li><a class="edit" href="/Orderinfo/confirm/id/{}/navTabId/SaleOrderDetail/ordertype/1\?type=org" target="dialog" title="选择部门"  width="450"><span>)([\u4e00-\u9fa5]*)(</span>)'.format(order_id), order_detail_res).group(2)
                if order_status == "确认订单":
                    logger.info(order_status)
                    sale_order_url = "{}/Orderinfo/confirm/id/{}/navTabId/SaleOrderDetail/ordertype/1?org_id={}".format(self.ERP_URL, order_id, 307)
                    sale_order_res = self.rss.post(url=sale_order_url, timeout=1000).json()
                    if self.order_sn in sale_order_res:
                        logger.info(f"确认订单成功，执行结果为{sale_order_res}")
            elif order_status_match == None:
                order_status = re.search('(<li><a class="edit" href="/Orderinfo/confirm/id/{}/navTabId/SaleOrderDetail/ordertype/2\?type=org" target="dialog" title="选择部门"  width="450"><span>)([\u4e00-\u9fa5]*)(</span>)'.format(order_id), order_detail_res).group(2)
                if order_status == "确认订单":
                    logger.info(order_status)
                    sale_order_url = "{}/Orderinfo/confirm/id/{}/navTabId/SaleOrderDetail/ordertype/2?org_id={}".format(self.ERP_URL, order_id, 307)
                    sale_order_res = self.rss.post(url=sale_order_url, timeout=1000).json()
                    if self.order_sn in sale_order_res:
                        logger.info(f"确认订单成功，执行结果为{sale_order_res}")
        goods_id = re.split('<a href="/Goods/detail/id/', order_detail_res)[1].split('/pass/1"')[0]
        order_details_goods_url = '{}/Goods/detail/id/{}/pass/1'.format(self.ERP_URL, goods_id)
        order_detail_goods_res = self.rss.get(url=order_details_goods_url, headers=self.headers).text  # 获取订单明细id
        erp_goods_sn = re.search('(<span class="ipt-tag">)(G[0-9]*)', order_detail_goods_res).group(2)
        logger.info(f"获取到订单：{self.order_sn}的型号的ERP编码：{erp_goods_sn}")
        # 将获取的ERP商品编码往Data里面作虚拟存储以【erp_goods_sn】命名以便后续提取
        setattr(Data, 'erp_goods_sn', erp_goods_sn)
        order_receipt_url = self.ERP_URL + f'/RecivePay/detail?id={order_detail_id}'
        time.sleep(60)
        logger.info(f"等待60s,获取收款单明细")
        order_verification_res = self.rss.get(url=order_receipt_url, headers=self.headers).text  # 获取核销金额
        order_money = re.search('(<label>合计：</label><span class="total">)([0-9]*\.?[0-9]+)',
                                order_verification_res).group(2)
        logger.info(f"收款单明细获取完成，成功拿到需要核销的金额: {order_money}")

        confirmation_writeOff_url = self.ERP_URL + f'/RecivePay/confirm/id/{order_detail_id}/navTabId/RecivePayDetail'
        logger.info(f"开始执行订单核销")
        confirmation_writeOff_body = {'money': order_money, 'remark': '测试订单'}
        self.rss.post(url=confirmation_writeOff_url, data=confirmation_writeOff_body, headers=self.headers)  # 执行核销
        logger.info(f"核销操作完成")

        time.sleep(10)
        order_detail = self.rss.get(url=order_details_url, headers=self.headers).text
        out_order = re.search('(rel="Removaledit">出库单)(OUT[0-9]*)', order_detail).group(2)
        otu_order_id = re.search('(href="/Removal/edit\?id=)([0-9]*)', order_detail).group(2)
        logger.info(f"出库单号: {out_order}")


        time.sleep(120)
        out_details_url = self.ERP_URL + f'/Removal/edit?id={otu_order_id}'
        out_details_res = self.rss.get(url=out_details_url).text
        out_order_status = re.search('(<label>订单状态：</label>)\s*(<span>)([\u4e00-\u9fa5]*)', out_details_res).group(3)
        # logger.info(re.search('(<label>订单状态：</label>)\s*(<span>)([\u4e00-\u9fa5]*)', out_details_res))
        if out_order_status == '复核中':
            logger.info(f"出库单复核中,可去wms操作出库")
            # 将生成的IC出库单号往Data里面作虚拟存储以【out_order】命名以便后续提取
            setattr(Data, 'out_order', out_order)
            out_order_businessTypeName = re.search('(<td>)([\u4e00-\u9fa5]*)(</td>)', out_details_res).group(2)
            logger.info(f"获取到出库单号商品定位的商品库存类型为：{out_order_businessTypeName}")
            setattr(Data, 'businessTypeName', out_order_businessTypeName)
        elif out_order_status == '待确认':
            # 将生成的IC出库单号往Data里面作虚拟存储以【out_order】命名以便后续提取
            setattr(Data, 'out_order', out_order)
            out_order_businessTypeName = re.search('(<td>)([\u4e00-\u9fa5]*)(</td>)', out_details_res).group(2)
            if out_order_businessTypeName == "代购储位":
                pass
            elif out_order_businessTypeName == "自营储位":
                out_order_stockStatus = re.search('(<td title="已生成补货需求，待自营PM确认">)([\u4e00-\u9fa5]*)(</td>)', out_details_res).group(2)
                logger.info(out_order_stockStatus)
                pass
            else:
                logger.error(f"出库单状态为:{out_order_status},无法进行出库")
                raise ValueError
        else:
            # setattr(Data, 'out_order', out_order)
            logger.error(f"出库单状态为:{out_order_status},无法进行出库")
            raise ValueError
        logger.debug('=*' * 50)
        return self
if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
    # rss = ErpLogin().login()
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin

    target_rss = SOOLogin("uat-e.hqchip.com", "AuthLogin").target_login()
    ErpOrderHandle(target_rss).order_handle()
