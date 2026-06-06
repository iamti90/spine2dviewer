import os
import sys
import webview
import http.server
import threading
import socket
import json
from urllib.parse import unquote

# --- CẤU HÌNH ---
PORT = 8080

def get_resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối đến tài nguyên, hỗ trợ cả khi chạy dev và EXE """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class SpineHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        requested_path = unquote(self.path).lstrip('/')
        if os.path.isfile(requested_path):
            try:
                with open(requested_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                if requested_path.endswith('.png'):
                    self.send_header('Content-Type', 'image/png')
                elif requested_path.endswith('.atlas') or requested_path.endswith('.txt'):
                    self.send_header('Content-Type', 'text/plain')
                else:
                    self.send_header('Content-Type', self.guess_type(requested_path))
                
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                self.wfile.write(content)
                return
            except Exception as e:
                print(f"Lỗi truyền tải file: {e}")
        super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def log_message(self, format, *args):
        pass

def run_server():
    server_address = ('127.0.0.1', PORT)
    httpd = http.server.HTTPServer(server_address, SpineHandler)
    httpd.serve_forever()

class Api:
    def __init__(self):
        self.current_path = None

    def select_folder(self):
        window = webview.active_window()
        result = window.create_file_dialog(webview.FOLDER_DIALOG)
        if result:
            folder_path = result[0]
            self.current_path = folder_path
            os.chdir(folder_path)
            return self.scan_spine_files(folder_path)
        return None

    def scan_spine_files(self, path):
        spine_data = []
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".json"):
                    base_name = file.rsplit('.', 1)[0]
                    atlas_file = next((f for f in files if f == f"{base_name}.atlas.txt" or f == f"{base_name}.atlas"), None)
                    
                    if atlas_file:
                        spine_version = "Unknown"
                        full_file_path = os.path.join(root, file)
                        
                        # 1. Đọc và lấy thông tin version trong JSON
                        try:
                            with open(full_file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if 'skeleton' in data and 'spine' in data['skeleton']:
                                    spine_version = str(data['skeleton']['spine'])
                        except Exception as e:
                            print(f"Không thể đọc thông tin của {file}: {e}")
                            continue  # Nếu file JSON lỗi cấu trúc, bỏ qua không load

                        # 2. KIỂM TRA ĐIỀU KIỆN LỌC PHIÊN BẢN (Chỉ lấy >= 3.8)
                        try:
                            # Lấy phần số chính (Ví dụ: "3.8.99" -> 3.8, "4.0.12" -> 4.0)
                            version_float = float('.'.join(spine_version.split('.')[:2]))
                            if version_float < 3.8:
                                print(f"-> Bỏ qua file {file} vì thuộc phiên bản cũ v{spine_version}")
                                continue  # Bỏ qua file này, chạy sang vòng lặp tiếp theo
                        except ValueError:
                            # Phòng trường hợp chuỗi version không đúng định dạng số
                            if spine_version != "Unknown" and spine_version < "3.8":
                                continue

                        # 3. Đạt điều kiện -> Thêm vào danh sách hiển thị
                        rel_root = os.path.relpath(root, ".").replace("\\", "/")
                        prefix = "" if rel_root == "." else rel_root + "/"
                        display_folder = os.path.basename(root) if rel_root != "." else "Gốc"
                        
                        spine_data.append({
                            "name": file,
                            "folder_display": display_folder,
                            "json": f"http://127.0.0.1:{PORT}/{prefix}{file}",
                            "atlas": f"http://127.0.0.1:{PORT}/{prefix}{atlas_file}",
                            "use_bound": False,
                            "version": spine_version
                        })
        return spine_data

if __name__ == '__main__':
    threading.Thread(target=run_server, daemon=True).start()
    html_path = get_resource_path("index_v5.html")
    api = Api()
    window = webview.create_window(
        title="SpineViewer Pro",
        url=html_path,
        js_api=api,
        width=1200,
        height=850,
        background_color='#121212',
    )
    webview.start(debug=True)