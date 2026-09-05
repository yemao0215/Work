import socket
import struct
import time


class PLC_Tester:
    def __init__(self, ip, port=502, protocol='modbus'):
        self.ip = ip
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3)
        self.sock.connect((self.ip, self.port))
        print(f"Connected to {self.ip}:{self.port}")

    def modbus_read_holding(self, address, quantity=1, unit=1):
        """Modbus 03功能码测试"""
        trans_id = 1
        # MBAP头 + 功能码03 + 起始地址 + 数量
        mbap = struct.pack('>HHHB', trans_id, 0, 6, unit)
        pdu = struct.pack('>BHH', 3, address, quantity)
        request = mbap + pdu
        self.sock.send(request)
        response = self.sock.recv(1024)
        return response.hex()

    def send_raw_hex(self, hex_string):
        """发送原始十六进制数据"""
        data = bytes.fromhex(hex_string)
        self.sock.send(data)
        return self.sock.recv(1024)

    def close(self):
        if self.sock:
            self.sock.close()


# 使用示例
tester = PLC_Tester('192.168.4.100', 502)
tester.connect()
print(tester.modbus_read_holding(0, 2))
tester.close()