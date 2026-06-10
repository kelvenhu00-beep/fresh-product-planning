"""全年水果采购计划系统 - 局域网同步服务

替代 `python -m http.server`，额外提供 /state 端点用于多设备共享数据。

启动：
    python3 procurement_server.py

端点：
    GET  /                    → 静态文件（index.html 等）
    GET  /state               → 当前状态 JSON（多设备共享）
    POST /state               → 写入新状态（任意设备保存时自动调用）

存储：在脚本同目录生成 state.json（原子写入，写前先写 .tmp 再 rename）
"""

import http.server
import json
import os
import socketserver
import sys
import threading

HOST = '0.0.0.0'
PORT = 8765
STATE_FILE = 'state.json'
DIR = os.path.dirname(os.path.abspath(__file__))
lock = threading.Lock()


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 允许跨设备访问；LAN 部署放开 CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path == '/state':
            self._send_state()
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/state':
            self._save_state()
            return
        self.send_error(404)

    def _send_state(self):
        path = os.path.join(DIR, STATE_FILE)
        with lock:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    body = f.read()
            else:
                body = b'{}'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _save_state(self):
        length = int(self.headers.get('Content-Length', 0))
        if length <= 0 or length > 20_000_000:
            self.send_error(400, 'Bad payload size')
            return
        raw = self.rfile.read(length)
        try:
            json.loads(raw)
        except json.JSONDecodeError as e:
            self.send_error(400, f'Invalid JSON: {e}')
            return
        target = os.path.join(DIR, STATE_FILE)
        tmp = target + '.tmp'
        with lock:
            with open(tmp, 'wb') as f:
                f.write(raw)
            os.replace(tmp, target)
        body = b'{"ok":true}'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # 简化日志：只打非 200 状态或 POST
        try:
            if self.command == 'POST' or '200' not in (args[1] if len(args) > 1 else ''):
                sys.stderr.write(f'[{self.command}] {self.path}\n')
        except Exception:
            pass


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


if __name__ == '__main__':
    os.chdir(DIR)
    print(f'Procurement LAN server starting at http://{HOST}:{PORT}')
    print(f'State file: {os.path.join(DIR, STATE_FILE)}')
    print('GET  /state — 返回当前状态 JSON')
    print('POST /state — 保存状态 JSON（覆盖式）')
    print('Ctrl+C 退出\n')
    try:
        ThreadingServer((HOST, PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.')
