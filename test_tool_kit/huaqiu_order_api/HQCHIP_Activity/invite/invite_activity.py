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

from huaqiu_order_api.common.loguru_logger import logger
from huaqiu_order_api.common.my_path import yaml_file, img_share_support_cover_dir, img_share_support_newusers_dir, img_plan_an_order_cover_PC_dir, \
                                        img_plan_an_order_cover_H5_dir, img_plan_an_order_share_dir, img_plan_an_order_MiniProgram_share_dir, img_plan_an_order_newusers_dir


class InviteActivity:
    def __init__(self, target_rss=None):
        """
        :param actiivity_type 活动形式
        """
        self.activity_rss = target_rss
        self.json_head = {"Content-Type": "application/json",
                          "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                          }
        self.headers_urlencoded = {"Content-Type": "application/x-www-form-urlencoded",}
        with open(yaml_file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        self.Activity_Center_URL = data['Activity_Center_URL']
    def invite_assembly_file_add(self, img_dir):
        files_name = img_dir.split('\\')[-1]
        assembly_file_url = "{}/ecmc/upload/uploadFile".format(self.Activity_Center_URL)
        file = [('file', (files_name, open(img_dir, 'rb'),'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
        assembly_file_res = self.activity_rss.post(url=assembly_file_url, files=file).json()
        # print(assembly_file_res)
        img_url = jsonpath.jsonpath(assembly_file_res, "$..url")[0]
        return img_url
    def invite_activity_list(self):
        """拉新活动查询"""
        invite_activity_search_url = "{}/ecmc/activityInvite/list".format(self.Activity_Center_URL)
        invite_activity_search_body = {
            "activityStatusValue": 0,
            "pageNum": 1,
            "pageSize": 20
        }
        invite_activity_search_res = self.activity_rss.post(url=invite_activity_search_url, json=invite_activity_search_body, headers=self.json_head).json()

    def invite_activity_add(self, actiivity_type=None):
        """"""
        actiivity_type_json = {1: "分享拉新获助力值", 2: "邀请注册并下单获取奖励"}
        now_time_ten_minutes = str((datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间10分钟后的时间：{now_time_ten_minutes}")
        time.sleep(1)
        now_time_one_day = str((datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"获取当前时间一天后的时间：{now_time_one_day}")
        actiivity_name_part = ""
        for k, v in actiivity_type_json:
            if actiivity_type == k:
                actiivity_name_part = v
        activity_name = "测试" + actiivity_name_part
        fitd_share_support_cover = self.invite_assembly_file_add(img_share_support_cover_dir)
        fitd_share_support_newusers = self.invite_assembly_file_add(img_share_support_newusers_dir)
        fitd_plan_an_order_cover_PC = self.invite_assembly_file_add(img_plan_an_order_cover_PC_dir)
        fitd_plan_an_order_cover_H5 = self.invite_assembly_file_add(img_plan_an_order_cover_H5_dir)
        fitd_plan_an_order_share = self.invite_assembly_file_add(img_plan_an_order_share_dir)
        fitd_plan_an_order_MiniProgram_share = self.invite_assembly_file_add(img_plan_an_order_MiniProgram_share_dir)
        fitd_plan_an_order_newusers = self.invite_assembly_file_add(img_plan_an_order_newusers_dir)
        invite_activity_add_body = {
            "activity_name": activity_name,
            "activityStartTime": now_time_ten_minutes,
            "activityEndTime": now_time_one_day,
            "actiivity_type": actiivity_type
        }
        if actiivity_type == 1:
            invite_activity_add_body["invitePoints"] = 1
            invite_activity_add_body["firstPayPoints"] = 2
            invite_activity_add_body["headerImage"] = fitd_share_support_cover
            invite_activity_add_body["pcHeaderImage"] = ""
            invite_activity_add_body["preActivityText"] = ""
            invite_activity_add_body["postActivityText"] = ""
            invite_activity_add_body["seoDescription"] = ""
            invite_activity_add_body["seoKeyword"] = ""
            invite_activity_add_body["seoTitle"] = ""
            invite_activity_add_body["sharePosterImage"] = ""
            invite_activity_add_body["shipRewardDelayDay"] = 0
            invite_activity_add_body["wechatShareDescription"] = ""
            invite_activity_add_body["wechatShareImage"] = ""
            invite_activity_add_body["wechatShareTitle"] = ""
            invite_activity_add_body["miniprogramPageTitle"] = ""
            invite_activity_add_body["bindExpireDay"] = 0
            invite_activity_add_body["deleteRewardIds"] = []
            invite_activity_add_body["introduction"] = "邀请好友点击你分享的活动链接，完成华秋PCB/商城登录/注册（未下过单用户），即可获得1个助力值；\n助力值可累计，满足对应数量即可兑换相应福利；\n被邀请好友需为华秋PCB及华秋商城未下单用户，已下单用户助力无效；"
            invite_activity_add_body["miniprogramPageTitle"] = ""
        elif actiivity_type == 2:
            invite_activity_add_body["invitePoints"] = None
            invite_activity_add_body["firstPayPoints"] = None
            invite_activity_add_body["headerImage"] = fitd_plan_an_order_cover_H5
            invite_activity_add_body["pcHeaderImage"] = fitd_plan_an_order_cover_PC
            invite_activity_add_body["preActivityText"] = f"<p><span style=\"color: #8c5034;\">活动预热中：本次邀请有礼活动将于 {now_time_ten_minutes} 正式开启，邀请链接与首单返利将在活动开启后正式生效，敬请期待！</span></p>"
            invite_activity_add_body["postActivityText"] = f"<p><span style=\"color: #8c5034; font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif; font-size: 16px; background-color: #ffffff;\">活动已结束：本次邀请有礼活动已于当前时间: {now_time_one_day}圆满结束。您已建立的<a style=\"background-color: #ffffff; color: #8c5034;\" href=\"https://uat-m.hqchip.com\" target=\"_blank\" rel=\"noopener\">邀请关系</a>及未发放的奖励在审核后仍将正常发放，感谢您的支持！</span></p>"
            invite_activity_add_body["seoDescription"] = invite_activity_add_body["activity_name"]
            invite_activity_add_body["seoKeyword"] = invite_activity_add_body["activity_name"]
            invite_activity_add_body["seoTitle"] = invite_activity_add_body["activity_name"]
            invite_activity_add_body["sharePosterImage"] = fitd_plan_an_order_share
            invite_activity_add_body["shipRewardDelayDay"] = 1
            invite_activity_add_body["wechatShareDescription"] = "小程序分享描述"
            invite_activity_add_body["wechatShareImage"] = fitd_plan_an_order_MiniProgram_share
            invite_activity_add_body["wechatShareTitle"] = "小程序分享标题"
            invite_activity_add_body["miniprogramPageTitle"] = invite_activity_add_body["activity_name"]
            invite_activity_add_body["bindExpireDay"] = 10
            invite_activity_add_body["deleteRewardIds"] = []
            invite_activity_add_body["introduction"] = ("<p><span style=\"font-size: 14px; color: #e03e2d;\">"
                                                        "一、活动参与条件</span></p>\n<p><span style=\"font-size: 14px;\">"
                                                        "1.邀请方须为华秋商城已注册并绑定手机号的正常有效用户。</span></p>\n<p><span style=\"font-size: 14px;\">"
                                                        "2.被邀请好友须为此前从未在华秋商城完成过首单的新用户（以订单支付并全额付款成功为准）。</span></p>\n<p><span style=\"font-size: 14px;\">"
                                                        "3.订单实付金额计算不含运费、优惠券抵扣部分，且面板打印、PCB打样、SMT贴片订单不参与此裂变活动。</span></p>\n"
                                                        "<p><span style=\"color: #e03e2d; font-size: 14px;\">"
                                                        "二、绑定时效与规则</span></p>\n<p><span style=\"font-size: 14px;\">"
                                                        "1.被邀请人首次点击好友的专属链接进入华秋商城起，即建立潜在绑定关系，有效期30天。若30天内好友完成首单，则绑定成功，发放相应奖励。超出30天未下单，绑定自动失效。</span></p>\n<p><span style=\"font-size: 14px;\">"
                                                        "2.一客一绑：同一新用户只能与一位邀请人绑定。若新用户点击了多个不同好友的链接，以首单发生前最新关联的链接为准。</span></p>\n<p><span style=\"color: #e03e2d; font-size: 14px;\">"
                                                        "三、奖励发放时限与追回</span></p>\n<p><span style=\"font-size: 14px;\">"
                                                        "1.奖励在被邀请好友首单发货后T+10个工作日内，经系统核对绑定关系、首单金额、参与品类与订单状态后，由系统批量派发至您的优惠券包。</span></p>\n<p><span style=\"font-size: 14px;\">"
                                                        "2.若好友首单发生拒收、退货、全额退款等异常关闭状态，系统将自动取消该笔奖励。如奖励已派发，将在下一笔活动奖励中予以等额扣回，或作废已派发对应优惠券。</span></p>\n<p><span style=\"font-size: 14px; color: #e03e2d;\">"
                                                        "四、活动资格与发奖条件</span></p>\n<p><span style=\"font-size: 14px;\">"
                                                        "1.新版活动仅按活动规则进行资格校验：被邀请人须符合新用户定义，且未绑定过其他邀请人；同一新用户只能建立一次邀请关系。</span></p>\n<p><span style=\"font-size: 14px;\">"
                                                        "2.自邀自禁：用户不能通过自己生成的邀请链接邀请自己。若不满足活动资格或发奖条件，将不建立邀请关系或不发放奖励。最终解释权归华秋商城所有。</span></p>")




