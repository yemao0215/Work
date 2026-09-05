import re
import time
import requests
from faker import Faker


class AccountSign:
    """uat环境注册账号+修改密码"""
    phone = []

    def __init__(self):
        self.res = requests.Session()

    def ic_sign(self, num):
        for i in range(num):
            phone = Faker("zh_CN").phone_number()
            send_captcha_url = 'https://uat-passport.elecfans.com/register/regsms'
            data = {"siteid": "12", "areacode": "86", "account": phone, "aliscene": "login"}
            res = self.res.post(url=send_captcha_url, data=data)
            msg = res.json()['msg']

            captcha = re.search('([0-9]{6})', msg)
            login_url = 'https://uat-passport.elecfans.com/smsLogin/index.html'
            login_data = {"siteid": "12", "scene": "quick", "areacode": "86", "account": phone, "aliscene": "login",
                          "smscode": captcha.group()}
            login_res = self.res.post(url=login_url, data=login_data)
            token = login_res.json()['source_data']['token']
            self.phone.append(phone + ':' + token)
        time.sleep(65)
        return self

    def update_password(self, password):
        for i in self.phone:
            li = i.split(":")
            phone = li[0]
            token = li[1]
            header = {"Authorization": token}
            try:
                url = 'https://uat-passport.elecfans.com/register/regsms'
                data = {"account": phone, "aliscene": "login", "siteid": "12"}
                res = self.res.post(url=url, data=data, headers=header)
                msg = res.json()['msg']
                captcha = re.search('([0-9]{6})', msg)

                update_url = 'https://uat-passport.elecfans.com/password/modifyPasswordPreVerifyByPhone'
                update_data = {"areacode": "", "code": captcha.group(), "phone": phone, "siteid": "12"}
                update_res = self.res.post(url=update_url, data=update_data, headers=header)
                token = update_res.json()['source_data']['token']
                uid = update_res.json()['source_data']['uid']

                reset_password_url = 'https://uat-passport.elecfans.com/password/resetPassword'
                reset_password_data = {"password": password, "token": token, "uid": uid}
                self.res.post(url=reset_password_url, data=reset_password_data, headers=header)
                print(f"注册的账号为:{phone},修改后的密码为:{password}")
            except Exception as e:
                print(f"密码修改失败,错误原因:{e}")


if __name__ == '__main__':
    AccountSign().ic_sign(1).update_password('a123456')
