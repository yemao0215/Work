# coding:utf-8
import requests
import json
import datetime


class SendMessage(object):
    # 初始化
    def __init__(self):
        pass

    # 开始推送
    def sendmessage(self, cont):
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
        message = {"msgtype": "text", "text": {"content": now_time + cont}}
        url = "https://oapi.dingtalk.com/robot/send?access_token" \
              "=6646cc67b2995699a53b78f05d9a5933ea81642caaeaca93eac1557cc1d0aa69 "
        headers = {'Content-Type': 'application/json'}
        requests.post(url=url, data=json.dumps(message), headers=headers)  # json.dumps  把python数据转换为json字符串


if __name__ == "__main__":
    SendMessage().sendmessage('测试报告')
