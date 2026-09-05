class SettleGoodsRexord:
    # 代售单据
    def __init__(self, target_rss, bill_sn):
        self.srm_rss = target_rss
        self.json_head = {"Content-Type": "application/json"}
        self.file_head = {"Content-Type": "multipart/form-source_data"}
        self.bill_sn = bill_sn