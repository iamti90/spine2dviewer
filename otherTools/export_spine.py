import os
import sys
import subprocess
import msvcrt

# ================= CAU HINH DUONG DAN =================
SPINE_EXE = r"C:\Program Files\Spine\Spine.exe" 

# Lấy thư mục chứa file script hiện tại bằng thư viện os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_SETTINGS = os.path.join(CURRENT_DIR, "json_settings.json")
# =======================================================

def get_spine_files(input_paths):
    """Sử dụng thư viện os để tìm toàn bộ file .spine trong các đường dẫn"""
    spine_files = []
    
    for p in input_paths:
        # Làm sạch dấu ngoặc kép bọc ngoài do Windows tự thêm khi kéo thả folder có dấu cách
        clean_path = p.strip('"\' ')
        if not clean_path:
            continue
            
        # Kiểm tra đường dẫn có tồn tại không
        if not os.path.exists(clean_path):
            print(f"[Canh bao] Duong dan khong ton tai: {clean_path}")
            continue
            
        # Nếu là file đơn lẻ
        if os.path.isfile(clean_path):
            if clean_path.lower().endswith('.spine'):
                spine_files.append(clean_path)
                
        # Nếu là thư mục, dùng os.walk để quét toàn bộ file bên trong (kể cả thư mục con)
        elif os.path.isdir(clean_path):
            for root, dirs, files in os.walk(clean_path):
                for file in files:
                    if file.lower().endswith('.spine'):
                        full_path = os.path.join(root, file)
                        spine_files.append(full_path)
                        
    # Loại bỏ các đường dẫn trùng lặp nếu có và sắp xếp lại cho đẹp
    return sorted(list(set(spine_files)))

def main():
    print("=== TOOL EXPORT SPINE RA JSON/GIF TU DONG (OS VERSION) ===")
    
    if not os.path.exists(EXPORT_SETTINGS):
        print(f"\n[LOI] Khong tim thay file json_settings.json!")
        print(f"Vui long luu file cau hinh tu Spine va de vao thu muc:\n{CURRENT_DIR}")
        input("\nNhan Enter de thoat...")
        return

    # Trường hợp 1: Nhận đường dẫn khi kéo thả trực tiếp vào file .bat
    raw_inputs = sys.argv[1:]

    # Trường hợp 2: Mở tool lên rồi mới kéo thả thư mục vào cửa sổ dòng lệnh
    if not raw_inputs:
        print("[Huong dan] Keo tha Folder vao file .bat hoac cua so nay de chay tool.")
        user_input = input("Keo tha folder vao day roi nhan Enter: ").strip()
        if not user_input:
            return
        
        # Mẹo xử lý dấu cách: Nếu kéo thả 1 folder có dấu cách, Windows sẽ bọc cả chuỗi trong cặp ""
        # Ta chỉ cần đưa nguyên chuỗi đó vào list, hàm get_spine_files sẽ tự gạt dấu "" ra
        raw_inputs = [user_input]

    # Tìm kiếm toàn bộ file .spine bằng thư viện os
    spine_files = get_spine_files(raw_inputs)
    total_files = len(spine_files)

    if not spine_files:
        print("\n[Canh bao] Khong tim thay file .spine nao trong thu muc da chon.")
        input("Nhan Enter de thoat...")
        return

    print(f"\n[OK] Tim thay {total_files} file .spine.")
    print("\n>>> DANG CHAY... BAM PHIM SPACE (DAU CACH) DE DUNG LAI GIUA CHUNG <<<\n")
    print("-" * 50)

    # Sử dụng enumerate để lấy số thứ tự (bắt đầu từ 1)
    for index, file_path in enumerate(spine_files, start=1):
        # Kiểm tra bấm phím Space để hủy tiến trình giữa chừng
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b' ':  
                print("\n[DA HUY] Ban vua nhan Space. Tool da dung lai an toan!")
                break 
            else:
                while msvcrt.kbhit(): msvcrt.getch()

        # Lấy tên file và thư mục chứa file bằng os.path
        file_name = os.path.basename(file_path)
        output_dir = os.path.dirname(file_path)

        # Hiển thị tiến độ theo định dạng [Hiện tại/Tổng số]
        print(f"[{index}/{total_files}] Dang xu ly: {file_name}...")

        # Cấu hình lệnh gọi Spine CLI an toàn với khoảng trắng
        command = [
            SPINE_EXE,
            "-i", file_path,
            "-o", output_dir,
            "-e", EXPORT_SETTINGS
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print(f" -> Thanh cong")
        except subprocess.CalledProcessError:
            print(f" -> [LOI] Khong the xuat {file_name}. Vui long kiem tra file settings hoac phien ban Spine.")
        except FileNotFoundError:
            print(f" -> [LOI] Khong tim thay file Spine.exe tai: {SPINE_EXE}")
            break

    print("-" * 50)
    print("Qua trinh hoan tat!")
    input("Nhan Enter de dong cua so...")

if __name__ == "__main__":
    main()