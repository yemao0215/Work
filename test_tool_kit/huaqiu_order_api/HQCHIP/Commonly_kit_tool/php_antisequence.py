import json

import phpserialize


class PhpAntisequence:
    def __init__(self, data):
        self.data = data

    # 定义递归函数将所有字节串转换为普通字符串
    def decode_bytes(self, data):
        if isinstance(data, bytes):
            return data.decode('utf-8')
        elif isinstance(data, dict):
            return {self.decode_bytes(key): self.decode_bytes(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.decode_bytes(element) for element in data]
        else:
            return data

    def is_php_serialized(self, data):
        try:
            phpserialize.loads(data.encode('utf-8'))
            return True
        except Exception as e:  # 捕获所有异常
            print(f"Error: {e}")  # 输出错误信息以进行调试
            return False
    def php_Antisequence(self):
        # 判断是否为PHP序列化数据
        if self.is_php_serialized(self.data) == True:
            php_data_bytes = self.data.encode('utf-8')
            # 解析PHP反序列化数据
            parsed_data = phpserialize.loads(php_data_bytes)

            # 转换PHP数据的键和值为字符串类型
            parsed_data_str = self.decode_bytes(parsed_data)

            # 将PHP数据转换为JSON格式
            json_data = json.dumps(parsed_data_str, ensure_ascii=False)
            print(json_data)
            return json_data
        else:
            print("不是PHP序列化数据")
            return self.data
if __name__ == '__main__':
    data = 'a:7:{s:3:"HDT";s:12:"香港：4-7";s:5:"price";N;s:3:"CDT";s:12:"2-3工作日";s:15:"main_brand_name";s:0:"";s:13:"provider_name";s:17:"UNI-ROYAL(厚声)";s:2:"PN";s:10:"HQCHIPLCSC";s:12:"goods_number";i:200;}'
    php_antisequence = PhpAntisequence(data).php_Antisequence()



