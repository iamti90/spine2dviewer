import os
import sys
import webview
import http.server
import threading
import socket
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
        # Giải mã đường dẫn, xử lý khoảng trắng và ký tự tiếng Việt
        requested_path = unquote(self.path).lstrip('/')
        
        # Kiểm tra file tồn tại trên ổ cứng
        if os.path.isfile(requested_path):
            try:
                # Đọc file ở chế độ BINARY tuyệt đối
                with open(requested_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                
                # Thiết lập MIME Type chuẩn xác
                if requested_path.endswith('.skel'):
                    self.send_header('Content-Type', 'application/octet-stream')
                elif requested_path.endswith('.png'):
                    self.send_header('Content-Type', 'image/png')
                elif requested_path.endswith('.atlas') or requested_path.endswith('.txt'):
                    self.send_header('Content-Type', 'text/plain')
                else:
                    self.send_header('Content-Type', self.guess_type(requested_path))
                
                # Gửi các Header quan trọng
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                
                # Ghi trực tiếp mảng byte vào luồng phản hồi
                self.wfile.write(content)
                return
            except Exception as e:
                print(f"Lỗi truyền tải file: {e}")
        
        super().do_GET()

    # Xử lý lệnh OPTIONS cho CORS
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def log_message(self, format, *args):
        pass # Tắt log CMD

def run_server():
    server_address = ('127.0.0.1', PORT)
    httpd = http.server.HTTPServer(server_address, SpineHandler)
    httpd.serve_forever()

# --- API KẾT NỐI GIỮA PYTHON VÀ JAVASCRIPT ---
class Api:
    def __init__(self):
        self.current_path = None

    def select_folder(self):
        # Mở hộp thoại chọn thư mục
        window = webview.active_window()
        result = window.create_file_dialog(webview.FOLDER_DIALOG)
        
        if result:
            folder_path = result[0]
            self.current_path = folder_path
            # Chuyển thư mục làm việc của server về thư mục vừa chọn
            os.chdir(folder_path)
            return self.scan_spine_files(folder_path)
        return None

    def scan_spine_files(self, path):
        spine_data = []
        # Quét toàn bộ thư mục và thư mục con
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".json") or file.endswith(".skel"):
                    is_binary = file.endswith(".skel")
                    base_name = file.rsplit('.', 1)[0]
                    
                    # Tìm file atlas tương ứng (.atlas hoặc .atlas.txt)
                    atlas_file = next((f for f in files if f == f"{base_name}.atlas.txt" or f == f"{base_name}.atlas"), None)
                    
                    if atlas_file:
                        # Chuẩn hóa đường dẫn để gửi sang JS
                        rel_root = os.path.relpath(root, ".").replace("\\", "/")
                        prefix = "" if rel_root == "." else rel_root + "/"
                        display_folder = os.path.basename(root) if rel_root != "." else "Gốc"
                        
                        spine_data.append({
                            "name": file,
                            "folder_display": display_folder,
                            "json": f"http://127.0.0.1:{PORT}/{prefix}{file}",
                            "atlas": f"http://127.0.0.1:{PORT}/{prefix}{atlas_file}",
                            "is_binary": is_binary,
                            "use_bound": False # Mặc định không dùng viewport thủ công
                        })
        return spine_data

# --- KHỞI CHẠY ỨNG DỤNG ---
if __name__ == '__main__':
    # 1. Chạy Server ở luồng riêng
    threading.Thread(target=run_server, daemon=True).start()

    # 2. Xác định đường dẫn index.html
    html_path = get_resource_path("index.html")
    
    # 3. Tạo API và Cửa sổ
    api = Api()
    window = webview.create_window(
        title="SpineViewer Pro",
        url=html_path,
        js_api=api,
        width=1200,
        height=850,
        background_color='#121212',
    )

    # 4. Chạy ứng dụng
    webview.start(debug=True)