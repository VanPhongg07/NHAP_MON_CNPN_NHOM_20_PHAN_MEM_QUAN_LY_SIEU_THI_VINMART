import sqlite3

sample_products = [
    ("SP001", "Sữa tươi tiệt trùng Vinamilk 1L", "Sữa & Chế phẩm", 32000, 120),
    ("SP002", "Sữa đặc Ông Thọ trắng 380g", "Sữa & Chế phẩm", 24000, 85),
    ("SP003", "Lốc 4 hộp sữa chua TH True Yogurt", "Sữa & Chế phẩm", 28000, 60),
    ("SP004", "Nước ngọt Coca-Cola lon 320ml", "Đồ uống", 10000, 240),
    ("SP005", "Nước khoáng LaVie 500ml", "Đồ uống", 6000, 300),
    ("SP006", "Trà Ô Long Tea+ Plus 450ml", "Đồ uống", 11000, 150),
    ("SP007", "Bia Tiger Crystal lon 330ml", "Đồ uống", 18000, 200),
    ("SP008", "Mì Hảo Hảo tôm chua cay (gói 75g)", "Thực phẩm khô", 4500, 500),
    ("SP009", "Gạo ST25 Ông Cua (túi 5kg)", "Thực phẩm khô", 185000, 45),
    ("SP010", "Phở bò Vifon (gói 65g)", "Thực phẩm khô", 9000, 180),
    ("SP011", "Bánh quy bơ Cosy Marie (hộp 288g)", "Bánh kẹo", 42000, 50),
    ("SP012", "Snack khoai tây Lay's vị tự nhiên 52g", "Bánh kẹo", 12000, 100),
    ("SP013", "Kẹo dẻo Chupa Chups Sour Belt", "Bánh kẹo", 15000, 90),
    ("SP014", "Dầu ăn thực vật Tường An 1L", "Gia vị", 48000, 75),
    ("SP015", "Nước mắm Nam Ngư Đệ Nhị 900ml", "Gia vị", 36000, 110),
    ("SP016", "Hạt nêm Knorr thịt thăn xương ống 400g", "Gia vị", 39000, 95),
    ("SP017", "Nước tương Tam Thái Tử Nhất Ca 500ml", "Gia vị", 16000, 130),
    ("SP018", "Nước rửa chén Sunlight chanh 750g", "Hóa mỹ phẩm", 29000, 80),
    ("SP019", "Dầu gội Clear bạc hà mát lạnh 630g", "Hóa mỹ phẩm", 165000, 40),
    ("SP020", "Kem đánh răng P/S Bảo Vệ 123 230g", "Hóa mỹ phẩm", 35000, 110),
]

def seed_database():
    conn = sqlite3.connect("supermarket.db")
    cursor = conn.cursor()
    
    # Đảm bảo bảng đã tồn tại
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)
    
    # Chèn dữ liệu (bỏ qua nếu mã SP đã tồn tại)
    cursor.executemany("""
        INSERT OR IGNORE INTO products (code, name, category, price, stock)
        VALUES (?, ?, ?, ?, ?)
    """, sample_products)
    
    conn.commit()
    print(f"Đã thêm thành công {cursor.rowcount} sản phẩm mới vào kho!")
    conn.close()

if __name__ == "__main__":
    seed_database()