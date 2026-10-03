"""
Seed Clean Synthetic Dataset: 1,000 Clean Job Postings & 500 Clean Student CVs
Dựa trên taxonomy ESCO v1.2.1 từ file skill_taxonomy_model_4nganh_FINAL.json
Thị trường lao động Cần Thơ & ĐBSCL - Năm 2026
"""
import json
import sys
import random
from datetime import date, timedelta
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

# ─── 1. BẢNG TỪ ĐIỂN CÔNG TY & CHỨC DANH TẠI CẦN THƠ ───────────────────────

COMPANIES = {
    "IT": [
        "FPT Software Cần Thơ", "Viettel Digital Cần Thơ", "VNPT Cần Thơ",
        "TMA Solutions Cần Thơ", "VNG Corporation - Chi nhánh Cần Thơ",
        "RikkeiSoft Mekong", "BAP Software Cần Thơ", "Enouvo Mekong Hub",
        "Mobifone IT Cần Thơ", "Hekate AI Tech Lab", "Lotus Quality Assurance CT",
        "Cty TNHH Giải Pháp Công Nghệ Mekong", "Can Tho Tech Hub", "BKAV Mekong",
        "NashTech Cần Thơ", "LogiGear Cần Thơ", "KMS Technology Mekong",
        "Giao Hàng Nhanh Tech Cần Thơ", "Shopee Tech Cần Thơ"
    ],
    "Du lịch": [
        "Saigontourist Cần Thơ", "Vietravel Chi nhánh Cần Thơ",
        "Khách sạn Mường Thanh Luxury Cần Thơ", "Vinpearl Hotel Cần Thơ",
        "Victoria Cần Thơ Resort", "Azerai Cần Thơ - Cồn Ấu",
        "Cần Thơ Eco Resort", "TTC Hotel Cần Thơ", "BenThanh Tourist Mekong",
        "Mekong Delta Tours & Cruises", "Khách sạn Ninh Kiều Riverside",
        "Vạn Phát Riverside Hotel", "Resort Cồn Khương Cần Thơ",
        "Làng Du Lịch Mỹ Khánh", "Công ty Du Lịch Nụ Cười Mê Kông"
    ],
    "Logistics": [
        "Cảng Cần Thơ (Can Tho Port)", "Cảng Quốc Tế Cái Cui",
        "Tổng Công Ty Tân Cảng Sài Gòn (Tân Cảng Cần Thơ)",
        "DHL Express Service Point Cần Thơ", "Viettel Post Chi Nhánh Cần Thơ",
        "Giao Hàng Tiết Kiệm Cần Thơ (GHTK)", "J&T Express Cần Thơ",
        "Vinafco Logistics Mekong", "Transimex Logistics Cần Thơ",
        "Công Ty Tiếp Vận Nông Sản Mê Kông", "Cảng Hàng Không Quốc Tế Cần Thơ - Cargo",
        "Mekong Logistics Cold Storage", "Sotrans Mekong Hub",
        "Viconship Cần Thơ", "Hateco Logistics Chi Nhánh Tây Nam Bộ"
    ],
    "Kinh tế": [
        "Ngân hàng Vietcombank - Chi nhánh Cần Thơ", "Ngân hàng BIDV Cần Thơ",
        "Ngân hàng MBBank Cần Thơ", "Công ty CP Dược Hậu Giang (DHG Pharma)",
        "Tập đoàn Thủy sản Minh Phú Cần Thơ", "Công ty CP Nông nghiệp Nam Miền Tây",
        "CASEAMEX - XNK Thủy sản Cần Thơ", "Siêu thị GO! Cần Thơ (Central Retail)",
        "Công ty Kiểm toán AASC - Chi nhánh Cần Thơ", "Ngân hàng ACB Cần Thơ",
        "Công ty CP Phân Bón & Hóa Chất Cần Thơ", "Tập đoàn Lộc Trời - VP Cần Thơ",
        "Công ty CP May Tây Đô", "Công ty TNHH Thuế & Kế Toán Mekong Tax",
        "Khu Công Nghiệp Trà Nóc - Ban QLDA Tài Chính"
    ]
}

JOB_TITLES = {
    "IT": [
        ("Python Backend Developer", ["Python", "FastAPI", "Docker", "SQL", "Git", "REST API"]),
        ("Fullstack Web Developer (Node/React)", ["JavaScript", "TypeScript", "ReactJS", "Node.js", "SQL", "Git"]),
        ("Data Analyst / BI Specialist", ["Data Analysis", "SQL", "Power BI", "Python", "Problem Solving"]),
        ("AI / Machine Learning Engineer", ["Python", "Machine Learning", "Data Analysis", "Docker", "AI Ethics"]),
        ("Mobile App Developer (Flutter/React Native)", ["JavaScript", "Mobile Development", "Git", "REST API", "UI/UX Design"]),
        ("Frontend Developer (React/Vue)", ["JavaScript", "TypeScript", "ReactJS", "HTML/CSS", "Git"]),
        ("DevOps / Cloud Engineer", ["Docker", "Linux", "CI/CD", "Cloud Computing", "Git", "Python"]),
        ("QA / QC Software Tester", ["Software Testing", "Automated Testing", "SQL", "Git", "Problem Solving"]),
        ("Database Administrator (DBA)", ["Database Administration", "SQL", "Performance Tuning", "Linux"]),
        ("Cyber Security Specialist", ["Network Security", "Information Security", "Linux", "Risk Assessment"]),
        ("Systems Analyst / Business Analyst IT", ["Define Technical Requirements", "Systems Development Life-Cycle", "Data Analysis", "Communication"]),
        ("Embedded Systems / IoT Engineer", ["C/C++", "Embedded Systems", "Linux", "Problem Solving"])
    ],
    "Du lịch": [
        ("Hướng Dẫn Viên Du Lịch Nội Địa & Quốc Tế", ["English", "Tour Operations", "Customer Service", "Communication", "Problem Solving"]),
        ("Quản Lý Sảnh & Tiền Sảnh (Duty Manager / Front Office)", ["Customer Service", "Hotel Management", "English", "Leadership", "Customer Complaint Handling"]),
        ("Nhân Viên Lễ Tân Khách Sạn 4-5 Sao", ["Customer Service", "English", "Hotel Booking Software", "Communication", "Interpersonal Skills"]),
        ("Chuyên Viên Sales & Marketing Du Lịch", ["Tourism Marketing", "Social Media", "Customer Service", "Negotiation", "English"]),
        ("Chuyên Viên Điều Hành Tour Du Lịch (Tour Operator)", ["Tour Operations", "Vendor Negotiation", "Logistics Planning", "Problem Solving", "Customer Service"]),
        ("Giám Sát Bộ Phận Ẩm Thực & Nhà Hàng (F&B Supervisor)", ["Food Safety & Hygiene", "Customer Service", "Inventory Control", "Leadership"]),
        ("Quản Lý Dịch Vụ Khách Hàng (Customer Experience Lead)", ["Customer Service", "Customer Complaint Handling", "Teamwork", "English"]),
        ("Chuyên Viên Thiết Kế Tour Sinh Thái ĐBSCL", ["Tour Operations", "Ecotourism Development", "English", "Customer Service"])
    ],
    "Logistics": [
        ("Chuyên Viên Xuất Nhập Khẩu (Import - Export Specialist)", ["International Trade Regulations", "Customs Compliance", "English", "Negotiation", "Documentation"]),
        ("Giám Sát Vận Hành Kho Bãi (Warehouse Supervisor)", ["Warehouse Management", "Inventory Control", "Safety Regulations", "ERP / SAP", "Problem Solving"]),
        ("Chuyên Viên Điều Phối Vận Tải (Transport Dispatcher)", ["Fleet Management", "Transport Route Planning", "Logistics Software", "Problem Solving"]),
        ("Chuyên Viên Khai Báo Hải Quan (Customs Clearance Officer)", ["Customs Compliance", "Tariff Classification", "VNACCS / VCIS Software", "Legal Compliance"]),
        ("Chuyên Viên Kế Hoạch Chuỗi Cung Ứng (Supply Chain Planner)", ["Supply Chain Management", "Demand Forecasting", "Data Analysis", "ERP / SAP", "Excel"]),
        ("Nhân Viên Quản Lý Giao Nhận Hàng Hóa (Freight Forwarding)", ["Freight Forwarding", "Carrier Management", "Customer Service", "English", "Documentation"]),
        ("Kỹ Sư Quản Trị Hệ Thống Kho Lạnh Nông Sản (Cold Chain)", ["Cold Chain Logistics", "Temperature Monitoring", "Quality Control", "Warehouse Management"]),
        ("Giám Sát An Toàn & Chuẩn Hóa Kho (Warehouse EHS Lead)", ["Safety Regulations", "Inventory Control", "Team Leadership", "Risk Management"])
    ],
    "Kinh tế": [
        ("Kế Toán Tổng Hợp (General Accountant)", ["Financial Statements", "Tax Compliance", "Accounting Software (MISA)", "Excel", "Data Analysis"]),
        ("Kế Toán Thuế & Báo Cáo Tài Chính", ["Tax Compliance", "Financial Statements", "Corporate Tax Law", "Accounting Software (MISA)"]),
        ("Chuyên Viên Phân Tích Tài Chính Doanh Nghiệp (Financial Analyst)", ["Financial Analysis", "Cash Flow Modeling", "Excel", "Data Analysis", "English"]),
        ("Kế Toán Trưởng / Phó Phòng Kế Toán", ["Financial Statements", "Financial Management", "Leadership", "Tax Compliance", "Auditing"]),
        ("Kiểm Toán Viên Nội Bộ (Internal Auditor)", ["Internal Auditing", "Risk Management", "Financial Statements", "Regulatory Compliance"]),
        ("Kế Toán Chi Phí & Giá Thành Sản Xuất (Cost Accountant)", ["Cost Accounting", "Inventory Valuation", "ERP / SAP", "Excel", "Analytical Skills"]),
        ("Chuyên Viên Quản Lý Nguồn Vốn & Dòng Tiền (Treasury Officer)", ["Cash Flow Modeling", "Banking Relations", "Negotiation", "Financial Analysis"]),
        ("Chuyên Viên Phân Tích Dữ Liệu Kinh Doanh (Business Data Analyst)", ["Data Analysis", "Power BI", "SQL", "Financial Statements", "Problem Solving"])
    ]
}

UNIVERSITIES = [
    "Trường Đại học Cần Thơ (CTU)",
    "Trường Đại học FPT Cần Thơ",
    "Trường Đại học Nam Cần Thơ (DNC)",
    "Trường Đại học Kỹ thuật - Công nghệ Cần Thơ (CTUT)",
    "Trường Cao đẳng Kinh tế - Kỹ thuật Cần Thơ",
    "Trường Cao đẳng Cần Thơ",
]

MAJORS = {
    "IT": [
        "Công nghệ thông tin", "Kỹ thuật phần mềm", "Khoa học máy tính",
        "Hệ thống thông tin", "Mạng máy tính & Truyền thông dữ liệu", "Trí tuệ nhân tạo (AI)"
    ],
    "Du lịch": [
        "Quản trị dịch vụ du lịch và lữ hành", "Quản trị khách sạn",
        "Quản trị nhà hàng và dịch vụ ăn uống", "Việt Nam học (Chuyên ngành Du lịch)"
    ],
    "Logistics": [
        "Logistics và Quản lý chuỗi cung ứng", "Kinh tế vận tải",
        "Kinh doanh quốc tế (Chuyên ngành Ngoại thương & Logistics)", "Khai thác cảng"
    ],
    "Kinh tế": [
        "Kế toán", "Kiểm toán", "Tài chính - Ngân hàng",
        "Quản trị kinh doanh", "Kinh tế nông nghiệp", "Kinh doanh thương mại"
    ]
}

VIETNAMESE_LAST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
VIETNAMESE_MIDDLE_NAMES = ["Văn", "Thị", "Hữu", "Đức", "Minh", "Thanh", "Hoàng", "Anh", "Xuân", "Quốc", "Ngọc", "Gia", "Bảo", "Đình"]
VIETNAMESE_FIRST_NAMES = [
    "An", "Bình", "Cường", "Dung", "Em", "Hoa", "Khoa", "Linh", "Minh", "Nam",
    "Oanh", "Phúc", "Quân", "Sơn", "Tâm", "Uyên", "Vinh", "Xuân", "Yến", "Tú",
    "Hùng", "Hải", "Tuấn", "Khang", "Trang", "Thảo", "Hương", "Hà", "Phương", "Diễm"
]

def generate_vietnamese_name():
    ln = random.choice(VIETNAMESE_LAST_NAMES)
    mn = random.choice(VIETNAMESE_MIDDLE_NAMES)
    fn = random.choice(VIETNAMESE_FIRST_NAMES)
    return f"{ln} {mn} {fn}"


def main():
    print("🚀 Bắt đầu tạo dữ liệu sạch (1,000 Job Postings & 500 Sinh viên CVs)...")
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3307,
        user="skillgap_user",
        password="skillgap_pass",
        database="skillgap_db",
        charset="utf8mb4",
        autocommit=False
    )
    cursor = conn.cursor()

    try:
        # Xóa dữ liệu cũ để nạp bộ dữ liệu chuẩn
        print("🧹 Đang dọn dẹp dữ liệu cũ...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE survey_skill_ratings;")
        cursor.execute("TRUNCATE TABLE survey_responses;")
        cursor.execute("TRUNCATE TABLE extracted_skills;")
        cursor.execute("TRUNCATE TABLE course_recommendations;")
        cursor.execute("TRUNCATE TABLE skill_catalog;")
        cursor.execute("TRUNCATE TABLE job_postings;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()

        # ─── BƯỚC 1: THIẾT LẬP SKILL CATALOG TỪ TAXONOMY ────────────────────
        print("📚 Khởi tạo danh mục kỹ năng chuẩn hóa (Skill Catalog)...")
        # Danh sách kỹ năng chuẩn theo ngành và kỹ năng mềm
        raw_skills = [
            # IT Skills
            ("Python", "IT"), ("FastAPI", "IT"), ("Docker", "IT"), ("SQL", "IT"),
            ("Git", "IT"), ("REST API", "IT"), ("JavaScript", "IT"), ("TypeScript", "IT"),
            ("ReactJS", "IT"), ("Node.js", "IT"), ("Data Analysis", "IT"),
            ("Power BI", "IT"), ("Machine Learning", "IT"), ("AI Ethics", "IT"),
            ("Linux", "IT"), ("CI/CD", "IT"), ("Cloud Computing", "IT"),
            ("Software Testing", "IT"), ("Automated Testing", "IT"),
            ("Database Administration", "IT"), ("Network Security", "IT"),
            ("Define Technical Requirements", "IT"), ("Systems Development Life-Cycle", "IT"),

            # Du lịch Skills
            ("Tour Operations", "Du lịch"), ("Customer Service", "Du lịch"),
            ("Hotel Management", "Du lịch"), ("Hotel Booking Software", "Du lịch"),
            ("Tourism Marketing", "Du lịch"), ("Food Safety & Hygiene", "Du lịch"),
            ("Customer Complaint Handling", "Du lịch"), ("Ecotourism Development", "Du lịch"),
            ("Interpersonal Skills", "Du lịch"),

            # Logistics Skills
            ("International Trade Regulations", "Logistics"), ("Customs Compliance", "Logistics"),
            ("Warehouse Management", "Logistics"), ("Inventory Control", "Logistics"),
            ("Fleet Management", "Logistics"), ("Transport Route Planning", "Logistics"),
            ("Logistics Software", "Logistics"), ("Supply Chain Management", "Logistics"),
            ("Demand Forecasting", "Logistics"), ("Freight Forwarding", "Logistics"),
            ("Cold Chain Logistics", "Logistics"), ("ERP / SAP", "Logistics"),

            # Kinh tế / Kế toán Skills
            ("Financial Statements", "Kinh tế"), ("Tax Compliance", "Kinh tế"),
            ("Accounting Software (MISA)", "Kinh tế"), ("Financial Analysis", "Kinh tế"),
            ("Financial Management", "Kinh tế"), ("Internal Auditing", "Kinh tế"),
            ("Cost Accounting", "Kinh tế"), ("Cash Flow Modeling", "Kinh tế"),
            ("Excel", "Kinh tế"),

            # Transversal / Soft Skills (Dùng chung cho tất cả các ngành)
            ("English", "Tất cả"), ("Communication", "Tất cả"), ("Problem Solving", "Tất cả"),
            ("Teamwork", "Tất cả"), ("Leadership", "Tất cả"), ("Negotiation", "Tất cả"),
            ("Time Management", "Tất cả"), ("Critical Thinking", "Tất cả")
        ]

        skill_id_map = {}
        for skill_name, ind in raw_skills:
            cursor.execute(
                "INSERT INTO skill_catalog (skill_name, industry, demand_pct, supply_pct, gap_pct, trend_pct) "
                "VALUES (%s, %s, 0.0, 0.0, 0.0, %s)",
                (skill_name, ind, "+0%")
            )
            skill_id_map[skill_name] = cursor.lastrowid
        conn.commit()
        print(f"   ✓ Đã tạo {len(skill_id_map)} kỹ năng chuẩn trong skill_catalog.")

        # ─── BƯỚC 2: TẠO 1,000 TIN TUYỂN DỤNG SẠCH ───────────────────────────
        print("🏢 Đang sinh 1,000 tin tuyển dụng sạch tại Cần Thơ & ĐBSCL...")
        # Tỷ lệ phân bố 4 ngành: IT: 350, Du lịch: 250, Logistics: 200, Kinh tế: 200
        industries_distribution = ["IT"] * 350 + ["Du lịch"] * 250 + ["Logistics"] * 200 + ["Kinh tế"] * 200
        random.seed(42)
        random.shuffle(industries_distribution)

        platforms = [("TopCV", 0.45), ("VietnamWorks", 0.30), ("ITviec", 0.15), ("CareerBuilder", 0.10)]
        districts = [
            "Quận Ninh Kiều, Cần Thơ", "Quận Cái Răng, Cần Thơ", "Quận Bình Thủy, Cần Thơ",
            "Khu Công Nghiệp Trà Nóc, Cần Thơ", "Khu Công Nghệ Cao Cần Thơ", "Quận Ô Môn, Cần Thơ",
            "Cần Thơ (Hybrid/Remote)"
        ]

        start_date = date(2026, 6, 1)
        job_skill_counter = {s: 0 for s in skill_id_map}
        industry_job_counter = {"IT": 0, "Du lịch": 0, "Logistics": 0, "Kinh tế": 0}

        job_ids = []
        for i, ind in enumerate(industries_distribution, start=1):
            industry_job_counter[ind] += 1
            company = random.choice(COMPANIES[ind])
            job_tuple = random.choice(JOB_TITLES[ind])
            title, req_skills = job_tuple[0], list(job_tuple[1])

            # Thêm ngẫu nhiên 1 kỹ năng mềm vào yêu cầu
            soft_skill = random.choice(["English", "Communication", "Problem Solving", "Teamwork"])
            if soft_skill not in req_skills:
                req_skills.append(soft_skill)

            # Lương thực tế theo vị trí
            base_sal = random.randint(8, 22)
            sal_min = base_sal * 1_000_000
            sal_max = (base_sal + random.randint(4, 15)) * 1_000_000

            # Ngày đăng từ 2026-06-01 đến 2026-10-01
            p_days = random.randint(0, 120)
            p_date = start_date + timedelta(days=p_days)

            # Chọn nền tảng
            r_plat = random.random()
            if ind == "IT" and r_plat < 0.3:
                platform = "ITviec"
            else:
                platform = random.choices(["TopCV", "VietnamWorks", "CareerBuilder"], weights=[55, 35, 10])[0]

            loc = random.choice(districts)
            desc = f"Vị trí: {title} tại {company}. Yêu cầu các kỹ năng chuyên môn: {', '.join(req_skills)}. Cơ hội làm việc chuyên nghiệp tại khu vực Cần Thơ."
            src_url = f"https://{platform.lower()}.vn/job/{ind.lower()}-{i}"

            cursor.execute(
                """INSERT INTO job_postings 
                   (title, company, location, industry, description, salary_min, salary_max, posted_date, source_url, source_platform, ai_classified) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (title, company, loc, ind, desc, sal_min, sal_max, p_date, src_url, platform, True)
            )
            jid = cursor.lastrowid
            job_ids.append(jid)

            # Gắn vào extracted_skills
            for sk in req_skills:
                if sk in skill_id_map:
                    job_skill_counter[sk] += 1
                    conf = round(random.uniform(0.88, 0.99), 2)
                    cursor.execute(
                        """INSERT INTO extracted_skills (job_id, skill_name, skill_category, confidence)
                           VALUES (%s, %s, %s, %s)""",
                        (jid, sk, ind, conf)
                    )

        conn.commit()
        print(f"   ✓ Đã tạo thành công {len(job_ids)} tin tuyển dụng & các kỹ năng trích xuất tương ứng.")

        # ─── BƯỚC 3: TẠO 500 CV / KHẢO SÁT SINH VIÊN SẠCH ────────────────────
        print("🎓 Đang sinh 500 hồ sơ sinh viên CV sạch tại các trường Cần Thơ...")
        # Tỷ lệ sinh viên các ngành: IT: 175, Du lịch: 125, Logistics: 100, Kinh tế: 100
        student_distribution = ["IT"] * 175 + ["Du lịch"] * 125 + ["Logistics"] * 100 + ["Kinh tế"] * 100
        random.shuffle(student_distribution)

        student_skill_proficient = {s: 0 for s in skill_id_map}
        industry_student_counter = {"IT": 0, "Du lịch": 0, "Logistics": 0, "Kinh tế": 0}

        survey_ids = []
        for i, ind in enumerate(student_distribution, start=1):
            industry_student_counter[ind] += 1
            st_code = f"SVCT{i:04d}"
            name = generate_vietnamese_name()
            major = random.choice(MAJORS[ind])
            institution = random.choices(
                UNIVERSITIES,
                weights=[40, 16, 16, 12, 8, 8]
            )[0]
            year = random.choices([3, 4, 5], weights=[35, 45, 20])[0]
            c_date = date(2026, 7, 1) + timedelta(days=random.randint(0, 90))

            cursor.execute(
                """INSERT INTO survey_responses (student_code, full_name, major, year_of_study, institution, completed_at)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (st_code, name, major, year, institution, c_date)
            )
            sid = cursor.lastrowid
            survey_ids.append(sid)

            # Đánh giá kỹ năng của sinh viên: kỹ năng ngành + kỹ năng mềm
            # Lấy các kỹ năng thuộc ngành sinh viên đang học
            ind_skills = [s for s, s_ind in raw_skills if s_ind in (ind, "Tất cả")]
            # Sinh viên có rating cho 8-12 kỹ năng
            rated_skills = random.sample(ind_skills, min(len(ind_skills), random.randint(8, 12)))

            for sk in rated_skills:
                # Điểm tự đánh giá từ 30 đến 95
                # Năm 4 hoặc 5 thường có điểm cao hơn năm 3
                bias = 10 if year >= 4 else 0
                rating = random.randint(30 + bias, 90 + bias)
                rating = min(98, rating)

                cursor.execute(
                    """INSERT INTO survey_skill_ratings (survey_id, skill_id, self_rating)
                       VALUES (%s, %s, %s)""",
                    (sid, skill_id_map[sk], rating)
                )

                # Coi là "thành thạo / có năng lực" (Supply) nếu rating >= 65
                if rating >= 65:
                    student_skill_proficient[sk] += 1

        conn.commit()
        print(f"   ✓ Đã tạo thành công {len(survey_ids)} hồ sơ sinh viên CVs & dữ liệu kỹ năng.")

        # ─── BƯỚC 4: TÍNH TOÁN CHÍNH XÁC DEMAND, SUPPLY & SKILL GAP ─────────
        print("📊 Đang tính toán ma trận Demand, Supply và Skill Gap...")
        total_jobs_count = len(job_ids)
        total_students_count = len(survey_ids)

        for sk, sk_id in skill_id_map.items():
            # Xác định ngành của skill
            sk_ind = [s_ind for s_name, s_ind in raw_skills if s_name == sk][0]
            if sk_ind == "Tất cả":
                denom_job = total_jobs_count
                denom_stu = total_students_count
            else:
                denom_job = industry_job_counter[sk_ind]
                denom_stu = industry_student_counter[sk_ind]

            demand_pct = round((job_skill_counter[sk] / denom_job) * 100, 1) if denom_job else 0.0
            supply_pct = round((student_skill_proficient[sk] / denom_stu) * 100, 1) if denom_stu else 0.0
            gap_pct = round(demand_pct - supply_pct, 1)

            # Xu hướng
            trend_val = random.randint(5, 45)
            sign = "+" if gap_pct >= 0 else "-"
            trend_str = f"{sign}{trend_val}%"

            cursor.execute(
                """UPDATE skill_catalog 
                   SET demand_pct = %s, supply_pct = %s, gap_pct = %s, trend_pct = %s 
                   WHERE id = %s""",
                (demand_pct, supply_pct, gap_pct, trend_str, sk_id)
            )

        conn.commit()
        print("   ✓ Đã cập nhật xong chỉ số Demand - Supply - Gap cho toàn bộ kỹ năng.")

        # ─── BƯỚC 5: TẠO GỢI Ý KHÓA HỌC THỰC TẾ ──────────────────────────────
        print("📚 Khởi tạo gợi ý khóa học bù đắp Skill Gap...")
        courses_data = [
            ("Python", "Python for Everybody Specialization", "Coursera × Univ. of Michigan", "https://coursera.org/specializations/python", 1),
            ("Python", "FastAPI - The Complete Course 2026", "Udemy", "https://udemy.com", 2),
            ("Machine Learning", "Machine Learning Specialization", "Coursera × DeepLearning.AI", "https://coursera.org", 1),
            ("Machine Learning", "Google Machine Learning Crash Course", "Google", "https://developers.google.com/machine-learning", 2),
            ("Data Analysis", "Google Data Analytics Professional Certificate", "Coursera × Google", "https://coursera.org", 1),
            ("Power BI", "Microsoft Power BI Data Analyst Associate (PL-300)", "Microsoft Learn", "https://learn.microsoft.com", 1),
            ("Docker", "Docker & Kubernetes: The Practical Guide", "Udemy", "https://udemy.com", 1),
            ("ReactJS", "The Complete 2026 Web Development Bootcamp", "Udemy", "https://udemy.com", 1),
            ("English", "IELTS Academic Preparation Band 6.5+", "British Council Vietnam", "https://britishcouncil.vn", 1),
            ("English", "Business English Communication Skills", "Coursera × Univ. of Washington", "https://coursera.org", 2),
            ("Tour Operations", "Nghiệp Vụ Hướng Dẫn & Quản Lý Tour Chuyên Nghiệp", "Đại học Cần Thơ (CTU)", "https://ctu.edu.vn", 1),
            ("Customer Service", "Customer Service Excellence in Hospitality", "edX × Cornell", "https://edx.org", 1),
            ("Customer Complaint Handling", "Kỹ Năng Xử Lý Than Phiền & Chăm Sóc Khách Hàng", "Viện Quản Trị PACE", "https://pace.edu.vn", 1),
            ("Hotel Management", "Hotel Management: Distribution, Revenue & Demand Management", "Coursera × ESSEC", "https://coursera.org", 1),
            ("Supply Chain Management", "Supply Chain Management Specialization", "Coursera × Rutgers", "https://coursera.org", 1),
            ("Customs Compliance", "Thực Hành Thủ Tục Hải Quan & Khai Báo VNACCS/VCIS", "VCCI Cần Thơ", "https://vccicantho.com.vn", 1),
            ("Warehouse Management", "Warehouse Management and Inventory Operations", "edX", "https://edx.org", 1),
            ("Cold Chain Logistics", "Cold Chain Management for Agricultural & Seafood Products", "FAO / Cần Thơ Agri Hub", "https://fao.org", 1),
            ("ERP / SAP", "SAP S/4HANA Logistics & Supply Chain Fundamentals", "openSAP", "https://open.sap.com", 1),
            ("Financial Statements", "Đọc Hiểu & Phân Tích Báo Cáo Tài Chính Chuyên Sâu", "Viện Quản Trị PACE", "https://pace.edu.vn", 1),
            ("Tax Compliance", "Chính Sách Thuế & Quyết Toán Thuế Doanh Nghiệp 2026", "Hội Kế Toán Cần Thơ", "https://vcaa.edu.vn", 1),
            ("Accounting Software (MISA)", "Thực Hành Kế Toán Doanh Nghiệp Trên Phần Mềm MISA SME", "MISA Academy", "https://misa.vn", 1),
            ("Communication", "Kỹ Năng Giao Tiếp & Thuyết Phục Đỉnh Cao", "Viện Quản Trị PACE", "https://pace.edu.vn", 1),
            ("Problem Solving", "Creative Problem Solving and Decision Making", "Coursera", "https://coursera.org", 1),
            ("Teamwork", "High Performance Collaboration: Leadership, Teamwork", "Coursera × Northwestern", "https://coursera.org", 2),
        ]

        for sk_name, c_name, plat, url, prio in courses_data:
            if sk_name in skill_id_map:
                cursor.execute(
                    """INSERT INTO course_recommendations (skill_id, course_name, platform, url, priority)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (skill_id_map[sk_name], c_name, plat, url, prio)
                )

        conn.commit()
        print(f"   ✓ Đã tạo {len(courses_data)} khóa học gợi ý.")

        # In tổng kết
        cursor.execute("SELECT count(*) FROM job_postings;")
        total_j = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM survey_responses;")
        total_s = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM skill_catalog;")
        total_sk = cursor.fetchone()[0]
        cursor.execute("SELECT avg(gap_pct) FROM skill_catalog;")
        avg_gap = round(cursor.fetchone()[0] or 0, 1)

        print("\n" + "="*50)
        print("🎉 HOÀN TẤT NẠP DỮ LIỆU SẠCH VÀO DATABASE:")
        print(f"   - Tổng tin tuyển dụng (Job Postings): {total_j}")
        print(f"   - Tổng khảo sát sinh viên (CVs):      {total_s}")
        print(f"   - Tổng kỹ năng chuẩn hóa:             {total_sk}")
        print(f"   - Khoảng cách kỹ năng trung bình:     {avg_gap}%")
        print("="*50)

    except Exception as e:
        conn.rollback()
        print("❌ Lỗi khi nạp dữ liệu:", e)
        raise e
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
