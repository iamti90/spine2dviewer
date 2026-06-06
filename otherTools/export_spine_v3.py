import os
import sys
import subprocess
import re
import msvcrt
import time

# ================= CAU HINH DUONG DAN =================
SPINE_EXE = r"C:\Program Files\Spine\Spine.exe" 

# KIỂM TRA ĐƯỜNG DẪN THỰC TẾ (Sửa lỗi PyInstaller .exe không tìm thấy json_settings)
if getattr(sys, 'frozen', False):
    CURRENT_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

EXPORT_SETTINGS = os.path.join(CURRENT_DIR, "json_settings.json")
# =======================================================

def get_spine_files(input_paths):
    """Sử dụng thư viện os để tìm toàn bộ file .spine trong các đường dẫn"""
    spine_files = []
    
    for p in input_paths:
        clean_path = p.strip('"\' ')
        if not clean_path:
            continue
            
        if not os.path.exists(clean_path):
            print(f"[Canh bao] Duong dan khong ton tai: {clean_path}")
            continue
            
        if os.path.isfile(clean_path):
            if clean_path.lower().endswith('.spine'):
                spine_files.append(clean_path)
                
        elif os.path.isdir(clean_path):
            for root, dirs, files in os.walk(clean_path):
                for file in files:
                    if file.lower().endswith('.spine'):
                        full_path = os.path.join(root, file)
                        spine_files.append(full_path)
                        
    return sorted(list(set(spine_files)))

def check_export_output(output_dir):
    """Kiểm tra xem thư mục có tồn tại đầy đủ cả 3 đuôi file json, atlas (hoặc atlas.txt) và png hay không"""
    has_json = False
    has_atlas = False
    has_png = False

    try:
        all_files = os.listdir(output_dir)
    except Exception:
        return False

    for file in all_files:
        file_lower = file.lower()
        if file_lower.endswith(".json"):
            has_json = True
        if file_lower.endswith(".atlas") or file_lower.endswith(".atlas.txt"):
            has_atlas = True
        if file_lower.endswith(".png"):
            has_png = True

        if has_json and has_atlas and has_png:
            return True

    return has_json and has_atlas and has_png

def main():
    if not os.path.exists(EXPORT_SETTINGS):
        print("=== TOOL EXPORT SPINE RA JSON ===")
        print(f"[LOI] Khong tim thay file json_settings.json!")
        print(f"Vui long luu file cau hinh tu Spine va de vao thu muc:\n{CURRENT_DIR}")
        input("\nNhan Enter de thoat...")
        return

    # 1. HỎI NGƯỜI DÙNG PHIÊN BẢN SPINE (CHỈ HỎI 1 LẦN DUY NHẤT LÚC MỞ TOOL)
    print("=== TOOL EXPORT SPINE RA JSON ===\n")
    spine_version = ""
    while True:
        print("Nhap phien ban Spine muon chay (Vi du: 3.7.93, 3.8.99, 4.1.24...)")
        user_version = input("De trong nuon dung ban mac dinh [3.8.99]: ").strip()
        
        if not user_version:
            spine_version = "3.8.99"
            break
            
        if re.match(r"^[0-9.]+$", user_version):
            spine_version = user_version
            break
        else:
            print("\n[LOI CHU Y] Phien ban khong hop le! Vui long chi nhap so va dau cham (.), khong nhap chu.\n")

    print(f"-> Sẽ su dung Spine phien ban: {spine_version}\n")
    print("-" * 50)

    # VÒNG LẶP CHÍNH: HỎI CÓ MUỐN EXPORT TIẾP KHÔNG
    while True:
        # 2. XỬ LÝ ĐƯỜNG DẪN INPUT TRONG VÒNG LẶP
        raw_inputs = sys.argv[1:]

        # Nếu không có tham số kéo thả từ bên ngoài file .exe/.bat, bắt đầu hỏi trong CMD
        if not raw_inputs:
            print("[Huong dan] Keo tha Folder vao cua so nay de chay tool.")
            user_input = input("Keo tha folder vao day roi nhan Enter: ").strip()
            if not user_input:
                print("[Canh bao] Duong dan trong!")
                continue
            raw_inputs = [user_input]
        else:
            # Nếu người dùng kéo thả trực tiếp vào file .exe/.bat từ bên ngoài Windows Explorer,
            # hệ thống sẽ lấy tham số đó chạy 1 lần. Sau đó dọn dẹp biến sys.argv để vòng lặp sau bắt đầu nhận input thủ công.
            sys.argv = [sys.argv[0]] 

        # Tìm kiếm toàn bộ file .spine
        spine_files = get_spine_files(raw_inputs)
        total_files = len(spine_files)

        if not spine_files:
            print("\n[Canh bao] Khong tim thay file .spine nao trong thu muc da chon.")
        else:
            print(f"\n[OK] Tim thay {total_files} file .spine.")
            print("\n>>> DANG CHAY... BAM PHIM SPACE (DAU CACH) DE DUNG LAI GIUA CHUNG <<<\n")
            print("-" * 50)

            # 3. VÒNG LẶP EXPORT FILE
            for index, file_path in enumerate(spine_files, start=1):
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b' ':  
                        print("\n[DA HUY] Ban vua nhan Space. Tool da dung lai an toan!")
                        break 
                    else:
                        while msvcrt.kbhit(): msvcrt.getch()

                file_name = os.path.basename(file_path)
                output_dir = os.path.dirname(file_path)

                print(f"[{index}/{total_files}] Dang xu ly: {file_name}...")

                command = [
                    SPINE_EXE,
                    "-u", spine_version, 
                    "-i", file_path,
                    "-o", output_dir,
                    "-e", EXPORT_SETTINGS
                ]

                try:
                    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                    
                    if check_export_output(output_dir):
                        print(f" -> Thanh cong")
                    else:
                        print(f" -> [LOI] Thieu file! Khong tim thay du bo .json, .atlas, va .png trong thu muc.")
                except subprocess.CalledProcessError:
                    print(f" -> [LOI CRASH] Khong the xuat {file_name}. Kiem tra phien ban hoac file settings.")
                except FileNotFoundError:
                    print(f" -> [LOI] Khong tim thay file Spine.exe tai: {SPINE_EXE}")
                    break

            print("-" * 50)
            print("Qua trinh export thu muc nay hoan tat!")

        # 4. HỎI NGƯỜI DÙNG CÓ MUỐN TIẾP TỤC KHÔNG
        print("\n" + "="*40)
        tiep_tuc = input("Ban co muon tiep tuc export thu muc khac khong? (Y/N) [Y]: ").strip().lower()
        print("="*40 + "\n")
        
        if tiep_tuc == 'n':
            print("\n👋 Cam on ban da su dung tool - tihihi")
            print("\nDang thoat sau 2 giay...")
            time.sleep(2)
            break
        else:
            # Lệnh xóa màn hình Console cho sạch sẽ trước khi nhận folder mới (Windows sử dụng 'cls')
            os.system('cls')
            print(f"=== TOOL EXPORT SPINE RA JSON ===")
            print(f"-> Phien ban Spine dang dung: {spine_version}\n")

if __name__ == "__main__":
    main()