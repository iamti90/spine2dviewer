import os
import sys

def rename_spine_files(target_dir):
    print(f"\n=== BẮT ĐẦU ĐỔI TÊN FILE .spine TRONG THƯ MỤC: {target_dir} ===")
    
    count = 0
    # Duyệt qua tất cả các thư mục và thư mục con
    for root, dirs, files in os.walk(target_dir):
        # Lấy tên thư mục cha trực tiếp của các file hiện tại
        parent_dir_name = os.path.basename(root)
        
        # Bỏ qua nếu là thư mục gốc không có tên (trường hợp ổ đĩa gốc như D:\, C:\)
        if not parent_dir_name:
            continue
            
        # Tìm các file có đuôi .spine
        for file in files:
            if file.lower().endswith('.spine'):
                # Tách phần mở rộng để giữ lại chính xác (.spine hoặc .SPINE)
                _, ext = os.path.splitext(file)
                
                # Tạo đường dẫn đầy đủ của file cũ
                old_file_path = os.path.join(root, file)
                
                # Tạo tên file mới dựa trên tên thư mục cha
                new_file_name = parent_dir_name + ext
                new_file_path = os.path.join(root, new_file_name)
                
                # Kiểm tra nếu tên file mới trùng tên cũ thì bỏ qua
                if old_file_path == new_file_path:
                    continue
                
                try:
                    # Tiến hành đổi tên
                    os.rename(old_file_path, new_file_path)
                    print(f" Đã đổi: {file} -> {new_file_name} (Trong: {root})")
                    count += 1
                except Exception as e:
                    print(f"❌ Lỗi khi đổi tên file {file}: {e}")
                    
    print(f"\n=== HOÀN THÀNH. ĐÀ ĐỔI TÊN TỔNG CỘNG {count} FILE ===")

if __name__ == "__main__":
    # Yêu cầu người dùng tự nhập đường dẫn bằng tay
    folder_input = input("Vui lòng nhập hoặc kéo thả đường dẫn thư mục vào đây: ").strip()
    
    # Loại bỏ dấu ngoặc kép ở 2 đầu nếu người dùng kéo thả thư mục vào Terminal
    folder_input = folder_input.strip('"').strip("'")
    
    if os.path.exists(folder_input) and os.path.isdir(folder_input):
        rename_spine_files(folder_input)
    else:
        print("❌ Đường dẫn không hợp lệ hoặc thư mục không tồn tại. Vui lòng kiểm tra lại!")
        
    # Giữ cửa sổ terminal không bị tắt ngay sau khi chạy xong (đối với Windows)
    input("\nNhấn Enter để thoát...")