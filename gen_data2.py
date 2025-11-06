import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('fa_IR')

def generate_large_library_data():
    NUM_MEMBERS = 1000
    NUM_BOOKS = 500
    NUM_ACTIVE_LOANS = 300
    NUM_RETURNED_LOANS = 1000
    
    first_names = ["محمد", "علی", "رضا", "حسین", "فاطمه", "زهرا", "مریم", "سارا", "امیر", "مهدی", 
                  "کاظم", "محسن", "عباس", "احمد", "محمدرضا", "نگین", "نرگس", "یاسمن", "پارسا", "آرش"]
    
    last_names = ["محمدی", "حسینی", "رضایی", "کریمی", "قربانی", "احمدی", "جعفری", "موسوی", 
                 "صادقی", "نجفی", "کاظمی", "امامی", "اشرفی", "مرادی", "رحیمی", "فلاحی"]
    
    book_topics = [
        "تاریخ", "ریاضی", "فیزیک", "شیمی", "ادبیات", "فلسفه", "روانشناسی", 
        "برنامه‌نویسی", "هوش مصنوعی", "داده‌کاوی", "شبکه", "امنیت", "هنر", 
        "موسیقی", "سینما", "تئاتر", "معماری", "مدیریت", "اقتصاد", "حقوق"
    ]
    
    book_titles = [
        "مبانی", "اصول", "تئوری", "کاربردی", "پیشرفته", "مقدماتی", "تحلیلی",
        "عملی", "نظری", "کلاسیک", "مدرن", "معاصر", "دیجیتال", "سنتی"
    ]
    
    persian_authors = [
        "دکتر شریفی", "پروفسور کرمانی", "استاد محمدی", "دکتر احمدی", "پروفسور رضایی",
        "دکتر جعفری", "استاد حسینی", "دکتر موسوی", "پروفسور نجفی", "دکتر کاظمی"
    ]

    # تولید اعضا
    members = []
    for i in range(NUM_MEMBERS):
        student_id = fake.unique.numerify(text="########")
        national_id = fake.unique.numerify(text="###########")
        
        members.append({
            "student_id": student_id,
            "national_id": national_id,
            "phone": fake.phone_number(),
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names)
        })

    # تولید کتاب‌ها
    books = []
    used_book_ids = set()
    
    for i in range(NUM_BOOKS):
        topic = random.choice(book_topics)
        title_word = random.choice(book_titles)
        author = random.choice(persian_authors)
        publish_date = str(random.randint(1380, 1402))
        
        title = f"{title_word} {topic}"
        
        # ساخت ID جدید به سبک درخواستی
        book_id = f"{title}_{author}_{publish_date}".replace(" ", "_")
        
        # اطمینان از یکتا بودن ID
        original_book_id = book_id
        counter = 1
        while book_id in used_book_ids:
            book_id = f"{original_book_id}_{counter}"
            counter += 1
        
        used_book_ids.add(book_id)
        
        total_copies = random.randint(1, 10)
        
        books.append({
            "id": book_id,
            "title": title,
            "author": author,
            "publish_date": publish_date,
            "total_copies": total_copies,
            "available_copies": total_copies,  # Initially all copies are available
            "is_borrowed": False
        })

    # تولید امانت‌ها
    loans = []
    loan_id = 1000
    
    # Track active loans per book
    book_active_loans = {book["id"]: 0 for book in books}
    
    # امانت‌های فعال
    active_loans_created = 0
    max_attempts = NUM_ACTIVE_LOANS * 3  # Prevent infinite loop
    
    while active_loans_created < NUM_ACTIVE_LOANS and max_attempts > 0:
        member = random.choice(members)
        book = random.choice(books)
        
        # Check if book has available copies
        current_loans = book_active_loans[book["id"]]
        if current_loans < book["total_copies"]:
            loan_date = fake.date_between(start_date='-60d', end_date='today')
            due_date = loan_date + timedelta(days=14)
            
            loans.append({
                "id": loan_id,
                "member_id": member["student_id"],
                "book_id": book["id"],
                "book_title": book["title"],
                "loan_date": loan_date.strftime("%Y-%m-%d"),
                "due_date": due_date.strftime("%Y-%m-%d"),
                "return_date": None,
                "loan_period": 14
            })
            
            # Update book active loans count
            book_active_loans[book["id"]] += 1
            loan_id += 1
            active_loans_created += 1
        
        max_attempts -= 1

    # امانت‌های بازگشته شده
    for _ in range(NUM_RETURNED_LOANS):
        member = random.choice(members)
        book = random.choice(books)
        
        loan_date = fake.date_between(start_date='-180d', end_date='-15d')
        due_date = loan_date + timedelta(days=14)
        return_date = due_date + timedelta(days=random.randint(-5, 10))
        
        # محاسبه جریمه
        days_late = max(0, (return_date - due_date).days)
        unpaid_fine = days_late * 1000
        fine_paid = random.choice([True, False])
        
        loans.append({
            "id": loan_id,
            "member_id": member["student_id"],
            "book_id": book["id"],
            "book_title": book["title"],
            "loan_date": loan_date.strftime("%Y-%m-%d"),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "return_date": return_date.strftime("%Y-%m-%d"),
            "loan_period": 14,
            "fine_paid": fine_paid,
            "unpaid_fine": 0 if fine_paid else unpaid_fine
        })
        loan_id += 1

    # Update book availability based on active loans
    for book in books:
        active_loans_count = book_active_loans[book["id"]]
        book["available_copies"] = book["total_copies"] - active_loans_count
        book["is_borrowed"] = active_loans_count > 0

    # ساخت ساختار نهایی
    library_data = {
        "members": members,
        "books": books,
        "loans": loans,
        "settings": {
            "default_loan_period": 14,
            "fine_per_day": 1000
        }
    }
    
    return library_data

def save_large_library_data():
    print("در حال تولید داده‌های کتابخانه...")
    library_data = generate_large_library_data()
    
    print("در حال ذخیره‌سازی در فایل...")
    with open('large_library_data.json', 'w', encoding='utf-8') as f:
        json.dump(library_data, f, ensure_ascii=False, indent=2)
    
    # Validate data consistency
    print("\nبررسی صحت داده‌ها:")
    book_loan_consistency_check(library_data)
    
    print(f"\nتولید داده‌ها با موفقیت انجام شد!")
    print(f"تعداد اعضا: {len(library_data['members'])}")
    print(f"تعداد کتاب‌ها: {len(library_data['books'])}")
    print(f"تعداد امانت‌ها: {len(library_data['loans'])}")
    print(f"تعداد امانت‌های فعال: {sum(1 for loan in library_data['loans'] if loan['return_date'] is None)}")
    
    # نمایش نمونه‌ای از کتاب‌های تولید شده
    print("\nنمونه‌ای از کتاب‌های تولید شده:")
    for i, book in enumerate(library_data['books'][:5]):
        print(f"  {i+1}. ID: {book['id']}")
        print(f"     عنوان: {book['title']}")
        print(f"     نویسنده: {book['author']}")
        print(f"     سال انتشار: {book['publish_date']}")
        print(f"     نسخه‌های موجود: {book['available_copies']}/{book['total_copies']}")
    
    print(f"فایل 'large_library_data.json' ایجاد شد")

def book_loan_consistency_check(library_data):
    """Validate that book availability matches active loans"""
    books = library_data['books']
    loans = library_data['loans']
    
    # Count active loans per book
    active_loans_per_book = {}
    for loan in loans:
        if loan['return_date'] is None:  # Active loan
            book_id = loan['book_id']
            active_loans_per_book[book_id] = active_loans_per_book.get(book_id, 0) + 1
    
    # Check consistency
    inconsistencies = 0
    for book in books:
        expected_available = book['total_copies'] - active_loans_per_book.get(book['id'], 0)
        actual_available = book['available_copies']
        
        if expected_available != actual_available:
            print(f"⚠️  ناسازگاری در کتاب {book['title']}:")
            print(f"   انتظار می‌رفت: {expected_available} نسخه موجود")
            print(f"   مقدار فعلی: {actual_available} نسخه موجود")
            inconsistencies += 1
    
    if inconsistencies == 0:
        print("✅ همه کتاب‌ها با تعداد امانت‌های فعال سازگار هستند")
    else:
        print(f"⚠️  تعداد {inconsistencies} ناسازگاری پیدا شد")

if __name__ == "__main__":
    save_large_library_data()