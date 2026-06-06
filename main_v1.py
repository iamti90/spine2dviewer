import os
import sys
import webview
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

# 1. Các hàm lấy đường dẫn (Giữ nguyên)
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_gui_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

BASE_PATH = get_base_path()
os.chdir(BASE_PATH)

# 2. Sửa Server thủ công để vượt lỗi CORS
PORT = 8080
class MyHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Đây là "chìa khóa" để vượt qua lỗi CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_PATH, **kwargs)

# Chạy server trong một luồng riêng (Giữ nguyên)
def start_server():
    # Allow_reuse_address giúp tránh lỗi cổng đang bận khi khởi động lại app nhanh
    TCPServer.allow_reuse_address = True
    with TCPServer(("", PORT), MyHandler) as httpd:
        httpd.serve_forever()

daemon = threading.Thread(name='daemon_server', target=start_server)
daemon.daemon = True
daemon.start()

# 3. Class API (Giữ nguyên)
class Api:
    def get_spine_files_auto(self):
        spine_data = []
        for root, dirs, files in os.walk(BASE_PATH):
            if "_MEI" in root: continue
            for file in files:
                if file.endswith(".json"):
                    base_name = file.replace(".json", "")
                    atlas = None
                    if f"{base_name}.atlas.txt" in files: atlas = f"{base_name}.atlas.txt"
                    elif f"{base_name}.atlas" in files: atlas = f"{base_name}.atlas"
                    
                    if atlas:
                        rel_root = os.path.relpath(root, BASE_PATH).replace("\\", "/")
                        prefix = "" if rel_root == "." else rel_root + "/"
                        spine_data.append({
                            "name": base_name,
                            "json": f"http://127.0.0.1:{PORT}/{prefix}{file}",
                            "atlas": f"http://127.0.0.1:{PORT}/{prefix}{atlas}"
                        })
        return spine_data

if __name__ == "__main__":
    api = Api()
    html_index = get_gui_path('index.html')
    # Thêm tham số text_select=True để dễ debug nếu cần
    window = webview.create_window('SpineViewer Pro', url=html_index, js_api=api, width=1200, height=900)
    webview.start(debug=True)