import pika


class PythonMq:

    def __init__(self, localhost, port, username, password, queue_name, message):
        self.localhost = localhost
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name
        self.message = message

    def message_push(self):
        # 设置 RabbitMQ 服务器的连接参数
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(self.localhost,
                                               self.port,
                                               '/',
                                               credentials)

        # 建立与 RabbitMQ 的连接
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # 声明队列
        channel.queue_declare(queue=self.queue_name, durable=True)

        # 发送消息
        channel.basic_publish(exchange='',
                              routing_key=self.queue_name,
                              body=self.message)

        print(f"[x] Sent {self.message}")
        # 关闭连接
        connection.close()
        return self

if __name__ == '__main__':
    localhost = "uat-rabbitmq_01.elecfant.net"
    port = 5672
    username = "hqjf"
    password = "LNE1gk0sjgKera7B1rgBFT2UtpxCiMo9"
    queue_name = "shopping-maintain_insert"
    message = ''
    PythonMq(localhost, port, username, password, queue_name, message).message_push()
