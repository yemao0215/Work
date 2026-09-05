from huaqiu_order_api.HQCHIP_ERP.erp_stencil_order_cancellation import ErpStencilOrdderCancellation
from huaqiu_order_api.HQSTENCIL.Stencil_Reception.Stencil_order import StencilOrder
from huaqiu_order_api.SSO_Reception.sso_reception import SSO_Reception


class RunStencil:
    def main(self, phone, phone_pwd):
        # 前台单点登录
        SSO_rss, token = SSO_Reception(phone, phone_pwd, 'https://uat-www.hqpcb.com').login()
        # 前台提交Stencil订单
        order_sn = StencilOrder(SSO_rss, phone).stencil_tmp_save().place_an_order()
        # ERP-Stencil订单处理
        ErpStencilOrdderCancellation("admin", "123456", order_sn, "uesr").login().erp_stencil_order_cancellation("G999999999")

if __name__ == "__main__":
    RunStencil().main(15912757721, "a123456")