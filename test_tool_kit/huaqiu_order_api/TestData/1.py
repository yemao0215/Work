# import ast
# import binascii
# from datetime import datetime
# import json
# import math
# import re
# from urllib.parse import quote
#
# import chardet
# import execjs
# import numpy as np
# import openpyxl
# import pandas
# import pinyin
# import requests
# # # #接口地址
# # # # url="https://account.cnblogs.com/account/checkphone"
# # # # #请求头
# # # # headers={  "content-type": "application/x-www-form-urlencoded; charset=UTF-8","user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36","origin": "https://account.cnblogs.com","referer": "https://account.cnblogs.com/signup/","sec-ch-ua": ""Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"","sec-ch-ua-mobile": "?0","sec-fetch-dest": "empty","sec-fetch-mode": "cors","sec-fetch-site": "same-origin","accept-encoding": "gzip, deflate, br","accept-language": "zh-CN,zh;q=0.9","content-length": "38","x-requested-with": "XMLHttpRequest","cookie": "_ga=GA1.2.507216764.1607696139; _gid=GA1.2.20006082.1607696139; __gads=ID=a0af3c482457fbd6:T=1607696140:S=ALNI_Ma4ZyAhdQj07-PWExgzpNmAJtGUoQ; .Cnblogs.Account.Antiforgery=CfDJ8AHUmC2ZwXVKl7whpe9_lasG7wDQV5i5vJUuukLmOI9F0itiUVrA3eVakBuojoT3IvqYSJ0yZWiUXeWpgLju3pbX7Rkf4bmX4mapSrqHPTAi75QT_gJjKjue0UkA0mkIioPJrYxe_IGFlUqHGyImDpU; .Cnblogs.Account.Session=CfDJ8AHUmC2ZwXVKl7whpe9%2FlavSYm3VRXi01KuhSFCTP5LWLHk5AaVajWlHycG8FtVGncRbtu7YIfV6dCPkid1l4r%2B5XuHI7lzVLUOgchpFbS5jbaqnc9P19JyRJAYN0DwJJx3acogHiJjcj9CwnUtYjHYdj2dgINAUjv%2BTTi779%2BVI; XSRF-TOKEN=CfDJ8AHUmC2ZwXVKl7whpe9_lavNd5Ha8h0P_4SPJrUu55X-8C12VbAql-CZ-bU8bgd0OTb5s2YU9SlUBqy4blAUiZggpbMQzpTyX8z_JQmfzKcDoflH9hIJNCNJQ16Po1JTDr8mcFuogzw4mTK2t5udd70; 4271c12252a544478175bac9772afc3d=99db986a-3708-4da5-b4c4-a98db5b8c355; SERVERID=daace45bf36fef87f4742d8b633fdae3|1607739455|1607739403"}
# # # # #请求参数
# # # # source_data={"PhoneNum": "1596463618","CountryCode": "+86"}
# # # # #打印结果
# # # # print(requests.post(url,source_data=source_data,headers=headers).json())
# # # import json
# # # from datetime import datetime
# # #
# # #
# # #
# # # import re
# # #
# # # # import requests
# # # #
# # # # url = "https://uat-e.hqchip.com/purchase/detail?id=459576&navTabId=PurchaseDetail"
# # # # # body = { "keytype": "plan_sn", "keyword": "SUP0028292"}
# # # # headers = {"Cookie":"visitor=9466d7d47f9ae9c27dcd412828a9479f; _ga=GA1.2.571724486.1677209505; sendRegisterCoupon=1; Hm_lvt_9c6fc722df7be37c5541a5d9ed1c2124=1678153271,1678247652,1678762118,1679314299; PHPSESSID=qienu78n769r2slvolbcle3v15; ICC_session_key=5bf4eb0ae56194dfcf6d0fc4ebd5fff0; Hm_lvt_4b7248f2d5bc464e6b35cdd795800722=1679015994,1679274958,1679626266,1679886267; Qs_lvt_284872=1679450388%2C1679450392%2C1679560099%2C1679626266%2C1679886267; Hm_lvt_6df77d80b496b34cbb807eeb82c01571=1679015994,1679274958,1679626266,1679886268; auth_token=14372699-edc9-5865-9416-cb098a1d5027-642107d7; union_id=4899764; ICC_auth_hqchip=avHix1UUc2UTg30i%252FLnLH%252BPsFmeKOW14OdkpGSKqqS%252BwTvyh8cMblyX4wkRxWy%252BZhpCq%252FiO%252FgApBGhhkmcQJRNIdigWnfCudpQPUQOV%252FjMANHsD0Bx%252FI3%252BOybs%252FLHS5cnCW1GXWeeOFeO4lbZ%252B0TsCrE0cmChHJIMei2r%252FGvYlojPJva9owgMhBy0F7isI5ne2GJP98hFAXokBLgt%252FwSin93oDkrK8We2arQ5f0vXH%252Bg6Y9%252BjkzIT%252Fw0cuE3%252BhiiZeV38rBf6NDpEX%252FbizsDAIq5MrAkw%252FLKR1WAzGR0zRcfOP5F0pMdQmT23%252B8Et5vkqYyDZA%252BB2jIaZDEMdy%252B6Fdi%252FvdTCGzfa%252BCUFKTmOr0u37u2fBUIjz8%252FOx%252BXdSm8zfe1XAsv%252F1KZEAX%252Fhomv1xiGDXGQv22CzAcUBkMMrVN3%252FiS4RzQUuXkHDOqZQ32bnqyvF1MPOpv8xfxvMV7u5GPkOz%252F2%252FK2NKG1%252BdYb1nyi7YmhVpeSBSvcbBTk4RiTi7iccInbt2c%252F6pLVaTWHKMDaWpEhjwq8BsZSdk3R5LjcAIPPIDg6IYXyTZINfFeq2%252FN0EfzDLCo97HX4N2%252BPy%252BoGBOmShyj3FY68i4grzPUj7IA0HKXGLhlC7zmTGYxxRdOdIT2ILH9xxnbRHYfaexe5H8UrMuHHYyJYZ0br0gWA3mOQ%252BcXavhpcavTuwZsogFT6cdGRtljHbn2Ek758DE7FtD6xLAqUX3al8cKik%252FI31wlmAKQDgOhs1JT93e8U4erZ1AdmKY9AP3kcLE8upIU%252FKA2pG2dzfBffjVrHDtA3veoyqM%252B0CDbxVo6%252FG09jTMTe9GF7FEjX0%252FN%252FD8bG2eSpiroDZCUarrh9o1zyWJGDxlSyN7PGLr6yC0OIeRN0ap6cZqRzVz45WjQOMtOvRMdMgA2mFF85qyGH04r5f8%252Bs8; ICC_session_key_verification=a%3A2%3A%7Bs%3A7%3A%22user_id%22%3Bs%3A7%3A%224899730%22%3Bs%3A11%3A%22session_key%22%3Bs%3A32%3A%225bf4eb0ae56194dfcf6d0fc4ebd5fff0%22%3B%7D; fingerprint=26f9047f459a22ab0a8c6628e3da3a97; ICC_new_key_history=WyIwNjAzIiwiY2hlbmNoZW4wMDYiLCIwNjAzQjEwNEs1MDBDVCIsIjE4LTJYWFgiLCIwNjAzMTExMTEiLCJFU1AtMTJGKEVTUDgyNjZNT0QpIiwiQkwtSFdDLUcxIiwiSFE4OTAiXQ%3D%3D; Hm_lpvt_6df77d80b496b34cbb807eeb82c01571=1679904825; Hm_lpvt_4b7248f2d5bc464e6b35cdd795800722=1679904825; Qs_pv_284872=2028434966155827700%2C3143327923566629000%2C4447324577933024000%2C1221866000552959700%2C1343369615982905600; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%224899764%22%2C%22first_id%22%3A%22186817a0cce5ac-0d12c512a5ed63-5437971-370944-186817a0ccf990%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%7D%2C%22%24device_id%22%3A%22186817a0cce5ac-0d12c512a5ed63-5437971-370944-186817a0ccf990%22%7D; authId=oFd9FczsLeculkwuaKQNeOW1c0oAUgLfkFwOjPD6vJaelP2ku2A6e%2BuGTTsHYT1xs9MfZsgX1wIYq64DHElrQw; logined_key=935e25067b30bedf1fe674c2fbe3c92a; purchase_tab_index=1"}
# # # # res = requests.get(url=url, headers=headers).text
# # # # inn_sn = re.search("(target="navTab" style="margin-left: 5px;" rel="addScan">)(IN[0-9]{8})", res).group(2)
# # # # # b = re.search("(<a  href="/Purchase/detail/id/)([0-9]{6})", res).group(2)
# # # # # c = re.search("(rel="PurchaseDetail" target="navTab"  title=")", res).group(1).split("明细" >")
# # # # # e = res.split("rel="PurchaseDetail" target="navTab"  title="")[1].split("明细" >")[0]
# # # # # print("rel="PurchaseDetail" target="navTab"  title="")
# # # # print(inn_sn)
# # #
# # # # if __name__ == "__main__":
# # # #     import json
# # # #     from datetime import datetime
# # # #
# # # #
# # # #
# # # #     item_id = old_user_id = customer_id =contact_id=predict_finish_time  = "1"
# # # #     import datetime
# # # #
# # # #     current_time = datetime.datetime.now()
# # # #     current_time_str = current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
# # # #     print(current_time_str)
# # # #     list = [{
# # # #         "confirm_id": "{}".format(item_id),
# # # #         "is_ordered": "2",
# # # #         "client_goods_sn": "1",
# # # #         "cat_name": "贴片电容",
# # # #         "brand_name": "Walsin",
# # # #         "goods_name": "0603B104K500CT",
# # # #         "goods_desc": "100000pF ±10% DC50VX7R",
# # # #         "encap": "603",
# # # #         "bit_number": "C3,C4,C5,C6",
# # # #         "dosage": "100",
# # # #         "other": "",
# # # #     }]
# # # #
# # # #     bom_order_1 = {
# # # #         "status": -1,
# # # #         "excel": list,
# # # #         "old_user_id": old_user_id,
# # # #         "customer_id": customer_id,
# # # #         "contact_id": contact_id,
# # # #         "predict_finish_time": predict_finish_time,
# # # #         "num": 5,
# # # #         "money_type": 1,
# # # #         "col_name[]": "client_goods_sn",
# # # #         "col_name[]": "cat_name",
# # # #         "col_name[]": "brand_name",
# # # #         "col_name[]": "goods_name",
# # # #         "col_name[]": "goods_desc",
# # # #         "col_name[]": "encap",
# # # #         "col_name[]": "bit_number",
# # # #         "col_name[]": "dosage",
# # # #         "col_name[]": "other",
# # # #         "is_ordered[" + item_id + "]": "2",
# # # #         "bom_category[" + item_id + "]": "",
# # # #         "ajax": "1",
# # # #         "is_iframe": "1",
# # # #     }
# # # #     bom_order_1 = json.dumps(bom_order_1)
# # # #     print(bom_order_1)
# # # # import requests
# # # # import json
# # # #
# # # # url = "https://uat-activity.hqchip.com/ecmc/coupon/couponList"
# # # #
# # # # payload = json.dumps({
# # # #   "pageNum": 1,
# # # #   "pageSize": 20
# # # # })
# # # # headers = {
# # # #   "Content-Type": "application/json",
# # # #   "Authorization": "Bearer {{token}}",
# # # #   "Cookie": "activityUATToken=AoNGg9yDNTta4D0sEjeZHs65YV/qOTKMh9xc7y3OFRtSDxeQyAWOPHrFs00UNx/C7cjmGsD0UrbUBOZnAag+gUNL8UYRoh1MuvV/spb/zYQmZMl0JmOHq1ifjGred272Y9js73OOiIeLILN4LYVVpapa9+FsOBABsrGG6rX4T1amvPqh3gvo8al7Y1xYrIl+CVHXJH//wBu2hot/8GdPywEJ8gQdRy3Sit8PY7+Ym3DO76atTbt2E9VZqWaXV66j3Cry2blFa5mOLSdE0xL7b3GibDInAYLOKon3nfkgLwiGz5kvnnZknW1/k3dLh8bBmEQPYdjcsK1txKU5L+iyTxUu4T55CkK8jdt/nGwYuRMKntyOuX/+hMKG/jXB0sHN"
# # # # }
# # # #
# # # # response = requests.request("POST", url, headers=headers, source_data=payload)
# # # # print(response.text)
# # # from openpyxl import Workbook, load_workbook
# # #
# # # # d =datetime.now().strftime("%Y-%m-%d %X")
# # # # print(d)
# # # # excel_path = "各省份最新疫情数据.xlsx"  #表格名称
# # # #
# # # # wb = Workbook(excel_path)             #创建xlsx表格
# # # # wb.save(excel_path)                   #保存
# # # #
# # # # wb = load_workbook(excel_path)        #导入表格，用于下面进行操作
# # # # wb.create_sheet("各省份最新疫情数据") #创建表名
# # # # ws = wb.active                        #激活
# # # #
# # # # for row in range(1,len(data_list)):   #控制行
# # # #     for column in range(1,6):         #控制列
# # # #         ws.cell(row,column).value = data_list[row-1][column-1]  #把数据传输到表格中
# # # #
# # # # wb.save(excel_path)                   #保存表格
# # # # wb.close()                            #关闭
# # # #
# # # # print("%s     保存成功！" % excel_path)
# # # # 加载excel，注意路径要与脚本一致
# # # from HC2018_admin.dgk_goods_means.dgk_goods_means import GoodsMeans
# # # from common.my_excel import MyExcel
# # # from common.my_path import stockup_dir
# # #
# # # #
# # # goods_msg =GoodsMeans("admin", "123456", "MF1/4W-680Ω±1% T52", "A Plus",2000).login().goods_means_list().goods_means_detil()
# # # # goods_brand_search_url = "https://uat-hc2019.hqchip.com/v1/goods/DgkGoods/ajaxGetProviderName"
# # # # goods_brand_keyword_body = {"provider_name": self.provider_name, "src_type": 0}
# # # # goods_list_headers = {"Content-Type": "application/json;charset=UTF-8", "Authorization": self.auth_token}
# # # # goods_brand_search_res = self.res.post(url=goods_brand_search_url, json=goods_brand_keyword_body, headers=self.goods_list_headers).json()
# # # # # print(goods_brand_search_res)
# # # # goods_brand_id = []
# # # # goods_brand_id = jsonpath.jsonpath(goods_brand_search_res, "$..brand_id")
# # # # for i in range(len(goods_brand_id)):
# # # #     goods_search_list_url = "https://uat-hc2019.hqchip.com/v1/goods/DgkGoods/findList"
# # # #     goods_search_list_body = {"goods_name": goods_name, "provider_name": provider_name}
# # # #     goods_search_list_res = rss.post(url=goods_search_list_url, json=goods_search_list_body, headers=self.goods_list_headers).json()
# # # #     print(goods_search_list_res)
# # #
# # #
# # # MyExcel(stockup_dir, "a1").excel_read(2, 1, goods_msg[0])
# # # MyExcel(stockup_dir, "b1").excel_read(2, 2, goods_msg[1])
# # # MyExcel(stockup_dir, "c1").excel_read(2, 3, goods_msg[2])
# # # MyExcel(stockup_dir, "d1").excel_read(2, 4, goods_msg[2])
# # # # wb = load_workbook("demo.xlsx")
# # # # # 激活excel表
# # # # sheet = wb.active
# # # #
# # # # # 向excel中写入表头
# # # # sheet["a1"] = "型号(必填)"
# # # # sheet["b1"] = "品牌(必填)"
# # # # sheet["c1"] = "包装类型"
# # # # sheet["d1"] = "包装数量"
# # # # sheet["e1"] = "采购价(含税,必填)"
# # # # sheet["f1"] = "采购数量(必填)"
# # # # sheet["g1"] = "交期 (必填)"
# # # # sheet["h1"] = "交货地(必填)"
# # # # sheet["i1"] = "需求仓(必填)"
# # # # sheet["j1"] = "DC"
# # # # sheet["k1"] = "供应商(必填)"
# # # # sheet["l1"] = "是否强制导入"
# # # # sheet["m1"] = "备货类型(必填)"
# # # # sheet["n1"] = "补备货"
# # # # sheet["o1"] = "客户ID(项目备货必填)"
# # # # sheet["p1"] = "项目编号(项目备货必填)"
# # # # sheet["q1"] = "备注"
# # # #
# # # # # 向excel中写入对应的value
# # # # for i in range(0):
# # # #         sheet.cell(row=i+2, column=1).value = goods_msg[0]
# # # #         sheet.cell(row=i+2, column=2).value = goods_msg[1]
# # # #         sheet.cell(row=i+2, column=3).value = goods_msg[2]
# # # #         sheet.cell(row=i + 2, column=4).value = goods_msg[3]
# # # #         sheet.cell(row=i + 2, column=5).value = "1"
# # # #         sheet.cell(row=i + 2, column=6).value = "4000"
# # # #         sheet.cell(row=i + 2, column=7).value = "3-7"
# # # #         sheet.cell(row=i + 2, column=8).value = "深圳华秋东莞仓"
# # # #         sheet.cell(row=i + 2, column=9).value = "深圳华秋东莞仓"
# # # #         sheet.cell(row=i + 2, column=10).value = "23+"
# # # #         sheet.cell(row=i + 2, column=11).value = "self-hqchip"
# # # #         sheet.cell(row=i + 2, column=12).value = "是"
# # # #         sheet.cell(row=i + 2, column=13).value = "常规备货"
# # # #         sheet.cell(row=i + 2, column=14).value = "补货"
# # # #         sheet.cell(row=i + 2, column=15).value = ""
# # # #         sheet.cell(row=i+2, column=16).value = ""
# # # #         sheet.cell(row=i + 2, column=17).value = "自动化测试"
# # #
# # #
# # #
# # #
# # # wb.save("demo.xlsx")
# # # print("数据写入成功！")
# # import json
# # import time
# # from time import sleep
# #
# # import jsonpath
# # import requests
# # from openpyxl.reader.excel import load_workbook
# #
# # from HQCHIP_SOO.login import SOOLogin
# # from common.loguru_logger import logger
# #
# # # wb = load_workbook("新建 Microsoft Excel 工作表.xlsx")
# # # sheet = wb.active
# # # sheet.cell(row=4, column=1).value = "11111"
# # # wb.save("新建 Microsoft Excel 工作表.xlsx")
# # # target_rss = SOOLogin("admin","12345678","uat-srm.huaqiu.com","partnermanage").target_login()
# # # upload_url = "https://uat-srm.huaqiu.com/partnermanage/partnerFile/upload"
# # # file = [("file", ("新建 Microsoft Excel 工作表.xlsx", open("C:\\Users\\WIN\Desktop\\自动化测试项目\\huaqiu_order_api\\新建 Microsoft Excel 工作表.xlsx", "rb"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))]
# # # stock_up_file_res = target_rss.post(url=upload_url, files=file).json()
# # # print(stock_up_file_res)
# # # multipartFile = stock_up_file_res["body"]
# # # body = {"goodType":1, "multipartFile":multipartFile, "supplierCode":"","supplierName": "测试供应商", "undercarriage": 1}
# # # url = "https://uat-srm.huaqiu.com/partnermanage/partnerSaleGoodsDetail/analysisExcel"
# # # res = target_rss.post(url=url, json=body).json()
# # # print(res)
# #
# # # json_head = {"Content-Type": "application/json"}
# # # target_rss.post(url=url,json=body,headers=json_head).json()
# #
# #
# #
# # import xlsxwriter as xw
# # import pandas as pd
# # import openpyxl as op
# #
# # # def get_data():
# # #     orderIds = [1, 2, 3]
# # #     items = ["A", "B", "C"]
# # #     myData = ["风犬少年的天空", "重启", "半泽直树"]
# # #     testData = [orderIds, items, myData]
# # #     return testData
# # #     # filename2 = "测试2.xlsx"
# # #     # filename3 = "测试3.xlsx"
# # #
# # #
# # # # xlsxwriter 一行一行写
# # # def xw_toexcel(source_data, file_name):
# # #     """ 通过 xlsxwriter 方式 """
# # #     # 创建工作簿
# # #     workbook = xw.Workbook(file_name)
# # #     # 创建子表
# # #     worksheet = workbook.add_worksheet("sheet")
# # #     # 激活表
# # #     worksheet.activate()
# # #     # 设置表头
# # #     title = ["序号", "等级", "名称"]
# # #     # 从A1单元格开始写入表头
# # #     worksheet.write_row("A1", title)
# # #     # 从第二行开始写入数据
# # #     i = 2
# # #     for j in range(len(source_data)):
# # #         insertData = [source_data[0][j], source_data[1][j], source_data[2][j]]
# # #         row = "A" + str(i)
# # #         worksheet.write_row(row, insertData)
# # #         i += 1
# # #     # 关闭表
# # #     workbook.close()
# # #
# # #
# # # def pd_toexcel(source_data, file_name):
# # #     """ pandas方式 """
# # #     # 用字典设置DataFrame所需数据
# # #     dfData = {
# # #         "序号": source_data[0],
# # #         "等级": source_data[1],
# # #         "名称": source_data[2]
# # #     }
# # #     # 创建DataFrame
# # #     df = pd.DataFrame(dfData)
# # #     # 存表，去除原始索引列（0,1,2...）
# # #     df.to_excel(file_name, index=False)
# # #
# # #
# # # def op_toexcel(source_data, file_name):
# # #     """ openpyxl方式 """
# # #     # 创建工作簿对象
# # #     wb = op.Workbook()
# # #     # 创建子表
# # #     ws = wb["Sheet"]
# # #     # 添加表头
# # #     ws.append(["序号", "等级", "名称"])
# # #     for i in range(len(source_data[0])):
# # #         d = source_data[0][i], source_data[1][i], source_data[2][i]
# # #         # 每次写入一行
# # #         ws.append(d)
# # #     wb.save(file_name)
# # #
# # #
# # # def main():
# # #     # xw_toexcel(get_data(), "测试1.xlsx")
# # #
# # #     # pd_toexcel(get_data(), "测试2.xlsx")
# # #
# # #     xw_toexcel(get_data(), "测试3.xlsx")
# # #
# # #
# # # if __name__ == "__main__":
# # #     main()
# # # pda_rss = requests.Session()
# # # json_head = {"Content-Type": "application/json"}
# # # pda_json_head = {"Content-Type": "application/json", "User-Agent": "okhttp/3.14.9", "Connection": "keep-alive"}
# # # wms_rss = SOOLogin("admin","12345678", "uat-wms.huaqiu.com", "wms/base").target_login()
# # # url = "https://uat-wms.huaqiu.com/wms/warehouse/shelvesBill/getshelvesbillpage"
# # # body = {"status": 1, "pageNum":1, "pageSize":100}
# # # res = wms_rss.post(url=url, json=body, headers=json_head).json()
# # # docCodeinfo = res["result"]
# # # docCodeinfo_count = len(res["result"])
# # # docCode = []
# # # logger.info(docCodeinfo_count)
# # # for i in range(docCodeinfo_count):
# # #     docCode.append(docCodeinfo[i]["sourceBillNumber"])
# # # for q in range(docCodeinfo_count):
# # #     theupper_list_url = "https://uat-wms.huaqiu.com/wms/warehouse/shelvesBill/getshelvesbillpage"  # 访问上架单列表
# # #     theupper_list_body = {"sourceBillNumber": docCode[q]}
# # #     n = 0
# # #     while True:
# # #         try:
# # #             order_warehousing_res = wms_rss.post(url=theupper_list_url, json=theupper_list_body,
# # #                                                       headers=json_head).json()
# # #             # print(order_warehousing_res)
# # #             theupper_id = jsonpath.jsonpath(order_warehousing_res, "$..id")[0]
# # #             theupper_code = jsonpath.jsonpath(order_warehousing_res, "$..code")[0]  #
# # #             print(f"第{n + 1}次访问上架单列表,获取到warehousing_id:{theupper_id},theupper_code:{theupper_code}")
# # #             break
# # #         except Exception as e:
# # #             n += 1
# # #             if n < 6:
# # #                 logger.warning(f"第 {n} 次,上架单列表没有找到上架单:{docCode},等待30秒后系统自动重试,错误信息:{e}")
# # #                 sleep(30)
# # #             else:
# # #                 logger.error(f"上架单列表查找上架单:{docCode} 出错,请手动检查上架单是否存在")
# # #                 raise ValueError
# # #     sleep(2)
# # #     labelNumber_url = "https://uat-wms.huaqiu.com/wms/warehouse/shelvesBill/getshelvesbilldetailpage"
# # #     labelNumber_body = {"id": theupper_id}
# # #     labelNumber_res = wms_rss.post(url=labelNumber_url, json=labelNumber_body, headers=json_head).json()
# # #     labelNumber_sn = jsonpath.jsonpath(labelNumber_res, "$..labelNumber")[0]
# # #     targetLocationCode = jsonpath.jsonpath(labelNumber_res, "$..targetLocationCode")[0]
# # #     labelNumber_sn = labelNumber_sn
# # #     targetLocationCode = targetLocationCode
# # #     logger.info(f"获取到上架商品的货品标签：{labelNumber_sn},库位：{targetLocationCode}")
# # #     pda_login = "https://uat-wms.huaqiu.com/wms/base/login"  # pda登录
# # #     pda_login_body = {"account": "admin", "password": "12345678"}
# # #     logger.info(f"开始执行pda登录,登录环境:{pda_login},登录账号密码:{pda_login_body}")
# # #     pda_login_res = pda_rss.post(url=pda_login, json=pda_login_body, headers=pda_json_head)
# # #     logger.info(f"pda登录完成,登录结果:{pda_login_res.json()}")
# # #     select_store_url = f"https://uat-wms.huaqiu.com/wms/base/store/selectStore?storeCode=2"
# # #     select_store_res = pda_rss.get(url=select_store_url, headers=pda_json_head)  # 选择仓库
# # #     logger.info(f"选择pda仓库:storeCode=2 东莞仓,返回结果:{select_store_res.json()}")
# # #     sleep(1)
# # #
# # #     theupper_headers = {"Content-Type": "x-www-from-urlencodeed", "User-Agent": "okhttp/3.14.9",
# # #                         "Connection": "keep-alive"}
# # #     # 上架步骤1：
# # #     theupper_labelNumber_url = f"https://uat-wms.huaqiu.com/wms/warehouse/pda/worktask/getShelvesTaskInfoByLabelNumber?labelNumber={labelNumber_sn}"
# # #     # theupper_labelNumber_body = {"labelNumber": self.labelNumber_sn}
# # #     # print(theupper_labelNumber_body)
# # #     pda_theupper_res1 = pda_rss.get(url=theupper_labelNumber_url, headers=theupper_headers).json()
# # #     logger.info(f"扫描商品标签成功，返回结果:{pda_theupper_res1}")
# # #     # 上架步骤2：
# # #     theupper_LocationCode_url = f"https://uat-wms.huaqiu.com/wms/warehouse/pda/worktask/confirmShevlesTask?locationCode={targetLocationCode}"
# # #     pda_theupper_res2 = pda_rss.get(url=theupper_LocationCode_url, headers=theupper_headers).json()
# # #     logger.info(f"扫描储位成功，返回结果:{pda_theupper_res2}")
# #
# # list_temp = [1]
# #
# # # print("方法1（推荐）：在Python中，False,0,"",[],{},()都视为假，因此可以直接进行逻辑运算。此方法效率最高。")
# # # if list_temp:  # 存在值即为真
# # #     a=True
# # # else:  # list_temp是空的
# # #     a= False
# # # if a == True:
# # #     print("----")
# # # timpestamp = int(time.time())
# # # logger.info(timpestamp)
# # #
# # # goods_list = [
# # #     {"out_goods_name": "0603L050YR", "qty": 10, "goods_id": 2500265801},
# # # ]
# # # invoice = {
# # #     "type": 1,
# # #     "inv_title": "刘权",
# # # }
# # # receive = {
# # #     "consignee": "刘权",
# # #     "province": 6,
# # #     "city": 77,
# # #     "district": 705,
# # #     "address": "深圳市福田区梅林街道梅秀璐1号",
# # #     "mobile": "15814783061",
# # #     "tel": "075512345678",
# # # }
# # # data = {
# # #     "goods_list": json.dumps(goods_list),
# # #     "invoice": json.dumps(invoice),
# # #     "receive": json.dumps(receive),
# # #     "shipping_type": 1,
# # #     "goods_type": 1,
# # #     "out_order_no": "YE20230522930010",
# # #     "product_num": "1",
# # # }
# # # print(data)
# #
# # import requests
# #
# # url = "https://uat-smt.hqchip.com/online/finish_new"
# #
# # payload = {"is_first_confirm": "0",
# # "shipping_id": "1",
# # "add_user_email": "15070739126@163.com",
# # "test_duration": "0",
# # "adjust_fee": "0",
# # "is_dodge_solder_joint": "false",
# # "custom_pcb_ban": "3",
# # "bom_material_type_number": "1",
# # "bom_order_amount": "0",
# # "is_program_burning": "0",
# # "patch_file": "/file/5/413093/ecba1ac36117f96c119d4d9dd421ba34/展台看点.zip",
# # "is_material_baking": "0",
# # "number": "3",
# # "gain_order_type": "0",
# # "is_assembly_weld": "0",
# # "pcb_send_smt": "1",
# # "is_plug": "1",
# # "splicing_number": "1",
# # "is_test": "0",
# # "old_patch_file": "",
# # "bom_purchase": "2",
# # "add_plat_form": "1",
# # "goods_name": "",
# # "is_pcb_ban": "0",
# # "pcb_file_name": "展台看点.zip",
# # "address_id": "4109",
# # "is_handwork_plug": "0",
# # "plug_number": "1",
# # "is_assemble": "0",
# # "weight": "",
# # "is_pcb_soft_board": "0",
# # "add_user_qq": "",
# # "single_or_double_technique": "1",
# # "jiaji_price": "0",
# # "tax_id": "",
# # "tmp_hash": "",
# # "bom_sn": "",
# # "tmp_status": "0",
# # "pcb_sn_file": "",
# # "user_id": "5146187",
# # "pcb_ban_width": "12",
# # "old_bom_file": "",
# # "patch_pad_number": "1",
# # "order_id": "0",
# # "application_sphere": "1",
# # "is_welding_wire": "0",
# # "city_id": "77",
# # "need_gangwang": "1",
# # "save_type": "1",
# # "is_steel_follow_delivery": "0",
# # "postscript": "",
# # "steel_type": "0",
# # "jiaji": "0",
# # "need_split": "0",
# # "is_accurate_price_type": "1",
# # "remark": "",
# # "shipping_pay_type": "1",
# # "invoicefee": "0",
# # "old_pcb_file": "",
# # "packing_type": "1",
# # "pcb_ban_height": "12",
# # "need_conformal_coating": "0",
# # "pcb_width": "0",
# # "smd_order_id": "0",
# # "add_user_tel": "15912757721",
# # "x_ray_number": "0",
# # "x_ray_unit_number": "0",
# # "pcb_file": "/file/5/413091/ecba1ac36117f96c119d4d9dd421ba34/展台看点.zip",
# # "pcb_height": "0",
# # "estimate_deliver": "36",
# # "bom_file": "https://uat-smt.hqchip.com/file/2/413092/e351b9918134f011e483af3d73d4a1d3/bom32.xls",
# # "assembly_production": "0",
# # "is_shipping_fee": "0",
# # "sidewidth": "false",
# # "bom_id": "",
# # "agreen_protocol": "True",
# # "expressage": "0",
# # "province_id": "6",
# # "smt_tmp_id": "3175",
# # "bom_file_name": "bom32.xls",
# # "pcb_sn_file_name": "",
# # "is_layout_cleaning": "0",
# # "vat_type": "3",
# # "patch_file_name": "展台看点.zip",
# # "add_user": "",
# # "is_increase_tinning": "0",
# # "inv_title": "undefined",
# # "shipping_name": "顺丰寄付",
# # "consignee_phone": "159127577210",
# # "pcb_sn": ""}
# # files=[
# #
# # ]
# # headers = {
# #   "Accept": "application/json, text/plain, */*",
# #   # "Accept-Language": "zh-CN,zh;q=0.9",
# #   # "Authorization": "",
# #   # "Cache-Control": "no-cache",
# #   # "Connection": "keep-alive",
# #   "Cookie": "sendRegisterCoupon=1; visitor=c3ba4eff82321d94c3b1397c19453a58; Hm_lvt_9c6fc722df7be37c5541a5d9ed1c2124=1685518466; fingerprint=31dcbc5feb01c51b66ed83f7be7566e6; _ga_MDD3ZMQYRW=GS1.1.1685676675.8.1.1685676710.0.0.0; _gid=GA1.2.1277827722.1685930006; Hm_lvt_4b7248f2d5bc464e6b35cdd795800722=1685581748,1685676642,1685930512,1686013868; Hm_lvt_6df77d80b496b34cbb807eeb82c01571=1685501427,1685676642,1685930512,1686013869; Hm_lpvt_6df77d80b496b34cbb807eeb82c01571=1686023662; Qs_lvt_284872=1685582716%2C1685614759%2C1685676641%2C1685930005%2C1686023663; ICC_history=2500330602; Qs_pv_284872=1346026706089273300%2C913120797007536900%2C4101050263705242000%2C2112189272225218000%2C2570231728650676000; _ga=GA1.2.15269848.1684912807; _ga_LN25H10JFV=GS1.1.1686038459.31.0.1686038459.0.0.0; ICC_new_key_history=WyJBQzA2MDNGUi0wNzEwS0wiLCIwNjAzIiwieGlhb3poZW4wMDIiLCIwNjAzQjEwMksxNjAiLCIzNjkyMC0wNjAzIiwiWEsyMDIyMTEyMyIsIlx1NTc4Ylx1NTNmNyBcdWZmMWEgQ0MxMjA2S0tYN1I4QkIxMDYgXHU4ZDM0XHU3MjQ3XHU3NTM1XHU1YmI5IFx1ZmYwOE1MQ0NcdWZmMDkgXHU1NGMxXHU3MjRjIFx1ZmYxYSBZYWdlbyggXHU1NmZkXHU1ZGU4ICIsIjA0MDIiXQ%3D%3D; Hm_lpvt_4b7248f2d5bc464e6b35cdd795800722=1686038852; ICC_session_key=80c0b894f480f055e7ec38cd549981c5; union_id=5146221; ICC_auth_hqchip=MGmR%252FBp8K3Yhv9UzJSGrthjlTSj2aQyhcawgY%252FiTP3lAVascibc25QnarUXHBdYkipmKras13k9BVWs1rls7x5wOfSRfY2sQR%252Ff4jgsAU2e%252Fs%252Fvgg9jl7AyUmZ1HES4IAUCTI2gb7FyTHeU35Rj2J11GakReKdzsflj6nxKHSvnLpvIhJ%252BOSnYthMTz4vX9RpojKCpnnTCQ62HV5ksSEwrurrkbaLPJ1OxkxVTjpl8H1DcTOug6MpoX9IkdWaOT4Tih0mcCvepW7yVeUTlHiG%252B7jaGi2PGeloOB6t9dluDlxBcdKBxtuY0Y2tgvUIo2IZh06W73hpZzGFGIhh65cmmALbc2hkLbSiFpfSCbeh%252FpWvsUQrhK2M3fB02JZLNfQ6S5Su6RO3rO14K%252Bwixo9%252BOZZl28I5IScjzkvTYSZhAg7Kk%252B8VRjNEWeJe9tj5x3Oq2BHkqTRVipLQ0ZokKHuGJMrN9zozrxriDpxVO1md6Kl5crT%252BkS%252FUw4OBQgbr9n0oOP6uBqvKiWoQZOQ5W%252FvhGD3nm8CwKJOWkMd%252BK9Oth%252FH7mBnRSZHyKBEpIzW%252FGAwe3jxBvbEqqJcCBpn7tTXIqSlC2VM%252BXkVMjTgfQNoQfyFLp4bUGzOmCnKRZ8x2eiGi%252FOGC8zk6kYx2d%252BhF%252FHmv%252B2r9RxYcb0HJHYHC4VIzDeTEeqlV%252BHrnTLv5I46NuMmDblFDxipJilj0gL0unZHuWRWivTY2f8u%252BgTraIRB3DS6dvwritNeO8Jr6%252BwpJsShjVbY4m4d6rjXAJiB9AApwKpeXUDyhYaq%252B8TLvBpu3ft8mh6lYBis3sd4tAIi5ac6Jq8N5dnQZvuhbmoMURQ1WTEPijg0aO8NQYvUk2L%252FU74ON%252BiatSlwPOzrZpjS5iHEQsT5cpxh0aUCCI9Mju3vpASSr%252F8cSbNgv5KrEkxEFiabSi4WH%252ByEi7enLP5zwaEA; ICC_hqcanal=https%3A%2F%2Fuat-passport.elecfans.com%2F; ICC_user_id=5146187; ICC_user_name=jf_15113305; ICC_session_key_verification=a%3A2%3A%7Bs%3A7%3A%22user_id%22%3Bs%3A7%3A%225146187%22%3Bs%3A11%3A%22session_key%22%3Bs%3A32%3A%2280c0b894f480f055e7ec38cd549981c5%22%3B%7D; ICC_union_cart_goods=1; PHPSESSID=3r8vvka0kk66u8825lcbdj35f6; SMT_user_id=5146187; SMT_user_name=jf_15113305; sdk_device_id=E9A27C082D650293CC048BE59A211DDA; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%225146221%22%2C%22%24device_id%22%3A%2218848960788fa9-0244000a2acb7d-26031a51-2073600-18848960789e58%22%2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_landing_page%22%3A%22https%3A%2F%2Fuat-smt.hqchip.com%2Fonline%3Fnumber%3D1%26patch_pad_number%3D1%26patch_material_type%3D1%26plug_number%3D1%22%7D%2C%22first_id%22%3A%2218848960788fa9-0244000a2acb7d-26031a51-2073600-18848960789e58%22%7D; sdk_session_corss=%7B%22utm_source%22%3A%22external%22%2C%22session_url%22%3A%22https%3A//uat-smt.hqchip.com/online/submitOrder%3Fid%3D3175%22%2C%22session_referrer%22%3A%22https%3A//uat-smt.hqchip.com/online%3Fnumber%3D1%26patch_pad_number%3D1%26patch_material_type%3D1%26plug_number%3D1%22%2C%22session_referrer_host%22%3A%22uat-smt.hqchip.com%22%7D; SMT_pcb_file=%2Ffile%2F5%2F413091%2Fecba1ac36117f96c119d4d9dd421ba34%2F%E5%B1%95%E5%8F%B0%E7%9C%8B%E7%82%B9.zip; SMT_bom_file=%2Ffile%2F2%2F413092%2Fe351b9918134f011e483af3d73d4a1d3%2Fbom32.xls; SMT_patch_file=%2Ffile%2F5%2F413093%2Fecba1ac36117f96c119d4d9dd421ba34%2F%E5%B1%95%E5%8F%B0%E7%9C%8B%E7%82%B9.zip; SMT_user_id=5146187; SMT_user_name=jf_15113305",
# #   # "Origin": "https://uat-smt.hqchip.com",
# #   # "Pragma": "no-cache",
# #   # "Referer": "https://uat-smt.hqchip.com/online/submitOrder?id=3175",
# #   # "Sec-Fetch-Dest": "empty",
# #   # "Sec-Fetch-Mode": "cors",
# #   # "Sec-Fetch-Site": "same-origin",
# #   # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
# #   # "sec-ch-ua": ""Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"",
# #   # "sec-ch-ua-mobile": "?0",
# #   # "sec-ch-ua-platform": ""Windows""
# # }
# #
# # response = requests.request("POST", url, headers=headers, data=payload, files=files).json()
# #
# # print(response)
# import urllib
#
# import requests
# import yaml
# from faker import Faker
# from xpinyin import Pinyin
#
# from huaqiu_order_api.common.my_path import encryption_order_dir
#
# # import requests
# #
# # url = "https://uat-e.hqchip.com/orderinfo/update/navTabId/SaleOrderDetail"
# #
# # payload = {"smt_order_id": "",
# #           "product_num": "1",
# #         "order_id": "301284",
# #         "company": "1",
# #         "place_delivery": "1",
# #         "shipping_strategy": "2",
# #         "commitment_time": "2023-06-28",
# #         "order_remark": "",
# #         "custom_sn": "YE20230627000096",
# #         "event_remark": "",
# #         "vat_type": "0",
# #         "users_vat_id": "-1",
# #         "inv_type": "2",
# #         "invoice_mode_type": "2",
# #         "recive_type": "2",
# #         "vat_registration_sn": "",
# #         "recive_consignee": "",
# #         "recive_mobile": "",
# #         "recive_province": "",
# #         "recive_city": "",
# #         "recive_district": "",
# #         "recive_address": "",
# #         "product_num": "1",
# #         "goods_name[]": "0603L050YR",
# #         "goods_id[]": "74106",
# #         "rec_id[]": "1490621",
# #         "self_stock[]": "0",
# #         "ic_goods_json[]": "",
# #         "warehouse_id[]": "0",
# #         "inv_desc[]": "电子元器件",
# #         "unit[]": "片",
# #         "supplier_id[]": "458",
# #         "sale_number[]": "10",
# #         "contact_delivery[]": "",
# #         "spec[]": "1",
# #         "removal_number[]": "0",
# #         "old_sale_price[]": "0.57630",
# #         "cost_price[]": "0.00000",
# #         "front_cn_cost_price[]": "0.38420",
# #         "sale_price[]": "0.57630",
# #         "bonus_money[]": "0.00",
# #         "tariff[]": "0.0000",
# #         "commodity_price[]": "0.0000",
# #         "delivery_time[]": "2023-06-27",
# #         "delivery_msg[]": "现货",
# #         "hqchip_remark[]": "",
# #         "remark[]": "",
# #         "bit_number[]": "",
# #         "goods_sn[]": "0603L050YR",
# #         "goods_name[]": "",
# #         "goods_id[]": "",
# #         "rec_id[]": "",
# #         "self_stock[]": "0",
# #         "ic_goods_json[]": "",
# #         "warehouse_id[]": "",
# #         "inv_desc[]": "电子元器件",
# #         "unit[]": "片",
# #         "supplier_id[]": "",
# #         "sale_number[]": "",
# #         "contact_delivery[]": "",
# #         "spec[]": "1",
# #         "old_sale_price[]": "",
# #         "cost_price[]": "0.00000",
# #         "sale_price[]": "",
# #         "bonus_money[]": "",
# #         "tariff[]": "0.00",
# #         "commodity_price[]": "0.00",
# #         "delivery_time[]": "2023-07-07",
# #         "delivery_msg[]": "现货",
# #         "hqchip_remark[]": "",
# #         "remark[]": "",
# #         "bit_number[]": "",
# #         "goods_sn[]": "",
# #         "picking_price": "0.00",
# #         "shipping_fee": "10.00",
# #         "estimate_gross_profit": "5.76",
# #         "pay_type": "3",
# #         "advance_money": "",
# #         "advance_money": "0.00",
# #         "ajax": "1",
# #         "is_iframe": "1",
# #         "order_cert2": ""
# #            }
# # # files=[
# # #   ("order_cert2",("file",open("/path/to/file","rb"),"application/octet-stream"))
# # # ]
# # headers = {
# #   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
# #   'Accept-Language': 'zh-CN,zh;q=0.9',
# #   'Cache-Control': 'no-cache',
# #   'Connection': 'keep-alive',
# #   'Cookie': 'sendRegisterCoupon=1; visitor=c3ba4eff82321d94c3b1397c19453a58; fingerprint=31dcbc5feb01c51b66ed83f7be7566e6; Hm_lvt_4b7248f2d5bc464e6b35cdd795800722=1686553094,1686729367,1687159592,1687657861; Hm_lvt_6df77d80b496b34cbb807eeb82c01571=1686273677,1686732324,1687159592,1687657861; _gid=GA1.2.1500281194.1687657861; _ga_105P53QJSQ=GS1.2.1687673851.1.1.1687673856.0.0.0; _ga_YSPVNEVYET=GS1.1.1687673851.1.1.1687673857.54.0.0; Qs_lvt_284872=1687329506%2C1687657860%2C1687684017%2C1687742813%2C1687832064; Hm_lvt_9c6fc722df7be37c5541a5d9ed1c2124=1685518466,1687845346; Hm_lpvt_6df77d80b496b34cbb807eeb82c01571=1687845386; _ga_LN25H10JFV=GS1.1.1687845368.61.1.1687845386.0.0.0; ICC_history=2500373615%2C2500379100%2C2500374654%2C2500311125%2C2500311936; PHPSESSID=45482kkfte0ds71rkkdrsdgs94; ICC_new_key_history=WyIwNjAzIiwiQU1TKCBcdTdmOGVcdTU2ZmQgKSIsIkFNUyhcdTdmOGVcdTU2ZmQpIiwiUkMwNjAzSlItMDcxTTFMIiwiNjYwOTktNCIsIiVFNSU4QyU4NSVFOCVBMyU4NSIsIiUyNUU1JTI1OEMlMjU4NSUyNUU4JTI1QTMlMjU4NSIsIktGR0pGUzAwMSJd; ICC_hqcanal=https%3A%2F%2Fuat-passport.elecfans.com%2F; Hm_lpvt_9c6fc722df7be37c5541a5d9ed1c2124=1687854071; Qs_pv_284872=3131015338961456000%2C1892936597082857500%2C4565770513804574700%2C1870073285733537000%2C3917740658017880000; _ga_MDD3ZMQYRW=GS1.1.1687853804.16.1.1687856209.0.0.0; _ga=GA1.1.15269848.1684912807; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%225146221%22%2C%22%24device_id%22%3A%2218848960788fa9-0244000a2acb7d-26031a51-2073600-18848960789e58%22%2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%2C%22first_id%22%3A%2218848960788fa9-0244000a2acb7d-26031a51-2073600-18848960789e58%22%7D; ICC_session_key_verification=a%3A2%3A%7Bs%3A7%3A%22user_id%22%3Bi%3A0%3Bs%3A11%3A%22session_key%22%3Bs%3A32%3A%22d867834f1cfd702966b2fcfb6844fd94%22%3B%7D; ICC_session_key=d867834f1cfd702966b2fcfb6844fd94; activityToken=5dIrTUxlraoSsnCO9cfbtMEX3osU3XLoHvx6+UDrDLQNGm8de8pDqTZ6a1qeeVoCf9RdUF8l9w1016cvBBmmPMrbvTF88LuQAZ61n289m5S6/uJ6+vS17HDiRLq5+APade52aHlsNu3KADMTRPZk6AyctVNEqDnuJHjpjDX0yR84Ai/snjMGbEEud8ziJXpDPerhJb6E4yyzIw5Rc+WR/97qQn6GhllLY29GACtbfeQd9StyixdIF5niy1VdHB0Il3tOw046DB8sSotJiReeLgfp4ibCmWirOn4AhUys73Vky/DG3j69A5br0BzeyszYEqdLjnSrPhrP43dLl86knCNe+ZokZn/ru5qCjiaSUwg=; Hm_lpvt_4b7248f2d5bc464e6b35cdd795800722=1687917749; authId=TDYbRCUWGMncIsOMTB65ZAzQpa7xWA70bgDzAuvfuuBT4Sb%2FpLAraWxozBfBhK28lEPD2zlClev%2FFMyhY%2FdiPQ; logined_key=935e25067b30bedf1fe674c2fbe3c92a',
# #   'Origin': 'https://uat-e.hqchip.com',
# #   'Pragma': 'no-cache',
# #   'Referer': 'https://uat-e.hqchip.com/index/index.html',
# #   'Sec-Fetch-Dest': 'iframe',
# #   'Sec-Fetch-Mode': 'navigate',
# #   'Sec-Fetch-Site': 'same-origin',
# #   'Sec-Fetch-User': '?1',
# #   'Upgrade-Insecure-Requests': '1',
# #   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
# #   'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
# #   'sec-ch-ua-mobile': '?0',
# #   'sec-ch-ua-platform': '"Windows"'
# # }
# #
# # response = requests.request("POST", url, headers=headers, data=payload)
# #
# # print(response.text)
#
# # import urllib.parse
# # c = "https%3A%2F%2Fuat-file.elecfans.com%2Fgroup1%2FM00%2F00%2FDC%2FwKgUfmSvbNGAVNfCAAAsUHZGEGc58.xlsx"
# # print(urllib.parse.unquote(c))
#
#
#
#
# # list = [{'a':'111'},{'a':'222'},{'a':'333'},{'a':'444'},{'a':'555'},{'a':'666'}]
# # ccc = ''
# # for i in range(len(list)):
# #     print(list[i]['a'])
# #     ccc = ccc+list[i]['a']+','
# # print(ccc[0:-1])
# # rss = requests.Session()
# # with open(r'./Conf/conf.yaml', 'r', encoding='utf-8') as yamlfile:
# #     data = yaml.load(yamlfile, Loader=yaml.FullLoader)
# # PassPort_URL = data['PassPort_URL']
# #
# # phone = input("请输入你的手机号码：")
# #
# # password = input("请输入你的密码：")
# # body = {'siteid': 12, 'account': phone, 'password': password}
# # url = '{}/login/dologin.html'.format(PassPort_URL)
# # res = rss.post(url=url, data=body, headers={"Connection": "close"})
# # print(f"开始执行登录账号:{body}")
# # json_res = res.json()
# # print(json_res)
#
# #
# # now_day = str(datetime.datetime.now().date())
# # print(type(now_day))
# # print(f"获取当前时间:{now_day}")
# # list = [1, 2, 3]
# # ccc = ''
# # for i in range(len(list)):
# #     print(list[i])
# #     ccc = ccc+str(list[i])+','
# # print(ccc)
#
#
# # instrumentList=["44433141537", "192797680391", "192773331481", "44433141641", "44434295873"]
# #
# # output = '['+ ', '.join([f'\\"{item}\\"' for item in instrumentList]) + ']'
# #
# # print(output)
# # import requests
# # from PIL import Image
# #
# # url = "https://uat-www.hqchip.com/api/goodsthumb.html?goods_id=2500326221&goods_name=NCD0603G2&v=pc"
# # headers = {"Content-Type": "text/html; charset=UTF-8",
# #                         "User-Agent": "Mozilla/5.0 (compatible; HuaQiuRobot-AutoTest/1.0; +https://www.huaqiu.com)"
# #                         }
# # res = requests.get(url, headers=headers)
# # # print(res.text)
# # image_data = res.content
# # with open('image.jpg', 'wb') as subject_logo_dir:
# #     subject_logo_dir.write(image_data)
# # image = Image.open('image.jpg')
# # image.show()
#
# # from faker import Faker
# #
# # fake = Faker("zh_CN")
# #
# # print(fake.name())  # 'Thomas Flynn'
# # print(fake.address())
# # print(fake.random_int(1, 10))
# # print("叶" + fake.first_name_female())
# # print("叶" + fake.first_name_male())
# # print(fake.name_female())
# # print(fake.ssn())
# # print(round(np.random.uniform(0, 10.64), 2))
#
# # my_data = '0755-232'
# #
# # # url编码
# # encode_data = quote(my_data)
# # print(encode_data)
# #
# #
# #
# #
# # import datetime as dt
# # from datetime import datetime
# # #x = 0
# # def weekday_create(n, date):
# #     """指定日期生成指定日期的n个工作日的日期
# #     :param date 指定日期
# #     :param n 工作日数
# #     """
# #     j = n
# #     i = 0
# #     while i < j:
# #         #a=dt.date.today()
# #         a = datetime.strptime(date, '%Y-%m-%d').date()
# #         a = (a+dt.timedelta(days=i+1)).strftime("%Y-%m-%d")
# #         list1 = a.split('-')
# #         list1 = list(int(x) for x in list1)
# #         tup = tuple(list1)
# #         b = dt.datetime(tup[0], tup[1], tup[2]).weekday()
# #         if b == 5 or b == 6:
# #             j = j+1
# #         i = i+1
# #     weekday_create = (dt.datetime.now() + dt.timedelta(days=i)).strftime("%Y-%m-%d")
# #     return weekday_create
# #
# #
# # print(weekday_create(7, str(datetime.now().strftime('%Y-%m-%d'))))
#
#
#
#
#
#
# # import time
# # from selenium import webdriver
# # from selenium.webdriver.chrome.service import Service as ChromeService
# # from webdriver_manager.chrome import ChromeDriverManager
# # service = ChromeService(executable_path=ChromeDriverManager().install())
# # driver = webdriver.Chrome(service=service)
# # #####
# # opt = webdriver.ChromeOptions()
# # opt.add_experimental_option('excludeSwitches', ['enable-automation'])
# # opt.add_argument('--headless')  # 这个和下面那两条是控制浏览器无头模式，注释掉就会开启浏览器跑
# # opt.add_argument('--disable-gpu')
# #
# # driver.get('https://www.hqchip.com')
# # driver.maximize_window()
# #
# # time.sleep(2)
# # driver.quit()
#
# # s = ['1', '安', 'A']
# # s1 = [x + y for x in s for y in s if x != y and y != x ]
# # print(s1)
# #
# # s = "1安"
# # # 拆分字符串
# # split_s = list(s)
# # # 替换"安"为"A"
# # replaced_s = [i.replace('安', 'A') for i in split_s]
# # print(replaced_s)
# # # 组合成新的列表
# # new_list = [''.join(replaced_s)]
# # print(new_list)
# # # 再次组合成新的列表
# # final_list = [''.join(new_list), ''.join(replaced_s)]
# # print(final_list)
# #
# #
# # data = ['0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '0402', '191KΩ', '191Kr', 'Ω', 'r', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '191KΩ', '1安', '1安', '1安', '1A', '安', 'A', '1安', '1安', '1安', '1安', '1安', '1安', '1安', '1安', '1安', '1安', '1安', '1安', '1安', '1安', '1安', '1安', '1安', '1安', '1安']
# # unique_data = list(set(data))
# # print(unique_data)
# #
# # tup = ('a', 'b')
# # list_name = []
# # str_name = ''.join(tup)
# # list_name.append(str_name)
# # print(list_name)
# #
# #
# # import ast
# #
# # str_list = ['1a','{a:2}','{b:3}']
# # int_list = [ast.literal_eval(x) for x in str_list]
# # print(int_list)
#
#
# # import tkinter as tk
# #
# # # 创建主窗口
# # root = tk.Tk()
# # root.title("面板示例")
# #
# # # 创建一个标签
# # label = tk.Label(root, text="这是一个面板")
# # label.pack()
# #
# # # 运行主循环
# # root.mainloop()
#
#
#
# # import pandas as pd
# #
# # data = {'column1': [1, 2, 3], 'column2': ['A', 'B', 'C']}
# # df = pd.DataFrame(data)
# #
# # # 保存为Excel文件，不包含索引列
# # df.to_excel('demo.xlsx', index=False)
#
#
# # lst = ['231205search07', '2.5w', 'yageo', '音频功率放大器']
# # s = {'25w': '25w', '2.5w': '2.5w'}
# # new_lst = []
# # # for i in range(len(lst)):
# # #     if lst[i] in s:
# # #         lst[i] = s[lst[i]]
# # for i in lst:
# #     new_lst.append(i)
# #     if i in s:
# #         new_lst.append(s[i])
# #         # lst.append(s[i])
# #
# # print(set(new_lst))
# #
# #
# # a=102
# # b=math.ceil(int(a) / 100)
# # print(b)
#
#
# # import pandas as pd
# # from openpyxl import load_workbook
# #
# # # 读取现有的Excel文件
# # data = pd.read_excel('demo.xlsx')
# # other_ws = load_workbook("demo.xlsx")
# # other_d = other_ws["Sheet1"]
# #
# #
# # # 创建一个新的列，并为其赋值
# # # new_column_values = ['column1', 'column2']  # 请替换为实际的值
# # row_count = len(data)
# # for i in range(int(row_count)):
# #     if isinstance(i, int) and (2 <= i <= other_d.max_row):  # 行号为整数，且行号为第2行以后的数据
# #         other_d.cell(row=i+1, column="column3", value="column1")
# #         other_d.save("demo.xlsx")  # 写入成功后保存文件
# #         other_d.close()
# # import pandas as pd
# # import re
# # import math
# #
# # data = pd.read_excel("demo.xlsx")
# # brand_cn = data["column2"]
# # print(brand_cn)
# # for i in brand_cn:
# #
# #     pattern = r'^\d+(\.\d+)?$'
# #     flags = 0
# #     try:
# #         x = float(i)
# #         # 判断string 是否为NaN, 是则传空值
# #         if math.isnan(x) == True:
# #             string = ""
# #         match_obj = re.compile(pattern, flags).match(str(i))
# #         print(string)
# #
# #     except ValueError:
# #         print("无法将字符串转换为浮点数")
# # b = "Sensata ."
# # print(b.upper())
#
# # a = [{"a": 4}, {"a": 3, "b": 1}]
# # a = [d for d in a if not ('b' in d and d['b'] == 1)]
# # print(a)
#
# # class MyClass:
# #     pass
# #
# # obj = MyClass()
# # print(obj.non_existent_attribute)  # 这里会引发AttributeError异常
# #
# # try:
# #     # 尝试执行的代码
# #     pass
# # except AttributeError:
# #     print(11)
# #     # 当发生AttributeError异常时执行的代码
# #     pass
#
#
# # from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# # from cryptography.hazmat.backends import default_backend
# # import base64
# #
# # # 加密函数
# # def encrypt(text):
# #     key = b's83uq8uu6018qth5'
# #     iv = b'bf9w3zresa6tdvec'
# #
# #     backend = default_backend()
# #     cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
# #     encryptor = cipher.encryptor()
# #
# #     ciphertext = encryptor.update(text.encode('utf-8')) + encryptor.finalize()
# #
# #     return base64.b64encode(ciphertext).decode('utf-8')
# #
# # # 调用加密函数
# # text = "mima123456"
# # encrypted_data = encrypt(text)
# # print("加密后的数据：", encrypted_data)
#
# # for m in range(1, 3):
# #     print(m)
# #     n = 16 + (m-1) * 2
# #     m = m + 1
# #     print(n, m)
# # import pandas as pd
# # from huaqiu_order_api.common.my_path import settle_goods_dir, yaml_file, dos_agency_sale_dir
# #
# # # 读取 .xlsx 文件
# # data_frame = pd.read_excel(dos_agency_sale_dir)
# #
# # # 将数据保存为 .xls 文件
# # data_frame.to_excel('output_file.xls', index=False, engine='openpyxl')
# #
# # import xlrd
# # import xlwt
# #
# # # 打开原有的Excel文件
# # workbook = xlrd.open_workbook('D:\Downloads\InventorySalesStockTpl-dos.xls')
# #
# # # 创建一个新的工作簿
# # new_workbook = xlwt.Workbook()
# #
# # # 复制原有工作表到新工作簿
# # for sheet_index in range(workbook.nsheets):
# #     sheet = workbook.sheet_by_index(sheet_index)
# #     new_sheet = new_workbook.add_sheet(sheet.name)
# #
# #     for row_index in range(sheet.nrows):
# #         for col_index in range(sheet.ncols):
# #             new_sheet.write(row_index, col_index, sheet.cell_value(row_index, col_index))
# #
# # # 往新工作簿的特定工作表追加数据
# # new_sheet = new_workbook.get_sheet(0)  # 假设我们要操作的是第一个工作表
# # # 假设我们要写入的数据是[['new1', 'new2', 'new3'], ['new4', 'new5', 'new6']]
# # for row_index, row in enumerate([['new1', 'new2', 'new3'], ['new4', 'new5', 'new6']]):
# #     for col_index, value in enumerate(row):
# #         new_sheet.write(sheet.nrows + row_index, col_index, value)
# #
# # # 保存新工作簿到文件
# # new_workbook.save('your_file_new.xls')
#
#
#
# # from huaqiu_order_api.common.my_path import settle_goods_dir, yaml_file, dos_agency_sale_dir, dos_consignment_launch_dir, dos_consignment_reprice_dir, dos_futures_launch_dir
# #
# #
# # workbook = openpyxl.load_workbook(dos_consignment_launch_dir)
# # sheet = workbook.active
# # for row in sheet.iter_rows(values_only=True):
# #     for cell in row:
# #         if isinstance(cell,str):
# #             encoding = chardet.detect(cell.encode())
# #             print(f"Data: {cell}, Encoding: {encoding['encoding']}")
# #
# # workbook.close()
#
#
# # def generate_sequence(starting_number, total_numbers):
# #     for i in range(total_numbers):
# #         yield "{:06d}".format(starting_number + i)
# #
# # starting_number = 1
# # total_numbers = 10
# #
# # sequence_generator = generate_sequence(starting_number, total_numbers)
# #
# # for number in sequence_generator:
# #     print(number)
# #
# # new = []
# # for i in range(total_numbers):
# #     new.append("{:06d}".format(starting_number + i))
# # print(new)
# #
# # product_label = "1,2,3,4"
# # product_label_list = product_label.split(",")
# # print(product_label_list)
# # product_label = "1kkop2"
# # product_label_list = list(product_label)
# # product_label_list_1 = product_label.split(",")
# # print(product_label_list)
# # print(product_label_list_1)
# #
# # import re
# #
# # # 原始字符串
# # text = "￥1"
# #
# # # 使用正则表达式提取数字
# # numbers = re.findall(r'\d+', text)
# #
# # # 将提取的数字转换为整数
# # numbers = [float(number) for number in numbers]
# #
# # print("从字符串中提取的数字:", numbers[0])
# #
# # a = [float(number) for number in re.findall(r'\d+', text)][0]
# # print("从字符串中提取的数字:", a)
# #
# # page_num = 4
# # for i in range(2, page_num):
# #     print(i)
# #
# # goods_name = ["apple", "banana", "apple", "orange"]
# # ids = [1, 2, 3, 4]
# #
# # goods_name_ids_dict = {}
# # for name, id in zip(goods_name, ids):
# #     if name in goods_name_ids_dict:
# #         goods_name_ids_dict[name].append(id)
# #     else:
# #         goods_name_ids_dict[name] = [id]
# #
# # print(goods_name_ids_dict)
# #
# #
# # import re
# #
# # def split_by_special_characters(input_string):
# #     pattern = '[@_!#$%^&*()<>?/\|}{~:，。、]'
# #     parts = re.split(pattern, input_string)
# #     return parts
# #
# # product_label = "KEFA"
# # result = split_by_special_characters(product_label)
# # # 过滤掉空字符串
# # result = [x for x in result if x.strip()]
# # print(result)
# #
# #
# # result = [x for x in re.split("[@_!#$%^&*()<>?/\|}{~:，。、]", product_label) if x.strip()]
# #
# # print(result)
# #
# #
# #
# # a = 155
# # print(a*2)
#
#
# # from cryptography.hazmat.primitives import serialization, hashes
# # from cryptography.hazmat.primitives.asymmetric import padding, rsa
# # from cryptography.hazmat.backends import default_backend
# # # import rsa
# #
# # # 生成RSA密钥对
# # def generate_rsa_key_pair():
# #     private_key = rsa.generate_private_key(
# #         public_exponent=65537,
# #         key_size=2048,
# #         backend=default_backend()
# #     )
# #
# #     public_key = private_key.public_key()
# #
# #     # 将私钥和公钥序列化为PEM格式
# #     private_pem = private_key.private_bytes(
# #         encoding=serialization.Encoding.PEM,
# #         format=serialization.PrivateFormat.TraditionalOpenSSL,
# #         encryption_algorithm=serialization.NoEncryption()
# #     )
# #
# #     public_pem = public_key.public_bytes(
# #         encoding=serialization.Encoding.PEM,
# #         format=serialization.PublicFormat.SubjectPublicKeyInfo
# #     )
# #
# #     return private_pem.decode('utf-8'), public_pem.decode('utf-8')
# #
# #
# # # 加密函数
# # def rsa_encrypt(message, public_key_pem):
# #     public_key = serialization.load_pem_public_key(
# #         public_key_pem.encode('utf-8'),
# #         backend=default_backend()
# #     )
# #
# #     encrypted_message = public_key.encrypt(
# #         message.encode('utf-8'),
# #         padding.OAEP(
# #             mgf=padding.MGF1(algorithm=hashes.SHA256()),
# #             algorithm=hashes.SHA256(),
# #             label=None
# #         )
# #     )
# #
# #     return encrypted_message
# #
# #
# # # 解密函数
# # def rsa_decrypt(encrypted_message, private_key_pem):
# #     private_key = serialization.load_pem_private_key(
# #         private_key_pem.encode('utf-8'),
# #         password=None,
# #         backend=default_backend()
# #     )
# #
# #     decrypted_message = private_key.decrypt(
# #         encrypted_message,
# #         padding.OAEP(
# #             mgf=padding.MGF1(algorithm=hashes.SHA256()),
# #             algorithm=hashes.SHA256(),
# #             label=None
# #         )
# #     )
# #
# #     return decrypted_message.decode('utf-8')
# #
# #
# # # 示例
# # # private_key_pem, public_key_pem = generate_rsa_key_pair()
# # public_key_pem, private_key_pem = "MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAIkOMjOCT9c82Cc9SPfXLGKiTW8LRzI2saMVVf7cUByJpJeul9CUAT9zUaLqIpvKokbHsZs5OcCjxzN7B+ORw06IlPtu69NCXOMBpUZwVAhOhi3T827nzuoVnD0Hs4GUFoV1HBrCks3nU1+JGSPIzOrXsGjz2j5d1I23a/2+IUf1AgMBAAECgYBvA0yuZDL/iI0c24srFOMi0YwfEeeNSLgB/No3IYTSWLs1EXpuvDN2jZXme/ekcTGYW1AFBwk8fGxxyonNTtf+pT6jAdmPF8wUMA686iTwK8HLgubNA0JHIBGAHtyCQ2VMXXjuuHRLV8UsQs3HW6Qcewtw/MhqbgsY6e0LLZ4x0QJBANwxH5p1l3vJouQZIhZvF1oPnJPIz3gIEu+t/N/9jv476OV6SacAb3dmVAEDDLq9WnS6GmBSLt56REWDeF1o3a8CQQCfV/55Bg55zeSGZQ4utsTG7cjDsfGfRccRcQSQ5aWUVQc4744qAWxnKm0e6AiyOQmNYbH6PrQqd/Dg+MINSKGbAkEAijE+X2dL0kHjPHrVnPTN2BUSNOID65ZNpCUzHrT5CHA7I8KS9P/d9TbAo/3xAEYUvkuKgEcz6ScdL+9qHF3TOwJAL/4V1CfB1mfwC5aGVgWQcQYPcPm4d6tRkOxEXsv8Ohf+C+UDIZ26I7yAj019yQgq211weJnIM/5aG7hw4gVdPwJBANhiMH5Y3Dww15Bi1YfDCiYGFx6iVdEAZm3P3POOLX49DHaXG2f+sj18AuRlAFkjWxLuEYFdBSCWHO1Cqhx6YuM="
# # message = "Hello, World!"
# #
# # encrypted_message = rsa_encrypt(message, public_key_pem)
# # print("Encrypted message:", encrypted_message.hex())
# #
# # decrypted_message = rsa_decrypt(encrypted_message, private_key_pem)
# # print("Decrypted message:", decrypted_message)
#
# a = {
#     '848': ['开关及按键', {'992': ['可配置开关元件', {'289': '照明光源'}]}],
#     '836': ['光学检测设备', {'67': '照明光源'}],
#     '1': ['11111', {'89': '照明光源'}]
# }
#
# def find_keys(data, target_value, result=None):
#     if result is None:
#         result = {}
#
#     for key, value in data.items():
#         if isinstance(value, list) and len(value) == 2 and isinstance(value[1], dict):
#             # 递归处理第二项是字典的情况
#             sub_result = find_keys(value[1], target_value)
#             for sub_key, sub_value in sub_result.items():
#                 if sub_value:
#                     if key not in result:
#                         result[key] = []
#                     for v in sub_value:
#                         result[key].append(sub_key + ':' + str(v))
#         elif isinstance(value, list) and target_value in value:
#             # 处理列表中直接包含目标值的情况
#             pass  # 在当前数据结构下，这个情况不会发生
#
#     return result
#
# target_value = '照明光源'
# keys_with_same_level = find_keys(a, target_value)
# print(keys_with_same_level)
#
#
#
# input_str = "TIANMA NLT USA"
# result = None
# if "(" in input_str or ")" in input_str:
#     matches = re.match(r'^(.*?)\((.*?)\)$', input_str)
#     # 如果匹配成功
#     if matches:
#         # 第一个匹配组是括号外的部分
#         part1 = matches.group(1).strip()
#
#         # 第二个匹配组是括号内的部分
#         part2 = matches.group(2).strip()
#
#         # 放入列表
#         result = [part1, part2]
# elif " " in input_str:
#     result = input_str.split()
# else:
#     result = [input_str]
#
#
# print(result)
#
#
#
# import urllib.parse
#
# # 定义字典
# s = {"222": 333, "keywork": "较劲儿哦"}
#
# # 将字典转换为 URL 编码格式
# encoded_s = urllib.parse.urlencode(s)
#
# print("URL 编码后的结果：", encoded_s)
#
#
# import json
#
# # 定义包含双引号的字典
# data = {"key": '"value"'}
#
# # 将字典转换为 JSON 字符串，并对双引号进行转义
# json_data = json.dumps(data)
#
# print("JSON 字符串：", json_data)
#
#
# body1 = {
#     'id': '1105871192',
#     'goods_number': '1863',
#     'min_buynum': '1',
#     'increment': '1',
#     'status': '1',
#     'number[]': 1,
#     'price[]': 6.99}
#
#
# body2 = {
#     'number[]': 100,
#     'price[]': 3.8394
# }
#
# # 合并两个字典
# body3 = str(body1) + str(body2)
# body3 = body3.replace('}{', ',')
# body3 = ast.literal_eval(json.dumps(body3))
#
#
# # 打印合并后的字典
# print(body3)
#
#
# import json
#
# # 假设这些是你的变量
# v = 123
# goods_number = "ABC123"
# min_buynum = 10
# increment = 5
# goods_tiered_number = [1, 100, 250, 500]
# goods_tiered_pricing = [6.99, 3.8394, 3.64744, 3.56518]
#
# supplier_goods_update_body = {
#     "id": int(v),
#     "goods_number": goods_number,
#     "min_buynum": min_buynum,
#     "increment": increment,
#     "status": 1,
#     "ajax": 1,
#     "prices": []  # 创建一个空列表用于存储价格和数量
# }
#
# # 构建价格和数量的列表
# for a in range(len(goods_tiered_number)):
#     price_item = {"number": goods_tiered_number[a], "price": goods_tiered_pricing[a]}
#     supplier_goods_update_body["prices"].append(price_item)
#
# # 将字典转换为JSON格式的字符串
# supplier_goods_update_json = json.dumps(supplier_goods_update_body)
# print(supplier_goods_update_json)
#
#
# # 假设 input_str 是你要处理的字符串
# input_str = "12345"  # 你的字符串
#
# # 判断长度是否小于6
# if len(input_str) < 6:
#     # 在字符串前面添加 0 补齐至长度为6
#     input_str = input_str.zfill(6)
#
# print(input_str)  # 输出处理后的字符串
#
#
# interface_params = {
#     "id": 1105871192,
#     "goods_number": 1863,
#     "min_buynum": 1,
#     "increment": 1,
#     "status": 0,
#     "ajax": 1,
#     "number": [1, 100, 250, 500],
#     "price": [6.99, 3.8394, 3.64744, 3.56518]
# }
#
# new_interface_params = {
#     "id": interface_params["id"],
#     "goods_number": interface_params["goods_number"],
#     "min_buynum": interface_params["min_buynum"],
#     "increment": interface_params["increment"],
#     "status": interface_params["status"],
#     "ajax": interface_params["ajax"]
# }
#
# for i in range(len(interface_params["number"])):
#     new_interface_params[f"number[{i}]"] = interface_params["number"][i]
#     new_interface_params[f"price[{i}]"] = interface_params["price"][i]
#
# print(new_interface_params)
#
#
# keys = ['a', 'b', 'c']
# values = [1, 2, 3]
# items = ['x', 'y', 'z']
#
# # 使用zip函数将三个列表合并成元组的列表
# combined = list(zip(keys, values, items))
#
# # 创建一个空字典
# result_dict = {}
#
# # 遍历合并后的列表，将元组中的第一个元素作为键，第二个元素作为值，添加到字典中
# for key, value, item in combined:
#     result_dict[key] = (value, item)
#
# print(result_dict)
#
#
# s = {'4627': [[5220], [1]]}
# b = {'supplier_id': 3041}
#
# result = {
#     "supplier": "Supplier: " + str(b['supplier_id']),
#     "order_id": {"order_id": list(s.keys())[0], "stock_id": s[list(s.keys())[0]][0], "at": s[list(s.keys())[0]][1]}
# }
#
# print(result)
# sunmmary = {1: ['111', '112'], 2: ['112']}
# wms_goods_update_body = {"id": 1, "weight": 0.25, "beSet": 1, "encapsulationFilePaths": [], "filePaths": [],
#                          "goodsFilePaths": [],
#                          "labelNumberFilePaths": [], "packingFilePaths": [], "silkscreenFilePaths": []}
# if sunmmary != {}:
#     img_type = {"filePaths": 1, "goodsFilePaths": 2, "silkscreenFilePaths": 3, "encapsulationFilePaths": 4,
#                 "labelNumberFilePaths": 5, "packingFilePaths": 6}
#     for key in img_type:
#         img_type_value = img_type[key]
#         if img_type_value in sunmmary:
#             wms_goods_update_body[key] = sunmmary[img_type_value]
#         else:
#             wms_goods_update_body[key] = []
# print(wms_goods_update_body)
#
#
# def extract_leaf_departments(department, leaf_departments):
#     if "child" not in department or len(department["child"]) == 0:
#         leaf_departments.append(department)
#     else:
#         for child_department in department["child"]:
#             extract_leaf_departments(child_department, leaf_departments)
#
# s=[{"name": "冬藏夏秀", "id": 839, "parentId": 0, "child": [{"name": "产研中心", "id": 1397, "parentId": 839, "child": [{"name": "技术服务部", "id": 1400, "parentId": 1397, "child": [{"name": "测试组", "id": 1403, "parentId": 1400, "child": []}, {"name": "前端研发组", "id": 1415, "parentId": 1400, "child": []}]}, {"name": "商城运营部", "id": 1401, "parentId": 1397, "child": [{"name": "国内产品组", "id": 1404, "parentId": 1401, "child": [{"name": "元器件商城", "id": 1414, "parentId": 1404, "child": []}]}, {"name": "国内研发组", "id": 1405, "parentId": 1401, "child": []}]}, {"name": "供应链部", "id": 1402, "parentId": 1397, "child": [{"name": "供应链研发组", "id": 1406, "parentId": 1402, "child": []}, {"name": "供应链产品组", "id": 1407, "parentId": 1402, "child": []}]}, {"name": "智能制造研发部", "id": 1411, "parentId": 1397, "child": [{"name": "PCBA MES研发组", "id": 1412, "parentId": 1411, "child": []}, {"name": "PCB MES研发组", "id": 1413, "parentId": 1411, "child": []}]}, {"name": "客户服务部", "id": 1420, "parentId": 1397, "child": [{"name": "CRM产品组", "id": 1421, "parentId": 1420, "child": []}, {"name": "客户服务研发组", "id": 1422, "parentId": 1420, "child": []}]}]}, {"name": "财务中心", "id": 1398, "parentId": 839, "child": [{"name": "财务BP组", "id": 1399, "parentId": 1398, "child": []}]}, {"name": "智能制造中心", "id": 1408, "parentId": 839, "child": [{"name": "MES系统部", "id": 1409, "parentId": 1408, "child": [{"name": "PCBA MES组", "id": 1410, "parentId": 1409, "child": []}, {"name": "PCB MES研发组", "id": 1416, "parentId": 1409, "child": []}]}]}, {"name": "总裁办", "id": 1417, "parentId": 839, "child": [{"name": "客户满意中心", "id": 1418, "parentId": 1417, "child": [{"name": "客诉组", "id": 1419, "parentId": 1418, "child": []}]}]}]}]
# leaf_departments = []
# for department in s:
#     extract_leaf_departments(department, leaf_departments)
# print(leaf_departments)
# # for leaf_department in leaf_departments:
# #     print(leaf_department["name"])
#
#
# Auth_Base_URL = "https://uat-auth.huaqiu.com"
# if "uat" not in Auth_Base_URL or "fat" not in Auth_Base_URL:
#    print(1111)
#
#
#
# text = "节目是客户跟进"
# capitalized_text = text.title()
# print(capitalized_text)
# buid_type_json = {"0": {"Bom": 3, "Pcb": 2}, "1": {"Bom": 2, "Pcb": 3}, "2": {"Bom": 1, "Pcb": 1}}
# build_type = "0"
# build_value_name = "Bom"
# # 初始化变量，用于存储找到的值
# build_value = None
# # # 遍历每个字典
# # for item in self.buid_type_json:
# #     if item["buid_type"] == build_type:
# #         build_value = item["value"]
# #         break  # 找到后退出循环
# # print(f"找到的值为：{build_value}")
# # return build_value
# for key, item in buid_type_json.items():
#     if key == build_type:
#         for k, v in item.items():
#             if k == build_value_name:
#                 build_value = v
#                 break
#         break
# print(f"找到的值为：{build_value}")
#
#
#
# a = {'hq_pack': 1, 'has_period': 0, 'period_format': 0, 'delivery_note': 0, 'audit_advice': 1, 'shipping_advice': 1,
#      'pcbfile': 'https://uat-smt.hqchip.com/file/5/414996/4f4e9b95d31eabe5097124f7450b0415/iFlyCode-IDEA-200.zip', 'report': '',
#      'report_type': 0, 'cross_board': 1, 'review_file': 0, 'file_type': -1, 'beveledge': 0, 'is_need_smt': 1, 'insurance': 0,
#      'paper': 1, 'user_stamp': 1, 'deduct_type': 2, 'deduct_limit': 0, 'smt_order_id': '42914', 'id': '1734690', 'status': '0',
#      'type': 1, 'guid': '', 'mid': '5147236', 'mobile': '', 'units': '1', 'bwidth': '12', 'blength': '12', 'blayer': '2', 'bcount': '5',
#      'layoutx': '1', 'layouty': '1', 'sidedirection': '无', 'sidewidth': '0.00', 'pbnum': '1', 'testpoint': '0', 'bheight': '1.60', 'lineweight': '6.0',
#      'bga': '0.00', 'vias': '0.30', 'bankong': '0', 'baobian': '0', 'blind': '0', 'impendance': '0', 'pressing': '', 'color': '绿色',
#      'charcolor': '白色', 'spray': '有铅喷锡', 'cover': '过孔盖油', 'test': '样品免费测试', 'copper': '1', 'insidecopper': '0', 'via_in_pad': '无',
#      'deltime': '正常6天', 'invoice': '不需要', 'express': '9', 'province': '14', 'city': '197', 'note': '', 'label_remark': '', 'jiajifee': '0',
#      'price': '91', 'order_id': '0', 'pro_quote_id': '0', 'site': '', 'site_url': '', 'without_discount': '0', 'board_type': 'FR-4',
#      'board_brand': '无要求', 'board_tg': '', 'cjh': '1', 'overlay': '[object Object]', 'zknum': '0', 'time': '0',
#      'extend': {'hq_pack': 1, 'has_period': 2, 'period_format': 0, 'delivery_note': 0, 'audit_advice': 1,
#                 'shipping_advice': 1, 'pcbfile': '', 'report': '', 'report_type': 0, 'cross_board': 1, 'review_file': 0,
#                 'file_type': -1, 'beveledge': 0, 'is_need_smt': 1, 'insurance': 0, 'paper': 1, 'user_stamp': 1, 'deduct_type': 2,
#                 'deduct_limit': 0, 'smt_order_id': '42914', 'ul_label': 1, 'insurance_type': 0}, 'c_time': '2024-06-12 18:26:24',
#      'u_time': '2024-06-12 18:26:24', 'sidedirection_cn': '无', 'setlength': '12', 'setwidth': '12', 'source': 'smtstep', 'bill_id': 0}
# # print(a)
# # 获取 extend 字典
# extend_dict = a.pop('extend', {})
#
# for k, v in extend_dict.items():
#     if k in a:
#         if isinstance(a[k], (int, float)) and isinstance(v, (int, float)):
#             a[k] = max(a[k], v)
#         elif isinstance(a[k], str) and a[k] == '':
#             a[k] = v
#     else:
#         a[k] = v
# print(a)
#
#
# from urllib.parse import quote
#
# url = 'https://uat-www.hqchip.com/hjgi/wi/k.html'
#
# # 手动替换斜杠为编码后的结果
# encoded_url = quote(url, safe='')
#
# # 将空格替换为%20
# encoded_url = encoded_url.replace(" ", "%20")
# print(encoded_url)
#
# a = {
#     "activity_id": "26",
#     "activity_name": "产品用0419",
#     "thematicNameInfo": [
#         {"thematicName": "大会主页22222", "thematicId": "188"},
#         {"thematicName": "大会报道", "thematicId": "206"},
#         {"thematicName": "大会报道", "thematicId": "207"},
#         {"thematicName": "展台看点", "thematicId": "209"},
#         {"thematicName": "大会回顾", "thematicId": "211"},
#         {"thematicName": "大会主页222222222", "thematicId": "214"},
#         {"thematicName": "商城尝试使用新组件", "thematicId": "215"},
#         {"thematicName": "042501", "thematicId": "217"}
#     ]
# }
#
# # 使用列表推导式找出 thematicId 为 "217" 的 thematicName 值
# thematicId = "217"
# thematicName = next((info["thematicName"] for info in a["thematicNameInfo"] if info["thematicId"] == thematicId), None)
#
# print(thematicName)
#
# text = Pinyin().get_pinyin("产品用0419", "")
#
# print(text)
#
# import random
#
# def generate_random_16_digits():
#     # Generate a random 16-digit number
#     return ''.join(random.choices('0123456789', k=16))
#
# # Example usage:
# random_number = generate_random_16_digits()
# print("Random 16-digit number:", random_number)
# goods_id_1  = '1,2,3'
# goods_id = goods_id_1.split(",")
# goods_list = [{"out_goods_name": "", "qty": "", "goods_id": i} for i in goods_id]
# print(goods_list)
#
# # 获取当前日期和时间
# now = datetime.now()
#
# # 获取当前年份
# current_year = (datetime.now()).year
# print(current_year)
#
# express_delivery_no = "SF" + datetime.now().strftime("%Y%m%d") + "000" + str(Faker("zh_CN").random_int(1, 10000))
# print(express_delivery_no)
#
#
#
#
# from datetime import datetime
#
# # 获取当前日期
# current_date = datetime.now()
#
# # 计算当前日期是本年度的第几个周
# week_number = current_date.isocalendar()[1]
#
# # 获取本年度的最后两位数字
# year_last_two_digits = current_date.year % 100
#
# # 拼接结果
# result = f"{year_last_two_digits}{week_number}"
#
# print(f"当前日期是 {result} 周")
#
#
#
# b = "2456"
#
# # 判断字符串是否符合年份后两位+周次的规则
# def is_valid_year_week(b):
#     # 检查字符串是否长度为4
#     if len(b) != 4:
#         return False
#
#     # 检查前两位是否是数字
#     year_last_two_digits = b[:2]
#     week_number = b[2:]
#
#     if not (year_last_two_digits.isdigit() and week_number.isdigit()):
#         return False
#
#     # 检查周数是否在 01 到 53 之间
#     week_number_int = int(week_number)
#     if 1 <= week_number_int <= 53:
#         return True
#
#     return False
#
# print(f"'{b}' 是否符合年份后两位+周次规则: {is_valid_year_week(b)}")
#
#
#
# s = "44"  # 可以设置为 "44" 来测试其他情况
# s1 = ["a", "4"]
#
# result = [s.split(',')[i] if s is not None and i < len(s.split(',')) else '' for i in range(len(s1))]
#
# print(result)
#
#
#
#
#
# # 中文文本
# text = "你好，世界"
# # from pypinyin import pinyin, Style
# # 转换为拼音
# pinyin_text = Pinyin().get_pinyins(text, )
#
# # 打印拼音
# print(pinyin_text)
# print(' '.join(word[0] for word in pinyin_text))
#
#
# from pypinyin import pinyin, lazy_pinyin, Style
#
# # 中文文本
# text = "叶茂"
#
# # 使用 lazy_pinyin 直接获取拼音字符串列表
# pinyin_text = lazy_pinyin(text)
#
# # 将拼音列表连接成一个字符串
# pinyin_string = ''.join(pinyin_text)
#
# # 打印拼音
# print(pinyin_string)
#
#
#
#
# import requests
#
# url = "https://uat-hc2019.hqchip.com/v1/goods/GoodsInfo/getBusinessGoodsList"
#
# payload = "{\"page\":1,\"per_page\":50,\"status\":1,\"goods_name\":\"111\",\"provider_name\":\"1111\",\"source\":\"partner\"}"
# headers = {
#   'Accept': '*/*',
#   'Accept-Language': 'zh-CN,zh;q=0.9',
#   'Access-Control-Request-Headers': 'authorization,content-type',
#   'Access-Control-Request-Method': 'POST',
#   'Cache-Control': 'no-cache',
#   'Connection': 'keep-alive',
#   'Origin': 'https://uat-hc2018.hqchip.com',
#   'Pragma': 'no-cache',
#   'Referer': 'https://uat-hc2018.hqchip.com/',
#   'Sec-Fetch-Dest': 'empty',
#   'Sec-Fetch-Mode': 'cors',
#   'Sec-Fetch-Site': 'same-site',
#   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
#   'Authorization': 'bb01cb6efb0b45e145b4ebeeb87d6477',
#   'Content-Type': 'application/json;charset=UTF-8',
#   'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
#   'sec-ch-ua-mobile': '?0',
#   'sec-ch-ua-platform': '"Windows"'
# }
#
# response = requests.request("POST", url, headers=headers, data=payload)
#
# print(response.text)
#
#
# list1 = [10, 20, 30, 40, 50]
# list2 = ['a', 'b', 'c', 'd', 'e']
# result = [y for x, y in zip(list1, list2) if x == 30]
#
# print(result)
#
#
#
# import math
#
# rule_minAmount = [5000.0, 10000.0, 30000.0, 50000.0, 100000.0, 300000.0]
# rule_voucher_id = ['1864555596577042434', '1864555536728518657', '1864555483272114178', '1864555444516745218', '1864555347846426626', '1864555313310527489']
# rule_minAmountLogic = ['gte', 'gte', 'gte', 'gte', 'gte', 'gte']
# rule_maxAmount = [10000.0, 30000.0, 50000.0, 100000.0, 300000.0, 0.0]
# rule_maxAmountLogic = ['lte', 'lt', 'lt', 'lt', 'lt', '-1']
# self_size_tool_json = {
#     "gte": ">=",
#     "lte": "<=",
#     "lt": "<",
#     "gt": ">",
#     "eq": "=",
#     "-1": "不限"
# }
#
# rule_minAmount_symbol = []
# rule_maxAmount_symbol = []
# rule_voucher_activity = []
#
# # 填充规则符号
# for i in range(len(rule_minAmount)):
#     if rule_minAmountLogic[i] in self_size_tool_json:
#         rule_minAmount_symbol.append(self_size_tool_json[rule_minAmountLogic[i]])
#
#     if rule_maxAmountLogic[i] in self_size_tool_json:
#         rule_maxAmount_symbol.append(self_size_tool_json[rule_maxAmountLogic[i]])
#
#     # 检查是否需要设置为无穷大
#     if rule_maxAmount[i] == 0.0:  # 这里使用 0.0 作为判断条件
#         rule_maxAmount[i] = math.inf
#
# # 创建规则字典
# for m in range(len(rule_minAmount)):
#     rule_json = {
#         rule_voucher_id[m]: {
#             "minAmount": rule_minAmount[m],
#             "minAmountLogic": rule_minAmount_symbol[m],
#             "maxAmount": rule_maxAmount[m],
#             "maxAmountLogic": rule_maxAmount_symbol[m]
#         }
#     }
#     rule_voucher_activity.append(rule_json)
#
# # 输出结果
# print(rule_voucher_activity)
#
#
# def find_matching_key(amount, rules):
#     for rule in rules:
#         for key, value in rule.items():
#             # 获取每个规则的 minAmount、minAmountLogic、maxAmount、maxAmountLogic
#             minAmount = value['minAmount']
#             minAmountLogic = value['minAmountLogic']
#             maxAmount = value['maxAmount']
#             maxAmountLogic = value['maxAmountLogic']
#
#             # 判断是否满足最小金额逻辑
#             if minAmountLogic == '>=' and amount < minAmount:
#                 continue
#             elif minAmountLogic == '>' and amount <= minAmount:
#                 continue
#
#             # 判断是否满足最大金额逻辑
#             if maxAmountLogic == '<=' and amount > maxAmount:
#                 continue
#             elif maxAmountLogic == '<' and amount >= maxAmount:
#                 continue
#             elif maxAmountLogic == '不限' and amount > maxAmount:
#                 continue
#
#             # 如果满足规则，返回key值
#             return key
#     return None  # 如果没有找到匹配的规则，返回None
#
#
# # 示例输入
# amount = 5001
# result = find_matching_key(amount, rule_voucher_activity)
#
# if result:
#     print(f"Amount {amount} 命中规则的 key: {result}")
# else:
#     print(f"Amount {amount} 未命中任何规则")
#
#
#
# # import translators as ts
# #
# # # 要翻译的文本
# # text = "DIP你好，世界3363"
# #
# # # 使用 Google 翻译
# # translated1 = ts.translate_text(text, translator='youdao', to_language='en')
# # # translated2 = ts.translate_text(text, translator='google', to_language='en')
# # #translated = ts.translate_text(text, from_language='zh', to_language='en')
# #
# # # 输出翻译结果
# # print(f"原文: {text}")
# # print(f"翻译结果: {translated1}")
# # # print(f"翻译结果: {translated2}")
# # # print(f"翻译结果: {translated}")
#
#
# a = ['1017508086', '1017504385', '1017496321', '1017774799', '1017501479', '1017500386', '1017777607', '1017501603', '1017499744', '1017496498', '1017499834', '1017503704', '1017503564', '1017506890', '1017769187', '1017520859', '1017769966', '1017503608', '1017501662', '1017501021', '1017486327', '1017501585', '1017520265', '1017520362', '1017520389', '1017501643', '1017501622', '1017777506', '1017520340', '1017520226']
# b = ['1017508086', '1017504385', '1017496321', '1017501603', '1017499744', '1017496498', '1017499834', '1017501479', '1017500386', '1017503704', '1017503564', '1017506890', '1017520859', '1017503608', '1017501662', '1017501021', '1017486327', '1017501585', '1017520340', '1017501643', '1017501622', '1017520265', '1017520362', '1017520389', '1017520226']
#
# # 将列表转换为集合
# set_a = set(a)
# set_b = set(b)
#
# # 找出 a 有但 b 没有的元素
# only_in_a = set_a - set_b
# # 找出 b 有但 a 没有的元素
# only_in_b = set_b - set_a
# # 合并所有不同值
# all_differences = only_in_a.union(only_in_b)
#
# print("仅在 a 中的元素:", only_in_a)
# print("仅在 b 中的元素:", only_in_b)
# print("所有不同的值:", all_differences)
#
#
#
#
#
# # from transformers import LlavaConfig, LlavaProcessor
# #
# # model_name = "liuhaotian/llava-v1.5"
# # config = LlavaConfig.from_pretrained(model_name)
# # processor = LlavaProcessor.from_pretrained(model_name)
# # model = LlavaForCausalLM.from_pretrained(model_name, config=config)
#
#
#
# error_msg = None
# try:
#     error_msg = ['fhudg1']  # 模拟错误信息
#     if error_msg is None:  # 这里始终为 False，无法触发
#         print(f"需求导入成功")
#     else:
#         # 手动抛出异常来测试
#         raise ValueError("模拟异常")
# except Exception as e:
#     print(f"捕获到异常: {e}")
#
#
# print(quote("Passive Components"))
#
#
# def find_top_keys(data, target_value, top_key=None, result=None):
#     if result is None:
#         result = {}
#     if top_key is None:
#         # 初始化时，当前键就是顶层键
#         top_key_mapping = {key: key for key in data.keys()}
#     else:
#         # 递归时继承父层的顶层键映射
#         top_key_mapping = top_key
#
#     for key, value in data.items():
#         current_top_key = top_key_mapping[key]  # 当前键对应的顶层键
#         if isinstance(value, list):
#             # 检查第二个元素是否为字典
#             if len(value) == 2 and isinstance(value[1], dict):
#                 # 更新子键的顶层键映射（继承当前顶层键）
#                 new_top_key_mapping = {**top_key_mapping, **{k: current_top_key for k in value[1].keys()}}
#                 # 递归处理子字典
#                 find_top_keys(value[1], target_value, new_top_key_mapping, result)
#         elif value == target_value:
#             # 找到目标值，记录其顶层键和当前键
#             if current_top_key not in result:
#                 result[current_top_key] = []
#             result[current_top_key].append(key)
#     return result
import json

data = {'855': ['电容器', {'2078': '电容ZT测试', '2079': '电容ZT测试2', '919': '电容器配件'}], '1787': ['接口及驱动芯片', {'1825': '电容式触摸屏控制器'}], '1663': ['传感器', {'1672': '电容触摸传感器芯片'}], '842': ['套件', {'172': '电容器套件'}]}
# target_value = "电容"
# print(find_top_keys(data, target_value))  # 输出: {'848': ['289'], '836': ['67']}
#
#
import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import execjs
import urllib.parse
from huaqiu_order_api.common.my_path import encryption_order_dir

def encrypt(data):
    """密码前置js加密"""
    # # 读取JavaScript文件内容
    with open(encryption_order_dir, "r", encoding="utf-8") as f:
        js_content = f.read()
    # 编译JavaScript代码
    js_runtime = execjs.compile(js_content)
    # 调用JavaScript函数
    dataStr = js_runtime.call("encryptData", data)
    return dataStr

def dencrypt(data):
    """密码前置js加密"""
    # # 读取JavaScript文件内容
    with open(encryption_order_dir, "r", encoding="utf-8") as f:
        js_content = f.read()
    # 编译JavaScript代码
    js_runtime = execjs.compile(js_content)
    # 调用JavaScript函数
    dataJSON = js_runtime.call("decodeData", data)
    return dataJSON
# datastr = "0VVFVeXhacnsiODQyIjpbIuWll+S7tiIseyIxNzIiOiLnlLXlrrnlmajlpZfku7YifV0sIjg1NSI6WyLnlLXlrrnlmagiLHsiOTE5Ijoi55S15a655Zmo6YWN5Lu2IiwiMjA3OCI6IueUteWuuVpU5rWL6K+VIiwiMjA3OSI6IueUteWuuVpU5rWL6K+VMiJ9XSwiMTY2MyI6WyLkvKDmhJ/lmagiLHsiMTY3MiI6IueUteWuueinpuaRuOS8oOaEn+WZqOiKr+eJhyJ9XSwiMTc4NyI6WyLmjqXlj6Plj4rpqbHliqjoiq/niYciLHsiMTgyNSI6IueUteWuueW8j+inpuaRuOWxj+aOp+WItuWZqCJ9XX0=0VVFVeXhacnsiODQyIjpbIuWll+S7tiIseyIxNzIiOiLnlLXlrrnlmajlpZfku7YifV0sIjg1NSI6WyLnlLXlrrnlmagiLHsiOTE5Ijoi55S15a655Zmo6YWN5Lu2IiwiMjA3OCI6IueUteWuuVpU5rWL6K+VIiwiMjA3OSI6IueUteWuuVpU5rWL6K+VMiJ9XSwiMTY2MyI6WyLkvKDmhJ/lmagiLHsiMTY3MiI6IueUteWuueinpuaRuOS8oOaEn+WZqOiKr+eJhyJ9XSwiMTc4NyI6WyLmjqXlj6Plj4rpqbHliqjoiq/niYciLHsiMTgyNSI6IueUteWuueW8j+inpuaRuOWxj+aOp+WItuWZqCJ9XX0="
datastr = encrypt(data)
print("加密结果:", datastr, type(datastr))

dataNew = dencrypt(datastr)
print(dataNew)
# print("解密结果（显示中文）:", json.dumps(dataNew, ensure_ascii=False, indent=2))

2