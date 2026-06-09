import os
import sys
import subprocess
import re
import msvcrt
import time

# ================= PATH CONFIGURATION =================
SPINE_EXE = r"C:\Program Files\Spine\Spine.exe" 

# VERIFY ACTUAL PATH (Fixes issue where PyInstaller .exe cannot find json_settings)
if getattr(sys, 'frozen', False):
    CURRENT_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

EXPORT_SETTINGS = os.path.join(CURRENT_DIR, "json_settings.json")
ERROR_LOG_FILE = os.path.join(CURRENT_DIR, "export_error.txt")
# =======================================================

# Global variable to mark the first error logged in this session
IS_FIRST_ERROR_IN_SESSION = True

def get_spine_files(input_paths):
    """Use os library to find all .spine files in the provided paths"""
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

def check_export_output(output_dir, spine_base_name):
    """UPDATED: Check if after running Spine, the folder generates a complete set of 3 files
    (.json, .atlas, and .png) matching EXACTLY the name of that .spine file"""
    has_json = False
    has_atlas = False
    has_png = False
    
    name_lower = spine_base_name.lower()

    try:
        all_files = os.listdir(output_dir)
    except Exception:
        return False

    for file in all_files:
        file_lower = file.lower()
        
        # Check for json file matching the spine file name
        if file_lower == f"{name_lower}.json":
            has_json = True
        # Check for atlas file matching the spine file name
        if file_lower == f"{name_lower}.atlas" or file_lower == f"{name_lower}.atlas.txt":
            has_atlas = True
        # Check for image file matching the spine file name (or subsequent page packs)
        if file_lower == f"{name_lower}.png" or file_lower.startswith(f"{name_lower}2.png") or file_lower.startswith(f"{name_lower}_2.png"):
            has_png = True

        # If a complete set with matching name is found, return True immediately
        if has_json and has_atlas and has_png:
            return True

    return has_json and has_atlas and has_png

def check_existing_files_by_spine(spine_file_path):
    """Take the .spine filename as standard to cross-check if complete sets of matching .json, .atlas, and .png exist"""
    output_dir = os.path.dirname(spine_file_path)
    file_name = os.path.basename(spine_file_path)
    
    # Get base name without .spine extension
    spine_base_name, _ = os.path.splitext(file_name)
    name_lower = spine_base_name.lower()

    try:
        all_files = os.listdir(output_dir)
    except Exception:
        return False

    has_json = False
    has_atlas = False
    has_png = False

    for file in all_files:
        file_lower = file.lower()
        # Check for json file matching the spine file name
        if file_lower == f"{name_lower}.json":
            has_json = True
        # Check for atlas file matching the spine file name
        if file_lower == f"{name_lower}.atlas" or file_lower == f"{name_lower}.atlas.txt":
            has_atlas = True
        # Check for image file matching the spine file name (or subsequent pack sheets e.g., name2.png, name_2.png)
        if file_lower == f"{name_lower}.png" or file_lower.startswith(f"{name_lower}2.png") or file_lower.startswith(f"{name_lower}_2.png"):
            has_png = True

    # If the name matches and all 3 components exist, consider it completed
    if has_json and has_atlas and has_png:
        return True

    return False

def log_single_error(file_path):
    """Append the error file path directly into export_error.txt"""
    global IS_FIRST_ERROR_IN_SESSION
    try:
        # Append mode "a" adds new lines to the end of the file without overwriting old content
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            # If this is the first error encountered since the tool started
            if IS_FIRST_ERROR_IN_SESSION:
                f.write(f"\n==================================================\n")
                f.write(f"SESSION WITH ERRORS ENCOUNTERED: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"==================================================\n")
                # Change state to False so subsequent files won't re-write this date header
                IS_FIRST_ERROR_IN_SESSION = False
                
            f.write(f"[{time.strftime('%H:%M:%S')}] {file_path}\n")
            print(f" -> Da luu vao file export_error.txt")
    except Exception as e:
        print(f" -> [LOI] Khong the ghi vao file log loi: {e}")

def main():
    if not os.path.exists(EXPORT_SETTINGS):
        print("=== TOOL EXPORT SPINE RA JSON ===")
        print(f"[LOI] Khong tim thay file json_settings.json!")
        print(f"Vui long luu file cau hinh tu Spine va de vao thu muc:\n{CURRENT_DIR}")
        input("\nNhan Enter de thoat...")
        return

    # 1. PROMPT USER FOR SPINE VERSION (ONLY PROMPTED ONCE WHEN OPENING THE TOOL)
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

    # MAIN LOOP: ASK IF USER WANTS TO CONTINUE EXPORTING
    while True:
        # 2. PROCESS INPUT PATHS WITHIN THE LOOP
        raw_inputs = sys.argv[1:]

        # If no drag-and-drop arguments are passed from outside the .exe/.bat, ask via CMD terminal
        if not raw_inputs:
            print("[Huong dan] Keo tha Folder vao cua so nay de chay tool.")
            user_input = input("Keo tha folder vao day roi nhan Enter: ").strip()
            if not user_input:
                print("[Canh bao] Duong dan trong!")
                continue
            raw_inputs = [user_input]
        else:
            # If user drags and drops directly into the .exe/.bat from Windows Explorer,
            # the system takes that argument for one run. Then clear sys.argv so subsequent loops accept manual inputs.
            sys.argv = [sys.argv[0]] 

        # Search for all .spine files
        spine_files = get_spine_files(raw_inputs)
        total_files = len(spine_files)

        if not spine_files:
            print("\n[Canh bao] Khong tim thay file .spine nao trong thu muc da chon.")
        else:
            print(f"\n[OK] Tim thay {total_files} file .spine.")
            print("\n>>> DANG CHAY... BAM PHIM SPACE (DAU CACH) DE DUNG LAI GIUA CHUNG <<<\n")
            print("-" * 50)

            # 3. EXPORT FILE LOOP
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
                spine_clean_name, _ = os.path.splitext(file_name) # Base name of .spine file without extension

                print(f"[{index}/{total_files}] Dang xu ly: {output_dir}\{file_name}...")

                # Pass the file_path of the .spine file to check for existing matching output files
                if check_existing_files_by_spine(file_path):
                    print(f" -> [BO QUA] Phat hien co san file {spine_clean_name}.json cung bo .atlas, .png hoan chinh.")
                    continue  

                command = [
                    SPINE_EXE,
                    "-u", spine_version, 
                    "-i", file_path,
                    "-o", output_dir,
                    "-e", EXPORT_SETTINGS
                ]

                try:
                    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                    
                    # UPDATED: Pass spine_clean_name to ensure precise validation
                    if check_export_output(output_dir, spine_clean_name):
                        print(f" -> Thanh cong")
                    else:
                        print(f" -> [LOI] Export khong thanh cong.")
                        print(f" -> [LOI] Kiem tra lai file source hoặc version Spine2d")
                        log_single_error(file_path) # Append log entry directly
                except subprocess.CalledProcessError:
                    print(f" -> [LOI CRASH] Khong the xuat {file_name}. Kiem tra phien ban hoac file settings.")
                    log_single_error(file_path) # Append log entry directly
                except FileNotFoundError:
                    print(f" -> [LOI] Khong tim thay file Spine.exe tai: {SPINE_EXE}")
                    log_single_error(file_path)
                    break

            print("-" * 50)
            print("Qua trinh export thu muc nay hoan tat!")

        # 4. ASK USER IF THEY WANT TO CONTINUE
        print("\n" + "="*40)
        tiep_tuc = input("Ban co muon tiep tuc export thu muc khac khong? (Y/N) [Y]: ").strip().lower()
        print("="*40 + "\n")
        
        if tiep_tuc == 'n':
            print("\n👋 Cam on ban da su dung tool - tihihi")
            print("\nDang thoat sau 2 giay...")
            time.sleep(2)
            break
        else:
            # Clear console terminal screen for a clean layout before receiving new folder (Windows uses 'cls')
            os.system('cls')
            print(f"=== TOOL EXPORT SPINE RA JSON ===")
            print(f"-> Phien ban Spine dang dung: {spine_version}\n")

if __name__ == "__main__":
    main()
