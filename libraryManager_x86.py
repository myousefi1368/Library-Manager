# libraryManager_modern_light.py
import sys, os, json, datetime
from typing import List, Dict

# External libs - IMPORTANT: Import jdatetime directly for PyInstaller
import jdatetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import (
    QFont, QFontInfo, QIcon
)
# Keep the try/except for qt_material only
try:
    from qt_material import apply_stylesheet
    QT_MATERIAL_AVAILABLE = True
except Exception:
    QT_MATERIAL_AVAILABLE = False

# ---------- Helpers ----------
def to_jalali(date_str: str) -> str:
    """Convert 'YYYY-MM-DD' to Jalali 'YYYY/MM/DD' — if invalid return '-'"""
    if not date_str:
        return "-"
    try:
        y, m, d = map(int, date_str.split('-'))
        jd = jdatetime.date.fromgregorian(year=y, month=m, day=d)
        return jd.strftime("%Y/%m/%d")
    except Exception:
        return date_str

def today_gregorian_str() -> str:
    return datetime.date.today().strftime("%Y-%m-%d")

class NumericTableWidgetItem(QtWidgets.QTableWidgetItem):
    def __init__(self, value, display_format="{}"):
        # مقدار عددی را ذخیره می‌کنیم
        if isinstance(value, (int, float)):
            self._value = value
        else:
            try:
                self._value = int(value)
            except (ValueError, TypeError):
                self._value = 0
                
        # نمایش فرمت شده را تنظیم می‌کنیم
        display_text = display_format.format(self._value)
        super().__init__(display_text)
        
    def __lt__(self, other):
        """برای مرتب‌سازی عددی"""
        if isinstance(other, NumericTableWidgetItem):
            return self._value < other._value
        return super().__lt__(other)
# ---------- Main Window ----------
class LibraryApp(QtWidgets.QMainWindow):
    DATA_FILE = "library_data.json"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("کتابدار — سیستم مدیریت کتابخانه")
        self.resize(1200, 760)
        self.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)

        # Data
        self.members: List[Dict] = []
        self.books: List[Dict] = []
        self.loans: List[Dict] = []
        self.settings = {"default_loan_period": 14, "fine_per_day": 1000}

        # Central container
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        root_layout = QtWidgets.QHBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        # Sidebar (left) - استفاده از create_section_card
        self.sidebar, s_layout = self.create_section_card("", "#ffffff")
        self.sidebar.setFixedWidth(220)
        s_layout.setContentsMargins(10, 10, 10, 10)
        s_layout.setSpacing(8)

        # App title in sidebar
        title_lbl = QtWidgets.QLabel("📚 کتابدار")
        title_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet("font-weight:700; font-size:18px; padding:6px;")
        s_layout.addWidget(title_lbl)

        # Sidebar buttons (emoji icons for portability)
        self.btn_dashboard = QtWidgets.QPushButton("🏠  داشبورد")
        self.btn_members = QtWidgets.QPushButton("👥  اعضا")
        self.btn_books = QtWidgets.QPushButton("📖  کتاب‌ها")
        self.btn_loans = QtWidgets.QPushButton("🔁  امانت‌ها")
        self.btn_member_details = QtWidgets.QPushButton("👤  جزئیات عضو")
        self.btn_book_details = QtWidgets.QPushButton("📚  جزئیات کتاب")
        self.btn_settings = QtWidgets.QPushButton("⚙️  تنظیمات")

        for btn in [self.btn_dashboard, self.btn_members, self.btn_books, self.btn_loans,
                    self.btn_member_details, self.btn_book_details, self.btn_settings]:
            btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            btn.setFixedHeight(44)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 16px;
                    padding-right: 12px;
                }
            """)
            btn.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
            s_layout.addWidget(btn)

        s_layout.addStretch()
        root_layout.addWidget(self.sidebar)

        # Content area (stacked)
        self.stack = QtWidgets.QStackedWidget()
        root_layout.addWidget(self.stack, 1)

        # Create pages
        self.page_dashboard = self.create_dashboard_page()
        self.page_members = self.create_members_page()
        self.page_books = self.create_books_page()
        self.page_loans = self.create_loans_page()
        self.page_member_details = self.create_member_details_page()
        self.page_book_details = self.create_book_details_page()
        self.page_settings = self.create_settings_and_backup_page()

        # Add to stack
        for p in [self.page_dashboard, self.page_members, self.page_books, self.page_loans,
                  self.page_member_details, self.page_book_details, self.page_settings]:
            self.stack.addWidget(p)

        # Connect sidebar
        self.btn_dashboard.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_dashboard))
        self.btn_members.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_members))
        self.btn_books.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_books))
        self.btn_loans.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_loans))
        self.btn_member_details.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_member_details))
        self.btn_book_details.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_book_details))
        self.btn_settings.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_settings))

        # Load and refresh
        self.load_data()
        self.refresh_ui()

        # Apply polish stylesheet
        self.apply_styles()

    # ---------- UI pages ----------
    def create_section_card(self, title: str, color: str = "#ffffff"):
        """
        Create a styled QGroupBox section with shadow and custom styling
        
        Args:
            title (str): Section title
            color (str): Background color hex
        
        Returns:
            tuple: (QGroupBox, QVBoxLayout) - The section and its layout
        """
        section = QtWidgets.QGroupBox(title)
        
        # Apply styling
        section.setStyleSheet(f"""
            QGroupBox {{
                background-color: {color};
                border: 0px solid #e0e0e0;
                border-radius: 12px;
                padding: 40px 15px 15px 15px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: padding;
                subcontrol-position: top left;
                left: 15px;
                top: 20px;
                padding: 0px 10px 0px 10px;
                color: #2e2e2e;
                font-weight: bold;
                font-size: 18px;
                background-color: {color};
            }}
        """)
        
        # Add shadow effect
        shadow_effect = QtWidgets.QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(20)
        shadow_effect.setColor(QtGui.QColor(0, 0, 0, 40))
        shadow_effect.setOffset(0, 3)
        section.setGraphicsEffect(shadow_effect)
        
        # Set font
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        section.setFont(font)
        
        # Create and set layout
        layout = QtWidgets.QVBoxLayout(section)
        
        return section, layout
        
    def create_section_card_(self, title: str, color: str = "#ffffff"):
        card = QtWidgets.QFrame()
        card.setObjectName("section_card")  # مهم!
        card.setStyleSheet(f"""
            background:{color};
            border-radius:12px;
        """)
        
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QtGui.QColor(0, 0, 0, 40))
        card.setGraphicsEffect(shadow)
        
        v = QtWidgets.QVBoxLayout(card)
        header = QtWidgets.QLabel(title)
        header.setStyleSheet("font-weight:700; padding:8px;")
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        v.addWidget(header)
        return card, v
    
    def create_card(self, title: str, color: str = "#ffffff", border: int = 0):
        """Return a styled card QWidget with title label and a vertical layout for content."""
        card = QtWidgets.QFrame()
        card.setObjectName("card")
        card.setStyleSheet(f"""
            background:{color};
            border-radius:12px;
            border:{border}px solid #dfe6ee;
        """)
        
        # 🔹 افزودن سایه واقعی با Qt
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)              # میزان پخش سایه
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QtGui.QColor(0, 0, 0, 40))  # رنگ خاکستری با شفافیت
        card.setGraphicsEffect(shadow)
        
        v = QtWidgets.QVBoxLayout(card)
        header = QtWidgets.QLabel(title)
        header.setStyleSheet("font-weight:700; padding:8px;")
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        v.addWidget(header)
        return card, v

    def create_dashboard_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setSpacing(12)

        # Header
        head = QtWidgets.QLabel("داشبورد — وضعیت کلی")
        head.setStyleSheet("font-size:18px; font-weight:800;")
        head.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        layout.addWidget(head)

        # Cards row
        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)

        self.card_members, members_layout = self.create_card("تعداد اعضا", "#E3F2FD", 0)       # آبی روشن
        self.card_books, books_layout = self.create_card("تعداد کتاب‌ها", "#FFF8E1", 0)       # زرد ملایم
        self.card_loans, loans_layout = self.create_card("امانت‌های فعال", "#E8F5E9", 0)      # سبز روشن
        self.card_available, avail_layout = self.create_card("کتاب‌های موجود", "#F3E5F5", 0)  # بنفش روشن

        # big labels
        self.lbl_members_count = QtWidgets.QLabel("0")
        self.lbl_books_count = QtWidgets.QLabel("0")
        self.lbl_loans_count = QtWidgets.QLabel("0")
        self.lbl_available_count = QtWidgets.QLabel("0")
        for lbl in [self.lbl_members_count, self.lbl_books_count, self.lbl_loans_count, self.lbl_available_count]:
            lbl.setStyleSheet("font-size:26px; font-weight:700; padding:12px;")
            lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        members_layout.addWidget(self.lbl_members_count)
        books_layout.addWidget(self.lbl_books_count)
        loans_layout.addWidget(self.lbl_loans_count)
        avail_layout.addWidget(self.lbl_available_count)

        row.addWidget(self.card_members)
        row.addWidget(self.card_books)
        row.addWidget(self.card_loans)
        row.addWidget(self.card_available)

        # Overdue table card
        overdue_card, overdue_layout = self.create_section_card("امانت‌های سررسید گذشته", "#ffffff")
        self.overdue_table = QtWidgets.QTableWidget(0, 5)
        
        self.overdue_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #ffffff;
                alternate-background-color: #fafafa;
                selection-background-color: #d9edf7;
                selection-color: #000;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #f7f7f7;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                padding: 4px;
            }
        """)
        
        self.overdue_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.overdue_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.overdue_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        
        self.overdue_table.setHorizontalHeaderLabels(["عضو", "کتاب", "تاریخ سررسید", "روز تأخیر", "جریمه (تومان)"])
        self.overdue_table.horizontalHeader().setStretchLastSection(True)
        overdue_layout.addWidget(self.overdue_table)
        layout.addWidget(overdue_card)

        return page

    def create_members_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setSpacing(10)

        # ---- Header ----
        header = QtWidgets.QLabel("👥 مدیریت اعضا")
        header.setStyleSheet("font-size:18px; font-weight:800;")
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        layout.addWidget(header)

        # ---- Main layout: Form | Table ----
        top = QtWidgets.QHBoxLayout()
        layout.addLayout(top)

        # ------------------- Form Section -------------------
        form_card, form_layout = self.create_section_card("افزودن عضو جدید", "#FAFCFF")

        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        
        # ایجاد validator برای فیلدهای عددی
        only_digits_validator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression("[0-9]*"))

        self.input_student_id = QtWidgets.QLineEdit()
        self.input_national_id = QtWidgets.QLineEdit()
        self.input_phone = QtWidgets.QLineEdit()
        self.input_first_name = QtWidgets.QLineEdit()
        self.input_last_name = QtWidgets.QLineEdit()
        
        # اعمال validator روی فیلدهای عددی
        self.input_student_id.setValidator(only_digits_validator)
        self.input_national_id.setValidator(only_digits_validator)
        self.input_phone.setValidator(only_digits_validator)

        for w in [self.input_student_id, self.input_national_id, self.input_phone, self.input_first_name, self.input_last_name]:
            w.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)

        form.addRow("شماره دانشجویی:", self.input_student_id)
        form.addRow("کد ملی:", self.input_national_id)
        form.addRow("نام:", self.input_first_name)
        form.addRow("نام خانوادگی:", self.input_last_name)
        form.addRow("تلفن:", self.input_phone)
        form_layout.addLayout(form)

        btn_row = QtWidgets.QHBoxLayout()
        btn_add_member = QtWidgets.QPushButton("افزودن عضو ✅")
        btn_add_member.clicked.connect(self.add_member)
        btn_add_member.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_clear = QtWidgets.QPushButton("پاک کردن فرم")
        btn_clear.setProperty("danger", "true")
        btn_clear.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_clear.clicked.connect(lambda: [w.clear() for w in [
            self.input_student_id, self.input_national_id, self.input_phone,
            self.input_first_name, self.input_last_name
        ]])
        btn_row.addWidget(btn_add_member)
        btn_row.addWidget(btn_clear)
        form_layout.addLayout(btn_row)

        top.addWidget(form_card, 1)

        # ------------------- Table Section -------------------
        table_card, table_layout = self.create_section_card("لیست اعضا", "#FFFFFF")

        # 🔹 جستجو + دکمه‌ها بالای جدول
        actions = QtWidgets.QHBoxLayout()
        self.member_search = QtWidgets.QLineEdit()
        self.member_search.setPlaceholderText("🔍 جستجوی اعضا...")
        self.member_search.textChanged.connect(self.search_members)

        btn_edit = QtWidgets.QPushButton("✏️ ویرایش عضو")
        btn_delete = QtWidgets.QPushButton("🗑️ حذف عضو")
        btn_edit.setProperty("info", "true")
        btn_delete.setProperty("danger", "true")
        btn_edit.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_delete.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_edit.clicked.connect(self.edit_member)
        btn_delete.clicked.connect(self.delete_member)

        actions.addWidget(self.member_search, 3)
        actions.addWidget(btn_edit, 1)
        actions.addWidget(btn_delete, 1)
        table_layout.addLayout(actions)

        # 🔹 جدول اعضا
        self.members_table = QtWidgets.QTableWidget(0, 5)
        self.members_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #ffffff;
                alternate-background-color: #fafafa;
                selection-background-color: #d9edf7;
                selection-color: #000;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #f7f7f7;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                padding: 4px;
            }
        """)
        self.members_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.members_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.members_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.members_table.setHorizontalHeaderLabels(["شماره دانشجویی", "کد ملی", "تلفن", "نام", "نام خانوادگی"])
        self.members_table.horizontalHeader().setStretchLastSection(True)
        self.members_table.cellDoubleClicked.connect(self.on_member_double_click)

        table_layout.addWidget(self.members_table)
        top.addWidget(table_card, 2)

        return page

    def create_books_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setSpacing(10)

        # ---- Header ----
        header = QtWidgets.QLabel("📖 مدیریت کتاب‌ها")
        header.setStyleSheet("font-size:18px; font-weight:800;")
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        layout.addWidget(header)

        # ---- Form section ----
        top = QtWidgets.QHBoxLayout()
        layout.addLayout(top)

        form_card, form_layout = self.create_section_card("افزودن کتاب جدید", "#FAFCFF")
        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.input_title = QtWidgets.QLineEdit()
        self.input_author = QtWidgets.QLineEdit()
        self.input_publish = QtWidgets.QLineEdit()
        self.input_copies = QtWidgets.QSpinBox()
        self.input_copies.setRange(1, 1000)

        form.addRow("نام کتاب:", self.input_title)
        form.addRow("نویسنده:", self.input_author)
        form.addRow("تاریخ چاپ:", self.input_publish)
        form.addRow("تعداد نسخه‌ها:", self.input_copies)
        form_layout.addLayout(form)

        btn_row = QtWidgets.QHBoxLayout()
        b_add = QtWidgets.QPushButton("افزودن کتاب ✅")
        b_add.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        b_add.clicked.connect(self.add_book)
        b_clear = QtWidgets.QPushButton("پاک کردن فرم")
        b_clear.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        b_clear.setProperty("danger", "true")
        b_clear.clicked.connect(lambda: [self.input_title.clear(), self.input_author.clear(), self.input_publish.clear(), self.input_copies.setValue(1)])
        btn_row.addWidget(b_add)
        btn_row.addWidget(b_clear)
        form_layout.addLayout(btn_row)

        top.addWidget(form_card, 1)

        # ---- Table + Search section ----
        table_card, table_layout = self.create_section_card("لیست کتاب‌ها", "#FFFFFF")

        # 🔹 جستجو و دکمه‌ها بالای جدول
        actions = QtWidgets.QHBoxLayout()
        self.book_search = QtWidgets.QLineEdit()
        self.book_search.setPlaceholderText("🔍 جستجوی کتاب‌ها...")
        self.book_search.textChanged.connect(self.search_books)

        b_edit = QtWidgets.QPushButton("✏️ ویرایش کتاب")
        b_edit.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        b_edit.setProperty("info", "true")
        b_edit.clicked.connect(self.edit_book)
        b_delete = QtWidgets.QPushButton("🗑️ حذف کتاب")
        b_delete.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        b_delete.setProperty("danger", "true")
        b_delete.clicked.connect(self.delete_book)

        actions.addWidget(self.book_search, 3)
        actions.addWidget(b_edit, 1)
        actions.addWidget(b_delete, 1)
        table_layout.addLayout(actions)  # ← حالا بالای جدول اضافه شد

        # 🔹 جدول کتاب‌ها
        self.books_table = QtWidgets.QTableWidget(0, 4)
        self.books_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #ffffff;
                alternate-background-color: #fafafa;
                selection-background-color: #d9edf7;
                selection-color: #000;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #f7f7f7;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                padding: 4px;
            }
        """)
        self.books_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.books_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.books_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.books_table.setHorizontalHeaderLabels(["نام کتاب", "نویسنده", "تاریخ چاپ", "وضعیت"])
        self.books_table.horizontalHeader().setStretchLastSection(True)
        self.books_table.cellDoubleClicked.connect(self.on_book_double_click)

        table_layout.addWidget(self.books_table)
        top.addWidget(table_card, 2)

        return page

    def create_loans_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        header = QtWidgets.QLabel("🔁 مدیریت امانت")
        header.setStyleSheet("font-size:18px; font-weight:800;")
        header.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        layout.addWidget(header)

        form_card, form_layout = self.create_section_card("اعطای امانت", "#FAFCFF")
        grid = QtWidgets.QGridLayout()
        
        self.loan_book_combo = QtWidgets.QComboBox()
        self.loan_book_combo.setEditable(True)
        self.loan_book_combo.lineEdit().setPlaceholderText("جستجوی کتاب...")
        self.loan_book_combo.lineEdit().setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.loan_book_combo.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)

        book_completer = QtWidgets.QCompleter(self.loan_book_combo.model(), self.loan_book_combo)
        book_completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        book_completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        self.loan_book_combo.setCompleter(book_completer)


        # --- فیلترشونده برای اعضا ---
        self.loan_member_combo = QtWidgets.QComboBox()
        self.loan_member_combo.setEditable(True)
        self.loan_member_combo.lineEdit().setPlaceholderText("جستجوی عضو...")
        self.loan_member_combo.lineEdit().setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.loan_member_combo.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)

        member_completer = QtWidgets.QCompleter(self.loan_member_combo.model(), self.loan_member_combo)
        member_completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        member_completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        self.loan_member_combo.setCompleter(member_completer)
        
        grid.addWidget(QtWidgets.QLabel("عضو:"), 0, 0, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.loan_member_combo, 0, 1)
        grid.addWidget(QtWidgets.QLabel("کتاب:"), 0, 2, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.loan_book_combo, 0, 3)
        form_layout.addLayout(grid)
        btn_loan = QtWidgets.QPushButton("امانت دادن")
        btn_loan.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_loan.setProperty("info", "true")
        btn_loan.clicked.connect(self.loan_book)
        form_layout.addWidget(btn_loan, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        layout.addWidget(form_card)

        # active loans table
        loans_card, loans_layout = self.create_section_card("امانت‌های فعال", "#FFFFFF")
        self.active_loans_table = QtWidgets.QTableWidget(0, 5)
        
        self.active_loans_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #ffffff;
                alternate-background-color: #fafafa;
                selection-background-color: #d9edf7;
                selection-color: #000;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #f7f7f7;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                padding: 4px;
            }
        """)
        
        self.active_loans_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.active_loans_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.active_loans_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        
        self.active_loans_table.setHorizontalHeaderLabels(["شناسه", "عضو", "کتاب", "تاریخ امانت", "تاریخ سررسید"])
        self.active_loans_table.horizontalHeader().setStretchLastSection(True)
        loans_layout.addWidget(self.active_loans_table)
        
        # 🔍 نوار جستجو در بالای جدول امانت‌ها
        actions = QtWidgets.QHBoxLayout()
        self.loan_search = QtWidgets.QLineEdit()
        self.loan_search.setPlaceholderText("🔍 جستجوی امانت‌ها...")
        self.loan_search.textChanged.connect(self.search_loans)
        actions.addWidget(self.loan_search)
        loans_layout.insertLayout(0, actions)

        layout.addWidget(loans_card)

        manage_row = QtWidgets.QHBoxLayout()
        b_renew = QtWidgets.QPushButton("تمدید امانت"); b_renew.clicked.connect(self.renew_loan)
        b_renew.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        b_renew.setProperty("info", "true")
        b_return = QtWidgets.QPushButton("بازگرداندن کتاب"); b_return.clicked.connect(self.return_book)
        b_return.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        manage_row.addWidget(b_renew); manage_row.addWidget(b_return)
        layout.addLayout(manage_row)

        return page

    def create_member_details_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        header = QtWidgets.QLabel("👤 جزئیات عضو")
        header.setStyleSheet("font-size:18px; font-weight:800;"); header.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        layout.addWidget(header)

        self.member_detail_search = QtWidgets.QLineEdit(); self.member_detail_search.setPlaceholderText("🔍 شماره دانشجویی یا نام...")
        self.member_detail_search.textChanged.connect(self.search_member_details)
        layout.addWidget(self.member_detail_search)

        self.member_info_label = QtWidgets.QLabel(""); self.member_info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.member_info_label)
        
        # ---- بخش امانت‌های فعال ----
        lbl_active = QtWidgets.QLabel("📚 امانت‌های فعال")
        lbl_active.setStyleSheet("font-weight:600; font-size:14px; margin-top:8px;")
        lbl_active.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        layout.addWidget(lbl_active)

        self.member_active_loans = QtWidgets.QTableWidget(0,5)
        
        self.member_active_loans.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #ffffff;
                alternate-background-color: #fafafa;
                selection-background-color: #d9edf7;
                selection-color: #000;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #f7f7f7;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                padding: 4px;
            }
        """)
        
        self.member_active_loans.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.member_active_loans.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.member_active_loans.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        
        self.member_active_loans.setHorizontalHeaderLabels(["کتاب","تاریخ امانت","تاریخ سررسید","روزهای باقی‌مانده","جریمه"])
        self.member_active_loans.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.member_active_loans, stretch=1)
        
        # ---- بخش تاریخچه امانت‌ها ----
        lbl_history = QtWidgets.QLabel("📖 تاریخچه امانت‌ها")
        lbl_history.setStyleSheet("font-weight:600; font-size:14px; margin-top:8px;")
        lbl_history.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        layout.addWidget(lbl_history)

        self.member_history = QtWidgets.QTableWidget(0,6)
        
        self.member_history.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #ffffff;
                alternate-background-color: #fafafa;
                selection-background-color: #d9edf7;
                selection-color: #000;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #f7f7f7;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                padding: 4px;
            }
        """)
        
        self.member_history.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.member_history.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.member_history.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        
        self.member_history.setHorizontalHeaderLabels(["کتاب","تاریخ امانت","تاریخ سررسید","تاریخ بازگشت","وضعیت","جریمه پرداخت نشده"])
        self.member_history.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.member_history, stretch=1)
        
        # ---- دکمه تسویه جریمه‌ها ----
        btn_pay_fines = QtWidgets.QPushButton("💰 تسویه جریمه‌های بازگشتی")
        btn_pay_fines.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_pay_fines.clicked.connect(self.pay_member_fines)
        btn_pay_fines.setStyleSheet("background-color:#4caf50; color:white; font-weight:600; padding:6px 12px; border-radius:8px;")
        layout.addWidget(btn_pay_fines, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        # ---- مجموع جریمه ----
        self.member_total_fine_label = QtWidgets.QLabel("مجموع جریمه: ۰ تومان")
        self.member_total_fine_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.member_total_fine_label.setStyleSheet("font-weight:600; font-size:14px; color:#b71c1c;")
        layout.addWidget(self.member_total_fine_label)

        return page
        
    def pay_member_fines(self):
        member_id = getattr(self, "selected_member_id", None)
        if not member_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "ابتدا یک عضو را انتخاب کنید")
            return

        unpaid_loans = [
            loan for loan in self.loans
            if loan.get("member_id") == member_id
            and loan.get("return_date")
            and loan.get("unpaid_fine", 0) > 0
        ]

        if not unpaid_loans:
            QtWidgets.QMessageBox.information(self, "اطلاع", "هیچ جریمه‌ای برای تسویه وجود ندارد ✅")
            return

        total = sum(l["unpaid_fine"] for l in unpaid_loans)
        confirm = QtWidgets.QMessageBox.question(
            self,
            "تسویه جریمه",
            f"مجموع جریمه‌های بازگشتی {total:,} تومان است.\nآیا مایل به تسویه هستید؟",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            for loan in unpaid_loans:
                loan["unpaid_fine"] = 0
                loan["fine_paid"] = True
            self.save_data()
            self.search_member_details()  # به‌روزرسانی صفحه
            QtWidgets.QMessageBox.information(self, "تسویه شد", "جریمه‌های بازگشتی با موفقیت تسویه شدند ✅")

    def create_book_details_page(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        header = QtWidgets.QLabel("📚 جزئیات کتاب"); header.setStyleSheet("font-size:18px; font-weight:800;"); header.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        layout.addWidget(header)

        self.book_detail_search = QtWidgets.QLineEdit(); self.book_detail_search.setPlaceholderText("🔍 عنوان یا نویسنده..."); self.book_detail_search.textChanged.connect(self.search_book_details)
        layout.addWidget(self.book_detail_search)

        self.book_info_label = QtWidgets.QLabel(""); self.book_info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.book_info_label)

        self.book_history = QtWidgets.QTableWidget(0,5)
        
        self.book_history.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: #ffffff;
                alternate-background-color: #fafafa;
                selection-background-color: #d9edf7;
                selection-color: #000;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #f7f7f7;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                padding: 4px;
            }
        """)
        
        self.book_history.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.book_history.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.book_history.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        
        self.book_history.setHorizontalHeaderLabels(["عضو","تاریخ امانت","تاریخ سررسید","تاریخ بازگشت","وضعیت"])
        self.book_history.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.book_history, stretch=1)
        return page
        
    def create_settings_and_backup_page(self):
        page = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(page)

        # 🔹 بخش تنظیمات - Use the unpacking version since create_section_card returns (section, layout)
        settings_group, settings_layout = self.create_section_card("⚙️ تنظیمات", "#ffffff")
        
        # Change settings_layout from VBoxLayout to FormLayout
        # First, remove the existing VBoxLayout
        QtWidgets.QWidget().setLayout(settings_group.layout())
        
        # Create FormLayout for settings
        settings_form_layout = QtWidgets.QFormLayout()
        settings_form_layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        settings_form_layout.setVerticalSpacing(10)
        settings_form_layout.setContentsMargins(5, 10, 5, 10)

        self.set_loan_period = QtWidgets.QSpinBox()
        self.set_loan_period.setRange(1, 365)
        self.set_loan_period.setValue(self.settings.get("default_loan_period", 14))

        self.set_fine_per_day = QtWidgets.QSpinBox()
        self.set_fine_per_day.setRange(0, 10000000)
        self.set_fine_per_day.setValue(self.settings.get("fine_per_day", 1000))

        settings_form_layout.addRow("دوره امانت پیش‌فرض (روز):", self.set_loan_period)
        settings_form_layout.addRow("جریمه روزانه (تومان):", self.set_fine_per_day)

        btn_save = QtWidgets.QPushButton("💾 ذخیره تنظیمات")
        btn_save.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_save.clicked.connect(self.save_settings)
        settings_form_layout.addRow(btn_save)

        settings_group.setLayout(settings_form_layout)

        # 🔹 بخش پشتیبان‌گیری
        backup_group, backup_layout = self.create_section_card("🗄️ پشتیبان‌گیری و بازیابی", "#ffffff")
        
        # Change backup_layout to HBoxLayout
        QtWidgets.QWidget().setLayout(backup_group.layout())
        backup_hbox_layout = QtWidgets.QHBoxLayout()

        btn_backup = QtWidgets.QPushButton("📦 پشتیبان گیری")
        btn_backup.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_backup.clicked.connect(self.create_backup)

        btn_restore = QtWidgets.QPushButton("🔁 بازیابی پشتیبان")
        btn_restore.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn_restore.setProperty("danger", "true")
        btn_restore.clicked.connect(self.restore_backup)

        backup_hbox_layout.addWidget(btn_backup)
        backup_hbox_layout.addWidget(btn_restore)
        backup_group.setLayout(backup_hbox_layout)

        # 🔹 افزودن هر دو بخش به صفحه
        main_layout.addWidget(settings_group)
        main_layout.addWidget(backup_group)
        main_layout.addStretch()

        return page

    # ---------- Data ----------
    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    d = json.load(f)
                self.members = d.get("members", [])
                self.books = d.get("books", [])
                self.loans = d.get("loans", [])
                self.settings.update(d.get("settings", {}))
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "خطا", f"خطا در بارگذاری داده‌ها:\n{e}")

    def save_data(self):
        d = {"members": self.members, "books": self.books, "loans": self.loans, "settings": self.settings}
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

    # ---------- Refresh UI ----------
    def refresh_ui(self):
        self.update_stats()
        self.load_members_table()
        self.load_books_table()
        self.update_loan_combos()
        self.load_active_loans()
        self.update_overdue_table()

    def update_stats(self):
        self.lbl_members_count.setText(str(len(self.members)))
        self.lbl_books_count.setText(str(len(self.books)))
        active_loans = len([l for l in self.loans if not l.get("return_date")])
        self.lbl_loans_count.setText(str(active_loans))
        available_books = sum(b.get("available_copies", 0) for b in self.books)
        self.lbl_available_count.setText(str(available_books))

    def update_overdue_table(self):
        self.overdue_table.setSortingEnabled(False)
        self.overdue_table.setRowCount(0)
        today = datetime.date.today()
        for loan in self.loans:
            if loan.get("return_date") is None:
                try:
                    due = datetime.datetime.strptime(loan.get("due_date",""), "%Y-%m-%d").date()
                    if due < today:
                        days = (today - due).days
                        mem = next((m for m in self.members if m.get("student_id")==loan.get("member_id")), None)
                        memname = f"{mem.get('first_name','')} {mem.get('last_name','')}" if mem else loan.get("member_id")
                        fine_per_day = self.settings.get("fine_per_day", 1000)
                        fine = days * fine_per_day
                        r = self.overdue_table.rowCount()
                        self.overdue_table.insertRow(r)
                        
                        # ستون‌های متنی
                        self.overdue_table.setItem(r, 0, QtWidgets.QTableWidgetItem(memname))
                        self.overdue_table.setItem(r, 1, QtWidgets.QTableWidgetItem(loan.get("book_title","")))
                        self.overdue_table.setItem(r, 2, QtWidgets.QTableWidgetItem(to_jalali(loan.get("due_date",""))))
                        
                        # ستون‌های عددی با آیتم مخصوص
                        self.overdue_table.setItem(r, 3, NumericTableWidgetItem(days))
                        self.overdue_table.setItem(r, 4, NumericTableWidgetItem(fine, "{:,}"))
                        
                except Exception as e:
                    print(f"Error in update_overdue_table: {e}")
                    continue
        self.overdue_table.setSortingEnabled(True)

    def load_members_table(self, filtered: List[Dict] = None):
        self.members_table.setSortingEnabled(False)
        rows = filtered if filtered is not None else self.members
        self.members_table.setRowCount(0)
        for m in rows:
            r = self.members_table.rowCount(); self.members_table.insertRow(r)
            self.members_table.setItem(r,0, QtWidgets.QTableWidgetItem(m.get("student_id","")))
            self.members_table.setItem(r,1, QtWidgets.QTableWidgetItem(m.get("national_id","")))
            self.members_table.setItem(r,2, QtWidgets.QTableWidgetItem(m.get("phone","")))
            self.members_table.setItem(r,3, QtWidgets.QTableWidgetItem(m.get("first_name","")))
            self.members_table.setItem(r,4, QtWidgets.QTableWidgetItem(m.get("last_name","")))
        self.members_table.setSortingEnabled(True)

    def load_books_table(self, filtered: List[Dict] = None):
        self.books_table.setSortingEnabled(False)
        rows = filtered if filtered is not None else self.books
        self.books_table.setRowCount(0)
                
        for i, b in enumerate(rows):
            r = self.books_table.rowCount()
            self.books_table.insertRow(r)
            
            # دریافت اطلاعات با مقادیر پیش‌فرض
            title = b.get("title", "بدون عنوان") or "بدون عنوان"
            author = b.get("author", "بدون نویسنده") or "بدون نویسنده"
            publish_date = b.get("publish_date", "تاریخ نامشخص") or "تاریخ نامشخص"
            total_copies = b.get("total_copies", 0)
            available_copies = b.get("available_copies", 0)
                        
            # ایجاد آیتم‌ها و تنظیم مستقیم متن
            title_item = QtWidgets.QTableWidgetItem()
            title_item.setText(title)
            
            author_item = QtWidgets.QTableWidgetItem()
            author_item.setText(author)
            
            date_item = QtWidgets.QTableWidgetItem()
            date_item.setText(to_jalali(publish_date))
            
            # وضعیت کتاب
            if available_copies > 0:
                status = f"آزاد ({available_copies} از {total_copies})"
            else:
                status = f"امانت داده شده (0 از {total_copies})"
            
            status_item = QtWidgets.QTableWidgetItem()
            status_item.setText(status)
            
            # قرار دادن آیتم‌ها در جدول
            self.books_table.setItem(r, 0, title_item)
            self.books_table.setItem(r, 1, author_item)
            self.books_table.setItem(r, 2, date_item)
            self.books_table.setItem(r, 3, status_item)
        self.books_table.setSortingEnabled(True)
        
    def load_active_loans(self):
        self.active_loans_table.setSortingEnabled(False)
        self.active_loans_table.setRowCount(0)
        for loan in self.loans:
            if loan.get("return_date") is None:
                r = self.active_loans_table.rowCount()
                self.active_loans_table.insertRow(r)
                
                # ستون شناسه (عددی)
                self.active_loans_table.setItem(r, 0, NumericTableWidgetItem(loan.get("id", 0)))
                
                mem = next((m for m in self.members if m.get("student_id")==loan.get("member_id")), None)
                memname = f"{mem.get('first_name','')} {mem.get('last_name','')}" if mem else loan.get("member_id")
                self.active_loans_table.setItem(r, 1, QtWidgets.QTableWidgetItem(memname))
                self.active_loans_table.setItem(r, 2, QtWidgets.QTableWidgetItem(loan.get("book_title","")))
                self.active_loans_table.setItem(r, 3, QtWidgets.QTableWidgetItem(to_jalali(loan.get("loan_date",""))))
                self.active_loans_table.setItem(r, 4, QtWidgets.QTableWidgetItem(to_jalali(loan.get("due_date",""))))
        self.active_loans_table.setSortingEnabled(True)

    def update_loan_combos(self):
        # Insert a default empty option first so nothing is selected by default
        self.loan_member_combo.clear()
        self.loan_member_combo.addItem("— انتخاب عضو —", "")
        for m in self.members:
            self.loan_member_combo.addItem(f"{m.get('first_name','')} {m.get('last_name','')} ({m.get('student_id','')})", m.get("student_id"))
        self.loan_member_combo.setCurrentIndex(0)

        self.loan_book_combo.clear()
        self.loan_book_combo.addItem("— انتخاب کتاب —", "")
        for b in self.books:
            if b.get("available_copies",0) > 0:
                self.loan_book_combo.addItem(f"{b.get('id','')} - {b.get('title','')} ({b.get('available_copies',0)} نسخه)", b.get("id"))
        self.loan_book_combo.setCurrentIndex(0)

    # ---------- Member ops ----------
    def add_member(self):
        sid = self.input_student_id.text().strip()
        if not sid:
            QtWidgets.QMessageBox.warning(self, "خطا", "شماره دانشجویی را وارد کنید")
            return
        if any(m.get("student_id")==sid for m in self.members):
            QtWidgets.QMessageBox.warning(self, "خطا", "عضو با این شماره دانشجویی وجود دارد")
            return
        member = {"student_id": sid,
                  "national_id": self.input_national_id.text().strip(),
                  "phone": self.input_phone.text().strip(),
                  "first_name": self.input_first_name.text().strip(),
                  "last_name": self.input_last_name.text().strip()}
        self.members.append(member)
        self.save_data(); self.load_members_table(); self.update_loan_combos(); self.update_stats()
        for w in [self.input_student_id, self.input_national_id, self.input_phone, self.input_first_name, self.input_last_name]:
            w.clear()
        QtWidgets.QMessageBox.information(self, "موفقیت", "عضو افزوده شد ✅")

    def search_members(self):
        q = self.member_search.text().strip()
        if not q:
            self.load_members_table()
            return

        # تقسیم عبارت جستجو به کلمات
        search_terms = [term.strip().lower() for term in q.split() if term.strip()]

        if not search_terms:
            self.load_members_table()
            return

        filtered = []
        for m in self.members:
            # ترکیب فیلدهای متنی
            full_name = f"{m.get('first_name','')} {m.get('last_name','')}".lower()
            student_id = m.get('student_id', '').lower()
            national_id = m.get('national_id', '').lower()
            phone = m.get('phone', '').lower()

            # همه کلمات جستجو باید در یکی از این فیلدها باشند
            if all(
                any(term in field for field in [full_name, student_id, national_id, phone])
                for term in search_terms
            ):
                filtered.append(m)

        self.load_members_table(filtered)

    def edit_member(self):
        r = self.members_table.currentRow()
        if r < 0:
            QtWidgets.QMessageBox.warning(self, "هشدار", "یک عضو انتخاب کنید")
            return
        sid = self.members_table.item(r,0).text()
        member = next((m for m in self.members if m.get("student_id")==sid), None)
        if not member:
            QtWidgets.QMessageBox.warning(self, "خطا", "عضو پیدا نشد"); return
        dlg = QtWidgets.QDialog(self); 
        dlg.setMinimumWidth(360); 
        dlg.setWindowTitle("ویرایش عضو"); 
        dlg.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)  # اضافه شد
        layout = QtWidgets.QFormLayout(dlg)
        layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)  # اضافه شد
        
        # ایجاد validator
        only_digits_validator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression("[0-9]*"))
        
        e_sid = QtWidgets.QLineEdit(member.get("student_id","")); 
        e_nid = QtWidgets.QLineEdit(member.get("national_id",""))
        e_phone = QtWidgets.QLineEdit(member.get("phone","")); 
        e_fn = QtWidgets.QLineEdit(member.get("first_name","")); 
        e_ln = QtWidgets.QLineEdit(member.get("last_name",""))
        
        # اعمال validator
        e_sid.setValidator(only_digits_validator)
        e_nid.setValidator(only_digits_validator)
        e_phone.setValidator(only_digits_validator)
        
        # راست‌چین کردن فیلدهای ورودی
        # for field in [e_sid, e_nid, e_phone, e_fn, e_ln]:
            # field.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
            # field.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        
        layout.addRow("شماره دانشجویی:", e_sid); 
        layout.addRow("کد ملی:", e_nid); 
        layout.addRow("نام:", e_fn); 
        layout.addRow("نام خانوادگی:", e_ln); 
        layout.addRow("تلفن:", e_phone)
        
        btn = QtWidgets.QPushButton("ذخیره"); 
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)); 
        btn.clicked.connect(lambda: (member.update({"student_id":e_sid.text().strip(),"national_id":e_nid.text().strip(),"phone":e_phone.text().strip(),"first_name":e_fn.text().strip(),"last_name":e_ln.text().strip()}), self.save_data(), self.load_members_table(), self.update_loan_combos(), dlg.accept()))
        layout.addRow(btn); 
        dlg.exec()

    def delete_member(self):
        r = self.members_table.currentRow()
        if r < 0:
            QtWidgets.QMessageBox.warning(self, "هشدار", "یک عضو انتخاب کنید"); return
        sid = self.members_table.item(r,0).text()
        if any(l for l in self.loans if l.get("member_id")==sid and not l.get("return_date")):
            QtWidgets.QMessageBox.critical(self, "خطا", "این عضو کتابی به امانت دارد و نمی‌توان حذف کرد"); return
        ans = QtWidgets.QMessageBox.question(self, "تأیید", "آیا حذف شود؟")
        if ans == QtWidgets.QMessageBox.StandardButton.Yes:
            self.members = [m for m in self.members if m.get("student_id")!=sid]; self.save_data(); self.load_members_table(); self.update_loan_combos(); self.update_stats()

    # ---------- Book ops ----------
    def add_book(self):
        title = self.input_title.text().strip(); author = self.input_author.text().strip()
        publish = self.input_publish.text().strip(); copies = self.input_copies.value()
        if not title or not author:
            QtWidgets.QMessageBox.warning(self, "خطا", "عنوان و نویسنده را وارد کنید"); return
        book_id = f"{title}_{author}_{publish}".replace(" ", "_")
        existing = next((b for b in self.books if b.get("id")==book_id), None)
        if existing:
            existing["total_copies"] = existing.get("total_copies",0) + copies
            existing["available_copies"] = existing.get("available_copies",0) + copies
        else:
            b = {"id": book_id, "title": title, "author": author, "publish_date": publish, "total_copies": copies, "available_copies": copies, "is_borrowed": False}
            self.books.append(b)
        self.save_data(); self.load_books_table(); self.update_loan_combos(); self.update_stats()
        self.input_title.clear(); self.input_author.clear(); self.input_publish.clear(); self.input_copies.setValue(1)
        QtWidgets.QMessageBox.information(self, "موفقیت", "کتاب افزوده شد ✅")

    def search_books(self):
        q = self.book_search.text().strip().lower()
        if not q:
            self.load_books_table(); return
        filtered = [b for b in self.books if q in b.get("title","").lower() or q in b.get("author","").lower() or q in b.get("publish_date","").lower()]
        self.load_books_table(filtered)

    def edit_book(self):
        r = self.books_table.currentRow()
        if r < 0: 
            QtWidgets.QMessageBox.warning(self, "هشدار", "یک کتاب انتخاب کنید")
            return
        
        # دریافت عنوان از جدول
        title_item = self.books_table.item(r, 0)
        if not title_item:
            QtWidgets.QMessageBox.warning(self, "خطا", "عنوان کتاب پیدا نشد")
            return
            
        selected_title = title_item.text()
        
        # نرمال‌سازی حروف فارسی/عربی برای مقایسه بهتر
        def normalize_text(text):
            if not text:
                return ""
            # تبدیل حروف عربی به فارسی
            text = text.replace('ي', 'ی')  # ی عربی به فارسی
            text = text.replace('ك', 'ک')  # ک عربی به فارسی
            text = text.replace('ۂ', 'ه')  # ه عربی به فارسی
            return text.strip()
        
        normalized_selected_title = normalize_text(selected_title)
        
        # پیدا کردن کتاب با تطبیق نرمال‌سازی شده
        book = None
        for b in self.books:
            book_title = b.get("title", "")
            normalized_book_title = normalize_text(book_title)
            
            # مقایسه عنوان‌های نرمال‌سازی شده
            if normalized_book_title == normalized_selected_title:
                book = b
                break
        
        # اگر با عنوان پیدا نشد، سعی کن با ID پیدا کنی
        if not book:
            author_item = self.books_table.item(r, 1)
            selected_author = author_item.text() if author_item else ""
            normalized_selected_author = normalize_text(selected_author)
            
            for b in self.books:
                book_title = b.get("title", "")
                book_author = b.get("author", "")
                
                normalized_book_title = normalize_text(book_title)
                normalized_book_author = normalize_text(book_author)
                
                if (normalized_book_title == normalized_selected_title and 
                    normalized_selected_author and 
                    normalized_book_author == normalized_selected_author):
                    book = b
                    break
        
        if not book:
            QtWidgets.QMessageBox.warning(self, "خطا", f"کتاب پیدا نشد\nعنوان انتخاب شده: '{selected_title}'\nعنوان نرمال‌سازی شده: '{normalized_selected_title}'")
            return
            
        # ادامه کد دیالوگ ویرایش...
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("ویرایش کتاب")
        dlg.setMinimumWidth(360); 
        dlg.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)  # اضافه شد
        layout = QtWidgets.QFormLayout(dlg)
        layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)  # اضافه شد
        
        e_title = QtWidgets.QLineEdit(book.get("title",""))
        e_author = QtWidgets.QLineEdit(book.get("author",""))
        e_pub = QtWidgets.QLineEdit(book.get("publish_date",""))
        e_copies = QtWidgets.QSpinBox()
        e_copies.setRange(1,10000)
        e_copies.setValue(book.get("total_copies",1))
        
        # راست‌چین کردن فیلدهای ورودی
        # for field in [e_title, e_author, e_pub]:
            # field.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
            # field.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        
        layout.addRow("عنوان:", e_title)
        layout.addRow("نویسنده:", e_author)
        layout.addRow("تاریخ چاپ:", e_pub)
        layout.addRow("تعداد نسخه‌ها:", e_copies)
        
        def save_book():
            new_title = e_title.text().strip()
            new_author = e_author.text().strip()
            new_total = e_copies.value()
            
            # به‌روزرسانی کتاب
            book.update({
                "title": new_title,
                "author": new_author,
                "publish_date": e_pub.text().strip(),
                "total_copies": new_total
            })
            
            # محاسبه نسخه‌های موجود
            diff = new_total - book.get("total_copies", 0)
            book["available_copies"] = max(0, book.get("available_copies", 0) + diff)
            
            # به‌روزرسانی ID کتاب اگر عنوان یا نویسنده تغییر کرد
            if new_title != book.get("title") or new_author != book.get("author"):
                book["id"] = f"{new_title}_{new_author}".replace(" ", "_")
            
            self.save_data()
            self.load_books_table()
            dlg.accept()
        
        b = QtWidgets.QPushButton("ذخیره")
        b.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        b.clicked.connect(save_book)
        layout.addRow(b)
        dlg.exec()
    
    def delete_book(self):
        r = self.books_table.currentRow(); 
        if r < 0: QtWidgets.QMessageBox.warning(self, "هشدار", "یک کتاب انتخاب کنید"); return
        title = self.books_table.item(r,0).text(); author = self.books_table.item(r,1).text()
        book = next((b for b in self.books if b.get("title")==title and b.get("author")==author), None)
        if not book: QtWidgets.QMessageBox.warning(self, "خطا", "کتاب پیدا نشد"); return
        if book.get("available_copies",0) < book.get("total_copies",0):
            QtWidgets.QMessageBox.critical(self, "خطا", "این کتاب به امانت داده شده و نمی‌توان حذف کرد"); return
        ans = QtWidgets.QMessageBox.question(self, "تأیید", "آیا حذف شود؟")
        if ans == QtWidgets.QMessageBox.StandardButton.Yes:
            self.books = [b for b in self.books if not (b.get("title")==title and b.get("author")==author)]; self.save_data(); self.load_books_table(); self.update_loan_combos(); self.update_stats()

    # ---------- Loan ops ----------
    def loan_book(self):
        # اطمینان از انتخاب عضو و کتاب
        member_id = self.loan_member_combo.currentData()
        book_id = self.loan_book_combo.currentData()
        if not member_id or not book_id:
            QtWidgets.QMessageBox.warning(self, "خطا", "لطفاً یک عضو و یک کتاب انتخاب کنید")
            return

        # پیدا کردن کتاب انتخاب‌شده
        book = next((b for b in self.books if b.get("id") == book_id), None)

        # 🟢 ایجاد دیالوگ تعیین روزهای امانت (با مقدار پیش‌فرض از تنظیمات)
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("تعیین مدت امانت")
        dialog.setLayout(QtWidgets.QVBoxLayout())

        label = QtWidgets.QLabel("مدت امانت (روز):")
        spin = QtWidgets.QSpinBox()
        spin.setRange(1, 365)
        spin.setValue(self.settings.get("default_loan_period", 14))
        spin.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        buttons = QtWidgets.QDialogButtonBox()
        btn_ok = buttons.addButton("تأیید", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        btn_cancel = buttons.addButton("انصراف", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)

        dialog.layout().addWidget(label)
        dialog.layout().addWidget(spin)
        dialog.layout().addWidget(buttons)

        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)

        # اگر کاربر انصراف داد
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        period = spin.value()  # تعداد روز امانت انتخاب‌شده توسط کاربر

        # 🧮 ثبت امانت جدید
        loan_date = today_gregorian_str()
        due_date = (datetime.date.today() + datetime.timedelta(days=period)).strftime("%Y-%m-%d")
        loan = {
            "id": len(self.loans) + 1,
            "member_id": member_id,
            "book_id": book_id,
            "book_title": book.get("title", "") if book else book_id,
            "loan_date": loan_date,
            "due_date": due_date,
            "return_date": None,
            "loan_period": period
        }

        if book:
            book["available_copies"] = max(0, book.get("available_copies", 0) - 1)
            if book.get("available_copies", 0) == 0:
                book["is_borrowed"] = True

        # ذخیره تغییرات
        self.loans.append(loan)
        self.save_data()
        self.load_active_loans()
        self.update_loan_combos()
        self.load_books_table()
        self.update_overdue_table()
        self.update_stats()

        QtWidgets.QMessageBox.information(
            self,
            "موفقیت",
            f"کتاب امانت داده شد — سررسید: {to_jalali(due_date)}"
        )
        
    def search_loans(self):
        self.active_loans_table.setSortingEnabled(False)
        q = self.loan_search.text().strip().lower()
        if not q:
            self.load_active_loans()
            return

        filtered = []
        for loan in self.loans:
            if loan.get("return_date") is not None:
                continue  # فقط امانت‌های فعال نمایش داده شوند
            member = next((m for m in self.members if m.get("student_id") == loan.get("member_id")), {})
            memname = f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
            # بررسی تطابق در همه‌ی فیلدها
            if (
                q in str(loan.get("id", "")).lower()
                or q in memname.lower()
                or q in loan.get("book_title", "").lower()
                or q in loan.get("loan_date", "").lower()
                or q in loan.get("due_date", "").lower()
            ):
                filtered.append(loan)

        # بارگذاری مجدد جدول فقط با ردیف‌های فیلتر شده
        self.active_loans_table.setRowCount(0)
        for loan in filtered:
            r = self.active_loans_table.rowCount()
            self.active_loans_table.insertRow(r)
            self.active_loans_table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(loan.get("id", ""))))
            mem = next((m for m in self.members if m.get("student_id") == loan.get("member_id")), None)
            memname = f"{mem.get('first_name', '')} {mem.get('last_name', '')}" if mem else loan.get("member_id")
            self.active_loans_table.setItem(r, 1, QtWidgets.QTableWidgetItem(memname))
            self.active_loans_table.setItem(r, 2, QtWidgets.QTableWidgetItem(loan.get("book_title", "")))
            self.active_loans_table.setItem(r, 3, QtWidgets.QTableWidgetItem(to_jalali(loan.get("loan_date", ""))))
            self.active_loans_table.setItem(r, 4, QtWidgets.QTableWidgetItem(to_jalali(loan.get("due_date", ""))))
        self.active_loans_table.setSortingEnabled(True)

    def renew_loan(self):
        r = self.active_loans_table.currentRow()
        if r < 0:
            QtWidgets.QMessageBox.warning(self, "هشدار", "یک امانت انتخاب کنید")
            return

        loan_id = int(self.active_loans_table.item(r, 0).text())
        loan = next((l for l in self.loans if l.get("id") == loan_id), None)
        if not loan:
            QtWidgets.QMessageBox.warning(self, "خطا", "امانت پیدا نشد")
            return

        # 🟢 ساخت دیالوگ سفارشی برای تمدید
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("تمدید امانت")
        dialog.setLayout(QtWidgets.QVBoxLayout())

        label = QtWidgets.QLabel("دوره تمدید (روز):")
        spin = QtWidgets.QSpinBox()
        spin.setRange(1, 365)
        spin.setValue(self.settings.get("default_loan_period", 14))
        spin.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        buttons = QtWidgets.QDialogButtonBox()
        btn_ok = buttons.addButton("تأیید", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        btn_cancel = buttons.addButton("انصراف", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)

        dialog.layout().addWidget(label)
        dialog.layout().addWidget(spin)
        dialog.layout().addWidget(buttons)

        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)

        # نمایش دیالوگ
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            days = spin.value()
            due = datetime.datetime.strptime(loan.get("due_date"), "%Y-%m-%d")
            new_due = (due + datetime.timedelta(days=days)).strftime("%Y-%m-%d")

            loan["due_date"] = new_due
            loan["renewed"] = True
            loan["loan_period"] = loan.get("loan_period", 0) + days

            self.save_data()
            self.load_active_loans()
            self.update_overdue_table()

            QtWidgets.QMessageBox.information(
                self,
                "موفقیت",
                f"تمدید شد — تاریخ جدید: {to_jalali(new_due)}"
            )

    def return_book(self):
        r = self.active_loans_table.currentRow()
        if r < 0:
            QtWidgets.QMessageBox.warning(self, "خطا", "یک امانت انتخاب کنید")
            return

        loan_id = int(self.active_loans_table.item(r, 0).text())
        loan = next((l for l in self.loans if l.get("id") == loan_id), None)
        if not loan:
            QtWidgets.QMessageBox.warning(self, "خطا", "امانت پیدا نشد")
            return

        today = datetime.date.today()
        due_date = datetime.datetime.strptime(loan.get("due_date"), "%Y-%m-%d").date()
        days_overdue = (today - due_date).days if today > due_date else 0
        fine_per_day = self.settings.get("fine_per_day", 1000)
        fine = days_overdue * fine_per_day

        loan["return_date"] = today.strftime("%Y-%m-%d")

        # 🔹 اگر جریمه وجود دارد
        if fine > 0:
            msg = QtWidgets.QMessageBox(self)
            msg.setWindowTitle("جریمه دیرکرد")
            msg.setText(
                f"کتاب با تأخیر {days_overdue} روز بازگردانده شد.\n"
                f"مبلغ جریمه: {fine:,} تومان"
            )
            pay_btn = msg.addButton("💰 تسویه جریمه", QtWidgets.QMessageBox.ButtonRole.AcceptRole)
            msg.addButton("بعداً پرداخت شود", QtWidgets.QMessageBox.ButtonRole.RejectRole)
            msg.exec()

            if msg.clickedButton() == pay_btn:
                loan["fine_paid"] = True
                loan["unpaid_fine"] = 0
                QtWidgets.QMessageBox.information(self, "تسویه", "جریمه تسویه شد ✅")
            else:
                loan["fine_paid"] = False
                loan["unpaid_fine"] = fine
                QtWidgets.QMessageBox.information(self, "ثبت", "کتاب بازگردانده شد و جریمه در حساب باقی ماند ⚠️")
        else:
            loan["fine_paid"] = True
            loan["unpaid_fine"] = 0
            QtWidgets.QMessageBox.information(self, "بازگشت", "بازگشت با موفقیت ثبت شد ✅")

        # 🔹 بروزرسانی کتاب‌ها و ذخیره
        book = next((b for b in self.books if b.get("id") == loan.get("book_id")), None)
        if book:
            book["available_copies"] = book.get("available_copies", 0) + 1
            if book["available_copies"] > 0:
                book["is_borrowed"] = False

        self.save_data()
        self.update_loan_combos()
        self.load_books_table()        
        self.load_active_loans()
        self.update_overdue_table()
        self.update_stats()

    # ---------- Details search ----------
    def search_member_details(self):
        self.member_active_loans.setSortingEnabled(False)
        self.member_history.setSortingEnabled(False)
        q = self.member_detail_search.text().strip().lower()
        if not q:
            self.member_info_label.setText("")
            self.member_active_loans.setRowCount(0)
            self.member_history.setRowCount(0)
            return

        member = next(
            (m for m in self.members if
             q in m.get("student_id", "").lower()
             or q in m.get("first_name", "").lower()
             or q in m.get("phone", "").lower()
             or q in m.get("national_id", "").lower()
             or q in m.get("last_name", "").lower()), None
        )
        if not member:
            self.member_info_label.setText("عضو پیدا نشد")
            return

        self.selected_member_id = member.get("student_id")

        info = (
            f"نام: {member.get('first_name','')} {member.get('last_name','')}\n"
            f"شماره دانشجویی: {member.get('student_id','')}\n"
            f"کد ملی: {member.get('national_id','')}\n"
            f"تلفن: {member.get('phone','')}"
        )
        self.member_info_label.setText(info)

        member_loans = [l for l in self.loans if l.get("member_id") == member.get("student_id")]
        self.member_active_loans.setRowCount(0)
        self.member_history.setRowCount(0)

        # محاسبه جریمه کل
        total_fine = 0
        fine_per_day = self.settings.get("fine_per_day", 1000)
        today = datetime.date.today()
        
        for loan in member_loans:
            if not loan.get("fine_paid", False):
                total_fine += loan.get("unpaid_fine", 0)
                
            if loan.get("return_date") is None:
                r = self.member_active_loans.rowCount()
                self.member_active_loans.insertRow(r)
                
                self.member_active_loans.setItem(r, 0, QtWidgets.QTableWidgetItem(loan.get("book_title","")))
                self.member_active_loans.setItem(r, 1, QtWidgets.QTableWidgetItem(to_jalali(loan.get("loan_date",""))))
                self.member_active_loans.setItem(r, 2, QtWidgets.QTableWidgetItem(to_jalali(loan.get("due_date",""))))
                
                due = datetime.datetime.strptime(loan.get("due_date"), "%Y-%m-%d").date()
                days_remaining = (due - today).days
                
                # ستون روزهای باقی‌مانده (عددی)
                self.member_active_loans.setItem(r, 3, NumericTableWidgetItem(days_remaining))
                
                if due < today:
                    days = (today - due).days
                    fine = days * fine_per_day
                    total_fine += fine
                    self.member_active_loans.setItem(r, 4, NumericTableWidgetItem(fine, "{:,}"))
                else:
                    self.member_active_loans.setItem(r, 4, NumericTableWidgetItem(0, "{:,}"))
                    
            else:
                r2 = self.member_history.rowCount()
                self.member_history.insertRow(r2)
                
                self.member_history.setItem(r2, 0, QtWidgets.QTableWidgetItem(loan.get("book_title","")))
                self.member_history.setItem(r2, 1, QtWidgets.QTableWidgetItem(to_jalali(loan.get("loan_date",""))))
                self.member_history.setItem(r2, 2, QtWidgets.QTableWidgetItem(to_jalali(loan.get("due_date",""))))
                self.member_history.setItem(r2, 3, QtWidgets.QTableWidgetItem(to_jalali(loan.get("return_date","")) if loan.get("return_date") else "-"))
                self.member_history.setItem(r2, 4, QtWidgets.QTableWidgetItem("فعال" if not loan.get("return_date") else "بازگشته"))
                
                unpaid_fine = loan.get("unpaid_fine", 0)
                self.member_history.setItem(r2, 5, NumericTableWidgetItem(unpaid_fine, "{:,}"))

        self.member_active_loans.setSortingEnabled(True)
        self.member_history.setSortingEnabled(True)
        self.member_total_fine_label.setText(f"مجموع جریمه: {total_fine:,} تومان")

    def search_book_details(self):
        self.book_history.setSortingEnabled(False)
        q = self.book_detail_search.text().strip().lower()
        if not q:
            self.book_info_label.setText(""); self.book_history.setRowCount(0); return
        book = next((b for b in self.books if q in b.get("title","").lower() or q in b.get("author","").lower() or q in b.get("id","").lower()), None)
        if not book: self.book_info_label.setText("کتاب پیدا نشد"); return
        info = f"عنوان: {book.get('title','')}\nنویسنده: {book.get('author','')}\nتاریخ چاپ: {to_jalali(book.get('publish_date',''))}\nکل نسخه‌ها: {book.get('total_copies',0)}\nنسخه‌های موجود: {book.get('available_copies',0)}"
        self.book_info_label.setText(info)
        book_loans = [l for l in self.loans if l.get("book_id")==book.get("id")]
        self.book_history.setRowCount(0)
        for loan in book_loans:
            r = self.book_history.rowCount(); self.book_history.insertRow(r)
            mem = next((m for m in self.members if m.get("student_id")==loan.get("member_id")), None)
            memname = f"{mem.get('first_name','')} {mem.get('last_name','')}" if mem else loan.get("member_id")
            self.book_history.setItem(r,0, QtWidgets.QTableWidgetItem(memname))
            self.book_history.setItem(r,1, QtWidgets.QTableWidgetItem(to_jalali(loan.get("loan_date",""))))
            self.book_history.setItem(r,2, QtWidgets.QTableWidgetItem(to_jalali(loan.get("due_date",""))))
            self.book_history.setItem(r,3, QtWidgets.QTableWidgetItem(to_jalali(loan.get("return_date","")) if loan.get("return_date") else "-"))
            self.book_history.setItem(r,4, QtWidgets.QTableWidgetItem("فعال" if not loan.get("return_date") else "بازگشته"))
        self.book_history.setSortingEnabled(True)

    # ---------- Double click handlers ----------
    def on_member_double_click(self, row, col):
        sid = self.members_table.item(row, 0).text()
        self.stack.setCurrentWidget(self.page_member_details)
        self.member_detail_search.setText(sid)
        self.search_member_details()

    def on_book_double_click(self, row, col):
        title = self.books_table.item(row, 0).text()
        author = self.books_table.item(row, 1).text()
        publish = self.books_table.item(row, 2).text()
        book_id = f"{title}_{author}_{publish}".replace(" ", "_")
        self.stack.setCurrentWidget(self.page_book_details)
        self.book_detail_search.setText(book_id)
        self.search_book_details()

    # ---------- Settings / Backup ----------
    def save_settings(self):
        self.settings["default_loan_period"] = self.set_loan_period.value()
        self.settings["fine_per_day"] = self.set_fine_per_day.value()
        self.save_data(); QtWidgets.QMessageBox.information(self, "موفقیت", "تنظیمات ذخیره شد ✅")

    def create_backup(self):
        try:
            if not os.path.exists("backup"): os.makedirs("backup")
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = os.path.join("backup", f"library_backup_{ts}.json")
            with open(fname, "w", encoding="utf-8") as f:
                json.dump({"members": self.members, "books": self.books, "loans": self.loans, "settings": self.settings}, f, ensure_ascii=False, indent=2)
            QtWidgets.QMessageBox.information(self, "پشتیبان", f"پشتیبان ذخیره شد:\n{fname}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"خطا در پشتیبان‌گیری:\n{e}")

    def restore_backup(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, "انتخاب پشتیبان", "", "JSON Files (*.json);;All Files (*)")
        if not fname: return
        try:
            with open(fname, "r", encoding="utf-8") as f:
                d = json.load(f)
            self.members = d.get("members", []); self.books = d.get("books", []); self.loans = d.get("loans", []); self.settings.update(d.get("settings", {}))
            self.save_data(); self.refresh_ui(); QtWidgets.QMessageBox.information(self, "بازیابی", "بازیابی انجام شد ✅")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "خطا", f"خطا در بازیابی:\n{e}")

    # ---------- UI polish ----------
    def apply_styles(self):
        if QT_MATERIAL_AVAILABLE:
            try:
                apply_stylesheet(app, theme='light_cyan_500.xml')
            except Exception:
                pass

        # فقط دکمه‌های داخل section_card را سبز کنید
        custom_css = """
        QPushButton {
            background-color: #4CAF50 !important;
            color: white !important;
            border: none !important;
            padding: 8px 16px !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            font-size: 13px !important;
            min-height: 30px !important;
        }
        QPushButton:hover {
            background-color: #45a049 !important;
        }
        QPushButton:pressed {
            background-color: #3d8b40 !important;
        }

        /* دکمه‌های خطر (حذف) */
        QPushButton[danger="true"] {
            background-color: #f44336 !important;
        }
        QPushButton[danger="true"]:hover {
            background-color: #da190b !important;
        }

        /* دکمه‌های اطلاعات (ویرایش) */
        QPushButton[info="true"] {
            background-color: #2196F3 !important;
        }
        QPushButton[info="true"]:hover {
            background-color: #0b7dda !important;
        }
        """

        # اعمال روی کل برنامه
        app.setStyleSheet(app.styleSheet() + custom_css)

# ---------- Run ----------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # Provide a Persian-friendly default font if available
    font = QFont("Vazirmatn", 10)
    if not QFontInfo(font).family():
        font = QFont("Tahoma", 10)
    app.setFont(font)
    icon_path = os.path.join(
        getattr(sys, "_MEIPASS", os.path.dirname(__file__)),
        "icon.ico"
    )
    app.setWindowIcon(QIcon(icon_path))

    win = LibraryApp()
    win.setWindowIcon(QIcon(icon_path))
    win.show()
    sys.exit(app.exec())
