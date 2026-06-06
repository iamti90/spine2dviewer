import os
import time


def delete_spine_by_json_reference(target_directory):
    deleted_count = 0

    print(
        f"\n[!] Bắt đầu quét: Tìm file .json để xoá các file .atlas, .atlas.txt và .png trùng tên...\n"
    )

    # os.walk duyệt qua tất cả thư mục con
    for root, dirs, files in os.walk(target_directory):

        # Bước 1: Tìm tất cả các file .json trong thư mục hiện tại
        # Lấy ra phần tên (không bao gồm đuôi) của các file .json
        json_names = set()
        for file in files:
            file_name, file_ext = os.path.splitext(file)
            if file_ext.lower() == ".json":
                json_names.add(file_name.lower())

        # Nếu thư mục này không có file .json nào, bỏ qua và đi tiếp
        if not json_names:
            continue

        # Bước 2: Duyệt lại các file để xoá file .png và .atlas trùng tên với file .json
        for file in files:
            file_lower = file.lower()
            
            # Khởi tạo biến để kiểm tra xem file có khớp tên json không
            is_target_file = False
            
            # Xử lý riêng cho trường hợp đuôi phức tạp .atlas.txt
            if file_lower.endswith(".atlas.txt"):
                # Lấy phần tên trước .atlas.txt (bỏ đi 10 ký tự cuối)
                pure_name = file_lower[:-10]
                if pure_name in json_names:
                    is_target_file = True
            
            # Xử lý cho các đuôi đơn bình thường (.png, .atlas, .json)
            else:
                file_name, file_ext = os.path.splitext(file)
                if file_ext.lower() in (".png", ".atlas", ".json"):
                    if file_name.lower() in json_names:
                        is_target_file = True

            # Tiến hành xoá nếu thoả mãn điều kiện
            if is_target_file:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Đã xoá: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Lỗi không thể xoá {file_path}: {e}")

    print(
        f"\n--- Hoàn thành! Đã xoá tổng cộng {deleted_count} file dựa theo file .json. ---"
    )


# --- CHƯƠNG TRÌNH CHÍNH ---
if __name__ == "__main__":
    print("=== CHƯƠNG TRÌNH XOÁ FILE THEO THAM CHIẾU .json ===")

    while True:
        thu_muc_nhap = input(
            "\nNhập hoặc kéo thả thư mục vào đây rồi ấn Enter: "
        ).strip()
        thu_muc_nhap = thu_muc_nhap.strip('"').strip("'")

        if os.path.exists(thu_muc_nhap) and os.path.isdir(thu_muc_nhap):
            xac_nhan = input(
                f"Bạn có chắc chắn muốn xoá các bộ file có chứa file .json trong '{thu_muc_nhap}'? (y/n): "
            )
            if xac_nhan.lower() == "y":
                delete_spine_by_json_reference(thu_muc_nhap)
            else:
                print("Đã huỷ thao tác xử lý thư mục này.")
        else:
            print(
                "Đường dẫn không hợp lệ hoặc thư mục không tồn tại! Vui lòng kiểm tra lại."
            )

        # Hỏi người dùng có muốn tiếp tục với thư mục khác không
        tiep_tuc = input("\nBạn có muốn tiếp tục xoá ở thư mục khác không? (y/n): ")
        if tiep_tuc.lower() != "y":
            print("\n👋 Cảm ơn bạn đã sử dụng tool - tihihi")
            print("\nDang thoat sau 2 giay...")
            time.sleep(2)
            break