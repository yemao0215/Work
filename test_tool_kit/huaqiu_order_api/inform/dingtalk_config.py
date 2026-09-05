#conding=utf-8

import sys
import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
from dingtalkchatbot.chatbot import DingtalkChatbot
from loguru import logger


class DingTalkHandle:
    def __init__(self, project_name, prams, msg_data):
        self.project_name = project_name
        self.prams = prams
        self.msg_data = msg_data

    def message(self, at_mobiles: list = None):
        if at_mobiles:
            at_mobiles = list(map(str, at_mobiles))
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "自动化测试报告",
                    "text": "标题：<font color=#dc143c size=20 face='黑体'>测试组内自动化工具-></font><font color=#6A5ACD size=20 face='黑体'>执行结果通知</font>" + '\n\n'
                    "执行脚本：<font color=#DAA520 size=6 face='微软雅黑'>{}</font>".format(self.project_name) + '\n\n'
                    "测试参数JSON信息：<font color=#DAA520 size=6 face='微软雅黑'>{}</font>".format(self.prams) + '\n\n'
                    "返回结果信息：<font color=#DAA520 size=6 face='微软雅黑'>{}</font>".format(self.msg_data) + '\n\n'
                    "执行地址：<font color=#228B22 size=6 face='微软雅黑'>{}</font>".format("http://192.168.10.41:5000 or http://www.yemaotest.com:5000") + '\n\n'+ '\n@' + '@'.join(at_mobiles)
                },
                "at": {
                    "atMobiles": f"{at_mobiles}",
                    "isAtAll": False,
                }
            }
            return data

        else:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "自动化测试报告",
                    "text": "标题：<font color=#dc143c size=20 face='黑体'>测试组内自动化工具-></font><font color=#6A5ACD size=20 face='黑体'>执行结果通知</font>" + '\n\n'
                    "执行脚本：<font color=#DAA520 size=6 face='微软雅黑'>{}</font>".format(self.project_name) + '\n\n'
                    "测试参数JSON信息：<font color=#DAA520 size=6 face='微软雅黑'>{}</font>".format(self.prams) + '\n\n'
                    "返回结果信息：<font color=#DAA520 size=6 face='微软雅黑'>{}</font>".format(self.msg_data) + '\n\n'
                    "执行地址：<font color=#228B22 size=6 face='微软雅黑'>{}</font>".format("http://192.168.10.41:5000 or http://www.yemaotest.com:5000") + '\n\n'
                },
                "at": {
                    "atMobiles": "",
                    "isAtAll": False,
                }
            }
            print("打印data信息：{}".format(data))
            return data

    def send_message(self, at_mobiles: list = None):
        if at_mobiles:
            data = self.message(at_mobiles)
        else:
            data = self.message()
        try:
            timestamp = str(round(time.time() * 1000))
            #群机器人密钥
            secret = 'SEC8188d296c26423582e152a41a72b2a9747c88890fcc204020c72e7d30698e864'
            secret_enc = secret.encode('utf-8')
            string_to_sign = '{}\n{}'.format(timestamp, secret)
            string_to_sign_enc = string_to_sign.encode('utf-8')
            hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

            headers = {'Content-Type': 'application/json'}  # 定义数据类型
            #群机器人对接
            webhook = 'https://oapi.dingtalk.com/robot/send?access_token=4e71bcc99b7f323a894288de5cfa1e555b3f1fc6d2c224cc78f0806d4cd9bcb2'
            webhook_timestamp_sign = '{}&timestamp={}&sign={}'.format(webhook, timestamp, sign)
            res = requests.post(webhook_timestamp_sign, data=json.dumps(data), headers=headers)  # 发送post请求
            logger.info(f'钉钉发送结果:{res.text}')
            return res
        except Exception as e:
            return f"发送消息失败: {str(e)}"




if __name__ == '__main__':
    mobile_list = ['15070739124']
    # mobile_list = None
    dth = DingTalkHandle(project_name='wms出库操作(仅出库)', prams={"text": {"text": "111"}}, msg_data={"text": 1})
    print("钉钉发送结果：", dth.send_message(at_mobiles=mobile_list))

