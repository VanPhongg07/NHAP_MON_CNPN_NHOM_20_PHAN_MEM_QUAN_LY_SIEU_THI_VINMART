"""
Chương trình cập nhật bảng sản phẩm - Siêu thị VinMart
"""

# Khởi tạo bảng dữ liệu sản phẩm dưới dạng danh sách các bản ghi (dictionary)
bang_san_pham = [
    {
        "stt": 1,
        "ma_vach": "8934567890123",
        "ten_sp": "Mì Hảo Hảo Tôm Chua Cay",
        "danh_muc": "Thực phẩm ăn liền",
        "don_gia": 4500,
        "ton_kho": 120
    },
    {
        "stt": 2,
        "ma_vach": "8935001234567",
        "ten_sp": "Sữa Vinamilk 100% 1L",
        "danh_muc": "Sữa & Chế phẩm",
        "don_gia": 38000,
        "ton_kho": 45
    },
    {
        "stt": 3,
        "ma_vach": "8936009876543",
        "ten_sp": "Coca Cola Chai 390ml",
        "danh_muc": "Đồ uống",
        "don_gia": 10000,
        "ton_kho": 80
    }
]


def ve_duong_ngang():
    """Vẽ đường kẻ viền ngang của bảng dữ liệu"""
    return "+" + "-"*6 + "+" + "-"*16 + "+" + "-"*27 + "+" + "-"*20 + "+" + "-"*13 + "+" + "-"*10 + "+"


def hien_thi_bang(danh_sach):
    """Hiển thị toàn bộ bảng dữ liệu sản phẩm có căn lề chuẩn"""
    print("\n" + ve_duong_ngang())
    tieu_de = f"| {'STT':^4} | {'MÃ VẠCH':<14} | {'TÊN SẢN PHẨM':<25} | {'DANH MỤC':<18} | {'ĐƠN GIÁ (Đ)':<11} | {'TỒN KHO':<8} |"
    print(tieu_de)
    print(ve_duong_ngang())

    for sp in danh_sach:
        gia_str = f"{sp['don_gia']:,}"
        dong = (
            f"| {sp['stt']:^4} "
            f"| {sp['ma_vach']:<14} "
            f"| {sp['ten_sp']:<25} "
            f"| {sp['danh_muc']:<18} "
            f"| {gia_str:<11} "
            f"| {sp['ton_kho']:<8} |"
        )
        print(dong)

    print(ve_duong_ngang() + "\n")


def tim_vi_tri_san_pham(ma_vach):
    """Tìm chỉ số (index) của sản phẩm trong bảng thông qua mã vạch"""
    for i in range(len(bang_san_pham)):
        if bang_san_pham[i]["ma_vach"] == ma_vach:
            return i
    return -1


def cap_nhat_san_pham():
    """Xử lý cập nhật từng thuộc tính của sản phẩm"""
    ma_vach = input("Nhập mã vạch sản phẩm cần cập nhật: ").strip()
    vi_tri = tim_vi_tri_san_pham(ma_vach)

    if vi_tri == -1:
        print(f" Không tìm thấy sản phẩm có mã vạch: {ma_vach}\n")
        return

    sp = bang_san_pham[vi_tri]
    print(f"\n---> Đang chọn sản phẩm: [{sp['ten_sp']}]")
    print("*(Ấn phím Enter nếu muốn giữ nguyên thông tin cũ)*")

    # 1. Cập nhật tên sản phẩm
    ten_moi = input(f"Tên mới [{sp['ten_sp']}]: ").strip()
    if ten_moi != "":
        sp["ten_sp"] = ten_moi

    # 2. Cập nhật danh mục
    dm_moi = input(f"Danh mục mới [{sp['danh_muc']}]: ").strip()
    if dm_moi != "":
        sp["danh_muc"] = dm_moi

    # 3. Cập nhật đơn giá
    gia_moi_str = input(f"Đơn giá mới [{sp['don_gia']:,} VNĐ]: ").strip()
    if gia_moi_str != "":
        try:
            gia_moi = int(gia_moi_str)
            if gia_moi >= 0:
                sp["don_gia"] = gia_moi
            else:
                print(" Đơn giá không được âm. Đã giữ nguyên giá cũ.")
        except ValueError:
            print(" Giá trị nhập không hợp lệ. Đã giữ nguyên giá cũ.")

    # 4. Cập nhật số lượng tồn kho
    ton_moi_str = input(f"Số lượng tồn kho mới [{sp['ton_kho']}]: ").strip()
    if ton_moi_str != "":
        try:
            ton_moi = int(ton_moi_str)
            if ton_moi >= 0:
                sp["ton_kho"] = ton_moi
            else:
                print(" Số lượng tồn không được âm. Đã giữ nguyên tồn cũ.")
        except ValueError:
            print(" Giá trị nhập không hợp lệ. Đã giữ nguyên tồn cũ.")

    # Lưu lại vào bảng
    bang_san_pham[vi_tri] = sp
    print("\n Cập nhật thông tin thành công!")
    hien_thi_bang(bang_san_pham)


def them_san_pham_moi():
    """Thêm một dòng mới vào bảng sản phẩm"""
    print("\n--- THÊM SẢN PHẨM MỚI ---")
    ma_vach = input("Nhập mã vạch: ").strip()
    if not ma_vach:
        print(" Mã vạch không được để trống!")
        return

    if tim_vi_tri_san_pham(ma_vach) != -1:
        print(f" Mã vạch {ma_vach} đã tồn tại trong bảng!")
        return

    ten_sp = input("Nhập tên sản phẩm: ").strip()
    danh_muc = input("Nhập danh mục: ").strip()

    try:
        don_gia = int(input("Nhập đơn giá (VNĐ): ").strip())
        ton_kho = int(input("Nhập số lượng tồn kho ban đầu: ").strip())
        if don_gia < 0 or ton_kho < 0:
            print(" Đơn giá và số lượng phải lớn hơn hoặc bằng 0!")
            return
    except ValueError:
        print(" Đơn giá và số lượng tồn phải là số nguyên!")
        return

    stt_tiep_theo = len(bang_san_pham) + 1
    san_pham_moi = {
        "stt": stt_tiep_theo,
        "ma_vach": ma_vach,
        "ten_sp": ten_sp,
        "danh_muc": danh_muc,
        "don_gia": don_gia,
        "ton_kho": ton_kho
    }

    bang_san_pham.append(san_pham_moi)
    print("\n Thêm sản phẩm mới thành công!")
    hien_thi_bang(bang_san_pham)


def chay_chuong_trinh():
    """Vòng lặp menu điều khiển chính"""
    while True:
        print("="*45)
        print("    HỆ THỐNG QUẢN LÝ BẢNG SẢN PHẨM VINMART")
        print("="*45)
        print("1. Xem danh sách bảng sản phẩm")
        print("2. Cập nhật thông tin sản phẩm theo mã vạch")
        print("3. Thêm sản phẩm mới vào bảng")
        print("4. Thoát chương trình")
        
        lua_chon = input("Nhập lựa chọn của bạn (1-4): ").strip()

        if lua_chon == "1":
            hien_thi_bang(bang_san_pham)
        elif lua_chon == "2":
            cap_nhat_san_pham()
        elif lua_chon == "3":
            them_san_pham_moi()
        elif lua_chon == "4":
            print("\nĐã kết thúc chương trình. Chúc bạn một ngày làm việc hiệu quả!")
            break
        else:
            print("\n Lựa chọn không hợp lệ, vui lòng chọn lại từ 1 đến 4.\n")


if __name__ == "__main__":
    chay_chuong_trinh()