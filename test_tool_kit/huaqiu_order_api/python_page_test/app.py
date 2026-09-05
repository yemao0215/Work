from flask import Flask, render_template
from flask_socketio import SocketIO
import logging
from collections import deque

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

log_buffer = deque(maxlen=100)

class SocketIOLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_buffer.append(log_entry)
        socketio.emit('new_log', log_entry)  # 主动推送日志到前端

# 配置日志
socketio_handler = SocketIOLogHandler()
socketio_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
app.logger.addHandler(socketio_handler)
app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('logs_websocket.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)