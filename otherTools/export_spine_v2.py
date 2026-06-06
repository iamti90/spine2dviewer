import os
import sys
import subprocess
import re
from pathlib import Path
import msvcrt
import time

# ================= CAU HINH DUONG DAN =================
SPINE_EXE = r"C:\Program Files\Spine\Spine.exe" 

CURRENT_DIR = Path(__file__).parent.resolve()
EXPORT_SETTINGS = CURRENT_DIR / "json_settings.json"
# =======================================================

def get_spine_files(input_paths):
    spine_files = []
    for p in input_paths:
        path = Path(p.strip('"\' '))
        if not path.exists():
            continue
            
        if path.is_file() and path.suffix.lower() == '.spine':
            spine_files.append(path)
        elif path.is_dir():
            spine_files.extend(path.rglob('*.spine'))
            
    return list(set(spine_files))

def rename_and_fix_atlas(file_path, files_before):
    """
    Đợi cả 3 file (.json, .atlas.txt, .png) mặc định xuất hiện đầy đủ,
    sau đó đổi tên đồng loạt về tên file .spine.
    """
    output_dir = file_path.parent
    file_name_clean = file_path.stem  # Tên mong muốn (tên file .spine)
    parent_name = output_dir.name     # Tên mặc định Spine sẽ tạo (tên folder cha)
    
    # SỬA TẠI ĐÂY: Định nghĩa đường dẫn 3 file mặc định ban đầu theo cấu hình .atlas.txt của bạn
    default_json = output_dir / f"{parent_name}.json"
    default_atlas = output_dir / f"{parent_name}.atlas.txt"  # Đổi đuôi mặc định chờ thành .atlas.txt
    default_png = output_dir / f"{parent_name}.png"
    
    # --- Vòng lặp chờ ĐỦ CẢ 3 FILE xuất hiện trên ổ cứng ---
    timeout = 15  
    start_time = time.time()
    while True:
        if default_json.exists() and default_atlas.exists() and default_png.exists():
            break
            
        time.sleep(0.2)
        if time.time() - start_time > timeout:
            print(f" -> [Canh bao] Qua thoi gian cho bo ba file ({parent_name}) xuat hien. Bo qua doi ten.")
            return

    # Trễ 0.5s để chắc chắn Windows đã thả khóa (unlock) hoàn toàn các file
    time.sleep(0.5)

    # 1. Xử lý đổi tên file .json mặc định sang tên file .spine
    if default_json.exists():
        final_json_path = output_dir / f"{file_name_clean}.json"
        if final_json_path.exists() and final_json_path != default_json: 
            os.remove(final_json_path)
        try:
            default_json.rename(final_json_path)
        except Exception as e:
            print(f" -> [LOI] Khong the doi ten file json: {e}")

    # 2. Xử lý đổi tên file .atlas.txt mặc định thành [tên_file].atlas.txt và sửa ruột
    if default_atlas.exists():
        new_atlas_path = output_dir / f"{file_name_clean}.atlas.txt"
        
        old_png_name = f"{parent_name}.png"
        new_png_name = f"{file_name_clean}.png"
        
        if new_atlas_path.exists() and new_atlas_path != default_atlas: 
            os.remove(new_atlas_path)
        
        try:
            default_atlas.rename(new_atlas_path)
            # Đọc và sửa nội dung liên kết ảnh bên trong file .atlas.txt mới tạo
            atlas_content = new_atlas_path.read_text(encoding='utf-8')
            if old_png_name in atlas_content:
                updated_content = atlas_content.replace(old_png_name, new_png_name)
                new_atlas_path.write_text(updated_content, encoding='utf-8')
        except Exception as e:
            print(f" -> [LOI] Khong the doi ten/sua file .atlas.txt: {e}")

    # 3. Xử lý đổi tên file .png mặc định sang tên file .spine
    if default_png.exists():
        new_png_path = output_dir / f"{file_name_clean}.png"
        if new_png_path.exists() and new_png_path != default_png: 
            os.remove(new_png_path)
        try:
            default_png.rename(new_png_path)
        except Exception as e:
            print(f" -> [LOI] Khong the doi ten file png: {e}")

def main():
    print("=== TOOL EXPORT SPINE RA JSON + AUTO RENAME (.ATLAS.TXT CO SAN) ===")
    
    if not EXPORT_SETTINGS.exists():
        print(f"\n[LOI] Khong tim thay file {EXPORT_SETTINGS.name}!")
        print(f"Vui long luu file cau hinh tu Spine va de vao thu muc:\n{CURRENT_DIR}")
        input("\nNhan Enter de thoat...")
        return

    input_paths = sys.argv[1:]

    if not input_paths:
        print("[Huong dan] Keo tha Folder vao file .bat de chay tool.")
        user_input = input("Hoac keo tha folder vao day roi nhan Enter: ")
        if not user_input.strip():
            return
        input_paths = [p[0] or p[1] for p in re.findall(r'"([^"]*)"|([^\s]+)', user_input)]

    spine_files = get_spine_files(input_paths)

    if not spine_files:
        print("\n[Canh bao] Khong tim thay file .spine nao trong folder vua chon.")
        input("Nhan Enter de thoat...")
        return

    print(f"\n[OK] Tim thay {len(spine_files)} file .spine.")
    print(f"[Dich den] Doi ten tu file (.atlas.txt goc) thanh bo ba trung ten file .spine")
    print("\n>>> DANG CHAY... BAM PHIM SPACE (DAU CACH) DE DUNG LAI GIUA CHUNG <<<\n")
    print("-" * 50)

    for file_path in spine_files:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b' ':  
                print("\n[DA HUY] Ban vua nhan Space. Tool da dung lai an toan!")
                break 
            else:
                while msvcrt.kbhit(): msvcrt.getch()

        print(f"Dang xu ly: {file_path.name}...")
        
        output_dir = file_path.parent
        output_file = output_dir 

        # Chụp lại trạng thái folder trước khi export
        files_before = set(output_dir.iterdir())

        command = [
            SPINE_EXE,
            "-i", str(file_path),
            "-o", str(output_file),
            "-e", str(EXPORT_SETTINGS)
        ]

        try:
            # Chạy lệnh xuất của Spine
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            
            # Đổi tên trực tiếp dựa trên file gốc mang đuôi .atlas.txt
            rename_and_fix_atlas(file_path, files_before)
            
            print(f" -> Thanh cong: Bo ba file (.json, .atlas.txt, .png) da dong bo theo: {file_path.stem}")
        except subprocess.CalledProcessError:
            print(f" -> [LOI] Khong the xuat {file_path.name}")
        except FileNotFoundError:
            print(f" -> [LOI] Khong tim thay file Spine.exe tai: {SPINE_EXE}")
            break

    print("-" * 50)
    print("Qua trinh hoan tat!")
    input("Nhan Enter de dong cua so...")

if __name__ == "__main__":
    main()