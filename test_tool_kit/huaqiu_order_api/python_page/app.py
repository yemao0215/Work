import base64
import glob
import os
import re
import time
import json
from datetime import datetime
from urllib.parse import quote
from io import BytesIO

import jsonpath
import qrcode
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, render_template, request, render_template_string, jsonify, send_file,abort
from logzero import json

import pcb_tool
from huaqiu_order_api.HC2016_admin.ask.sensitive_words_detection import SensitiveWordsDetection
from huaqiu_order_api.HC2018_admin.ECCN_add.ECCN_Mouser_sync import EccnMouserSync
from huaqiu_order_api.HC2018_admin.auto_stock.auto_stock import AutoStock
from huaqiu_order_api.HC2018_admin.dgk_goods_means.dgk_goods_means import GoodsMeans
from huaqiu_order_api.HC2018_admin.login.login import Login
from huaqiu_order_api.HC2018_admin.openapi.goods_profile_obtain import GoodsProfileObtain
from huaqiu_order_api.HC2018_admin.stock_up.import_stock_up import StockUp
from huaqiu_order_api.HC2018_admin.stock_up.self_order_stock_up import SelfOrderStockUp
from huaqiu_order_api.HC2018_admin.supplier_goods_publish.consign_publish import ConsignPublish
from huaqiu_order_api.HQCHIP.Commonly_kit_tool.php_antisequence import PhpAntisequence
from huaqiu_order_api.HQCHIP.Es.es_search_sql import EsSearchSQL
from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.HC2016_APP_SEC_search.HC2016_APP_SEC_search import HC2016APPSECSearch
from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.OpenAPI_Goods.goods_search import GoodsNameSearch
from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.OpenAPI_Order.create_order import CreateOrder
from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.OpenAPI_Order.order_detail_search import OrderDetailSearch
from huaqiu_order_api.HQCHIP.HQCHIP_OpenAPI.OpenAPI_Order.pay_order import PayOrder
from huaqiu_order_api.HQCHIP.mian_ic import RunIC
from huaqiu_order_api.HQCHIP.mongoDB.mongodb_renew import MongodbRenew
from huaqiu_order_api.HQCHIP.product.hotSearchword.hotSearchword import HotSearchWord
from huaqiu_order_api.HQCHIP.search.search_rule.search_filtration_rule import SearchFiltrstionRule
from huaqiu_order_api.HQCHIP.search.search_tool.overseas_agent_stock_api import OverseAgentStockApi
from huaqiu_order_api.HQCHIP.search.search_tool.search_tool_kit import SearchToolKit
from huaqiu_order_api.HQCHIP.search.stock_update.supplier_update import SupplierUpdate
from huaqiu_order_api.HQCHIP.search.supplier_search.element14_search_cn import Element14Search
from huaqiu_order_api.HQCHIP.search.supplier_search.mide_search import MiDeSearch
from huaqiu_order_api.HQCHIP_Activity.card_manage.coupon.coupon_list import Coupon
from huaqiu_order_api.HQCHIP_Activity.card_manage.voucher.user_voucher import UserVocher
from huaqiu_order_api.HQCHIP_Activity.card_manage.voucher.voucher_reception import VoucherReception
from huaqiu_order_api.HQCHIP_Activity.hqshop.hqshop_activity.hqshop_activity import HqshopActivity
from huaqiu_order_api.HQCHIP_Activity.hqshop.hqshop_subject.hqshop_subject import HqshopSubject
from huaqiu_order_api.HQCHIP_ERP.erp_order_cancellation import ErpOrderCancellation
from huaqiu_order_api.HQCHIP_ERP.erp_order_putaway import ErpOrderPutaway
from huaqiu_order_api.HQCHIP_ERP.erp_order_stock import ErpOrderStock
from huaqiu_order_api.HQCHIP_ERP.erp_stock_purchase import ErpStockPurchase
from huaqiu_order_api.HQCHIP_ERP.erp_sync_api import ErpSyncAPI
from huaqiu_order_api.HQCHIP_ERP.login import ErpLogin
from huaqiu_order_api.HQCHIP_PAY.assets.balance_payment import BalancePayment
from huaqiu_order_api.HQCHIP_PAY.banlk_statement.banlk_statement import BanlkStatement
from huaqiu_order_api.HQCHIP_PAY.recharge.center_pay_callback import CenterPayCallback
from huaqiu_order_api.HQCHIP_PAY.withdraw.withdraw_pay_status_verify import WithdrawPayStatusVerify
from huaqiu_order_api.HQCHIP_RCS.reported_data.reported_data_apis import ReportedData
from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.HQCHIP_SRM.partner_settle.partner_potential import PartnerPotential
from huaqiu_order_api.HQCHIP_SRM.pass_partner.pass_partner import PassPartner
from huaqiu_order_api.HQCHIP_SRM.settle_goods_bill.settle_goods_file import SettleGoods
from huaqiu_order_api.HQCHIP_Task.hq_task import HQTask
from huaqiu_order_api.HQCHIP_Task.login import TaskLogin
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_FAT.PDA_login import FATPdaLogin
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_FAT.PDA_theupper import FATPdaTheupper
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_inventory import PdaInventory
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_login import PdaLogin
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_pick import PdaPick
from huaqiu_order_api.HQCHIP_WMS.HQCHIP_PDA_UAT.pda_theupper import PdaTheupper
from huaqiu_order_api.HQCHIP_WMS.wms_in_warehouse import WmsInWarehouse
from huaqiu_order_api.HQCHIP_WMS.wms_inventory import WmsInventory
from huaqiu_order_api.HQCHIP_WMS.wms_out_warehouse import WmsOutWarehouse
from huaqiu_order_api.HQCHIP_Zentao.log_work_hour import LogWorkHour
from huaqiu_order_api.HQPCB.PCB_Reception.PCB_order import PCBOrder
from huaqiu_order_api.HQSMT.SMT_Reception.SMT_order import SmtOrder
from huaqiu_order_api.HQSTENCIL.Stencil_Reception.Stencil_order import StencilOrder
from huaqiu_order_api.SSO_Reception.orderSensitiveMsgEncrypt import orderSensitiveMsgEncrypt
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception
from huaqiu_order_api.HQCHIP.ic_order import IcOrder
from huaqiu_order_api.HQCHIP_RCS.rule.data_source import DataSource
from huaqiu_order_api.HQPCB.main_run import RunPcb
from huaqiu_order_api.SSO_Reception.user_register import UserRegister
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import log_file, account_yaml, yaml_file, qr_code_dir, cookie_dir, supplier_dir, \
    JenkinsProjectYaml_dir
from huaqiu_order_api.common.my_tool import convert_numpy_types
from huaqiu_order_api.common.yaml_handler import write_yaml, read_yaml
from huaqiu_order_api.help_oneself_tool.timestamp_convert import TimestampConvert
from huaqiu_order_api.help_oneself_tool.windows_shutdown import WindowsShutdown
from huaqiu_order_api.help_oneself_tool.yzmcode_obtain import YzmCodeObtain
from huaqiu_order_api.inform.dingtalk_config import DingTalkHandle
from huaqiu_order_api.mian_goods_stock_warehouse import MainGoodsStockWarehouse
from huaqiu_order_api.project_jenkins.login import JenkinsLogin
from huaqiu_order_api.project_jenkins.project_build_jenkins import ProjectBuildJenkins
from huaqiu_order_api.project_sqlreview.login import SqlReviewLogin
from huaqiu_order_api.project_sqlreview.sqlreview_kit_tool import SqlReviewKitTool
from huaqiu_order_api.python_page.logreader import get_latest_log
from huaqiu_order_api.reconstruction_project.i_2025activity.i_2025muniheiactivity import Muniheiactivity

app = Flask(__name__, template_folder='templates')
# 使通过jsonify返回的中文显示正常，否则显示为ASCII码
app.config["JSON_AS_ASCII"] = False
# app.config['SERVER_NAME'] = 'www.yemaotest.com'
# 添加RESTFUL_JSON配置
app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))

# 钉钉机器人Webhook地址
DINGTALK_WEBHOOK = 'https://oapi.dingtalk.com/robot/send?access_token=25a90a87d158533948196f11e0746502039d606b7f071f4b87cd00dbcdeb3669'
# def schedule_task():
#     """定时任务: 每天 21:00:00 执行关机操作"""
#     import_time = datetime.now().strftime("%Y-%m-%d") + " 21:00"
#     shutdown = WindowsShutdown(import_time)
#     shutdown.schedule_shutdown()
#
# # 初始化 APScheduler
# scheduler = BackgroundScheduler()
#
# # 添加定时任务，每天的 21:00 执行一次 `schedule_task` 方法
# scheduler.add_job(schedule_task, 'cron', hour=21, minute=0, second=0)
#
# # 启动定时任务
# scheduler.start()



@app.route('/')
def index():
    # if request.method == 'POST':
    #     # 获取第一个表单的数据
    #     form1_data = request.form['form1']
    #     # 获取第二个表单的数据aa
    #     form2_data = request.form['form2']
    #
    #     # 在这里可以对表单数据进行处理或保存到数据库等操作
    #
    #     return 'Form submitted successfully!'
    # 读取YAML文件，得到供应商字典
    supplier_dict = read_yaml(supplier_dir)
    jenkins_project_str = read_yaml(JenkinsProjectYaml_dir)
    jenkins_project = jenkins_project_str.split()
    # 调试：打印变量内容
    # print(f"传递给模板的供应商数据：{supplier_dict}")
    return render_template('index.html', suppliers=supplier_dict, JenkinsProjects=jenkins_project)


@app.route('/submit', methods=['POST'])
def submit():
    #### 风控上报 ####
    phone = request.form['phone']
    name = request.form['name']
    password = request.form['password']
    form = request.form['type']
    uid = request.form['pcbuid']
    ic_params = {'form': form}
    pass_port_user_msg = {"phone": phone, "name": name, "password": password}
    user_msg = {'PassPort': pass_port_user_msg}
    pcb_params = {'UID': uid}
    write_yaml(account_yaml, ic_params)
    write_yaml(account_yaml, user_msg)
    pcb_tool.PcbTools().write_yaml(pcb_params)
    # return jsonify({"message": "数据已成功处理"})
    #处理表单数据
    for i in range(1):
        target_rss = SOOLogin("uat-rcs.huaqiu.com", "api").target_login()
        if form == "ic":
            rss = SSO_Reception('https://uat-www.hqchip.com').login()
            IcOrder(rss).add_cart().place_an_order()
            DataSource(target_rss).data_source_list(form).tactics_obtain()
            ReportedData(form).reported_data().risk_evaluate()
        elif form == "pcb":
            RunPcb().main('phpsessid')
            RunPcb().main('mid', uid)
            RunPcb().main("orders")
            DataSource(target_rss).data_source_list(form).tactics_obtain()
            ReportedData(form).reported_data().risk_evaluate()
            # ReportedData(form).risk_evaluate()
    # 读取日志文件内容
    log_files = glob.glob(os.path.join(log_file, '*.log'))
    # 对日志文件按照修改时间进行排序
    log_files.sort(key=os.path.getmtime, reverse=True)
    # 获取最新的日志文件
    latest_log_file = log_files[0] if log_files else None
    if latest_log_file:
        with open(latest_log_file, 'rb') as f:
            log_content = f.readlines()
            # print(type(log_content))
            total_lines = len(log_content)
            for i, content in enumerate(log_content):
                log_content[i] = content.decode('utf-8', 'ignore')
            return render_template('logs.html', data=log_content, encoding='utf-8')
    else:
        return '没有找到日志文件'
@app.route('/opencreate', methods=['POST'])
def opencreate():
    """OPENAPI生成订单"""
    APP_KEY = request.form['APP_KEY']
    APP_SEC = request.form['APP_SEC']
    phone = request.form['phone']
    goods_name = request.form['goodsName']
    goods_id = request.form['goodsId']
    number = request.form['number']
    warehouse_id = request.form['warehouse']
    goods_type = request.form['OrderType']
    vat_type = request.form['vat_type']
    remark = request.form['remark']
    partial_order_alloweb = request.form['openapiPartialOrderAlloweb']
    env_type = request.form['openapiEnvType']
    ic_order_params = {'goods_id': goods_id, "number": number, "warehouse_id": warehouse_id, "vat_type": vat_type, "vat_sub_type": '', 'shipping_method': '1', 'relation_smt_order_sn': ''}
    conf_phone_goods_msg = {"APIPhone": phone, "APIGoodsName": goods_name, "APIGoodsType": goods_type, "APIOderRemark": remark,
                            "APIPartialOrderAlloweb": partial_order_alloweb} # , "APIProductNum": product_num
    app_key_conf_dict = {}
    if APP_KEY != "":
        setattr(Data, 'APP_KEY', APP_KEY)
        if APP_SEC == "":
            APP_SEC, app_key_conf_dict = HC2016APPSECSearch().mian_app_sec()
            conf_phone_goods_msg["APP_KEY"] = APP_KEY
            conf_phone_goods_msg["APP_SEC"] = APP_SEC
        else:
            if env_type == 'pro':
                app_key_conf_dict = {"permission_vmi_order": 1}
            else:
                app_key_conf_dict = {"permission_vmi_order": 0}
            conf_phone_goods_msg["APP_KEY"] = APP_KEY
            conf_phone_goods_msg["APP_SEC"] = APP_SEC
    order_params = {"HQCHIP_GOODS": ic_order_params}
    write_yaml(account_yaml, order_params)
    write_yaml(yaml_file, conf_phone_goods_msg)
    # 检查必填字段  env_type 和APP_SEC关系
    if env_type == 'pro' and APP_SEC == '':
        return jsonify({"message": "必填字段：环境为正式、应用密钥不能为空，请检查输入值!!!!!", "msgcode": 200})
    # 检查必填字段 phone, number
    if phone == '' or number == '':
        return jsonify({"message": "必填字段：phone、number为空，请检查输入值!!!!!", "msgcode": 200})

    # 初始化允许创建订单的标志
    can_create_order = True
    # 判断 goods_name 和 goods_id 的条件
    if goods_name == '' and goods_id == '':
        can_create_order = False
        return jsonify({"message": "必填字段：goods_name、goods_id不能同时为空，请检查输入值!!!!!", "msgcode": 200})
    # 以下代码是2024-10-18之前版本，此版本在goods_id不为空时，无法创建订单，直接返回错误信息，与预想流程不一致
    # if goods_name == '' and app_key_conf_dict != {} and 'permission_vmi_order' in app_key_conf_dict:
    #     can_create_order = False
    #     return jsonify({"message": "必填字段为空，请检查输入值!!!!!", "msgcode": 200})
    #
    # # 如果 goods_id 为空但 goods_name 不为空，则需检查权限
    # if goods_id == '' and goods_name != '':
    #     if 'permission_vmi_order' not in app_key_conf_dict:
    #         can_create_order = False
    #         return jsonify({"message": "无下VMI单权限，无法继续操作", "msgcode": 200})


    # 以下代码是2024-10-18之后版本，此版本兼容在goods_id不为空时，无法创建订单，直接返回错误信息优化
    # 如果 goods_id 为空但 goods_name 不为空，则需检查权限--是否存在：VMI单权限
    if goods_id == '' and goods_name != '':
        if 'permission_vmi_order' not in app_key_conf_dict:
            can_create_order = False
            return jsonify({"message": "必填字段：goods_name不为空、goods_id为空时无下VMI单权限，无法继续操作", "msgcode": 200})

    # 执行创建订单
    print(can_create_order)
    # 允许创建订单的标志是否为True
    if can_create_order == True:
        error_message, order_sn, order_id, out_order_no, sgin, failed_goods_list, goods_list_new = CreateOrder(env_type=env_type).openapi_make()
        if order_sn is None:
            return jsonify({"message": f"商城开放接口生单失败，报错信息为：{error_message}", "error_goods_list": failed_goods_list, "msgcode": 200})
        if failed_goods_list == []:
            return jsonify({
                "message": "订单成功生成,请通知相关在ERP上确认该订单",
                "result": {
                    "SignAture": sgin,
                    "order_sn": order_sn,
                    "ic_order_id": order_id,
                    "out_order_no": out_order_no,
                    "order_tracking_number": out_order_no,
                    "order_detail_goods_list": goods_list_new
                },
                "msgcode": 200
            })
        else:
            return jsonify({
                "message": "订单生成成功，但部分商品生成失败，请检查商品信息是否正确！！！",
                "result": {
                    "SignAture": sgin,
                    "order_sn": order_sn,
                    "ic_order_id": order_id,
                    "out_order_no": out_order_no,
                    "order_tracking_number": out_order_no,
                    "error_goods_list": failed_goods_list,
                    "order_detail_goods_list": goods_list_new
                },
                "msgcode": 200
            })
    return jsonify({"message": "无法生成订单，未满足条件", "msgcode": 200})
@app.route('/openpay', methods=['POST'])
def openpay():
    """OPENAPI支付订单"""
    order_sn = request.form['order']
    order_id = request.form["OrderId"]
    out_order_no = request.form["Outorder"]
    data_amount = request.form['DataAmount']
    pay_type = request.form['payType']
    if pay_type == "1" or pay_type == "3":
        return jsonify({"message": "此支付方式在商城暂不支持，若有支持通知，则同步告知！！！", "msgcode": 200})
    else:
        if order_sn == '':
            return jsonify({"message": "必填字段未填，请核对传参！！！", "msgcode": 404})
        else:
            setattr(Data, 'ic_order_sn', order_sn)
            setattr(Data, 'ic_order_id', order_id)
            setattr(Data, 'pay_type', pay_type)
            order_detaill_data = OrderDetailSearch().order_detail_search(order_sn=order_sn)
            order_amount = jsonpath.jsonpath(order_detaill_data, "$..order_amount")[0]
            data, error_message = PayOrder().order_pay(data_amount=data_amount)
            if order_id == "":
                order_id = getattr(Data, "ic_order_id", '')
                out_order_no = getattr(Data, "out_order_no", '')
            if data == None:
                return jsonify({"message": f"支付失败,报错信息为{error_message}，请检查订单是否处于支付状态",
                                "argument_data": {
                                    "order_sn": order_sn,
                                    "order_id": order_id,
                                    "pay_type": pay_type,
                                    "out_order_no": out_order_no,
                                    "order_amount": order_amount,
                                    "data_amount": data_amount
                                },
                                "msgcode": 404})
            else:
                return jsonify({"message": f"支付成功，执行结果为：{data}, 请到ERP中核对状态", "argument_data": {
                    "order_sn": order_sn,
                    "order_id": order_id,
                    "pay_type": pay_type,
                    "out_order_no": out_order_no,
                    "order_amount": order_amount,
                    "data_amount": data_amount
                }, "msgcode": 200})

@app.route('/opendetail', methods=['POST'])
def opendetail():
    """OPENAPI订单详情"""
    order_sn = request.form['OrderSn']
    out_order_no = request.form['orderNo']
    order_id = request.form["orderId"]
    if order_sn == '':
        return jsonify({"message": "必填字段未填，请核对传参！！！", "msgcode": 404})
    else:
        data = OrderDetailSearch().order_detail_search(order_sn, order_id, out_order_no)
        if data == "":
            return jsonify({"message": "获取订单详情失败，请检查传参", "msgcode": 404})
        else:
            return jsonify({"message": "获取订单详情成功", "detail": data, "msgcode": 200})
@app.route('/opengoodssearch', methods=['POST'])
def opengoodssearch():
    """型号搜索"""
    environment_type = request.form['APPKEYReviewenvironmentType']
    APP_KEY = request.form['APP_KEY']
    APP_SEC = request.form['APP_SEC']
    goods_name = request.form['goodsName']
    goods_id = request.form['goodsId']
    goodsGcode = request.form['goodsGcode']
    version_type = request.form['goodsVersionType']
    number = request.form['RequestCount']
    ic_order_params = {'goods_id': goods_id, "number": '', "warehouse_id": "2", "vat_type": '', "vat_sub_type": ''}
    conf_phone_goods_msg = {"APIPhone": '', "APIGoodsName": goods_name, "APIGoodsType": '', "APIOderRemark": '',  "APIPartialOrderAlloweb": '', "APIGcode": goodsGcode}
    if APP_KEY != "":
        setattr(Data, 'APP_KEY', APP_KEY)
        if APP_SEC == "":
            APP_SEC, app_key_conf_dict = HC2016APPSECSearch().mian_app_sec()
            conf_phone_goods_msg["APP_KEY"] = APP_KEY
            conf_phone_goods_msg["APP_SEC"] = APP_SEC
        else:
            conf_phone_goods_msg["APP_KEY"] = APP_KEY
            conf_phone_goods_msg["APP_SEC"] = APP_SEC
    order_params = {"HQCHIP_GOODS": ic_order_params}
    write_yaml(account_yaml, order_params)
    write_yaml(yaml_file, conf_phone_goods_msg)
    if goods_name == '':
        return jsonify({"message": "必填字段为空，请检查输入值!!!!!", "msgcode": 200})
    else:
        (openapi_goods_search_res, openapi_goods_query_res, openapi_goods_detail_res, openapi_goods_list_res, openapi_goods_mquery_res,
         openapi_goods_query_best_res, openapi_goods_querybygcode_res, openapi_goods_product_res, openapi_goods_stock_detail_res) = GoodsNameSearch(environment_type=environment_type, version_type=version_type).mian_goods_search()
        return jsonify({"message": {
                                "/goods/search/": openapi_goods_search_res,
                                "/goods/query/": openapi_goods_query_res,
                                "/goods/detail/": openapi_goods_detail_res,
                                "/goods/list/": openapi_goods_list_res,
                                "/goods/mquery/": openapi_goods_mquery_res,
                                "/goods/query/best/": openapi_goods_query_best_res,
                                "/goods/querybygcode/": openapi_goods_querybygcode_res,
                                "/goods/porduct/info/": openapi_goods_product_res,
                                "/goods/stock/query": openapi_goods_stock_detail_res
                            }})
@app.route('/recharge', methods=['POST'])
def recharge():
    """余额充值"""
    frequency = request.form['frequency']
    phone = request.form['phone']
    password = request.form["password"]
    Amount = request.form['Amount']
    activity_type = request.form['rechargeActivityType']
    if phone == "" and password == "" and Amount == '':
        return jsonify({"message": "入参参数不能为空，请检查", "msgcode": 200})
    else:
        if int(Amount) >= 5000000:
            return jsonify({"message": "输入的充值金额过大，请核对充值金额！！！", "msgcode": 200})
        else:
            pass_port_user_msg = {"phone": phone, "name": '', "pwd": password}
            user_msg = {'PassPort': pass_port_user_msg}
            write_yaml(account_yaml, user_msg)
            setattr(Data, 'Amount', Amount)
            setattr(Data, 'activity_type', activity_type)
            recharge_order = ''
            # centerTradeNoExtend = ''
            recharge_order_voucher_json = None
            for i in range(int(frequency)):
                recharge_order, centerTradeNoExtend = CenterPayCallback().mian_pay_callback()
                target_rss = SOOLogin("uat-activity.hqchip.com", "ecmc").target_login()
                voucher_create_json = UserVocher(target_rss, recharge_order, unionId=getattr(Data, 'uid', ''), activity_id=getattr(Data, 'voucher_activity_id', ''), amount=Amount).mian_activity_voucher_create_accounting()
                recharge_order_voucher_json = {"recharge_order": recharge_order, "centerTradeNoExtend": centerTradeNoExtend,
                                               "voucher_create": voucher_create_json}
            if recharge_order == None:
                return jsonify({"message": "创建充值订单失败", "msgcode": 404})
            else:
                return jsonify({"message": "创建充值订单成功",
                                "data": {"phone": phone, "password": password, "Amount": Amount,
                                         "recharge_order_create": recharge_order_voucher_json},
                                "msgcode": 200})
@app.route('/banlkstatement', methods=['POST'])
def banlkstatement():
    frequency = request.form['frequency']
    Amount = request.form['Amount']
    if Amount == '':
        return jsonify({"message": "入参参数不能为空，请检查", "msgcode": 200})
    else:
        setattr(Data, 'Amount', Amount)
        for i in range(int(frequency)):
            BanlkStatement().banlk_statement_create()
        return jsonify({"message": "同步成功，请到ERP的公司转账查询", "msgcode": 200})
@app.route('/eccnSync', methods=['POST'])
def eccnSync():
    frequency = request.form['frequency']
    goods_name = request.form['goodsName']
    brand_name = request.form['brandName']
    eccn = request.form['eccnCode']
    if goods_name == "" and brand_name == "" and eccn == "":
        return jsonify({"message": "入参参数不能为空，请检查", "msgcode": 200})
    else:
        result_eccn_sync = EccnMouserSync(goods_name, brand_name, eccn).eccn_mouser_sync().eccn_mouser_sync_result_search()
        if result_eccn_sync == '':
            return jsonify({"message": "同步失败，请检查输入型号等关键参数的存在性", "msgcode": 200})
        else:
            return jsonify({"message": result_eccn_sync + "，请到DOS核查同步结果",
                            "argument": {"goods_name": goods_name, "brand_name": brand_name, "eccn": eccn},
                            "msgcode": 200})
@app.route('/withdrawAct', methods=['POST'])
def withdrawAct():
    """活动余额提现"""
    recharge_order = request.form['rechargeOrder']
    phone = request.form['phone']
    password = request.form["password"]
    Amount = request.form['Amount']
    pay_password = request.form['paypassword']
    if recharge_order == '':
        recharge_order = None
    if Amount == '':
        Amount = None
    if pay_password == '':
        pay_password = None
    if phone == '' and password == '':
        return jsonify({"message": "手机号码或登录密码不能为空，请检查", "msgcode": 200})
    else:
        pass_port_user_msg = {"phone": phone, "name": '', "pwd": password}
        user_msg = {'PassPort': pass_port_user_msg}
        write_yaml(account_yaml, user_msg)
        pay_rss = SOOLogin("uat-pay.huaqiu.com", "management").target_login()
        withdraw_order,  withdrawAmount = WithdrawPayStatusVerify(pay_rss).mian_withdraw_flow(recharge_order=recharge_order, paypassword=pay_password, withdrawAmount=Amount)
        if withdraw_order != None:
            return jsonify({"message": "创建提现订单成功",
                            "data": {"phone": phone, "password": password, "withdrawAmount": withdrawAmount,
                                     "recharge_order": recharge_order, "withdraw_order": withdraw_order},
                            "msgcode": 200})
        else:
            return jsonify({"message": "创建提现订单失败", "msgcode": 404})

@app.route('/iccreate', methods=['POST'])
def create():
    """ic订单创建"""
    frequency = request.form['frequency']
    phone = request.form['phone1']
    name = request.form['name1']
    password = request.form['password1']
    goods_id = request.form['goodsId']
    number = request.form['number']
    warehouse_id = request.form['warehouse']
    vat_type = request.form['vat_type']
    vat_sub_type = request.form['vat_sub_type']
    shipping_method = request.form['shipping_method_type']
    # logger.info(phone, name, password, goods_id, muber, warehouse_id)
    ic_order_params = {'goods_id': goods_id, "number": number, "warehouse_id": warehouse_id, "vat_type": vat_type,
                       "vat_sub_type": vat_sub_type, 'shipping_method': shipping_method, 'relation_smt_order_sn': ''}
    pass_port_user_msg = {"phone": phone, "name": name, "pwd": password}
    user_msg = {'PassPort': pass_port_user_msg}
    order_params = {"HQCHIP_GOODS": ic_order_params}
    write_yaml(account_yaml, order_params)
    write_yaml(account_yaml, user_msg)
    for i in range(int(frequency)):
        RunIC().mian_ic_order_create()
    # 读取日志文件内容
    log_files = glob.glob(os.path.join(log_file, '*.log'))
    # 对日志文件按照修改时间进行排序
    log_files.sort(key=os.path.getmtime, reverse=True)
    # 获取最新的日志文件
    latest_log_file = log_files[0] if log_files else None
    if latest_log_file:
        with open(latest_log_file, 'rb') as f:
            log_content = f.readlines()
            # print(type(log_content))
            total_lines = len(log_content)
            for i, content in enumerate(log_content):
                log_content[i] = content.decode('utf-8', 'ignore')
            return render_template('logs.html', data=log_content, encoding='utf-8')

@app.route('/pcboperation', methods=['POST'])
def pcbbutton():
    """pcb订单操作"""
    form = request.form['type3']
    uid = request.form['pcbuid2']
    order_id = request.form['order']
    if form == "phpsessid":
        RunPcb().main('phpsessid')
    elif form == "mid":
        RunPcb().main('mid', uid)
    elif form == "orders":

        RunPcb().main('mid', uid)
        if order_id == "":
            RunPcb().main('orders')
        else:
            # 返单
            RunPcb().main('orders', order_id)
    elif form == "audit":
        RunPcb().main('phpsessid')
        if order_id == "":
            RunPcb().main('audit', order_id)
        else:
            logger.error("请输入需要审核订单id")
    elif form == "details":
        RunPcb().main('phpsessid')
        if order_id == "":
            RunPcb().main('audit', order_id)
        else:
            logger.error("请输入需要查询订单详情的订单id")
    elif form == "order_audit":
        RunPcb().main('phpsessid')
        RunPcb().main('order_audit')
    elif form == "order_pay":
        RunPcb().main('phpsessid')
        RunPcb().main('order_pay')
    elif form == "cam_doen":
        RunPcb().main('phpsessid')
        RunPcb().main('cam_doen')
    elif form == "run_pb":
        RunPcb().main('phpsessid')
        if order_id == "":
            RunPcb().main('run_pb', order_id)
        else:
            logger.error("请输入需要拼板审核确认的订单id")
    elif form == "ruku":
        RunPcb().main('phpsessid')
        if order_id == "":
            RunPcb().main('ruku', order_id)
        else:
            logger.error("请输入需要自动跑到发货的订单id")
    elif form == "order_ruku":
        RunPcb().main('phpsessid')
        RunPcb().main('order_ruku')
    elif form == "nextpcb_order":
        RunPcb().main('phpsessid')
        RunPcb().main('mid', uid)
        RunPcb().main('nextpcb_order')
    elif form == "review_order":
        RunPcb().main('phpsessid')
        RunPcb().main('mid', uid)
        RunPcb().main('review_order')
    else:
        logger.error(f"参数类型：{form}输入异常，请检查参数")
#         # 读取日志文件内容
    log_files = glob.glob(os.path.join(log_file, '*.log'))
    # 对日志文件按照修改时间进行排序
    log_files.sort(key=os.path.getmtime, reverse=True)
    # 获取最新的日志文件
    latest_log_file = log_files[0] if log_files else None
    if latest_log_file:
        with open(latest_log_file, 'rb') as f:
            log_content = f.readlines()
            # print(type(log_content))
            total_lines = len(log_content)
            for i, content in enumerate(log_content):
                log_content[i] = content.decode('utf-8', 'ignore')
            return render_template('logs.html', data=log_content, encoding='utf-8')

@app.route('/icoutbound', methods=['POST'])
def outbound():
    """IC订单一键出库"""
    phone = request.form['phone2']
    name = request.form['name2']
    password = request.form['password2']
    goods_id = request.form['goodsId']
    number = request.form['number']
    warehouse_id = request.form['warehouse1']
    vat_type = request.form['vat_type1']
    main_type = request.form['mainType']
    vat_sub_type = request.form['vat_sub_type']
    # logger.info(phone, name, password, goods_id, muber, warehouse_id)
    ic_order_params = {'goods_id': goods_id, "number": number, "warehouse_id": warehouse_id, "vat_type": vat_type, "vat_sub_type": vat_sub_type, 'shipping_method': '1', 'relation_smt_order_sn': ''}
    pass_port_user_msg = {"phone": phone, "name": name, "pwd": password}
    user_msg = {'PassPort': pass_port_user_msg}
    order_params = {"HQCHIP_GOODS": ic_order_params}
    write_yaml(account_yaml, order_params)
    write_yaml(account_yaml, user_msg)
    if main_type == "self_have":
        RunIC().mian_ic_order_spots()
    elif main_type == "supp_sa":
        RunIC().mian_ic_order_daigou()
    else:
        pass
    log_files = glob.glob(os.path.join(log_file, '*.log'))
    # 对日志文件按照修改时间进行排序
    log_files.sort(key=os.path.getmtime, reverse=True)
    # 获取最新的日志文件
    latest_log_file = log_files[0] if log_files else None
    if latest_log_file:
        with open(latest_log_file, 'rb') as f:
            log_content = f.readlines()
            # print(type(log_content))
            total_lines = len(log_content)
            for i, content in enumerate(log_content):
                log_content[i] = content.decode('utf-8', 'ignore')
            return render_template('logs.html', data=log_content, encoding='utf-8')
@app.route('/stencilOrder', methods=['POST'])
def stencilOrder():
    """钢网下单"""
    frequency = request.form['frequency']
    stencilphone = request.form['stencilphone']
    stencilname = request.form['stencilname']
    stencilpassword = request.form['stencilpassword']
    stencilFrame = request.form['stencilFrame']
    stencilType = request.form['stencilType']
    printingType = request.form['printingType']
    elec_tropolishing = request.form['elec_tropolishing']
    stencil_size = request.form['stencil_size']
    stencil_side = request.form['stencil_side']
    stencil_thickness = request.form['stencil_thickness']
    existing_fiducials = request.form['existing_fiducials']
    engineering_require = request.form['engineering_require']
    stencil_vat_type = request.form['stencil_vat_type']
    stencil_vat_sub_type = request.form['stencil_vat_sub_type']
    stencilNumber = request.form['stencilNumber']
    pass_port_user_msg = {"phone": stencilphone, "name": stencilname, "pwd": stencilpassword}
    ic_order_params = {'goods_id': '', "number": stencilNumber, "warehouse_id": "2", "vat_type": stencil_vat_type, "vat_sub_type": stencil_vat_sub_type}
    user_msg = {'PassPort': pass_port_user_msg}
    order_params = {"HQCHIP_GOODS": ic_order_params}
    write_yaml(account_yaml, order_params)
    write_yaml(account_yaml, user_msg)
    rss = SSO_Reception('https://uat-www.hqpcb.com').login()
    for i in range(int(frequency)):
        if printingType == "1" and stencil_size == "30*40":
            return jsonify({"message": "当印刷方式为 半自动印刷 时，尺寸30*40cm不可提交",
                            "argument": {"stencilFrame": stencilFrame, "stencilType": stencilType,
                                         "printingType": printingType, "existing_fiducials": existing_fiducials,
                                         "elec_tropolishing": elec_tropolishing, "stencil_size": stencil_size,
                                         "stencil_side": stencil_side, "stencilname": stencilname,
                                         "stencil_thickness": stencil_thickness, "stencilNumber": stencilNumber,
                                         "stencilphone": stencilphone, "stencilpassword": stencilpassword,
                                         "engineering_require": engineering_require, "stencil_vat_type": stencil_vat_type,
                                         "stencil_vat_sub_type": stencil_vat_sub_type},
                            "msgcode": 200})
        else:
            if stencil_vat_type == '3' and stencil_vat_sub_type == "0":
                order_sn = StencilOrder(rss, stencilFrame, stencilType, printingType, elec_tropolishing, stencil_size, stencil_side, stencil_thickness,
                             existing_fiducials,engineering_require).stencil_tmp_save().place_an_order()
                return jsonify({"message": "成功生成钢网订单", "order_sn": order_sn,
                                "argument": {"stencilFrame": stencilFrame, "stencilType": stencilType, "printingType": printingType,  "existing_fiducials": existing_fiducials,
                                             "elec_tropolishing": elec_tropolishing, "stencil_size": stencil_size, "stencil_side": stencil_side, "stencilname": stencilname,
                                             "stencil_thickness": stencil_thickness, "stencilNumber": stencilNumber, "stencilphone": stencilphone, "stencilpassword": stencilpassword,
                                             "engineering_require": engineering_require, "stencil_vat_type": stencil_vat_type, "stencil_vat_sub_type": stencil_vat_sub_type},
                                "msgcode": 200})
            elif stencil_vat_type == '1' and stencil_vat_sub_type == "2":
                order_sn = StencilOrder(rss, stencilFrame, stencilType, printingType, elec_tropolishing, stencil_size, stencil_side, stencil_thickness,
                             existing_fiducials, engineering_require).stencil_tmp_save().place_an_order()
                return jsonify({"message": "成功生成钢网订单", "order_sn": order_sn,
                                "argument": {"stencilFrame": stencilFrame, "stencilType": stencilType, "printingType": printingType,  "existing_fiducials": existing_fiducials,
                                             "elec_tropolishing": elec_tropolishing, "stencil_size": stencil_size, "stencil_side": stencil_side, "stencilname": stencilname,
                                             "stencil_thickness": stencil_thickness, "stencilNumber": stencilNumber, "stencilphone": stencilphone, "stencilpassword": stencilpassword,
                                             "engineering_require": engineering_require, "stencil_vat_type": stencil_vat_type, "stencil_vat_sub_type": stencil_vat_sub_type},
                                "msgcode": 200})

            elif stencil_vat_type == '0' and stencil_vat_sub_type == "3":
                order_sn = StencilOrder(rss, stencilFrame, stencilType, printingType, elec_tropolishing, stencil_size,
                                        stencil_side, stencil_thickness,
                                        existing_fiducials, engineering_require).stencil_tmp_save().place_an_order()
                return jsonify({"message": "成功生成钢网订单", "order_sn": order_sn,
                                "argument": {"stencilFrame": stencilFrame, "stencilType": stencilType, "printingType": printingType,  "existing_fiducials": existing_fiducials,
                                             "elec_tropolishing": elec_tropolishing, "stencil_size": stencil_size, "stencil_side": stencil_side, "stencilname": stencilname,
                                             "stencil_thickness": stencil_thickness, "stencilNumber": stencilNumber, "stencilphone": stencilphone, "stencilpassword": stencilpassword,
                                             "engineering_require": engineering_require, "stencil_vat_type": stencil_vat_type, "stencil_vat_sub_type": stencil_vat_sub_type},
                                "msgcode": 200})

            else:
                return jsonify({"message": "选泽发票类型和开票类型无法传入下一个代码片段",
                                "argument": {"stencilFrame": stencilFrame, "stencilType": stencilType, "printingType": printingType,  "existing_fiducials": existing_fiducials,
                                             "elec_tropolishing": elec_tropolishing, "stencil_size": stencil_size, "stencil_side": stencil_side, "stencilname": stencilname,
                                             "stencil_thickness": stencil_thickness, "stencilNumber": stencilNumber, "stencilphone": stencilphone, "stencilpassword": stencilpassword,
                                             "engineering_require": engineering_require, "stencil_vat_type": stencil_vat_type, "stencil_vat_sub_type": stencil_vat_sub_type},
                                "msgcode": 200})
@app.route('/smtOrder', methods=['POST'])
def smtOrder():
    """SMT下单"""
    frequency = request.form['frequency']
    phone = request.form['phone']
    name = request.form['name']
    password = request.form['password']
    application_sphere = request.form['applicationSphere']
    is_pcb_soft_board = request.form['isPcbSoftBoard']
    single_or_double_technique = request.form['singleOrDoubleTechnique']
    pcb_ban_width = request.form['width']
    pcb_ban_height = request.form['height']
    number = request.form['number']
    splicing_number = request.form['splicingNumber']
    bom_material_type_number = request.form['bomMaterialTypeNumber']
    passport_user_msg = {"phone": phone, "name": name, "pwd": password}
    smt_order_msg = {"application_sphere": application_sphere, "is_pcb_soft_board": is_pcb_soft_board,
                     "single_or_double_technique": single_or_double_technique, "pcb_ban_width": pcb_ban_width,
                     "pcb_ban_height": pcb_ban_height, "number": number, "splicing_number": splicing_number,
                     "bom_material_type_number": bom_material_type_number, "bom_sn": '', "pcb_sn": '',
                     "pcb_bind_type": '1', "bom_bind_type": '1', "pcbaInvoiceNeed": "不需要"}
    user_msg = {'PassPort': passport_user_msg}
    order_params = {"HQCHIP_SMT": smt_order_msg}
    smt_order_list = []
    rss = SSO_Reception('https://uat-smt.hqchip.com').login()
    write_yaml(account_yaml, order_params)
    write_yaml(account_yaml, user_msg)
    for i in range(int(frequency)):
        if pcb_ban_width == '' or pcb_ban_height == '' or number == '' or splicing_number == '':
            return jsonify({"message": "必填数据未填写，请核对填写值", "msgcode": 403})
        else:
            #
            if 1.00 <= float("{:.2f}".format(float(pcb_ban_width))) <= 51.00 or 1.00 <= float("{:.2f}".format(float(pcb_ban_height))) <= 46.00:
                smt_order = SmtOrder(rss).smt_tmp_save().place_an_order()
                if smt_order != None:
                    smt_order_list.append(smt_order)
            else:
                return jsonify({"message": "SMT订单生成失败，尺寸不能小于1cm，且长边不能大于51cm，短边不能大于46cm，请重新输入", "smt_order_list": smt_order_list,
                                "argument": smt_order_msg,
                                "msgcode": 403})
    if smt_order_list != []:
        return jsonify({"message": "成功生成SMT订单", "smt_order_list": smt_order_list,
                        "argument": smt_order_msg,
                        "msgcode": 200})
    else:
        return jsonify({"message": "SMT订单生成失败，请检查入参数据", "smt_order_list": smt_order_list,
                        "argument": smt_order_msg,
                        "msgcode": 200})
@app.route('/pcbaOrder', methods=['POST'])
def pcbaOrder():
    """pcba下单"""
    frequency = request.form['frequency']
    pcbaInvoiceNeed = request.form['pcbaInvoiceNeed']
    phone = request.form['phone']
    name = request.form['name']
    password = request.form['password']
    application_sphere = request.form['applicationSphere']
    is_pcb_soft_board = request.form['isPcbSoftBoard']
    single_or_double_technique = request.form['singleOrDoubleTechnique']
    pcb_ban_width = request.form['width']
    pcb_ban_height = request.form['height']
    number = request.form['number']
    splicing_number = request.form['splicingNumber']
    bom_material_type_number = request.form['bomMaterialTypeNumber']
    pcb_bind_type = request.form['PCBBindType']
    pcb_bind_vaule = request.form['PCBBindVaule']
    bom_bind_type = request.form['BOMBindType']
    bom_bind_vaule = request.form['BOMBindVaule']
    passport_user_msg = {"phone": phone, "name": name, "pwd": password}
    smt_order_msg = {"application_sphere": application_sphere, "is_pcb_soft_board": is_pcb_soft_board,
                     "single_or_double_technique": single_or_double_technique, "pcb_ban_width": pcb_ban_width,
                     "pcb_ban_height": pcb_ban_height, "number": number, "splicing_number": splicing_number,
                     "bom_material_type_number": bom_material_type_number, "bom_sn": bom_bind_vaule, "pcb_sn": pcb_bind_vaule,
                     "pcb_bind_type": pcb_bind_type, "bom_bind_type": bom_bind_type, "pcbaInvoiceNeed": pcbaInvoiceNeed}
    user_msg = {'PassPort': passport_user_msg}
    order_params = {"HQCHIP_SMT": smt_order_msg}
    smt_order_list = []
    bom_order_list = []
    pcb_order_list = []
    write_yaml(account_yaml, user_msg)
    rss = SSO_Reception('https://uat-smt.hqchip.com').login()
    write_yaml(account_yaml, order_params)
    for i in range(int(frequency)):
        if pcb_ban_width == '' or pcb_ban_height == '' or number == '' or splicing_number == '':
            return jsonify({"message": "必填数据未填写，请核对填写值", "msgcode": 403})
        elif pcb_bind_type == '0' and pcb_bind_vaule == '':
            return jsonify({"message": "PCB绑定类型为已在华秋下单时，已在华秋绑定订单号不能为空", "msgcode": 403})
        elif bom_bind_type == '0' and bom_bind_vaule == '':
            return jsonify({"message": "bom绑定类型为已在华秋下单时，已在华秋绑定订单号不能为空", "msgcode": 403})
        else:
            #
            if 1.00 <= float("{:.2f}".format(float(pcb_ban_width))) <= 51.00 or 1.00 <= float("{:.2f}".format(float(pcb_ban_height))) <= 46.00:
                smt_order_sn, bom_order_sn = SmtOrder(rss).smt_tmp_save().place_an_order()
                pcborderId = None
                if pcb_bind_type == '2':
                    smt_order_id = getattr(Data, 'smt_order_id', None)
                    pcborderId = PCBOrder(rss, smt_order_id).pcb_tmp_save().place_an_order()
                else:
                    pass
                if smt_order_sn != None:
                    smt_order_list.append(smt_order_sn)
                    bom_order_list.append(bom_order_sn)
                    pcb_order_list.append(pcborderId)
            else:
                return jsonify({"message": "SMT订单生成失败，尺寸不能小于1cm，且长边不能大于51cm，短边不能大于46cm，请重新输入",
                                "orders": {"smt_order_list": smt_order_list, "bom_order_list": bom_order_list, "pcb_order_list": pcb_order_list},
                                "argument": smt_order_msg,
                                "msgcode": 403})
    if smt_order_list != []:
        return jsonify({"message": "成功生成PCBA订单包",
                        "orders": {"smt_order_list": smt_order_list, "bom_order_list": bom_order_list, "pcb_order_list": pcb_order_list},
                        "argument": smt_order_msg,
                        "msgcode": 200})
    else:
        return jsonify({"message": "SMT订单生成失败，请检查入参数据",
                        "orders": {"smt_order_list": smt_order_list, "bom_order_list": bom_order_list, "pcb_order_list": pcb_order_list},
                        "argument": smt_order_msg,
                        "msgcode": 200})


@app.route('/wmsOut', methods=['POST'])
def wmsOut():
    """wms出库操作"""
    out_order = request.form['Outorder']
    invoiceNo = request.form['invoiceNo']
    smt_order = request.form['smtOrderSn']
    out_number = request.form['number']
    execution_type = request.form['ExecutionType']
    out_warehouse = request.form['warehouse']
    logger.info(out_warehouse)
    execution_type_name_json = {"all": "出库", "pick_completed": "拣货", "pack_completed": "打包", "alone_out": "单独出库（打包后再次启动出库）"}
    if out_order == '' and invoiceNo == '' and smt_order == '':
        # logger.info("传入出库单号为空，不执行WMS出库操作")
        return jsonify({"message": "传入出库单号、WMS预出库单、SMT委外单号同时为空，不执行WMS出库操作", "msgcode": 200})
    else:
        # 将生成的IC出库单号往Data里面作虚拟存储以【out_order】命名以便后续提取
        logger.info(f"传入出库单号为{out_order}，执行WMS出库操作")
        setattr(Data, 'out_order', out_order)
        setattr(Data, 'invoiceNo', invoiceNo)
        setattr(Data, 'smt_order', smt_order)
        ic_order_params = {'goods_id': '', "number": out_number, "warehouse_id": out_warehouse, "vat_type": "0", "vat_sub_type": "3"}
        order_params = {"HQCHIP_GOODS": ic_order_params}
        write_yaml(account_yaml, order_params)
        execution_type_name = ''
        for i in execution_type_name_json:
            if execution_type == i:
                execution_type_name = execution_type_name_json[i]
                break
            else:
                execution_type_name = '出库'
        try:
            target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
            WmsOutWarehouse(target_rss).wms_pick()
            if execution_type == "all":
                # 出库所有步骤
                pda_rss = PdaLogin().pda_login()
                PdaPick(pda_rss).pda_pick()   # 预出库单  商品标签
                WmsOutWarehouse(target_rss).wms_pack()
            elif execution_type == "pick_completed":
                # 拣货完成
                pda_rss = PdaLogin().pda_login()
                PdaPick(pda_rss).pda_pick()   # 预出库单  商品标签
            elif execution_type == "pack_completed":
                #打包完成
                pda_rss = PdaLogin().pda_login()
                PdaPick(pda_rss).pda_pick()   # 预出库单  商品标签
                WmsOutWarehouse(target_rss).wms_pack(is_out="NoOUT")
            elif execution_type == "alone_out":
                #打包完成后，单独出库
                WmsOutWarehouse(target_rss).wms_pack(is_pack=None, is_out=None)
            DingTalkHandle(
                project_name='wms出库操作(仅出库)',
                prams={"out_order": out_order},
                msg_data={"message": {"out_order": out_order, "sourcebillnumber": invoiceNo, "smtOrderSn": smt_order}, "msgStr": f"输入出库单号已{execution_type_name}请等待数据同步", "msgcode": 200}
            ).send_message()
            return jsonify({"message": {"out_order": out_order, "sourcebillnumber": invoiceNo, "smtOrderSn": smt_order}, "msgStr": f"输入出库单号已{execution_type_name}请等待数据同步", "msgcode": 200})
        except ValueError:
            DingTalkHandle(
                project_name='wms出库操作(仅出库)',
                prams={"out_order": out_order},
                msg_data={"message": {"out_order": out_order, "sourcebillnumber": invoiceNo, "smtOrderSn": smt_order, "msgStr": f"输入出库单号不存在或者不满足出库步骤：{execution_type_name}要求，请检查出库单号"}, "msgcode": 403}
            ).send_message()
            return jsonify({"message": {"out_order": out_order, "sourcebillnumber": invoiceNo, "smtOrderSn": smt_order, "msgStr": f"输入出库单号不存在或者不满足出库步骤：{execution_type_name}要求，请检查出库单号"}, "msgcode": 403})

@app.route('/wmsInn', methods=['POST'])
def wmsInn():
    """wms入库（含上架）"""
    inn_order = request.form['Innorder']
    inn_number = request.form['number']
    inn_warehouse = request.form['warehouse']
    if inn_order == '':
        logger.info("传入入库单号为空，不执行WMS入库操作")
        return jsonify({"message": "传入入库单号为空，不执行WMS入库操作", "msgcode": 200})
    else:
        # 将生成的IC出库单号往Data里面作虚拟存储以【out_order】命名以便后续提取
        logger.info(f"传入入库单号为{inn_order}，执行WMS入库操作")
        setattr(Data, 'inn_sn', inn_order)
        ic_order_params = {'goods_id': '', "number": inn_number, "warehouse_id": inn_warehouse, "vat_type": "0"}
        inn_params = {"HQCHIP_GOODS": ic_order_params}
        write_yaml(account_yaml, inn_params)
        try:
            target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
            WmsInWarehouse(target_rss).wms_warehousing().wms_theupper_list(theupper_sn='', status='')
            pda_rss = PdaLogin().pda_login()
            PdaTheupper(pda_rss).pda_theupper()
            DingTalkHandle(
                project_name='wms入库（含上架）',
                prams={"inn_sn": inn_order},
                msg_data={"message": {"inn_sn": inn_order}, "msgStr": "输入入库单号已入库请等待数据同步", "msgcode": 200}
            ).send_message()
            return jsonify({"message": {"inn_sn": inn_order}, "msgStr": "输入入库单号已入库请等待数据同步", "msgcode": 200})
        except ValueError:
            DingTalkHandle(
                project_name='wms入库（含上架）',
                prams={"inn_sn": inn_order},
                msg_data={"message": {"inn_sn": inn_order}, "msgStr": "输入入库单号已入库请等待数据同步", "msgcode": 200}
            ).send_message(at_mobiles=["15070739124"])
            return jsonify({"message": {"inn_sn": inn_order, "msgStr": "输入入库单号不存在或者不满足入库要求，请检查入库单号"}, "msgcode": 403})
@app.route('/wmsTheupper', methods=['POST'])
def wmsTheupper():
    """wms上架操作"""
    vibe_type = request.form['Executvibe']
    inn_order = request.form['Innsn']
    theupper_sn = request.form['theuppersn']
    ASN_sn = request.form['ASNtheuppersn']
    theupper_type = request.form['Inntheuppertype']
    product_label = request.form['ProductLabel']
    theupper_warehouse = request.form['warehouse']
    tag_day = request.form['TagDay']
    label_create_number = request.form['LabelCreateNumber']
    if vibe_type == "UAT":
        target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
        if inn_order == '' and theupper_sn == '' and ASN_sn == '' and theupper_type == "0":
            logger.info("传入入库单号和上架单号为空，执行WMS批量上架操作")
            ic_order_params = {'goods_id': '', "number": '', "warehouse_id": theupper_warehouse, "vat_type": "0"}
            print(ic_order_params)
            setattr(Data, 'inn_sn', inn_order)
            inn_params = {"HQCHIP_GOODS": ic_order_params}
            write_yaml(account_yaml, inn_params)
            try:
                WmsInWarehouse(target_rss).wms_theupper_list(ASN_sn, theupper_sn, 1)
            except ValueError:
                WmsInWarehouse(target_rss).wms_theupper_list(ASN_sn, theupper_sn, 4)
            pda_rss = PdaLogin().pda_login()
            PdaTheupper(pda_rss).pda_theupper()
            DingTalkHandle(
                project_name='wms上架操作(FAT上架在外网)',
                prams={
                    "vibe_type": vibe_type + "环境",
                    "inn_sn": inn_order,
                    "code": theupper_sn,
                    "asn_order": ASN_sn,
                    "theupper_type": theupper_type,
                    "theupper_warehouse": theupper_warehouse},
                msg_data={"message": "上架列表待上架的上架单号均以上架，等待数据同步稍后核对",
                            "argument": {"vibe_type": vibe_type + "环境", "inn_sn": inn_order, "code": theupper_sn, "asn_order": ASN_sn, "theupper_type": theupper_type, "theupper_warehouse":theupper_warehouse},
                            "msgcode": 200}
            ).send_message()
            return jsonify({"message": "上架列表待上架的上架单号均以上架，等待数据同步稍后核对",
                            "argument": {"vibe_type": vibe_type + "环境", "inn_sn": inn_order, "code": theupper_sn, "asn_order": ASN_sn, "theupper_type": theupper_type, "theupper_warehouse":theupper_warehouse},
                            "msgcode": 200})
        else:
            # 将生成的IC出库单号往Data里面作虚拟存储以【out_order】命名以便后续提取
            logger.info(f"传入入库单号为{inn_order}，执行WMS入库操作")
            setattr(Data, 'inn_sn', inn_order)
            ic_order_params = {'goods_id': '', "number": '', "warehouse_id": theupper_warehouse, "vat_type": "0"}
            inn_params = {"HQCHIP_GOODS": ic_order_params}
            write_yaml(account_yaml, inn_params)
            try:
                WmsInWarehouse(target_rss).wms_theupper_list(ASN_sn, theupper_sn, 1)
                pda_rss = PdaLogin().pda_login()
                msg = PdaTheupper(pda_rss).pda_theupper()
                if msg == None:
                    DingTalkHandle(
                        project_name='wms上架操作(FAT上架在外网)',
                        prams={
                            "vibe_type": vibe_type + "环境",
                            "inn_sn": inn_order,
                            "code": theupper_sn,
                            "asn_order": ASN_sn,
                            "theupper_type": theupper_type,
                            "theupper_warehouse": theupper_warehouse},
                        msg_data={"message": "上架列表待上架的上架单号均以上架，等待数据同步稍后核对",
                                  "argument": {"vibe_type": vibe_type + "环境", "inn_sn": inn_order,
                                               "code": theupper_sn, "asn_order": ASN_sn, "theupper_type": theupper_type,
                                               "theupper_warehouse": theupper_warehouse},
                                  "msgcode": 200}
                    ).send_message()
                    return jsonify({"message": "输入相关单号均已上架，等待数据同步稍后核对",
                                    "argument": {"vibe_type": vibe_type + "环境", "inn_sn": inn_order, "code": theupper_sn, "asn_order": ASN_sn, "theupper_type": theupper_type, "theupper_warehouse":theupper_warehouse},
                                    "msgcode": 200})
                else:
                    DingTalkHandle(
                        project_name='wms上架操作(FAT上架在外网)',
                        prams={
                            "vibe_type": vibe_type + "环境",
                            "inn_sn": inn_order,
                            "code": theupper_sn,
                            "asn_order": ASN_sn,
                            "theupper_type": theupper_type,
                            "theupper_warehouse": theupper_warehouse},
                        msg_data={"message": msg,
                                  "argument": {"vibe_type": vibe_type + "环境", "inn_sn": inn_order,
                                               "code": theupper_sn, "asn_order": ASN_sn, "theupper_type": theupper_type,
                                               "theupper_warehouse": theupper_warehouse},
                                  "msgcode": 200}
                    ).send_message()
                    return jsonify({"message": msg,
                                    "argument": {"vibe_type": vibe_type + "环境", "inn_sn": inn_order, "code": theupper_sn, "asn_order": ASN_sn, "theupper_type": theupper_type, "theupper_warehouse":theupper_warehouse},
                                    "msgcode": 200})
            except ValueError:
                try:
                    WmsInWarehouse(target_rss).wms_theupper_list(ASN_sn, theupper_sn, 4)
                    pda_rss = PdaLogin().pda_login()
                    msg = PdaTheupper(pda_rss).pda_theupper()
                    if msg == None:
                        return jsonify({"message": "输入相关单号均已上架，等待数据同步稍后核对",
                                        "argument": {"vibe_type": vibe_type + "环境", "inn_sn": inn_order, "code": theupper_sn, "asn_order": ASN_sn, "theupper_type": theupper_type, "theupper_warehouse":theupper_warehouse},
                                        "msgcode": 200})
                    else:
                        return jsonify({"message": msg,
                                        "argument": {"vibe_type": vibe_type + "环境", "inn_sn": inn_order, "code": theupper_sn, "asn_order": ASN_sn, "theupper_type": theupper_type, "theupper_warehouse":theupper_warehouse},
                                        "msgcode": 200})
                except ValueError:
                    return jsonify({"message": "输入入库单号或者上架单号或者ASN订单号不存在或者不满足入库要求，请检查相关单号",
                                "argument": {"vibe_type": vibe_type + "环境", "inn_sn": inn_order, "code": theupper_sn, "asn_order": ASN_sn, "theupper_type": theupper_type, "theupper_warehouse":theupper_warehouse},
                                "msgcode": 403})
    else:
        if theupper_type == "0":
            logger.info("传入入库单号和上架单号为空，执行WMS批量上架操作")
            return jsonify({"message": "执行环境为FAT时，工具不支持批量上架，请重新核对执行环境，确保达到系统应满足工具要求",
                            "argument": {"vibe_type": vibe_type + "环境", "inn_sn": inn_order, "code": theupper_sn,
                                         "asn_order": ASN_sn, "theupper_type": theupper_type,
                                         "theupper_warehouse": theupper_warehouse},
                            "msgcode": 403})
        else:
            ic_order_params = {'goods_id': '', "number": '', "warehouse_id": theupper_warehouse, "vat_type": "0"}
            inn_params = {"HQCHIP_GOODS": ic_order_params}
            print(ic_order_params)
            write_yaml(account_yaml, inn_params)
            pda_rss = FATPdaLogin().pda_login()
            if product_label != '':
                if "," in product_label:
                    product_label_list = product_label.split(",")
                    setattr(Data, "labelNumber_sn", product_label_list)
                    msg = FATPdaTheupper(pda_rss).pda_theupper()
                    if msg == None:
                        return jsonify({"message": "输入相关单号均已上架，等待数据同步稍后核对",
                                        "argument": {"vibe_type": vibe_type + "环境",
                                                     "inn_sn": inn_order,
                                                     "code": theupper_sn,
                                                     "asn_order": ASN_sn,
                                                     "theupper_type": theupper_type,
                                                     "labelNumber_sn": product_label_list,
                                                     "theupper_warehouse": theupper_warehouse},
                                        "msgcode": 200})
                    else:
                        return jsonify({"message": msg,
                                        "argument": {"vibe_type": vibe_type + "环境",
                                                     "inn_sn": inn_order,
                                                     "code": theupper_sn,
                                                     "asn_order": ASN_sn,
                                                     "theupper_type": theupper_type,
                                                     "labelNumber_sn": product_label_list,
                                                     "theupper_warehouse": theupper_warehouse},
                                        "msgcode": 200})

                elif re.compile(r'[@_!#$%^&*()<>?/\|}{~:，。、]').search(product_label) is None:
                    product_label_list = [product_label]
                    setattr(Data, "labelNumber_sn", product_label_list)
                    msg = FATPdaTheupper(pda_rss).pda_theupper()
                    if msg == None:
                        return jsonify({"message": "输入相关单号均已上架，等待数据同步稍后核对",
                                        "argument": {"vibe_type": vibe_type + "环境",
                                                     "inn_sn": inn_order,
                                                     "code": theupper_sn,
                                                     "asn_order": ASN_sn,
                                                     "theupper_type": theupper_type,
                                                     "labelNumber_sn": product_label_list,
                                                     "theupper_warehouse": theupper_warehouse},
                                        "msgcode": 200})
                    else:
                        return jsonify({"message": msg,
                                        "argument": {"vibe_type": vibe_type + "环境",
                                                     "inn_sn": inn_order,
                                                     "code": theupper_sn,
                                                     "asn_order": ASN_sn,
                                                     "theupper_type": theupper_type,
                                                     "labelNumber_sn": product_label_list,
                                                     "theupper_warehouse": theupper_warehouse},
                                        "msgcode": 200})

                else:
                    return jsonify({"message": "商品标签不正确，无法进行PDA上架操作，请核对商品标签",
                                    "argument": {"vibe_type": vibe_type + "环境",
                                                 "inn_sn": inn_order,
                                                 "code": theupper_sn,
                                                 "asn_order": ASN_sn,
                                                 "theupper_type": theupper_type,
                                                 "labelNumber_sn": product_label,
                                                 "theupper_warehouse": theupper_warehouse},
                                    "msgcode": 200})
            elif tag_day != '':
                if re.match(r'^\d{4}-\d{2}-\d{2}$', tag_day):
                    year, month, day = tag_day.split('-')
                    year_short = year[2:]
                    new_format = year_short + month + day
                    new = []
                    product_label_pass_list = []
                    product_label_error_list = []
                    for i in range(int(label_create_number)):
                        new.append("{:06d}".format(1 + i))
                    for m in new:
                        product_label_new = "LL" + new_format + m
                        product_label_new_list = product_label_new.split(",")
                        setattr(Data, "labelNumber_sn", product_label_new_list)
                        msg = FATPdaTheupper(pda_rss).pda_theupper()

                        if msg == None:
                            product_label_pass_list.append(product_label_new)
                        else:
                            product_label_error_list.append(product_label_new)
                    if product_label_error_list == []:
                        return jsonify(
                            {"message": f"基于日期：{tag_day}生成的商品标签已存在且已上架，等待数据同步稍后核对",
                             "argument": {"vibe_type": vibe_type + "环境",
                                          "inn_sn": inn_order,
                                          "code": theupper_sn,
                                          "asn_order": ASN_sn,
                                          "theupper_type": theupper_type,
                                          "labelNumber_sn": product_label_pass_list,
                                          "theupper_warehouse": theupper_warehouse},
                             "msgcode": 200})
                    else:
                        return jsonify({"message": f"基于日期：{tag_day}生成的商品标签不存在或异常，请核对",
                                        "argument": {"vibe_type": vibe_type + "环境",
                                                     "inn_sn": inn_order,
                                                     "code": theupper_sn,
                                                     "asn_order": ASN_sn,
                                                     "theupper_type": theupper_type,
                                                     "labelNumber_sn_pass": product_label_pass_list,
                                                     "labelNumber_sn_error": product_label_error_list,
                                                     "theupper_warehouse": theupper_warehouse},
                                        "msgcode": 200})
                else:
                    return jsonify({"message": f"输入日期：{tag_day}格式不符合工具入参，请核对",
                                    "argument": {"vibe_type": vibe_type + "环境",
                                                 "inn_sn": inn_order,
                                                 "code": theupper_sn,
                                                 "asn_order": ASN_sn,
                                                 "theupper_type": theupper_type,
                                                 "tag_day": tag_day,
                                                 "theupper_warehouse": theupper_warehouse},
                                    "msgcode": 200})
            else:
                return jsonify({"message": "商品标签或入库日期不能为空，请输入商品标签或入库日期",
                                "argument": {"vibe_type": vibe_type + "环境",
                                             "inn_sn": inn_order,
                                             "code": theupper_sn,
                                             "asn_order": ASN_sn,
                                             "theupper_type": theupper_type,
                                             "labelNumber_sn": product_label,
                                             "theupper_warehouse": theupper_warehouse},
                                "msgcode": 200})
@app.route('/wmsInventory', methods=['POST'])
def wmsInventory():
    """wms盘点操作"""
    vibe_type = request.form['Executvibe']
    inventory_no = request.form['InventoryNo']
    transform_no = request.form['transformNo']
    inventory_status = request.form['InventoryStatus']
    inventory_type = request.form['Inventorytype']
    product_label = request.form['ProductLabel']
    inventory_warehouse = request.form['warehouse']
    tag_day = request.form['TagDay']
    # setattr(Data, 'inventory_no', inventory_no)
    setattr(Data, 'transform_no', transform_no)
    setattr(Data, 'inventory_status', inventory_status)
    if vibe_type == "UAT":
        target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
        if inventory_no == '' and transform_no == '' and inventory_type == "0":
            logger.info("传入盘点单号和转换单号为空，执行WMS批量盘点操作")
            ic_order_params = {'goods_id': '', "number": '', "warehouse_id": inventory_warehouse, "vat_type": "0"}
            goods_params = {"HQCHIP_SOO": ic_order_params}
            write_yaml(account_yaml, goods_params)
            inventory_no_list = WmsInventory(target_rss).wms_inventory()
            if inventory_no_list != []:
                for i in range(len(inventory_no_list)):
                    inventory_no = inventory_no_list[i]
                    setattr(Data, 'inventory_no', inventory_no)
                    pda_rss = PdaLogin().pda_login()
                    PdaInventory(pda_rss).pda_inventory()
                    WmsInventory(target_rss).wms_inventory_confirm_audit()
                    return jsonify({"message": "盘点列表待盘点的盘点单号均以盘点完成，等待数据同步稍后核对",
                                    "argument": {"vibe_type": vibe_type + "环境", "inventory_no": inventory_no_list,
                                                 "code": transform_no, "product_label": product_label,
                                                 "inventory_type": inventory_type,
                                                 "inventory_warehouse": inventory_warehouse},
                                    "msgcode": 200})
            else:
                return jsonify({"message": "盘点列表已无待盘点的盘点单，等待数据同步稍后核对", "msgcode": 200})
        elif tag_day != '':
            pda_rss = PdaLogin().pda_login()
            if re.match(r'^\d{4}-\d{2}-\d{2}$', tag_day):
                year, month, day = tag_day.split('-')
                year_short = year[2:]
                new_format = year_short + month + day
                new = []
                inventory_no_pass_list = []
                inventory_no_error_list = []
                for i in range(50):
                    new.append("{:06d}".format(1 + i))
                for m in new:
                    inventory_no_new = "PD" + new_format + m
                    inventory_no_new_list = inventory_no_new.split(",")
                    for n in inventory_no_new_list:
                        setattr(Data, "inventory_no", n)
                        msg = PdaInventory(pda_rss).pda_inventory()


                        if msg == None:
                            inventory_no_pass_list.append(inventory_no_new)
                        else:
                            inventory_no_error_list.append(inventory_no_new)
                WmsInventory(target_rss).wms_inventory_confirm_audit()
                if inventory_no_error_list == []:
                    return jsonify(
                        {"message": f"基于日期：{tag_day}生成的盘点单号已存在且已盘点，等待数据同步稍后核对",
                         "argument": {"vibe_type": vibe_type + "环境",
                                      "inventory_no": inventory_no,
                                      "code": transform_no,
                                      "inventory_type": inventory_type,
                                      "product_label": product_label,
                                      "inventory_warehouse": inventory_warehouse,
                                      "inventory_no_pass": inventory_no_pass_list,},
                         "msgcode": 200})
                else:
                    return jsonify({"message": f"基于日期：{tag_day}生成的商品标签不存在或异常，请核对",
                                    "argument": {"vibe_type": vibe_type + "环境",
                                                 "inventory_no": inventory_no,
                                                 "code": transform_no,
                                                 "inventory_type": inventory_type,
                                                 "inventory_no_pass": inventory_no_pass_list,
                                                 "inventory_no_error": inventory_no_error_list,
                                                 "inventory_warehouse": inventory_warehouse},
                                    "msgcode": 200})
        elif re.compile(r'[@_!#$%^&*()<>?/\|}{~:，。、]').search(product_label) is None:
            product_label_list = [product_label]
            for a in product_label_list:
                setattr(Data, "labelNumber_sn", a)
                ic_order_params = {'goods_id': '', "number": '', "warehouse_id": inventory_warehouse, "vat_type": "0"}
                goods_params = {"HQCHIP_GOODS": ic_order_params}
                write_yaml(account_yaml, goods_params)
                inventory_no_list = WmsInventory(target_rss).wms_inventory()
                if inventory_no_list != []:
                    for i in range(len(inventory_no_list)):
                        inventory_no = inventory_no_list[i]
                        setattr(Data, 'inventory_no', inventory_no)
                        pda_rss = PdaLogin().pda_login()
                        PdaInventory(pda_rss).pda_inventory()
                        WmsInventory(target_rss).wms_inventory_confirm_audit()
                        return jsonify({"message": "盘点列表待盘点的盘点单号均以盘点完成，等待数据同步稍后核对",
                                        "argument": {"vibe_type": vibe_type + "环境", "inventory_no": inventory_no_list,
                                                     "code": transform_no, "product_label": product_label,
                                                     "inventory_type": inventory_type,
                                                     "inventory_warehouse": inventory_warehouse},
                                        "msgcode": 200})
                else:
                    return jsonify({"message": "盘点列表已无待盘点的盘点单，等待数据同步稍后核对", "msgcode": 200})
        else:
            setattr(Data, 'inventory_no', inventory_no)
            pda_rss = PdaLogin().pda_login()
            PdaInventory(pda_rss).pda_inventory()
            WmsInventory(target_rss).wms_inventory_confirm_audit()
            return jsonify({"message": "盘点列表待盘点的盘点单号均以盘点完成，等待数据同步稍后核对",
                            "argument": {"vibe_type": vibe_type + "环境", "inventory_no": inventory_no,
                                         "code": transform_no, "product_label": product_label,
                                         "inventory_type": inventory_type,
                                         "inventory_warehouse": inventory_warehouse},
                            "msgcode": 200})

@app.route('/hotSearchCache')
def hotSearchcache():
    """替代料专题页热词缓存清空"""
    hot_word_external_res = HotSearchWord().hot_word_external()
    if hot_word_external_res != 404:
        return jsonify({"message": {"result": hot_word_external_res}, "msgCode": 200})
    else:
        return jsonify({"message": "接口异常，检查营销中台数据", "msgCode": 404})
@app.route('/Search/filtrstionRule')
def filtrstion_rule_verify():
    """搜索替换规则配置验证"""
    keyword = request.args.get('keyword', default=1, type=str)
    version = request.args.get('version', default=1, type=str)
    participlelist = SearchToolKit(keyword).mian_search_goods_log_push(version)
    dos_rss = Login().login()
    auth_token = getattr(Data, "dos_auth_token")
    test_participlelist = SearchFiltrstionRule(keyword).str_list_remove_blank().hc2018_search_filtration_new(dos_rss, auth_token)
    result = set(sorted(participlelist)) == set(sorted(test_participlelist))
    es_search_sql = EsSearchSQL(keyword, version).es_search_sql_form()
    if result == True :
        return jsonify({"message": {"result": {"participlelist": sorted(participlelist), "test_participlelist": sorted(test_participlelist),
                                               "contrast":  True}, "es_sql": es_search_sql}, "msgCode": 200})
    else:
        return jsonify({"message": {"result": {"participlelist": sorted(participlelist), "test_participlelist": sorted(test_participlelist),
                                                "contrast": False}, "es_sql": es_search_sql}, "msgCode": 200})
@app.route('/Search/keywordparticiple')
def keyword_participle():
    """搜索分词验证"""
    keyword = request.args.get('keyword', default=1, type=str)
    version = request.args.get('version', default=1, type=str)
    participlelist = SearchToolKit(keyword).mian_search_goods_log_push(version)
    es_search_sql = EsSearchSQL(keyword, version).es_search_sql_form()
    if participlelist != []:
        return jsonify({"message": {
            "result": {"participlelist": sorted(participlelist), "contrast": True}, "es_sql": es_search_sql}, "msgCode": 200})
    else:
        return jsonify({"message": {
            "result": {"participlelist": sorted(participlelist), "contrast": True}, "es_sql": es_search_sql},
            "msgCode": 200})

@app.route('/supplier/mide')
def supplie_sync():
    """第三方接口库存同步"""
    keyword = request.args.get('keyword', default=1, type=str)
    goods_id = MiDeSearch(keyword).mide_search_api().supplier_huaqiu_sync().hc2016_login().hc2016_cooperative_inventory()
    if goods_id != None:
        msgGoodsId = f"获取到到最后一个同步生成的goodsId：{goods_id}"
        return jsonify({"message": {"result": {"msgStr": "同步成功", "goodsId": msgGoodsId}}, "msgCode": 200})
    else:
        return jsonify({"message": "同步失败:请联系开发或者测试", "msgCode": 404})
@app.route('/hqSrm/goodsIdSyncInterface')
def supplie_goodsId_update_sync():
    """合作库存一键导入更新---接口层面"""
    supplier_name = request.args.get('supplier_name', default=1, type=str)
    goods_name = request.args.get('goods_name', default=1, type=str)
    provider_name = request.args.get('provider_name', default=1, type=str)
    encap = request.args.get('encap', default=1, type=str)
    target_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
    suc, bill_sn = SettleGoods(target_rss, supplier_name, goods_name, provider_name, encap).excel_file_write().settle_goods_file().settle_search_excel().parther_audit_list()
    if suc != None:
        msgcode = f"生成导入单号为：{bill_sn}"
        return jsonify({"message": {"result": {"msgStr": "上传更新成功", "msgCode": 200, "msgcode": msgcode,
                                               "goodsIdInfo": {"supplier_name": supplier_name,
                                                               "goods_name": goods_name,
                                                               "provider_name": provider_name,
                                                               "encap": encap
                                                               }}}})
    else:
        return jsonify({"message": "上传更新失败", "msgCode": 404})

@app.route('/hqSrm/goodsIdSyncPage', methods=['POST'])
def supplie_update_sync():
    """合作库存一键导入更新-页面层面"""

    supplier_name = request.form['supplierName']
    goods_name = request.form['goodsName']
    provider_name = request.form['providerName']
    encap = request.form['encap']
    min_pack = request.form['minPage']
    MOQ=  request.form['MOQ']
    min_step_price = request.form['MinStepPrice']
    inland_delivery_day = request.form['InlandDeliveryDay']
    CNY_domestic_stock = request.form['CNYDomesticStock']
    OverView = request.form['OverView']
    if supplier_name == '' and provider_name == '' and encap == '' and goods_name == "":
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        if OverView == '' or OverView == '0':
            OverView = None
        if min_pack == '' or min_pack == '0':
            min_pack = None
        else:
            if MOQ == '' or MOQ == '0':
                MOQ = None
            else:
                if min_step_price == '' or min_step_price == '0':
                    min_step_price = None
                else:
                    if inland_delivery_day == '' or inland_delivery_day == '0':
                        inland_delivery_day = None
                    if '-' in inland_delivery_day:
                        inland_delivery_day = inland_delivery_day
                    else:
                        # 检查一个字符串inland_delivery_day是否以数字开头和结尾。如果满足条件，返回True，否则返回False。
                        if re.search(r'\d', inland_delivery_day) and re.match(r'\d', inland_delivery_day)  and re.search(r'\d$', inland_delivery_day):
                            inland_delivery_day = re.sub(r'\D+', '-', inland_delivery_day)
                        else:
                            inland_delivery_day = None
        target_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
        suc, bill_sn = SettleGoods(target_rss,
                                   supplier_name=supplier_name,
                                   goods_name=goods_name,
                                   provider_name=provider_name,
                                   encap=encap,
                                   Overview=OverView,
                                   min_pack=min_pack,
                                   MOQ=MOQ,
                                   min_step_price=min_step_price,
                                   inland_delivery_day=inland_delivery_day,
                                   CNY_domestic_stock=CNY_domestic_stock
                 ).excel_file_write().settle_goods_file().settle_search_excel().settle_goods_audit()
        if suc != None:
            msgcode = f"生成导入单号为：{bill_sn}"
            return jsonify({"message": {"result": {"msgStr": "上传更新成功", "msgCode": 200, "msgcode": msgcode,
                                                   "goodsIdInfo": {"supplier_name": supplier_name,
                                                                   "goods_name": goods_name,
                                                                   "provider_name": provider_name,
                                                                   "encap": encap
                                                                   }}}})
        else:
            return jsonify({"message": "上传更新失败", "msgCode": 404})
@app.route('/hqSrm/goodsIdSyncBatchPage', methods=['POST'])
def supplie_update_sync_batch():
    """合作库存一键导入更新-页面层面--批量"""
    cooperationType = request.form['cooperationType']
    goods_name = request.form['goodsName']
    provider_name = request.form['providerName']
    encap = request.form['encap']
    min_pack = request.form['minPage']
    MOQ=  request.form['MOQ']
    min_step_price = request.form['MinStepPrice']
    inland_delivery_day = request.form['InlandDeliveryDay']
    CNY_domestic_stock = request.form['CNYDomesticStock']
    if provider_name == '' and encap == '' and goods_name == "":
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        if min_pack == '' or min_pack == '0':
            min_pack = None
        else:
            if MOQ == '' or MOQ == '0':
                MOQ = None
            else:
                if min_step_price == '' or min_step_price == '0':
                    min_step_price = None
                else:
                    if inland_delivery_day == '' or inland_delivery_day == '0':
                        inland_delivery_day = None
                    if '-' in inland_delivery_day:
                        inland_delivery_day = inland_delivery_day
                    else:
                        # 检查一个字符串inland_delivery_day是否以数字开头和结尾。如果满足条件，返回True，否则返回False。
                        if re.search(r'\d', inland_delivery_day) and re.match(r'\d', inland_delivery_day)  and re.search(r'\d$', inland_delivery_day):
                            inland_delivery_day = re.sub(r'\D+', '-', inland_delivery_day)
                        else:
                            inland_delivery_day = None
        target_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
        SettleGoods(target_rss, None, goods_name, provider_name, encap, min_pack,
                                   MOQ, min_step_price, inland_delivery_day, CNY_domestic_stock
                                   ).excel_file_write()

        supplierId, supplier_name, supplier_code, approveStatus = PassPartner(target_rss, cooperationType=cooperationType).pass_partner_list()

        supplier_name_new = []
        supplier_code_new = []
        bill_sn_create = []
        supplier_dictionary = {}
        for i in range(len(supplier_name)):
            if supplier_name[i] not in ("深圳市汇芯微电子有限公司"):
                logger.info(f"此时供应商：{supplier_name[i]}，编码：{supplier_code[i]}")
                suc, bill_sn = SettleGoods(target_rss, supplier_name=supplier_name[
                    i]).settle_goods_file().settle_search_excel().settle_goods_audit()
                bill_sn_create.append(bill_sn)
                supplier_name_new.append(supplier_name[i])
                supplier_code_new.append(supplier_code[i])
        supplier_dictionary = dict(zip(supplier_code_new, zip(supplier_name_new, bill_sn_create)))
        return jsonify({"message": "导入成功", "msgCode": 200, "result": {"supplier_batch": supplier_dictionary}})
@app.route('/hqSrm/partnerCreate', methods=['POST'])
def partnerCreate():
    """供应商创建以及修改"""
    supplier_name = request.form['supplierName']
    supplierBackName = request.form['supplierBackName']
    socialCreditCode = request.form['socialCreditCode']
    companyType = request.form['companyType']
    companyNature = request.form['companyNature']
    intendedType = request.form['intendedType']
    specialDevelopmentType = request.form['specialDevelopmentType']
    phone = request.form['phone']
    Contacts = request.form['Contacts']
    values = request.form.get('myField').split(',')
    supplierSort = [x for x in values if x]
    if supplier_name == '' and supplierBackName == '':
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    elif supplierSort == []:
        return jsonify({"message": "供应商分类必选，请检查", "msgCode": 404})
    else:
        target_rss = SOOLogin("uat-srm.huaqiu.com", "partnermanage").target_login()
        supplierCode = PartnerPotential(target_rss, supplier_name, companyType, companyNature, intendedType, specialDevelopmentType,
                         supplierSort, socialCreditCode, Contacts, phone, supplierBackName).mian_potential_partner_add()
        return jsonify({"message": f"供应商：{supplier_name}创建成", "msgCode": 200,
                            "argument": {
                                "supplierName": supplier_name,
                                "supplierBackName": supplierBackName,
                                "socialCreditCode": socialCreditCode,
                                "companyType": companyType,
                                "companyNature": companyNature,
                                "intendedType": intendedType,
                                "specialDevelopmentType": specialDevelopmentType,
                                "phone": phone,
                                "Contacts": Contacts,
                                "supplierSort": supplierSort,
                                "supplierCode": supplierCode
                            }})

@app.route('/stock/selfstock', methods=['POST'])
def stock_self():
    """自营补货"""
    goods_name = request.form['GoodsName']
    brand_name = request.form['BrandName']
    packer = request.form['Packer']
    packer_number = request.form['PackerNumber']
    stock_number = request.form['stockNumber']
    goods_id = request.form['GoodsId']
    order_sn = request.form['OrderSn']
    warehouse_id = request.form['warehouse']
    stock_type = request.form['stockType']
    target_rss = Login().login()
    if stock_type == "4":
        if order_sn != '' or goods_id != '':
            ic_order_params = {'goods_id': goods_id, "number": '', "warehouse_id": warehouse_id, "vat_type": "0"}
            setattr(Data, 'ic_order_sn', order_sn)
            yaml_params = {"HQCHIP_GOODS": ic_order_params}
            write_yaml(account_yaml, yaml_params)
            logger.info(f"此时自营补货为自营销售补货")
            SelfOrderStockUp(target_rss).mian_self_order_stockup()
        else:
            return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    elif stock_type in ("3", "5"):
        if goods_name == '' or brand_name == '' or packer == '' or packer_number == '' or stock_number == '':
            return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
        else:
            stock_type_name = ''
            warehouse_name = ''
            if stock_type == "3":
                stock_type_name = "常规备货"
            else:
                stock_type_name = "寄售备货"
            if warehouse_id == "2":
                warehouse_name = "深圳华秋东莞仓"
            elif warehouse_id == "8":
                warehouse_name = "长沙华秋仓"
            StockUp(target_rss, goods_name, brand_name, packer, packer_number, stock_number, stock_type_name, warehouse_name).mian_self_file_stockup()
            return jsonify({"message": "导入文件成功", "msgCode": 200})

    else:
        return jsonify({"message": "所选择类型暂不支持，敬请稍后", "msgCode": 201})




@app.route('/stock/supplierstock', methods=['POST'])
def stock_supplier():
    """合作销售补货"""
    goods_name = request.form['GoodsName']
    brand_name = request.form['BrandName']
    goods_id = request.form['stockGoodsId']
    order_sn = request.form['stockOrderSn']
    warehouse_id = request.form['warehouse']
    if order_sn == '':
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        erp_rss = SOOLogin(system_name="erp").target_login()
        setattr(Data, 'ic_order_sn', order_sn)
        # ErpOrderCancellation(erp_rss).erp_ic_order_cancellation()
        ErpOrderStock(erp_rss).need_order_cancellation()
        ErpStockPurchase(erp_rss).mian_order_stock_purchase()
        wms_target_rss = SOOLogin(system_name="wms").target_login()
        WmsInWarehouse(wms_target_rss).wms_warehousing()
        WmsInWarehouse(wms_target_rss).wms_theupper_list('', '', 1)
        pda_rss = PdaLogin().pda_login()
        PdaTheupper(pda_rss).pda_theupper()
        WmsOutWarehouse(wms_target_rss).wms_pick()
        PdaPick(pda_rss).pda_pick()
        WmsOutWarehouse(wms_target_rss).wms_pack()
        return jsonify({"message": "已处理", "msgCode": 200})


@app.route('/stock/daigoustock', methods=['POST'])
def stock_daigou():
    """代购销售补货"""
@app.route('/voucher/voucherPay', methods=['POST'])
def voucherpay_simulate():
    """现金券模拟消费 """
    order_id = request.form['voucherOrderId']
    order_sn = request.form['voucherOrderSn']
    order_type = request.form['voucherOrderType']
    order_amount = request.form['voucherOrderAmount']
    detail_number = request.form['voucherOrderDetailNumber'] if request.form['voucherOrderDetailNumber'] != '' else None
    unionId = request.form['voucherUnionId']
    voucher_id = request.form['voucherOrderUseVoucherId'] if request.form['voucherOrderUseVoucherId'] != '' else None
    if order_amount == '' or unionId == '':
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        voucher_use_body = VoucherReception(order_id, order_sn, order_type, order_amount, detail_number, unionId, voucher_id).voucher_use()
        if "detail" in voucher_use_body:
            return jsonify({"message": "该订单已消费，请勿重复消费", "body": voucher_use_body, "msgCode": 200})
        else:
            return jsonify({"message": "用户：{}没有可用的现金券".format(unionId)})



@app.route('/hqshop', methods=['POST'])
def hqshop():
    """专题创建以及修改"""
    activityName = request.form['activityName']
    thematicName = request.form['SpecialSubjectName']
    activity_id = request.form['activityId']
    shopThemat_id = request.form['SpecialSubjectId']
    appSite = request.form['appSiteType']
    client = request.form['clientType']
    templateId = request.form['templateType']
    topicStatus = request.form['topicStatusType']
    finishedRedirectUrl = request.form['skipUrl']
    values = request.form.get('myField1').split(',')
    module_name_list = [x for x in values if x]
    if templateId == '0' and module_name_list == '':
        return jsonify({"message": "当模板选择为不引用模板时，组件类型必选，请检查", "msgCode": 404})
    else:
        if activity_id == "" and activityName == "":
            return jsonify({"message": "当活动id为空时，专题活动名称不得为空，请检查", "msgCode": 404})
        elif shopThemat_id == "" and thematicName == "":
            return jsonify({"message": "当专题id为空时，专题名称不得为空，请检查", "msgCode": 404})
        else:
            target_rss = SOOLogin("uat-activity.hqchip.com", "ecmc").target_login()
            activity_id, activity_name, thematicName, shopThemat_id = HqshopActivity(target_rss, activityName, activity_id,
                                                                                     thematicName, shopThemat_id).main_hqshop_activity()
            module_name_list = HqshopSubject(target_rss, activity_id, shopThemat_id, thematicName, finishedRedirectUrl,
                 appSite, client, topicStatus, templateId,  module_name_list).mian_hqshop_subject()
            return jsonify({"message": "专题更新成功", "msgCode": 200,
                            "argument": {
                                "activityName": activity_name,
                                "activity_id": activity_id,
                                "thematicName": thematicName,
                                "shopThemat_id": shopThemat_id,
                                "module_name_list": module_name_list,
                                "templateId": templateId,
                                "topicStatus": topicStatus,
                                "finishedRedirectUrl": finishedRedirectUrl,
                                "client": client,
                                "appSite": appSite
                            }})
@app.route('/coupon', methods=['POST'])
def coupon_create():
    """营销中台优惠券创建"""
    couponName = request.form['couponName']
    effectiveType = request.form['effectiveType']
    couponExpireDays = request.form['couponExpireDays']
    useType = request.form['useType']
    couponAmount = request.form['couponAmount']
    couponDiscount = request.form['couponDiscount']
    orderAmountLimit = request.form['orderAmountLimit']
    values = request.form.get('myField').split(',')
    values = [x for x in values if x]
    couponTypeSum= '{}'.format(', '.join(values))
    print(couponTypeSum)
    target_rss = SOOLogin("uat-activity.hqchip.com", "ecmc").target_login()
    if effectiveType == "2":
        logger.info(111)
        if couponExpireDays != "":
            logger.info(112)
            if useType == "2":
                logger.info(113)
                if couponAmount != "":
                    logger.info(114)
                    coupon_id = Coupon(target_rss, couponType=couponTypeSum, coupon_name=couponName).common_add(effectiveType,
                                                                                                    couponExpireDays,
                                                                                                    useType,
                                                                                                    couponAmount,
                                                                                                    couponDiscount,
                                                                                                    orderAmountLimit)
                    if coupon_id !=None:
                        return jsonify({"message": f"优惠券：{couponName} 创建成功，生成的优惠券id为{coupon_id}", "msgCode": 200})
                    else:
                        return jsonify({"message":  f"优惠券：{couponName} 创建失败", "msgCode": 400})
                else:
                    return jsonify({"message": "折扣类型选择满减金额，优惠金额不能为空", "msgCode": 400})
            else:
                logger.info(115)
                if couponDiscount != "":
                    logger.info(116)
                    if float(couponDiscount)<=99.9 and float(couponDiscount) >= 90.0:
                        coupon_id = Coupon(target_rss, couponType=couponTypeSum, coupon_name=couponName).common_add(effectiveType,
                                                                                                         couponExpireDays,
                                                                                                         useType,
                                                                                                         couponAmount,
                                                                                                         couponDiscount,
                                                                                                         orderAmountLimit)
                        if coupon_id != None:
                            return jsonify({"message": f"优惠券：{couponName} 创建成功，生成的优惠券id为{coupon_id}",
                                            "msgCode": 200})
                        else:
                            return jsonify({"message": f"优惠券：{couponName} 创建失败", "msgCode": 400})
                    else:
                        return jsonify({"message": "折扣类型选择折扣率，折扣不能超过99.9且不能低于90.0", "msgCode": 400})
                else:
                    return jsonify({"message": "折扣类型选择折扣率，折扣不能为空", "msgCode": 400})

        else:
            return jsonify({"message": "选择领取后，领取N天不能为空", "msgCode": 400})
    # return jsonify({"message": "已处理", "msgCode": couponTypeSum})
@app.route('/GoodsMeansAdd', methods=['POST'])
def means_create():
    """DOS资料一键创建"""
    goods_name = request.form['AddGoodsName']
    provider_name = request.form['AddProviderName']
    pack_type = request.form['AddPackType']
    spq = request.form['AddPackNumber']
    cat_id_s = request.form['AddCatIds']
    special_type = request.form['AddSpecialType']
    special_attr_value = request.form['AddSpecialAttrValue']
    if provider_name == '' or pack_type == '' or goods_name == "" or spq == '':
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        if int(special_type) == 1 and special_attr_value != '':
            special_type_attr_dict = {"special_type": int(special_type), "attr_value": special_attr_value}
        else:
            if int(special_type) == 1:
                special_type_attr_dict = {"special_type": int(special_type)}
            else:
                special_type_attr_dict = None
        if cat_id_s == '':
            cat_id_s = None
        rss = Login().login()
        goods_id, brand_id, goods_no, erp_goods_sn = GoodsMeans(rss, goods_name, provider_name, pack_type, spq, cat_id_s).mian_means_add(special_type_attr_dict=special_type_attr_dict)
        if goods_id != []:
            return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}创建成功", "msgCode": 200,
                            "argument": {
                                "goods_name": goods_name,
                                "provider_name": provider_name,
                                "pack_type": pack_type,
                                "spq": spq,
                                "cat_id": cat_id_s,
                                "create_goods_id": goods_id[0],
                                "create_brand_id": brand_id}
                            })
        else:
            return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}创建失败，请检查入参", "msgCode": 200,
                            "argument": {
                                "goods_name": goods_name,
                                "provider_name": provider_name,
                                "pack_type": pack_type,
                                "spq": spq,
                                "cat_id": cat_id_s,
                                "create_goods_id": goods_id[0],
                                "create_brand_id": brand_id}
                            })
@app.route('/XLGoodsMeansAdd', methods=['POST'])
def xl_means_create():
    """芯灵资料一键创建"""
    goods_name = request.form['XLAddGoodsName']
    provider_name = request.form['XLAddProviderName']
    cat_name = request.form['XLAddCatName']
    venodr = request.form['XLVenodrId']
    package_value = request.form['XLAddAttrPackageValue']
    if goods_name == '' or provider_name == '' or cat_name == "" or package_value == '':
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        pass
@app.route('/MyZentaoWordHour', methods=['POST'])
def zentao_word_hour():
    ZentaoWordHourDim = request.form['ZentaoWordHourDim']
    date = request.form['date']
    year = request.form['year']
    month = request.form['month']
    cookie = request.form['cookie']
    if cookie == '':
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        with open(cookie_dir, 'w', encoding='utf-8') as f:
            f.write(cookie)
        if year == '':
            year = None
        if month == '':
            month = None
        date_work_hour = None
        date_work_hour_count = None
        if ZentaoWordHourDim == "1":
            date_work_hour, date_work_hour_count, date_total_type_count = LogWorkHour(start_day=date).week_work_hour()
        elif ZentaoWordHourDim == "2":
            date_work_hour, date_work_hour_count, date_total_type_count = LogWorkHour(start_day=date).month_work_hour(year=year, month=month)
        print(date_work_hour)
        date_range = "本周"
        if ZentaoWordHourDim == "2" and (month != '' or month != None or year != '' or year != None):
            date_range = "本月"
        if date != '':
            return jsonify(
                {"message": {"此时统计工时日期段": date, "统计结果": date_work_hour, "统计日期的总工时": date_work_hour_count, "关联任务总工时": date_total_type_count}})
        else:
            return jsonify(
                {"message": {"此时统计工时日期段": f"{date_range}", "统计结果": date_work_hour, "统计日期的总工时": date_work_hour_count, "关联任务总工时": date_total_type_count}})
@app.route('/ErpMatchRule', methods=['POST'])
def erp_match_rule():
    """ERP统一资料匹配规则"""
    goods_name = request.form['GoodsMeansGoodsName']
    provider_name = request.form['GoodsMeansBandName']
    encap = request.form['GoodsMeansEncap']
    if provider_name == '' or goods_name == "":
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        data_loads_json, opapi_map_goods_res = GoodsProfileObtain(goods_name=goods_name, brand_name=provider_name, goods_id="", encap=encap).opapi_map_goods()
        return jsonify(
            {"message": {"此时入参": data_loads_json, "此时匹配结果": opapi_map_goods_res}})
@app.route('/ImportStockUp', methods=['POST'])
def import_stock_up():
    goods_name = request.form['ImportStockUpGoodsName']
    provider_name = request.form['ImportStockUpProviderName']
    encap = request.form['ImportStockUpEncap']
    goods_no_type = request.form['ImportStockUpGoodsNoVauleType']
    goods_no = request.form['ImportStockUpGoodsNoVaule']
    pack_type = request.form['ImportStockUpPackType']
    spq = request.form['ImportStockUpPackNumber']
    stock_number = request.form['ImportStockUpStockNumber']
    purchase_price = request.form['ImportStockUpPurchasePrice']
    order_sn = request.form['ImportStockUpPurchaseOrderSN']
    stock_type = request.form['ImportStockUpStockType']
    MTS_Rep = request.form['ImportStockUpMTSRep']
    warehouse_name = request.form['ImportStockUpWarehouseName']
    dc = request.form['ImportStockUpDc']
    import_file_type = request.form['ImportStockUpFileType']
    execution_Type = request.form['ImportStockUpExecutionType']
    urgent_Type = request.form['ImportStockUpUrgentType']
    print(execution_Type)
    if not order_sn and (goods_name == '' or provider_name == '' or stock_number == '' or encap == '') and execution_Type in ["all"]:
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    elif not order_sn and (goods_name == '' or provider_name == '' or stock_number == '' or encap == '') and execution_Type in ["import_need_completed"] and import_file_type != "1":
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    elif not order_sn and (goods_name == '' or provider_name == '' or stock_number == '' or encap == '') and execution_Type in ["search_audit_completed"]:
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        msg_MTS_Rep = ''
        msg_pack_type = ''
        msg_spq = ''
        if execution_Type == "all":
            setattr(Data, 'dc', dc)
            rss = Login().login()
            msg, MTS_Rep_new, packer_new, packer_number_new = StockUp(rss, goods_name, provider_name, encap, pack_type, spq, purchase_price, stock_number, stock_type,
                          MTS_Rep, warehouse_name, order_sn, import_file_type, goods_no, goods_no_type, urgent_Type).mian_self_file_stockup()
            if stock_type == "寄售备货":
                # 寄售补货需要在dos这边发货
                order_sn, inn_order_list = ConsignPublish(rss, consign_sn=None, goods_name=goods_name, supplier_sn=None).main_consign_publish_delivery(status=5)
                setattr(Data, 'inn_sn', inn_order_list[0] if inn_order_list != [] else '')
            # msg = "success"
            # setattr(Data, 'stock_goods_name', goods_name)
            if stock_type != "寄售备货":
                # 寄售补货不需要处理erp流程
                erp_target_rss = SOOLogin(system_name="erp").target_login()
                ErpStockPurchase(erp_target_rss).mian_stock_up_purchase()
            wms_target_rss = SOOLogin(system_name="wms").target_login()
            WmsInWarehouse(wms_target_rss).wms_warehousing().wms_theupper_list(theupper_sn='', status='')
            pda_rss = PdaLogin().pda_login()
            PdaTheupper(pda_rss).pda_theupper()
            print("审核结果{}".format(msg))
            if msg == "success":
                if MTS_Rep != MTS_Rep_new:
                    msg_MTS_Rep = "脚本选择的补备货与系统不一致，现由脚本自动替换成{}；".format(MTS_Rep_new)
                if pack_type != packer_new:
                    msg_pack_type = "脚本填入商品的包装方式与系统不一致，现由脚本自动替换成{}；".format(packer_new)
                if spq != packer_number_new:
                    msg_spq = "脚本填入商品的包装数量与系统不一致，现由脚本自动替换成{}；".format(packer_number_new)
                DingTalkHandle(
                    project_name='DOS补备货',
                    prams={
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                },
                    msg_data={"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求成功且审核成功" + msg_MTS_Rep +msg_pack_type+msg_spq, "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                }
                ).send_message()
                return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求成功且审核成功" + msg_MTS_Rep +msg_pack_type+msg_spq, "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                })
            else:
                DingTalkHandle(
                    project_name='DOS补备货',
                    prams={
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                },
                    msg_data={"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求失败，报错信息为{msg}，请检查入参参数", "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                }
                ).send_message(at_mobiles=["15070739124"])
                return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求失败，报错信息为{msg}，请检查入参参数", "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                })
        elif execution_Type == "import_need_completed" and import_file_type == "1":
            setattr(Data, 'dc', dc)
            rss = Login().login()
            msg, MTS_Rep_new, packer_new, packer_number_new = StockUp(rss, goods_name, provider_name, encap, pack_type,
                                                                      spq, purchase_price, stock_number, stock_type,
                                                                      MTS_Rep, warehouse_name, order_sn,
                                                                      import_file_type, goods_no, goods_no_type,
                                                                      urgent_Type).mian_self_file_stockup(IsAudit="No")
            if msg == "success":
                if MTS_Rep != MTS_Rep_new:
                    msg_MTS_Rep = "脚本选择的补备货与系统不一致，现由脚本自动替换成{}；".format(MTS_Rep_new)
                if pack_type != packer_new:
                    msg_pack_type = "脚本填入商品的包装方式与系统不一致，现由脚本自动替换成{}；".format(packer_new)
                if spq != packer_number_new:
                    msg_spq = "脚本填入商品的包装数量与系统不一致，现由脚本自动替换成{}；".format(packer_number_new)
                DingTalkHandle(
                    project_name='DOS补备货',
                    prams={
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                },
                    msg_data={"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求成功" + msg_MTS_Rep +msg_pack_type+msg_spq, "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                }
                ).send_message()
                return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求成功" + msg_MTS_Rep +msg_pack_type+msg_spq, "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                })
            else:
                DingTalkHandle(
                    project_name='DOS补备货',
                    prams={
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                },
                    msg_data={"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求失败，报错信息为{msg}，请检查入参参数", "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                }
                ).send_message(at_mobiles=["15070739124"])
                return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求失败，报错信息为{msg}，请检查入参参数", "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                })
        elif execution_Type == "search_audit_completed" and import_file_type == "1":
            setattr(Data, 'dc', dc)
            rss = Login().login()
            msg, MTS_Rep_new, packer_new, packer_number_new = StockUp(rss, goods_name, provider_name, encap, pack_type,
                                                                      spq, purchase_price, stock_number, stock_type,
                                                                      MTS_Rep, warehouse_name, order_sn,
                                                                      import_file_type, goods_no, goods_no_type,
                                                                      urgent_Type).mian_self_file_stockup()
            if msg == "success":
                if MTS_Rep != MTS_Rep_new:
                    msg_MTS_Rep = "脚本选择的补备货与系统不一致，现由脚本自动替换成{}；".format(MTS_Rep_new)
                if pack_type != packer_new:
                    msg_pack_type = "脚本填入商品的包装方式与系统不一致，现由脚本自动替换成{}；".format(packer_new)
                if spq != packer_number_new:
                    msg_spq = "脚本填入商品的包装数量与系统不一致，现由脚本自动替换成{}；".format(packer_number_new)
                DingTalkHandle(
                    project_name='DOS补备货',
                    prams={
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                },
                    msg_data={"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求成功" + msg_MTS_Rep +msg_pack_type+msg_spq, "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                }
                ).send_message()
                return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求成功" + msg_MTS_Rep +msg_pack_type+msg_spq, "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                })
            else:
                DingTalkHandle(
                    project_name='DOS补备货',
                    prams={
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                },
                    msg_data={"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求失败，报错信息为{msg}，请检查入参参数", "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                }
                ).send_message(at_mobiles=["15070739124"])
                return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求失败，报错信息为{msg}，请检查入参参数", "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                })
        elif execution_Type == "create_procure_completed" and import_file_type == "1":
            setattr(Data, 'dc', dc)
            rss = Login().login()
            msg, MTS_Rep_new, packer_new, packer_number_new = StockUp(rss, goods_name, provider_name, encap, pack_type, spq, purchase_price, stock_number, stock_type,
                          MTS_Rep, warehouse_name, order_sn, import_file_type, goods_no, goods_no_type, urgent_Type).mian_self_file_stockup()
            if stock_type == "寄售备货":
                # 寄售补货需要在dos这边发货
                order_sn, inn_order_list = ConsignPublish(rss, consign_sn=None, goods_name=goods_name, supplier_sn=None).main_consign_publish_delivery(status=5)
                setattr(Data, 'inn_sn', inn_order_list[0] if inn_order_list != [] else '')
            # msg = "success"
            # setattr(Data, 'stock_goods_name', goods_name)
            if stock_type != "寄售备货":
                # 寄售补货不需要处理erp流程
                erp_target_rss = SOOLogin(system_name="erp").target_login()
                ErpStockPurchase(erp_target_rss).mian_stock_up_purchase(IsPurchase="No")
            if msg == "success":
                if MTS_Rep != MTS_Rep_new:
                    msg_MTS_Rep = "脚本选择的补备货与系统不一致，现由脚本自动替换成{}；".format(MTS_Rep_new)
                if pack_type != packer_new:
                    msg_pack_type = "脚本填入商品的包装方式与系统不一致，现由脚本自动替换成{}；".format(packer_new)
                if spq != packer_number_new:
                    msg_spq = "脚本填入商品的包装数量与系统不一致，现由脚本自动替换成{}；".format(packer_number_new)
                DingTalkHandle(
                    project_name='DOS补备货',
                    prams={
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                },
                    msg_data={"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求成功且审核成功" + msg_MTS_Rep +msg_pack_type+msg_spq, "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                }
                ).send_message()
                return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求成功且审核成功" + msg_MTS_Rep +msg_pack_type+msg_spq, "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                })
            else:
                DingTalkHandle(
                    project_name='DOS补备货',
                    prams={
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                },
                    msg_data={"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求失败，报错信息为{msg}，请检查入参参数", "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                }
                ).send_message(at_mobiles=["15070739124"])
                return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求失败，报错信息为{msg}，请检查入参参数", "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                })
        elif execution_Type == "procure_process_completed" and import_file_type == "1":
            setattr(Data, 'dc', dc)
            rss = Login().login()
            msg, MTS_Rep_new, packer_new, packer_number_new = StockUp(rss, goods_name, provider_name, encap, pack_type,
                                                                      spq, purchase_price, stock_number, stock_type,
                                                                      MTS_Rep, warehouse_name, order_sn,
                                                                      import_file_type, goods_no, goods_no_type,
                                                                      urgent_Type).mian_self_file_stockup()
            if stock_type == "寄售备货":
                # 寄售补货需要在dos这边发货
                order_sn, inn_order_list = ConsignPublish(rss, consign_sn=None, goods_name=goods_name,
                                                          supplier_sn=None).main_consign_publish_delivery(status=5)
                setattr(Data, 'inn_sn', inn_order_list[0] if inn_order_list != [] else '')
            # msg = "success"
            # setattr(Data, 'stock_goods_name', goods_name)
            if stock_type != "寄售备货":
                # 寄售补货不需要处理erp流程
                erp_target_rss = SOOLogin(system_name="erp").target_login()
                ErpStockPurchase(erp_target_rss).mian_stock_up_purchase()
            if msg == "success":
                if MTS_Rep != MTS_Rep_new:
                    msg_MTS_Rep = "脚本选择的补备货与系统不一致，现由脚本自动替换成{}；".format(MTS_Rep_new)
                if pack_type != packer_new:
                    msg_pack_type = "脚本填入商品的包装方式与系统不一致，现由脚本自动替换成{}；".format(packer_new)
                if spq != packer_number_new:
                    msg_spq = "脚本填入商品的包装数量与系统不一致，现由脚本自动替换成{}；".format(packer_number_new)
                DingTalkHandle(
                    project_name='DOS补备货',
                    prams={
                        "goods_name": goods_name,
                        "provider_name": provider_name,
                        "pack_type": pack_type,
                        "spq": spq,
                        "purchase_price": float(purchase_price),
                        "stock_number": stock_number,
                        "stock_type": stock_type,
                        "MTS_Rep": MTS_Rep,
                        "warehouse_name": warehouse_name
                    },
                    msg_data={
                        "message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求成功且审核成功" + msg_MTS_Rep + msg_pack_type + msg_spq,
                        "msgCode": 200,
                        "argument": {
                            "goods_name": goods_name,
                            "provider_name": provider_name,
                            "pack_type": pack_type,
                            "spq": spq,
                            "purchase_price": float(purchase_price),
                            "stock_number": stock_number,
                            "stock_type": stock_type,
                            "MTS_Rep": MTS_Rep,
                            "warehouse_name": warehouse_name
                        }
                        }
                ).send_message()
                return jsonify({
                                   "message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求成功且审核成功" + msg_MTS_Rep + msg_pack_type + msg_spq,
                                   "msgCode": 200,
                                   "argument": {
                                       "goods_name": goods_name,
                                       "provider_name": provider_name,
                                       "pack_type": pack_type,
                                       "spq": spq,
                                       "purchase_price": float(purchase_price),
                                       "stock_number": stock_number,
                                       "stock_type": stock_type,
                                       "MTS_Rep": MTS_Rep,
                                       "warehouse_name": warehouse_name
                                   }
                                   })
            else:
                DingTalkHandle(
                    project_name='DOS补备货',
                    prams={
                        "goods_name": goods_name,
                        "provider_name": provider_name,
                        "pack_type": pack_type,
                        "spq": spq,
                        "purchase_price": float(purchase_price),
                        "stock_number": stock_number,
                        "stock_type": stock_type,
                        "MTS_Rep": MTS_Rep,
                        "warehouse_name": warehouse_name
                    },
                    msg_data={
                        "message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求失败，报错信息为{msg}，请检查入参参数",
                        "msgCode": 200,
                        "argument": {
                            "goods_name": goods_name,
                            "provider_name": provider_name,
                            "pack_type": pack_type,
                            "spq": spq,
                            "purchase_price": float(purchase_price),
                            "stock_number": stock_number,
                            "stock_type": stock_type,
                            "MTS_Rep": MTS_Rep,
                            "warehouse_name": warehouse_name
                        }
                        }
                ).send_message(at_mobiles=["15070739124"])
                return jsonify({
                                   "message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求失败，报错信息为{msg}，请检查入参参数",
                                   "msgCode": 200,
                                   "argument": {
                                       "goods_name": goods_name,
                                       "provider_name": provider_name,
                                       "pack_type": pack_type,
                                       "spq": spq,
                                       "purchase_price": float(purchase_price),
                                       "stock_number": stock_number,
                                       "stock_type": stock_type,
                                       "MTS_Rep": MTS_Rep,
                                       "warehouse_name": warehouse_name
                                   }
                                   })
        elif execution_Type == "warehous_process_completed" and import_file_type == "1":
            setattr(Data, 'dc', dc)
            rss = Login().login()
            msg, MTS_Rep_new, packer_new, packer_number_new = StockUp(rss, goods_name, provider_name, encap, pack_type, spq, purchase_price, stock_number, stock_type,
                          MTS_Rep, warehouse_name, order_sn, import_file_type, goods_no, goods_no_type, urgent_Type).mian_self_file_stockup()
            if stock_type == "寄售备货":
                # 寄售补货需要在dos这边发货
                order_sn, inn_order_list = ConsignPublish(rss, consign_sn=None, goods_name=goods_name, supplier_sn=None).main_consign_publish_delivery(status=5)
                setattr(Data, 'inn_sn', inn_order_list[0] if inn_order_list != [] else '')
            # msg = "success"
            # setattr(Data, 'stock_goods_name', goods_name)
            if stock_type != "寄售备货":
                # 寄售补货不需要处理erp流程
                erp_target_rss = SOOLogin(system_name="erp").target_login()
                ErpStockPurchase(erp_target_rss).mian_stock_up_purchase()
            wms_target_rss = SOOLogin(system_name="wms").target_login()
            WmsInWarehouse(wms_target_rss).wms_warehousing().wms_theupper_list(theupper_sn='', status='')
            pda_rss = PdaLogin().pda_login()
            PdaTheupper(pda_rss).pda_theupper()
            print("审核结果{}".format(msg))
            if msg == "success":
                if MTS_Rep != MTS_Rep_new:
                    msg_MTS_Rep = "脚本选择的补备货与系统不一致，现由脚本自动替换成{}；".format(MTS_Rep_new)
                if pack_type != packer_new:
                    msg_pack_type = "脚本填入商品的包装方式与系统不一致，现由脚本自动替换成{}；".format(packer_new)
                if spq != packer_number_new:
                    msg_spq = "脚本填入商品的包装数量与系统不一致，现由脚本自动替换成{}；".format(packer_number_new)
                DingTalkHandle(
                    project_name='DOS补备货',
                    prams={
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                },
                    msg_data={"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求成功且审核成功" + msg_MTS_Rep +msg_pack_type+msg_spq, "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                }
                ).send_message()
                return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求成功且审核成功" + msg_MTS_Rep +msg_pack_type+msg_spq, "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                })
            else:
                DingTalkHandle(
                    project_name='DOS补备货',
                    prams={
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                },
                    msg_data={"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求失败，报错信息为{msg}，请检查入参参数", "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                }
                ).send_message(at_mobiles=["15070739124"])
                return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}导入补备货需求失败，报错信息为{msg}，请检查入参参数", "msgCode": 200,
                                "argument": {
                                    "goods_name": goods_name,
                                    "provider_name": provider_name,
                                    "pack_type": pack_type,
                                    "spq": spq,
                                    "purchase_price": float(purchase_price),
                                    "stock_number": stock_number,
                                    "stock_type": stock_type,
                                    "MTS_Rep": MTS_Rep,
                                    "warehouse_name": warehouse_name
                                }
                                })
@app.route('/AutoStock', methods=['POST'])
def auto_stock():
    """DOS自动补货触发"""
    goods_name = request.form['AutoStockGoodsName']
    provider_name = request.form['AutoStockProviderName']
    goods_no = request.form['AutoStockGoodsNo']
    goods_id = request.form['AutoStockGoodsId']
    if goods_name == '' or provider_name == ''or goods_no == '' or goods_id == '':
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        msg, miss_rule_information = AutoStock(goods_id, goods_name, goods_no, provider_name).auto_stock_mian()
        if msg == False:
            return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}, 芯城编码：{goods_no}自动补货成功", "msgCode": 200,
                            "argument": {
                                "goods_name": goods_name,
                                "provider_name": provider_name,
                                "goods_no": goods_no,
                                "goods_id": goods_id
                            },
                            "result": miss_rule_information
            })
        else:
            return jsonify({"message": f"型号：{goods_name}，品牌：{provider_name}, 芯城编码：{goods_no}自动补货不符规则", "msgCode": 200,
                            "argument": {
                                "goods_name": goods_name,
                                "provider_name": provider_name,
                                "goods_no": goods_no,
                                "goods_id": goods_id
                            },
                            "result": miss_rule_information
            })

@app.route('/jenkinsBuild', methods=['POST'])
def jenkinsBuild():
    """jenkins发布"""
    environment = request.form['environmentType']
    build_project = request.form['BuildProject']
    project_branch = request.form['ProjectBranch']
    if build_project == '' or project_branch == '':
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        jenkins_rss = JenkinsLogin().jenkins_login()
        code = ProjectBuildJenkins(jenkins_rss, environment, build_project, project_branch).mian_build_project()
        if code == 200:
            return jsonify({"message": f"项目：{build_project}在环境：{environment}的分支：{project_branch}执行构建成功，请检查页面执行最终结果", "msgcode": 200})
        else:
            return jsonify({"message": f"项目：{build_project}在环境：{environment}的分支：{project_branch}执行构建成功，请检查页面执行最终结果", "msgcode": 200})

@app.route('/hqTaskTool', methods=['POST'])
def hqTaskBuild():
    environment = request.form['hqTaskenvironmentType']
    task_name = request.form['hqTaskName']
    match_type = request.form['hqTaskMacthType']
    action_name = request.form['hqTaskActionName']
    action_name_json = {"start": "启动", "stop": "停止", "restart": "重启"}
    match_type_json = {1: "精确匹配", 0: "模糊匹配"}
    if task_name == '' :
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        rss = TaskLogin().login()
        msg = HQTask(rss, environment, task_name, int(match_type), action_name).mian_environment_match_task()
        action_name_cn = ''
        match_type_cn = ''
        for key, value in action_name_json.items():
            if action_name == key:
                action_name_cn = value
        for k, v in match_type_json.items():
            if int(match_type) == k:
                match_type_cn = v
        if len(msg) >= 1:
            if any("请检查任务名称或者匹配类型" in item for item in msg):
                return jsonify({"message": f"任务：{task_name}在环境：{environment}的匹配方式：{match_type_cn}执行{action_name_cn}操作存在错误，执行结果为{msg}", "msgcode": 200})
            else:
                return jsonify({"message": f"任务：{task_name}在环境：{environment}的匹配方式：{match_type_cn}执行{action_name_cn}操作成功，执行结果为{msg}", "msgcode": 200})
        else:
            return jsonify({"message": f"任务：{task_name}在环境：{environment}的匹配方式：{match_type_cn}执行{action_name_cn}操作存在错误，执行结果为{msg}", "msgcode": 200})

@app.route('/PhpAntisequencePython')
def ParsePhpPython():
    keyword = request.args.get('keyword', default=1, type=str)
    json_data = PhpAntisequence(keyword).php_Antisequence()
    if json_data != '':
        return jsonify({"message": json.loads(json_data)})
    else:
        return jsonify({"message": "失败"})
@app.route('/sqlReviewTool', methods=['POST'])
def sqlReviewTool():
    sqlReviewenvironmentType = request.form['sqlReviewenvironmentType']
    BuildBase = request.form['BuildBase']
    sqls = request.form['sqls']
    submit_text = request.form['SubmitText']
    work_id = request.form['WorkId']
    if sqls != '' or work_id != '':
        rss = SqlReviewLogin().sqlReview_login()
        if work_id == '' and submit_text != '':
            source_name = sqlReviewenvironmentType + '-' + BuildBase
            msg = SqlReviewKitTool(rss, data_base=BuildBase, source_name=source_name, sql=sqls, text=submit_text).mian_sql_work_submit()
            return jsonify({"message": f"提交SQL语句结果：{msg}", "msgCode": 200,
                            "argument": {
                                "source_name": source_name,
                                "data_base": BuildBase,
                                "sqls": sqls,
                                "submit_text": submit_text
                            }
                            })
        elif work_id != '':
            source_name = sqlReviewenvironmentType + '-' + BuildBase
            msg = SqlReviewKitTool(rss, data_base=BuildBase, source_name=source_name, sql=sqls, text=submit_text).mian_sql_work_audit(work_id)
            return jsonify({"message": f"审核工单{work_id}结果：{msg}", "msgCode": 200,
                            "argument": {
                                "source_name": source_name,
                                "data_base": BuildBase,
                                "work_id": work_id
                            }
                            })
        else:
            return jsonify({"message": "必填字段缺失请检查", "msgcode": 200})
    else:
        return jsonify({"message": "SQL语句和工单不能同时为空", "msgcode": 200})
@app.route('/MongodbStockUpdate')
def MongodbStockUpdate():
    goods_id = request.args.get('goods_id', default=None, type=str)
    supplier_uuid = request.args.get('supplier_uuid', default=None, type=str)
    other_model_name = request.args.get('other_model_name', default=None, type=str)
    if goods_id is None or goods_id.strip() == '':
        return jsonify({"message": "goods_id不能为空"})

    MongodbRenew(goods_id, supplier_uuid, other_model_name).mian_mongodb_stock_update()
    return jsonify({"message": "库存更新中..."})
@app.route('/consignPublish', methods=['POST'])
def consignPublish():
    consign_sn = request.form['consignSn']
    goods_name = request.form['consignGoodsName']
    supplier_sn = request.form['supplierSn']
    if consign_sn != '' or goods_name != '' or supplier_sn != '':
        hc2018_target_rss = Login().login()
        order_sn = ConsignPublish(hc2018_target_rss, consign_sn, goods_name, supplier_sn).main_consign_publish_delivery()
        Erp_rss = ErpLogin().login()
        inn_order_success_count = []
        inn_order_error_count = []
        for i in range(len(order_sn)):
            setattr(Data, 'relevance_order_sn', order_sn[i])
            ErpOrderPutaway(Erp_rss, "关联采购单号").putaway_order_search()

            inn_order = getattr(Data, 'inn_sn')
            try:
                wms_target_rss = SOOLogin("uat-wms.huaqiu.com", "wms/base").target_login()
                WmsInWarehouse(wms_target_rss).wms_warehousing().wms_theupper_list(theupper_sn='', status='')
                pda_rss = PdaLogin().pda_login()
                PdaTheupper(pda_rss).pda_theupper()
                inn_order_success_count.append(inn_order)
                return jsonify(
                    {"message": {"inn_sn": inn_order_success_count}, "msgStr": "以上入库单号已入库请等待数据同步", "msgcode": 200})
            except:
                inn_order_error_count.append(inn_order)
                return jsonify(
                    {"message": {"inn_sn": inn_order_error_count}, "msgStr": "以上入库单号不存在或者不满足入库要求，请检查入库单号",
                     "msgcode": 403})
@app.route('/suppliersearch/goodssearch')
def supplie_search_sync():
    """element14---接口层面"""

    goods_name = request.args.get('goods_name', default=1, type=str)
    products = Element14Search(goods_name).element14_search_api()
    print(products)


    if products != []:
        return jsonify({"message": products})
    else:
        return jsonify({"message": "查询失败", "msgCode": 404})

@app.route('/qrcodekit/qrcodeLink', methods=['POST'])
def qrcode_link():
    """根据链接生成二维码"""
    url_link_type = request.form['qrcodeLinkType']
    url_link = request.form['urlLink']
    if url_link_type == "字典格式":
        if isinstance(url_link, str):
            try:
                parsed = json.loads(url_link)
                if isinstance(parsed, dict):
                    url_link = json.dumps(parsed, ensure_ascii=False, separators=(',', ':'))
            except:
                pass
    # url_link = request.args.get('urlLink', default='', type=str)
    if url_link:
        # 创建 QRCode 对象并生成二维码图像
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # 将链接添加到二维码中
        qr.add_data(url_link)
        qr.make(fit=True)
        # 创建 PIL 图像对象
        img = qr.make_image(fill_color="black", back_color="white")
        # 保存生成的二维码图片到内存中
        # img_io = BytesIO()
        # img.save(img_io, format='PNG')
        # img_io.seek(0)
        #
        # # 将生成的二维码图片直接作为响应返回给客户端
        # return render_template('index.html', qr_image=base64.b64encode(img_io.getvalue()).decode('utf-8'))
        # 保存生成的二维码图片到本地文件
        current_timestamp = str(int(time.time()))
        # 手动替换斜杠为编码后的结果
        encoded_url = quote(url_link, safe='')
        # 将空格替换为%20
        encoded_url = encoded_url.replace(" ", "%20")
        save_path = qr_code_dir + encoded_url + current_timestamp + '.png' # 替换为你希望保存的文件路径
        img.save(save_path)

        # 返回响应到客户端，如果需要在页面上显示二维码，可以使用 base64 编码的方式传递给模板
        with open(save_path, 'rb') as f:
            qr_image = base64.b64encode(f.read()).decode('utf-8')

        return render_template('index.html', qr_image=qr_image)
    else:
        return "请提供有效的链接", 400
@app.route('/expressSearch', methods=['POST'])
def express_search():
    """物流查询"""
    express_number = request.form['expressNumber']
    comCode_url = "https://www.kuaidi100.com/autonumber/autoComNum?text={}"

@app.route('/sensitiveWords/detection', methods=['POST'])
def sensitive_words_detection():
    """问答敏感词检测"""
    title = request.form['Title']
    seo_title = request.form['SeoTitle']
    seo_keyword = request.form['SeoKeyword']
    seo_desc = request.form['SeoDesc']
    reply_content = request.form['replyContent']
    if title == '' or reply_content == '':
        return jsonify({"message": "必填字段缺失请检查", "msgcode": 200})
    else:
        detection_msg = SensitiveWordsDetection(title, reply_content, seo_title, seo_keyword, seo_desc).sensitive_words_detection()
        if detection_msg['retMsg'] == '':
            ask_id = detection_msg["result"]['askId']
            return jsonify({"message": "恭喜，该内容没有敏感词,并且生成问答",
                            "argument": {"title": title, "seo_title": seo_title, "seo_keyword": seo_keyword,
                                         "seo_desc": seo_desc, "reply_content": reply_content},
                            "askId": ask_id,
                            "msgcode": 200})
        else:
            return jsonify({"message": detection_msg['retMsg'],
                            "argument": {"title": title, "seo_title": seo_title, "seo_keyword": seo_keyword,
                                         "seo_desc": seo_desc, "reply_content": reply_content},
                            "msgcode": 200})
@app.route('/orderCompanyTransferWriteOff', methods=['POST'])
def order_transfer_write_off():
    # 公司转账核销
    order_sn = request.form['orderWriteOff']
    bank_statement_id = request.form['companyTransferStatementId']
    if order_sn == '':
        return jsonify({"message": "必填字段缺失请检查", "msgcode": 200})
    else:
        target_rss = SOOLogin("uat-e.hqchip.com", "AuthLogin").target_login()
        result = ErpOrderCancellation(target_rss, order_sn).erp_ic_order_transfer_claim(bank_statement_id=bank_statement_id)
        if result['info'] == "复核成功！":
            return jsonify({"message": "恭喜，该订单已核销", "msgcode": 200})
        else:
            return jsonify({"message": "该订单核销失败，请检查相关信息", "msgcode": 404})
@app.route('/hqErp/apiSync')
def ERP_sync():
    """合作库存一键导入更新---接口层面"""
    pbill_id = request.args.get('pbill_id', default=1, type=str)
    products = ErpSyncAPI().final_statement_sync(pbill_id=pbill_id)
    print(products)

@app.route('/timestamp_real_time')
def timestamp_real_time():
    timestamp = TimestampConvert().timestamp_real_time()
    return jsonify({'timestamp': timestamp})
@app.route('/timestampConvert', methods=['POST'])
def timestamp_convert():
    convert_time = request.form['convertTimestamp']
    convert_timestamp = request.form['convertTime']
    print(convert_time, convert_timestamp)
    timestamp = None
    formatted_time = None
    if convert_time != ''and convert_timestamp == '':
        timestamp = TimestampConvert().time_convert_timestamp(convert_time)
    elif convert_timestamp != '' and convert_time == '':
        formatted_time = TimestampConvert().timestamp_convert_time(convert_timestamp)
    elif convert_time != '' and convert_timestamp != '':
        timestamp = TimestampConvert().time_convert_timestamp(convert_time)
        formatted_time = TimestampConvert().timestamp_convert_time(convert_timestamp)
    else:
        pass
    return jsonify({"message": "时间转换成功",
                    "result": {"转换的时间戳": timestamp, "转换的时间": formatted_time},
                    "msgcode": 200})



@app.route('/2025munich', methods=['POST'])
def munich():
    LOTTERY_TIMES_start = request.form['LotteryChancesStart']
    LOTTERY_TIMES_end = request.form['LotteryChancesEnd']
    THREAD_COUNT = request.form['ThreadCount']
    data = None
    if not LOTTERY_TIMES_start and not LOTTERY_TIMES_end:
        return jsonify({"message": "必填字段缺失请检查", "msgcode": 200})
    else:
        LOTTERY_TIMES_start = int([LOTTERY_TIMES_start if LOTTERY_TIMES_start else 0][0])
        LOTTERY_TIMES_end = int([LOTTERY_TIMES_end if LOTTERY_TIMES_end else int(LOTTERY_TIMES_start) + 600][0])
        THREAD_COUNT = int(THREAD_COUNT)
        data = Muniheiactivity(LOTTERY_TIMES_start, LOTTERY_TIMES_end, THREAD_COUNT).main()
        # 递归转换 data 中的所有 numpy.int64 类型
        data = convert_numpy_types(data)
        if data:
            return jsonify({"message": "恭喜，该活动抽奖成功",
                            "result": {"LotteryChancesStart": LOTTERY_TIMES_start, "LotteryChancesEnd": LOTTERY_TIMES_end,
                                       "ThreadCount": THREAD_COUNT, "data": data},
                            "msgcode": 200})
        else:
            return jsonify({"message": "该活动抽奖失败，请检查相关信息", "msgcode": 404})
@app.route('/useryzmcode', methods=['POST'])
def useryzmcode():
    yzmCodeType = request.form['yzmCodeType']
    yzmCodePhone = request.form['yzmCodePhone']
    yzmCodeUid = request.form['yzmCodeUid']
    yzmCodeType_Name = {
        '1': '注册登录或修改密码',
        '2': '支付密码',
        '3': '企业认证',
        '4': '用户注销'
    }
    yzmCodeName = None
    required_msg = None
    for key in yzmCodeType_Name:
        if yzmCodeType == key:
            yzmCodeName = yzmCodeType_Name[key]
    if yzmCodeType in ['1', '3'] and yzmCodePhone == '' or yzmCodeType == '2' and yzmCodeUid == '':
        yzmCodeType_required = {
            '1': '必填字段缺失，请检查手机号',
            '2': '必填字段缺失，请检查UID',
            '3': '必填字段缺失，请检查手机号',
            '4': '必填字段缺失，请检查手机号'
        }

        for key in yzmCodeType_required:
            if yzmCodeType == key:
                required_msg = yzmCodeType_required[key]
        return jsonify({"message": f"验证码类型为{yzmCodeName}的{required_msg}", "msgcode": 200})
    else:
        code = YzmCodeObtain(yzmCodeType, yzmCodePhone, yzmCodeUid).yzmcode_obtain()
        print(f"验证码：{code}")

        if code:
            return jsonify({"message": f"{yzmCodeName}验证码为{code}", "msgcode": 200})
        else:
            return jsonify({"message": "获取验证码失败", "msgcode": 404})
@app.route('/orderSensitiveEncryptAndDecrypt', methods=['POST'])
def orderSensitiveEncryptAndDecrypt():
    execution_type = request.form['ExecutionType']
    data = request.form['data']
    if data == "":
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        if isinstance(data, str):
            # 清理字符串（去掉换行、空格）
            s = data.strip().replace("\n", "").replace("\r", "")
            if (s.startswith("{") and s.endswith("}")):
                print(111)
                try:
                    # 3. 给无引号key加双引号
                    s = re.sub(r'([{,])([a-zA-Z_][a-zA-Z0-9_]*):', r'\1"\2":', s)

                    # 4. 【关键修复】把 JS 关键字转成 Python 能识别的
                    s = s.replace("true", "True").replace("false", "False").replace("null", "None")

                    # 5. 强制转换
                    data = eval(s)  # 👈 这个方法对你的数据 100% 成功

                    print("✅ 转换成功！类型：", type(data))

                except:
                    # 转换失败 → 返回原始字符串
                    pass

        type_Sensitive = {
            '1': '加密',
            '2': '解密',
            '3': '自动解密'
        }
        execution_type_name = None
        for key in type_Sensitive:
            if execution_type == key:
                execution_type_name = type_Sensitive[key]
        if int(execution_type) == 1:
            print(11)
            dataStr = orderSensitiveMsgEncrypt(data=data).encrypt()
            return jsonify({"message": f"字段{execution_type_name}结果为： {dataStr}", "msgCode": 200})
        elif int(execution_type) == 2:
            print(12)
            if isinstance(data, str):
                print(14)
                dataJSON = orderSensitiveMsgEncrypt(dataStr=data).dencrypt()
                return jsonify({"message": f"字段{execution_type_name}结果为： {dataJSON}", "msgCode": 200})
            else:

                return jsonify({"message": f"字段{execution_type_name}不支持类型为： {type(data)}", "msgCode": 200})
        elif int(execution_type) == 3:
            print(13)
            dataJSON = orderSensitiveMsgEncrypt(dencrypt_data=data).auto_dencrypt()
            return jsonify({"message": f"字段{execution_type_name}结果为： {dataJSON}", "msgCode": 200})


@app.route('/searchoverseas', methods=['POST'])
def search_overseas_agent_stock():
    goods_name = request.form['overseasGoodsName']
    goods_no = request.form['overseasGoodsNo']
    brand_name = request.form['overseasGoodsBrand']
    max_res_count = request.form['overseasGoodsReturnNumber']
    alias_brand_name_list = request.form['overseasGoodsBrandAlias']
    if goods_name == '' and brand_name == '' or goods_name == '' and alias_brand_name_list == '':
        return jsonify({"message": "必填字段缺失，请检查型号名称和品牌名称或品牌别名", "msgcode": 200})
    else:
        stocks_info = OverseAgentStockApi(goods_name,  goods_no, brand_name, max_res_count, alias_brand_name_list).overse_agent_stock_search_java()
        print(stocks_info)
        if stocks_info != []:
            return jsonify({"message": "获取海外库存成功", "data": stocks_info, "msgcode": 200})
        else:
            return jsonify({"message": "该型号名称或品牌名称或品牌别名不存在", "msgcode": 404})

@app.route('/refreshSupplierDt', methods=['GET'])
def supplie_goodsId_update_DT():
    """合作库存交期更新---接口层面"""
    pn2 = request.args.get('pn2', default=1, type=str)
    suc = SupplierUpdate(pn2=pn2).mian_update()
    # print(suc)
    if suc[0] == True:
        return jsonify({"message": {"result": {"msgStr": "pn2:{}更新中，请稍后".format(pn2), "msgCode": 200}}})
    else:
        return jsonify({"message": "pn2:{}更新失败".format(pn2), "msgCode": 404})
@app.route('/WindowsShutdown', methods=['GET'])
def windows_shutdown():
    """设置电脑自动关机时间-接口层面"""
    import_time = request.args.get('import_time', default=1, type=str)
    code = WindowsShutdown(import_time).schedule_shutdown()
    # print(suc)
    if code == True:
        return jsonify({"message": {"result": {"msgStr": "自动添加关机任务成功", "msgCode": 200}}})
    else:
        return jsonify({"message": "自动添加关机任务失败", "msgCode": 404})
@app.route('/userRegisterRechargeICOrder', methods=['POST'])
def user_register_recharge_ic_order():
    # 用户注册充值 IC下单
    userRegisterPhone = request.form['userRegisterRechargeICOrderPhone']
    userRegisterLoginPassword = request.form['userRegisterRechargeICOrderLoginPassword']
    userRegisterPayPassword = request.form['userRegisterRechargeICOrderPayPassword']
    userRegisterRechargeType = request.form['userRegisterRechargeICOrderRechargeType']
    userRegisterRechargeAmount = request.form['userRegisterRechargeICOrderAmount']
    goods_id = request.form['userRegisterRechargeICOrderGoodsId']
    number = request.form['userRegisterRechargeICOrderNumber']
    warehouse_id = request.form['userRegisterRechargeICOrderWarehouse']
    vat_type = request.form['userRegisterRechargeICOrderVatType']
    vat_sub_type = request.form['userRegisterRechargeICOrderVatSubType']
    shipping_method = request.form['userRegisterRechargeICOrderShippingMethodType']
    password_update_type = request.form['userRegisterRechargeICOrderPasswordUpdateType']
    place_an_order_type = request.form['userRegisterRechargeICOrderRechargePlaceAnOrderType']
    pay_type = request.form['userRegisterRechargeICOrderRechargePayType']
    recharge_order_create = {}
    if ((password_update_type in ["1", "3"] and userRegisterLoginPassword == '') or (password_update_type in ["2", "3"] and userRegisterPayPassword == '')
         or (userRegisterRechargeType == "2" and userRegisterRechargeAmount == "") or (place_an_order_type == "1" and (goods_id == "" or number == ""))):
        return jsonify({"message": "必填字段为空，请检查", "msgCode": 404})
    else:
        if userRegisterPhone == "":
            userRegisterPhone = None
        login_phone, paypassword, userRegisterLoginPassword = UserRegister(phone=userRegisterPhone).register(password_update_type = password_update_type, paypassword=userRegisterPayPassword, new_password=userRegisterLoginPassword)
        if int(userRegisterRechargeAmount) >= 5000000:
            return jsonify({"message": "输入的充值金额过大，请核对充值金额！！！", "msgcode": 200})
        else:
            pass_port_user_msg = {"phone": login_phone, "name": '', "pwd": userRegisterLoginPassword}
            ic_order_params = {
                'goods_id': goods_id,
                "number": number,
                "warehouse_id": warehouse_id,
                "vat_type": vat_type,
                "vat_sub_type": vat_sub_type,
                'shipping_method': shipping_method,
               'relation_smt_order_sn': ''
            }
            user_msg = {'PassPort': pass_port_user_msg}
            order_params = {"HQCHIP_GOODS": ic_order_params}
            write_yaml(account_yaml, order_params)
            write_yaml(account_yaml, user_msg)
            setattr(Data, 'Amount', userRegisterRechargeAmount)
            setattr(Data, 'activity_type', "不参与")
            recharge_order = ''
            reception_rss = None
            voucher_create_json = None
            if userRegisterRechargeType == "2":
                for i in range(int(1)):
                    recharge_order, centerTradeNoExtend, reception_rss = CenterPayCallback().mian_pay_callback()
                    target_rss = SOOLogin("uat-activity.hqchip.com", "ecmc").target_login()
                    voucher_create_json = UserVocher(target_rss, recharge_order, unionId=getattr(Data, 'uid', ''),
                                                     activity_id=getattr(Data, 'voucher_activity_id', ''),
                                                     amount=userRegisterRechargeAmount).mian_activity_voucher_create_accounting()
            recharge_order_create["voucher_create_json"] = voucher_create_json
            recharge_order_create["recharge_order"] = recharge_order
            if place_an_order_type == "1":
                RunIC(reception_rss=reception_rss).mian_ic_order_create()
                order_json = getattr(Data, 'order_json')
                order_sn = order_json["order_sn"]
                if recharge_order == None and order_json == {}:
                    return jsonify({"message": "用户注册创建销售订单成功", "msgcode": 404})
                else:
                    if pay_type == "1":
                        BalancePayment(order_sn=order_sn).main_balance_pay()
                        return jsonify({"message": "用户注册创建销售订单成功",
                                            "data": {"phone": login_phone,
                                                     "password": userRegisterLoginPassword,
                                                     "Amount": userRegisterRechargeAmount,
                                                     "recharge_order_create": recharge_order_create,
                                                     "IcOrderJson": order_json
                                                     },
                                            "msgcode": 200})
                    else:
                        return jsonify({"message": "用户注册创建销售订单成功但未支付",
                                        "data": {"phone": login_phone,
                                                 "password": userRegisterLoginPassword,
                                                 "Amount": userRegisterRechargeAmount,
                                                 "recharge_order_create": recharge_order_create,
                                                 "IcOrderJson": order_json
                                                 },
                                        "msgcode": 200})
            else:
                return jsonify({"message": "用户注册或充值成功成功",
                                "data": {"phone": login_phone,
                                         "password": userRegisterLoginPassword,
                                         "Amount": userRegisterRechargeAmount,
                                         "recharge_order_create": recharge_order_create,
                                         "IcOrderJson": {}
                                         },
                                "msgcode": 200})
# @app.before_request
# def check_host():
#     allow_hosts = {
#         "www.yemaotest.com:5000",
#         "192.168.14.69:5000",
#         "127.0.0.1:5000"
#     }
#     if request.host not in allow_hosts:
#         abort(404)
if __name__ == '__main__':
    # app.config['SERVER_NAME'] = "www.yemaotest.com:5000"
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)

