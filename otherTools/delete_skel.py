import os
import time


def delete_spine_by_skel_reference(target_directory):
    deleted_count = 0

    print(
        f"\n[!] Bắt đầu quét: Tìm file .skel để xoá các file .atlas và .png trùng tên...\n"
    )

    # os.walk duyệt qua tất cả thư mục con
    for root, dirs, files in os.walk(target_directory):

        # Bước 1: Tìm tất cả các file .skel trong thư mục hiện tại
        # Lấy ra phần tên (không bao gồm đuôi) của các file .skel
        skel_names = set()
        for file in files:
            file_name, file_ext = os.path.splitext(file)
            if file_ext.lower() == ".skel":
                skel_names.add(file_name.lower())

        # Nếu không có file .skel nào, bỏ qua thư mục này
        if not skel_names:
            continue

        # Bước 2: Duyệt lại các file để xoá file .png và .atlas trùng tên với file .skel
        for file in files:
            file_name, file_ext = os.path.splitext(file)
            file_ext_lower = file_ext.lower()

            # Chỉ xử lý file .png và .atlas (và cả chính file .skel nếu bạn muốn xoá sạch bộ)
            if file_ext_lower in (".png", ".atlas", ".skel"):
                # Kiểm tra xem tên file này có nằm trong danh sách file .skel đã tìm thấy không
                if file_name.lower() in skel_names:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"Đã xoá: {file_path}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"Lỗi không thể xoá {file_path}: {e}")

    print(
        f"\n[ Xong ] Đã xoá tổng cộng {deleted_count} file dựa theo file .skel tại thư mục này."
    )


# --- CHƯƠNG TRÌNH CHÍNH (VÒNG LẶP) ---
if __name__ == "__main__":
    print("=== CHƯƠNG TRÌNH XOÁ FILE THEO THAM CHIẾU .SKEL ===")

    while True:
        print("\n" + "=" * 50)
        thu_muc_nhap = input("Nhập hoặc kéo thả thư mục vào đây rồi ấn Enter: ").strip()
        thu_muc_nhap = thu_muc_nhap.strip('"').strip("'")

        # 1. Kiểm tra thư mục hợp lệ
        if not os.path.exists(thu_muc_nhap) or not os.path.isdir(thu_muc_nhap):
            print(
                "❌ Đường dẫn không hợp lệ hoặc thư mục không tồn tại! Vui lòng thử lại."
            )
            continue  # Quay lại đầu vòng lặp để nhập lại

        # 2. Xác nhận xoá
        xac_nhan = input(
            f"⚠️ Bạn có chắc chắn muốn xoá bộ file .skel trong '{thu_muc_nhap}'? (y/n): "
        )
        if xac_nhan.lower() == "y":
            delete_spine_by_skel_reference(thu_muc_nhap)
        else:
            print("❌ Đã huỷ thao tác xoá tại thư mục này.")

        # 3. Hỏi người dùng có muốn tiếp tục với thư mục khác không
        tiep_tuc = input(
            "\n👉 Bạn có muốn tiếp tục xoá ở thư mục khác không? (y/n) [Mặc định: y]: "
        ).strip()

        # Nếu người dùng gõ 'n' hoặc 'N' thì bẻ gãy vòng lặp để thoát chương trình
        if tiep_tuc.lower() == "n":
            print("\n👋 Cảm ơn bạn đã sử dụng tool - tihihi")
            print("\nDang thoat sau 2 giay...")
            time.sleep(2)
            break