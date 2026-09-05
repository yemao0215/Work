import yaml


class A:

    """"全局读取yaml文件统一方法（待完善）"""
    @classmethod
    def getyaml(self, file):
        with open(file, 'r', encoding='utf-8') as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
            return data

    """"全局修改覆盖yaml文件统一方法（待完善）"""
    @classmethod
    def modyaml(self, file, address):
        with open(file, encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            for t in address:
                data[t] = address[t]
        with open(file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)
            f.close()

    """"全局追加写入yaml文件统一方法（待完善）"""
    @classmethod
    def append(self, file, address):
        with open(file, encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        with open(file, "w+", encoding="utf-8") as f:
            if data:
                data.update(address)
                yaml.dump(data, f, allow_unicode=True)
                print('写入成功{}'.format(address))
            else:
                yaml.dump({'订单编号': '拼板编号'}, f, allow_unicode=True)
                A.append(file, address)
            f.close()

# address = {'blayer': 1, 'bcount': 12}
# A.append(r'pb.yaml', {1673328: "P6H210820A1"})

# getyaml(file, address)

