#coding=utf-8


import copy,jsonpath,random,requests,time,json


cookie = {
    "token": "1CsDa87GGyhwLRDF1X35y7/JM27PdJMGyyPL+QzHHIYZ19iavV7DY/6hnSIQ1pXRKYNDpHtLSHKSInSbt12CxE0NmiYUEFxEdvhzrk2MmTacCcv8XQi4HKiy68myModcyyNS1Bt+B0CujL3l2yMemMjNNC8xzwYQfgFDbN60bX4Fqpljx+r2CbWqb5V5ta8FSX9K9i8gO23it9XUojnsh5MC8x1J2Y5+Bazn2QQGx26dDgjmATJU8yqJwt6X2QQ4Wf1sO4j1ludFfJnNy/S6uRj//HBjY0obUPca6bUu9Cx+osMKVekMGgQzWaZg/eQuW1sEAM5ZPbP2Eqz++9/LDwFHCGEPUGQOqXNdYAVeeTY="
}

def create_order(Sn):
  url = 'https://uat-scm.huaqiu.com/hqScm/demand/getDetail'
  data = {
    "demandSn": Sn,
  }
  base_data = requests.post(url=url,json=data,cookies=cookie).json()['result']
  print(base_data)
  base_data_info = copy.deepcopy(base_data)
  demandPcbaId_lits = jsonpath.jsonpath(base_data,'$.pcbaInfo..demandPcbaId')
  pcba_info_list = []
  for demandPcbaId in demandPcbaId_lits:
      url = 'https://uat-scm.huaqiu.com/hqScm/demand/getPcbaDetail'
      data = {
          "demandPcbaId": demandPcbaId
        }
      pcba_info = requests.post(url=url, json=data, cookies=cookie).json()['result']
      pcba_info_base = copy.deepcopy(pcba_info)
      pcba_info_base.update(
        {'bom': pcba_info['bomInfo']}
      )
      pcba_info_base['bom'].update(
        {'bomItems': pcba_info['bomInfo']['bomList']}
      )
      pcba_info_base.update(
          {'smt': pcba_info['smtInfo']['attrs']}
      )
      pcba_info_base.update(
          {'pcb': pcba_info['pcbInfo'],
           'bomFileName': pcba_info['fileList'][0]['fileName'],
           'bomFileUrl': pcba_info['fileList'][0]['fileUrl'],
           'pcbFileName': pcba_info['fileList'][1]['fileName'],
           'pcbFileUrl': pcba_info['fileList'][1]['fileUrl'],
           'smtFileName': pcba_info['fileList'][2]['fileName'],
           'smtFileUrl': pcba_info['fileList'][2]['fileUrl'],
           }
      )
      pcba_info_list.append(pcba_info_base)
  base_data.update(
      base_data_info['baseInfo']
  )
  base_data.update(
      {'pcbaList': pcba_info_list}
  )
  url = 'https://uat-scm.huaqiu.com/hqScm/demand/insert'
  res = requests.post(url=url, json=base_data, cookies=cookie).json()
  print(res)
  global demandSn, demandId
  demandSn = res['result']['demandSn']
  demandId = res['result']['demandId']
  url = 'https://uat-scm.huaqiu.com/hqScm/demand/submitQuote'
  data = {
      "demandId": res['result']['demandId']
  }
  res = requests.post(url=url, json=data, cookies=cookie).json()
  print(res)


def approve_smt():
  url = 'https://uat-scm.huaqiu.com/hqScm/approve/smt/queryScmApproveSmtPage'
  data = {
    'approveType': 3,
    'demandSn': demandSn,
    'smtType': 1
  }
  res = requests.post(url=url,json=data,cookies=cookie).json()
  approveNo_list = jsonpath.jsonpath(res,'$.result..approveNo')
  approveId_list = jsonpath.jsonpath(res,'$.result..approveId')
  for approveNo in approveNo_list:
      url = 'https://uat-scm.huaqiu.com/hqScm/approve/smt/confirmApproveSmtArt'
      data = {
        "approveId": approveId_list[approveNo_list.index(approveNo)],
        "approveNo": approveNo,
        "approveType": "3",
        "auditStatus": "1"
      }
      res = requests.post(url=url, json=data, cookies=cookie).json()
      print(res)
      url = 'https://uat-scm.huaqiu.com/hqScm/approve/smt/smtMirrorDetail'
      data = {
        "approveNo": approveNo,
        "approveType": "3"
      }
      smtParams = requests.post(url=url, json=data, cookies=cookie).json()['result']['content']['smtParams']
      url = 'https://uat-scm.huaqiu.com/hqScm/approve/smt/smtMirrorQuoteConfirm'
      data = {
        'approveId': approveId_list[approveNo_list.index(approveNo)],
        'onlinePrice': 500,
        'smtParams': smtParams,
        'smtParamsPrice':{
            "smt_goods_fee": 614,
            "smt_order_fee": 614,
            "smtFee": 614
        }
      }
      res = requests.post(url=url, json=data, cookies=cookie).json()
      print(res)



def push_bom_to_quote():
  print(demandSn)
  url = 'https://uat-scm.huaqiu.com/hqScm/approve/bom/queryScmApproveBomPage'
  data = {
    'demandSn': demandSn,
    'approveType': 3,
  }
  res = requests.post(url=url, json=data, cookies=cookie).json()
  print(res)
  global QuoteSn, approveNo_list, approveId_list
  approveNo_list = jsonpath.jsonpath(res,'$.result..approveNo')
  approveId_list = jsonpath.jsonpath(res,'$.result..approveId')
  print(approveId_list, 'id')
  QuoteSn = ''
  for approveNo in approveNo_list:
      url = 'https://uat-scm.huaqiu.com/hqScm/approve/bom/findApproveBomMirrorDetail'
      data = {
        "approveNo": approveNo,
        "approveType": 3,
        "getAllBomItem": 1
      }
      res = requests.post(url=url, json=data, cookies=cookie).json()
      approveBomItem = jsonpath.jsonpath(res,'$.result.approveBomItem..mirrorBomItemId')
      # print(approveBomItem)
      url = 'https://uat-scm.huaqiu.com/hqScm/approve/bom/editProcess'
      data = {
          'itemIds': approveBomItem,
          'process': 2
      }
      requests.post(url=url, json=data, cookies=cookie).json()
      url = 'https://uat-scm.huaqiu.com/hqScm/approve/bom/rePushBomToQuote'
      data = {
          'approveNo': approveNo,
          'bomApproveId': approveId_list[approveNo_list.index(approveNo)],
          'itemIds': approveBomItem,
          'requoteReason': '测试'
      }
      res = requests.post(url=url, json=data, cookies=cookie).json()
      # print(res)
      url = 'https://uat-scm.huaqiu.com/hqScm/approve/bom/findApproveBomMirrorDetail'
      data = {
          "approveNo": approveNo,
          "approveType": 3,
          "getAllBomItem": 1
      }
      erpQuoteSn = requests.post(url=url, json=data, cookies=cookie).json()['result']['erpQuoteSn']
      print(erpQuoteSn)
      QuoteSn = QuoteSn + ''.join(erpQuoteSn) + ','
  # print(QuoteSn)


def save_quote():
    print(QuoteSn)
    url = 'https://uat-scm.huaqiu.com/scmoffer/web/orderItems/pageList'
    data = {
        'orderSn': QuoteSn,
        'type': 2
    }
    res = requests.post(url=url, json=data, cookies=cookie).json()
    save_data_list = res['result']
    # print(save_data_list)
    orderId = jsonpath.jsonpath(res, '$.result..orderId')[0]
    # print(orderId)
    itemId_list = jsonpath.jsonpath(res,'$.result..itemId')
    url = 'https://uat-scm.huaqiu.com/scmoffer/web/orderItems/addDispatcher'
    item_data = {
        'idList': itemId_list,
        'userId': 1,
        'userName': '超级管理员',
        'submitType': 1,
        'itemAuditStatus': 20
    }
    print(item_data)
    requests.post(url=url, json=item_data, cookies=cookie).json()
    url = 'https://uat-scm.huaqiu.com/scmoffer/web/goods/getMatterByModel'
    data = {
      "goodsName": "taoting001",
      "orderId": orderId
    }
    matte_list = requests.post(url=url, json=data, cookies=cookie).json()['result']
    print(matte_list)
    # randlist = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    randlist = [0]
    for save_data in save_data_list:
        try:
            url = 'https://uat-scm.huaqiu.com/scmoffer/web/orderItems/save'
            randint = int(random.sample(randlist, 1)[0])
            print(randint)
            randlist.remove(randint)
            save_data.update(matte_list[randint])
            save_data.update({
                'purchasePrice': 66.66,
                'suggestPrice': 88.88,
                'dt': "1-4",
                'quotationNumber': 8000,
                'lossRemark': 'MOQ要求',
                # 'brandName': matte_list[randint]['providerName'],
                'brandName': 'HTC',
                'bomSupplierName': 'HQCHIP-TTTEST',
                'supplierName': '测试合作库存优化',
            })
            # if matte_list[randint]['bomSupplierName'] == None:
            #     save_data.update({
            #         'bomSupplierName': 'HQCHIP-TTTEST',
            #         'supplierName': '测试合作库存优化',
            #     })
            if matte_list[randint]['encap'] == '':
                save_data.update({
                    'encap': '-',
                })
            # print(json.dumps(save_data,indent=3,ensure_ascii=False))
            res = requests.post(url=url, json=save_data, cookies=cookie,timeout=0.5).json()
            print(res)
        except:
            pass
    time.sleep(1)
    url = 'https://uat-scm.huaqiu.com/scmoffer/web/orderItems/submitOffer'
    res = requests.post(url=url, json=item_data, cookies=cookie).json()
    print(res)
    url = 'https://uat-scm.huaqiu.com/scmoffer/web/orderItems/examine'
    res = requests.post(url=url, json=item_data, cookies=cookie).json()
    print(res)


def approve_bom():
    print('waitting for quote result')
    # time.sleep(10)
    for approveNo in approveNo_list:
        url = 'https://uat-scm.huaqiu.com/hqScm/approve/bom/bomAudit'
        data = {
          "approveNo": approveNo,
          "id": approveId_list[approveNo_list.index(approveNo)],
          "approveId": approveId_list[approveNo_list.index(approveNo)],
          "auditStatus": 1
        }
        res = requests.post(url=url, json=data, cookies=cookie).json()
        # print(res)
        while not res['result']:
            res = requests.post(url=url, json=data, cookies=cookie).json()
            print(res)
        url = 'https://uat-scm.huaqiu.com/hqScm/approve/bom/bomDirectorAudit'
        res = requests.post(url=url, json=data, cookies=cookie).json()
        print(res)


def sale_confirm():
    # demandId = '1811316100672933889'
    url = 'https://uat-scm.huaqiu.com/hqScm/demand/saleConfirm'
    data = {
      "demandId": demandId
    }
    res = requests.post(url=url, json=data, cookies=cookie).json()
    # print(res)
    url = 'https://uat-scm.huaqiu.com/hqScm/demand/getDetail'
    base_data = requests.post(url=url, json=data, cookies=cookie).json()['result']
    base_data_info = copy.deepcopy(base_data)
    url = 'https://uat-scm.huaqiu.com/hqScm/demand/getDemandQuoteDetail'
    quote_detail = requests.post(url=url, json=data, cookies=cookie).json()['result']
    base_data_info.update(base_data['baseInfo'])
    base_data_info.update(quote_detail)
    base_data_info.update(
        {
            'saveType': '2',
            'payType': 3,
            'prepaidAmount': "0",
            'prepayRate': 0,
            'customerExpectedTime': '2025-08-05'
        }
    )
    url = 'https://uat-scm.huaqiu.com/hqScm/salesOrder/insert'
    res = requests.post(url=url, json=base_data_info, cookies=cookie).json()
    # print(res['result']['orderSn'])
    global orderSn
    orderSn = res['result']['orderSn']
    return res['result']['orderSn']
    # print(json.dumps(res,indent=3,ensure_ascii=False))


def approve_bom_pay():
    print(orderSn)
    if orderSn == '':
        return
    url = 'https://uat-scm.huaqiu.com/hqScm/approve/bom/queryScmApproveBomPage'
    data = {
        'saleCode': orderSn,
        'approveType': 5,
    }
    print(data)
    res = requests.post(url=url, json=data, cookies=cookie).json()
    i = 0
    while not res['result'] and i < 10:
        time.sleep(0.5)
        res = requests.post(url=url, json=data, cookies=cookie).json()
        print('11111111111',res)
        i += 1
    # global QuoteSn, approveNo_list, approveId_list
    approveNo_list = jsonpath.jsonpath(res, '$.result..approveNo')
    approveId_list = jsonpath.jsonpath(res, '$.result..approveId')
    print(approveId_list, 'id')
    for approveNo in approveNo_list:
        url = 'https://uat-scm.huaqiu.com/hqScm/approve/bom/bomAudit'
        data = {
          "approveNo": approveNo,
          "id": approveId_list[approveNo_list.index(approveNo)],
          "approveId": approveId_list[approveNo_list.index(approveNo)],
          "auditStatus": 1
        }
        res = requests.post(url=url, json=data, cookies=cookie).json()
        print(res)
        url = 'https://uat-scm.huaqiu.com/hqScm/approve/bom/bomDirectorAudit'
        res = requests.post(url=url, json=data, cookies=cookie).json()
        print(res)


# def project_quote():
#     ####SMT项目报价####
#     for demandPcbaId in demandPcbaId_list:
#         url = 'https://fat-scm.huaqiu.com/hqScm/demand/updateSmtOfflineQuote'
#         data = {
#             'demandPcbaId': demandPcbaId,
#             'modifyAfterPrice': 500,
#             'modifyPrice': 0,
#             'smtQuoteType': 0
#         }
#         res = requests.post(url=url,json=data,cookies=hepeng_cookie).json()
#         print(res)
#     url = 'https://fat-scm.huaqiu.com/hqScm/demand/pushProjectQuote'
#     data = {
#         'demandId': demandId,
#         'approveStatus': 1
#     }
#     requests.post(url=url, json=data, cookies=hepeng_cookie).json()
#     url = 'https://fat-scm.huaqiu.com/hqScm/demand/saleProjectQuoteAudit'
#     requests.post(url=url, json=data, cookies=hepeng_cookie).json()



def run(Sn):
    s = time.time()
    create_order(Sn)
    approve_smt()
    push_bom_to_quote()
    save_quote()
    approve_bom()
    try:
        print('----------------------------------------------------------------')
        project_quote()
        orderDa = sale_confirm()
        orderTl = 'TL'+orderDa[2:]
        print(f'create order successful: {orderDa}')
        res = 0
    except:
        print('----------------------------------------------------------------')
        print('create order failed: pcb order is not finished')
        res = -1
        orderDa = ''
        orderTl = ''
    # try:
    #     approve_bom_pay()
    # except:
    #     pass
    e = time.time()
    print(e-s)
    return res,orderDa,orderTl





# url = 'https://uat-scm.huaqiu.com/hqScm/approve/bom/queryScmApproveBomPage'
# data = {
#         'saleCode': '1111111111',
#         'approveType': 5,
# }
# res = requests.post(url=url, json=data, cookies=cookie).json()
# print(res)
