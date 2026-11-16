"""
Trend Evidence Engine & Labor Market Shift Intelligence
Dành riêng cho nền tảng Skill Lens Lab (SkillLed LAB / SkillGap AI)

Tích hợp toàn diện 4 tài liệu ngành chứng minh xu hướng:
1. IT_CongNghe.docx (IT & Công nghệ số)
2. Logistics_XNK_FINAL_HOAN_CHINH.docx (Logistics & Xuất Nhập Khẩu)
3. DuLich_KhachSan_Final.docx (Du lịch & Khách sạn)
4. KinhTe_TaiChinh_Final.docx (Kinh tế & Tài chính)
Kết hợp tài liệu số liệu biểu đồ chuyển dịch (So_Lieu_Bieu_do.docx).

Đảm bảo:
- Phân tách nguồn: DASHBOARD_LIVE vs SHIFT_CHART_2025_2026 vs INDUSTRY_EVIDENCE vs FORECAST.
- Phân biệt phạm vi: Cần Thơ & ĐBSCL (biểu đồ) vs Toàn quốc / Khảo sát chuyên ngành (tài liệu ngành).
- Nhận diện ý định ngữ nghĩa (Semantic Intent) & câu hỏi đồng nghĩa.
- 4 cấp độ trả lời (Level 1: Trực tiếp, Level 2: Nguyên nhân, Level 3: Phân tích sâu, Level 4: Phản biện).
- Hỗ trợ câu hỏi hội thoại tiếp nối (Multi-turn Follow-up) không lẫn ngành.
- Kiểm toán mẫu số tỷ trọng năm 2026 (mẫu số 1.078 tin, không dùng 1.000 tin).
"""

import re
from typing import Dict, Any, List, Optional, Tuple

# ══════════════════════════════════════════════════════════════════════════════
# 1. DỮ LIỆU BIỂU ĐỒ CHUYỂN DỊCH (2025 – 2026) ĐÃ KIỂM TOÁN TỶ TRỌNG (MẪU SỐ 1.078)
# ══════════════════════════════════════════════════════════════════════════════
AUDITED_SHIFT_CHART_2025_2026 = {
    "scope": "TP. Cần Thơ & Đồng bằng Sông Cửu Long (ĐBSCL)",
    "period": "Giai đoạn 2025 – 2026",
    "total_postings_2025": 1000,
    "total_postings_2026": 1078,
    "total_growth_postings": 78,
    "total_growth_rate_pct": 7.8,
    "industries": {
        "IT": {
            "name": "IT & Công nghệ",
            "aliases": ["it", "cntt", "công nghệ số", "lập trình", "phần mềm", "công nghệ thông tin", "digital technology"],
            "postings_2025": 285,
            "share_2025_pct": 28.5,
            "postings_2026": 385,
            "share_2026_audited_pct": 35.7,  # 385 / 1078 = 35.71%
            "share_2026_raw_pct": 38.5,       # Mẫu số cũ 1000
            "diff_postings": 100,
            "growth_rate_pct": 35.1,          # (385 - 285) / 285 = +35.09%
            "diff_share_pp": 7.2,             # 35.7 - 28.5 = +7.2 điểm %
            "rank_growth_pct": 2,             # Xếp thứ 2 sau Nông nghiệp CNC
            "rank_abs_increase": 1,           # Tăng nhiều tin nhất (+100 tin)
            "status": "growth",
            "forecast_2027_postings": 460,
            "forecast_2027_share_pct": 41.8
        },
        "Logistics": {
            "name": "Logistics & XNK",
            "aliases": ["logistics", "xuất nhập khẩu", "xnk", "kho vận", "giao nhận", "chuỗi cung ứng", "supply chain", "vận tải hàng hóa"],
            "postings_2025": 190,
            "share_2025_pct": 19.0,
            "postings_2026": 241,
            "share_2026_audited_pct": 22.4,  # 241 / 1078 = 22.36%
            "share_2026_raw_pct": 24.1,       # Mẫu số cũ 1000
            "diff_postings": 51,
            "growth_rate_pct": 26.8,          # (241 - 190) / 190 = +26.84%
            "diff_share_pp": 3.4,             # 22.4 - 19.0 = +3.4 điểm %
            "rank_growth_pct": 3,
            "rank_abs_increase": 2,           # Tăng nhiều tin thứ 2 (+51 tin)
            "status": "growth",
            "forecast_2027_postings": 290,
            "forecast_2027_share_pct": 26.4
        },
        "Du lịch": {
            "name": "Du lịch & Khách sạn",
            "aliases": ["du lịch", "khách sạn", "lưu trú", "hospitality", "tourism", "lữ hành"],
            "postings_2025": 210,
            "share_2025_pct": 21.0,
            "postings_2026": 218,
            "share_2026_audited_pct": 20.2,  # 218 / 1078 = 20.22%
            "share_2026_raw_pct": 21.8,       # Mẫu số cũ 1000
            "diff_postings": 8,
            "growth_rate_pct": 3.8,           # (218 - 210) / 210 = +3.81%
            "diff_share_pp": -0.8,            # 20.2 - 21.0 = -0.8 điểm %
            "rank_growth_pct": 4,
            "rank_abs_increase": 4,
            "status": "stable",
            "forecast_2027_postings": 225,
            "forecast_2027_share_pct": 20.5
        },
        "Kinh tế": {
            "name": "Kinh tế & Tài chính",
            "aliases": ["kinh tế", "tài chính", "kế toán", "kiểm toán", "ngân hàng", "finance", "accounting"],
            "postings_2025": 270,
            "share_2025_pct": 27.0,
            "postings_2026": 156,
            "share_2026_audited_pct": 14.5,  # 156 / 1078 = 14.47%
            "share_2026_raw_pct": 15.6,       # Mẫu số cũ 1000
            "diff_postings": -114,
            "growth_rate_pct": -42.2,         # (156 - 270) / 270 = -42.22%
            "diff_share_pp": -12.5,           # 14.5 - 27.0 = -12.5 điểm %
            "rank_growth_pct": 5,             # Giảm mạnh nhất
            "rank_abs_increase": 5,           # Giảm nhiều tin nhất (-114 tin)
            "status": "decline",
            "forecast_2027_postings": 115,
            "forecast_2027_share_pct": 10.5
        },
        "Nông nghiệp": {
            "name": "Nông nghiệp Công nghệ cao",
            "aliases": ["nông nghiệp", "nông nghiệp cnc", "nông nghiệp công nghệ cao", "agritech", "nông nghiệp thông minh"],
            "postings_2025": 45,
            "share_2025_pct": 4.5,
            "postings_2026": 78,
            "share_2026_audited_pct": 7.2,   # 78 / 1078 = 7.24%
            "share_2026_raw_pct": 7.8,        # Mẫu số cũ 1000
            "diff_postings": 33,
            "growth_rate_pct": 73.3,          # (78 - 45) / 45 = +73.33%
            "diff_share_pp": 2.7,             # 7.2 - 4.5 = +2.7 điểm %
            "rank_growth_pct": 1,             # Tỷ lệ tăng nhanh nhất (+73.3%)
            "rank_abs_increase": 3,           # Tăng +33 tin
            "status": "boom",
            "forecast_2027_postings": 110,
            "forecast_2027_share_pct": 10.0
        }
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# 2. KHO DỮ LIỆU BẰNG CHỨNG CÓ CẤU TRÚC TỪ 4 TÀI LIỆU NGÀNH (INDUSTRY_EVIDENCE)
# ══════════════════════════════════════════════════════════════════════════════
STRUCTURED_INDUSTRY_EVIDENCE = {
    "IT": [
        {
            "id": "EV_IT_001",
            "point": "Doanh nghiệp mở rộng quy mô nhân sự IT năm 2025 và kế hoạch năm 2026",
            "metric": "66.1% DN mở rộng nhân sự IT năm 2025; 69.6% có kế hoạch mở rộng năm 2026",
            "scope": "Việt Nam (Khảo sát doanh nghiệp tuyển dụng IT)",
            "period": "2025 – 2026",
            "source_doc": "IT_CongNghe.docx",
            "section_page": "Mục 2: Nhu cầu tuyển dụng IT phục hồi (Trang 8)",
            "original_source": "Báo cáo Lương & Thị trường Tuyển dụng IT Việt Nam 2025–2026 của ITviec (khảo sát 1.839 chuyên gia, sinh viên và doanh nghiệp)",
            "info_type": "khảo sát",
            "verification_level": "khảo sát mẫu uy tín",
            "key_takeaway": "Nhu cầu tuyển dụng IT phục hồi rõ rệt nhưng mang tính chọn lọc; không khẳng định mọi DN IT đều mở rộng đồng loạt."
        },
        {
            "id": "EV_IT_002",
            "point": "Ứng dụng AI và xu hướng tăng ngân sách, đội ngũ AI",
            "metric": "73% DN đang ứng dụng AI; 65.1% tăng ngân sách AI; 62% mở rộng đội ngũ AI trong 12 tháng tới; 96.8% chuyên gia dùng AI hàng ngày",
            "scope": "Việt Nam",
            "period": "2025 – 2026",
            "source_doc": "IT_CongNghe.docx",
            "section_page": "Mục 3: AI và công nghệ lõi tạo động lực mới (Trang 8, 16–18)",
            "original_source": "Khảo sát ITviec 2025–2026 kết hợp Quyết định 1131/QĐ-TTg & Luật Công nghiệp công nghệ số",
            "info_type": "khảo sát & chính sách",
            "verification_level": "khảo sát mẫu & văn bản quy phạm",
            "key_takeaway": "AI thúc đẩy tăng trưởng chiều sâu và nhu cầu nhân lực công nghệ cao; không tự động suy ra tỷ lệ tuyển dụng riêng tại Cần Thơ."
        },
        {
            "id": "EV_IT_003",
            "point": "Chuyển dịch tiêu chí tuyển dụng sang năng lực thực tế thay vì tuyển ồ ạt",
            "metric": "Vị trí trọng tâm: Back-end, Full-stack, Front-end. Tiêu chí: giải quyết vấn đề thực tế (44.6%), thích nghi học công nghệ mới (43.4%), tính chủ động ownership (39.8%)",
            "scope": "Việt Nam (chủ yếu TP.HCM và Hà Nội)",
            "period": "2025 – 2026",
            "source_doc": "IT_CongNghe.docx",
            "section_page": "Mục 2: Chiến lược & Nhu cầu tuyển dụng (Trang 9)",
            "original_source": "Báo cáo ITviec 2025–2026",
            "info_type": "khảo sát",
            "verification_level": "khảo sát mẫu",
            "key_takeaway": "Tăng trưởng IT chuyển từ số lượng sang chất lượng và kỹ năng thực tế chuyên sâu."
        },
        {
            "id": "EV_IT_004",
            "point": "Quy mô kinh tế số và đóng góp GDP ngành công nghệ số",
            "metric": "Năm 2024: doanh thu 158 tỷ USD; 2025: ước đạt 198 tỷ USD, đóng góp GDP hơn 1,07 triệu tỷ đồng; hơn 80.000 doanh nghiệp công nghệ số",
            "scope": "Việt Nam",
            "period": "2024 – 2025",
            "source_doc": "IT_CongNghe.docx",
            "section_page": "Mục 1: Quy mô ngành và đóng góp kinh tế",
            "original_source": "Cổng Thông tin điện tử Chính phủ (baochinhphu.vn, 06/02/2026 & 26/12/2025)",
            "info_type": "dữ liệu quan sát chính thức",
            "verification_level": "chính thống",
            "key_takeaway": "Quy mô kinh tế số mở rộng nhanh chóng, bảo chứng nền tảng vĩ mô vững chắc cho ngành IT."
        }
    ],

    "Logistics": [
        {
            "id": "EV_LOG_001",
            "point": "Quy mô kim ngạch thương mại quốc tế xuất nhập khẩu tăng trưởng kỷ lục",
            "metric": "Năm 2025: 930.05 tỷ USD (+18.2%); 10 tháng năm 2026: 1.010.6 tỷ USD (+32.3%, lần đầu vượt mốc 1.000 tỷ USD trong 10 tháng)",
            "scope": "Việt Nam",
            "period": "2025 – 10 tháng 2026",
            "source_doc": "Logistics_XNK_FINAL_HOAN_CHINH.docx",
            "section_page": "Mục 1: Quy mô thương mại quốc tế",
            "original_source": "Cục Thống kê (BCKT-XH năm 2025) & Bộ Công Thương (29/10/2026)",
            "info_type": "dữ liệu quan sát chính thức",
            "verification_level": "chính thống",
            "key_takeaway": "Kim ngạch XNK là giá trị hàng hóa qua biên giới, KHÔNG phải doanh thu thuần của dịch vụ logistics; không thể đồng nhất tốc độ tăng kim ngạch với tốc độ tăng doanh thu hay việc làm logistics."
        },
        {
            "id": "EV_LOG_002",
            "point": "Quy mô thị trường dịch vụ logistics và cơ cấu doanh nghiệp",
            "metric": "Quy mô thị trường dịch vụ logistics ước đạt 45–50 tỷ USD (~10% GDP, 5% kim ngạch XNK), tăng trưởng 14–16%/năm. 95% là DN vừa và nhỏ",
            "scope": "Việt Nam",
            "period": "2025 – 2026",
            "source_doc": "Logistics_XNK_FINAL_HOAN_CHINH.docx",
            "section_page": "Mục 2: Quy mô và vị thế thị trường logistics",
            "original_source": "Cổng thông tin Logistics Việt Nam – Bộ Công Thương & Báo cáo Logistics Việt Nam 2025",
            "info_type": "ước tính ngành",
            "verification_level": "ước tính ngành chính thức",
            "key_takeaway": "Thị trường tăng trưởng tích cực nhưng 95% là DN vừa và nhỏ; điều kiện tuyển dụng khác biệt lớn giữa đại lý nhỏ và tập đoàn logistics tích hợp 3PL–4PL."
        },
        {
            "id": "EV_LOG_003",
            "point": "Triển vọng tuyển dụng Trade & Logistics phục hồi mạnh mẽ trong quý III/2026",
            "metric": "Triển vọng việc làm Trade & Logistics phục hồi mạnh nhất, tăng 26 điểm phần trăm trong Q3/2026. 61% DN dự kiến tăng nhân sự cho biết động lực chính là mở rộng hoạt động",
            "scope": "Việt Nam (Khảo sát nhà tuyển dụng)",
            "period": "Quý 2 & Quý 3/2026",
            "source_doc": "Logistics_XNK_FINAL_HOAN_CHINH.docx",
            "section_page": "Mục 5: Xu hướng nhà tuyển dụng",
            "original_source": "ManpowerGroup Employment Outlook Survey (MEOS) Q2 & Q3/2026",
            "info_type": "khảo sát",
            "verification_level": "khảo sát mẫu quốc tế",
            "key_takeaway": "Mức tăng 26 điểm phần trăm trong khảo sát Manpower KHÔNG phải mức tăng 26.8% số tin của biểu đồ Cần Thơ. 61% là tỷ lệ nêu lý do mở rộng trong nhóm DN tăng nhân sự, không phải 61% toàn bộ DN đều tuyển."
        },
        {
            "id": "EV_LOG_004",
            "point": "Nhóm chức năng và kỹ năng tuyển dụng cốt lõi của ngành Logistics",
            "metric": "Chức năng phổ biến: Nghiệp vụ XNK/chứng từ (10–28 tr/th), Customer Service (10.5–26 tr/th), Purchasing, Merchandiser, Sales logistics (10–28 tr/th), vận hành kho, điều phối vận tải. Kỹ năng số: WMS, TMS, ERP, phân tích chuỗi cung ứng",
            "scope": "Việt Nam",
            "period": "2025 – 2026",
            "source_doc": "Logistics_XNK_FINAL_HOAN_CHINH.docx",
            "section_page": "Mục 5.2 & Mục 6: Chuyển đổi số và chuẩn lương",
            "original_source": "Reeracoen Vietnam – Logistics & Supply Chain Talent 2026 & Báo cáo Logistics Việt Nam 2025",
            "info_type": "chuẩn lương tham khảo & báo cáo ngành",
            "verification_level": "khảo sát tuyển dụng",
            "key_takeaway": "Nhu cầu tập trung vào kỹ năng thực hành chứng từ, số hóa quy trình WMS/TMS/ERP và khả năng giao tiếp ngoại ngữ."
        }
    ],

    "Du lịch": [
        {
            "id": "EV_DL_001",
            "point": "Lượng khách quốc tế và tổng thu du lịch tăng trưởng mạnh mẽ, vượt mốc trước dịch",
            "metric": "Năm 2025: đón 21.2 triệu lượt khách quốc tế (+20.4% so với 2024, +17.8% so với 2019); tổng thu du lịch đạt 1.000 nghìn tỷ đồng (+19.0%). 10 tháng năm 2026: 19.5 triệu khách quốc tế (+13.8%), tổng thu khoảng 945 nghìn tỷ đồng",
            "scope": "Việt Nam",
            "period": "2025 – 10 tháng 2026",
            "source_doc": "DuLich_KhachSan_Final.docx",
            "section_page": "Phần I, Mục 1 & 2: Lượng khách và Doanh thu du lịch",
            "original_source": "Cục Du lịch Quốc gia Việt Nam & Cục Thống kê (tháng 10/2026)",
            "info_type": "dữ liệu quan sát chính thức",
            "verification_level": "chính thống",
            "key_takeaway": "Hoạt động du lịch mở rộng mạnh mẽ trên toàn quốc; tuy nhiên doanh thu 'lưu trú & ăn uống' bao gồm cả nhà hàng, không phải toàn bộ là của khách sạn."
        },
        {
            "id": "EV_DL_002",
            "point": "Nghịch lý tuyển dụng: Doanh nghiệp khó tuyển người nhưng chỉ bổ sung số lượng nhỏ",
            "metric": "8/10 DN gặp khó khăn khi tuyển dụng; gần 90% có kế hoạch tuyển. NHƯNG 64% DN chỉ cần bổ sung một lượng nhân sự nhỏ. Tỷ lệ nghỉ việc bình quân 18.9% (25% DN có tỷ lệ nghỉ việc > 30%)",
            "scope": "Việt Nam (Khảo sát 331 doanh nghiệp du lịch – khách sạn)",
            "period": "Năm 2026",
            "source_doc": "DuLich_KhachSan_Final.docx",
            "section_page": "Phần II: Xu hướng việc làm và nhu cầu nhân lực",
            "original_source": "Hoteljob.vn – Khảo sát 2026 về thực trạng và triển vọng việc làm ngành Du lịch – Khách sạn (25/08/2026)",
            "info_type": "khảo sát",
            "verification_level": "khảo sát mẫu chuyên ngành",
            "key_takeaway": "Giải thích vì sao số tin biểu đồ chỉ tăng 3.8% dù khách tăng mạnh: DN du lịch chủ yếu tuyển bù chỗ trống thay thế người nghỉ việc và bổ sung quy mô nhỏ, sử dụng lao động linh hoạt theo mùa vụ chứ không mở rộng ồ ạt biên chế."
        },
        {
            "id": "EV_DL_003",
            "point": "Các vị trí thiếu hụt và khoảng trống kỹ năng lớn nhất",
            "metric": "Bộ phận khó tuyển nhất: Buồng phòng (50%), Bếp (41.5%), Tiền sảnh (39.6%). Khoảng trống kỹ năng lớn nhất: Tư duy dịch vụ/thái độ (49%), Ngoại ngữ (26%), Kỹ năng chuyên môn (22%), Kỹ năng công nghệ (4%)",
            "scope": "Việt Nam",
            "period": "Năm 2026",
            "source_doc": "DuLich_KhachSan_Final.docx",
            "section_page": "Phần II: Xu hướng việc làm & Yêu cầu kỹ năng",
            "original_source": "Hoteljob.vn (khảo sát 2026) & Vietnam News (15/09/2026)",
            "info_type": "khảo sát",
            "verification_level": "khảo sát mẫu",
            "key_takeaway": "Thiếu hụt tập trung ở nhóm vận hành tuyến đầu trực tiếp phục vụ khách hàng; lợi thế cạnh tranh của người lao động là thái độ, nghiệp vụ và ngoại ngữ."
        }
    ],

    "Kinh tế": [
        {
            "id": "EV_KT_001",
            "point": "Hoạt động kinh tế và tài chính vĩ mô vẫn tăng trưởng tích cực",
            "metric": "GDP 2025 tăng 8.02%; 9 tháng năm 2026: giá trị tăng thêm ngành tài chính, ngân hàng và bảo hiểm tăng 9.45% so với cùng kỳ. Vốn hóa thị trường cổ phiếu đạt ~10.57 triệu tỷ đồng (tháng 6/2026). FTSE Russell nâng hạng từ 21/09/2026",
            "scope": "Việt Nam",
            "period": "2025 – 9 tháng 2026",
            "source_doc": "KinhTe_TaiChinh_Final.docx",
            "section_page": "Phần II, Mục 1 & 3: Nền kinh tế mở rộng & Thị trường vốn",
            "original_source": "Cục Thống kê (BCKT-XH 2025 & 9 tháng 2026), Bộ Tài chính, FTSE Russell",
            "info_type": "dữ liệu quan sát chính thức",
            "verification_level": "chính thống",
            "key_takeaway": "Mức giảm -42.2% số tin tuyển dụng trong biểu đồ KHÔNG đồng nghĩa ngành tài chính - kinh tế Việt Nam suy thoái 42.2%. Quy mô kinh tế và thị trường tài chính vẫn mở rộng."
        },
        {
            "id": "EV_KT_002",
            "point": "Quy mô tài sản ngân hàng tăng nhanh vượt trội so với quy mô nhân sự",
            "metric": "Giai đoạn 2020–2025 trên mẫu 28 ngân hàng: Tổng tài sản tăng trung vị 117% nhưng nhân sự chỉ tăng 11%; tài sản bình quân trên mỗi lao động tăng 98%",
            "scope": "Việt Nam (Mẫu 28 ngân hàng thương mại)",
            "period": "2020 – 2025",
            "source_doc": "KinhTe_TaiChinh_Final.docx",
            "section_page": "Phần II: Xu hướng việc làm và nhu cầu nhân lực ngành Tài chính – Ngân hàng",
            "original_source": "Nghiên cứu của Viện Nghiên cứu Khoa học Ngân hàng – Học viện Ngân hàng (15/07/2026)",
            "info_type": "nghiên cứu thực nghiệm chuyên sâu",
            "verification_level": "nghiên cứu học thuật",
            "key_takeaway": "Ngân hàng và định chế tài chính ưu tiên nâng cao năng suất, tự động hóa quy trình và tối ưu hóa vận hành thay vì mở rộng biên chế lao động theo tỷ lệ thuận với tài sản."
        },
        {
            "id": "EV_KT_003",
            "point": "Cơ cấu tuyển dụng và tác động của tự động hóa/AI đối với nghiệp vụ lặp lại",
            "metric": "Trong 3.005 tin tuyển dụng ngân hàng: Tín dụng và Quản trị rủi ro chiếm 58.3%. Khoảng 40–50% tổ chức tín dụng dự kiến tuyển thêm người năm 2026 (theo NHNN/VCCI). Tác vụ nhập liệu và giao dịch viên chịu áp lực tự động hóa",
            "scope": "Việt Nam (Khảo sát ngân hàng và thị trường tuyển dụng)",
            "period": "2025 – 2026",
            "source_doc": "KinhTe_TaiChinh_Final.docx",
            "section_page": "Phần II: Cơ cấu tuyển dụng & AI chuyển đổi số",
            "original_source": "Học viện Ngân hàng (3.005 tin tuyển dụng), VCCI dẫn khảo sát NHNN (10/01/2026), WEF Future of Jobs Report 2025",
            "info_type": "khảo sát & phân tích",
            "verification_level": "khảo sát mẫu",
            "key_takeaway": "Tự động hóa/AI tác động mạnh vào công việc lặp lại (nhập liệu, kế toán cơ bản), trong khi nhu cầu chuyên môn cao (thẩm định tín dụng, quản trị rủi ro, phân tích dữ liệu, tuân thủ) vẫn tuyển dụng có chọn lọc."
        }
    ]
}

# ══════════════════════════════════════════════════════════════════════════════
# 3. SEMANTIC INTENT CLASSIFIER & SCOPE RESOLVER CHO XU HƯỚNG CHUYỂN DỊCH
# ══════════════════════════════════════════════════════════════════════════════
def classify_trend_semantic_intent(query: str, history: List[Any] = None) -> Dict[str, Any]:
    """
    Phân loại ý định ngữ nghĩa (Semantic Intent) của câu hỏi về xu hướng chuyển dịch:
    - INTENT: EXPLAIN_LABOR_MARKET_SHIFT (Tổng thể)
    - INTENT: EXPLAIN_INDUSTRY_TREND (Riêng ngành)
    - LEVEL: 1 (Trực tiếp), 2 (Giải thích nguyên nhân), 3 (Phân tích sâu có chứng minh), 4 (So sánh & Phản biện)
    - TARGET_INDUSTRY: IT / Logistics / Du lịch / Kinh tế / Nông nghiệp / None
    - FOLLOW_UP: Hỗ trợ 'Thế Logistics?', 'Còn Kinh tế?', 'Còn Du lịch?'
    """
    q_raw = query.strip()
    q_low = q_raw.lower()

    # Nhận diện ngành đề cập trong câu hỏi
    target_ind = None

    # Nếu câu hỏi đề cập nhiều ngành hoặc là câu hỏi tổng quát so sánh các ngành:
    has_multiple_industries = (
        ("it" in q_low or "công nghệ" in q_low) and ("logistics" in q_low or "kinh tế" in q_low)
    ) or (
        "kinh tế" in q_low and "công nghệ" in q_low
    ) or (
        "thị trường lao động đang chuyển dịch mạnh sang" in q_low
    ) or (
        "dựa vào đâu mà nói it và logistics tăng" in q_low
    )

    if not has_multiple_industries:
        if any(k in q_low for k in ["kế toán", "kiểm toán", "ngân hàng", "tài chính", "finance", "accounting", "kinh tế"]):
            target_ind = "Kinh tế"
        elif any(k in q_low for k in ["logistics", "xuất nhập khẩu", "xnk", "kho vận", "giao nhận", "chuỗi cung ứng", "supply chain", "vận tải"]):
            target_ind = "Logistics"
        elif any(k in q_low for k in ["du lịch", "khách sạn", "lưu trú", "hospitality", "tourism", "lữ hành"]):
            target_ind = "Du lịch"
        elif any(k in q_low for k in ["it", "cntt", "công nghệ số", "lập trình", "phần mềm", "công nghệ thông tin", "digital tech"]):
            target_ind = "IT"
        elif any(k in q_low for k in ["nông nghiệp", "nông nghiệp cnc", "nông nghiệp công nghệ cao", "agritech"]):
            target_ind = "Nông nghiệp"

    # Kiểm tra ngữ cảnh hội thoại đa lượt (Multi-turn Follow-up)
    is_followup = False
    followup_patterns = ["thế ", "còn ", "vậy còn ", "thế còn ", "thế thì ", "còn ngành ", "với ngành "]
    if any(q_low.startswith(p) for p in followup_patterns) or len(q_low.split()) <= 4:
        if target_ind:
            is_followup = True

    # Nhóm A: Câu hỏi giải thích chuyển dịch tổng thể (EXPLAIN_LABOR_MARKET_SHIFT)
    general_shift_patterns = [
        "tại sao hệ thống ai lại kết luận như vậy",
        "tại sao hệ thống kết luận như vậy",
        "tại sao hệ thống kết luận",
        "vì sao có sự chuyển dịch ngành nghề",
        "vì sao có sự chuyển dịch",
        "dựa vào đâu mà nói it và logistics tăng",
        "dựa vào đâu mà nói",
        "cơ sở nào chứng minh xu hướng chuyển dịch",
        "cơ sở nào chứng minh",
        "những con số này lấy từ đâu",
        "con số này lấy từ đâu",
        "ai căn cứ vào đâu để đưa ra kết luận",
        "ai căn cứ vào đâu",
        "tại sao kinh tế giảm mà công nghệ tăng",
        "hãy chứng minh nhận định của biểu đồ",
        "chứng minh nhận định của biểu đồ",
        "giải thích kết luận chuyển dịch 2025–2026",
        "giải thích kết luận chuyển dịch 2025-2026",
        "giải thích kết luận chuyển dịch",
        "kết luận này có đáng tin không",
        "vì sao thị trường lao động đang thay đổi",
        "thị trường lao động đang chuyển dịch mạnh sang",
        "what evidence supports the labor market shift",
        "hãy giải thích toàn bộ kết luận chuyển dịch",
        "kết luận chuyển dịch từ hệ thống ai",
        "kết luận chuyển dịch"
    ]

    is_general_shift = any(p in q_low for p in general_shift_patterns) or has_multiple_industries

    # Các chủ đề chuyên biệt trong 16 câu hỏi Section VIII
    special_topic_patterns = [
        "suy thoái không", "có suy thoái", "ngành tài chính đang suy thoái", "kinh tế suy thoái",
        "chỉ tăng 3,8%", "chỉ tăng 3.8%", "lượng khách", "lượng khách du lịch",
        "nhanh nhất trong biểu đồ", "tăng trưởng tuyển dụng nhanh nhất", "tăng nhanh nhất trong biểu đồ", "tỷ lệ tăng cao nhất",
        "tăng nhiều tin tuyển dụng nhất", "tăng nhiều tin nhất trong biểu đồ", "tăng nhiều tin nhất", "tăng số lượng tuyệt đối lớn nhất",
        "giảm tuyển dụng mạnh nhất", "giảm mạnh nhất trong biểu đồ", "sụt giảm nhiều nhất", "giảm nhiều tin nhất",
        "thay thế kế toán", "kế toán có bị thay thế", "ai thay thế kế toán", "kế toán bị ai",
        "tất cả doanh nghiệp logistics", "tất cả công ty logistics", "có phải tất cả",
        "chú trọng kỹ năng hơn số lượng", "kỹ năng hơn số lượng", "ưu tiên hơn việc tuyển ồ ạt", "tuyển ồ ạt", "chọn lọc hơn",
        "73,3%", "73.3%", "con số này có ý nghĩa gì", "có ý nghĩa gì",
        "dữ liệu thực hay dự báo", "thực tế hay dự báo", "dự báo hay thực",
        "riêng của tp. cần thơ", "riêng của cần thơ", "riêng cần thơ", "4 tài liệu ngành có phải", "tài liệu ngành có phải",
        "chứng minh ai làm giảm việc làm", "chứng minh ai gây ra", "ai làm giảm việc làm", "nguyên nhân duy nhất",
        "tại sao nhân sự chậm", "tăng nhân sự chậm", "tài sản tăng nhưng nhân sự"
    ]
    is_special_topic = any(p in q_low for p in special_topic_patterns)
    if any(k in q_low for k in ["nhóm kỹ năng nào", "cần kỹ năng gì", "cần những kỹ năng", "kỹ năng cần thiết"]) and ("logistics" in q_low or "xnk" in q_low):
        is_special_topic = True
    if ("du lịch" in q_low or "khách sạn" in q_low) and any(k in q_low for k in ["vị trí nào", "thiếu người ở", "khó tuyển nhất", "vị trí khó tuyển"]):
        is_special_topic = True

    # Loại trừ các câu hỏi đặc thù khác (không thuộc phạm vi Trend Shift Engine)
    exclusion_patterns = [
        "gap cao nhất", "kỹ năng có gap", "kỹ năng nào thiếu nhất", "top 5 kỹ năng", "top 10 kỹ năng",
        "mức lương", "lương", "thu nhập", "mật khẩu", "password", "bỏ qua dữ liệu", "dump database",
        "bao nhiêu tin tuyển dụng trong database", "toàn hệ thống có bao nhiêu tin", "hệ thống hiện có bao nhiêu tin"
    ]
    is_excluded = any(p in q_low for p in exclusion_patterns)

    # Đánh giá xem câu hỏi có thuộc Trend Evidence Engine hay không
    is_trend_match = False
    if not is_excluded:
        if is_special_topic:
            is_trend_match = True
        elif is_general_shift:
            is_trend_match = True
        elif target_ind and any(k in q_low for k in ["tại sao", "vì sao", "lý do", "căn cứ", "nguyên nhân", "chứng minh"]) and any(k in q_low for k in ["tăng", "giảm", "chuyển dịch", "xu hướng"]):
            is_trend_match = True
        elif is_followup and target_ind:
            is_trend_match = True
        elif ("2025" in q_low and "2026" in q_low) and any(k in q_low for k in ["bao nhiêu", "số tin", "tuyển dụng"]):
            is_trend_match = True

    # Xác định cấp độ phản hồi (Level 1, 2, 3, 4)
    level_4_patterns = [
        "suy thoái không", "có suy thoái", "ngành tài chính đang suy thoái",
        "chỉ tăng 3,8% dù lượng khách", "chỉ tăng 3.8% dù lượng khách", "lượng khách tăng mạnh",
        "ai có đang thay thế kế toán", "thay thế kế toán không", "thay thế hoàn toàn",
        "tất cả công ty logistics đều tuyển", "tất cả công ty logistics", "có phải tất cả",
        "vẫn phát triển nhưng tăng nhân sự chậm", "tăng nhân sự chậm",
        "dữ liệu thực hay dự báo", "là dữ liệu thực hay",
        "ai làm giảm việc làm kế toán không", "ai làm giảm việc làm"
    ]
    is_level_4 = any(p in q_low for p in level_4_patterns)

    # Level 1: Hỏi một con số trực tiếp / Xếp hạng ngắn gọn
    level_1_patterns = [
        "tăng bao nhiêu", "giảm bao nhiêu", "tăng trưởng bao nhiêu",
        "ngành nào tăng trưởng tuyển dụng nhanh nhất", "ngành nào tăng nhanh nhất",
        "ngành nào tăng nhiều tin tuyển dụng nhất", "ngành nào tăng nhiều nhất",
        "ngành nào giảm tuyển dụng mạnh nhất", "ngành nào giảm mạnh nhất",
        "tăng bao nhiêu tin", "giảm bao nhiêu tin"
    ]
    is_level_1 = any(p in q_low for p in level_1_patterns) and not any(k in q_low for k in ["tại sao", "vì sao", "lý do"])

    # Phân loại Intent & Level
    if is_level_4:
        level = 4
        intent = "EXPLAIN_INDUSTRY_TREND" if target_ind else "EXPLAIN_LABOR_MARKET_SHIFT"
    elif is_level_1:
        level = 1
        intent = "EXPLAIN_INDUSTRY_TREND" if target_ind else "EXPLAIN_LABOR_MARKET_SHIFT"
    elif is_general_shift and not target_ind:
        level = 3 if ("toàn bộ" in q_low or "chứng minh" in q_low or "bằng chứng" in q_low) else 2
        intent = "EXPLAIN_LABOR_MARKET_SHIFT"
    elif target_ind and any(k in q_low for k in ["tại sao", "vì sao", "lý do", "nguyên nhân", "căn cứ", "chứng minh", "xu hướng"]):
        level = 2
        intent = "EXPLAIN_INDUSTRY_TREND"
    elif is_general_shift and target_ind:
        level = 2
        intent = "EXPLAIN_INDUSTRY_TREND"
    else:
        level = 2 if target_ind else 3
        intent = "EXPLAIN_INDUSTRY_TREND" if target_ind else "EXPLAIN_LABOR_MARKET_SHIFT"

    return {
        "is_trend_match": is_trend_match,
        "intent": intent,
        "level": level,
        "target_industry": target_ind,
        "is_followup": is_followup,
        "raw_query": q_raw
    }

# ══════════════════════════════════════════════════════════════════════════════
# 4. TRÌNH TẠO PHẢN HỒI THÔNG MINH CHO CẢ 16 CÂU HỎI THAM CHIẾU VÀ CÁC BIẾN THỂ
# ══════════════════════════════════════════════════════════════════════════════
def generate_trend_insight_answer(intent_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Sinh câu trả lời thông minh dựa trên 4 cấp độ, dữ liệu biểu đồ và 4 tài liệu ngành.
    Bảo đảm:
    - Đúng con số từ biểu đồ 2025–2026.
    - Dẫn đúng tài liệu chứng minh và nguồn nghiên cứu gốc.
    - Không lẫn ngành khác khi người dùng hỏi riêng một ngành.
    - Tách biệt rõ ràng phạm vi địa lý (Cần Thơ & ĐBSCL vs Toàn quốc).
    - Cảnh báo giới hạn dữ liệu và không khẳng định quan hệ nhân quả cực đoan.
    """
    q_low = intent_info["raw_query"].lower()
    ind = intent_info.get("target_industry")
    lvl = intent_info.get("level", 2)
    chart = AUDITED_SHIFT_CHART_2025_2026

    # ──────────────────────────────────────────────────────────────────────────
    # ƯU TIÊN 1: CÁC CÂU HỎI CHỦ ĐỀ CHUYÊN BIỆT (Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13, Q14, Q15, Q16)
    # ──────────────────────────────────────────────────────────────────────────

    # Câu 4: Kinh tế giảm tuyển dụng có nghĩa ngành tài chính đang suy thoái không?
    if any(k in q_low for k in ["suy thoái không", "có suy thoái", "ngành tài chính đang suy thoái", "kinh tế suy thoái"]):
        answer = (
            "Không. Biểu đồ ghi nhận số tin tuyển dụng giảm trong một nhóm dữ liệu cụ thể (giảm từ 270 xuống 156 tin tại Cần Thơ & ĐBSCL), "
            "còn các tài liệu chính thống cho thấy hoạt động kinh tế, tài chính, ngân hàng và bảo hiểm Việt Nam vẫn tăng trưởng tích cực ở nhiều chỉ tiêu:\n"
            "- Theo Cục Thống kê, 9 tháng năm 2026, giá trị tăng thêm của hoạt động tài chính, ngân hàng và bảo hiểm tăng 9,45% so với cùng kỳ.\n"
            "- Quy mô vốn hóa thị trường cổ phiếu đạt khoảng 10,57 triệu tỷ đồng vào tháng 6/2026 (~82,3% GDP năm 2025), và thị trường chứng khoán được FTSE Russell chính thức nâng hạng từ tháng 9/2026.\n\n"
            "Tăng trưởng hoạt động kinh tế/tài chính và tăng trưởng số việc làm tuyển mới là hai chỉ số hoàn toàn khác nhau. Ngành tài chính đang tối ưu hóa năng suất và tinh gọn bộ máy chứ không hề suy thoái."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "finance_va_growth_9m2026", "value": "+9.45%", "source": "INDUSTRY_EVIDENCE (KinhTe_TaiChinh_Final.docx - Cục Thống kê)"},
                {"metric": "market_cap_gdp", "value": "10.57 triệu tỷ đồng (~82.3% GDP)", "source": "INDUSTRY_EVIDENCE (Bộ Tài chính)"}
            ],
            "analysis": "Phân biệt rõ ràng giữa chỉ số hoạt động kinh tế vĩ mô và chỉ số nhu cầu tuyển dụng trong một mẫu khảo sát cụ thể.",
            "recommendations": ["Không đánh đồng số lượng tin tuyển dụng giảm với suy thoái kinh tế."],
            "chart_refs": ["So Sánh Cơ Cấu Tỷ Trọng (2025 vs 2026)"],
            "limitations": ["Cần theo dõi thêm diễn biến chất lượng tài sản và tăng trưởng tín dụng cả năm."]
        }

    # Câu 5: Tại sao Du lịch chỉ tăng 3,8% dù lượng khách tăng mạnh?
    if ("du lịch" in q_low or "khách sạn" in q_low) and any(k in q_low for k in ["3,8", "3.8", "chỉ tăng", "lượng khách", "khách tăng mạnh"]):
        answer = (
            "Số tin tuyển dụng du lịch trong biểu đồ 2025–2026 tăng từ 210 lên 218 tin, tương đương mức tăng 3,8% "
            "(tỷ trọng chuẩn hóa biến động nhẹ từ 21,0% xuống 20,2%, tức -0,8 điểm % thị phần). Trong khi đó, lượng khách quốc tế toàn quốc "
            "năm 2025 đạt kỷ lục 21,2 triệu lượt và 10 tháng năm 2026 đạt 19,5 triệu lượt (tăng 13,8% so với cùng kỳ).\n\n"
            "Điều này không hề mâu thuẫn vì:\n"
            "1. Khảo sát Hoteljob.vn năm 2026 cho thấy dù gần 90% doanh nghiệp có kế hoạch tuyển, có đến 64% đơn vị chỉ cần bổ sung một lượng nhân sự nhỏ "
            "để thay thế người nghỉ việc (tỷ lệ nghỉ việc bình quân ngành là 18,9%), chứ không mở rộng ồ ạt quy mô.\n"
            "2. Biến động khách theo mùa là áp lực lớn đối với quỹ lương (42% DN cho biết), do đó doanh nghiệp có xu hướng duy trì đội ngũ nòng cốt, "
            "nâng cao hiệu suất phục vụ và sử dụng lao động linh hoạt theo mùa vụ thay vì tăng biên chế cố định."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "tourism_chart_growth", "value": "3.8% (210 -> 218 tin)", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"},
                {"metric": "hoteljob_small_hiring", "value": "64% DN chỉ bổ sung số lượng nhỏ", "source": "INDUSTRY_EVIDENCE (DuLich_KhachSan_Final.docx - Hoteljob.vn)"}
            ],
            "analysis": "Lượng khách tăng mạnh nhưng số tin tuyển dụng chỉ tăng nhẹ do doanh nghiệp tối ưu năng suất và tuyển thay thế theo mùa vụ.",
            "recommendations": ["Nâng chuẩn ngoại ngữ, năng lực giao tiếp đa văn hóa và kỹ năng ứng dụng công nghệ khách sạn."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Doanh thu lưu trú và ăn uống bao gồm cả nhà hàng, không phải toàn bộ của khách sạn."]
        }

    # Câu 6: Ngành nào tăng trưởng tuyển dụng nhanh nhất trong biểu đồ?
    if any(k in q_low for k in ["nhanh nhất trong biểu đồ", "tăng trưởng tuyển dụng nhanh nhất", "tăng nhanh nhất", "tỷ lệ tăng cao nhất"]):
        answer = (
            "Nông nghiệp công nghệ cao có tỷ lệ tăng số tin cao nhất trong biểu đồ, đạt 73,3% (tăng từ 45 lên 78 tin). "
            "IT & Công nghệ đứng sau với mức tăng 35,1% (từ 285 lên 385 tin)."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "agri_growth_rate", "value": "73.3%", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"},
                {"metric": "it_growth_rate", "value": "35.1%", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"}
            ],
            "analysis": "Nông nghiệp CNC đạt tốc độ tăng trưởng phần trăm cao nhất do xuất phát từ quy mô nền nhỏ.",
            "recommendations": ["Lưu ý phân biệt giữa tỷ lệ tăng trưởng phần trăm và số lượng tin tuyệt đối tăng thêm."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Dữ liệu Nông nghiệp CNC trong biểu đồ có quy mô mẫu còn nhỏ (78 tin)."]
        }

    # Câu 7: Ngành nào tăng nhiều tin tuyển dụng nhất?
    if any(k in q_low for k in ["tăng nhiều tin tuyển dụng nhất", "tăng nhiều tin nhất", "tăng số lượng tuyệt đối lớn nhất", "tăng nhiều việc làm nhất"]):
        answer = (
            "IT & Công nghệ tăng 100 tin tuyển dụng, từ 285 lên 385 tin. Đây là mức tăng số lượng tuyệt đối lớn nhất "
            "trong năm ngành được hiển thị trên biểu đồ chuyển dịch 2025–2026."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "it_absolute_increase", "value": "+100 tin (285 -> 385)", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"}
            ],
            "analysis": "IT là động lực tăng trưởng tuyệt đối lớn nhất của thị trường việc làm khu vực.",
            "recommendations": ["Ưu tiên kết nối đào tạo nhân lực CNTT chất lượng cao."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Dữ liệu phản ánh số tin tuyển dụng thu thập trong giai đoạn khảo sát."]
        }

    # Câu 8: Ngành nào giảm tuyển dụng mạnh nhất?
    if any(k in q_low for k in ["giảm tuyển dụng mạnh nhất", "giảm mạnh nhất", "sụt giảm nhiều nhất", "giảm nhiều tin nhất"]):
        answer = (
            "Kinh tế & Tài chính giảm mạnh nhất trong biểu đồ, từ 270 xuống 156 tin, tức giảm 114 tin tuyển dụng, "
            "tương đương mức giảm 42,2% (tỷ trọng chuẩn hóa sụt giảm từ 27,0% xuống 14,5%)."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "finance_absolute_decrease", "value": "-114 tin (270 -> 156)", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"},
                {"metric": "finance_growth_rate", "value": "-42.2%", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"}
            ],
            "analysis": "Nhóm ngành Kinh tế & Kế toán ghi nhận mức thu hẹp số tin tuyển dụng sâu nhất trên biểu đồ.",
            "recommendations": ["Cần tái đào tạo người lao động kế toán sang kỹ năng tài chính công nghệ."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Chỉ phản ánh số tin thu thập được trong nhóm khảo sát."]
        }

    # Câu 9: AI có đang thay thế kế toán không?
    if any(k in q_low for k in ["thay thế kế toán", "ai thay thế kế toán", "kế toán có bị thay thế", "kế toán bị ai"]):
        answer = (
            "AI và tự động hóa đang làm thay đổi các tác vụ kế toán lặp lại, đặc biệt là nhập liệu và xử lý quy trình chứng từ. "
            "Tuy nhiên, dữ liệu không chứng minh mọi vị trí kế toán đều bị thay thế.\n\n"
            "Nhu cầu chuyên môn về phân tích tài chính, kiểm soát nội bộ, quản trị rủi ro, tuân thủ pháp lý và kỹ năng sử dụng công nghệ vẫn tồn tại. "
            "Xu hướng thực tế là chuyển dịch từ công việc kế toán sổ sách thủ công sang vai trò tư vấn, hoạch định và giám sát dữ liệu tài chính số."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "accounting_automation", "value": "Tác vụ nhập liệu lặp lại chịu áp lực", "source": "INDUSTRY_EVIDENCE (KinhTe_TaiChinh_Final.docx & WEF Future of Jobs)"}
            ],
            "analysis": "Tác động của AI mang tính tái định hình kỹ năng công việc hơn là loại bỏ hoàn toàn ngành nghề.",
            "recommendations": ["Trang bị kỹ năng phân tích dữ liệu (PowerBI, Python) và hiểu biết về quản trị thuế chuyên sâu."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Cần thêm nghiên cứu định lượng độc lập để đo lường tỷ lệ thay thế việc làm trực tiếp."]
        }

    # Câu 10: Logistics đang cần những nhóm kỹ năng nào?
    if any(k in q_low for k in ["nhóm kỹ năng nào", "cần kỹ năng gì", "cần những kỹ năng", "kỹ năng cần thiết"]) and ("logistics" in q_low or "xnk" in q_low):
        answer = (
            "Tài liệu ngành Logistics nhấn mạnh các nhóm kỹ năng trọng tâm:\n"
            "- Nghiệp vụ chuyên ngành: Xuất nhập khẩu, quản trị chuỗi cung ứng, chứng từ hải quan, quản lý kho bãi và khai thác cảng.\n"
            "- Kỹ năng công nghệ & hệ thống số: Khả năng vận hành phần mềm quản lý kho (WMS), hệ thống điều phối vận tải (TMS), hệ thống hoạch định doanh nghiệp (ERP) và phân tích dữ liệu luồng hàng.\n"
            "- Ngoại ngữ & Giao tiếp: Tiếng Anh thương mại phục vụ đàm phán hợp đồng, phối hợp chuỗi cung ứng quốc tế và chăm sóc khách hàng (Customer Service)."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "logistics_key_skills", "value": "WMS, TMS, ERP, XNK, Ngoại ngữ", "source": "INDUSTRY_EVIDENCE (Logistics_XNK_FINAL_HOAN_CHINH.docx - Reeracoen & BC Logistics 2025)"}
            ],
            "analysis": "Logistics hiện đại đòi hỏi nhân sự tích hợp giữa nghiệp vụ vận tải và năng lực xử lý dữ liệu số.",
            "recommendations": ["Học thực hành các phần mềm WMS/TMS và rèn luyện kỹ năng giải quyết phát sinh giao nhận."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Yêu cầu kỹ năng khác nhau giữa doanh nghiệp vận tải nhỏ và tập đoàn 3PL–4PL."]
        }

    # Câu 11: Du lịch thiếu người ở những vị trí nào?
    if ("du lịch" in q_low or "khách sạn" in q_low) and any(k in q_low for k in ["vị trí nào", "thiếu người ở", "khó tuyển nhất", "vị trí khó tuyển"]):
        answer = (
            "Theo khảo sát Hoteljob.vn năm 2026 được trích dẫn trong tài liệu, ba bộ phận khó tuyển nổi bật nhất trong nhóm doanh nghiệp được khảo sát là:\n"
            "1. Buồng phòng (50% doanh nghiệp đánh giá khó tuyển nhất).\n"
            "2. Bếp (41,5% doanh nghiệp đánh giá khó tuyển).\n"
            "3. Tiền sảnh (39,6% doanh nghiệp đánh giá khó tuyển).\n\n"
            "Ngoài ra, các khảo sát bổ sung ghi nhận khó tuyển ở bộ phận kỹ thuật – bảo trì và phục vụ bàn/tiệc. "
            "Đây là những vị trí vận hành tuyến đầu thiết yếu, trực tiếp quyết định công suất phục vụ và chất lượng trải nghiệm của khách lưu trú."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "tourism_hard_to_fill", "value": "Buồng phòng (50%), Bếp (41.5%), Tiền sảnh (39.6%)", "source": "INDUSTRY_EVIDENCE (DuLich_KhachSan_Final.docx - Hoteljob.vn 2026)"}
            ],
            "analysis": "Sự thiếu hụt nhân lực du lịch tập trung ở nhóm lao động vận hành trực tiếp, có tay nghề và chấp nhận làm việc theo ca kíp.",
            "recommendations": ["Tăng cường liên kết đào tạo nghề thực hành giữa trường đào tạo và các khu nghỉ dưỡng, khách sạn."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Khảo sát đại diện cho mẫu 331 doanh nghiệp tham gia khảo sát của Hoteljob.vn."]
        }

    # Câu 12: Vì sao doanh nghiệp IT chú trọng kỹ năng hơn số lượng?
    if ("it" in q_low or "cntt" in q_low or "công nghệ" in q_low) and any(k in q_low for k in ["kỹ năng hơn số lượng", "chú trọng kỹ năng", "chọn lọc", "tại sao it tuyển chọn lọc"]):
        answer = (
            "Tài liệu ITviec 2025–2026 ghi nhận tuyển dụng ngành IT đang chuyển từ giai đoạn 'bùng nổ số lượng' sang giai đoạn phát triển chiều sâu và bền vững. "
            "Doanh nghiệp tập trung tuyển dụng cấp trung và cao cấp ở các vị trí cốt lõi (Back-end, Full-stack, Front-end) và đặc biệt ưu tiên các năng lực thực tế:\n"
            "- Khả năng giải quyết vấn đề thực tế (44,6% doanh nghiệp coi là tiêu chí hàng đầu).\n"
            "- Khả năng thích nghi và học công nghệ mới (43,4%).\n"
            "- Tính chủ động và tinh thần trách nhiệm ownership (39,8%).\n\n"
            "Khi các công cụ AI và tự động hóa đã xử lý tốt các tác vụ lập trình cơ bản, doanh nghiệp cần nhân sự có tư duy hệ thống và năng lực giải quyết bài toán nghiệp vụ phức tạp."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "itviec_criteria", "value": "Giải quyết vấn đề (44.6%), Thích nghi (43.4%), Ownership (39.8%)", "source": "INDUSTRY_EVIDENCE (IT_CongNghe.docx - ITviec)"}
            ],
            "analysis": "Thị trường IT trưởng thành đòi hỏi kỹ sư công nghệ có chiều sâu kiến thức và tư duy sản phẩm.",
            "recommendations": ["Xây dựng các dự án thực tế chứng minh năng lực giải quyết vấn đề trọn vẹn."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Yêu cầu kỹ năng phản ánh mẫu khảo sát 1.839 chuyên gia và doanh nghiệp trên ITviec."]
        }

    # Câu 13: Có phải tất cả công ty Logistics đều tuyển nhiều người?
    if ("logistics" in q_low or "xnk" in q_low) and any(k in q_low for k in ["tất cả công ty logistics", "có phải tất cả", "tuyển ồ ạt", "tuyển nhiều người"]):
        answer = (
            "Không. Khảo sát ManpowerGroup Q2/2026 từng ghi nhận kế hoạch nhân sự trong nhóm Trade & Logistics khá phân hóa (42% tăng và 42% giảm). "
            "Mặc dù bước sang Q3/2026 triển vọng tuyển dụng phục hồi mạnh mẽ (+26 điểm phần trăm), nhu cầu tuyển dụng vẫn phân hóa sâu sắc:\n"
            "- Khoảng 95% doanh nghiệp logistics Việt Nam là doanh nghiệp vừa và nhỏ, chủ yếu cung cấp dịch vụ kho bãi đơn lẻ hoặc vận tải nội địa với quy mô nhân sự hạn chế.\n"
            "- Nhu cầu tuyển mở rộng tập trung nhiều hơn ở nhóm doanh nghiệp logistics tích hợp (3PL–4PL), doanh nghiệp FDI và các trung tâm kho vận hiện đại.\n\n"
            "Vì vậy, không đủ căn cứ để khẳng định toàn bộ các công ty trong ngành logistics đều đang mở rộng nhân sự đồng loạt."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "manpower_q2_q3", "value": "Q2 phân hóa 42/42; Q3 phục hồi +26 điểm %", "source": "INDUSTRY_EVIDENCE (Logistics_XNK_FINAL_HOAN_CHINH.docx - ManpowerGroup)"},
                {"metric": "sme_logistics_ratio", "value": "95% DN vừa và nhỏ", "source": "INDUSTRY_EVIDENCE (Báo cáo Logistics Việt Nam 2025)"}
            ],
            "analysis": "Cơ hội tuyển dụng logistics có thật và đang mở rộng, nhưng mức độ tuyển dụng phân hóa theo quy mô và mô hình dịch vụ của từng doanh nghiệp.",
            "recommendations": ["Tìm kiếm cơ hội tại các doanh nghiệp logistics tích hợp và chuỗi cung ứng lạnh."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Khảo sát ManpowerGroup không công bố tỷ lệ tuyển dụng cho từng doanh nghiệp cụ thể."]
        }

    # Câu 14: Vì sao ngành tài chính vẫn phát triển nhưng tăng nhân sự chậm?
    if ("tài chính" in q_low or "ngân hàng" in q_low or "kinh tế" in q_low) and any(k in q_low for k in ["vẫn phát triển nhưng", "tăng nhân sự chậm", "tài sản tăng nhưng nhân sự", "tại sao nhân sự chậm"]):
        answer = (
            "Tài liệu nghiên cứu của Học viện Ngân hàng trên mẫu 28 ngân hàng thương mại Việt Nam giai đoạn 2020–2025 cung cấp bằng chứng rõ ràng cho hiện tượng này:\n"
            "- Tổng tài sản tăng trung vị 117%, nhưng quy mô nhân sự chỉ tăng 11%.\n"
            "- Tài sản bình quân trên mỗi nhân viên tăng tới 98% (đến cuối 2025, mẫu nghiên cứu sử dụng khoảng 318.000 lao động).\n\n"
            "Điều này cho thấy các định chế tài chính đang chuyển mạnh sang mô hình tăng trưởng dựa trên năng suất, tự động hóa quy trình giao dịch, "
            "ứng dụng ngân hàng số và AI. Tăng trưởng hoạt động kinh doanh vì thế không nhất thiết phải đi kèm với việc mở rộng biên chế lao động số lượng lớn."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "bank_productivity_gap", "value": "Tài sản +117% vs Nhân viên +11% (Tài sản/NV +98%)", "source": "INDUSTRY_EVIDENCE (KinhTe_TaiChinh_Final.docx - Học viện Ngân hàng)"}
            ],
            "analysis": "Ngành tài chính minh chứng cho xu hướng chuyển dịch thâm dụng công nghệ và năng suất thay vì thâm dụng lao động phổ thông.",
            "recommendations": ["Trang bị tư duy phân tích rủi ro và kỹ năng tài chính công nghệ để gia nhập nhóm nhân sự chất lượng cao."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Nghiên cứu thực hiện trên mẫu 28 ngân hàng thương mại, không đại diện cho toàn bộ các công ty chứng khoán, bảo hiểm nhỏ."]
        }

    # Câu 15: Xu hướng này là dữ liệu thực hay dự báo?
    if any(k in q_low for k in ["dữ liệu thực hay dự báo", "thực tế hay dự báo", "số liệu thực hay", "dự báo hay thực"]):
        answer = (
            "Cần phân biệt rõ hai giai đoạn trên hệ thống Skill Lens Lab:\n"
            "1. Dữ liệu giai đoạn 2025–2026: Là số liệu được hệ thống tổng hợp từ các tin tuyển dụng thu thập thực tế tại TP. Cần Thơ & ĐBSCL (tổng cộng 1.000 tin năm 2025 và 1.078 tin năm 2026) kết hợp bằng chứng đối chiếu từ các báo cáo chính thống.\n"
            "2. Dữ liệu giai đoạn 2026–2027: Được xác định riêng là DỰ BÁO (Forecast) dựa trên mô hình chuỗi thời gian ARIMA và mục tiêu quy hoạch phát triển kinh tế vùng.\n\n"
            "Do đó, các số liệu 2025–2026 là dữ liệu quan sát trong bộ mẫu, còn các mốc 2027 là kịch bản dự phóng tham khảo, không phải thống kê thực tế đã diễn ra."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "period_2025_2026", "value": "Dữ liệu quan sát mẫu (1.000 -> 1.078 tin)", "source": "SHIFT_CHART_2025_2026"},
                {"metric": "period_2026_2027", "value": "Mô hình dự báo (Forecast)", "source": "FORECAST_ARIMA"}
            ],
            "analysis": "Minh bạch tuyệt đối giữa dữ liệu quan sát lịch sử và kết quả mô hình dự báo tương lai.",
            "recommendations": ["Sử dụng số liệu 2027 cho mục đích định hướng dài hạn, không dùng làm căn cứ thống kê hiện tại."],
            "chart_refs": ["Đường Đi Chuyển Dịch Nhu Cầu Việc Làm (2023–2027)"],
            "limitations": ["Dự báo phụ thuộc vào các giả định ổn định kinh tế vĩ mô."]
        }

    # Câu 16: Kết luận này có chứng minh AI làm giảm việc làm kế toán không?
    if any(k in q_low for k in ["nguyên nhân duy nhất", "chứng minh ai làm giảm việc làm", "chứng minh ai gây ra", "ai làm giảm việc làm", "khẳng định ai"]):
        answer = (
            "Chưa thể khẳng định quan hệ nhân quả trực tiếp chỉ bằng biến động số tin tuyển dụng trên biểu đồ. "
            "Hệ thống không khẳng định AI là nguyên nhân duy nhất làm giảm việc làm kế toán.\n\n"
            "Biểu đồ ghi nhận số tin tuyển dụng nhóm Kinh tế & Tài chính giảm từ 270 xuống 156 tin (-42,2%), "
            "và tài liệu ngành cung cấp bằng chứng về xu hướng tự động hóa tác vụ lặp lại cũng như chuyển dịch nhu cầu kỹ năng. "
            "Tuy nhiên, sự suy giảm số tin tuyển dụng còn có thể chịu tác động từ chu kỳ kinh doanh, tái cấu trúc bộ máy, sáp nhập chi nhánh ngân hàng "
            "và chính sách tuyển dụng thắt chặt. Cần có dữ liệu điều tra chuyên biệt để lượng hóa chính xác tỷ lệ đóng góp của AI vào mức giảm việc làm này."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "finance_drop", "value": "-42.2%", "source": "SHIFT_CHART_2025_2026"},
                {"metric": "causal_link", "value": "Chưa đủ dữ liệu khẳng định quan hệ nhân quả duy nhất", "source": "SYSTEM_LIMITATION_RULE"}
            ],
            "analysis": "AI là một yếu tố giải thích có cơ sở khoa học nhưng không thể kết luận là nguyên nhân duy nhất.",
            "recommendations": ["Cần nhìn nhận đa chiều giữa chuyển đổi công nghệ và tái cấu trúc mô hình kinh doanh."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Chưa có dữ liệu kiểm định nhân quả độc lập về mức độ thay thế của AI tại Cần Thơ."]
        }

    # Câu hỏi về phạm vi địa lý: 4 tài liệu ngành có phải số liệu riêng của Cần Thơ không?
    if any(k in q_low for k in ["riêng của tp. cần thơ", "riêng của cần thơ", "riêng cần thơ", "4 tài liệu ngành có phải", "tài liệu ngành có phải", "phạm vi 4 tài liệu"]):
        answer = (
            "Không. Bốn tài liệu ngành cung cấp bằng chứng bối cảnh chủ yếu trên phạm vi toàn quốc (Việt Nam) và các trung tâm kinh tế lớn (Hà Nội, TP.HCM), "
            "được sử dụng để giải thích nguyên nhân kinh tế, động lực công nghệ và xu hướng chung của thị trường.\n\n"
            "Trong khi đó, biểu đồ chuyển dịch 2025–2026 có phạm vi địa lý riêng là TP. Cần Thơ & Đồng bằng Sông Cửu Long (1.000 tin năm 2025 và 1.078 tin năm 2026). "
            "Hệ thống sử dụng tài liệu ngành để bổ trợ nhận định bối cảnh, tuyệt đối không tự động coi dữ liệu toàn quốc là số liệu thống kê hành chính trực tiếp cho Cần Thơ."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "chart_scope", "value": "TP. Cần Thơ & ĐBSCL (1.000 -> 1.078 tin)", "source": "SHIFT_CHART_2025_2026"},
                {"metric": "doc_scope", "value": "Toàn quốc (Việt Nam) & Chuyên ngành", "source": "4_INDUSTRY_DOCS"}
            ],
            "analysis": "Tách bạch rõ ràng giữa phạm vi khảo sát biểu đồ khu vực và tài liệu bằng chứng bối cảnh vĩ mô toàn quốc.",
            "recommendations": ["Luôn lưu ý phạm vi địa lý khi diễn giải số liệu tuyển dụng."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Tài liệu ngành phản ánh mẫu khảo sát quy mô quốc gia, không phải số liệu thống kê riêng của UBND TP. Cần Thơ."]
        }

    # Câu hỏi: Ngành Nông nghiệp công nghệ cao tăng 73,3%, con số này có ý nghĩa gì?
    if ("nông nghiệp" in q_low or "agri" in q_low or "73,3" in q_low or "73.3" in q_low) and any(k in q_low for k in ["ý nghĩa", "con số này có ý nghĩa gì", "73,3% có ý nghĩa gì", "73.3% có ý nghĩa gì"]):
        answer = (
            "Trong biểu đồ 2025–2026, Nông nghiệp công nghệ cao tăng từ 45 lên 78 tin (+73,3%, tương ứng tăng thêm 33 tin tuyển dụng). "
            "Con số này mang hai ý nghĩa phân tích quan trọng:\n"
            "1. Về tốc độ tăng trưởng: Đây là ngành có tốc độ tăng trưởng phần trăm nhanh nhất (+73,3%) trong năm ngành, phản ánh đà chuyển đổi mạnh mẽ sang nông nghiệp số, "
            "đề án 1 triệu ha lúa chất lượng cao và ứng dụng thiết bị bay không người lái (drone), cảm biến IoT tại vùng ĐBSCL.\n"
            "2. Về quy mô tuyển dụng thực tế: Mặc dù tăng trưởng nhanh về tỷ lệ, quy mô việc làm tuyệt đối vẫn ở mức nhỏ (chiếm 7,2% tỷ trọng chuẩn hóa năm 2026 với 78 tin).\n\n"
            "Vì vậy, Nông nghiệp CNC là điểm sáng tiềm năng bứt phá nhưng chưa phải là ngành có số việc làm áp đảo trên thị trường."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "agri_growth_rate", "value": "+73.3% (45 -> 78 tin)", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"},
                {"metric": "agri_audited_share_2026", "value": "7.2% (78 / 1.078 tin)", "source": "SHIFT_CHART_2025_2026"}
            ],
            "analysis": "Phân biệt rõ ràng giữa tốc độ tăng trưởng tỷ lệ phần trăm cao và quy mô tuyệt đối còn khiêm tốn.",
            "recommendations": ["Cần đẩy mạnh liên kết doanh nghiệp nông nghiệp số với các trường đại học vùng ĐBSCL."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động", "So Sánh Cơ Cấu Tỷ Trọng (2025 vs 2026)"],
            "limitations": ["Dữ liệu nông nghiệp CNC dựa hoàn toàn trên số tin biểu đồ; không tự tạo tài liệu chứng minh chưa có."]
        }

    # ──────────────────────────────────────────────────────────────────────────
    # ƯU TIÊN 2: CÂU HỎI TỔNG THỂ (EXPLAIN_LABOR_MARKET_SHIFT)
    # ──────────────────────────────────────────────────────────────────────────
    if intent_info["intent"] == "EXPLAIN_LABOR_MARKET_SHIFT":
        answer = (
            "Hệ thống đưa ra nhận định này vì số tin tuyển dụng trong bộ dữ liệu biểu đồ giai đoạn 2025–2026 tại TP. Cần Thơ & ĐBSCL "
            "có sự thay đổi rõ rệt giữa các ngành:\n"
            "- IT & Công nghệ tăng từ 285 lên 385 tin (+35,1%, tỷ trọng chuẩn hóa tăng từ 28,5% lên 35,7%).\n"
            "- Logistics & XNK tăng từ 190 lên 241 tin (+26,8%, tỷ trọng chuẩn hóa tăng từ 19,0% lên 22,4%).\n"
            "- Kinh tế & Tài chính giảm từ 270 xuống 156 tin (-42,2%, tỷ trọng chuẩn hóa sụt giảm từ 27,0% xuống 14,5%).\n"
            "- Du lịch & Khách sạn tăng nhẹ từ 210 lên 218 tin (+3,8%, tỷ trọng chuẩn hóa giữ mức 20,2%).\n"
            "- Nông nghiệp công nghệ cao tăng từ 45 lên 78 tin (+73,3%, tỷ trọng chuẩn hóa tăng từ 4,5% lên 7,2%), dù quy mô tuyển dụng còn nhỏ.\n\n"
            "Xu hướng này phù hợp với những bằng chứng bổ trợ trong 4 tài liệu ngành chính thức: nhu cầu phát triển công nghệ số và ứng dụng AI (khảo sát ITviec), "
            "mở rộng hoạt động thương mại – xuất nhập khẩu đạt trên 1.000 tỷ USD kéo theo nhu cầu logistics (Bộ Công Thương, ManpowerGroup), "
            "và quá trình tái cấu trúc nâng cao năng suất bằng tự động hóa trong nhóm tài chính – ngân hàng (nghiên cứu Học viện Ngân hàng).\n\n"
            "Tuy nhiên, đây là biến động số tin tuyển dụng trong bộ dữ liệu được phân tích (1.000 tin năm 2025 và 1.078 tin năm 2026), "
            "chưa đủ để kết luận toàn bộ thị trường lao động Cần Thơ thay đổi với đúng các tỷ lệ đó. Tác động của AI và chuyển đổi số là một cách giải thích "
            "có cơ sở tham khảo thực tiễn, nhưng cần thêm bằng chứng thống kê chuyên biệt để khẳng định quan hệ nguyên nhân trực tiếp."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "it_shift", "value": "+35.1% (285 -> 385)", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"},
                {"metric": "logistics_shift", "value": "+26.8% (190 -> 241)", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"},
                {"metric": "finance_shift", "value": "-42.2% (270 -> 156)", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"},
                {"metric": "tourism_shift", "value": "+3.8% (210 -> 218)", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"},
                {"metric": "agri_shift", "value": "+73.3% (45 -> 78)", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"}
            ],
            "analysis": "Chuyển dịch trọng tâm từ kế toán truyền thống sang kinh tế số, logistics và nông nghiệp công nghệ cao.",
            "recommendations": ["Theo dõi biến động cung cầu nhân lực theo từng quý để kịp thời điều chỉnh chuẩn đào tạo."],
            "chart_refs": [
                "Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động",
                "So Sánh Cơ Cấu Tỷ Trọng (2025 vs 2026)",
                "Đường Đi Chuyển Dịch Nhu Cầu Việc Làm (2023–2027)"
            ],
            "limitations": [
                "Bốn tài liệu ngành cung cấp bằng chứng bối cảnh toàn quốc, không đồng nhất tuyệt đối với thống kê hành chính riêng tại Cần Thơ.",
                "Tổng số tin năm 2026 là 1.078 tin; tỷ trọng chuẩn hóa đã được tính toán lại theo đúng mẫu số này."
            ]
        }

    # ──────────────────────────────────────────────────────────────────────────
    # ƯU TIÊN 3: CÂU HỎI TRỰC TIẾP RIÊNG TỪNG NGÀNH (IT / LOGISTICS / KINH TẾ / DU LỊCH / NÔNG NGHIỆP)
    # ──────────────────────────────────────────────────────────────────────────
    if ind == "IT":
        if lvl == 1:
            answer = "Trong biểu đồ 2025–2026, số tin IT tăng 35.1% (35,1%), tương đương tăng từ 285 lên 385 tin (tăng thêm 100 tin tuyển dụng)."
        else:
            answer = (
                "Trong biểu đồ chuyển dịch 2025–2026, số tin IT tăng từ 285 lên 385 tin, tăng thêm 100 tin tuyển dụng, tương đương tăng 35.1% (35,1%) "
                "(tỷ trọng chuẩn hóa tăng từ 28.5% lên 35.7%, tức tăng +7.2 điểm % thị phần).\n\n"
                "Tài liệu ITviec 2025–2026 bổ trợ cho xu hướng này khi ghi nhận 66,1% doanh nghiệp mở rộng nhân sự IT năm 2025 "
                "và 69,6% có kế hoạch mở rộng năm 2026, cùng với 73% doanh nghiệp đang ứng dụng AI và 65,1% tăng ngân sách cho AI. "
                "Nhu cầu tuyển dụng chuyển trọng tâm sang chất lượng, năng lực giải quyết vấn đề và các vị trí kỹ thuật cốt lõi (Back-end, Full-stack, Front-end).\n\n"
                "Tuy nhiên, số liệu khảo sát của ITviec được thực hiện trên phạm vi toàn quốc (chủ yếu tại TP.HCM và Hà Nội), "
                "chỉ đóng vai trò bằng chứng bối cảnh hỗ trợ, không trực tiếp chứng minh quan hệ nhân quả cho biến động riêng tại TP. Cần Thơ."
            )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "it_chart_growth", "value": "35.1%", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"},
                {"metric": "itviec_expansion_2026", "value": "69.6%", "source": "INDUSTRY_EVIDENCE (IT_CongNghe.docx - Khảo sát ITviec)"}
            ],
            "analysis": "Ngành IT dẫn đầu về số lượng tin tuyển dụng tăng thêm (+100 tin), phù hợp với làn sóng chuyển đổi số và đầu tư AI.",
            "recommendations": ["Tập trung phát triển kỹ năng Back-end, Full-stack, Python và năng lực ứng dụng AI thực tế."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động", "So Sánh Cơ Cấu Tỷ Trọng (2025 vs 2026)"],
            "limitations": ["Khảo sát ITviec là dữ liệu toàn quốc, không phải thống kê hành chính riêng tại Cần Thơ."]
        }

    if ind == "Logistics":
        if lvl == 1:
            answer = "26,8%, tương đương tăng từ 190 lên 241 tin trong biểu đồ 2025–2026 (tăng thêm 51 tin tuyển dụng)."
        else:
            answer = (
                "Số tin Logistics tăng từ 190 lên 241 tin trong bộ dữ liệu biểu đồ 2025–2026, tương đương tăng 26,8% "
                "(tỷ trọng chuẩn hóa tăng từ 19,0% lên 22,4%, tức tăng +3,4 điểm % thị phần).\n\n"
                "Sự gia tăng này phù hợp với bối cảnh thương mại xuất nhập khẩu mở rộng (kim ngạch XNK 10 tháng năm 2026 đạt 1.010,6 tỷ USD theo Bộ Công Thương) "
                "và triển vọng tuyển dụng Trade & Logistics phục hồi mạnh mẽ trong khảo sát ManpowerGroup Q3/2026 (tăng 26 điểm phần trăm so với quý trước). "
                "Trong nhóm doanh nghiệp có kế hoạch tăng nhân sự, 61% nêu lý do mở rộng hoạt động kinh doanh.\n\n"
                "Đây là bằng chứng hỗ trợ xu hướng tăng trưởng của ngành, không phải chứng minh nhân quả trực tiếp cho mọi vị trí việc làm."
            )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "logistics_chart_growth", "value": "26.8%", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"},
                {"metric": "xnk_10m_2026", "value": "1010.6 tỷ USD", "source": "INDUSTRY_EVIDENCE (Logistics_XNK_FINAL_HOAN_CHINH.docx - Bộ Công Thương)"}
            ],
            "analysis": "Logistics tăng trưởng mạnh theo sau đà bứt phá của hoạt động thương mại và xuất nhập khẩu nông thủy sản vùng ĐBSCL.",
            "recommendations": ["Bổ sung chứng chỉ nghiệp vụ XNK, kỹ năng sử dụng phần mềm WMS/TMS/ERP và tiếng Anh thương mại."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Kim ngạch XNK là giá trị hàng hóa, không đồng nhất tuyệt đối với doanh thu dịch vụ logistics hay số việc làm."]
        }

    if ind == "Kinh tế":
        if lvl == 1:
            answer = "Trong biểu đồ 2025–2026, số tin Kinh tế & Tài chính giảm 42,2%, tương đương giảm từ 270 xuống 156 tin (giảm 114 tin)."
        else:
            answer = (
                "Trong biểu đồ chuyển dịch 2025–2026, số tin tuyển dụng nhóm Kinh tế & Tài chính giảm từ 270 xuống 156 tin, "
                "tương đương mức giảm 42,2% (tỷ trọng chuẩn hóa sụt giảm từ 27,0% xuống 14,5%, tức giảm -12,5 điểm % thị phần).\n\n"
                "Một cách giải thích phù hợp với tài liệu ngành là các công việc lặp lại (nhập liệu, kế toán cơ bản, giao dịch thủ công) "
                "đang chịu áp lực tự động hóa từ AI, RPA và Core Banking số. Đồng thời, nghiên cứu của Học viện Ngân hàng trên 28 ngân hàng "
                "cho thấy tổng tài sản tăng trung vị 117% nhưng nhân sự chỉ tăng 11%, phản ánh xu hướng ưu tiên nâng cao năng suất và hiệu quả sử dụng lao động.\n\n"
                "Tuy nhiên, đây là biến động trong bộ dữ liệu được phân tích, chưa đủ dữ liệu để khẳng định AI là nguyên nhân duy nhất gây ra toàn bộ mức giảm này."
            )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [
                {"metric": "finance_chart_decline", "value": "-42.2%", "source": "SHIFT_CHART_2025_2026 (Cần Thơ & ĐBSCL)"},
                {"metric": "bank_assets_vs_workforce", "value": "Tài sản +117% vs Nhân sự +11%", "source": "INDUSTRY_EVIDENCE (KinhTe_TaiChinh_Final.docx - Học viện Ngân hàng)"}
            ],
            "analysis": "Sụt giảm số tin tuyển dụng kế toán và hành chính truyền thống do số hóa quy trình, nhưng vị trí chuyên môn sâu vẫn được tuyển dụng có chọn lọc.",
            "recommendations": ["Nâng cấp từ nghiệp vụ kế toán thủ công sang phân tích tài chính số, quản trị dữ liệu và kiểm soát rủi ro."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Mức giảm số tin trong mẫu không đại diện cho việc toàn bộ ngành tài chính bị cắt giảm nhân sự."]
        }

    if ind == "Du lịch":
        if lvl == 1:
            answer = "Trong biểu đồ 2025–2026, số tin Du lịch & Khách sạn tăng 3,8%, từ 210 lên 218 tin (tăng thêm 8 tin tuyển dụng)."
        else:
            answer = (
                "Số tin tuyển dụng du lịch trong biểu đồ 2025–2026 tăng từ 210 lên 218 tin (+3,8%). "
                "Mức tăng nhẹ này phản ánh thực tế doanh nghiệp chủ yếu tuyển bù chỗ trống và điều chỉnh nhân sự theo mùa vụ "
                "thay vì mở rộng biên chế ồ ạt, dù lượng khách du lịch toàn quốc tăng trưởng rất mạnh."
            )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [{"metric": "tourism_postings", "value": "+3.8% (+8 tin)", "source": "SHIFT_CHART_2025_2026"}],
            "analysis": "Ngành du lịch duy trì mức tăng trưởng việc làm ổn định và tập trung vào chất lượng dịch vụ.",
            "recommendations": ["Nâng cao trình độ ngoại ngữ và kỹ năng chăm sóc khách hàng chuyên nghiệp."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Doanh nghiệp sử dụng nhiều lao động thời vụ."]
        }

    if ind == "Nông nghiệp":
        answer = (
            "Trong biểu đồ 2025–2026, Nông nghiệp công nghệ cao tăng từ 45 lên 78 tin (+73,3%, tăng 33 tin). "
            "Đây là ngành có tốc độ tăng trưởng phần trăm nhanh nhất trong biểu đồ, gắn liền với các đề án phát triển "
            "nông nghiệp chất lượng cao, drone gieo sạ và cảm biến IoT tại vùng ĐBSCL. "
            "Tuy nhiên, quy mô việc làm của ngành hiện tại vẫn ở mức nhỏ (chiếm 7,2% thị phần tuyển dụng)."
        )
        return {
            "answer": answer,
            "data_status": "verified",
            "evidence": [{"metric": "agri_postings", "value": "+73.3% (+33 tin)", "source": "SHIFT_CHART_2025_2026"}],
            "analysis": "Nông nghiệp CNC là điểm sáng tiềm năng bứt phá của ĐBSCL.",
            "recommendations": ["Đào tạo kỹ sư nông nghiệp số và vận hành thiết bị IoT thông minh."],
            "chart_refs": ["Bảng Chi Tiết Mức Độ Dịch Chuyển & Nguyên Nhân Tác Động"],
            "limitations": ["Chỉ sử dụng dữ liệu biểu đồ; không tự tạo tài liệu chứng minh chưa có."]
        }

    return None
