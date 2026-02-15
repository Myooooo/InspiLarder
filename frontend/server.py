#!/usr/bin/env python3
"""
灵感食仓前端服务器 - 支持SPA路由
所有非文件请求都返回index.html
"""
import http.server
import socketserver
import os
from pathlib import Path

PORT = 3000

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def do_GET(self):
        path = self.path.split('?')[0]
        file_path = Path(self.directory) / path.lstrip('/')
        
        if file_path.is_file():
            return super().do_GET()
        
        if file_path.is_dir() and (file_path / 'index.html').exists():
            self.path = str(path.rstrip('/') + '/index.html')
            return super().do_GET()
        
        self.path = '/index.html'
        return super().do_GET()
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), SPAHandler) as httpd:
        print(f"🚀 灵感食仓前端服务器启动成功!")
        print(f"📱 访问地址: http://localhost:{PORT}")
        print(f"✨ 支持SPA路由，刷新页面不会404")
        print(f"🛑 按 Ctrl+C 停止服务器")
        print("-" * 50)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")
