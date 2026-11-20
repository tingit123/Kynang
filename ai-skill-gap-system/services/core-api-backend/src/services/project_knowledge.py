"""
Project Knowledge Base & Intent Classification Engine
Dành riêng cho nền tảng Skill Lens Lab (SkillLed LAB / SkillGap AI)
Cung cấp nguồn tri thức chuẩn xác, có thẩm quyền từ mã nguồn và tài liệu hệ thống.
Hỗ trợ RAG (Retrieval-Augmented Generation), phân loại ý định và giải quyết câu hỏi tiếp nối.
Tích hợp trích xuất 100% tài liệu 'So_Lieu_Bieu_do.docx' (30 trang).
"""
import re
from src.services.insight_trends import trend_kind, prior_turns
from typing import List, Dict, Any, Optional

PROJECT_KNOWLEDGE_DOCUMENTS = [
    {
        "doc_id": "KB_OVERVIEW_001",
        "title": "Tổng quan và Mục tiêu của Skill Lens Lab",
        "category": "PROJECT_OVERVIEW",
        "access_scope": "public",
        "relevant_roles": ["all", "admin", "worker", "employer", "course_provider", "guest"],
        "content": (
            "Skill Lens Lab (còn được gọi là SkillGap AI / SkillLed LAB) là hệ thống AI phân tích và phát hiện khoảng cách kỹ năng "
            "lao động (Skill Gap), được xây dựng chuyên biệt nhằm giải quyết bài toán lệch pha cung - cầu nhân lực "
            "tại TP. Cần Thơ, khu vực Đồng bằng Sông Cửu Long (ĐBSCL) và mở rộng phạm vi toàn quốc.\n"
            "Mục tiêu cốt lõi của dự án:\n"
            "1. Tự động thu thập và phân tích dữ liệu việc làm thực tế từ các nguồn tuyển dụng uy tín (hơn 1.000 tin tuyển dụng TopCV) "
            "kết hợp dữ liệu khảo sát hơn 500 sinh viên/người lao động.\n"
            "2. Sử dụng mô hình AI/NLP để chuẩn hóa danh mục kỹ năng theo chuẩn phân loại ESCO trên các nhóm ngành trọng điểm: "
            "Công nghệ thông tin (IT), Du lịch & Khách sạn, Logistics & Chuỗi cung ứng, Kinh tế & Tài chính, và Nông nghiệp Công nghệ cao.\n"
            "3. Đo lường chính xác khoảng cách cung - cầu (Skill Gap) bằng công thức chuẩn hóa Gap = Demand - Supply (tính bằng điểm phần trăm).\n"
            "4. Đóng vai trò cầu nối thông minh: hỗ trợ người lao động chẩn đoán thiếu sót kỹ năng để kê đơn khóa học bù đắp, "
            "hỗ trợ nhà tuyển dụng tiếp cận đúng nhân tài, và giúp cơ sở đào tạo điều chỉnh chuẩn đầu ra bám sát thị trường."
        )
    },
    {
        "doc_id": "KB_USERS_002",
        "title": "Đối tượng sử dụng và Phân quyền Vai trò (RBAC)",
        "category": "USER_ROLES",
        "access_scope": "public",
        "relevant_roles": ["all", "admin", "worker", "employer", "course_provider", "guest"],
        "content": (
            "Hệ thống Skill Lens Lab phục vụ 4 nhóm đối tượng chính với phân quyền chặt chẽ:\n"
            "1. Người lao động / Sinh viên / Ứng viên (Role: 'worker' hoặc 'candidate'): Xem Dashboard thị trường, "
            "tra cứu kỹ năng mềm và kỹ năng ngành, sử dụng công cụ Phân tích CV bằng AI để tự chẩn đoán lỗ hổng kỹ năng, "
            "nhận lộ trình khóa học đề xuất và tìm kiếm việc làm phù hợp.\n"
            "2. Nhà tuyển dụng (Role: 'employer'): Đăng tin tuyển dụng, quản lý hồ sơ ứng viên nộp vào, "
            "theo dõi xu hướng và chỉ số kỹ năng thị trường để xây dựng tiêu chuẩn tuyển dụng chuẩn xác.\n"
            "3. Đơn vị đào tạo (Role: 'course_provider' hoặc 'provider'): Đăng tải khóa học, quản lý danh mục chương trình "
            "bồi dưỡng kỹ năng, liên kết chuẩn đầu ra với các kỹ năng thiếu hụt thực tế trên thị trường.\n"
            "4. Quản trị viên (Role: 'admin'): Toàn quyền quản trị tài khoản, phê duyệt đối tác nhà tuyển dụng và đơn vị đào tạo, "
            "giám sát an toàn bảo mật, cấu hình hệ thống và kiểm duyệt dữ liệu."
        )
    },
    {
        "doc_id": "KB_FEATURES_003",
        "title": "Các chức năng chính và Luồng hoạt động của Website",
        "category": "SYSTEM_FEATURES",
        "access_scope": "public",
        "relevant_roles": ["all", "admin", "worker", "employer", "course_provider", "guest"],
        "content": (
            "Các phân hệ chức năng chính trên giao diện Skill Lens Lab:\n"
            "1. Cổng Đăng nhập / Đăng ký (Auth Web - Cổng 8081): Xác thực JWT bảo mật qua Cookie HttpOnly, hỗ trợ đăng ký cho Ứng viên, Doanh nghiệp và Đối tác đào tạo.\n"
            "2. Dashboard Tổng quan (Dashboard Overview - Cổng 8080): Hiển thị KPI toàn hệ thống (tin tuyển dụng, hồ sơ khảo sát, Gap trung bình), "
            "biểu đồ Top 5 kỹ năng thiếu hụt nhiều nhất, biểu đồ phân bố ngành nghề, bản đồ địa bàn toàn quốc và bộ lọc đa chiều (Ngành, Địa bàn, Quý/Năm).\n"
            "3. Chức năng Chẩn đoán & Lộ trình (Hồ Sơ Năng Lực & Mục Tiêu Nghề Nghiệp): Khung chuẩn 20 chức vụ Cần Thơ & ĐBSCL, nạp nhanh 1 trong 500 sinh viên mẫu trong CSDL, "
            "chẩn đoán ma trận kỹ năng tương tác, phân biệt kỹ năng Bắt buộc (Mandatory) và Bổ trợ (Nice-to-have), AI tính toán Gap và tự động kê đơn khóa học bù đắp.\n"
            "4. Chức năng Phân tích CV bằng AI (Phân Tích CV & Kê Đơn Lộ Trình Học bằng Gemini AI): Công nghệ Google Gemini AI Powered đa phương thức (Multimodal Input: file PDF, DOCX, TXT; "
            "ảnh chụp CV PNG, JPG, WEBP hoặc bấm Ctrl+V dán ảnh màn hình qua OCR; dán trực tiếp đoạn văn bản thô). Xử lý thông minh 3 bước: Trích xuất tự động (Semantic Reading) -> "
            "Đối sánh sâu (Gap Analysis) với cơ sở dữ liệu hàng ngàn JD doanh nghiệp Cần Thơ & ĐBSCL -> Kê đơn lộ trình học cá nhân hóa theo tuần/tháng với các khóa học cụ thể.\n"
            "5. Khám phá Ngành nghề (Industry Exploration): Khảo sát 5 ngành trọng điểm (IT, Du lịch, Logistics, Kinh tế, Nông nghiệp CNC), cung cấp quy mô tin tuyển dụng, mức lương trung bình, và bảng xếp hạng kỹ năng thiếu hụt theo Gap.\n"
            "6. Khóa học LMS Studio: Học viện kỹ năng AI thực chiến với 3 trụ cột đào tạo (Free 0đ, Thực chiến có code thật, Chuyên sâu Pro), tích hợp phòng học LMS Studio, Lab console chạy code, trắc nghiệm Quiz, và AI Trợ giảng.\n"
            "7. Trợ lý AI Chatbox: Nút bong bóng chat nổi ở góc phải màn hình, hỗ trợ giải đáp 24/7 về dự án, hướng dẫn sử dụng và phân tích dữ liệu chuyên sâu."
        )
    },
    {
        "doc_id": "KB_GUIDE_004",
        "title": "Hướng dẫn sử dụng chi tiết từng chức năng cho Người dùng",
        "category": "USER_GUIDE",
        "access_scope": "public",
        "relevant_roles": ["all", "admin", "worker", "employer", "course_provider", "guest"],
        "content": (
            "Hướng dẫn thao tác sử dụng hệ thống Skill Lens Lab:\n"
            "1. Cách đăng ký / đăng nhập: Truy cập cổng Auth tại http://localhost:8081 hoặc bấm nút 'Đăng nhập / Đăng ký' ở góc trên thanh công cụ Dashboard. "
            "Chọn vai trò phù hợp (Ứng viên, Doanh nghiệp hoặc Đơn vị đào tạo) và điền thông tin.\n"
            "2. Cách sử dụng Chẩn đoán & Lộ trình: Truy cập tab 'Chẩn đoán & Lộ trình' trên thanh điều hướng. Chọn ngành nghề mong muốn -> Chọn chức vụ mục tiêu -> "
            "Tích chọn kỹ năng đã có hoặc chọn nhanh 1 trong 500 hồ sơ sinh viên mẫu trong CSDL -> Bấm '🚀 AI CHẨN ĐOÁN & KÊ ĐƠN KHÓA HỌC'.\n"
            "3. Cách sử dụng Phân tích CV bằng AI: Truy cập tab 'Phân tích CV (AI)' trên thanh điều hướng. Kéo thả file CV (PDF, DOCX, TXT) hoặc tải ảnh chụp CV (PNG, JPG, WEBP) "
            "hoặc bấm Ctrl+V để dán trực tiếp ảnh màn hình (hệ thống tự chạy OCR nhận diện văn bản) hoặc dán văn bản thô -> Bấm '✨ AI Phân Tích CV' để nhận điểm phù hợp (Match Score %), phân tích điểm mạnh - điểm yếu và lộ trình khóa học.\n"
            "4. Cách xem phân tích kỹ năng và xu hướng: Dùng các bộ lọc Ngành nghề, Địa bàn (Cần Thơ, TP.HCM, Hà Nội, Toàn quốc) và Kỳ báo cáo ở đầu trang Dashboard.\n"
            "5. Cách mở AI Chatbox: Bấm vào biểu tượng hình tròn nổi 'AI Chatbox' màu xanh teal ở góc dưới cùng bên phải màn hình để đặt câu hỏi trực tiếp."
        )
    },
    {
        "doc_id": "KB_FORMULAS_005",
        "title": "Định nghĩa Nghiệp vụ và Công thức Tính toán Chỉ số",
        "category": "ANALYTICS_LOGIC",
        "access_scope": "public",
        "relevant_roles": ["all", "admin", "worker", "employer", "course_provider", "guest"],
        "content": (
            "Định nghĩa chuẩn hóa và công thức tính toán của Skill Lens Lab:\n"
            "1. JD (Job Description): Tin tuyển dụng do doanh nghiệp công bố, thể hiện Nhu cầu tuyển dụng của thị trường.\n"
            "2. CV (Curriculum Vitae) / Khảo sát sinh viên: Hồ sơ năng lực đo lường Nguồn cung lao động thực tế.\n"
            "3. Nhu cầu tuyển dụng (Demand %): Tỷ lệ phần trăm số tin tuyển dụng yêu cầu kỹ năng đó trên tổng số tin tuyển dụng trong ngành. "
            "Công thức: Demand (%) = (Số JD yêu cầu skill / Tổng JD ngành) * 100%.\n"
            "4. Nguồn cung lao động (Supply %): Tỷ lệ phần trăm người lao động/sinh viên đạt chuẩn kỹ năng đó. "
            "Công thức: Supply (%) = (Số ứng viên đạt chuẩn skill / Tổng ứng viên ngành) * 100%.\n"
            "5. Khoảng cách kỹ năng (Skill Gap % / điểm phần trăm): Chênh lệch giữa nhu cầu và nguồn cung. "
            "Công thức chuẩn: Skill Gap = Demand (%) - Supply (%).\n"
            "- Khi Demand và Supply tính bằng %, chênh lệch Skill Gap được diễn đạt chuẩn là điểm phần trăm (điểm %).\n"
            "- Gap dương (> 0): Tình trạng thiếu hụt kỹ năng (doanh nghiệp cần nhiều hơn nguồn cung đáp ứng).\n"
            "- Gap >= 35%: Mức độ thiếu hụt nghiêm trọng (Severe Shortage), được đánh dấu là điểm bất thường thị trường.\n"
            "- Gap âm (<= 0): Nguồn cung dư thừa hoặc đáp ứng đầy đủ nhu cầu thị trường."
        )
    },
    {
        "doc_id": "KB_AI_TECH_006",
        "title": "Ứng dụng Trí tuệ Nhân tạo (AI) trong Hệ thống",
        "category": "AI_CAPABILITIES",
        "access_scope": "public",
        "relevant_roles": ["all", "admin", "worker", "employer", "course_provider", "guest"],
        "content": (
            "Skill Lens Lab ứng dụng AI tại 5 cấu phần công nghệ then chốt:\n"
            "1. AI Web Crawler & Cleaner: Tự động cào dữ liệu định kỳ (mỗi 6 giờ), làm sạch văn bản, loại bỏ tin tuyển dụng trùng lặp.\n"
            "2. AI Skill Extractor: Kết hợp spaCy và mô hình ngôn ngữ lớn (Gemini / Groq) để trích xuất tự động các kỹ năng chuyên môn và kỹ năng mềm từ JD và CV không có cấu trúc.\n"
            "3. AI Skill Classifier: Tự động ánh xạ và phân loại kỹ năng vào danh mục chuẩn hóa ESCO theo 5 nhóm ngành (IT, Du lịch, Logistics, Kinh tế, Nông nghiệp CNC).\n"
            "4. AI CV Analyzer & Recommendation Engine: Nhận diện nội dung CV qua OCR/NLP (hỗ trợ đa phương thức PDF/ảnh/text), chấm điểm mức độ tương thích công việc và tự động gợi ý lộ trình khóa học bù đắp kỹ năng còn thiếu.\n"
            "5. AI Chatbox (Interactive Insights): Trợ lý AI đàm thoại thông minh theo kiến trúc RAG, phân tích dữ liệu thực tế và tri thức biểu đồ tham khảo, tuân thủ nghiêm ngặt nguyên tắc Question-Only Answering (không bịa số liệu, không chèn nội dung ngoài phạm vi)."
        )
    },
    {
        "doc_id": "KB_LIMITS_007",
        "title": "Phạm vi Dữ liệu, Giới hạn Hệ thống và Phân biệt Nguồn dữ liệu",
        "category": "SYSTEM_LIMITS",
        "access_scope": "public",
        "relevant_roles": ["all", "admin", "worker", "employer", "course_provider", "guest"],
        "content": (
            "Phân định rõ ràng các nguồn dữ liệu trong Skill Lens Lab:\n"
            "1. Dữ liệu thực tế trong cơ sở dữ liệu MySQL: Hệ thống lưu trữ các tin tuyển dụng và khảo sát thực tế thu thập năm 2026 (tổng số hơn 1.000 tin tuyển dụng, hơn 500 khảo sát sinh viên, danh mục kỹ năng chuẩn hóa).\n"
            "2. Dữ liệu tham khảo từ tài liệu nghiên cứu và biểu đồ (So_Lieu_Bieu_do.docx): Chứa chuỗi số liệu chuyển dịch nhu cầu việc làm qua các năm 2023, 2024, 2025, 2026 và 2027 (dự báo); so sánh cơ cấu 2025 vs 2026; và bảng đối sánh chi tiết theo khu vực Cần Thơ, TP.HCM, Hà Nội.\n"
            "3. Dữ liệu năm 2027: Luôn được đánh dấu là số liệu DỰ BÁO (forecast), tuyệt đối không mô tả như số liệu thực tế đã xảy ra.\n"
            "4. Nguyên tắc ưu tiên nguồn dữ liệu: Khi hỏi số liệu hiện tại của hệ thống -> truy xuất MySQL thực. Khi hỏi số liệu trong biểu đồ/tài liệu -> sử dụng đúng dataset biểu đồ tham khảo. Khi hỏi kết quả CV -> sử dụng kết quả CV đã phân tích. Nếu không có dữ liệu -> thông báo thiếu dữ liệu trung thực, không tự bịa số liệu."
        )
    },
    {
        "doc_id": "KB_DOCUMENT_DATA_008",
        "title": "Dữ liệu Nghiên cứu và Biểu đồ Chuẩn hóa (So_Lieu_Bieu_do.docx)",
        "category": "CHART_DATASET",
        "access_scope": "public",
        "relevant_roles": ["all", "admin", "worker", "employer", "course_provider", "guest"],
        "content": (
            "Dữ liệu chi tiết từ 30 trang tài liệu nghiên cứu và biểu đồ chuẩn hóa:\n"
            "1. Bảng Top 5 kỹ năng thiếu hụt tổng quan: Python (Demand 89.4%, Supply 51.2%, Gap 38.2%), Docker & Cloud DevOps (Demand 84.6%, Supply 47.8%, Gap 36.8%), "
            "Tiếng Anh chuyên ngành (Demand 82.1%, Supply 39.5%, Gap 42.6% - khoảng cách thiếu hụt lớn nhất), Giải quyết vấn đề (Demand 78.5%, Supply 56.4%, Gap 22.1%), "
            "Cybersecurity & Mạng (Demand 73.2%, Supply 34.9%, Gap 38.3%). Kỹ năng có nhu cầu tuyển dụng cao nhất là Python (89.4%).\n"
            "2. Biểu đồ cơ cấu ngành nghề 2026: IT & Công nghệ 38.5% (385 tin / mẫu 1.000 hoặc 1.150 tin / mẫu 3.000), Logistics 24.1% (241 tin / mẫu 1.000 hoặc 720 tin / mẫu 3.000), "
            "Du lịch 21.8% (218 tin / mẫu 1.000 hoặc 680 tin / mẫu 3.000), Kinh tế 15.6% (156 tin / mẫu 1.000 hoặc 450 tin / mẫu 3.000), Nông nghiệp 0.0% (chưa phát sinh mẫu trong kỳ này).\n"
            "3. Biểu đồ đường đi chuyển dịch nhu cầu việc làm (2023 - 2027) (số tin qua các năm 2023, 2024, 2025, 2026, 2027 Dự báo):\n"
            "- IT & Công nghệ: 180 -> 230 -> 285 -> 385 -> 460 (Dự báo) | Tăng trưởng bứt phá (+155.6%)\n"
            "- Logistics & XNK: 140 -> 165 -> 190 -> 241 -> 290 (Dự báo) | Tăng trưởng liên tục (+107.1%)\n"
            "- Du lịch & Khách sạn: 150 -> 180 -> 210 -> 218 -> 225 (Dự báo) | Tăng đều rồi đi ngang (+50.0%)\n"
            "- Kinh tế & Tài chính: 310 -> 290 -> 270 -> 156 -> 115 (Dự báo) | Thu hẹp mạnh do tự động hóa (-62.9%)\n"
            "- Nông nghiệp CNC: 25 -> 35 -> 45 -> 78 -> 110 (Dự báo) | Tốc độ tăng cao nhất (+340.0%)\n"
            "4. So sánh cơ cấu tỷ trọng (2025 vs 2026):\n"
            "- IT: 2025: 28.5% (285 tin), 2026: 38.5% (385 tin), Tăng +10.0 điểm %, Tốc độ tăng trưởng: +35.1% (Dịch chuyển trọng tâm lớn nhất)\n"
            "- Logistics: 2025: 19.0% (190 tin), 2026: 24.1% (241 tin), Tăng +5.1 điểm %, Tốc độ tăng trưởng: +26.8%\n"
            "- Du lịch: 2025: 21.0% (210 tin), 2026: 21.8% (218 tin), Tăng +0.8 điểm %, Tốc độ tăng trưởng: +3.8%\n"
            "- Kinh tế: 2025: 27.0% (270 tin), 2026: 15.6% (156 tin), Giảm -11.4 điểm %, Tốc độ sụt giảm: -42.2%\n"
            "- Nông nghiệp: 2025: 4.5% (45 tin), 2026: 7.8% (78 tin), Tăng +3.3 điểm %, Tốc độ tăng trưởng: +73.3%\n"
            "5. Kỹ năng thiếu nhất theo khu vực:\n"
            "- IT Cần Thơ: IoT & Cảm biến giám sát độ mặn/phèn (Gap 64.0 điểm %, Demand 85.0%, Supply 21.0%, Lương 12–28 triệu, 285 tin).\n"
            "- IT TP.HCM: Cloud Architecture (AWS/GCP/Azure) (Gap 59.7 điểm %, Demand 96.2%, Supply 36.5%, Lương 20–50 triệu, 450 tin).\n"
            "- IT Hà Nội: Python AI & LLM (Generative AI) (Gap 56.3 điểm %, Demand 94.5%, Supply 38.2%, Lương 18–45 triệu, 420 tin).\n"
            "- Logistics Cần Thơ: Chuỗi cung ứng lạnh nông sản (Gap 65.0 điểm %, Demand 89.0%, Supply 24.0%, Lương 10–22 triệu, 241 tin).\n"
            "- Du lịch Cần Thơ: Tiếng Anh du lịch sinh thái (Gap 54.2 điểm %, Demand 92.4%, Supply 38.2%, Lương 8–18 triệu, 218 tin).\n"
            "- Kinh tế Cần Thơ: TMĐT & Livestream bán nông sản (Gap 57.0 điểm %, Demand 85.0%, Supply 28.0%, Lương 8–20 triệu, 156 tin)."
        )
    }
]


def search_project_knowledge(query: str, user_role: str = "guest", top_k: int = 2) -> List[Dict[str, Any]]:
    """Tìm kiếm tri thức dự án phù hợp nhất qua RAG kết hợp chấm điểm từ khóa trọng tâm."""
    q_low = query.lower()
    scored_docs = []

    keyword_weights = {
        "KB_OVERVIEW_001": ["skillled lab", "skill lens lab", "là gì", "mục tiêu", "giải quyết", "bài toán", "dự án", "nền tảng"],
        "KB_USERS_002": ["những ai", "ai có thể dùng", "đối tượng", "vai trò", "phân quyền", "rbac", "quyền hạn", "admin", "doanh nghiệp", "sinh viên"],
        "KB_FEATURES_003": ["chức năng", "website có gì", "tính năng", "menu", "phân hệ", "chẩn đoán & lộ trình", "hồ sơ năng lực", "20 chức vụ"],
        "KB_GUIDE_004": ["làm sao", "làm thế nào", "hướng dẫn", "cách", "phân tích cv", "chẩn đoán", "đăng ký", "đăng nhập", "chọn hồ sơ mẫu", "ctrl+v"],
        "KB_FORMULAS_005": ["demand", "supply", "skill gap", "khoảng cách", "công thức", "tính như thế nào", "điểm phần trăm", "severe shortage"],
        "KB_AI_TECH_006": ["sử dụng ai", "ai ở những phần nào", "ai làm gì", "gemini", "groq", "multimodal", "ocr", "spacy"],
        "KB_LIMITS_007": ["giới hạn", "phân biệt", "nguồn dữ liệu", "phạm vi", "lịch sử", "database thực", "bảo mật"],
        "KB_DOCUMENT_DATA_008": ["2023", "2024", "2025", "2027", "dự báo", "bảng số liệu", "biểu đồ", "cơ cấu", "tỷ trọng", "cần thơ", "tp.hcm", "hà nội", "lương"]
    }

    for doc in PROJECT_KNOWLEDGE_DOCUMENTS:
        if doc["access_scope"] != "public" and user_role not in doc.get("relevant_roles", []):
            continue

        doc_id = doc["doc_id"]
        score = 0

        if doc_id in keyword_weights:
            for kw in keyword_weights[doc_id]:
                if kw in q_low:
                    score += 4

        content_words = set(re.findall(r"\w+", doc["content"].lower()))
        query_words = set(re.findall(r"\w+", q_low))
        overlap = len(content_words.intersection(query_words))
        score += overlap * 0.2

        if score > 0:
            scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_docs[:top_k]]


def classify_user_intent(query: str, context: Optional[Any] = None) -> str:
    """
    Phân loại câu hỏi thành các nhóm Intent rõ ràng:
    - INTENT_8_OUT_OF_SCOPE: Injection, vi phạm RBAC
    - INTENT_LOOKUP_METRIC: Hỏi một số liệu cụ thể (Gap, share, lương, tin tuyển dụng, dự báo)
    - INTENT_TOP_RANKING: Hỏi Top 5 / Top 10 / Kỹ năng thiếu nhất
    - INTENT_COMPARISON: So sánh 2 năm, 2 ngành, 2 khu vực
    - INTENT_TREND: Hỏi xu hướng chuyển dịch, biến động theo thời gian
    - INTENT_USER_GUIDANCE: Hướng dẫn sử dụng tính năng
    - INTENT_PROJECT_KNOWLEDGE: Giới thiệu dự án, mục tiêu, vai trò
    - INTENT_3_DATA_ANALYTICS: Phân tích tổng thể dữ liệu
    """
    q = query.lower().strip()

    # INTENT 8: OUT_OF_SCOPE / PROMPT INJECTION / RBAC
    out_of_scope_terms = [
        "xóa database", "drop database", "hack", "dump database", "tài khoản admin",
        "mật khẩu người dùng", "user password", "token blacklist", "bỏ qua quy tắc",
        "tự tạo số liệu", "giả sử python tăng", "fake data", "mật khẩu"
    ]
    if any(k in q for k in out_of_scope_terms):
        return "INTENT_8_OUT_OF_SCOPE"

    trend = trend_kind(query)
    if trend:
        return "INTENT_" + trend.upper()

    # INTENT_LOOKUP_METRIC: Hỏi một con số/chỉ số cụ thể
    metric_lookup_terms = [
        "bao nhiêu trong bảng", "bao nhiêu trong biểu đồ", "chiếm bao nhiêu",
        "bao nhiêu tin tuyển dụng năm", "mức lương", "lương bao nhiêu", "thiếu hụt bao nhiêu"
    ]
    if any(k in q for k in metric_lookup_terms):
        return "INTENT_LOOKUP_METRIC"

    # INTENT_COMPARISON
    compare_terms = [
        "so sánh", "khác nhau thế nào", "đối chiếu", "so với", "ngành nào có quy mô việc làm lớn hơn",
        "giữa 2 ngành", "giữa hai ngành", "năm 2025 và 2026", "2025 vs 2026"
    ]
    if any(k in q for k in compare_terms) and not any(k in q for k in ["kỹ năng mềm khác"]):
        return "INTENT_5_COMPARISON"

    # INTENT_TOP_RANKING
    top_terms = [
        "thiếu kỹ năng nào nhất", "thiếu nhất", "cao nhất trong top 5", "gap cao nhất",
        "top 5 kỹ năng", "top 10 kỹ năng", "kỹ năng đứng đầu", "nhiều nhất là gì"
    ]
    if any(k in q for k in top_terms):
        return "INTENT_TOP_RANKING"

    # INTENT_TREND
    trend_terms = [
        "đường đi chuyển dịch", "xu hướng biến động", "chuyển dịch nhu cầu",
        "xu hướng việc làm", "quỹ đạo biến động"
    ]
    if any(k in q for k in trend_terms):
        return "INTENT_TREND"

    # INTENT 2: USER_GUIDANCE
    guidance_terms = [
        "làm sao để", "làm thế nào để", "cách phân tích cv", "cách xem xu hướng",
        "tìm việc ở đâu", "tìm khóa học ở đâu", "xem skill gap ở đâu", "làm sao tìm",
        "hướng dẫn sử dụng", "cách đăng nhập", "cách đăng ký", "đổi bộ lọc", "cách dùng chẩn đoán"
    ]
    if any(k in q for k in guidance_terms):
        return "INTENT_2_USER_GUIDANCE"

    # INTENT 1: PROJECT_KNOWLEDGE
    knowledge_terms = [
        "skillled lab là gì", "skill lens lab là gì", "dự án này là gì", "website này là gì",
        "giải quyết vấn đề gì", "mục tiêu của", "những ai có thể", "ai sử dụng",
        "có những chức năng gì", "chức năng nào", "hệ thống sử dụng ai ở những phần nào",
        "sử dụng ai để làm gì", "dự án của ai"
    ]
    if any(k in q for k in knowledge_terms):
        return "INTENT_1_PROJECT_KNOWLEDGE"

    return "INTENT_3_DATA_ANALYTICS"


def resolve_followup_context(
    query: str,
    history: List[Any],
    current_context: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Phân giải đại từ thay thế và câu hỏi tiếp nối đa lượt (Multi-turn Anaphora & Context Tracking).
    Hỗ trợ chuyển đổi khu vực ('Còn TP.HCM?', 'Còn Hà Nội?'), chuyển đổi năm ('Thế năm 2026?'),
    và chuyển đổi chủ đề (từ Python sang Logistics).
    """
    q_low = query.lower().strip()
    resolved = {
        "is_followup": False,
        "target_industry": None,
        "target_region": None,
        "target_skill": None,
        "target_year": None,
        "reference_text": ""
    }

    history = prior_turns(query, history)
    if not history:
        return resolved

    # Lấy câu hỏi gần nhất của user và phản hồi gần nhất của trợ lý
    last_user_query = ""
    last_assistant_msg = ""
    for msg in reversed(history):
        role = getattr(msg, "role", None) or (msg.get("role") if isinstance(msg, dict) else None)
        cnt = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else "")
        if role == "user" and not last_user_query:
            last_user_query = cnt.lower()
        elif role in ["assistant", "ai"] and not last_assistant_msg:
            last_assistant_msg = cnt

    # Kiểm tra chuyển đổi khu vực: "Còn TP.HCM?", "Còn Hà Nội?", "Còn Cần Thơ?"
    if any(k in q_low for k in ["còn tp.hcm", "còn tphcm", "còn hồ chí minh", "thế tp.hcm", "tp.hcm thì sao", "tp.hcm", "tphcm"]):
        resolved["is_followup"] = True
        resolved["target_region"] = "HCM"
    elif any(k in q_low for k in ["còn hà nội", "còn hn", "thế hà nội", "hà nội thì sao", "hà nội", "ha noi"]):
        resolved["is_followup"] = True
        resolved["target_region"] = "HN"
    elif any(k in q_low for k in ["còn cần thơ", "còn ct", "thế cần thơ", "cần thơ thì sao", "cần thơ", "can tho"]):
        resolved["is_followup"] = True
        resolved["target_region"] = "CT"

    # Kế thừa ngành từ lịch sử hội thoại nếu user đổi khu vực hoặc hỏi tiếp
    if resolved["is_followup"]:
        for msg in reversed(history):
            content = (getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else "")).lower()
            if any(k in content for k in ["it & công nghệ", "ngành it", " it ", "cntt", "công nghệ thông tin", "công nghệ", "phần mềm"]):
                resolved["target_industry"] = "IT"
                break
            elif any(k in content for k in ["du lịch & khách sạn", "ngành du lịch", "du lịch", "khách sạn"]):
                resolved["target_industry"] = "Du lịch"
                break
            elif any(k in content for k in ["logistics & xuất nhập khẩu", "ngành logistics", "logistics", "chuỗi cung ứng", "xnk"]):
                resolved["target_industry"] = "Logistics"
                break
            elif any(k in content for k in ["kinh tế & tài chính", "ngành kinh tế", "kinh tế", "tài chính"]):
                resolved["target_industry"] = "Kinh tế"
                break
            elif any(k in content for k in ["nông nghiệp công nghệ cao", "ngành nông nghiệp", "nông nghiệp"]):
                resolved["target_industry"] = "Nông nghiệp"
                break

        if not resolved["target_industry"] and current_context:
            ind_ctx = getattr(current_context, "industry", None) or (current_context.get("industry") if isinstance(current_context, dict) else None)
            if ind_ctx and ind_ctx not in ["Tất cả", "all"]:
                resolved["target_industry"] = "IT" if ind_ctx in ["IT", "Công nghệ thông tin"] else ind_ctx

    # Kiểm tra chuyển đổi năm: "Thế năm 2026?", "Còn năm 2027?"
    if any(k in q_low for k in ["năm 2026", "2026", "năm 2027", "2027", "năm 2025", "2025"]):
        if any(k in q_low for k in ["còn", "thế", "sang", "vậy"]):
            resolved["is_followup"] = True
            for y in [2027, 2026, 2025, 2024, 2023]:
                if str(y) in q_low:
                    resolved["target_year"] = y
                    break
            # Kế thừa ngành
            if any(k in last_user_query for k in ["it", "cntt", "công nghệ"]):
                resolved["target_industry"] = "IT"
            elif any(k in last_user_query for k in ["logistics", "xnk"]):
                resolved["target_industry"] = "Logistics"
            elif any(k in last_user_query for k in ["du lịch"]):
                resolved["target_industry"] = "Du lịch"
            elif any(k in last_user_query for k in ["kinh tế"]):
                resolved["target_industry"] = "Kinh tế"
            elif any(k in last_user_query for k in ["nông nghiệp"]):
                resolved["target_industry"] = "Nông nghiệp"

    # Kỹ năng đứng đầu / kỹ năng đó
    if any(k in q_low for k in ["kỹ năng đứng đầu", "kỹ năng số 1", "kỹ năng top 1", "kỹ năng đó", "kỹ năng này"]):
        resolved["is_followup"] = True
        if "tiếng anh" in last_assistant_msg.lower():
            resolved["target_skill"] = "Tiếng Anh chuyên ngành"
        elif "python" in last_assistant_msg.lower():
            resolved["target_skill"] = "Python (AI & Phân tích dữ liệu)"
        elif "iot" in last_assistant_msg.lower():
            resolved["target_skill"] = "IoT & Cảm biến"
        elif "cloud" in last_assistant_msg.lower():
            resolved["target_skill"] = "Cloud Architecture"

    return resolved
