import json, random, names, datetime, uuid

# -------------------------------------------------
# 1. Members (1000 total)
# -------------------------------------------------
first_names = ["علی", "محمد", "رضا", "حسین", "مهدی", "امیر", "سجاد", "یاسین", "زهرا", "فاطمه", "مریم", "سارا", "نرگس", "لیلا", "آتنا"]
last_names  = ["احمدی", "محمدی", "رضایی", "کریمی", "جعفری", "حسینی", "قربانی", "صادقی", "سلطانی", "یوسفی", "کاظمی", "موسوی", "نجفی", "رضوانی"]

def rand_phone():
    return "0915" + "".join([str(random.randint(0,9)) for _ in range(7)])

members = []
for i in range(1000):
    sid = f"{10000000 + i}"
    nid = f"07{random.randint(0,99999999):08d}"
    members.append({
        "student_id": sid,
        "national_id": nid,
        "phone": rand_phone(),
        "first_name": random.choice(first_names),
        "last_name": random.choice(last_names)
    })

# -------------------------------------------------
# 2. Books (500 total)
# -------------------------------------------------
book_titles  = [f"کتاب {i}" for i in range(1,481)]
book_authors = [f"نویسنده{i}" for i in range(1,481)]

books = []
for i in range(500):
    title = book_titles[i] if i < len(book_titles) else f"رمان {i}"
    author = book_authors[i] if i < len(book_authors) else f"مورخ {i}"
    total = random.randint(1,8)
    avail = random.randint(0, total)
    books.append({
        "id": f"{title}_{author}".replace(" ", "_"),
        "title": title,
        "author": author,
        "publish_date": str(random.randint(1395,1402)),
        "total_copies": total,
        "available_copies": avail,
        "is_borrowed": avail < total,
        "copies_details": []
    })

# -------------------------------------------------
# 3. Loans
# -------------------------------------------------
def rand_date(start, end):
    delta = end - start
    return (start + datetime.timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d")

start = datetime.date(2025,8,1)
end   = datetime.date(2025,10,31)

loans = []
loan_id = 1000

# 300 active loans
for _ in range(300):
    loan_id += 1
    mem = random.choice(members)["student_id"]
    bk  = random.choice([b for b in books if b["available_copies"] > 0])
    loan_date = rand_date(start, end)
    due = (datetime.datetime.strptime(loan_date, "%Y-%m-%d") + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
    loans.append({
        "id": loan_id,
        "member_id": mem,
        "book_id": bk["id"],
        "book_title": bk["title"],
        "loan_date": loan_date,
        "due_date": due,
        "return_date": None,
        "loan_period": 14
    })
    # decrease availability
    bk["available_copies"] -= 1
    bk["is_borrowed"] = True

# 1000 returned loans
for _ in range(1000):
    loan_id += 1
    mem = random.choice(members)["student_id"]
    bk  = random.choice(books)
    loan_date = rand_date(start, datetime.date(2025,10,15))
    due = (datetime.datetime.strptime(loan_date, "%Y-%m-%d") + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
    ret = (datetime.datetime.strptime(loan_date, "%Y-%m-%d") + datetime.timedelta(days=random.randint(5,20))).strftime("%Y-%m-%d")
    fine = max(0, (datetime.datetime.strptime(ret, "%Y-%m-%d") - datetime.datetime.strptime(due, "%Y-%m-%d")).days * 1000)
    loans.append({
        "id": loan_id,
        "member_id": mem,
        "book_id": bk["id"],
        "book_title": bk["title"],
        "loan_date": loan_date,
        "due_date": due,
        "return_date": ret,
        "loan_period": 14,
        "fine_paid": random.choice([True, False]),
        "unpaid_fine": fine if random.choice([True, False]) else 0
    })
    # increase availability back
    bk["available_copies"] = min(bk["available_copies"] + 1, bk["total_copies"])

# -------------------------------------------------
# 4. Final JSON
# -------------------------------------------------
data = {
    "members": members,
    "books": books,
    "loans": loans,
    "settings": {"default_loan_period": 14, "fine_per_day": 1000}
}
with open("library_data_large.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)