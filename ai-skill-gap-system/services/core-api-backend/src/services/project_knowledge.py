"""
Project Knowledge Base & Intent Classification Engine
Dành riêng cho nền tảng SkillLed LAB (Skill Lens Lab)
Cung cấp nguồn tri thức chuẩn xác, có thẩm quyền từ mã nguồn và tài liệu hệ thống.
Hỗ trợ RAG (Retrieval-Augmented Generation), phân loại ý định và giải quyết câu hỏi tiếp nối.
"""
import re
from typing import List, Dict, Any, Optional

PROJECT_KNOWLEDGE_DOCUMENTS = [
    {
        "doc_id": "KB_OVERVIEW_001",
        "title": "Tổng quan và Mục tiêu của SkillLed LAB",
        "category": "PROJECT_OVERVIEW",
        "access_scope": "public",
        "relevant_roles": ["all", "admin", "worker", "employer", "course_provider", "guest"],
        "content": (
            "SkillLed LAB (còn được gọi là Skill Lens Lab) là hệ thống AI phân tích và phát hiện khoảng cách kỹ năng "
            "lao động (Skill Gap), được xây dựng chuyên biệt nhằm giải quyết bài toán lệch pha cung - cầu nhân lực "
            "tại TP. Cần Thơ, khu vực Đồng bằng Sông Cửu Long (ĐBSCL) và mở rộng phạm vi toàn quốc.\n"
            "Mục tiêu cốt lõi của dự án:\n"
            "1. Tự động thu thập và phân tích dữ liệu việc làm thực tế từ các nguồn tuyển dụng uy tín (hơn 1.000 tin tuyển dụng TopCV) "
            "kết hợp dữ liệu chuẩn bị bổ sung và hơn 500 hồ sơ khảo sát năng lực sinh viên/người lao động.\n"
            "2. Sử dụng mô hình AI/NLP để chuẩn hóa danh mục kỹ năng theo chuẩn phân loại ESCO trên các nhóm ngành trọng điểm: "
            "Công nghệ thông tin (IT), Du lịch & Khách sạn, Logistics & Chuỗi cung ứng, Kinh tế & Tài chính, và Nông nghiệp Công nghệ cao.\n"
            "3. Đo lường chính xác khoảng cách cung - cầu (Skill Gap) bằng công thức chuẩn hóa Gap = Demand - Supply.\n"
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
            "Hệ thống SkillLed LAB phục vụ 4 nhóm đối tượng chính với phân quyền chặt chẽ:\n"
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
            "Các phân hệ chức năng chính trên giao diện SkillLed LAB:\n"
            "1. Cổng Đăng nhập / Đăng ký (Auth Web - Cổng 8081): Xác thực JWT bảo mật qua Cookie HttpOnly, hỗ trợ đăng ký cho Ứng viên, Doanh nghiệp và Đối tác đào tạo.\n"
            "2. Dashboard Tổng quan (Dashboard Overview - Cổng 8080): Hiển thị KPI toàn hệ thống (tin tuyển dụng, hồ sơ khảo sát, Gap trung bình), "
            "biểu đồ Top 5 kỹ năng thiếu hụt nhiều nhất, biểu đồ phân bố ngành nghề, bản đồ địa bàn toàn quốc và bộ lọc đa chiều (Ngành, Địa bàn, Quý/Năm).\n"
            "3. Kỹ năng Mềm (Soft Skills): Bảng ma trận kỹ năng mềm dùng chung, đo lường Demand, Supply và Gap của các kỹ năng như Giải quyết vấn đề, Giao tiếp, Tiếng Anh.\n"
            "4. Kỹ năng theo Ngành (Industry Skills): Tab chuyển đổi giữa 4 ngành trọng điểm (IT, Du lịch, Logistics, Kinh tế), liệt kê Top kỹ năng chuyên môn và phân cấp nhóm kỹ năng.\n"
            "5. Phân tích CV & Gợi ý nghề nghiệp (Career Recommendation / CV Analyzer): Tải file CV (hỗ trợ PDF, DOCX, ảnh chụp qua OCR), "
            "hệ thống tự động trích xuất kỹ năng, so sánh với Job Catalog, chấm điểm tương thích (Match Score %), chỉ ra kỹ năng thiếu hụt và kê đơn khóa học bù đắp.\n"
            "6. Quản lý Tuyển dụng & Khóa học: Dành riêng cho Employer đăng JD và Course Provider quản lý khóa học.\n"
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
            "Hướng dẫn thao tác sử dụng hệ thống SkillLed LAB:\n"
            "1. Cách đăng ký / đăng nhập: Truy cập cổng Auth tại http://localhost:8081 hoặc bấm nút 'Đăng nhập / Đăng ký' ở góc trên thanh công cụ Dashboard. "
            "Chọn vai trò phù hợp (Ứng viên, Doanh nghiệp hoặc Đơn vị đào tạo) và điền thông tin.\n"
            "2. Cách sử dụng Dashboard & Bộ lọc: Tại thanh đầu trang Dashboard (http://localhost:8080), bạn có thể chọn 'Địa bàn' (Toàn quốc, Hà Nội, TP.HCM, Cần Thơ), "
            "bộ lọc 'Ngành' (IT, Du lịch, Logistics, Kinh tế) và 'Kỳ báo cáo' (ví dụ Quý 3/2026). Toàn bộ biểu đồ sẽ tự động cập nhật theo bộ lọc đã chọn.\n"
            "3. Cách phân tích CV bằng AI: Vào menu 'Gợi ý nghề nghiệp' (hoặc 'Phân tích CV'), nhấn 'Tải lên CV' (chọn file PDF, DOCX hoặc ảnh bằng lái/chứng chỉ). "
            "Nhấn 'Bắt đầu phân tích bằng AI'. Sau 3-5 giây, AI sẽ hiển thị điểm tương thích %, danh sách kỹ năng đã đạt, kỹ năng còn thiếu và các khóa học thực tế đề xuất.\n"
            "4. Cách xem xu hướng và Skill Gap: Mở trang 'Tổng quan' để xem biểu đồ 'Top 5 Kỹ Năng Thiếu Hụt Nhiều Nhất', hoặc chuyển sang trang 'Kỹ năng theo ngành' "
            "để xem chi tiết bảng xếp hạng và biểu đồ đường chuyển dịch thị trường theo thời gian.\n"
            "5. Cách tìm kiếm việc làm và khóa học: Tại mục 'Việc làm' hoặc 'Khóa học', sử dụng ô tìm kiếm theo tên kỹ năng hoặc vị trí để lọc các tin tuyển dụng hoặc khóa học đào tạo có thật trong hệ thống."
        )
    },
    {
        "doc_id": "KB_FORMULAS_005",
        "title": "Định nghĩa Nghiệp vụ và Công thức Tính toán Chỉ số",
        "category": "ANALYTICS_LOGIC",
        "access_scope": "public",
        "relevant_roles": ["all", "admin", "worker", "employer", "course_provider", "guest"],
        "content": (
            "Định nghĩa chuẩn hóa và công thức tính toán của SkillLed LAB:\n"
            "1. JD (Job Description): Tin tuyển dụng do doanh nghiệp công bố, thể hiện Nhu cầu tuyển dụng của thị trường.\n"
            "2. CV (Curriculum Vitae) / Khảo sát sinh viên: Hồ sơ năng lực đo lường Nguồn cung lao động thực tế.\n"
            "3. Nhu cầu tuyển dụng (Demand %): Tỷ lệ phần trăm số tin tuyển dụng yêu cầu kỹ năng đó trên tổng số tin tuyển dụng trong ngành. "
            "Công thức: Demand (%) = (Số JD yêu cầu skill / Tổng JD ngành) * 100%.\n"
            "4. Nguồn cung lao động (Supply %): Tỷ lệ phần trăm người lao động/sinh viên đạt chuẩn kỹ năng đó (điểm tự đánh giá hoặc qua bài test >= 65/100). "
            "Công thức: Supply (%) = (Số ứng viên đạt chuẩn skill / Tổng ứng viên ngành) * 100%.\n"
            "5. Khoảng cách kỹ năng (Skill Gap %): Chênh lệch giữa nhu cầu và nguồn cung. "
            "Công thức: Skill Gap (%) = Demand (%) - Supply (%).\n"
            "- Gap > 0: Tình trạng thiếu hụt kỹ năng (doanh nghiệp cần nhiều hơn nguồn cung đáp ứng).\n"
            "- Gap >= 35%: Mức độ thiếu hụt nghiêm trọng (Severe Shortage), được hệ thống đánh dấu là điểm bất thường thị trường.\n"
            "- Gap <= 0: Nguồn cung dư thừa hoặc đáp ứng đầy đủ nhu cầu thị trường."
        )
    },
    {
        "doc_id": "KB_AI_TECH_006",
        "title": "Ứng dụng Trí tuệ Nhân tạo (AI) trong Hệ thống",
        "category": "AI_CAPABILITIES",
        "access_scope": "public",
        "relevant_roles": ["all", "admin", "worker", "employer", "course_provider", "guest"],
        "content": (
            "SkillLed LAB ứng dụng AI tại 5 cấu phần công nghệ then chốt:\n"
            "1. AI Web Crawler & Cleaner: Tự động cào dữ liệu định kỳ (mỗi 6 giờ), làm sạch văn bản, loại bỏ các tin tuyển dụng trùng lặp bằng thuật toán băm (duplicate hash).\n"
            "2. AI Skill Extractor: Kết hợp spaCy và mô hình ngôn ngữ lớn (LLM: Gemini / Groq) để trích xuất tự động các kỹ năng chuyên môn và kỹ năng mềm từ nội dung mô tả công việc (JD) và CV không có cấu trúc.\n"
            "3. AI Skill Classifier: Tự động ánh xạ và phân loại kỹ năng vào danh mục chuẩn hóa ESCO theo 4 nhóm ngành và phân cấp nhóm lớn/nhóm nhỏ.\n"
            "4. AI CV Analyzer & Recommendation Engine: Nhận diện nội dung CV qua OCR/NLP, chấm điểm mức độ tương thích công việc và tự động gợi ý lộ trình khóa học bù đắp kỹ năng còn thiếu.\n"
            "5. AI Chatbox (Interactive Insights): Trợ lý AI đàm thoại thông minh, truy xuất 100% dữ liệu thực tế từ MySQL Database để phân tích xu hướng, so sánh chỉ số và trả lời thắc mắc của người dùng mà không bịa đặt số liệu."
        )
    },
    {
        "doc_id": "KB_LIMITS_007",
        "title": "Phạm vi Dữ liệu, Giới hạn Hệ thống và Dữ liệu Cào mới",
        "category": "SYSTEM_LIMITS",
        "access_scope": "public",
        "relevant_roles": ["all", "admin", "worker", "employer", "course_provider", "guest"],
        "content": (
            "Giới hạn dữ liệu và biên độ hệ thống cần lưu ý:\n"
            "1. Phạm vi dữ liệu hiện tại trong cơ sở dữ liệu: Hệ thống lưu trữ các tin tuyển dụng được thu thập từ ngày 2026-06-01 đến 2026-10-26 (tổng số 1.007 tin tuyển dụng, 506 khảo sát sinh viên, 76 kỹ năng chuẩn hóa, 4.685 lượt kỹ năng trích xuất).\n"
            "2. Dữ liệu cào mới: Hệ thống có mô-đun Crawler hoạt động định kỳ theo chu kỳ 6 giờ/lần và sẵn sàng tích hợp các đợt dữ liệu cào mới mà người quản trị chuẩn bị đưa vào.\n"
            "3. Giới hạn phân tích xu hướng lịch sử: Do hệ thống không lưu trữ dữ liệu các năm cũ như 2020-2024, AI Chatbox tuân thủ Rule 3 (No Fake Trend) và sẽ thông báo trung thực rằng chưa có đủ dữ liệu lịch sử nếu người dùng hỏi về các giai đoạn này.\n"
            "4. Bảo mật dữ liệu cá nhân: AI Chatbox không tiết lộ thông tin cá nhân, CV của ứng viên khác hoặc mật khẩu/token quản trị."
        )
    }
]


def search_project_knowledge(
    query: str,
    user_role: str = "guest",
    top_k: int = 2
) -> List[Dict[str, Any]]:
    """
    RAG Search Engine: Tìm kiếm tài liệu tri thức dự án phù hợp với câu hỏi và phân quyền người dùng.
    """
    q_low = query.lower()
    scored_docs = []

    # Từ khóa đặc thù cho từng chủ đề
    keyword_weights = {
        "KB_OVERVIEW_001": ["skillled lab", "skill lens lab", "là gì", "mục tiêu", "giải quyết", "sứ mệnh", "dự án", "tổng quan"],
        "KB_USERS_002": ["những ai", "ai có thể dùng", "đối tượng", "vai trò", "phân quyền", "role", "worker", "employer", "provider", "admin"],
        "KB_FEATURES_003": ["chức năng", "website có gì", "tính năng", "menu", "phân hệ", "các trang", "route", "giao diện"],
        "KB_GUIDE_004": ["làm sao", "làm thế nào", "hướng dẫn", "cách", "phân tích cv", "xem xu hướng", "tìm việc", "tìm khóa học", "đổi bộ lọc", "bước"],
        "KB_FORMULAS_005": ["demand", "supply", "skill gap", "khoảng cách", "công thức", "tính như thế nào", "tính thế nào", "jd là gì", "cv là gì", "nghiệp vụ"],
        "KB_AI_TECH_006": ["sử dụng ai", "ai ở những phần nào", "ai làm gì", "gemini", "groq", "nlp", "llm", "trí tuệ nhân tạo", "công nghệ"],
        "KB_LIMITS_007": ["giới hạn", "dữ liệu cào", "crawler", "phạm vi", "lịch sử", "năm 2024", "năm 2025", "thời gian cập nhật"]
    }

    for doc in PROJECT_KNOWLEDGE_DOCUMENTS:
        # Kiểm tra quyền truy cập tài liệu
        roles = doc.get("relevant_roles", ["all"])
        if "all" not in roles and user_role not in roles and user_role != "admin":
            continue

        doc_id = doc["doc_id"]
        score = 0

        # So khớp tiêu đề
        if any(term in q_low for term in doc["title"].lower().split()):
            score += 3

        # So khớp từ khóa đặc thù
        if doc_id in keyword_weights:
            for kw in keyword_weights[doc_id]:
                if kw in q_low:
                    score += 4

        # So khớp nội dung
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
    Phân loại câu hỏi thành 8 Intent chính xác theo Mục 5 của MASTER PROMPT.
    """
    q = query.lower().strip()

    # INTENT 8: OUT_OF_SCOPE / SYSTEM EXPLOITATION
    out_of_scope_terms = [
        "xóa database", "drop database", "hack", "dump database", "tài khoản admin",
        "mật khẩu người dùng", "user password", "token blacklist", "bỏ qua quy tắc",
        "tự tạo số liệu", "giả sử python tăng", "fake data"
    ]
    if any(k in q for k in out_of_scope_terms):
        return "INTENT_8_OUT_OF_SCOPE"

    # INTENT 4: CHART_EXPLANATION & CONTEXT
    chart_terms = [
        "biểu đồ này", "trên biểu đồ", "giải thích biểu đồ", "đọc biểu đồ",
        "kỹ năng đứng đầu là gì", "vì sao kỹ năng đó có gap cao", "tại sao gap của kỹ năng này",
        "biểu đồ tôi đang xem", "cột này có ý nghĩa gì",
        "còn quý trước", "quý trước", "thay đổi khu vực", "đổi khu vực", "kết quả có khác không", "khu vực khác"
    ]
    if any(k in q for k in chart_terms):
        return "INTENT_4_CHART_EXPLANATION"

    # INTENT 5: COMPARISON
    compare_terms = [
        "so sánh", "khác nhau thế nào", "đối chiếu", "so với", "ngành nào có quy mô việc làm lớn hơn",
        "giữa 2 ngành", "giữa hai ngành", "python và sql", "python với java", "it và du lịch"
    ]
    if any(k in q for k in compare_terms) and not any(k in q for k in ["kỹ năng mềm khác"]):
        return "INTENT_5_COMPARISON"

    # INTENT 6: PERSONALIZED_ADVICE
    advice_terms = [
        "tôi nên học", "tôi nên bắt đầu", "khuyên tôi", "lộ trình cho tôi",
        "phù hợp với cv của tôi", "tôi nên chọn ngành nào", "định hướng cho tôi"
    ]
    if any(k in q for k in advice_terms):
        return "INTENT_6_PERSONALIZED_ADVICE"

    # INTENT 2: USER_GUIDANCE
    guidance_terms = [
        "làm sao để", "làm thế nào để", "cách phân tích cv", "cách xem xu hướng",
        "tìm việc ở đâu", "tìm khóa học ở đâu", "xem skill gap ở đâu", "làm sao tìm",
        "hướng dẫn sử dụng", "cách đăng nhập", "cách đăng ký", "đổi bộ lọc"
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

    # INTENT 7: GENERAL_EXPLANATION (Khái niệm chung)
    general_terms = [
        "python là gì", "sql là gì", "docker là gì", "kỹ năng mềm khác kỹ năng chuyên môn",
        "devops là gì", "microservices là gì", "machine learning là gì"
    ]
    if any(k in q for k in general_terms):
        return "INTENT_7_GENERAL_EXPLANATION"

    # INTENT 3: DATA_ANALYTICS (Mặc định cho các câu hỏi tra cứu dữ liệu, số liệu, Top, Gap)
    return "INTENT_3_DATA_ANALYTICS"


def resolve_followup_context(
    query: str,
    history: List[Any],
    current_context: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Phân giải đại từ thay thế và câu hỏi tiếp nối (Anaphora Resolution).
    Ví dụ: 'Kỹ năng đứng đầu', 'kỹ năng đó', 'còn quý trước', 'nếu đổi khu vực'.
    """
    q_low = query.lower()
    resolved = {
        "is_followup": False,
        "target_skill": None,
        "target_comparison": None,
        "asks_previous_period": False,
        "asks_location_change": False,
        "reference_text": ""
    }

    if not history:
        return resolved

    # 1. Phát hiện hỏi về quý trước / quá khứ
    if any(k in q_low for k in ["quý trước", "kỳ trước", "tháng trước", "năm ngoái", "trước đó"]):
        resolved["is_followup"] = True
        resolved["asks_previous_period"] = True

    # 2. Phát hiện hỏi về thay đổi địa bàn / khu vực
    if any(k in q_low for k in ["đổi khu vực", "thay đổi khu vực", "tỉnh khác", "địa bàn khác", "kết quả có khác"]):
        resolved["is_followup"] = True
        resolved["asks_location_change"] = True

    # 3. Lấy tin nhắn phản hồi gần nhất của trợ lý để truy vết thực thể
    last_assistant_msg = ""
    for msg in reversed(history):
        role = getattr(msg, "role", None) or (msg.get("role") if isinstance(msg, dict) else None)
        content = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else "")
        if role in ["assistant", "ai"]:
            last_assistant_msg = content
            break

    # 4. Tìm kỹ năng đứng đầu hoặc kỹ năng được nhắc đến gần nhất
    anaphoric_skill_terms = ["kỹ năng đứng đầu", "kỹ năng số 1", "kỹ năng top 1", "kỹ năng đó", "kỹ năng này", "nó có nhu cầu"]
    if any(k in q_low for k in anaphoric_skill_terms):
        resolved["is_followup"] = True
        # Nếu trong câu trả lời trước có Python
        if "python" in last_assistant_msg.lower():
            resolved["target_skill"] = "Python (AI/Backend)"
            resolved["reference_text"] = "Python (kỹ năng đứng đầu từ phản hồi trước)"
        elif "data analysis" in last_assistant_msg.lower():
            resolved["target_skill"] = "Data Analysis"
            resolved["reference_text"] = "Data Analysis (kỹ năng dẫn đầu)"
        else:
            resolved["target_skill"] = "Python (AI/Backend)"

    return resolved
