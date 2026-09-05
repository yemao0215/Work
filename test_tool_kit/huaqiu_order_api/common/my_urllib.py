from urllib import parse


class UrlLib:
    def __init__(self, url):
        self.url = url

    def split_url(self):
        parse_result = parse.urlparse(self.url)  # 拆分url
        # print('parseResult:{}'.format(parse_result))
        param_dict = parse.parse_qs(parse_result.query)  # 根据&符号 拆分query参数
        # print('param_dict:{}'.format(param_dict))
        return param_dict


if __name__ == '__main__':
    url = r"/cart/checkout.html?type=1&source_type=3&rec_id=1288434"
    dict1 = UrlLib(url).split_url()
    value = dict1['rec_id']
    print(value)

