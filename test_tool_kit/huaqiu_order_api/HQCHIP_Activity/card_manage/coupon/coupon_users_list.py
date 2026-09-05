

class CouponUserList:

    def __init__(self, target_rss,coupon_name):
        self.coupon_users_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.coupon_name = coupon_name
        # self.forbidType = forbidType