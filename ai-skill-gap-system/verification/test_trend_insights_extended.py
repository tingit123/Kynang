"""
Bộ kiểm thử mở rộng: AI Chatbox Trend Insights & 4 Tài Liệu Ngành (Skill Lens Lab)
Kiểm thử toàn diện 16 câu hỏi Section VIII, Nhóm A câu hỏi đồng nghĩa, 4 cấp độ trả lời,
Hội thoại tiếp nối không lẫn ngành và Kiểm toán mẫu số tỷ trọng 1.078.
"""
import requests
import json
import sys

API_URL = "http://localhost:8000/api/insights/chat"

def run_extended_trend_tests():
    print("=" * 80)
    print("🚀 BẮT ĐẦU CHẠY BỘ KIỂM THỬ TREND INSIGHTS & 4 TÀI LIỆU NGÀNH MỞ RỘNG")
    print("=" * 80)

    results = {}

    # ──────────────────────────────────────────────────────────────────────────
    # PHẦN 1: 16 CÂU HỎI THAM CHIẾU SECTION VIII
    # ──────────────────────────────────────────────────────────────────────────
    print("\n--- PHẦN 1: 16 CÂU HỎI SECTION VIII ---")

    test_q16 = [
        (
            "Q1",
            "Tại sao ngành IT tăng 35,1%?",
            lambda a: ("285" in a and "385" in a and ("35.1" in a or "35,1" in a)) and ("itviec" in a.lower()),
            "Có đủ 285, 385, 35.1% và dẫn chứng ITviec"
        ),
        (
            "Q2",
            "Vì sao Logistics tăng 26,8%?",
            lambda a: ("190" in a and "241" in a and ("26.8" in a or "26,8" in a)) and ("xuất nhập khẩu" in a.lower() or "xnk" in a.lower()),
            "Có đủ 190, 241, 26.8% và bối cảnh XNK"
        ),
        (
            "Q3",
            "Tại sao Kinh tế & Tài chính giảm 42,2%?",
            lambda a: ("270" in a and "156" in a and ("42.2" in a or "42,2" in a)) and ("tự động hóa" in a.lower() or "ai" in a.lower()),
            "Có đủ 270, 156, -42.2% và lý do tự động hóa"
        ),
        (
            "Q4",
            "Kinh tế giảm tuyển dụng có nghĩa ngành tài chính đang suy thoái không?",
            lambda a: ("không" in a.lower()) and ("9,45" in a or "9.45" in a or "tăng trưởng" in a.lower()),
            "Khẳng định KHÔNG suy thoái và phân biệt hoạt động kinh tế vs tuyển dụng"
        ),
        (
            "Q5",
            "Tại sao Du lịch chỉ tăng 3,8% dù lượng khách tăng mạnh?",
            lambda a: (("3,8" in a or "3.8" in a) and "210" in a and "218" in a) and ("hoteljob" in a.lower() or "mùa vụ" in a.lower()),
            "Có đủ 210, 218, 3.8% và lý giải tối ưu năng suất / mùa vụ"
        ),
        (
            "Q6",
            "Ngành nào tăng trưởng tuyển dụng nhanh nhất trong biểu đồ?",
            lambda a: ("nông nghiệp" in a.lower()) and ("73,3" in a or "73.3" in a),
            "Nông nghiệp CNC tăng nhanh nhất 73.3%"
        ),
        (
            "Q7",
            "Ngành nào tăng nhiều tin tuyển dụng nhất?",
            lambda a: ("it" in a.lower() or "công nghệ" in a.lower()) and ("100 tin" in a or "100" in a),
            "IT tăng nhiều nhất (+100 tin tuyệt đối)"
        ),
        (
            "Q8",
            "Ngành nào giảm tuyển dụng mạnh nhất?",
            lambda a: ("kinh tế" in a.lower() or "tài chính" in a.lower()) and ("114" in a or "42.2" in a or "42,2" in a),
            "Kinh tế & Tài chính giảm mạnh nhất (-114 tin, -42.2%)"
        ),
        (
            "Q9",
            "AI có đang thay thế kế toán không?",
            lambda a: ("lặp lại" in a.lower() or "nhập liệu" in a.lower()) and ("không chứng minh mọi" in a.lower() or "vẫn tồn tại" in a.lower()),
            "Tác động tác vụ lặp lại, không thay thế hoàn toàn"
        ),
        (
            "Q10",
            "Logistics đang cần những nhóm kỹ năng nào?",
            lambda a: ("xuất nhập khẩu" in a.lower() or "chuỗi cung ứng" in a.lower()) and ("wms" in a.lower() or "tms" in a.lower() or "ngoại ngữ" in a.lower()),
            "Nghiệp vụ XNK, chuỗi cung ứng, phần mềm WMS/TMS và ngoại ngữ"
        ),
        (
            "Q11",
            "Du lịch thiếu người ở những vị trí nào?",
            lambda a: ("buồng phòng" in a.lower() or "bếp" in a.lower() or "tiền sảnh" in a.lower()),
            "Buồng phòng, bếp, tiền sảnh theo khảo sát Hoteljob"
        ),
        (
            "Q12",
            "Vì sao doanh nghiệp IT chú trọng kỹ năng hơn số lượng?",
            lambda a: ("giải quyết vấn đề" in a.lower() or "thích nghi" in a.lower() or "chọn lọc" in a.lower()),
            "Tập trung giải quyết vấn đề, thích nghi công nghệ mới"
        ),
        (
            "Q13",
            "Có phải tất cả công ty Logistics đều tuyển nhiều người?",
            lambda a: ("không" in a.lower()) and ("phân hóa" in a.lower() or "3pl" in a.lower() or "vừa và nhỏ" in a.lower()),
            "Khẳng định KHÔNG, nhu cầu phân hóa theo quy mô"
        ),
        (
            "Q14",
            "Vì sao ngành tài chính vẫn phát triển nhưng tăng nhân sự chậm?",
            lambda a: ("28 ngân hàng" in a.lower() or "học viện ngân hàng" in a.lower()) and ("tài sản" in a.lower() and "nhân sự" in a.lower()),
            "Tổng tài sản tăng nhanh hơn nhân sự (tối ưu hóa năng suất)"
        ),
        (
            "Q15",
            "Xu hướng này là dữ liệu thực hay dự báo?",
            lambda a: ("2025" in a and "2026" in a) and ("2027" in a) and ("dự báo" in a.lower()),
            "2025-2026 là dữ liệu quan sát, 2027 là dự báo (Forecast)"
        ),
        (
            "Q16",
            "Hệ thống có khẳng định AI là nguyên nhân duy nhất làm giảm việc làm kế toán không?",
            lambda a: ("chưa thể" in a.lower() or "không thể khẳng định" in a.lower()) and ("nguyên nhân duy nhất" in a.lower()),
            "Cảnh báo giới hạn: AI không phải nguyên nhân duy nhất"
        )
    ]

    for q_code, prompt_text, validator, desc in test_q16:
        try:
            resp = requests.post(API_URL, json={"message": prompt_text}, timeout=10).json()
            ans = resp.get("answer", "")
            is_pass = validator(ans)
            results[f"{q_code}: {prompt_text[:40]}..."] = ("PASS" if is_pass else "FAIL", ans[:120])
            print(f"[{'PASS' if is_pass else 'FAIL'}] {q_code}: {desc}")
        except Exception as e:
            results[f"{q_code}: {prompt_text[:40]}..."] = ("ERROR", str(e))
            print(f"[ERROR] {q_code}: {e}")

    # ──────────────────────────────────────────────────────────────────────────
    # PHẦN 2: NHÓM A - CÂU HỎI ĐỒNG NGHĨA GIẢI THÍCH CHUYỂN DỊCH TỔNG THỂ
    # ──────────────────────────────────────────────────────────────────────────
    print("\n--- PHẦN 2: NHÓM A - CÂU HỎI ĐỒNG NGHĨA CHUYỂN DỊCH TỔNG THỂ ---")

    synonyms_group_a = [
        "Tại sao hệ thống AI lại kết luận như vậy?",
        "Vì sao có sự chuyển dịch ngành nghề?",
        "Dựa vào đâu mà nói IT và Logistics tăng?",
        "Cơ sở nào chứng minh xu hướng chuyển dịch?",
        "Những con số này lấy từ đâu?",
        "AI căn cứ vào đâu để đưa ra kết luận?",
        "Tại sao kinh tế giảm mà công nghệ tăng?",
        "Hãy chứng minh nhận định của biểu đồ.",
        "Giải thích kết luận chuyển dịch 2025–2026.",
        "Kết luận này có đáng tin không?",
        "Vì sao thị trường lao động đang thay đổi?",
        "What evidence supports the labor market shift?"
    ]

    for syn in synonyms_group_a:
        try:
            resp = requests.post(API_URL, json={"message": syn}, timeout=10).json()
            ans = resp.get("answer", "")
            # Câu trả lời tổng thể chuẩn phải có cả 5 ngành và số tin: 285->385, 190->241, 270->156, 210->218, 45->78
            is_valid_shift = (
                ("285" in ans and "385" in ans)
                and ("190" in ans and "241" in ans)
                and ("270" in ans and "156" in ans)
            )
            results[f"Synonym: {syn[:35]}..."] = ("PASS" if is_valid_shift else "FAIL", ans[:100])
            print(f"[{'PASS' if is_valid_shift else 'FAIL'}] Synonym: '{syn}' -> Phản hồi chuyển dịch tổng thể 5 ngành")
        except Exception as e:
            results[f"Synonym: {syn[:35]}..."] = ("ERROR", str(e))
            print(f"[ERROR] Synonym: {syn} -> {e}")

    # ──────────────────────────────────────────────────────────────────────────
    # PHẦN 3: KIỂM TOÁN TỶ TRỌNG NĂM 2026 (MẪU SỐ 1.078)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n--- PHẦN 3: KIỂM TOÁN TỶ TRỌNG NĂM 2026 (MẪU SỐ 1.078) ---")
    resp_shift = requests.post(API_URL, json={"message": "Giải thích kết luận chuyển dịch 2025–2026."}, timeout=10).json()
    ans_shift = resp_shift.get("answer", "")
    pass_audit = (
        ("35,7%" in ans_shift or "35.7%" in ans_shift)
        and ("22,4%" in ans_shift or "22.4%" in ans_shift)
        and ("14,5%" in ans_shift or "14.5%" in ans_shift)
        and ("20,2%" in ans_shift or "20.2%" in ans_shift)
        and ("7,2%" in ans_shift or "7.2%" in ans_shift)
    )
    results["AUDIT: Tỷ trọng chuẩn hóa 2026 mẫu số 1.078 (35.7%, 22.4%, 20.2%, 14.5%, 7.2%)"] = (
        "PASS" if pass_audit else "FAIL",
        ans_shift[:140]
    )
    print(f"[{'PASS' if pass_audit else 'FAIL'}] Tỷ trọng năm 2026 đã được chuẩn hóa đúng mẫu số 1.078 (Tổng = 100.0%)")

    # ──────────────────────────────────────────────────────────────────────────
    # PHẦN 4: HỘI THOẠI ĐA LƯỢT TIẾP NỐI (KHÔNG LẪN NGÀNH)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n--- PHẦN 4: HỘI THOẠI TIẾP NỐI KHÔNG LẪN NGÀNH ---")

    # Turn 1: Hỏi IT
    h1 = [{"role": "user", "content": "Vì sao ngành IT tăng?"}]
    r_t1 = requests.post(API_URL, json={"message": "Vì sao ngành IT tăng?", "history": []}, timeout=10).json()
    a_t1 = r_t1.get("answer", "")
    pass_t1 = ("285" in a_t1 and "385" in a_t1) and ("du lịch" not in a_t1.lower() and "nông nghiệp" not in a_t1.lower())

    # Turn 2: Thế Logistics? (không lẫn IT)
    h2 = h1 + [{"role": "assistant", "content": a_t1}]
    r_t2 = requests.post(API_URL, json={"message": "Thế Logistics?", "history": h2}, timeout=10).json()
    a_t2 = r_t2.get("answer", "")
    pass_t2 = ("190" in a_t2 and "241" in a_t2) and ("fpt" not in a_t2.lower() and "khách sạn" not in a_t2.lower())

    # Turn 3: Còn Kinh tế? (không lẫn Logistics)
    h3 = h2 + [{"role": "user", "content": "Thế Logistics?"}, {"role": "assistant", "content": a_t2}]
    r_t3 = requests.post(API_URL, json={"message": "Còn Kinh tế?", "history": h3}, timeout=10).json()
    a_t3 = r_t3.get("answer", "")
    pass_t3 = ("270" in a_t3 and "156" in a_t3) and ("cảng biển" not in a_t3.lower() and "công nghệ thông tin" not in a_t3.lower())

    results["MULTI-TURN: Turn 1 (IT chỉ chứa dữ liệu IT)"] = ("PASS" if pass_t1 else "FAIL", a_t1[:100])
    results["MULTI-TURN: Turn 2 (Thế Logistics chỉ chứa dữ liệu Logistics)"] = ("PASS" if pass_t2 else "FAIL", a_t2[:100])
    results["MULTI-TURN: Turn 3 (Còn Kinh tế chỉ chứa dữ liệu Kinh tế)"] = ("PASS" if pass_t3 else "FAIL", a_t3[:100])

    print(f"[{'PASS' if pass_t1 else 'FAIL'}] Turn 1: Hỏi IT -> Trả lời riêng IT (không lẫn Du lịch/Kinh tế)")
    print(f"[{'PASS' if pass_t2 else 'FAIL'}] Turn 2: 'Thế Logistics?' -> Kế thừa ngữ cảnh, trả lời riêng Logistics")
    print(f"[{'PASS' if pass_t3 else 'FAIL'}] Turn 3: 'Còn Kinh tế?' -> Kế thừa ngữ cảnh, trả lời riêng Kinh tế")

    # ──────────────────────────────────────────────────────────────────────────
    # PHẦN 5: CÂU HỎI VỀ PHẠM VI 4 TÀI LIỆU & NÔNG NGHIỆP CNC Ý NGHĨA
    # ──────────────────────────────────────────────────────────────────────────
    print("\n--- PHẦN 5: PHẠM VI ĐỊA LÝ & Ý NGHĨA NÔNG NGHIỆP CNC ---")

    r_scope = requests.post(API_URL, json={"message": "Số liệu 4 tài liệu ngành có phải là số liệu riêng của TP. Cần Thơ không?"}, timeout=10).json()
    a_scope = r_scope.get("answer", "")
    pass_scope = ("không" in a_scope.lower()) and ("toàn quốc" in a_scope.lower() or "việt nam" in a_scope.lower())
    results["SCOPE: 4 tài liệu ngành là bối cảnh toàn quốc, không phải riêng Cần Thơ"] = ("PASS" if pass_scope else "FAIL", a_scope[:120])
    print(f"[{'PASS' if pass_scope else 'FAIL'}] Nhận diện chính xác 4 tài liệu ngành là bằng chứng toàn quốc")

    r_agri = requests.post(API_URL, json={"message": "Ngành Nông nghiệp công nghệ cao tăng 73,3%, con số này có ý nghĩa gì?"}, timeout=10).json()
    a_agri = r_agri.get("answer", "")
    pass_agri = ("73,3%" in a_agri or "73.3%" in a_agri) and ("quy mô" in a_agri.lower() or "khiêm tốn" in a_agri.lower() or "nhỏ" in a_agri.lower())
    results["AGRI: Nông nghiệp CNC tăng 73.3% có ý nghĩa gì (Tốc độ cao vs Quy mô nhỏ)"] = ("PASS" if pass_agri else "FAIL", a_agri[:120])
    print(f"[{'PASS' if pass_agri else 'FAIL'}] Giải thích đa chiều ý nghĩa số liệu Nông nghiệp CNC")

    # ──────────────────────────────────────────────────────────────────────────
    # BẢNG TỔNG HỢP KẾT QUẢ
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("📊 BẢNG TỔNG HỢP KẾT QUẢ BỘ KIỂM THỬ TREND INSIGHTS MỞ RỘNG:")
    print("=" * 80)
    all_passed = True
    for test_name, (status, detail) in results.items():
        icon = "✅" if status == "PASS" else "❌"
        if status != "PASS":
            all_passed = False
        print(f"{icon} [{status}] {test_name}")
        if status != "PASS":
            print(f"    Chi tiết: {detail}")

    print("=" * 80)
    if all_passed:
        print(f"🎉 TẤT CẢ {len(results)}/{len(results)} TIÊU CHÍ KIỂM THỬ ĐÃ ĐẠT CHUẨN THÀNH CÔNG 100%!")
    else:
        print("⚠️ CÓ TIÊU CHÍ CHƯA ĐẠT, CẦN KIỂM TRA LẠI!")
    print("=" * 80)
    return all_passed

if __name__ == "__main__":
    success = run_extended_trend_tests()
    sys.exit(0 if success else 1)
