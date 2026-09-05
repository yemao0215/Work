from huaqiu_order_api.HQCHIP_Center.user_center import login_code_obtain, pay_code_obtain, \
    enterprise_certification_code, logout_code_obtain


class YzmCodeObtain:
    # 验证码获取
    def __init__(self, yzmcode_type=None,  phone=None, uid=None):
        self.yzmcode_type = yzmcode_type
        self.phone = phone
        self.uid = uid
    def yzmcode_obtain(self):
        yzmcode = None
        if self.yzmcode_type == "1":
            # 注册登录、修改密码
            yzmcode = login_code_obtain(self.phone)
        elif self.yzmcode_type == "2":
            # 修改支付密码
            yzmcode = pay_code_obtain(int(self.uid))
        elif self.yzmcode_type == "3":
            # 企业认证
            yzmcode = enterprise_certification_code(int(self.uid))
        elif self.yzmcode_type == "4":
            # 用户注销
            yzmcode = logout_code_obtain(self.phone)
        print(yzmcode)
        return yzmcode
if __name__ == "__main__":
    yzmcode_type = "1"
    phone = "15527195467"
    uid = ""
    YzmCodeObtain(yzmcode_type,  phone, uid).yzmcode_obtain()