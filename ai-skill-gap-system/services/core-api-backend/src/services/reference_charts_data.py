"""
Reference Charts & Document Dataset Module – Skill Lens Lab
Trích xuất toàn diện 100% dữ liệu từ tài liệu tham khảo 'So_Lieu_Bieu_do.docx' và các biểu đồ hệ thống.
Bao gồm:
- Nhóm A: Dashboard tổng quan (Top 5 kỹ năng thiếu hụt, Phân bổ ngành nghề, Chuyển dịch 2023-2027, So sánh 2025 vs 2026, Kỹ năng mềm, Xu hướng theo quý)
- Nhóm B: Dữ liệu ngành nghề toàn quốc (5 ngành: IT, Du lịch, Logistics, Kinh tế, Nông nghiệp CNC)
- Nhóm C: Dữ liệu theo khu vực (Cần Thơ, TP.HCM, Hà Nội)
- Nhóm D: Thông tin chức năng hệ thống (Chẩn đoán & Lộ trình, Phân tích CV bằng AI)

Mỗi bản ghi tuân thủ chuẩn:
source_id, dataset_id, chart_id, industry, region, period, period_type, skill_id, skill_name,
demand_pct, supply_pct, gap_pp, trend_pct, sample_size, validation_status
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# ═════════════════════════════════════════════════════════════════════
# 1. NHÓM A – DASHBOARD TỔNG QUAN
# ═════════════════════════════════════════════════════════════════════

# Bảng A1: Top 5 Kỹ năng thiếu hụt tổng quan (Bảng số liệu chi tiết)
OVERVIEW_TOP5_SKILLS = [
    {
        "rank": 1,
        "skill": "Python (Python AI/Backend)",
        "clean_name": "Python",
        "demand": 89.4,
        "supply": 51.2,
        "gap": 38.2,
        "note": "Kỹ năng có nhu cầu tuyển dụng cao nhất: Python (89.4%)"
    },
    {
        "rank": 2,
        "skill": "Docker & Cloud DevOps",
        "clean_name": "Docker & Cloud DevOps",
        "demand": 84.6,
        "supply": 47.8,
        "gap": 36.8,
        "note": ""
    },
    {
        "rank": 3,
        "skill": "Tiếng Anh chuyên ngành",
        "clean_name": "Tiếng Anh chuyên ngành",
        "demand": 82.1,
        "supply": 39.5,
        "gap": 42.6,
        "note": "Kỹ năng có khoảng cách thiếu hụt lớn nhất: Tiếng Anh chuyên ngành (thiếu hụt 42.6% / 42.6 điểm %)"
    },
    {
        "rank": 4,
        "skill": "Giải quyết vấn đề",
        "clean_name": "Giải quyết vấn đề",
        "demand": 78.5,
        "supply": 56.4,
        "gap": 22.1,
        "note": ""
    },
    {
        "rank": 5,
        "skill": "Cybersecurity & Mạng",
        "clean_name": "Cybersecurity & Mạng",
        "demand": 73.2,
        "supply": 34.9,
        "gap": 38.3,
        "note": ""
    }
]

# Bảng A2: Phân bổ ngành nghề (Tỷ lệ tin tuyển dụng theo ngành năm 2026)
INDUSTRY_DISTRIBUTION_2026 = {
    "IT": {
        "name": "IT & Công nghệ",
        "color": "Xanh lam ngọc",
        "share_pct": 38.5,
        "postings_1000": 385,
        "postings_3000": 1150,
        "note": "385 tin (hoặc 1.150 tin / mẫu 3.000)"
    },
    "Logistics": {
        "name": "Logistics & XNK",
        "color": "Cam vàng",
        "share_pct": 24.1,
        "postings_1000": 241,
        "postings_3000": 720,
        "note": "241 tin (hoặc 720 tin / mẫu 3.000)"
    },
    "Du lịch": {
        "name": "Du lịch & Khách sạn",
        "color": "Xanh lá cây",
        "share_pct": 21.8,
        "postings_1000": 218,
        "postings_3000": 680,
        "note": "218 tin (hoặc 680 tin / mẫu 3.000)"
    },
    "Kinh tế": {
        "name": "Kinh tế & Tài chính",
        "color": "Đỏ",
        "share_pct": 15.6,
        "postings_1000": 156,
        "postings_3000": 450,
        "note": "156 tin (hoặc 450 tin / mẫu 3.000)"
    },
    "Nông nghiệp": {
        "name": "Nông nghiệp CNC",
        "color": "Tím",
        "share_pct": 0.0,
        "postings_1000": 0,
        "postings_3000": 0,
        "note": "0 tin (hiển thị ở chú thích, chưa phát sinh mẫu trong kỳ này trên biểu đồ tròn phân bổ)"
    }
}

# Bảng A3: Đường đi chuyển dịch nhu cầu việc làm (2023 – 2027)
# Số lượng tin tuyển dụng theo từng ngành qua các mốc thời gian
INDUSTRY_TREND_2023_2027 = {
    "IT": {
        "name": "IT & Công nghệ",
        "years": {2023: 180, 2024: 230, 2025: 285, 2026: 385, 2027: 460},
        "forecast_2027": 460,
        "trend_summary": "Tăng trưởng bứt phá (+155.6% từ 2023 đến 2027)"
    },
    "Logistics": {
        "name": "Logistics & XNK",
        "years": {2023: 140, 2024: 165, 2025: 190, 2026: 241, 2027: 290},
        "forecast_2027": 290,
        "trend_summary": "Tăng trưởng liên tục (+107.1% từ 2023 đến 2027)"
    },
    "Du lịch": {
        "name": "Du lịch & Khách sạn",
        "years": {2023: 150, 2024: 180, 2025: 210, 2026: 218, 2027: 225},
        "forecast_2027": 225,
        "trend_summary": "Tăng đều rồi đi ngang (+50.0% từ 2023 đến 2027)"
    },
    "Kinh tế": {
        "name": "Kinh tế & Tài chính",
        "years": {2023: 310, 2024: 290, 2025: 270, 2026: 156, 2027: 115},
        "forecast_2027": 115,
        "trend_summary": "Thu hẹp mạnh do tự động hóa (-62.9% từ 2023 đến 2027)"
    },
    "Nông nghiệp": {
        "name": "Nông nghiệp CNC",
        "years": {2023: 25, 2024: 35, 2025: 45, 2026: 78, 2027: 110},
        "forecast_2027": 110,
        "trend_summary": "Tốc độ tăng cao nhất (+340.0% từ 2023 đến 2027)"
    }
}

# Bảng A4: So sánh cơ cấu tỷ trọng (2025 vs 2026)
INDUSTRY_SHARE_COMPARE_2025_2026 = {
    "IT": {
        "name": "IT & Công nghệ",
        "share_2025": 28.5,
        "postings_2025": 285,
        "share_2026": 38.5,
        "postings_2026": 385,
        "diff_share_pp": 10.0,
        "growth_rate_pct": 35.1,
        "evaluation": "Dịch chuyển trọng tâm lớn nhất (tăng 100 tin, +35.1%, thị phần tăng +10.0 điểm %)"
    },
    "Logistics": {
        "name": "Logistics & XNK",
        "share_2025": 19.0,
        "postings_2025": 190,
        "share_2026": 24.1,
        "postings_2026": 241,
        "diff_share_pp": 5.1,
        "growth_rate_pct": 26.8,
        "evaluation": "Tăng trưởng mạnh mẽ theo hạ tầng (+51 tin, +26.8%, thị phần tăng +5.1 điểm %)"
    },
    "Du lịch": {
        "name": "Du lịch & Khách sạn",
        "share_2025": 21.0,
        "postings_2025": 210,
        "share_2026": 21.8,
        "postings_2026": 218,
        "diff_share_pp": 0.8,
        "growth_rate_pct": 3.8,
        "evaluation": "Ổn định & chuẩn hóa chất lượng (+8 tin, +3.8%, thị phần tăng +0.8 điểm %)"
    },
    "Kinh tế": {
        "name": "Kinh tế & Tài chính",
        "share_2025": 27.0,
        "postings_2025": 270,
        "share_2026": 15.6,
        "postings_2026": 156,
        "diff_share_pp": -11.4,
        "growth_rate_pct": -42.2,
        "evaluation": "Sụt giảm mạnh do tự động hóa/AI (giảm 114 tin, -42.2%, thị phần giảm -11.4 điểm %)"
    },
    "Nông nghiệp": {
        "name": "Nông nghiệp CNC",
        "share_2025": 4.5,
        "postings_2025": 45,
        "share_2026": 7.8,
        "postings_2026": 78,
        "diff_share_pp": 3.3,
        "growth_rate_pct": 73.3,
        "evaluation": "Tăng tốc bứt phá công nghệ cao (+33 tin, +73.3%, thị phần tăng +3.3 điểm %)"
    }
}

# Bảng A5: Top kỹ năng mềm thiếu hụt
OVERVIEW_SOFT_SKILLS = [
    {
        "rank": 1,
        "skill": "Giao tiếp",
        "industry_focus": "Du lịch & Dịch vụ",
        "demand": 88.4,
        "supply": 52.1,
        "gap": 36.3
    },
    {
        "rank": 2,
        "skill": "Giải quyết vấn đề",
        "industry_focus": "CNTT & Kỹ thuật",
        "demand": 82.6,
        "supply": 48.3,
        "gap": 34.3
    },
    {
        "rank": 3,
        "skill": "Tiếng Anh",
        "industry_focus": "IT & Logistics",
        "demand": 79.8,
        "supply": 39.2,
        "gap": 40.6
    },
    {
        "rank": 4,
        "skill": "Làm việc nhóm",
        "industry_focus": "Sản xuất & Đa ngành",
        "demand": 76.5,
        "supply": 55.8,
        "gap": 20.7
    },
    {
        "rank": 5,
        "skill": "Tư duy phản biện",
        "industry_focus": "Fintech & AI",
        "demand": 71.3,
        "supply": 34.6,
        "gap": 36.7
    }
]

# Bảng A6: Xu hướng biến động theo quý (2025 – 2026) – Quỹ đạo biến động Gap (%) qua 7 quý
QUARTERLY_GAP_TREND = {
    "Tiếng Anh": {
        "skill": "Tiếng Anh (IT & Logistics)",
        "quarters": {
            "Q1/2025": 28.0, "Q2/2025": 31.2, "Q3/2025": 33.5, "Q4/2025": 36.0,
            "Q1/2026": 38.2, "Q2/2026": 39.5, "Q3/2026": 40.6
        },
        "gap_increase": 12.6,
        "note": "+12.6 điểm % (Khoảng cách lớn nhất)"
    },
    "Tư duy phản biện": {
        "skill": "Tư duy phản biện (Fintech & AI)",
        "quarters": {
            "Q1/2025": 18.5, "Q2/2025": 22.0, "Q3/2025": 26.1, "Q4/2025": 29.8,
            "Q1/2026": 33.0, "Q2/2026": 35.2, "Q3/2026": 36.7
        },
        "gap_increase": 18.2,
        "note": "+18.2 điểm % (Tốc độ thiếu hụt tăng nhanh nhất)"
    },
    "Giao tiếp": {
        "skill": "Giao tiếp (Du lịch & Dịch vụ)",
        "quarters": {
            "Q1/2025": 30.5, "Q2/2025": 31.8, "Q3/2025": 32.9, "Q4/2025": 34.0,
            "Q1/2026": 35.1, "Q2/2026": 35.8, "Q3/2026": 36.3
        },
        "gap_increase": 5.8,
        "note": "+5.8 điểm % (Duy trì mức thiếu hụt cao)"
    },
    "Giải quyết vấn đề": {
        "skill": "Giải quyết vấn đề (CNTT & Kỹ thuật)",
        "quarters": {
            "Q1/2025": 26.0, "Q2/2025": 27.8, "Q3/2025": 29.5, "Q4/2025": 31.0,
            "Q1/2026": 32.8, "Q2/2026": 33.6, "Q3/2026": 34.3
        },
        "gap_increase": 8.3,
        "note": "+8.3 điểm % (Gia tăng đều đặn)"
    },
    "Thích nghi": {
        "skill": "Thích nghi (Tech & GenAI)",
        "quarters": {
            "Q1/2025": 8.0, "Q2/2025": 9.5, "Q3/2025": 11.0, "Q4/2025": 12.0,
            "Q1/2026": 13.0, "Q2/2026": 13.8, "Q3/2026": 14.2
        },
        "gap_increase": 6.2,
        "note": "Tăng từ 8.0% lên 14.2%"
    }
}


# ═════════════════════════════════════════════════════════════════════
# 2. NHÓM B – DỮ LIỆU NGÀNH NGHỀ TRÊN PHẠM VI CẢ NƯỚC (TOÀN QUỐC)
# ═════════════════════════════════════════════════════════════════════

NATIONAL_INDUSTRY_DATA = {
    "IT": {
        "name": "IT & Công nghệ",
        "job_postings": 1150,
        "salary_range": "16 – 38 triệu đồng/tháng",
        "top_missing_skill": "Python AI & Cloud Architecture (Gap 58.7% / Gap cao nhất ngành)",
        "skills": [
            {"rank": 1, "skill": "Python AI & Backend", "type": "Chuyên môn", "group": "Lập trình", "demand": 91.2, "supply": 32.5, "gap": 58.7, "trend": "+45%"},
            {"rank": 2, "skill": "Cloud (AWS/GCP/Azure)", "type": "Chuyên môn", "group": "Infrastructure", "demand": 72.8, "supply": 28.6, "gap": 44.2, "trend": "+41%"},
            {"rank": 3, "skill": "Docker & DevOps (SRE)", "type": "Chuyên môn", "group": "Infrastructure", "demand": 74.0, "supply": 30.0, "gap": 44.0, "trend": "+38%"},
            {"rank": 4, "skill": "Cybersecurity & An toàn thông tin", "type": "Chuyên môn", "group": "Bảo mật", "demand": 68.6, "supply": 25.3, "gap": 43.3, "trend": "+52%"},
            {"rank": 5, "skill": "Kubernetes & Microservices", "type": "Chuyên môn", "group": "Infrastructure", "demand": 64.1, "supply": 22.3, "gap": 41.8, "trend": "+47%"},
            {"rank": 6, "skill": "ReactJS & Fullstack Web", "type": "Chuyên môn", "group": "Frontend", "demand": 78.7, "supply": 44.3, "gap": 34.4, "trend": "+24%"},
            {"rank": 7, "skill": "Tiếng Anh chuyên ngành Tech", "type": "Kỹ năng mềm", "group": "Ngoại ngữ / Mềm", "demand": 74.4, "supply": 48.1, "gap": 26.3, "trend": "+12%"},
            {"rank": 8, "skill": "Giải quyết vấn đề", "type": "Kỹ năng mềm", "group": "Kỹ năng mềm", "demand": 68.2, "supply": 48.9, "gap": 19.3, "trend": "+10%"},
            {"rank": 9, "skill": "SQL & Cơ sở dữ liệu", "type": "Chuyên môn", "group": "Database", "demand": 62.7, "supply": 45.2, "gap": 17.5, "trend": "+8%"},
            {"rank": 10, "skill": "Làm việc nhóm & Agile", "type": "Kỹ năng mềm", "group": "Kỹ năng mềm", "demand": 65.0, "supply": 52.4, "gap": 12.6, "trend": "+6%"}
        ]
    },
    "Du lịch": {
        "name": "Du lịch & Khách sạn",
        "job_postings": 680,
        "job_postings_ct": 218,
        "salary_range": "9 – 20 triệu đồng/tháng",
        "top_missing_skill": "Tiếng Anh & Đa ngôn ngữ du lịch (Gap 48.2% / Gap cao nhất ngành)",
        "skills": [
            {"rank": 1, "skill": "Tiếng Anh Du lịch & Dịch vụ", "type": "Kỹ năng mềm", "group": "Ngoại ngữ", "demand": 90.4, "supply": 42.2, "gap": 48.2, "trend": "+25%"},
            {"rank": 2, "skill": "Revenue Management & OTA", "type": "Chuyên môn", "group": "Quản lý doanh thu", "demand": 69.7, "supply": 30.4, "gap": 39.3, "trend": "+35%"},
            {"rank": 3, "skill": "Hướng dẫn viên du lịch", "type": "Chuyên môn", "group": "Nghiệp vụ tour", "demand": 81.3, "supply": 44.6, "gap": 36.7, "trend": "+12%"},
            {"rank": 4, "skill": "Quản lý khách sạn & PMS", "type": "Chuyên môn", "group": "Vận hành PMS", "demand": 75.5, "supply": 40.8, "gap": 34.7, "trend": "+18%"},
            {"rank": 5, "skill": "Chăm sóc khách hàng (CX)", "type": "Kỹ năng mềm", "group": "Dịch vụ khách hàng", "demand": 72.2, "supply": 54.4, "gap": 17.8, "trend": "+8%"}
        ],
        "local_specialties": {
            "Cần Thơ & ĐBSCL": "Hướng dẫn viên miệt vườn & sinh thái thiếu 43.0%, Tiếng Trung du lịch thiếu 44.0%"
        }
    },
    "Logistics": {
        "name": "Logistics & Xuất nhập khẩu (XNK)",
        "job_postings": 720,
        "job_postings_ct": 241,
        "salary_range": "11 – 24 triệu đồng/tháng",
        "top_missing_skill": "Quản lý chuỗi cung ứng SCM (Gap 57.2% / Gap cao nhất ngành)",
        "skills": [
            {"rank": 1, "skill": "Quản lý chuỗi cung ứng SCM", "type": "Chuyên môn", "group": "Logistics", "demand": 87.6, "supply": 30.4, "gap": 57.2, "trend": "+35%"},
            {"rank": 2, "skill": "Vận tải biển & Forwarding", "type": "Chuyên môn", "group": "Vận tải quốc tế", "demand": 84.0, "supply": 34.0, "gap": 50.0, "trend": "+28%"},
            {"rank": 3, "skill": "Quản trị kho vận WMS / ERP", "type": "Chuyên môn", "group": "Quản lý kho bãi", "demand": 74.8, "supply": 34.2, "gap": 40.6, "trend": "+30%"},
            {"rank": 4, "skill": "Khai báo hải quan & Incoterms", "type": "Chuyên môn", "group": "Nghiệp vụ XNK", "demand": 81.2, "supply": 41.8, "gap": 39.4, "trend": "+16%"},
            {"rank": 5, "skill": "Tiếng Anh thương mại", "type": "Kỹ năng mềm", "group": "Ngoại ngữ đàm phán", "demand": 80.3, "supply": 45.6, "gap": 34.7, "trend": "+16%"}
        ],
        "local_specialties": {
            "Cần Thơ & ĐBSCL": "Chuỗi cung ứng lạnh nông thủy sản (Cold Chain) thiếu hụt lên đến 58.5% do nhu cầu xuất khẩu gạo và trái cây"
        }
    },
    "Kinh tế": {
        "name": "Kinh tế & Tài chính",
        "job_postings": 450,
        "job_postings_ct": 156,
        "salary_range": "11 – 26 triệu đồng/tháng",
        "top_missing_skill": "Phân tích dữ liệu & Digital Marketing (Gap 50.4% / Gap cao nhất ngành)",
        "skills": [
            {"rank": 1, "skill": "Digital Marketing & Performance", "type": "Chuyên môn", "group": "Marketing số", "demand": 86.6, "supply": 36.2, "gap": 50.4, "trend": "+42%"},
            {"rank": 2, "skill": "Phân tích tài chính & BI", "type": "Chuyên môn", "group": "Tài chính doanh nghiệp", "demand": 82.3, "supply": 34.6, "gap": 47.7, "trend": "+36%"},
            {"rank": 3, "skill": "Excel nâng cao & Power BI", "type": "Chuyên môn", "group": "Công cụ phân tích", "demand": 78.5, "supply": 48.4, "gap": 30.1, "trend": "+15%"},
            {"rank": 4, "skill": "Kế toán MISA / ERP", "type": "Chuyên môn", "group": "Kế toán quản trị", "demand": 74.4, "supply": 50.8, "gap": 23.6, "trend": "+10%"}
        ],
        "trend_note": "Các vị trí kế toán/nhập liệu sơ cấp đang giảm mạnh do tự động hóa/AI, nhưng các kỹ năng kết hợp công nghệ số như E-Commerce & Digital Marketing tăng trưởng vượt bậc."
    },
    "Nông nghiệp": {
        "name": "Nông nghiệp Công nghệ cao",
        "job_postings": 320,
        "job_postings_ct": 180,
        "salary_range": "8 – 18 triệu đồng/tháng",
        "top_missing_skill": "Công nghệ nông nghiệp AgTech (Gap 60.2% / Gap cao nhất ngành)",
        "skills": [
            {"rank": 1, "skill": "Công nghệ nông nghiệp AgTech", "type": "Chuyên môn", "group": "Công nghệ số nông nghiệp", "demand": 82.4, "supply": 22.2, "gap": 60.2, "trend": "+65%"},
            {"rank": 2, "skill": "Drone & IoT trong nông nghiệp", "type": "Chuyên môn", "group": "Thiết bị thông minh", "demand": 72.8, "supply": 18.4, "gap": 54.4, "trend": "+70%"},
            {"rank": 3, "skill": "Tiêu chuẩn VietGAP / GlobalGAP", "type": "Chuyên môn", "group": "Nghiệp vụ tiêu chuẩn", "demand": 78.2, "supply": 36.0, "gap": 42.2, "trend": "+30%"},
            {"rank": 4, "skill": "Chế biến & Bảo quản sau thu hoạch", "type": "Chuyên môn", "group": "Kỹ thuật bảo quản", "demand": 68.4, "supply": 32.6, "gap": 35.8, "trend": "+22%"}
        ]
    }
}


# ═════════════════════════════════════════════════════════════════════
# 3. NHÓM C – DỮ LIỆU THEO KHU VỰC (CẦN THƠ, TP.HCM, HÀ NỘI)
# ═════════════════════════════════════════════════════════════════════

REGIONAL_DATA = {
    "CT": {
        "region_name": "Cần Thơ & Đồng bằng sông Cửu Long",
        "industries": {
            "IT": {
                "name": "IT & Công nghệ",
                "job_postings": 285,
                "salary_range": "12 – 28 triệu đồng/tháng",
                "top_missing_skill": "IoT & Cảm biến giám sát độ mặn/phèn (Gap 64.0% / Gap cao nhất)",
                "skills": [
                    {"rank": 1, "skill": "IoT & Cảm biến giám sát độ mặn/phèn", "group": "IoT / Phần cứng", "type": "Chuyên môn", "demand": 85.0, "supply": 21.0, "gap": 64.0, "trend": "+65%"},
                    {"rank": 2, "skill": "Machine Learning (AI)", "group": "AI / Dữ liệu", "type": "Chuyên môn", "demand": 76.0, "supply": 20.0, "gap": 56.0, "trend": "+50%"},
                    {"rank": 3, "skill": "Python & Phân tích dữ liệu", "group": "Lập trình", "type": "Chuyên môn", "demand": 88.0, "supply": 32.5, "gap": 55.5, "trend": "+45%"},
                    {"rank": 4, "skill": "Docker & DevOps", "group": "Infrastructure", "type": "Chuyên môn", "demand": 62.4, "supply": 22.1, "gap": 40.3, "trend": "+38%"},
                    {"rank": 5, "skill": "ReactJS & Mobile App", "group": "Frontend", "type": "Chuyên môn", "demand": 72.0, "supply": 38.0, "gap": 34.0, "trend": "+25%"},
                    {"rank": 6, "skill": "Phần mềm ERP nông sản", "group": "Phần mềm", "type": "Chuyên môn", "demand": 68.0, "supply": 34.0, "gap": 34.0, "trend": "+30%"},
                    {"rank": 7, "skill": "Bảo mật mạng IoT", "group": "Bảo mật", "type": "Chuyên môn", "demand": 54.0, "supply": 22.0, "gap": 32.0, "trend": "+28%"},
                    {"rank": 8, "skill": "Lập trình vi điều khiển (Embedded)", "group": "Phần cứng", "type": "Chuyên môn", "demand": 50.0, "supply": 24.0, "gap": 26.0, "trend": "+35%"},
                    {"rank": 9, "skill": "Tiếng Anh chuyên ngành Tech", "group": "Ngoại ngữ", "type": "Kỹ năng mềm", "demand": 60.4, "supply": 42.1, "gap": 18.3, "trend": "+9%"},
                    {"rank": 10, "skill": "SQL & Cơ sở dữ liệu", "group": "Database", "type": "Chuyên môn", "demand": 58.7, "supply": 44.6, "gap": 14.1, "trend": "+6%"}
                ]
            },
            "Du lịch": {
                "name": "Du lịch & Khách sạn",
                "job_postings": 218,
                "salary_range": "8 – 18 triệu đồng/tháng",
                "top_missing_skill": "Tiếng Anh du lịch sinh thái (Gap 54.2% / Gap cao nhất)",
                "skills": [
                    {"rank": 1, "skill": "Tiếng Anh du lịch sinh thái", "group": "Ngoại ngữ", "type": "Kỹ năng mềm", "demand": 92.4, "supply": 38.2, "gap": 54.2, "trend": "+20%"},
                    {"rank": 2, "skill": "Tiếng Trung du lịch", "group": "Ngoại ngữ", "type": "Kỹ năng mềm", "demand": 68.0, "supply": 24.0, "gap": 44.0, "trend": "+35%"},
                    {"rank": 3, "skill": "Hướng dẫn viên miệt vườn & sông nước", "group": "Nghiệp vụ", "type": "Chuyên môn", "demand": 85.0, "supply": 42.0, "gap": 43.0, "trend": "+15%"},
                    {"rank": 4, "skill": "Quản lý Ecolodge & Homestay", "group": "Nghiệp vụ", "type": "Chuyên môn", "demand": 74.0, "supply": 36.0, "gap": 38.0, "trend": "+22%"},
                    {"rank": 5, "skill": "Digital Marketing tour miền Tây", "group": "Marketing", "type": "Chuyên môn", "demand": 62.0, "supply": 34.0, "gap": 28.0, "trend": "+28%"},
                    {"rank": 6, "skill": "Xử lý sự cố lộ trình đường sông", "group": "Mềm", "type": "Kỹ năng mềm", "demand": 65.2, "supply": 38.1, "gap": 27.1, "trend": "+10%"},
                    {"rank": 7, "skill": "Quản trị F&B ẩm thực sông nước", "group": "Nghiệp vụ", "type": "Chuyên môn", "demand": 60.0, "supply": 41.0, "gap": 19.0, "trend": "+12%"},
                    {"rank": 8, "skill": "Chăm sóc khách quốc tế", "group": "Mềm", "type": "Kỹ năng mềm", "demand": 68.2, "supply": 52.4, "gap": 15.8, "trend": "+6%"}
                ]
            },
            "Logistics": {
                "name": "Logistics & XNK",
                "job_postings": 241,
                "salary_range": "10 – 22 triệu đồng/tháng",
                "top_missing_skill": "Chuỗi cung ứng lạnh nông sản (Gap 65.0% / Gap cao nhất)",
                "skills": [
                    {"rank": 1, "skill": "Chuỗi cung ứng lạnh (Cold Chain nông sản)", "group": "Logistics", "type": "Chuyên môn", "demand": 89.0, "supply": 24.0, "gap": 65.0, "trend": "+45%"},
                    {"rank": 2, "skill": "Khai báo hải quan nông thủy sản", "group": "Nghiệp vụ", "type": "Chuyên môn", "demand": 82.0, "supply": 35.0, "gap": 47.0, "trend": "+25%"},
                    {"rank": 3, "skill": "Quản lý kho bảo quản sau thu hoạch", "group": "Kho vận", "type": "Chuyên môn", "demand": 78.0, "supply": 36.0, "gap": 42.0, "trend": "+30%"},
                    {"rank": 4, "skill": "Vận tải thủy nội địa sà lan Mekong", "group": "Vận tải", "type": "Chuyên môn", "demand": 74.0, "supply": 38.0, "gap": 36.0, "trend": "+20%"},
                    {"rank": 5, "skill": "Tiếng Anh XNK thương mại", "group": "Ngoại ngữ", "type": "Kỹ năng mềm", "demand": 76.0, "supply": 40.0, "gap": 36.0, "trend": "+18%"},
                    {"rank": 6, "skill": "Phần mềm WMS / ERP kho gạo & thủy sản", "group": "Phần mềm", "type": "Chuyên môn", "demand": 64.0, "supply": 32.0, "gap": 32.0, "trend": "+28%"},
                    {"rank": 7, "skill": "Incoterms & Hợp đồng xuất khẩu gạo", "group": "Nghiệp vụ", "type": "Chuyên môn", "demand": 69.0, "supply": 42.0, "gap": 27.0, "trend": "+14%"},
                    {"rank": 8, "skill": "Điều độ luồng vận tải đa phương thức", "group": "Vận hành", "type": "Chuyên môn", "demand": 61.0, "supply": 39.0, "gap": 22.0, "trend": "+10%"}
                ]
            },
            "Kinh tế": {
                "name": "Kinh tế & Tài chính",
                "job_postings": 156,
                "salary_range": "8 – 20 triệu đồng/tháng",
                "top_missing_skill": "Thương mại điện tử nông sản (Gap 57.0% / Gap cao nhất)",
                "skills": [
                    {"rank": 1, "skill": "TMĐT & Livestream bán nông sản", "group": "E-Commerce", "type": "Chuyên môn", "demand": 85.0, "supply": 28.0, "gap": 57.0, "trend": "+55%"},
                    {"rank": 2, "skill": "Digital Marketing & SEO địa phương", "group": "Marketing", "type": "Chuyên môn", "demand": 78.0, "supply": 32.0, "gap": 46.0, "trend": "+40%"},
                    {"rank": 3, "skill": "Phân tích dữ liệu kinh doanh SME", "group": "Phân tích", "type": "Chuyên môn", "demand": 72.0, "supply": 34.0, "gap": 38.0, "trend": "+35%"},
                    {"rank": 4, "skill": "Quản trị dòng tiền nông hộ & HTX", "group": "Tài chính", "type": "Chuyên môn", "demand": 68.0, "supply": 35.0, "gap": 33.0, "trend": "+20%"},
                    {"rank": 5, "skill": "Kế toán thuế & phần mềm MISA SME", "group": "Kế toán", "type": "Chuyên môn", "demand": 74.0, "supply": 46.0, "gap": 28.0, "trend": "+10%"},
                    {"rank": 6, "skill": "Kỹ năng đàm phán hợp đồng thu mua", "group": "Mềm", "type": "Kỹ năng mềm", "demand": 66.0, "supply": 40.0, "gap": 26.0, "trend": "+12%"},
                    {"rank": 7, "skill": "Bán hàng B2B kênh phân phối MT/GT", "group": "Kinh doanh", "type": "Chuyên môn", "demand": 62.0, "supply": 42.0, "gap": 20.0, "trend": "+8%"}
                ]
            }
        }
    },
    "HCM": {
        "region_name": "TP. Hồ Chí Minh",
        "industries": {
            "IT": {
                "name": "IT & Công nghệ",
                "job_postings": 450,
                "salary_range": "20 – 50 triệu đồng/tháng",
                "top_missing_skill": "Cloud Architecture (AWS/GCP/Azure) (Gap 59.7% / Gap cao nhất)",
                "skills": [
                    {"rank": 1, "skill": "Cloud Architecture (AWS/GCP/Azure)", "group": "Infrastructure", "type": "Chuyên môn", "demand": 96.2, "supply": 36.5, "gap": 59.7, "trend": "+58%"},
                    {"rank": 2, "skill": "Docker & Kubernetes (SRE)", "group": "DevOps", "type": "Chuyên môn", "demand": 92.4, "supply": 38.6, "gap": 53.8, "trend": "+50%"},
                    {"rank": 3, "skill": "Golang & Fintech Backend", "group": "Backend", "type": "Chuyên môn", "demand": 88.5, "supply": 35.8, "gap": 52.7, "trend": "+46%"},
                    {"rank": 4, "skill": "Data Engineer (Kafka/Spark/DWH)", "group": "Dữ liệu", "type": "Chuyên môn", "demand": 78.5, "supply": 36.0, "gap": 42.5, "trend": "+44%"},
                    {"rank": 5, "skill": "Thanh toán số & Transaction Security", "group": "Bảo mật", "type": "Chuyên môn", "demand": 82.0, "supply": 39.5, "gap": 42.5, "trend": "+38%"},
                    {"rank": 6, "skill": "ReactJS & Next.js Fullstack", "group": "Frontend", "type": "Chuyên môn", "demand": 84.2, "supply": 48.0, "gap": 36.2, "trend": "+25%"},
                    {"rank": 7, "skill": "Tiếng Anh thương mại Quốc tế", "group": "Ngoại ngữ", "type": "Kỹ năng mềm", "demand": 88.0, "supply": 52.0, "gap": 36.0, "trend": "+18%"},
                    {"rank": 8, "skill": "Microservices High-load", "group": "Kiến trúc", "type": "Chuyên môn", "demand": 75.0, "supply": 41.2, "gap": 33.8, "trend": "+32%"},
                    {"rank": 9, "skill": "Terraform & IaC CI/CD", "group": "DevOps", "type": "Chuyên môn", "demand": 71.0, "supply": 38.0, "gap": 33.0, "trend": "+35%"},
                    {"rank": 10, "skill": "SQL & NoSQL (Redis/MongoDB)", "group": "Database", "type": "Chuyên môn", "demand": 70.0, "supply": 54.0, "gap": 16.0, "trend": "+10%"}
                ]
            },
            "Du lịch": {
                "name": "Du lịch & Khách sạn",
                "job_postings": 240,
                "salary_range": "12 – 25 triệu đồng/tháng",
                "top_missing_skill": "Revenue Management & OTA Booking (Gap 57.0% / Gap cao nhất)",
                "skills": [
                    {"rank": 1, "skill": "Revenue Management & OTA Booking", "group": "Quản lý", "type": "Chuyên môn", "demand": 89.0, "supply": 32.0, "gap": 57.0, "trend": "+42%"},
                    {"rank": 2, "skill": "Tiếng Anh giao tiếp lưu loát", "group": "Ngoại ngữ", "type": "Kỹ năng mềm", "demand": 91.0, "supply": 45.0, "gap": 46.0, "trend": "+22%"},
                    {"rank": 3, "skill": "Quản lý chuỗi F&B cao cấp", "group": "Nghiệp vụ", "type": "Chuyên môn", "demand": 82.0, "supply": 40.0, "gap": 42.0, "trend": "+28%"},
                    {"rank": 4, "skill": "Quản trị khách sạn PMS Opera", "group": "Nghiệp vụ", "type": "Chuyên môn", "demand": 79.0, "supply": 42.0, "gap": 37.0, "trend": "+16%"},
                    {"rank": 5, "skill": "Digital Marketing tour quốc tế (Inbound)", "group": "Marketing", "type": "Chuyên môn", "demand": 75.0, "supply": 45.0, "gap": 30.0, "trend": "+24%"}
                ]
            },
            "Logistics": {
                "name": "Logistics & XNK",
                "job_postings": 290,
                "salary_range": "15 – 30 triệu đồng/tháng",
                "top_missing_skill": "Sea Freight Forwarding Quốc tế (Gap 58.0% / Gap cao nhất)",
                "skills": [
                    {"rank": 1, "skill": "Sea Freight Forwarding Quốc tế", "group": "Vận tải", "type": "Chuyên môn", "demand": 92.0, "supply": 34.0, "gap": 58.0, "trend": "+45%"},
                    {"rank": 2, "skill": "Incoterms 2020 & Hợp đồng vận tải QT", "group": "Nghiệp vụ", "type": "Chuyên môn", "demand": 86.0, "supply": 38.0, "gap": 48.0, "trend": "+20%"},
                    {"rank": 3, "skill": "Quản trị kho tự động WMS / Smart Warehouse", "group": "Kho vận", "type": "Chuyên môn", "demand": 81.0, "supply": 36.0, "gap": 45.0, "trend": "+35%"},
                    {"rank": 4, "skill": "Khai báo hải quan điện tử (Customs)", "group": "Nghiệp vụ", "type": "Chuyên môn", "demand": 84.0, "supply": 46.0, "gap": 38.0, "trend": "+18%"},
                    {"rank": 5, "skill": "Tiếng Anh Logistics thương mại quốc tế", "group": "Ngoại ngữ", "type": "Kỹ năng mềm", "demand": 85.0, "supply": 49.0, "gap": 36.0, "trend": "+15%"}
                ]
            },
            "Kinh tế": {
                "name": "Kinh tế & Tài chính",
                "job_postings": 210,
                "salary_range": "15 – 35 triệu đồng/tháng",
                "top_missing_skill": "Growth Marketing & Performance Ads (Gap 54.0% / Gap cao nhất)",
                "skills": [
                    {"rank": 1, "skill": "Growth Marketing & Performance Ads", "group": "Marketing", "type": "Chuyên môn", "demand": 90.0, "supply": 36.0, "gap": 54.0, "trend": "+50%"},
                    {"rank": 2, "skill": "Phân tích dữ liệu BI & SQL", "group": "Dữ liệu", "type": "Chuyên môn", "demand": 88.0, "supply": 38.0, "gap": 50.0, "trend": "+45%"},
                    {"rank": 3, "skill": "Tài chính doanh nghiệp & Quỹ đầu tư (VC/PE)", "group": "Tài chính", "type": "Chuyên môn", "demand": 82.0, "supply": 35.0, "gap": 47.0, "trend": "+35%"},
                    {"rank": 4, "skill": "Kế toán quản trị & ERP SAP/Oracle", "group": "Kế toán", "type": "Chuyên môn", "demand": 78.0, "supply": 42.0, "gap": 36.0, "trend": "+14%"},
                    {"rank": 5, "skill": "CRM & Tự động hóa bán hàng (HubSpot/Salesforce)", "group": "Marketing", "type": "Chuyên môn", "demand": 76.0, "supply": 44.0, "gap": 32.0, "trend": "+25%"}
                ]
            }
        }
    },
    "HN": {
        "region_name": "Hà Nội",
        "industries": {
            "IT": {
                "name": "IT & Công nghệ",
                "job_postings": 420,
                "salary_range": "18 – 45 triệu đồng/tháng",
                "top_missing_skill": "Python AI & LLM (Generative AI) (Gap 56.3% / Gap cao nhất)",
                "skills": [
                    {"rank": 1, "skill": "Python AI & LLM (Generative AI)", "group": "AI / Dữ liệu", "type": "Chuyên môn", "demand": 94.5, "supply": 38.2, "gap": 56.3, "trend": "+52%"},
                    {"rank": 2, "skill": "Cybersecurity & Giám sát SOC", "group": "Bảo mật", "type": "Chuyên môn", "demand": 89.2, "supply": 35.4, "gap": 53.8, "trend": "+48%"},
                    {"rank": 3, "skill": "Big Data (Hadoop / Spark)", "group": "Dữ liệu", "type": "Chuyên môn", "demand": 82.6, "supply": 32.1, "gap": 50.5, "trend": "+41%"},
                    {"rank": 4, "skill": "Machine Learning / PyTorch", "group": "AI / Dữ liệu", "type": "Chuyên môn", "demand": 85.0, "supply": 36.5, "gap": 48.5, "trend": "+45%"},
                    {"rank": 5, "skill": "Java Spring Boot Enterprise", "group": "Backend", "type": "Chuyên môn", "demand": 78.4, "supply": 46.2, "gap": 32.2, "trend": "+15%"},
                    {"rank": 6, "skill": "Cloud Architecture", "group": "Infrastructure", "type": "Chuyên môn", "demand": 72.5, "supply": 41.0, "gap": 31.5, "trend": "+28%"},
                    {"rank": 7, "skill": "Docker & DevOps", "group": "DevOps", "type": "Chuyên môn", "demand": 68.4, "supply": 42.1, "gap": 26.3, "trend": "+22%"},
                    {"rank": 8, "skill": "Tiếng Anh chuyên ngành Tech", "group": "Ngoại ngữ", "type": "Kỹ năng mềm", "demand": 75.0, "supply": 52.0, "gap": 23.0, "trend": "+12%"},
                    {"rank": 9, "skill": "SQL & Data Warehouse", "group": "Database", "type": "Chuyên môn", "demand": 64.2, "supply": 45.6, "gap": 18.6, "trend": "+10%"},
                    {"rank": 10, "skill": "Quản trị hệ thống Linux", "group": "Hạ tầng", "type": "Chuyên môn", "demand": 61.5, "supply": 44.8, "gap": 16.7, "trend": "+8%"}
                ]
            },
            "Du lịch": {
                "name": "Du lịch & Khách sạn",
                "job_postings": 195,
                "salary_range": "10 – 22 triệu đồng/tháng",
                "top_missing_skill": "Tiếng Trung & Hàn du lịch (Gap 54.0% / Gap cao nhất)",
                "skills": [
                    {"rank": 1, "skill": "Tiếng Trung & Hàn du lịch", "group": "Ngoại ngữ", "type": "Kỹ năng mềm", "demand": 88.0, "supply": 34.0, "gap": 54.0, "trend": "+38%"},
                    {"rank": 2, "skill": "Hướng dẫn viên di sản văn hóa", "group": "Nghiệp vụ", "type": "Chuyên môn", "demand": 82.0, "supply": 38.0, "gap": 44.0, "trend": "+18%"},
                    {"rank": 3, "skill": "Quản trị khách sạn hội nghị (MICE)", "group": "Nghiệp vụ", "type": "Chuyên môn", "demand": 76.0, "supply": 40.0, "gap": 36.0, "trend": "+20%"},
                    {"rank": 4, "skill": "Tiếng Anh du lịch quốc tế", "group": "Ngoại ngữ", "type": "Kỹ năng mềm", "demand": 84.0, "supply": 50.0, "gap": 34.0, "trend": "+15%"},
                    {"rank": 5, "skill": "Quản lý F&B ẩm thực miền Bắc", "group": "Nghiệp vụ", "type": "Chuyên môn", "demand": 68.0, "supply": 45.0, "gap": 23.0, "trend": "+8%"}
                ]
            },
            "Logistics": {
                "name": "Logistics & XNK",
                "job_postings": 230,
                "salary_range": "12 – 25 triệu đồng/tháng",
                "top_missing_skill": "Hải quan cửa khẩu VNACCS (Gap 51.0% / Gap cao nhất)",
                "skills": [
                    {"rank": 1, "skill": "Hải quan cửa khẩu VNACCS", "group": "Nghiệp vụ", "type": "Chuyên môn", "demand": 86.0, "supply": 35.0, "gap": 51.0, "trend": "+35%"},
                    {"rank": 2, "skill": "Chuỗi cung ứng KCN phụ trợ (Bắc Ninh, Thái Nguyên)", "group": "Logistics", "type": "Chuyên môn", "demand": 83.0, "supply": 36.0, "gap": 47.0, "trend": "+30%"},
                    {"rank": 3, "skill": "Vận tải liên vận biên giới Việt - Trung", "group": "Vận tải", "type": "Chuyên môn", "demand": 75.0, "supply": 38.0, "gap": 37.0, "trend": "+25%"},
                    {"rank": 4, "skill": "Tiếng Trung thương mại XNK", "group": "Ngoại ngữ", "type": "Kỹ năng mềm", "demand": 78.0, "supply": 42.0, "gap": 36.0, "trend": "+28%"},
                    {"rank": 5, "skill": "Phần mềm SAP Logistics", "group": "Phần mềm", "type": "Chuyên môn", "demand": 69.0, "supply": 35.0, "gap": 34.0, "trend": "+22%"}
                ]
            },
            "Kinh tế": {
                "name": "Kinh tế & Tài chính",
                "job_postings": 175,
                "salary_range": "12 – 28 triệu đồng/tháng",
                "top_missing_skill": "Phân tích tài chính & Thẩm định dự án (Gap 52.0% / Gap cao nhất)",
                "skills": [
                    {"rank": 1, "skill": "Phân tích tài chính & Thẩm định dự án", "group": "Tài chính", "type": "Chuyên môn", "demand": 88.0, "supply": 36.0, "gap": 52.0, "trend": "+35%"},
                    {"rank": 2, "skill": "Data Analyst (Power BI & Python)", "group": "Dữ liệu", "type": "Chuyên môn", "demand": 84.0, "supply": 35.0, "gap": 49.0, "trend": "+45%"},
                    {"rank": 3, "skill": "Kiểm toán & Thuế doanh nghiệp lớn", "group": "Kế toán", "type": "Chuyên môn", "demand": 79.0, "supply": 41.0, "gap": 38.0, "trend": "+15%"},
                    {"rank": 4, "skill": "Quản trị rủi ro tín dụng ngân hàng", "group": "Tài chính", "type": "Chuyên môn", "demand": 75.0, "supply": 40.0, "gap": 35.0, "trend": "+20%"},
                    {"rank": 5, "skill": "Kế toán phần mềm MISA / FAST", "group": "Kế toán", "type": "Chuyên môn", "demand": 72.0, "supply": 48.0, "gap": 24.0, "trend": "+8%"}
                ]
            }
        }
    }
}


# ═════════════════════════════════════════════════════════════════════
# 4. NHÓM D – THÔNG TIN CHỨC NĂNG HỆ THỐNG
# ═════════════════════════════════════════════════════════════════════

SYSTEM_FEATURES_INFO = {
    "diagnosis_pathway": {
        "title": "Chẩn đoán & Lộ trình (Hồ Sơ Năng Lực & Mục Tiêu Nghề Nghiệp)",
        "framework": "Chuẩn 20 Chức Vụ Cần Thơ & ĐBSCL",
        "sample_profiles": "500 hồ sơ sinh viên mẫu trong CSDL",
        "steps": [
            "Bước 1 - Mục tiêu ngành nghề: Chọn lĩnh vực (IT 20 chức vụ chuyên sâu, Logistics, Du lịch, Kinh tế...).",
            "Bước 2 - Chức vụ mục tiêu: Chọn vị trí cụ thể (VD: Software Engineer), hệ thống hiển thị bộ khung Tiêu chuẩn kỹ năng bắt buộc chuẩn Cần Thơ.",
            "Bước 3 - Tự đánh giá & Nạp hồ sơ mẫu: Tích chọn kỹ năng tự có hoặc chọn nhanh 1 trong 500 hồ sơ sinh viên mẫu.",
            "Đầu ra (Output): Bấm '🚀 AI CHẨN ĐOÁN & KÊ ĐƠN KHÓA HỌC' tính toán Gap, liệt kê kỹ năng khuyết thiếu và tự động gợi ý khóa học đối ứng."
        ],
        "goals": [
            "Định vị năng lực theo chuẩn nghề nghiệp thực tế của doanh nghiệp.",
            "Linh hoạt cho sinh viên năm 1, 2, 3 chưa từng có CV.",
            "Minh bạch hóa lộ trình: phân biệt kỹ năng Bắt buộc (Mandatory) và Bổ trợ (Nice-to-have)."
        ]
    },
    "cv_analysis_gemini": {
        "title": "Phân tích CV (AI) (Phân Tích CV & Kê Đơn Lộ Trình Học bằng Gemini AI)",
        "tech_stack": "Google Gemini AI Powered kết hợp OCR nhận diện mặt chữ",
        "input_modalities": [
            "Kéo thả file CV văn bản: PDF, DOCX, TXT.",
            "Ảnh chụp CV: PNG, JPG, WEBP hoặc bấm phím tắt Ctrl + V dán ảnh chụp màn hình qua OCR.",
            "Dán trực tiếp đoạn văn bản thô (Text)."
        ],
        "process_steps": [
            "Bước 1 - Trích xuất tự động: Gemini AI đọc hiểu ngữ cảnh tự nhiên (Semantic Reading), bóc tách học vấn, dự án và công cụ.",
            "Bước 2 - Đối sánh sâu (Gap Analysis): So sánh hồ sơ với cơ sở dữ liệu hàng ngàn JD thực tế Cần Thơ & ĐBSCL.",
            "Bước 3 - Kê đơn lộ trình học cá nhân hóa: Điểm phù hợp (Match Score %), phân tích mạnh/yếu, thiết kế lộ trình theo tuần/tháng với khóa học cụ thể."
        ]
    }
}


# ═════════════════════════════════════════════════════════════════════
# 5. TRUY VẤN VÀ TÌM KIẾM TRỰC TIẾP (DIRECT LOOKUP HELPERS)
# ═════════════════════════════════════════════════════════════════════

def normalize_industry_key(ind: Optional[str]) -> str:
    if not ind:
        return "IT"
    ilow = ind.lower().strip()
    if any(k in ilow for k in ["it", "cntt", "công nghệ", "phần mềm", "lập trình"]):
        return "IT"
    if any(k in ilow for k in ["du lịch", "khách sạn", "tourism", "du lich"]):
        return "Du lịch"
    if any(k in ilow for k in ["logistics", "xnk", "xuất nhập khẩu", "kho vận", "vận tải"]):
        return "Logistics"
    if any(k in ilow for k in ["kinh tế", "tài chính", "kế toán", "economics", "ngân hàng", "marketing"]):
        return "Kinh tế"
    if any(k in ilow for k in ["nông nghiệp", "agriculture", "agri", "nông nghiệp cnc", "nong nghiep"]):
        return "Nông nghiệp"
    return "IT"


def normalize_region_key(reg: Optional[str]) -> str:
    if not reg:
        return "all"
    rlow = reg.lower().strip()
    if any(k in rlow for k in ["cần thơ", "can tho", "ct", "đbscl", "miền tây"]):
        return "CT"
    if any(k in rlow for k in ["hồ chí minh", "tp.hcm", "tphcm", "hcm", "sài gòn"]):
        return "HCM"
    if any(k in rlow for k in ["hà nội", "ha noi", "hn"]):
        return "HN"
    return "all"


# ═════════════════════════════════════════════════════════════════════
# 6. ENGINE TRUY VẤN VÀ ĐỐI CHIẾU SỐ LIỆU CHÍNH XÁC (QUERY ENGINE)
# ═════════════════════════════════════════════════════════════════════

def lookup_skill_in_overview(query: str) -> Optional[Dict[str, Any]]:
    """Tìm một kỹ năng cụ thể trong bảng Top 5 kỹ năng thiếu hụt tổng quan."""
    q_low = query.lower()
    for item in OVERVIEW_TOP5_SKILLS:
        if item["clean_name"].lower() in q_low or item["skill"].lower() in q_low:
            return item
        if "tiếng anh" in q_low and "tiếng anh" in item["clean_name"].lower():
            return item
        if "cyber" in q_low and "cyber" in item["clean_name"].lower():
            return item
        if "giải quyết" in q_low and "giải quyết" in item["clean_name"].lower():
            return item
        if "docker" in q_low and "docker" in item["clean_name"].lower():
            return item
        if "python" in q_low and "python" in item["clean_name"].lower():
            return item
    return None


def lookup_industry_distribution(industry_key: str) -> Optional[Dict[str, Any]]:
    """Tra cứu tỷ trọng cơ cấu năm 2026 của một ngành."""
    key = normalize_industry_key(industry_key)
    return INDUSTRY_DISTRIBUTION_2026.get(key)


def lookup_industry_trend(industry_key: str, year: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Tra cứu xu hướng số lượng tin tuyển dụng (2023–2027) của ngành."""
    key = normalize_industry_key(industry_key)
    data = INDUSTRY_TREND_2023_2027.get(key)
    if not data:
        return None
    if year:
        cnt = data["years"].get(year)
        is_forecast = (year == 2027)
        return {
            "industry": data["name"],
            "year": year,
            "postings": cnt,
            "is_forecast": is_forecast,
            "trend_summary": data["trend_summary"]
        }
    return data


def lookup_share_comparison(industry_key: str) -> Optional[Dict[str, Any]]:
    """Tra cứu so sánh cơ cấu tỷ trọng (2025 vs 2026) của ngành."""
    key = normalize_industry_key(industry_key)
    return INDUSTRY_SHARE_COMPARE_2025_2026.get(key)


def lookup_top_missing_by_scope(industry_key: str, region_key: str) -> Dict[str, Any]:
    """
    Tra cứu kỹ năng thiếu nhất theo đúng phạm vi:
    - Nếu region_key == 'all': Lấy theo dữ liệu Toàn quốc (Nhóm B).
    - Nếu region_key in ['CT', 'HCM', 'HN']: Lấy theo dữ liệu Khu vực (Nhóm C).
    """
    ind_k = normalize_industry_key(industry_key)
    reg_k = normalize_region_key(region_key)

    if reg_k != "all" and reg_k in REGIONAL_DATA:
        reg_info = REGIONAL_DATA[reg_k]
        ind_info = reg_info["industries"].get(ind_k)
        if ind_info:
            top_skill = ind_info["skills"][0]
            return {
                "scope": f"{ind_info['name']} tại {reg_info['region_name']}",
                "top_missing_skill": top_skill["skill"],
                "gap": top_skill["gap"],
                "demand": top_skill["demand"],
                "supply": top_skill["supply"],
                "salary": ind_info["salary_range"],
                "postings": ind_info["job_postings"],
                "full_info": top_skill
            }

    # Mặc định: Phạm vi Cả nước (Toàn quốc)
    nat_info = NATIONAL_INDUSTRY_DATA.get(ind_k, NATIONAL_INDUSTRY_DATA["IT"])
    top_skill = nat_info["skills"][0]
    return {
        "scope": f"{nat_info['name']} (Cả nước)",
        "top_missing_skill": top_skill["skill"],
        "gap": top_skill["gap"],
        "demand": top_skill["demand"],
        "supply": top_skill["supply"],
        "salary": nat_info["salary_range"],
        "postings": nat_info["job_postings"],
        "full_info": top_skill
    }


def lookup_salary_by_scope(industry_key: str, region_key: str) -> Dict[str, Any]:
    """Tra cứu mức lương tham chiếu theo ngành và khu vực."""
    ind_k = normalize_industry_key(industry_key)
    reg_k = normalize_region_key(region_key)

    if reg_k != "all" and reg_k in REGIONAL_DATA:
        reg_info = REGIONAL_DATA[reg_k]
        ind_info = reg_info["industries"].get(ind_k)
        if ind_info:
            return {
                "scope": f"{ind_info['name']} tại {reg_info['region_name']}",
                "salary_range": ind_info["salary_range"],
                "postings": ind_info["job_postings"]
            }

    nat_info = NATIONAL_INDUSTRY_DATA.get(ind_k, NATIONAL_INDUSTRY_DATA["IT"])
    return {
        "scope": f"{nat_info['name']} (Cả nước)",
        "salary_range": nat_info["salary_range"],
        "postings": nat_info["job_postings"]
    }
