import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ==========================================
# 1. TẦNG CƠ SỞ DỮ LIỆU (DATABASE LAYER)
# ==========================================
class Database:
    def __init__(self, db_name="supermarket.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Bảng sản phẩm
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT,
                price REAL NOT NULL,
                stock INTEGER NOT NULL
            )
        """)
        # Bảng hóa đơn
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                total_amount REAL NOT NULL
            )
        """)
        # Bảng chi tiết hóa đơn
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER,
                product_code TEXT,
                product_name TEXT,
                quantity INTEGER,
                unit_price REAL,
                subtotal REAL,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id)
            )
        """)
        self.conn.commit()

    # --- Quản lý sản phẩm ---
    def add_product(self, code, name, category, price, stock):
        try:
            self.cursor.execute(
                "INSERT INTO products (code, name, category, price, stock) VALUES (?, ?, ?, ?, ?)",
                (code, name, category, price, stock)
            )
            self.conn.commit()
            return True, "Thêm sản phẩm thành công!"
        except sqlite3.IntegrityError:
            return False, "Mã sản phẩm đã tồn tại!"

    def update_product(self, prod_id, code, name, category, price, stock):
        try:
            self.cursor.execute(
                "UPDATE products SET code=?, name=?, category=?, price=?, stock=? WHERE id=?",
                (code, name, category, price, stock, prod_id)
            )
            self.conn.commit()
            return True, "Cập nhật sản phẩm thành công!"
        except sqlite3.IntegrityError:
            return False, "Mã sản phẩm bị trùng với sản phẩm khác!"

    def delete_product(self, prod_id):
        self.cursor.execute("DELETE FROM products WHERE id=?", (prod_id,))
        self.conn.commit()

    def get_products(self, keyword=""):
        if keyword:
            self.cursor.execute(
                "SELECT * FROM products WHERE code LIKE ? OR name LIKE ? OR category LIKE ?",
                (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
            )
        else:
            self.cursor.execute("SELECT * FROM products")
        return self.cursor.fetchall()

    def get_product_by_code(self, code):
        self.cursor.execute("SELECT * FROM products WHERE code=?", (code,))
        return self.cursor.fetchone()

    # --- Xử lý thanh toán & hóa đơn ---
    def create_invoice(self, cart_items, total_amount):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO invoices (created_at, total_amount) VALUES (?, ?)",
            (created_at, total_amount)
        )
        invoice_id = self.cursor.lastrowid

        for item in cart_items:
            code, name, qty, price, subtotal = item
            # Lưu chi tiết hóa đơn
            self.cursor.execute("""
                INSERT INTO invoice_items (invoice_id, product_code, product_name, quantity, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (invoice_id, code, name, qty, price, subtotal))
            # Trừ tồn kho
            self.cursor.execute(
                "UPDATE products SET stock = stock - ? WHERE code = ?",
                (qty, code)
            )

        self.conn.commit()
        return invoice_id

    def get_invoices(self):
        self.cursor.execute("SELECT * FROM invoices ORDER BY id DESC")
        return self.cursor.fetchall()

    def get_invoice_items(self, invoice_id):
        self.cursor.execute(
            "SELECT product_code, product_name, quantity, unit_price, subtotal FROM invoice_items WHERE invoice_id=?",
            (invoice_id,)
        )
        return self.cursor.fetchall()

    def get_revenue_summary(self):
        self.cursor.execute("SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM invoices")
        return self.cursor.fetchone()


# ==========================================
# 2. TẦNG GIAO DIỆN (GUI LAYER)
# ==========================================
class SupermarketApp:
    def __init__(self, root):
        self.db = Database()
        self.root = root
        self.root.title("Phần Mềm Quản Lý Siêu Thị - POS & Inventory")
        self.root.geometry("1100x650")

        # Giỏ hàng hiện tại: list các dict hoặc tuple
        self.cart = []

        # Tạo Notebook (Các Tab chức năng)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_pos = ttk.Frame(self.notebook)
        self.tab_inventory = ttk.Frame(self.notebook)
        self.tab_reports = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_pos, text="🛒 Bán Hàng (POS)")
        self.notebook.add(self.tab_inventory, text="📦 Quản Lý Kho Hàng")
        self.notebook.add(self.tab_reports, text="📊 Lịch Sử & Doanh Thu")

        self.build_pos_tab()
        self.build_inventory_tab()
        self.build_reports_tab()

        # Tự động làm mới dữ liệu khi chuyển tab
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        self.load_products()
        self.load_reports()

    # ------------------------------------------
    # TAB 1: BÁN HÀNG (POS)
    # ------------------------------------------
    def build_pos_tab(self):
        left_frame = ttk.LabelFrame(self.tab_pos, text="Thêm sản phẩm vào giỏ", padding=10)
        left_frame.place(x=10, y=10, width=350, height=600)

        ttk.Label(left_frame, text="Mã Sản Phẩm:").pack(anchor=tk.W, pady=5)
        self.pos_code_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.pos_code_var, font=("Arial", 12)).pack(fill=tk.X, pady=5)

        ttk.Label(left_frame, text="Số Lượng:").pack(anchor=tk.W, pady=5)
        self.pos_qty_var = tk.IntVar(value=1)
        ttk.Spinbox(left_frame, from_=1, to=1000, textvariable=self.pos_qty_var, font=("Arial", 12)).pack(fill=tk.X, pady=5)

        ttk.Button(left_frame, text="➕ Thêm vào giỏ hàng", command=self.add_to_cart).pack(fill=tk.X, pady=15)
        ttk.Button(left_frame, text="🗑️ Xóa món đã chọn", command=self.remove_from_cart).pack(fill=tk.X, pady=5)
        ttk.Button(left_frame, text="🔄 Làm mới giỏ hàng", command=self.clear_cart).pack(fill=tk.X, pady=5)

        # Khung giỏ hàng & thanh toán bên phải
        right_frame = ttk.LabelFrame(self.tab_pos, text="Giỏ hàng hiện tại", padding=10)
        right_frame.place(x=370, y=10, width=710, height=600)

        columns = ("code", "name", "qty", "price", "subtotal")
        self.cart_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=18)
        self.cart_tree.heading("code", text="Mã SP")
        self.cart_tree.heading("name", text="Tên Sản Phẩm")
        self.cart_tree.heading("qty", text="Số Lượng")
        self.cart_tree.heading("price", text="Đơn Giá (VNĐ)")
        self.cart_tree.heading("subtotal", text="Thành Tiền (VNĐ)")

        self.cart_tree.column("code", width=100, anchor=tk.CENTER)
        self.cart_tree.column("name", width=220)
        self.cart_tree.column("qty", width=80, anchor=tk.CENTER)
        self.cart_tree.column("price", width=120, anchor=tk.E)
        self.cart_tree.column("subtotal", width=140, anchor=tk.E)
        self.cart_tree.pack(fill=tk.BOTH, expand=True)

        # Tổng tiền và nút thanh toán
        bottom_frame = ttk.Frame(right_frame)
        bottom_frame.pack(fill=tk.X, pady=15)

        self.total_label = ttk.Label(bottom_frame, text="Tổng cộng: 0 VNĐ", font=("Arial", 16, "bold"), foreground="red")
        self.total_label.pack(side=tk.LEFT, padx=10)

        pay_btn = tk.Button(bottom_frame, text="💳 THANH TOÁN & XUẤT HÓA ĐƠN", bg="#28a745", fg="white",
                            font=("Arial", 12, "bold"), padx=15, pady=8, command=self.checkout)
        pay_btn.pack(side=tk.RIGHT, padx=10)

    def add_to_cart(self):
        code = self.pos_code_var.get().strip()
        try:
            qty = int(self.pos_qty_var.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng phải là số nguyên!")
            return

        if not code or qty <= 0:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã sản phẩm và số lượng hợp lệ!")
            return

        product = self.db.get_product_by_code(code)
        if not product:
            messagebox.showerror("Không tìm thấy", f"Không tồn tại sản phẩm có mã '{code}'!")
            return

        prod_id, prod_code, prod_name, prod_cat, prod_price, prod_stock = product

        # Kiểm tra số lượng trong giỏ + số lượng muốn thêm có vượt tồn kho không
        current_qty_in_cart = sum(item[2] for item in self.cart if item[0] == prod_code)
        if current_qty_in_cart + qty > prod_stock:
            messagebox.showwarning("Hết hàng", f"Tồn kho chỉ còn {prod_stock} sản phẩm!")
            return

        # Cập nhật nếu đã có trong giỏ
        for i, item in enumerate(self.cart):
            if item[0] == prod_code:
                new_qty = item[2] + qty
                self.cart[i] = (prod_code, prod_name, new_qty, prod_price, new_qty * prod_price)
                self.refresh_cart_ui()
                self.pos_code_var.set("")
                self.pos_qty_var.set(1)
                return

        # Thêm mới vào giỏ
        self.cart.append((prod_code, prod_name, qty, prod_price, qty * prod_price))
        self.refresh_cart_ui()
        self.pos_code_var.set("")
        self.pos_qty_var.set(1)

    def remove_from_cart(self):
        selected = self.cart_tree.selection()
        if not selected:
            return
        index = self.cart_tree.index(selected[0])
        del self.cart[index]
        self.refresh_cart_ui()

    def clear_cart(self):
        self.cart.clear()
        self.refresh_cart_ui()

    def refresh_cart_ui(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        total = 0
        for item in self.cart:
            code, name, qty, price, subtotal = item
            total += subtotal
            self.cart_tree.insert("", tk.END, values=(code, name, qty, f"{price:,.0f}", f"{subtotal:,.0f}"))
        self.total_label.config(text=f"Tổng cộng: {total:,.0f} VNĐ")

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Giỏ hàng trống", "Chưa có sản phẩm nào trong giỏ hàng!")
            return

        total_amount = sum(item[4] for item in self.cart)
        invoice_id = self.db.create_invoice(self.cart, total_amount)
        messagebox.showinfo("Thành công", f"Thanh toán thành công!\nMã hóa đơn: #{invoice_id}\nTổng tiền: {total_amount:,.0f} VNĐ")
        self.clear_cart()

    # ------------------------------------------
    # TAB 2: QUẢN LÝ KHO HÀNG (INVENTORY)
    # ------------------------------------------
    def build_inventory_tab(self):
        form_frame = ttk.LabelFrame(self.tab_inventory, text="Thông tin sản phẩm", padding=10)
        form_frame.place(x=10, y=10, width=330, height=600)

        self.selected_prod_id = None
        self.inv_code_var = tk.StringVar()
        self.inv_name_var = tk.StringVar()
        self.inv_cat_var = tk.StringVar()
        self.inv_price_var = tk.StringVar()
        self.inv_stock_var = tk.StringVar()

        fields = [
            ("Mã Sản Phẩm (*):", self.inv_code_var),
            ("Tên Sản Phẩm (*):", self.inv_name_var),
            ("Danh Mục:", self.inv_cat_var),
            ("Giá Bán (VNĐ) (*):", self.inv_price_var),
            ("Số Lượng Tồn (*):", self.inv_stock_var)
        ]

        for label_text, var in fields:
            ttk.Label(form_frame, text=label_text).pack(anchor=tk.W, pady=3)
            ttk.Entry(form_frame, textvariable=var).pack(fill=tk.X, pady=3)

        ttk.Button(form_frame, text="➕ Thêm Sản Phẩm", command=self.add_product).pack(fill=tk.X, pady=8)
        ttk.Button(form_frame, text="✏️ Cập Nhật Sản Phẩm", command=self.update_product).pack(fill=tk.X, pady=4)
        ttk.Button(form_frame, text="🗑️ Xóa Sản Phẩm", command=self.delete_product).pack(fill=tk.X, pady=4)
        ttk.Button(form_frame, text="🧹 Xóa Trắng Form", command=self.clear_inventory_form).pack(fill=tk.X, pady=4)

        # Danh sách sản phẩm bên phải
        list_frame = ttk.LabelFrame(self.tab_inventory, text="Danh sách sản phẩm trong kho", padding=10)
        list_frame.place(x=350, y=10, width=730, height=600)

        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=5)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="🔍 Tìm kiếm", command=self.load_products).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Hiển thị tất cả", command=lambda: [self.search_var.set(""), self.load_products()]).pack(side=tk.LEFT)

        columns = ("id", "code", "name", "category", "price", "stock")
        self.prod_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.prod_tree.heading("id", text="ID")
        self.prod_tree.heading("code", text="Mã SP")
        self.prod_tree.heading("name", text="Tên Sản Phẩm")
        self.prod_tree.heading("category", text="Danh Mục")
        self.prod_tree.heading("price", text="Giá Bán")
        self.prod_tree.heading("stock", text="Tồn Kho")

        self.prod_tree.column("id", width=40, anchor=tk.CENTER)
        self.prod_tree.column("code", width=100, anchor=tk.CENTER)
        self.prod_tree.column("name", width=220)
        self.prod_tree.column("category", width=120)
        self.prod_tree.column("price", width=110, anchor=tk.E)
        self.prod_tree.column("stock", width=80, anchor=tk.CENTER)
        self.prod_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        self.prod_tree.bind("<<TreeviewSelect>>", self.on_product_select)
        self.load_products()

    def load_products(self):
        for row in self.prod_tree.get_children():
            self.prod_tree.delete(row)
        for prod in self.db.get_products(self.search_var.get().strip()):
            prod_id, code, name, cat, price, stock = prod
            self.prod_tree.insert("", tk.END, values=(prod_id, code, name, cat, f"{price:,.0f}", stock))

    def on_product_select(self, event):
        selected = self.prod_tree.selection()
        if not selected:
            return
        values = self.prod_tree.item(selected[0], "values")
        self.selected_prod_id = values[0]
        self.inv_code_var.set(values[1])
        self.inv_name_var.set(values[2])
        self.inv_cat_var.set(values[3])
        self.inv_price_var.set(values[4].replace(",", ""))
        self.inv_stock_var.set(values[5])

    def add_product(self):
        try:
            code = self.inv_code_var.get().strip()
            name = self.inv_name_var.get().strip()
            cat = self.inv_cat_var.get().strip()
            price = float(self.inv_price_var.get())
            stock = int(self.inv_stock_var.get())
            if not code or not name:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi dữ liệu", "Vui lòng nhập đầy đủ thông tin, giá và tồn kho phải là số!")
            return

        ok, msg = self.db.add_product(code, name, cat, price, stock)
        if ok:
            messagebox.showinfo("Thành công", msg)
            self.clear_inventory_form()
            self.load_products()
        else:
            messagebox.showerror("Lỗi", msg)

    def update_product(self):
        if not self.selected_prod_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một sản phẩm trong bảng để cập nhật!")
            return
        try:
            code = self.inv_code_var.get().strip()
            name = self.inv_name_var.get().strip()
            cat = self.inv_cat_var.get().strip()
            price = float(self.inv_price_var.get())
            stock = int(self.inv_stock_var.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Giá và số lượng tồn phải là số hợp lệ!")
            return

        ok, msg = self.db.update_product(self.selected_prod_id, code, name, cat, price, stock)
        if ok:
            messagebox.showinfo("Thành công", msg)
            self.clear_inventory_form()
            self.load_products()
        else:
            messagebox.showerror("Lỗi", msg)

    def delete_product(self):
        if not self.selected_prod_id:
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa sản phẩm này?"):
            self.db.delete_product(self.selected_prod_id)
            self.clear_inventory_form()
            self.load_products()

    def clear_inventory_form(self):
        self.selected_prod_id = None
        self.inv_code_var.set("")
        self.inv_name_var.set("")
        self.inv_cat_var.set("")
        self.inv_price_var.set("")
        self.inv_stock_var.set("")

    # ------------------------------------------
    # TAB 3: LỊCH SỬ HÓA ĐƠN & DOANH THU
    # ------------------------------------------
    def build_reports_tab(self):
        top_frame = ttk.Frame(self.tab_reports, padding=10)
        top_frame.pack(fill=tk.X)

        self.summary_label = ttk.Label(top_frame, text="Tổng số hóa đơn: 0 | Tổng doanh thu: 0 VNĐ",
                                       font=("Arial", 14, "bold"), foreground="#0056b3")
        self.summary_label.pack(side=tk.LEFT)

        body_frame = ttk.Frame(self.tab_reports, padding=10)
        body_frame.pack(fill=tk.BOTH, expand=True)

        # Danh sách hóa đơn
        inv_frame = ttk.LabelFrame(body_frame, text="Danh sách hóa đơn", padding=5)
        inv_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.inv_tree = ttk.Treeview(inv_frame, columns=("id", "date", "total"), show="headings")
        self.inv_tree.heading("id", text="Mã HĐ")
        self.inv_tree.heading("date", text="Thời Gian")
        self.inv_tree.heading("total", text="Tổng Tiền (VNĐ)")
        self.inv_tree.column("id", width=70, anchor=tk.CENTER)
        self.inv_tree.column("date", width=160, anchor=tk.CENTER)
        self.inv_tree.column("total", width=130, anchor=tk.E)
        self.inv_tree.pack(fill=tk.BOTH, expand=True)
        self.inv_tree.bind("<<TreeviewSelect>>", self.on_invoice_select)

        # Chi tiết hóa đơn
        detail_frame = ttk.LabelFrame(body_frame, text="Chi tiết hóa đơn", padding=5)
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.detail_tree = ttk.Treeview(detail_frame, columns=("code", "name", "qty", "price", "sub"), show="headings")
        self.detail_tree.heading("code", text="Mã SP")
        self.detail_tree.heading("name", text="Tên SP")
        self.detail_tree.heading("qty", text="SL")
        self.detail_tree.heading("price", text="Đơn Giá")
        self.detail_tree.heading("sub", text="Thành Tiền")
        self.detail_tree.column("code", width=80, anchor=tk.CENTER)
        self.detail_tree.column("name", width=160)
        self.detail_tree.column("qty", width=50, anchor=tk.CENTER)
        self.detail_tree.column("price", width=100, anchor=tk.E)
        self.detail_tree.column("sub", width=110, anchor=tk.E)
        self.detail_tree.pack(fill=tk.BOTH, expand=True)

    def load_reports(self):
        for row in self.inv_tree.get_children():
            self.inv_tree.delete(row)
        for row in self.detail_tree.get_children():
            self.detail_tree.delete(row)

        count, revenue = self.db.get_revenue_summary()
        self.summary_label.config(text=f"Tổng số hóa đơn: {count}  |  Tổng doanh thu: {revenue:,.0f} VNĐ")

        for inv in self.db.get_invoices():
            inv_id, created_at, total = inv
            self.inv_tree.insert("", tk.END, values=(inv_id, created_at, f"{total:,.0f}"))

    def on_invoice_select(self, event):
        selected = self.inv_tree.selection()
        if not selected:
            return
        inv_id = self.inv_tree.item(selected[0], "values")[0]
        for row in self.detail_tree.get_children():
            self.detail_tree.delete(row)
        for item in self.db.get_invoice_items(inv_id):
            code, name, qty, price, sub = item
            self.detail_tree.insert("", tk.END, values=(code, name, qty, f"{price:,.0f}", f"{sub:,.0f}"))


if __name__ == "__main__":
    root = tk.Tk()
    app = SupermarketApp(root)
    root.mainloop()