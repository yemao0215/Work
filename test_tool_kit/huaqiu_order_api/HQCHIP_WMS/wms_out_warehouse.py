import json
import re
import time

import jsonpath
import requests
import yaml
from bs4 import BeautifulSoup

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, account_yaml
class WmsOutWarehouse:

    def __init__(self, target_rss):
        self.wms_rss = target_rss
        self.pda_rss = requests.Session()
        self.json_head = {"Content-Type": "application/json"}
        self.out_order = getattr(Data, 'out_order', "")
        self.invoiceNo = getattr(Data, 'invoiceNo', "")
        self.smt_order = getattr(Data, 'smt_order', "")
        # self.out_order = "OUT00264486"
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.WMS_URL = data["WMS_URL"]
        self.apiEelec_url = data["apiEelec_url"]
        self.appconfig_id = data["appconfig_id"]
        self.courier_number = data["courier_number"]
        with open(account_yaml, 'r', encoding='utf-8') as yamlfile:
            account = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.warehouse_type = int(account["HQCHIP_GOODS"]["warehouse_id"])


    def wms_pick(self):
        """
        wms拣货单列表
        :param out_order: erp出库单号 out开头
        :return:
        """
        logger.info(self.out_order)
        select_store_url = self.WMS_URL + f'/wms/base/store/selectStore?storeCode={self.warehouse_type}'  # 选择仓库 2：东莞仓，8：长沙仓
        self.wms_rss.get(url=select_store_url)
        logger.info(f"选择东莞仓 storeCode={self.warehouse_type}")

        order_pick_url = '{}/wms/warehouse/transLocationBill/queryPickingList'.format(self.WMS_URL)  # 访问拣货单列表
        order_pick_body = {"originalNumber": self.out_order, "sourcebillnumber": self.invoiceNo, "smtOrderSn": self.smt_order, "type": self.warehouse_type}
        n = 0
        while True:
            try:
                pick_res = self.wms_rss.post(url=order_pick_url, json=order_pick_body, headers=self.json_head).json()
                pick_id = jsonpath.jsonpath(pick_res, '$..id')[0]
                sourcebillnumber = jsonpath.jsonpath(pick_res, '$..sourceBillNumber')[0]
                originalnumber = jsonpath.jsonpath(pick_res, '$..originalNumber')[0]
                self.sourcebillnumber = sourcebillnumber
                self.originalNumber = originalnumber
                logger.info(f"第{n+1}次访问拣货单列表,获取到pick_id:{pick_id},sourcebillnumber:{sourcebillnumber},originalnumber:{originalnumber}")
                break
            except Exception as e:
                n += 1
                if n < 6:
                    logger.warning(f"第 {n} 次,拣货单列表没有找到出库单:{self.out_order},等待30秒后系统自动重试,错误信息:{e}")
                    time.sleep(30)
                else:
                    logger.error(f"拣货单列表查找出库单:{self.out_order} 出错,请手动检查出库单是否存在")
                    raise ValueError
        time.sleep(2)
        pick_details_url = '{}/wms/warehouse/locationBillDetail/page'.format(self.WMS_URL)  # 拣货单明细
        pick_details_body = {"billId": pick_id, "counted": True}
        pick_details_res = self.wms_rss.post(url=pick_details_url, json=pick_details_body, headers=self.json_head).json()
        time.sleep(10)
        logger.info(f"返回的拣货单明细:{pick_details_res}")
        # distributionLabel = jsonpath.jsonpath(pick_details_res, '$..distributionLabel')[0]
        # logger.info(f"访问拣货单明细,第一次获取到distributionLabel:{distributionLabel}")
        # resultinfo = pick_details_res["result"]
        # logger.info(resultinfo)
        distributionLabels = jsonpath.jsonpath(pick_details_res, '$..distributionLabel')
        goodsCode = jsonpath.jsonpath(pick_details_res, '$..goodsCode')
        # for i in range(len(resultinfo)):
        #     distributionLabels.append(resultinfo[i]["distributionLabel"])
        logger.info(f"访问拣货单明细,第一次获取到distributionLabel列表为:{distributionLabels}")
        for i in range(len(distributionLabels)):
            if distributionLabels[i] is None:
                time.sleep(3)
                inventory_list_search_url = "{}/wms/warehouse/inventory/queryInventoryPage".format(self.WMS_URL)
                inventory_list_search_body = {"goodsInfo": goodsCode[i], "pageNum": 1, "pageSize": 50, "storeId": 1}
                inventory_list_search_res = self.wms_rss.post(url=inventory_list_search_url, json=inventory_list_search_body,headers=self.json_head).json()
                # print(inventory_list_search_res)
                resultInfo = inventory_list_search_res["result"]
                if resultInfo == []:
                    logger.info(f"订单：{self.out_order}的型号编码{goodsCode}在wms不存在")
                else:
                    ids = []
                    for i in range(len(resultInfo)):
                        ids.append(resultInfo[i]["id"])
                    logger.info(ids)
                    generate_label_url = "{}/wms/warehouse/inventory/printInventoryLabelByInvId".format(self.WMS_URL)
                    generate_label_body = ids
                    generate_label_res = self.wms_rss.post(url=generate_label_url, data=generate_label_body, headers=self.json_head).json()
                    logger.info(generate_label_res)
                    logger.info("开始执行手动分配")
                    manual_assign_url = "{}/wms/warehouse/transLocationBill/shelvesDistribution".format(self.WMS_URL)
                    manual_assign_body = {"billId": pick_id}
                    manual_assign_res = self.wms_rss.post(url=manual_assign_url, json=manual_assign_body, headers=self.json_head).json()
                    result = manual_assign_res["result"]
                    if result == True:
                        logger.info("执行手动分配成功")
                        pick_details_res = self.wms_rss.post(url=pick_details_url, json=pick_details_body, headers=self.json_head).json()
                        # distributionLabel = jsonpath.jsonpath(pick_details_res, '$..distributionLabel')[0]
                        resultinfo = pick_details_res["result"]
                        # distributionLabels = []
                        for i in range(len(resultinfo)):
                            distributionLabels.append(resultinfo[i]["distributionLabel"])
                    logger.info(f"访问拣货单明细,第二次获取到distributionLabel列表为:{distributionLabels}")
        self.distributionLabel = distributionLabels
        logger.debug('=*' * 50)
        # 将生成的WMS预出库单号【sourcebillnumber】往Data里面作虚拟存储以【sourcebillnumber】命名以便后续提取
        setattr(Data, 'sourcebillnumber', sourcebillnumber)
        # 将生成的WMS预出库单号里面商品标签【distributionLabels】往Data里面作虚拟存储以【distributionLabels】命名以便后续提取
        setattr(Data, 'distributionLabels', distributionLabels)
        return self

    def wms_pack(self, is_pack='pack_completed', is_out=None):
        """wms打包操作+出库"""
        # self.sourcebillnumber = "DO230915000003"
        self.sourcebillnumber = getattr(Data, 'sourcebillnumber')
        self.out_order = getattr(Data, 'out_order', "")
        self.invoiceNo = getattr(Data, 'invoiceNo', "")
        self.smt_order = getattr(Data, 'smt_order', "")
        pack_url = self.WMS_URL + f'/wms/business/outboundBill/getPackOutboundBillByShipBillCode?shipBillCode={self.sourcebillnumber}'
        logger.info(f"wms执行打包操作,sourcebillnumber:{self.sourcebillnumber}")
        logger.info(f"等待五秒钟,让出库单打包信息同步到wms")
        time.sleep(5)
        pack_res = self.wms_rss.get(url=pack_url).json()  # 打包
        logger.info(f"打包步骤1完成,返回结果:{pack_res}")
        pack_id = jsonpath.jsonpath(pack_res, '$..id')[0]
        time.sleep(1)
        if is_pack == "pack_completed":
            pack_url2 = self.WMS_URL + f'/wms/business/outboundBillDetail/findByInvoiceNo?invoiceNo={self.sourcebillnumber}'
            pack_res2 = self.wms_rss.get(url=pack_url2).json()  # 打包2
            logger.info(f"打包操作2返回结果:{pack_res2}")
            #
            # labelNumber = jsonpath.jsonpath(pack_res2, '$..labelNumber')[0]
            # outboundBillDetailId = jsonpath.jsonpath(pack_res2, '$..outboundBillDetailId')[0]
            # logger.info(f"打包步骤2完成,获取到labelNumber:{labelNumber},outboundBillDetailId:{outboundBillDetailId}")
            resultInfo = pack_res2["result"]
            logger.info(resultInfo)
            labelNumbers = []
            outboundBillDetailIds = []
            for i in range(len(resultInfo)):
                labelNumbers.append(resultInfo[i]["labelNumber"])
                outboundBillDetailIds.append(resultInfo[i]["outboundBillDetailId"])
            logger.info(f"打包步骤2完成,获取到labelNumber列表:{labelNumbers},outboundBillDetailId:{outboundBillDetailIds}")
            time.sleep(1)

            for m in range(len(labelNumbers)):
                labelNumber = labelNumbers[m]
                pack_url3 = self.WMS_URL + f'/wms/business/outboundBillDetail/checkLabelNumber?invoiceNo={self.sourcebillnumber}&labelNumber={labelNumber}'
                pack_res3 = self.wms_rss.get(url=pack_url3)  # 打包3
                logger.info(f"打包步骤3-第{m+1}商品完成,返回结果:{pack_res3.json()}")
            time.sleep(1)

            pack_url4 = '{}/wms/business/shipping/package'.format(self.WMS_URL)
            pack_body = {"outboundBillDetailIds": outboundBillDetailIds}
            pack_res4 = self.wms_rss.post(url=pack_url4, json=pack_body, headers=self.json_head)  # 打包4
            logger.info(f"打包步骤4完成,返回结果:{pack_res4.json()}")
            time.sleep(1)
        else:
            logger.info('不需要打包操作')
        if is_out == None:
            get_waybill_number_url = '{}/wms/base/carrier/list'.format(self.WMS_URL)
            get_waybill_number_res = self.wms_rss.post(url=get_waybill_number_url, json={}, headers=self.json_head).json()  # 获取运单号列表
            logger.info(f"开始获取运单号")
            settle_account = ''
            for i in get_waybill_number_res['result']:
                if i['name'] == '顺丰速运':
                    settle_account = i['settleAccount']
                    logger.info(f"获取到顺丰速运的单号:{settle_account}")
                    break
            else:
                logger.error(f"没有找到顺丰速运单号")

            generate_waybill_number_url = self.WMS_URL + f'/wms/business/outboundBill/get?id={pack_id}'
            waybill_number = self.wms_rss.get(url=generate_waybill_number_url).json() # 生成运单号
            logger.info(f"生成运单号,返回结果:{waybill_number}")
            time.sleep(1)

            submit_pack_url = '{}/wms/business/shipping/createTrackNumber'.format(self.WMS_URL)
            submit_pack_body = {"storeId": "1", "storeCode": "2", "carrier": "顺丰速运", "carrierCode": "1", "packageNum": 1, "expressType": 1,
                                "outboundBillIds": [pack_id], "trackNumber": "932003300148", "weight": "1", "payType": "1", "monthlyCard": settle_account}
            waybill_number_result = waybill_number['result']
            print(waybill_number_result)
            for m in waybill_number_result:
                if waybill_number_result[m] == '客户自提':
                    logger.info(f"出库单：{self.out_order}为自提出库单，更改相关参数")
                    submit_pack_body["carrier"] = '客户自提'
                    submit_pack_body["carrierCode"] = '100'
                    submit_pack_body["trackNumber"] = ''
                    submit_pack_body["monthlyCard"] = ''
                    submit_pack_body["weight"] = '0'
            submit_pack_res = self.wms_rss.post(url=submit_pack_url, json=submit_pack_body, headers=self.json_head).json()  # 打包出库
            logger.info(f"打包出库,返回结果:{submit_pack_res}")
            ret_code = jsonpath.jsonpath(submit_pack_res, '$.retCode')[0]
            if ret_code == 0:
                logger.info(f"订单成功完成出库,等待erp数据同步")
            else:
                logger.error(f"订单出库失败,失败信息:{jsonpath.jsonpath(submit_pack_res, '$.retMsg')[0]}")
                logger.debug('=*' * 50)
        return self

    def interface_log_search(self):
        """接口日志查询"""
        time.sleep(5)
        interface_log_search_url = "{}/wms/business/interfacelog/page".format(self.WMS_URL)
        interface_log_search_body = {"businessNo": self.out_order, "counted": True, "wmsStatus": "", "pageNum": 1, "pageSize": 20}
        # interface_log_search_res = self.wms_rss.post(url=interface_log_search_url, json=interface_log_search_body, headers=self.json_head).json()
        # resultInfo = interface_log_search_res["result"]
        # if resultInfo != []:
        #     logger.error("接口推送失败，请检查推送接口报错信息")
        #     receiveContent = resultInfo[0]["receiveContent"]
        #     receiver = resultInfo[0]["receiver"]
        #     logger.info(f"接口推送单号：{self.out_order}至目标系统：{receiver} 失败，返回错误信息：{receiveContent}")
        # else:
        #     logger.info("接口推送成功")
        while True:
            i = 0
            interface_log_search_res = self.wms_rss.post(url=interface_log_search_url, json=interface_log_search_body, headers=self.json_head).json()
            total_num = jsonpath.jsonpath(interface_log_search_res, '$..total')
            receiver = jsonpath.jsonpath(interface_log_search_res, '$..receiver')
            if int(total_num[0]) > 0:
                msgInfo = jsonpath.jsonpath(interface_log_search_res, '$..receiveContent')
                # logger.info(msgInfo)
                if msgInfo[0]["retMsg"] == "出库单反馈更新成功!" and msgInfo[1]["retCode"] == 0:
                        logger.info(f"接口推送单号：{self.out_order}至目标系统：{receiver[0]} 成功")
                        break
                else:
                    i += 1
                    if i > 1:
                        logger.info(f"接口推送单号：{self.out_order}至目标系统：{receiver[0]} 失败，返回错误信息：{msgInfo[0]}")
                        break
        return self

    def wms_express_update(self):
        """更改快递单号"""
        search_url = "{}/wms/business/outboundBill/page".format(self.WMS_URL)
        search_body = {"originalNumber": self.out_order, "counted": True, "storeCode": "2", "pageNum": 1, "pageSize": 20}
        search_res = self.wms_rss.post(url=search_url, json=search_body, headers=self.json_head).json()
        billId = jsonpath.jsonpath(search_res, "$..id")
        for i in billId:
            billId_msg_url  = "{}/wms/business/trackNumberLog/list".format(self.WMS_URL)
            billId_msg_body = {"billId": i, "billType": 1}
            billId_msg_res = self.wms_rss.post(url=billId_msg_url, json=billId_msg_body, headers=self.json_head).json()
            logger.info(billId_msg_res)
            monthlyCard = jsonpath.jsonpath(billId_msg_res, "$..monthlyCard")[-1]
            payType = jsonpath.jsonpath(billId_msg_res, "$..payType")[-1]
            # storeCode = jsonpath.jsonpath(billId_msg_res, "$..storeCode")[-1]
            storeId = jsonpath.jsonpath(billId_msg_res, "$..storeId")[-1]
            packageNum = jsonpath.jsonpath(billId_msg_res, "$..packageQuantity")[-1]
            weight = jsonpath.jsonpath(billId_msg_res, "$..weight")[-1]
            courier_number_url = "{}/express/query.json?appid={}&version=2.0&number={}".format(self.apiEelec_url, self.appconfig_id, self.courier_number)
            logger.info(courier_number_url)
            courier_number_res = self.wms_rss.get(url=courier_number_url).json()
            list = courier_number_res["data"]["list"]
            trackNumber = 'SF7444476820729'
            if list != []:
                logger.info("----")
                trackNumber = self.courier_number
            billId_express_update_url = "{}/wms/business/shipping/updateTrackNumber".format(self.WMS_URL)
            billId_express_update_body = {"carrier": "顺丰速运", "carrierCode": "1", "expressType": 1, "storeCode": "2",
                                          "monthlyCard": monthlyCard, "payType": payType, "storeId": storeId, "weight": weight,
                                           "packageNum": packageNum, "outboundBillIds": [i], "trackNumber": trackNumber
                                          }
            billId_express_update_res = self.wms_rss.post(url=billId_express_update_url, json=billId_express_update_body, headers=self.json_head).json()
            logger.info(billId_express_update_res)
            return self
    def promise_tm_obtain(self):
        """获取预计到货时间---沙箱"""
        courier_number_url = "{}/express/expressArrivalTime.json?searchNos={}&type=sfexpress".format(self.apiEelec_url, self.courier_number)
        logger.info(courier_number_url)
        courier_number_res = self.wms_rss.get(url=courier_number_url).json()
        promise_tm_result = courier_number_res['data']['data'][0]
        for k in promise_tm_result:
                if k == 'promiseTm':
                    if promise_tm_result[k] != "":
                        promise_tm = promise_tm_result[k]
                        print(f"快递单号: {self.courier_number}的预计到货时间为{promise_tm}")
                else:
                    if k == 'extmsg':
                        print(f"快递单号: {self.courier_number}的预计到货时间为为空，原因为：{promise_tm_result[k]}")
        return self
    def sandbox_express_create(self):
        '''沙箱顺丰快递单号生成----仅限内网'''
        self.target_rss = requests.session()
        soo_login_url = "https://dev-auth.huaqiu.com/orgauth/login"
        soo_account = {"account": "admin", "password": "12345678", "securityCode": "123", "isBind": 1}
        soo_login_res = self.target_rss.post(url=soo_login_url, json=soo_account, headers=self.json_head).json()
        print(f"登录完成，{soo_login_res}")

        url = "https://dev-auth.huaqiu.com/orgauth/getAuthToken?"
        target_login_connect_url = url + f"url=pcb.elecfans.net"
        target_rss = self.target_rss.get(url=target_login_connect_url).json()
        print(target_rss)
        self.token = target_rss['result']
        print(f"获取重定向系统(https://pcb.elecfans.net)的登录token:{self.token}")
        target_login_url = f'https://pcb.elecfans.net/hqjfpcb/OrgAuth/ssoLogin?authToken={self.token}'
        logger.info(f"打印组成目标系统登录地址：{target_login_url}")
        target_login_res = self.target_rss.get(url=target_login_url)
        print(target_login_res)
        logger.info(f"获取到登录cookie")

        pcb_delivery_url = "https://pcb.elecfans.net/hqjfpcb/Delivery/index"
        pcb_delivery_body = {"pageNum": 1, "unship": 1, "time_type": "shippingtime"}
        pcb_delivery_res = self.target_rss.post(url=pcb_delivery_url, data=pcb_delivery_body).text
        order_id_matches = re.findall(r'<input type="checkbox" name="id" value="([0-9]*)', pcb_delivery_res)
        # 获取页面列表表格关键字段
        soup = BeautifulSoup(pcb_delivery_res, 'html.parser')
        table = soup.find('tbody')
        rows = table.find_all('tr')
        pbid_column = []
        stock_number_column = []
        # for row in rows[1:]: # 跳过表头
        for row in rows:  #不跳过表头
            cells = row.find_all('td')
            pbid_column.append(cells[5].text)
            stock_number_column.append(cells[14].text)
        for i in range(len(order_id_matches)):
            if pbid_column[i] != '':
                logger.info(f"此订单号为：{order_id_matches[i]}")
                if stock_number_column[i] == "0":
                    simulate_inn_stokc_url = "https://pcb.elecfans.net/test/putway?id={}&qty=50".format(order_id_matches[i])
                    simulate_inn_stock_res = self.target_rss.get(url=simulate_inn_stokc_url).text
                    print(simulate_inn_stock_res)
                    stock_number_column[i] = "50 pcs"
                option_express_url = "https://pcb.elecfans.net/hqjfpcb/Delivery/set_wl"
                option_express_body = {"id": order_id_matches[i], "wl": "顺丰快递"}
                option_express_res = self.target_rss.post(url=option_express_url, data=option_express_body).json()
                print(option_express_res)
                # 操作发货
                # 操作点击发货按钮
                operations_delivery_url = "https://pcb.elecfans.net/hqjfpcb/delivery/ajaxConfirmMessage"
                operations_delivery_body = {"order_id": order_id_matches[i]}
                operations_delivery_res = self.target_rss.post(url=operations_delivery_url, data=operations_delivery_body).json()
                print(operations_delivery_res)
                if "确认是否需要发货。点击确认则继续发货" in operations_delivery_res["msg"]:
                    ship_url = "https://pcb.elecfans.net/hqjfpcb/Delivery/ship?id={}&together=0&ind_oids=".format(order_id_matches[i])
                    ship_res = self.target_rss.post(url=ship_url).json()
                    print(ship_res)
                    if "设置顺丰快件类型" in ship_res["title"]:
                        ship_setting_url = "https://pcb.elecfans.net/hqjfpcb/Delivery/ship_setting/type/sf/id/{}/together/0".format(order_id_matches[i])
                        ship_setting_res = self.target_rss.get(url=ship_setting_url).text
                        need_number = re.search(r'订单量：(\d+) pcs', ship_setting_res).group(1)
                        stock_number = re.search(r'(\d+) pcs', stock_number_column[i]).group(1)
                        if int(need_number) > int(stock_number):
                            residue_need_number = int(need_number) - int(stock_number)
                            simulate_inn_stokc_url = "https://pcb.elecfans.net/test/putway?id={}&qty=50".format(order_id_matches[i], residue_need_number)
                            simulate_inn_stock_res = self.target_rss.get(url=simulate_inn_stokc_url).text
                        ship_confirm_url = "https://pcb.elecfans.net/hqjfpcb/Delivery/ship/navTabId/Delivery"
                        ship_confirm_body = {"id": order_id_matches[i], "together": 0, "shipping_cid": 17, "express_type": 1, "pay_method": 1,
                                             "parcel_quantity": 1, f"ship_num[{order_id_matches[i]}]": need_number, f"box_num[{order_id_matches[i]}]": 1,
                                             f"ship_finished[{order_id_matches[i]}]": 1, "cargo_total_weight": 3.2000, "ajax": 1,"is_iframe": 1}
                        sandbox_express_create_res = self.target_rss.post(url=ship_confirm_url, data=ship_confirm_body).json()
                        wlid = sandbox_express_create_res["wlid"]
                        logger.info(f"订单号： {order_id_matches[i]}发货后生成沙箱快递单号为：{wlid}")
            break
        return self



            

if __name__ == '__main__':
    from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
    from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_pick import PdaPick
    from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_login import PdaLogin
    target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
    WmsOutWarehouse(target_rss).wms_pick()
    pda_rss = PdaLogin().pda_login()
    PdaPick(pda_rss).pda_pick()   # 预出库单  商品标签
    # WmsOutWarehouse(target_rss).wms_pack()
    # WmsOutWarehouse(target_rss).interface_log_search()
    WmsOutWarehouse(target_rss).promise_tm_obtain()