import base64
import json
import os
import random
import time
from datetime import datetime, timedelta
from urllib.parse import quote
from xpinyin import Pinyin
import jsonpath
import yaml

from huaqiu_order_api.HQCHIP_SOO.login import SOOLogin
from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_data import Data
from huaqiu_order_api.common.my_path import yaml_file, subject_one_img_dir, \
    subject_order_now_dir, subject_form_submit_dir, subject_more_img3_dir, subject_more_img3_icon_left_dir, \
    subject_more_img3_icon_right_dir, subject_more_HandleImg1_dir, subject_more_HandleImg1_icon_right_dir, \
    subject_more_TextAndImage_dir, subject_more_TextAndImage_icon_right_dir, subject_more_Images2_dir, \
    subject_more_Images2_icon_right_dir, subject_more_Images3_dir, subject_more_Images3_icon_right_dir, \
    subject_more_Images4_dir, subject_more_Images4_icon_right_dir, subject_more_img2_dir, \
    subject_more_img2_icon_right_dir, subject_more_Aspect1_dir, subject_more_Aspect1_icon_right_dir, \
    subject_more_Aspect1_button_dir, subject_more_banner_txts, subject_more_Pendant_dir, subject_more_img_dir, \
    subject_NavBar_main_icon_dir, subject_NavBar_button_review_icon_dir, subject_NavBar_button_enroll_icon_dir, \
    subject_orderSalesRanking_dir, subject_Sign_dir, subject_Register_dir


class HqshopSubject:
    def __init__(self, target_rss=None, activity_id=None, shopThemat_id=None, thematicName=None, finishedRedirectUrl=None,
                 appSite=None, client=None, topicStatus=None, templateId=None,  module_name_list=None):
        """
        :param activity_id 活动id
        :param shopThemat_id 专题id
        :param thematicName 专题名称
        :param finishedRedirectUrl 专题结束跳转URL
        :param appSite 站点 1 华秋商城 2 华秋电路 3 华秋智造 4 电子发烧友
        :param client 平台  1 pc 2 移动端
        :param topicStatus 专题状态  0草稿（存储） 1发布
        :param templateId 模板id 0不引用模板 1品牌专区模板(一) 2双十一专题模板 3慕尼黑专题模板 4大会主页模板 5展台看点模板 6大会报道模板 7大会回顾模板
        :param module_name_list 组件列表
        """
        self.activity_rss = target_rss
        self.json_head = {"Content-Type": "application/json",
                          "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                          }
        self.headers_urlencoded = {"Content-Type": "application/x-www-form-urlencoded",}
        self.activity_id = activity_id
        self.shopThemat_id = shopThemat_id
        self.thematicName = thematicName
        self.finishedRedirectUrl = finishedRedirectUrl
        self.appSite = appSite
        self.client = client
        self.topicStatus = topicStatus
        self.templateId = templateId
        self.module_name_list = module_name_list
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data['Activity_Center_URL']
        self.HQCHIP_URL = data['HQCHIP_URL']
        self.SMT_HQCHIP = self.HQCHIP_URL.replace("www", "smt")
        self.HQPCB_URL = data['HQPCB_URL']
        self.ELECFANS_URL = data['ELECFANS_URL']
        if (self.finishedRedirectUrl == "" and self.appSite != None) or (self.finishedRedirectUrl == None and self.appSite != None):
            appSite_finishedRedirectUrl_json = {1: self.HQCHIP_URL, 2: self.SMT_HQCHIP, 3: self.HQPCB_URL, 4: self.ELECFANS_URL}
            for i, v in appSite_finishedRedirectUrl_json.items():
                if i == int(self.appSite):
                    self.finishedRedirectUrl = v

    def hqshop_subject_add(self):
        """
        创建专题页面
        :param thematicName 专题名称
        :param finishedRedirectUrl 专题结束跳转URL
        :param appSite 站点 1 华秋商城 2 华秋电路 3 华秋智造 4 电子发烧友
        :param client 平台  1 pc 2 移动端
        """
        now_time_ten_minutes = str((datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间10分钟后的时间：{now_time_ten_minutes}")
        time.sleep(1)
        now_time_one_day = str((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一天后的时间：{now_time_one_day}")
        # 专题名称拼音
        urlKey = Pinyin().get_pinyin(self.thematicName, "")
        add_subject_url = "{}/ecmc/shop/addSubject".format(self.Activity_Center_URL)
        add_subject_body = {"shopActivityId": self.activity_id, "shopActivityStartTime": now_time_ten_minutes, "shopActivityEndTime": now_time_one_day,
                            "thematicName": self.thematicName, "finishedRedirectUrl": self.finishedRedirectUrl, "appSite": self.appSite, "client": self.client, "language": 1,
                            "seoTitle": "自动化测试", "seoKeyword": "自动化测试", "seoIntro": "自动化测试", "urlKey": urlKey, "tmpId":123
                            }
        logger.info(add_subject_body)
        add_subject_res = self.activity_rss.post(url=add_subject_url, json=add_subject_body, headers=self.json_head).json()
        logger.info(add_subject_res)
        self.shopThemat_id = add_subject_res["result"]["id"]
        logger.info(f"获取到生成的专题id：{self.shopThemat_id}")
        return self


    def hqshop_subject_assembly_file_add(self, img_dir):
        files_name = img_dir.split('\\')[-1]
        assembly_file_url = "{}/ecmc/upload/uploadFile".format(self.Activity_Center_URL)
        file = [('file', (files_name, open(img_dir, 'rb'),'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
        assembly_file_res = self.activity_rss.post(url=assembly_file_url, files=file).json()
        # print(assembly_file_res)
        img_url = jsonpath.jsonpath(assembly_file_res, "$..url")[0]
        return img_url
    def upload_all_images_in_dir(self, img_dir, upload_func):
        """
        遍历目录下所有文件，依次执行上传函数，返回 url 列表
        :param img_dir: 图片所在目录路径
        :param upload_func: 上传函数，接受图片完整路径，返回 img_url
        :return: img_url 列表
        """
        img_urls = []
        # 支持的图片扩展名
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
        # 获取目录下所有文件（不递归子目录）
        for filename in os.listdir(img_dir):
            # 检查扩展名是否为图片
            ext = os.path.splitext(filename)[1].lower()
            if ext not in image_extensions:
                continue  # 跳过 __init__.py 等非图片文件
            file_path = os.path.join(img_dir, filename)
            # print(file_path)
            # 只处理文件，跳过子目录
            if os.path.isfile(file_path):
                # 调用上传函数，获取 url
                url = upload_func(file_path)

                # print(url)
                img_urls.append(url)
        return img_urls

    def hqshop_subject_coupon(self, couponType=None):
        """优惠券接口"""

        coupon_url = "{}/ecmc/common/getOngoingAndWillCouponList".format(self.Activity_Center_URL)
        coupon_body = {"pageNum": 1, "pageSize": 20, "couponType": couponType}
        coupon_res = self.activity_rss.post(url=coupon_url, json=coupon_body).json()
        coupon_list = jsonpath.jsonpath(coupon_res, "$..couponId")
        coupon_name_list = jsonpath.jsonpath(coupon_res, "$..name")
        coupon_list_new = []
        for i in range(len(coupon_list)):
            if coupon_name_list[i] == "自动化--专题测试-优惠券":
                coupon_list_new.append(coupon_list[i])
        coupon_id_collect_str = ','.join(coupon_list_new)
        print(coupon_id_collect_str)
        return coupon_id_collect_str
    def img_base64(self,img_dir):
        """图片转成base64"""
        encoded = str(base64.b64encode(open(img_dir, 'rb').read()),'utf-8')
        print("source_data:image/png;base64,"+encoded)
        # logger.info(f"图片{img_dir}转译成base64格式：{encoded}")
        # open('1.txt', 'wb').write(encoded)



    def hqshop_subject_topicfrom(self):
        """表单接口"""
        topicfrom_url = "{}/ecmc/shop/topicFormList".format(self.Activity_Center_URL)
        topicfrom_body = {"pageNum": 1, "pageSize": 20}
        topicfrom_res = self.activity_rss.post(url=topicfrom_url, json=topicfrom_body, headers=self.json_head).json()
        topicfrom_id = jsonpath.jsonpath(topicfrom_res, "$..id")[0]
        action = jsonpath.jsonpath(topicfrom_res, "$..action")[0]
        return action, topicfrom_id


    def hqshop_subject_elecfans_taglist(self,tags_name):
        """发烧友文章接口"""

        # url的中文转译
        url_encode_name = quote(tags_name)
        logger.info(f"转译传入中文参数{tags_name}为：{url_encode_name }")
        taglist_url = f"https://uat-www.elecfans.com/webapi/index.php?s=/Home/News/getAi2020News&p=1&tags={url_encode_name}"
        res = self.activity_rss.get(url=taglist_url, headers=self.json_head).json()
        logger.info(res)

    def hqshop_subject_discountActivity_list(self):
        """折扣活动获取"""
        discountActivity_url = "{}/ecmc/common/getOngoingAndWillActivityList".format(self.Activity_Center_URL)
        discountActivity_body = {"activityType": [2, 3]}
        discountActivity_res = self.activity_rss.post(url=discountActivity_url, json=discountActivity_body).json()
        activityId_list = jsonpath.jsonpath(discountActivity_res, "$..id")
        # activityId_collect_str = ','.join(activityId_list)
        # print(activityId_collect_str)
        return activityId_list

    def hqshop_subject_registerActivity_list(self, activity_name=None):
        registerActivity_url = "{}/ecmc/activitySignUp/relationList".format(self.Activity_Center_URL)
        registerActivity_body = {"pageNum": 1, "pageSize": 50, "activityStatusValue": -1}
        registerActivity_res = self.activity_rss.post(url=registerActivity_url, json=registerActivity_body).json()
        activityId_list = jsonpath.jsonpath(registerActivity_res, "$..activityId")
        activityName_list = jsonpath.jsonpath(registerActivity_res, "$..activityName")

        # 若两个列表无效，返回 None
        if not isinstance(activityId_list, list) or not isinstance(activityName_list, list):
            return None,None

        # 情况1：未传入 activity_name，返回第一个 activityId
        if activity_name is None:
            return activityId_list[0] if activityId_list else None, activityName_list[0] if activityName_list else None

        # 情况2：传入 activity_name，查找匹配的 activityId（取第一个匹配）
        for act_id, act_name in zip(activityId_list, activityName_list):
            if act_name == activity_name:
                return act_id, act_name

        # 未找到匹配的名称，返回 None
        return None,None
    def hqshop_subject_sampleGoods(self):
        """样品获取"""
        sampleGoods_url = "{}/ecmc/common/getSampleList".format(self.Activity_Center_URL)
        sampleGoods_body = {"pageNum": 1, "pageSize": 50}
        sampleGoods_res = self.activity_rss.post(url=sampleGoods_url, json=sampleGoods_body).json()
        total = jsonpath.jsonpath(sampleGoods_res, "$..total")[0]
        total_num = int(total) / 50
        sampleGoods_id_count = []
        if total_num > 1:
            for i in range(int(total_num)):
                sampleGoods_body = {"pageNum": i+1, "pageSize": 50}
                sampleGoods_res = self.activity_rss.post(url=sampleGoods_url, json=sampleGoods_body).json()
                sampleGoods_list = jsonpath.jsonpath(sampleGoods_res, "$..id")
                sampleGoods_id_count = sampleGoods_id_count + sampleGoods_list
        else:
            sampleGoods_id_count = jsonpath.jsonpath(sampleGoods_res, "$..id")
        return sampleGoods_id_count




    def hqshop_subject_detail(self):
        """专题组件详情页"""
        # self.subject_id = 314
        detail_url = "{}/ecmc/shop/subjectPageDetail".format(self.Activity_Center_URL)
        detail_body = {"shopThematicId": self.shopThemat_id}
        detail_subject_res = self.activity_rss.post(url=detail_url, json=detail_body, headers=self.json_head).json()
        # logger.info(detail_subject_res)
        self.detail_edit_body = detail_subject_res["result"]
        return self.detail_edit_body
    def dict_module_cearte(self, name=None):
        global p
        moduleInfo = [{"editModule": "ImageEdit", "module": "settingInfo", "name": "设置模块", "index": 0, "formData": [{"code": "color", "value": "#f5f5f5"}]}]
        # 组件类别：
        module_name_json = {
            "单张图片": "Image",
            "滑动式单图": "Banner",
            "多张图片": "Images",
            "文字": "RichText",
            "导航菜单(一)": "NavBar",
            "分享组件": "Share",
            "超级文本": "Hypertext",
            "虚拟浏览": "VirtualBrowsing",
            "左文右图": "TextAndImage",
            "图片组件2": "Images2",
            "图片组件3": "Images3",
            "图片组件4": "Images4",
            "文章组件1": "Article1",
            "多张图片2": "MultiGraph2",
            "多张图片3": "MultiGraph3",
            "交互图片组件1": "HandleImg1",
            "挂件组件": "Pendant",
            "通栏图片": "FullColumn",
            "看点组件1": "Aspect1",
            "表单组件": "FormElement",
            "PCB-快捷下单样式(一)": "QuickOrder",
            "优惠券": "Coupon",
            "热门推荐": "Best",
            "样品组件": "Sample",
            "商品列表": "GoodsList",
            "排行榜（一）": "orderSalesRanking",
            "注册组件（一）": "Sign",
            "报名组件(普通版)": "Register",
            "抽奖转盘": "Lottery"
        }
        module = ""
        if not isinstance(name, list):
            name = [name]
        else:
            name = name
        for i in name:
            if i == "None":
                name = random.choice(list(module_name_json.keys()))
                print(name)
                module = module_name_json[name]

            else:
                for k in module_name_json:
                    if k == i:
                        module = module_name_json[k]
            if module == "Lottery":
                module_data_json = {"editModule": module + "Edit", "module": module, "name": i}
            else:
                module_data_json = {"editModule": module + "Edit", "module": module, "name": i, "previewImg": module,"tagImage": module}
            formData = []
            if module == "Coupon":
                coupon_id_str = self.hqshop_subject_coupon()
                # 选择优惠券
                coupon_pattern_title_json = {1: "优惠券样式一", 2: "优惠券样式二", 3: "优惠券样式三", 4: "优惠券样式四"}
                # 选择优惠券
                pattern_id = 1
                title = None
                for p, t in coupon_pattern_title_json.items():
                    if p == pattern_id:
                        title = t
                        break
                    if pattern_id == None:
                        p = 1
                        title = coupon_pattern_title_json[p]
                        break
                couponInfo = {}
                couponList = {}
                # print("coupon_id_str: ", coupon_id_str)
                if coupon_id_str != None and coupon_id_str != '':
                    couponInfo = {"code": module.lower() + "Info",
                                  "value": {"bgInfo": {"bgColor": "#ffffff", "bgImgUrl": "", "showType": 1},
                                            "moreUrl": "{}/act/coupon.html".format(self.HQCHIP_URL),
                                            "styleType": p,
                                            "title": title,
                                            "titleInfo": {"defaultTitleIcon": "", "color": "#ffffff", "bolder": False,
                                                          "titleAlign": "left", "rightTitleIcon": ""}
                                            }}
                    couponList = {"code": module.lower() + "List"}
                    coupon_list = []
                    coupon_value = []
                    coupon_id_lst = coupon_id_str.split(',')
                    # print("coupon_id_lst: ", coupon_id_lst)
                    for k in coupon_id_lst:
                        coupon_list.append({"detailUrl": "", "couponId": k})
                        coupon_value.append({"couponId": k})
                    # print("coupon_list: ", coupon_list)
                    print("coupon_value: ", coupon_value)
                    couponList["couponList"] = coupon_list
                    couponList["value"] = coupon_value
                if couponInfo != {}:
                    formData.append(couponInfo)
                if couponList != {}:
                    formData.append(couponList)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb"]
                # print(json.dumps(module_data_json, ensure_ascii=False).replace("'", '"'))
            elif module == "Image":
                img_url = self.hqshop_subject_assembly_file_add(subject_one_img_dir)
                oneImgInfo = {"code": module,
                              "value": {"formModel": "", "imagePath": img_url, "url": "{}/act/new.html".format(self.HQCHIP_URL)}}
                formData.append(oneImgInfo)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "Banner":
                img_url = self.hqshop_subject_assembly_file_add(subject_one_img_dir)
                slideImgInfo = {"code": module.lower() + "List", "value": [{"url": "{}/act/new.html".format(self.HQCHIP_URL), "imagePath": img_url, "index": 0}]}
                formData.append(slideImgInfo)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "Best":
                activity_id = self.hqshop_subject_discountActivity_list()
                module_data_json["editModule"] = "Goods" + module + "Edit"
                # 选择样式
                hotGoods_pattern_title_json = {1: "热门推荐样式一", 2: "热门推荐样式二"}
                # 选择样式
                pattern_id = 1
                title = None
                for p, t in hotGoods_pattern_title_json.items():
                    if p == pattern_id:
                        title = t
                        break
                    if pattern_id == None:
                        p = 1
                        title = hotGoods_pattern_title_json[p]
                        break
                hotGoodsInfo = {"code": "hotGoodsInfo",
                            "value": {
                                "styleType": p,
                                "titleInfo": {"defaultTitleIcon": "", "color": "#ffffff", "bolder": False, "titleAlign": "left", "rightTitleIcon": ""},
                                "bgInfo": {"bgColor": "#ffffff", "bgImgUrl": "", "showType": 1},
                                "title": title,
                                "moreUrl": "{}/app".format(self.HQCHIP_URL)}
                                }
                hotGoodsList = {"code": "hotGoods" + "List"}
                if activity_id != None:
                    hotGoodsList['value'] = [{"activityId": activity_id, "brandName": [], "goodsId": [], "filePath": "", "brandId": [], "cat": "", "type": 3}]
                formData.append(hotGoodsInfo)
                formData.append(hotGoodsList)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb"]
            elif module == "Sample":
                sample_goods_id = self.hqshop_subject_sampleGoods()
                # 选择样式
                sample_pattern_title_json = {1: "样品样式一", 2: "样品样式二"}
                # 选择样式
                pattern_id = 1
                title = None
                for p, t in sample_pattern_title_json.items():
                    if p == pattern_id:
                        title = t
                        break
                    if pattern_id == None:
                        p = 1
                        title = sample_pattern_title_json[p]
                        break
                sampleInfo = {"code": module + "Info",
                            "value": {"styleType": p,
                            "titleInfo": {"defaultTitleIcon": "", "color": "#ffffff", "bolder": False, "titleAlign": "left", "rightTitleIcon": ""},
                            "bgInfo": {"bgColor": "#ffffff", "bgImgUrl": "", "showType": 1},
                            "title": title,
                            "moreUrl": "{}/sample.html".format(self.HQCHIP_URL)}}
                sampleList = {"code": module + "List"}
                sample_goods_list = []
                for k in sample_goods_id:
                    sample_goods_list.append({"sampleId": k})
                sampleList["value"] = sample_goods_list
                formData.append(sampleInfo)
                formData.append(sampleList)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb"]
            elif module == "GoodsList":
                activity_id = self.hqshop_subject_discountActivity_list()
                GoodsList_pattern_title_json = {1: "商品列表样式一", 2: "商品列表样式二"}
                # 选择样式
                pattern_id = 1
                title = None
                for p, t in GoodsList_pattern_title_json.items():
                    if p == pattern_id:
                        title = t
                        break
                    if pattern_id == None:
                        p = 1
                        title = GoodsList_pattern_title_json[p]
                        break
                goodsListInfo = {"code": "goodsListInfo",
                            "value": {"styleType": p,
                            "titleInfo": {"defaultTitleIcon": "", "color": "#ffffff", "bolder": False, "titleAlign": "left", "rightTitleIcon": ""},
                            "bgInfo": {"bgColor": "#ffffff", "bgImgUrl": "", "showType": 1},
                            "title": title,
                            "moreUrl": "{}/app".format(self.HQCHIP_URL)}}
                goodsList = {"code": "goods" + "List"}
                if activity_id != None:
                    goodsList['value'] = [{"activityId": activity_id, "brandName": [], "goodsId": [], "filePath": "", "brandId": [], "cat": "", "type": 3}]
                formData.append(goodsListInfo)
                formData.append(goodsList)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb"]
            elif module == "QuickOrder":
                img_url = self.hqshop_subject_assembly_file_add(subject_order_now_dir)
                QuickOrder_pattern_title_json = {1: "PCB-快捷下单样式(一)", 2: "PCB-快捷下单样式(二)"}
                # 选择样式
                pattern_id = 1
                title = None
                for p, t in QuickOrder_pattern_title_json.items():
                    if p == pattern_id:
                        title = t
                        break
                    if pattern_id == None:
                        p = 1
                        title = QuickOrder_pattern_title_json[p]
                        break
                QuickOrderInfo = {"code": module,
                                  "value": {
                                      "styleType": p,
                                      "titleInfo": {"defaultTitleIcon": "", "color": "#ffffff", "bolder": False, "titleAlign": "left", "rightTitleIcon": ""},
                                      "bgInfo": {"bgColor": "#ffffff", "bgImgUrl": "", "showType": 1},
                                      "title": title,
                                      "orderInfo": {"boardNum": None, "btnUrl": img_url, "max": None, "min": None,
                                                    "plies": None, "priorityShow": None, "type": 1}
                                  }}
                formData.append(QuickOrderInfo)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "FormElement":
                action, topicfrom_id = self.hqshop_subject_topicfrom()
                img_url = self.hqshop_subject_assembly_file_add(subject_form_submit_dir)
                FormElementInfo = {"code": module,
                                  "value": {
                                      "beforeTextContent": "<p>表单</p>",
                                      "textContent": "<p>提交表单成功</p>",
                                      "btnEl": img_url,
                                      "titleInfo": {"iconUrl": "", "color": "#260C0C", "bolder": False, "text": "表单测试"},
                                      "bgInfo": {"bgColor": "#1C63BB", "bgImgUrl": "", "showType": 2},
                                      "subheadInfo": {"color": "#260C0C", "bolder": False, "text": "表单测试-副"},
                                      "formInfo": {"action": action, "id": topicfrom_id, "isLogin": 1}
                                  }}
                formData.append(FormElementInfo)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "RichText":
                RichTextInfo = {"code": module + "Info", "value": "<p>自动化测试</p>"}
                formData.append(RichTextInfo)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "Share":
                ShareInfo = {"code": module,
                             "value": {
                                 "bgInfo": {"bgColor": "#459ACF", "bgImgUrl": "", "showType": 2},
                                 "shareColor": "#ffffff"}}
                formData.append(ShareInfo)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "Images":
                # 移除 tagImage、previewImg
                module_data_json.pop('tagImage')
                module_data_json.pop('previewImg')
                img_url = self.hqshop_subject_assembly_file_add(subject_more_img_dir)
                QuickOrder_pattern_title_json = {"TextImages": "大", "Images": "小"}
                # 选择样式
                pattern_type = "TextImages"
                title = None
                for p, t in QuickOrder_pattern_title_json.items():
                    if p == pattern_type:
                        title = t
                        break
                    if pattern_type == None:
                        p = "TextImages"
                        title = QuickOrder_pattern_title_json[p]
                        break
                if p == "TextImages":
                    module_data_json["module"] = "TextImages"
                ImagesInfo = {"code": module.lower() + "Info",
                              "value": {"moreUrl": "{}/app".format(self.HQCHIP_URL), "title": "多张图片-" + title}}
                ImagesList = {"code": module.lower() + "List"}
                valueInfo = []
                for i in range(1, 9):
                    k = {"imagePath": img_url, "index": i, "url": "{}/app".format(self.HQCHIP_URL)}
                    if p == "TextImages":
                        k["bigTitle"] = "多张图片" + str(i)
                        k["smallTitle"] = "多张图片" + str(i) + "-副"
                    valueInfo.append(k)
                ImagesList["value"] = valueInfo
                formData.append(ImagesInfo)
                formData.append(ImagesList)
                module_data_json["formData"] = formData
                # module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "VirtualBrowsing":
                title = ["页面浏览量", "报名人数", "观看人数"]
                itemList = []
                for i in title:
                    k = {"count": 10000, "countStyle": {"bolder": False, "color": "#ffffff"}, "title": i, "titleStyle": {"bolder": False, "color": "#ffffff"}}
                    itemList.append(k)
                VirtualBrowsingInfo = {"code": module,
                                      "value": {
                                          "bgInfo": {"bgColor": "#3559C5", "bgImgUrl": "", "showType": 2},
                                          "itemList": itemList}}
                formData.append(VirtualBrowsingInfo)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "Hypertext":
                HypertextInfo = {"code": module,
                                  "value": {
                                      "bgInfo": {"bgColor": "#BDE1FE", "bgImgUrl": "", "showType": 2},
                                      "textContent": "<p><span style=\"font-size: 18px;\"><strong>活动说明："
                                                   "</strong></span></p>\n<p>1）元器件【华秋自营满减券】 &nbsp;满1000-40元、满330-25元仅限全场元器件华秋自营库存使用，不含运费，每个客户限领1张，领取后30天内有效；"
                                                   "</p>\n<p>2）订单累计金额满足门槛即可使用；"
                                                   "</p>\n<p>3）法律允许范围内，本次活动未尽事宜和最终解释权归华秋商城所有。"
                                                   "</p>\n<p>4）活动时间：xx月xx日&mdash;xx月xx日</p>"
                                  }}
                formData.append(HypertextInfo)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "Images2":
                img_url = self.hqshop_subject_assembly_file_add(subject_more_Images2_dir)
                img_icon_right_url = self.hqshop_subject_assembly_file_add(subject_more_Images2_icon_right_dir)
                Images2Info = {"code": module,
                                      "value": {"bgInfo": {"bgColor": "#1C0E3C", "bgImgUrl": "", "showType": 2},
                                                "subheadInfo": {"bolder": False, "color": "#ffffff", "text": "XIANCHANGHUIGU"},
                                                "titleInfo": {"bolder": False, "color": "#ffffff", "iconUrl": img_icon_right_url, "text": "现场回顾"},

                                           }}
                imgList = []
                for i in range(20):
                    k = {"imgUrl": img_url, "showType": 1, "smallTitle": "", "videoBgUrl": "",
                         "videoTitle": 1, "videoUrl": "",
                         "jumpInfo": {"anchor": "", "jumpType": 1, "url": "",
                                      "formInfo": {"action": "", "id": "", "isLogin": 0}}}
                    imgList.append(k)
                Images2Info["value"]["mediaList"] = imgList
                formData.append(Images2Info)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "Images3":
                img_url = self.hqshop_subject_assembly_file_add(subject_more_Images3_dir)
                img_icon_right_url = self.hqshop_subject_assembly_file_add(subject_more_Images3_icon_right_dir)
                Images3Info = {"code": module,
                                      "value": {"bgInfo": {"bgColor": "#1C0E3C", "bgImgUrl": "", "showType": 2},
                                                "subheadInfo": {"bolder": False, "color": "#ffffff", "text": "YANJIANGJIABIN"},
                                                "titleInfo": {"bolder": False,"iconUrl": img_icon_right_url, "text": "演讲嘉宾",
                                                               "color": "#ffffff", "showType": 1},
                                                "smallTitleStyle": {"bolder": False, "color": "#ffffff"},
                                                "textBg": {"bolder": False, "bgColor": "#412A76", "bgImgUrl": "","showType": 2},
                                                "titleStyle": {"bolder": False, "color": "#ffffff"}
                                           }}
                imgList = []
                for i in range(20):
                    k = {"imgUrl": img_url, "showType": 1, "smallTitle": "Qorvo 电机与电源应用部门经理", "title": "Calvin Li",
                         "videoBgUrl": "", "videoTitle": 1, "videoUrl": "",
                         "jumpInfo": {"anchor": "", "jumpType": 1, "url": "", "formInfo": {"action": "", "id": "", "isLogin": 0}}}
                    imgList.append(k)
                Images3Info["value"]["mediaList"] = imgList
                formData.append(Images3Info)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "Images4":
                img_url = self.hqshop_subject_assembly_file_add(subject_more_Images4_dir)
                img_icon_right_url = self.hqshop_subject_assembly_file_add(subject_more_Images4_icon_right_dir)
                Images4Info = {"code": module,
                                      "value": {"bgInfo": {"bgColor": "#1C0E3C", "bgImgUrl": "", "showType": 2},
                                                "subheadInfo": {"bolder": False, "color": "#ffffff", "text": "XIANCHANGZHAOPIAN"},
                                                "titleInfo": {"bolder": False,"iconUrl": img_icon_right_url, "text": "现场照片-向下展开",
                                                               "color": "#ffffff", "showType": 1},
                                                "smallTitleStyle": {"bolder": False, "color": "#ffffff"},
                                                "textBg": {"bolder": False, "bgColor": "#1E41DA", "bgImgUrl": "","showType": 2},
                                                "titleStyle": {"bolder": False, "color": "#ffffff"},
                                                "interactionType": 2 # 2: 向下展开 1: 横向轮播
                                           }}
                imgList = []
                for i in range(21):
                    k = {"imgUrl": img_url, "showType": 1, "smallTitle": "Qorvo 电机与电源应用部门经理", "title": "Calvin Li",
                         "videoBgUrl": "", "videoTitle": "", "videoUrl": "", "pdfUrl": "",
                         "jumpInfo": {"anchor": "", "jumpType": 1, "url": "", "formInfo": {"action": "", "id": "", "isLogin": 0}},
                         "downloadTextInfo": {"bolder": False, "color": "", "text": ""}}
                    imgList.append(k)
                Images4Info["value"]["mediaList"] = imgList
                formData.append(Images4Info)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "MultiGraph2":
                img_url = self.hqshop_subject_assembly_file_add(subject_more_img2_dir)
                img_icon_right_url = self.hqshop_subject_assembly_file_add(subject_more_img2_icon_right_dir)
                MultiGraph2Info = {"code": module,
                                      "value": {"bgInfo": {"bgColor": "#1C0E3C", "bgImgUrl": "", "showType": 2},
                                                "subheadInfo": {"bolder": False, "color": "#ffffff", "text": "CHANGSHANGZHANSHI"},
                                                "titleInfo": {"bolder": False,"iconUrl": img_icon_right_url, "text": "现场照片-横向轮播",
                                                               "color": "#ffffff", "showType": 1},
                                                "smallTitleInfo": {"bolder": False, "color": "#ffffff", "text": "合作厂商"},
                                                "interactionType": 1 # 2: 向下展开 1: 横向轮播
                                           }}
                imgList = []
                for i in range(21):
                    k = {"imgUrl": img_url,
                         "jumpInfo": {"anchor": "", "jumpType": 1, "url": "",
                                      "formInfo": {"action": "", "id": "", "isLogin": 0}}}
                    imgList.append(k)
                MultiGraph2Info["value"]["mediaList"] = imgList
                formData.append(MultiGraph2Info)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "MultiGraph3":
                img_url = self.hqshop_subject_assembly_file_add(subject_more_img3_dir)
                img_icon_left_url = self.hqshop_subject_assembly_file_add(subject_more_img3_icon_left_dir)
                img_icon_right_url = self.hqshop_subject_assembly_file_add(subject_more_img3_icon_right_dir)
                MultiGraph3_pattern_title_json = {1: "大", 2: "小"}
                # 选择样式
                pattern_id = 1
                title = None
                for p, t in MultiGraph3_pattern_title_json.items():
                    if p == pattern_id:
                        title = t
                        break
                    if pattern_id == None:
                        p = 1
                        title = MultiGraph3_pattern_title_json[p]
                        break
                MultiGraph3Info = {"code": module,
                              "value": {"moreUrl": "{}/app".format(self.HQCHIP_URL), "title": "多张图片3-" + title,
                                        "bgInfo": {"bgColor": "#BDE1FE", "bgImgUrl": "", "showType": 1},
                                        "imgSizeType": p,
                                        "titleInfo": {"bolder": False, "color": "#110202", "titleAlign": "center",
                                                      "rightTitleIcon": img_icon_left_url, "defaultTitleIcon": img_icon_right_url}
                                        }}
                MultiGraph3List = []
                for i in range(1, 9):
                    k = {"imagePath": img_url, "url": "{}/app".format(self.HQCHIP_URL), "imgUrl": img_url,
                         "bigTitle": "多张图片3-" + str(i), "smallTitle": "多张图片3-" + str(i) + "-副",
                         "jumpInfo": {"anchor": "", "jumpType": 6, "url": "{}/app".format(self.HQCHIP_URL),
                                      "formInfo": {"action": "", "id": "", "isLogin": 0}}}
                    MultiGraph3List.append(k)
                MultiGraph3Info["value"]["mediaList"] = MultiGraph3List
                formData.append(MultiGraph3Info)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "TextAndImage":
                img_url = self.hqshop_subject_assembly_file_add(subject_more_TextAndImage_dir)
                img_icon_right_url = self.hqshop_subject_assembly_file_add(subject_more_TextAndImage_icon_right_dir)
                TextAndImageInfo = {"code": module,
                                    "value": {
                                        "bgInfo": {"bgColor": "#1C0E3C", "bgImgUrl": "", "showType": 1},
                                         "subheadInfo": {"bolder": False, "color": "#ffffff", "text": "HUODONGGAIYAO"},
                                         "titleInfo": {"bolder": False, "color": "#ffffff", "iconUrl": img_icon_right_url, "text": "活动概要"},
                                          "textContent": "<p><span style=\"color: #ffffff; font-size: 16px;\">&nbsp; &nbsp; &nbsp; &nbsp;据Grand View Research统计，2021年全球电机市场的规模为1505亿美元，预计未来几年将会以6.4%左右的年复合增长率增长，到2028年将会达到2325亿美元。按照应用领域划分，电机可分为消费级电机、工业级电机，以及车载电机。据估算，2021年国内电机的市场规模约为740亿元，其中，消费级电机为300亿元、伺服电机为250亿元、新能源汽车电机为140亿元，其他电机约为50亿元。"
                                                         "</span></p>\n<p>&nbsp;</p>\n<p><span style=\"color: #ffffff; font-size: 16px;\">&nbsp; &nbsp; &nbsp; &nbsp;近几年来，国内电机市场规模在不断增大，产量也在不断提升，其实全球大部分的电机都是我国生产的，但主要以中低端电机产品为主，包括罩极电机、异步电机、有刷电机、感应电机、步进电机等等，主要应用于家电、工业，以及办公自动化等领域，而高端电机市场主要以日系、德系品牌为主。随着我国科技技术的进步，国内电机企业也开始逐步向无刷电机、伺服电机等高端电机产品迈进，电机智能化和高效节能化成为我国当前电机行业发展的主要方向。"
                                                         "</span></p>\n<p>&nbsp;</p>\n<p><span style=\"color: #ffffff; font-size: 16px;\">&nbsp; &nbsp; &nbsp; &nbsp;而电机的智能化和高效节能化，离不开上游芯片、传感器、编码器等硬件，以及电机控制软件算法的支持，因此，我们特意举办了此次电机控制先进技术研讨会，提供给广大电机工程师一个资讯和交流平台，帮助工程师提升工作技能。</span></p>"
                                                }}
                imgList = []
                for i in range(2):
                    k = {"imgUrl": img_url, "showType": 1, "smallTitle": "", "title": "", "videoBgUrl": "",
                         "videoTitle": "", "videoUrl": "",
                         "jumpInfo": {"anchor": "", "jumpType": 6, "url": "{}/app".format(self.HQCHIP_URL),
                                      "formInfo": {"action": "", "id": "", "isLogin": 0}}}
                    imgList.append(k)
                    time.sleep(1)
                TextAndImageInfo["value"]["mediaList"] = imgList
                formData.append(TextAndImageInfo)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "HandleImg1":
                img_url = self.hqshop_subject_assembly_file_add(subject_more_HandleImg1_dir)
                img_icon_right_url = self.hqshop_subject_assembly_file_add(subject_more_HandleImg1_icon_right_dir)
                HandleImg1_pattern_title_json = {1: "(1x1通栏)", 2: "(1x1非通栏)", 3: "(2x1)", 4: "(3x1)", 5: "(4x1)"}
                # 选择样式
                pattern_id = 1
                title = None
                for p, t in HandleImg1_pattern_title_json.items():
                    if p == pattern_id:
                        title = t
                        break
                    if pattern_id == None:
                        p = 1
                        title = HandleImg1_pattern_title_json[p]
                        break
                HandleImg1Info = {"code": module,
                                   "value": {"title": "交互图片组件1-" + title, "isTiled": False,
                                             "bgInfo": {"bgColor": "#BDE1FE", "bgImgUrl": "", "showType": 2},
                                             "imgType": p,
                                             "titleInfo": {"bolder": False, "color": "#110202",
                                                           "defaultTitleIcon": img_icon_right_url}
                                             }}
                if p == 1:
                    HandleImg1Info["value"]["isTiled"] = True
                if p >= 2:
                    HandleImg1Info["value"]["imgType"] = p-1
                imgList = []
                if p >= 3:
                    for i in range(2, 5):
                        k = {"imgUrl": img_url, "dataOrigin": 1, "groupCode": "", "groupName": "", "handleType": 1,"roleType": 1,
                             "jumpInfo": {"anchor": "", "jumpType": 6, "url": "{}/app".format(self.HQCHIP_URL),
                                          "formInfo": {"action": "", "id": "", "isLogin": 0}}}
                        imgList.append(k)
                else:
                    k = {"imgUrl": img_url, "dataOrigin": 1, "groupCode": "", "groupName": "", "handleType": 1,
                         "roleType": 1,
                         "jumpInfo": {"anchor": "", "jumpType": 6, "url": "{}/app".format(self.HQCHIP_URL),
                                      "formInfo": {"action": "", "id": "", "isLogin": 0}}}
                    imgList.append(k)
                HandleImg1Info["value"]["imgList"] = imgList
                formData.append(HandleImg1Info)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "Pendant":
                img_url = self.hqshop_subject_assembly_file_add(subject_more_Pendant_dir)
                PendantInfo = {"code": module,
                                   "value": {"imgUrl": img_url,
                                       "jumpInfo": {"anchor": "", "jumpType": 6, "url": "{}/app".format(self.HQCHIP_URL),
                                                    "formInfo": {"action": "", "id": "", "isLogin": 0}}}}
                formData.append(PendantInfo)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "FullColumn":
                FullColumnInfo = {"code": module,
                                   "value": {#"bgInfo": {"bgColor": "#ffffff", "bgImgUrl": "", "showType": 1},
                                   "titleInfo": {"bolder": False, "color": "#ffffff", "text": "", "iconUrl": ""}
                           }}
                imgList = []
                for img_url_dir in subject_more_banner_txts:
                    img_url = self.hqshop_subject_assembly_file_add(img_url_dir)
                    k = {"imgUrl": img_url,
                         "jumpInfo": {"anchor": "", "jumpType": 6, "url": "{}/app".format(self.HQCHIP_URL),
                                      "formInfo": {"action": "", "id": "", "isLogin": 0}}}
                    imgList.append(k)
                FullColumnInfo["value"]["mediaList"] = imgList
                formData.append(FullColumnInfo)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "Aspect1":
                img_url = self.hqshop_subject_assembly_file_add(subject_more_Aspect1_dir)
                img_icon_right_url = self.hqshop_subject_assembly_file_add(subject_more_Aspect1_icon_right_dir)
                img_button_url = self.hqshop_subject_assembly_file_add(subject_more_Aspect1_button_dir)
                Aspect1Info = {"code": module,
                                   "value": {"btnEl": img_button_url,
                                             "bgInfo": {"bgColor": "#1C0E3C", "bgImgUrl": "", "showType": 2},
                                             "subheadInfo": {"bolder": False, "color": "#ffffff", "text": "ZHANTAIKANDIAN"},
                                             "titleInfo": {"bolder": False, "color": "#ffffff", "iconUrl": img_icon_right_url, "text": "展台看点"}
                                             }}
                imgList = []
                for i in range(8):
                    k = {"bgUrl": img_url, "moreUrl":  "https://www.mindmotion.com.cn/", "title": "上海灵动微电子股份有限公司", "text": "",
                         "desc":"上海灵动微电子股份有限公司成立于2011年，是中国本土通用32位MCU产品及解决方案供应商。灵动股份的MCU产品以MM32为标识，基于Arm Cortex-M系列内核....",
                         "contentInfo": {
                                         "videoList": [{"bgUrl": "", "desc": "", "url": ""}],
                                         "classList": [
                                             {
                                                 "name": "MM32SPIN0280",
                                                 "text": "<div class=\"product-box\" data-v-91d8cd9a=\"\">\n<div class=\"product-desc\" data-v-91d8cd9a=\"\">\n<div class=\"window_pop_content window_pop_content7\">\n<div class=\"pop_content_info\">\n<div class=\"pop_content_box\">\n<div class=\"pop_content_nav_item\">\n<div class=\"pop_content_nav_item_left\">\n<h4 data-v-da0de1e7=\"\">应用领域</h4>\n<p>空气净化器、服务器风机、吊扇、吊扇灯、落地扇、电动手工具、吸尘器、无人机电调、水泵</p>\n</div>\n<div class=\"pop_content_nav_item_right\">\n<div class=\"swiper mySwiper62 mySwiperstyle\">\n<div class=\"swiper-wrapper\">\n<div class=\"swiper-slide\">\n<div class=\"swiper-slide-item\"><img title=\"MM32SPIN0280.png\" src=\"data:image/png;base64,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\" width=\"240\" height=\"160\" /></div>\n</div>\n</div>\n</div>\n</div>\n</div>\n</div>\n</div>\n</div>\n</div>\n</div>"
                                              },
                                             {
                                                 "name": "MM32SPIN560C",
                                                 "text": "<div class=\"pop_content_nav_item_left\">\n<h4 data-v-da0de1e7=\"\">功能特性</h4>\n<p>&bull;Arm&reg; Cortex-M0 内核，主频高达96MHz<br />&bull;128KB Flash，8KB SRAM<br />&bull;包含2个12位的ADC，采样速度高达3Msps<br />&bull;5个通用定时器、2个针对电机控制的 PWM 高级定时器<br />&bull;1个I2C接口、2个SPI 接口和 3个UART接口<br />&bull;针对电机应用内置 3个运放，3个比较器<br />&bull;预驱工作电压高达60V<br />&bull;工作温度范围（环境温度）-40℃ - 105℃<br />&bull;提供 QFN48 封装</p>\n</div>\n<div class=\"pop_content_nav_item_right\">\n<div class=\"swiper mySwiper62 mySwiperstyle\">\n<div class=\"swiper-wrapper\">\n<div class=\"swiper-slide\">\n<div class=\"swiper-slide-item\"><img title=\"MM32SPIN0280.png\" src=\"data:image/png;base64,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\" width=\"240\" height=\"160\" /></div>\n</div>\n</div>\n</div>\n</div>"
                                             },
                                             {
                                                 "name": "MM32SPIN580C",
                                                 "text": "<div class=\"pop_content_nav_item_left\">\n<h4 data-v-da0de1e7=\"\">应用领域</h4>\n<p>空气净化器、服务器风机、吊扇、吊扇灯、落地扇、电动手工具、吸尘器、无人机电调、水泵</p>\n<h4 data-v-da0de1e7=\"\">功能特性</h4>\n<p>&bull;Arm&reg; Cortex-M0 内核，主频高达96MHz<br />&bull;128KB Flash，8KB SRAM<br />&bull;包含2个12位的ADC，采样速度高达3Msps<br />&bull;5个通用定时器、2个针对电机控制的 PWM 高级定时器<br />&bull;1个I2C接口、2个SPI 接口和 3个UART接口<br />&bull;针对电机应用内置 3个运放，3个比较器<br />&bull;预驱工作电压高达60V<br />&bull;工作温度范围（环境温度）-40℃ - 105℃<br />&bull;提供 QFN48 封装</p>\n</div>\n<div class=\"pop_content_nav_item_right\">\n<div class=\"swiper mySwiper62 mySwiperstyle\">\n<div class=\"swiper-wrapper\">\n<div class=\"swiper-slide\">\n<div class=\"swiper-slide-item\"><img title=\"MM32SPIN0280.png\" src=\"data:image/png;base64,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\" width=\"240\" height=\"160\" /></div>\n</div>\n</div>\n</div>\n</div>"
                                             }]}}
                    imgList.append(k)
                Aspect1Info["value"]["mediaList"] = imgList
                formData.append(Aspect1Info)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "Article1":
                Article1Info = {"code": module,
                                "value": {
                                    "bgInfo": {"bgColor": "#0E35C2", "bgImgUrl": "", "showType": 2},
                                    "subheadInfo": {"bolder": False,"color": "#ffffff",  "text": "REPORTS"},
                                    "titleInfo": {"bolder": False, "color": "#ffffff", "iconUrl": "", "text": "大会报道"},
                                    "tagList": ["AI，人工智能", "电机控制", "电机技术"]}}
                formData.append(Article1Info)
                module_data_json["formData"] = formData
                module_data_json["role"] = ["elecfans"]
            elif module == "Lottery":
                module_data_json["module"] = "Munich" + module
                module_templateId_json = {8: "2025", 9: "202511", 10: "202512", 11: "202603"}
                for k, v in module_templateId_json.items():
                    if int(self.templateId) == k:
                        module_data_json["module"] = module + v
                LotteryInfo = {"code": module + "Info", "value": 1}
                formData.append(LotteryInfo)
                module_data_json["formData"] = formData
                # module_data_json["role"] = ["ic", "pcb", "elecfans"]
            elif module == "orderSalesRanking":
                img_urls = self.upload_all_images_in_dir(subject_orderSalesRanking_dir, self.hqshop_subject_assembly_file_add)
                now_time_thirty_minutes = str((datetime.now() + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"))
                # logger.info(f"获取当前时间10分钟后的时间：{now_time_thirty_minutes}")
                time.sleep(1)
                now_time_thirty_day = str((datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d %H:%M:%S"))
                # logger.info(f"获取当前时间一天后的时间：{now_time_thirty_day}")
                module_data_json['previewImg'] = ""
                module_data_json['onlyIndex'] = 2
                module_data_json['height'] = "auto"
                module_data_json['isAlreadySave'] = True
                module_data_json['role'] = ["ic"]
                orderSalesRankingInfo = {
                    "code": module,
                    "value": {
                        # 填写注册来源（必填）
                        "userRegSite": ["all"],
                        # 填写注册时间段（必填）
                        "userRegStartDate": now_time_thirty_minutes,
                        "userRegEndDate": now_time_thirty_day,
                        # 选择订单类型及支付（必填）
                        "lineType": "ic",
                        "orderType": [10, 11, 12, 13, 14, 15],
                        "isIncludeCreditPayment": 1,
                        "isIncludeRebateUser": 1,
                        # 选择订单状态（必填）
                        "orderStatusScene": 1,
                        # 填写生单统计时间段（必填）
                        "orderAddStartDate": now_time_thirty_minutes,
                        "orderAddEndDate": now_time_thirty_day,
                        # 填写付款统计时间段（必填）
                        "orderPayStartDate": now_time_thirty_minutes,
                        "orderPayEndDate": now_time_thirty_day,
                        # 填写进入榜单的金额门槛（必填）
                        "firstPlaceLimit": 1000,
                        "firstPlaceAvatar": img_urls[0] if isinstance(img_urls, list) else img_urls,
                        "secondPlaceLimit": 900,
                        "secondPlaceAvatar": img_urls[1] if isinstance(img_urls, list) else img_urls,
                        "thirdPlaceLimit": 800,
                        "thirdPlaceAvatar": img_urls[2] if isinstance(img_urls, list) else img_urls,
                        # 选择展示的排名个数（必填）
                        "rankingTotal": 10,
                        # 排行榜说明文案（选填）
                        "rankingTextarea": "📌 公平声明\n\n所有销售金额数据均由系统自动核算，不支持人工干预上榜。\n\n刷单、虚假交易、恶意退货等行为一经查实，将清除该金额记录并取消评榜资格。\n\n对榜单数据有异议，请联系在线客服并提供对应订单号",
                        # 文字颜色
                        "fontColor": "#ffffff",
                        #  上传排行榜背景图片
                        "contentBgInfo": {
                            "bgColor": "#ffffff",
                            "bgImgUrl":  img_urls[3] if isinstance(img_urls, list) else img_urls,
                            "showType": 1
                        },
                        "bgInfo":  {
                            "bgColor": "#ffffff",
                            "bgImgUrl": "",
                            "showType": 1
                        }
                    }
                }
                formData.append(orderSalesRankingInfo)
                module_data_json["formData"] = formData
            elif module == "Sign":
                module_data_json['previewImg'] = ""
                module_data_json['onlyIndex'] = 2
                module_data_json['height'] = "auto"
                module_data_json['isAlreadySave'] = True
                module_data_json['role'] = ["ic", "pcb"]
                img_url = self.hqshop_subject_assembly_file_add(subject_Sign_dir)
                SignInfo = {
                    "code": module,
                    "value": {
                        "buttonText": "注册/登录",
                        "loginShowStyle": 0,
                        "bgInfo": {
                            "bgColor": "#ffffff",
                            "bgImgUrl": "",
                            "showType": 1
                        },
                        "titleImgUrl": img_url,
                        "jumpUrl": self.HQCHIP_URL
                    }
                }
                formData.append(SignInfo)
                module_data_json["formData"] = formData
            elif module == "Register":
                module_data_json['onlyIndex'] = 5
                module_data_json['height'] = "auto"
                module_data_json['role'] = ["ic", "pcb"]
                register_img_urls = self.upload_all_images_in_dir(subject_Register_dir, self.hqshop_subject_assembly_file_add)
                registerActivity_id, registerActivity_name = self.hqshop_subject_registerActivity_list()
                if registerActivity_id != None:
                    RegisterInfo = {
                        "code": module.lower() + "ForActivity",
                        "value": {
                            "title": "验证报名式活动",
                            "activityName": "验证报名式活动",
                            "activityNameBg": register_img_urls[3] if isinstance(register_img_urls, list) else register_img_urls,
                            "activityBg": register_img_urls[5] if isinstance(register_img_urls, list) else register_img_urls,
                            "countdownInfo": {
                                "bolder": False,
                                "color": "#88662F"
                            },
                            "countdownNumberInfo": {
                                "bolder": False,
                                "color": "#CC0000"
                            },
                            "adImg": register_img_urls[6] if isinstance(register_img_urls, list) else register_img_urls,
                            "rulesDetailInfo": {
                                "bolder": False,
                                "color": "#834417"
                            },
                            "registerDynamicInfo": {
                                "bolder": False,
                                "color": "#88662F"
                            },
                            "activityBeforeBtn": register_img_urls[1] if isinstance(register_img_urls, list) else register_img_urls,
                            "activityNotRegBtn": register_img_urls[2] if isinstance(register_img_urls, list) else register_img_urls,
                            "activityRegBtn": register_img_urls[0] if isinstance(register_img_urls, list) else register_img_urls,
                            "regBtnHandle": {
                                "handleType": 1,
                                "jumpInfo": {
                                    "jumpType": 6,
                                    "url": self.HQCHIP_URL,
                                    "anchor": "",
                                    "formInfo": {
                                        "action": "",
                                        "id": "",
                                        "isLogin": 0
                                    }
                                }
                            },
                            "activityFinishBtn": register_img_urls[4] if isinstance(register_img_urls, list) else register_img_urls,
                            "simpleRules": "<p>自动化测试</p>",
                            "detialRules": "<p>自动化测试</p>",
                            "bindActivityArr": [
                                {
                                    "activityId": registerActivity_id,
                                    "activityName":  registerActivity_name
                                }
                            ],
                            "bgInfo": {
                                "showType": 2,
                                "bgColor": "#EF1414",
                                "bgImgUrl": ""
                            }
                        }
                    }
                else:
                    RegisterInfo = {}
                if RegisterInfo != {}:
                    formData.append(RegisterInfo)
                module_data_json["formData"] = formData
            elif module == "NavBar":
                skip_url = "{}/act/new.html".format(self.HQCHIP_URL)
                img_main_icon_url = self.hqshop_subject_assembly_file_add(subject_NavBar_main_icon_dir)
                NavBarInfo = {"code": module,
                              "value": {
                                  "bgInfo": {"bgColor": "#150705", "bgImgUrl": "", "showType": 2},
                                  "childMenuHoveBgColor": "#280F20",
                                  "fontStyle": {"bolder": True, "color": "#ffffff", "hoveColor": "#EFA70C"}
                              }}
                NavBarInfo["value"]["logoInfo"] = {"iconUrl": img_main_icon_url, "showType": 1, "text": "",
                                                   "jumpInfo": {"jumpType": 4, "action": "测试表单", "id": 380,"isLogin": 0}}
                navTexts = []
                if self.templateId == 4:
                    img_button_enroll_icon_url = self.hqshop_subject_assembly_file_add(subject_NavBar_button_enroll_icon_dir)
                    NavBarInfo["value"]["btnEl"] = {"iconUrl": img_button_enroll_icon_url, "showType": 1, "text": "",
                                                    "jumpInfo": {"anchor": "Hypertext18", "jumpType": 7, "url": skip_url,
                                                                 "formInfo": {"action": "测试表单", "id": 380}}}
                    navTexts = ["活动概要", "会议议程", "演讲嘉宾", "市场表现奖", "展台看点", "大会报道", "影响力报告"]

                elif self.templateId == 5:
                    img_button_review_icon_url = self.hqshop_subject_assembly_file_add(subject_NavBar_button_enroll_icon_dir)
                    NavBarInfo["value"]["btnEl"] = {"iconUrl": img_button_review_icon_url, "showType": 1, "text": "",
                                                    "jumpInfo": {"anchor": "Hypertext18", "jumpType": 7, "url": skip_url,
                                                                 "formInfo": {"action": "测试表单", "id": 380}}}
                    navTexts = ["活动概要", "会议议程", "演讲嘉宾", "市场表现奖", "展台看点", "大会报道", "影响力报告",
                                "往届回顾"]
                elif self.templateId == 6:
                    img_button_review_icon_url = self.hqshop_subject_assembly_file_add(subject_NavBar_button_enroll_icon_dir)
                    NavBarInfo["value"]["btnEl"] = {"iconUrl": img_button_review_icon_url, "showType": 1, "text": "",
                                                    "jumpInfo": {"anchor": "Hypertext18", "jumpType": 7, "url": skip_url,
                                                                 "formInfo": {"action": "测试表单", "id": 380}}}
                    navTexts = ["活动概要", "会议议程", "演讲嘉宾", "市场表现奖", "展台看点", "大会报道", "影响力报告", "往届回顾"]
                elif self.templateId == 7:
                    img_button_review_icon_url = self.hqshop_subject_assembly_file_add(subject_NavBar_button_enroll_icon_dir)
                    NavBarInfo["value"]["btnEl"] = {"iconUrl": img_button_review_icon_url, "showType": 1, "text": "",
                                                    "jumpInfo": {}}
                    NavBarInfo["value"]["logoInfo"]["jumpInfo"] = {}
                    navTexts = ["活动介绍", "会议议程", "演讲嘉宾", "大会报道", "影响力报告", "往届回顾"]
                navTexList = []
                for i in range(len(navTexts)):
                    i = i + 1
                    k = {"child": [], "imgUrl": "", "index": i, "navText": navTexts[i-1], "navType": 2,
                             "jumpInfo": {"jumpType": 7, "anchor": "", "formInfo": {"action": "", "id": ""}, "url": skip_url}}
                    navTexList.append(k)
                NavBarInfo["value"]["navList"] = navTexList
                formData.append(NavBarInfo)
                module_data_json["formData"] = formData
            moduleInfo.append(module_data_json)
        for m in range(len(moduleInfo)):
            moduleInfo[m]["index"] = m
        # print(moduleInfo)
        print(json.dumps(moduleInfo, ensure_ascii=False).replace("'", '"'))
        return moduleInfo


    def hqshop_subject_detail_edit(self):
        """
        存储/发布专题组件内容+应用模板--6大会报道模板
        :param self.topicStatus 专题状态  0草稿（存储） 1发布
        :param templateId 模板id 0不引用模板 1品牌专区模板(一) 2双十一专题模板 3慕尼黑专题模板 4大会主页模板 5展台看点模板 6大会报道模板 7大会回顾模板
        """
        moduleInfo = None
        self.templateId = int(self.templateId)
        self.templateId_title_json = {0: "不引用模板", 1: "品牌专区模板(一)", 2: "双十一专题模板", 3: "慕尼黑专题模板", 4: "大会主页模板", 5: "展台看点模板",
                                 6: "大会报道模板", 7: "大会回顾模板", 8: "2025年4月慕尼黑专题模板", 9: "2025双十一抽奖模板", 10: "2025双十二抽奖模板", 11: "2026年3月抽奖模板"}
        if self.templateId == 0:
            if self.module_name_list != None:
                moduleInfo = self.dict_module_cearte(name=self.module_name_list)
        elif self.templateId == 1:
            self.module_name_list = ["单张图片", "多张图片", "优惠券", "热门推荐", "样品组件", "商品列表", "文字"]
            moduleInfo = self.dict_module_cearte(name=self.module_name_list)
        elif self.templateId == 2:
            self.module_name_list = ["单张图片", "多张图片", "优惠券", "抽奖转盘", "热门推荐", "商品列表", "样品组件", "商品列表", "文字"]
            moduleInfo = self.dict_module_cearte(name=self.module_name_list)
        elif self.templateId == 3:
            self.module_name_list = ["单张图片", "多张图片", "优惠券", "抽奖转盘", "热门推荐", "商品列表", "样品组件", "商品列表", "文字"]
            moduleInfo = self.dict_module_cearte(name=self.module_name_list)
        elif self.templateId == 4:
            self.module_name_list = ["导航菜单(一)", "通栏图片", "分享组件", "左文右图", "超级文本", "图片组件3", "多张图片2", "通栏图片",
                                "多张图片2", "多张图片2", "多张图片2", "超级文本"]
            moduleInfo = self.dict_module_cearte(name=self.module_name_list)
        elif self.templateId == 5:
            self.module_name_list = ["导航菜单(一)", "通栏图片", "分享组件", "看点组件1", "超级文本"]
            moduleInfo = self.dict_module_cearte(name=self.module_name_list)
        elif self.templateId == 6:
            self.module_name_list = ["导航菜单(一)", "通栏图片", "分享组件", "文章组件1", "超级文本"]
            moduleInfo = self.dict_module_cearte(name=self.module_name_list)
        elif self.templateId == 7:
            self.module_name_list = ["导航菜单(一)", "通栏图片", "分享组件", "虚拟浏览", "左文右图", "图片组件2", "图片组件4", "多张图片2",
                                "多张图片2", "多张图片2", "多张图片2", "超级文本"]
            moduleInfo = self.dict_module_cearte(name=self.module_name_list)
        elif self.templateId == 8:
            self.module_name_list = ["单张图片", "多张图片", "优惠券", "抽奖转盘", "热门推荐", "样品组件", "商品列表", "超级文本"]
            moduleInfo = self.dict_module_cearte(name=self.module_name_list)
        elif self.templateId == 9:
            self.module_name_list = ["单张图片", "多张图片", "优惠券", "抽奖转盘", "热门推荐", "样品组件", "商品列表", "超级文本"]
            moduleInfo = self.dict_module_cearte(name=self.module_name_list)
        elif self.templateId == 10:
            self.module_name_list = ["单张图片", "多张图片", "优惠券", "抽奖转盘", "热门推荐", "样品组件", "商品列表", "超级文本"]
            moduleInfo = self.dict_module_cearte(name=self.module_name_list)
        elif self.templateId == 11:
            self.module_name_list = ["单张图片", "多张图片", "优惠券", "抽奖转盘", "热门推荐", "样品组件", "商品列表","报名组件(普通版)", "超级文本"]
            moduleInfo = self.dict_module_cearte(name=self.module_name_list)
        self.detail_edit_body = self.hqshop_subject_detail()
        detail_edit_body = {"moduleInfo": moduleInfo, "shopThematicId": self.shopThemat_id, "topicStatus": self.topicStatus}
        print(self.detail_edit_body)
        if self.detail_edit_body == None:
            # 新建的专题
            detail_edit_url = "{}/ecmc/shop/addSubjectPage".format(self.Activity_Center_URL)
        else:
            # 历史的专题
            detail_edit_url = "{}/ecmc/shop/editSubjectPage".format(self.Activity_Center_URL)
            detail_edit_body["id"] = self.detail_edit_body["id"]
            detail_edit_body["pushTime"] = self.detail_edit_body["pushTime"]
        # 设置模块dict
        for k, v in self.templateId_title_json.items():
            if int(self.templateId) == k:
                logger.info("专题模板为【{}】".format(v))
                if k == 0:
                    detail_edit_body["role"] = ["ic", "pcb"]
                elif k > 0:
                    detail_edit_body["templateId"] = int(self.templateId)
                    detail_edit_body["title"] = v
                    if k > 3 and  k < 8 :
                        detail_edit_body["role"] = ["elecfans"]
                    else:
                        detail_edit_body["role"] = ["ic", "pcb"]
                break
        print(json.dumps(detail_edit_body, ensure_ascii=False).replace("'", '"'))
        detail_edit_subject_res = self.activity_rss.post(url=detail_edit_url, json=detail_edit_body, headers=self.json_head).json()
        logger.info(detail_edit_subject_res)
        if self.topicStatus == 0:
            logger.info("存储成功！！")
        elif self.topicStatus == 1:
            logger.info("发布成功！！")
        return self.module_name_list
    def mian_hqshop_subject(self):
        if self.shopThemat_id == None:
            self.hqshop_subject_add()
        elif self.shopThemat_id == []:
            self.hqshop_subject_add()
        elif self.shopThemat_id == "":
            self.hqshop_subject_add()
        module_name_list = self.hqshop_subject_detail_edit()
        print("组件列表: ",module_name_list)
        return module_name_list


if __name__ == '__main__':
    activity_id = 49
    shopThemat_id = None
    thematicName = "自动化测试验证30"
    finishedRedirectUrl = None
    appSite = 1
    client = 1
    target_rss = SOOLogin("uat-activity.hqchip.com", "ecmc").target_login()
    # HqshopSubject(target_rss=target_rss, activity_id=activity_id, shopThemat_id=shopThemat_id, thematicName=thematicName,
    #              finishedRedirectUrl=finishedRedirectUrl, appSite=appSite, client=client, topicStatus=1, templateId=11).mian_hqshop_subject()
    # HqshopSubject(target_rss=target_rss).hqshop_subject_elecfans_taglist("AI，人工智能")
    HqshopSubject(target_rss=target_rss, templateId=4).dict_module_cearte(name=["热门推荐"])
    HqshopSubject(target_rss=target_rss, templateId=4).hqshop_subject_topicfrom()
    # HqshopSubject(target_rss=target_rss, activity_id=activity_id, shopThemat_id=shopThemat_id,
    #               thematicName=thematicName,
                 # finishedRedirectUrl=finishedRedirectUrl, appSite=appSite, client=client, topicStatus=1, templateId=11).img_portp()
