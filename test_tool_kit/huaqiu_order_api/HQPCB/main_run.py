from huaqiu_order_api.HQPCB.pcb_api import get_phpsessid, review_order, test_hqpcb_order, add_user_key
from huaqiu_order_api.HQPCB.pcb_mes import Cam, xnpb
from huaqiu_order_api.HQPCB.next_pcb import nextpcb


class RunPcb:
    @staticmethod
    def main(type, params=None):
        dict = {'phpsessid': get_phpsessid.Factory().get_phpsessid,
                'mid': add_user_key.UserKey().exists,
                'orders': test_hqpcb_order.PcbOrder().test_order_make,
                'audit': review_order.ReviewOrder().run,
                'details': review_order.ReviewOrder().run_get_order,
                'order_audit': test_hqpcb_order.PcbOrder().test_order_audit,
                'order_pay': test_hqpcb_order.PcbOrder().run_order_pay,
                'cam_doen': Cam.Cam().cam_doen,
                'run_pb': xnpb.Virtualpb().run_pb,
                'ruku': xnpb.Virtualpb().run_pb_mi_ruku,
                'order_ruku': xnpb.Virtualpb().run_order_pb,
                'nextpcb_order': nextpcb.NextPcb().paymentTotal,
                'review_order': nextpcb.NextPcb().review_order

                }
        dict[type]() if params is None else dict[type](params)


if __name__ == '__main__':
    """
    'phpsessid': 如果提示请重新登录，执行一下这个即可（需要注意谷歌浏览器版本和谷歌浏览器驱动版本匹配）
    'mid': 传入客户编号，执行一下，就会自动切换成对应账号
    'orders': PCB自动下单，可传入一个原单号下返单，不传则下新单  
    'audit': PCB自动审核订单，传入需审核的订单号
    'details': 获取PCB订单详情，传入要查询的订单号
    'order_audit': 自动下单审单，得到一个审核通过的订单
    'order_pay': 自动下单到付款，得到一个已付款的订单
    'cam_doen': 一键外协完成（生产稿需要外协完成触发）
    'run_pb': 传入已付款的订单号，自动跑到拼板审核确认（完成所有工程模块操作，后续接刷卡过数）
    'ruku': 传入已付款的订单号，自动跑到发货
    'order_ruku': 自动下单到发货
    'nextpcb_order': 外贸订单自动下单付款
    'review_order': 外贸下单到内贸审核完成
    
    如需切换环境，打开pcb_config.yaml配置文件，修改域名即可
    """
    # RunPcb().main('phpsessid')
    RunPcb().main('mid', 	5147236)
    # RunPcb().main('orders',{"invoice": {"invoice_type": '增票', "invoice_title": '测试专用账号', "invoice_number": '12345678'}})
    # RunPcb().main("audit", 2402113) # 审核订单
    # RunPcb().main('order_audit', {"bwidth": 10, "blength": 10, "bcount": 50})
    RunPcb().main('order_ruku') #已付款到已发货
