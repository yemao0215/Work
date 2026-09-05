import os
# os.path.dirname: 求所输入参数的上一级目录
# 获取当前文件的绝对路径
config_path = os.path.abspath(__file__)
# 获取common路径
config_dir = os.path.dirname(config_path)
# 获取 项目路径
root_dir = os.path.dirname(config_dir)
# 获取 conf路径
conf_dir = os.path.join(root_dir, r'Conf')
if not os.path.exists(conf_dir):
    os.mkdir(conf_dir)


# 拼到config.yaml配置文件路径
yaml_file = os.path.join(conf_dir, r'conf.yaml')
# 拼到config.yaml配置文件路径
account_yaml = os.path.join(conf_dir, r'account_conf.yaml')
# 拼到supplier.yaml配置文件路径
supplier_dir = os.path.join(conf_dir, r'supplier.yaml')
# partner.yaml配置文件路径
partnerYaml_dir = os.path.join(conf_dir, r'partner.yaml')
# shieId_eccn.yaml文件路径
shieIdEccnYaml_dir = os.path.join(conf_dir, r'partner.yaml')
# Jenkins_project.yaml配置文件路径
JenkinsProjectYaml_dir = os.path.join(conf_dir, r'Jenkins_project.yaml')

# 拼到搜索报错检查型号报错配置文件路径
field1_goodsId_yaml = os.path.join(conf_dir, r'UAT-search_API\\fieId1_goods_id.yaml')
field2_goodsId_yaml = os.path.join(conf_dir, r'UAT-search_API\\fieId2_goods_id.yaml')


# 自动补货型号Yaml文件
autoStockYaml_dir = os.path.join(conf_dir, r'auto_stock.yaml')
# 抖音来客body数据Yaml文件
crmLifeDataYaml_dir = os.path.join(conf_dir, r'douyin_life_data.yaml')

# 是否加密字段Yaml文件路径
encryptConfYaml_dir = os.path.join(conf_dir, r'encrypted_conf.yaml')

# 拼到配置目录conf.ini文件路径
conf_ini = os.path.join(conf_dir, r"conf.ini")

# 日志路径
outputs_dir = os.path.join(root_dir, r"outputs")
log_dir = os.path.join(outputs_dir, r"logs", r"log_file")
log_file = os.path.join(outputs_dir, r"logs")


# 报告路径
report_dir = os.path.join(root_dir, r"outputs", r"reports")

# 测试用例路径
testdata_dir = os.path.join(root_dir, r"testdatas")
excel_path = os.path.join(testdata_dir, r"测试用例.xlsx")

# bom路径
hqchip_dir = os.path.join(root_dir, r"HQCHIP")
bom_dir = os.path.join(hqchip_dir, r"BOM\\bom.xls")
bom_math_dir = os.path.join(hqchip_dir, r"BOM\\bom.csv")
# HQCHIP-mouser goods_id文件
goodsid_dir = os.path.join(hqchip_dir, r"product\\goods_id.csv")

# HC2018相关文件路径
hc2018Admin_dir =os.path.join(root_dir, r"HC2018_admin")
stockup_dir = os.path.join(hc2018Admin_dir, r"stock_up\\stockup.xlsx")
stockup_error_dir = os.path.join(hc2018Admin_dir, r"stock_up\\stockup_error.xlsx")
b = os.path.join(root_dir,"渠道员-现货发布模版.xls")
eccn_dir = os.path.join(hc2018Admin_dir, r"ECCN_add\\ENNC编码_20230822.csv")
szlcsc_brand_dir = os.path.join(hc2018Admin_dir, r"third_party_mapping\\szlcsc_data_basics\\芯灵DOS品牌一对多映射 OK.xlsx")
szlcsc_category_dir = os.path.join(hc2018Admin_dir, r"third_party_mapping\\szlcsc_data_basics\\芯灵DOS类目一对多映射 OK.xlsx")
attr_dir = os.path.join(hc2018Admin_dir, r"dgk_goods_means\\属性.xlsx")
dos_agency_sale_dir = os.path.join(hc2018Admin_dir, r"supplier_goods_publish\\settle_goods_bill\\代售库存发布模板.xlsx")
dos_consignment_launch_dir = os.path.join(hc2018Admin_dir, r"supplier_goods_publish\\settle_goods_bill\\寄售发布模板.xlsx")
dos_consignment_reprice_dir = os.path.join(hc2018Admin_dir, r"supplier_goods_publish\\settle_goods_bill\\寄售改价模板.xlsx")
dos_futures_launch_dir = os.path.join(hc2018Admin_dir, r"supplier_goods_publish\\settle_goods_bill\\期货发布模板.xlsx")
dos_stock_txt_sql = os.path.join(hc2018Admin_dir, r"stock_sql_text\\text_sql.sql")
xlsx_dos_brand_dir = os.path.join(hc2018Admin_dir, r"dgk_goods_means\\dos_brand.xlsx")
# 芯灵相关文件路径
ShangHai_XinLing_dir =os.path.join(root_dir, r"ShangHai_XinLing")
xl_brand_dir = os.path.join(ShangHai_XinLing_dir, r"XLSX\\xl_brand.xlsx")
xl_dos_brand_dir = os.path.join(ShangHai_XinLing_dir, r"XLSX\\xl_dos_brand.xlsx")
xl_dos_category_dir_pro = os.path.join(ShangHai_XinLing_dir, r"XLSX\\芯灵与DOS类目属性映射.xlsx")
xl_category_dir = os.path.join(ShangHai_XinLing_dir, r"XLSX\\xl_category.xlsx")
xl_create_goods_dir = os.path.join(ShangHai_XinLing_dir, r"XinLing_bpm\\芯灵资料创建导入模板.xlsx")

# 专题文件信息
subject_logo_dir =os.path.join(root_dir,"专题图片\\logo")
# assembly_file_dir = os.path.join(subject_logo_dir,"发烧友.png")
# 获取logo文件夹的图片信息
logo_files = os.listdir(subject_logo_dir)  #得到⽂件夹下的所有⽂件名称
logo_txts = []
for file in logo_files:  #遍历⽂件夹
    position = subject_logo_dir+"\\"+file  #构造绝对路径，"\\"，其中⼀个'\'为转义符
    logo_txts.append(position)
img_dir = subject_logo_dir+"\\"+logo_files[0]
# print(logo_txts)
# 专题图片信息
subject_one_img_dir = os.path.join(root_dir, r"专题图片\\单张图片\\单张图片.png")
subject_more_Images2_dir = os.path.join(root_dir, r"专题图片\\图片组件2\\图片组件2.png")
subject_more_Images2_icon_right_dir = os.path.join(root_dir, r"专题图片\\图片组件2\\iCON.png")
subject_more_Images3_dir = os.path.join(root_dir, r"专题图片\\图片组件3\\图片组件3.png")
subject_more_Images3_icon_right_dir = os.path.join(root_dir, r"专题图片\\图片组件3\\iCON.png")
subject_more_Images4_dir = os.path.join(root_dir, r"专题图片\\图片组件4\\图片组件4.png")
subject_more_Images4_icon_right_dir = os.path.join(root_dir, r"专题图片\\图片组件4\\iCON.png")
subject_more_img_dir = os.path.join(root_dir, r"专题图片\\多张图片\\多张图片.png")
subject_more_img2_dir = os.path.join(root_dir, r"专题图片\\多张图片2\\多张图片2.png")
subject_more_img2_icon_right_dir = os.path.join(root_dir, r"专题图片\\图片组件2\\iCON.png")
subject_more_img3_dir = os.path.join(root_dir, r"专题图片\\多张图片3\\多张图片3.jpg")
subject_more_img3_icon_left_dir = os.path.join(root_dir, r"专题图片\\多张图片3\\iCON-left.png")
subject_more_img3_icon_right_dir = os.path.join(root_dir, r"专题图片\\多张图片3\\iCON-right.png")
subject_more_HandleImg1_dir = os.path.join(root_dir, r"专题图片\\交互图片组件1\\交互图片.png")
subject_more_HandleImg1_icon_right_dir = os.path.join(root_dir, r"专题图片\\交互图片组件1\\iCON-right.png")
subject_more_TextAndImage_dir = os.path.join(root_dir, r"专题图片\\左文右图\\左文右图.png")
subject_more_TextAndImage_icon_right_dir = os.path.join(root_dir, r"专题图片\\左文右图\\iCON.png")
subject_more_Aspect1_dir = os.path.join(root_dir, r"专题图片\\看点组件图片\\看点组件图片.png")
subject_more_Aspect1_icon_right_dir = os.path.join(root_dir, r"专题图片\\看点组件图片\\iCON.png")
subject_more_Aspect1_button_dir = os.path.join(root_dir, r"专题图片\\看点组件图片\\按钮.png")
subject_order_now_dir = os.path.join(root_dir, r"专题图片\\立即下单logo\\样式一.png")
subject_form_submit_dir = os.path.join(root_dir, r"专题图片\\表单组件图片\\提交报名按钮.png")
subject_banner_dir = os.path.join(root_dir, r"专题图片\\通栏图片")
subject_more_banner_txts = [os.path.join(subject_banner_dir, file) for file in os.listdir(subject_banner_dir)]
subject_NavBar_main_icon_dir = os.path.join(root_dir, r"专题图片\\导航菜单(一)图片\\主LOGO.png")
subject_NavBar_button_enroll_icon_dir = os.path.join(root_dir, r"专题图片\\导航菜单(一)图片\\大会报名按钮.png")
subject_NavBar_button_review_icon_dir = os.path.join(root_dir, r"专题图片\\导航菜单(一)图片\\大会回顾按钮.png")
subject_orderSalesRanking_dir = os.path.join(root_dir, r"专题图片\\排行榜")
subject_more_Pendant_dir = os.path.join(root_dir, r"专题图片\\挂件组件\\挂件组件图片.png")
subject_Sign_dir = os.path.join(root_dir, r"专题图片\\注册组件\\注册组件.png")
subject_Register_dir = os.path.join(root_dir, r"专题图片\\报名式组件")
qr_code_dir = os.path.join(root_dir, r"专题图片\\二维码生成数据\\")
img_code_dir = os.path.join(root_dir, r"ShangHai_XinLing\\img\\output_image.png")
img_processed_captcha_dir = os.path.join(root_dir, r"ShangHai_XinLing\\img\\processed_captcha.png")

#  拉新活动
img_share_support_cover_dir = os.path.join(root_dir, r"HQCHIP_Activity\\invite\\img\\invite_share_support\\活动头图.png")
img_share_support_newusers_dir = os.path.join(root_dir, r"HQCHIP_Activity\\invite\\img\\invite_share_support\\奖品-被邀请人-pcb新客.png")

img_plan_an_order_cover_PC_dir = os.path.join(root_dir, r"HQCHIP_Activity\\invite\\img\\invite_plan_an_order_img\\PC-活动头图.png")
img_plan_an_order_cover_H5_dir = os.path.join(root_dir, r"HQCHIP_Activity\\invite\\img\\invite_plan_an_order_img\H5小程序活动头图.png")
img_plan_an_order_share_dir = os.path.join(root_dir, r"HQCHIP_Activity\\invite\\img\\invite_plan_an_order_img\\分享海报图片.png")
img_plan_an_order_MiniProgram_share_dir = os.path.join(root_dir, r"HQCHIP_Activity\\invite\\img\\invite_plan_an_order_img\\小程序分享图.png")
img_plan_an_order_newusers_dir = os.path.join(root_dir, r"HQCHIP_Activity\\invite\\img\\invite_plan_an_order_img\\活动奖品(被邀请人领取)-IC新客.png")



# 海报图片路径
poseter_img_dir = os.path.join(root_dir, r"huaqiu_order_api\\HQCHIP_Activity\\poster\\poseter.png")

# 折扣商品文件路径
discount_dir = os.path.join(root_dir, r"huaqiu_order_api\\HQCHIP_Activity\\discount\\discount.csv")

#运费促销库存商品文件路径
freight_goods_dir = os.path.join(root_dir, r"huaqiu_order_api\\HQCHIP_Activity\\freight\\freight_goods.csv")
#运费促销人群包文件路径
freight_people_dir = os.path.join(root_dir, r"huaqiu_order_api\\HQCHIP_Activity\\freight\\freight_people.csv")
# 兑换码文件
clear_redis_cache_dir = os.path.join(root_dir, r"HQCHIP_Activity\\redemption\\uid.csv")
redemption_code_password_dir = os.path.join(root_dir, r"HQCHIP_Activity\\redemption\\redemption_code_password.csv")
# 热搜词文件
# clear_redis_cache_dir = os.path.join(root_dir, r"HQCHIP_Activity\\redemption\\uid.csv")
hot_word_icon_dir = os.path.join(root_dir, r"HQCHIP_Activity\\hotSearchword\\icon.png")

# 活动测试相关文件
reconstruction_project_dir = os.path.join(root_dir, r"reconstruction_project")
munihei_user_dir = os.path.join(reconstruction_project_dir, r"预发布芯城用id.xlsx")
# 合作商相关文件
partner_dir = os.path.join(root_dir,"HQCHIP_SRM")
partner_potential_apply_import_dir = os.path.join(partner_dir, r"partner_settle\\apply_import.png")
settle_goods_dir = os.path.join(partner_dir, r"settle_goods_bill\\渠道员-现货发布模版.xlsx")
# 组织架构相关文件
auth_dir = os.path.join(root_dir, r"HQCHIP_SOO")
auth_users_test_dir = os.path.join(auth_dir, r"Excel\\users_test.xlsx")
auth_users_formal_dir = os.path.join(auth_dir, r"Excel\\users_formal.xlsx")

# ERP 相关文件
ERP_dir = os.path.join(root_dir, r"HQCHIP_ERP")
smt_order_bom_import_dir = os.path.join(ERP_dir, r"生产BOM模板.xlsx")

# SMT 相关文件
smt_file_dir = os.path.join(root_dir, r"HQSMT")
smt_yansuo_dir = os.path.join(smt_file_dir, r"yansuo.zip")

# PCB相关文件
PCB_file_dir = os.path.join(root_dir, r"HQPCB")
pcb_config_yaml_dir = os.path.join(PCB_file_dir, r"pcb_config.yaml")

# 密码加密js文件
encryption_dir = os.path.join(os.path.join(root_dir, r"SSO_Reception"), r"passwordEncrypt.js")
encryption_auth_dir = os.path.join(os.path.join(root_dir, r"HQCHIP_SOO"), r"passwordJsEncrypt.js")
# 订单敏感信息加密JS文件
encryption_order_dir = os.path.join(os.path.join(root_dir, r"SSO_Reception"), r"orderSensitiveMsgJsEncrypt.js")
# 订单敏感信息加密JS文件
encryption_order_new_dir = os.path.join(os.path.join(root_dir, r"SSO_Reception"), r"orderSensitiveMsgJsEncrypt_new.js")

# PCBAMES相关文件
PCBAMES_file_dir = os.path.join(smt_file_dir, r"HQMES_new\\首件检验.png")
#  sql 批量写入原始文件
excel_create_sql_ai_inquiry_dir = os.path.join(root_dir, r"help_oneself_tool\\sql_create\\EXCEL_DATA\\AI询价销售天数数据.xlsx")
#  sql 批量写入生成文件
excel_create_sql_ai_inquiry_dir_sql = os.path.join(root_dir, r"help_oneself_tool\\sql_create\\EXCEL_DATA\\ai_inquiry_sql.sql")

# Zentao禅道写入
cookie_dir = os.path.join(root_dir, r"HQCHIP_Zentao\\Zentao_cookie.txt")
# Zentao禅道写入
ehr_cookie_dir = os.path.join(root_dir, r"HQCHIP_EHR\\Attendance_statistics‌\\cookie.txt")
# ui测试
uiTest_img_dir = os.path.join(root_dir, r"HQCHIP_UITest\\Img")
uiTest_img_2018 = os.path.join(uiTest_img_dir, r"hc2018")
uiTest_img_hqchip = os.path.join(uiTest_img_dir, r"hqchip")
uiTest_img_hqchip_suess = os.path.join(uiTest_img_hqchip, r"hqchip_suess")
uiTest_img_hqchip_full = os.path.join(uiTest_img_hqchip, r"hqchip_full")


if __name__ == '__main__':
    # a = conf_ini
    # print(config_path)
    print(encryptConfYaml_dir)
    # b = config_dir
    # print(logo_files, logo_txts)
    print(dos_consignment_launch_dir)
    file_name = os.path.basename(dos_consignment_launch_dir)
    print(encryption_auth_dir)

    print(ehr_cookie_dir)
    # c = root_dir
    # print(c)
    # d = log_dir
    # print(d)
    # e = log_dir
    # print(e)