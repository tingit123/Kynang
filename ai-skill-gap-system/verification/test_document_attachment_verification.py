"""
Test Suite: Xác minh tính năng Tự động đính kèm tài liệu chứng minh cho AI Chatbox – Trend Insights
Theo đúng 10 tiêu chí nghiệm thu Section 7 trong yêu cầu của người dùng.
"""

import sys
import os
import unittest
import requests

API_URL = "http://localhost:8000/api/insights/chat"
DOCS_API_URL = "http://localhost:8000/api/insights/documents"
DASHBOARD_URL = "http://localhost:8080"


class TestDocumentAttachmentVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Kiểm tra kết nối API
        try:
            r = requests.get(f"{DOCS_API_URL}", timeout=5)
            assert r.status_code == 200, f"Docs API status {r.status_code}"
        except Exception as e:
            raise RuntimeError(f"Không thể kết nối đến Backend Core API: {e}")

    def test_case_01_it_attachment(self):
        """1. Hỏi IT: Đính kèm đúng IT_CongNghe.docx, không lẫn file khác, có số liệu 35.1%."""
        payload = {"message": "Tại sao ngành IT tăng trưởng 35,1%?"}
        res = requests.post(API_URL, json=payload, timeout=8).json()
        
        answer = res.get("answer", "")
        attachments = res.get("attachments", [])
        
        self.assertIn("35", answer)
        self.assertIn("ITviec", answer)
        self.assertEqual(len(attachments), 1, "Chỉ được đính kèm đúng 1 tài liệu IT")
        self.assertEqual(attachments[0]["filename"], "IT_CongNghe.docx")
        self.assertIn("/api/insights/documents/it/download", attachments[0]["download_url"])
        self.assertNotIn("C:\\", answer, "Không được để lộ đường dẫn ổ đĩa C:\\")

    def test_case_02_logistics_attachment(self):
        """2. Hỏi Logistics: Đính kèm Logistics_XNK_FINAL_HOAN_CHINH.docx, có bối cảnh XNK."""
        payload = {"message": "Vì sao Logistics tăng mạnh?"}
        res = requests.post(API_URL, json=payload, timeout=8).json()
        
        answer = res.get("answer", "")
        attachments = res.get("attachments", [])
        
        self.assertIn("26,8", answer.replace(".", ","))
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0]["filename"], "Logistics_XNK_FINAL_HOAN_CHINH.docx")
        self.assertIn("/api/insights/documents/logistics/download", attachments[0]["download_url"])

    def test_case_03_finance_attachment(self):
        """3. Hỏi Kinh tế: Đính kèm KinhTe_TaiChinh_Final.docx, giải thích tự động hóa/năng suất."""
        payload = {"message": "Tại sao ngành Kinh tế & Kế toán giảm tuyển dụng?"}
        res = requests.post(API_URL, json=payload, timeout=8).json()
        
        answer = res.get("answer", "")
        attachments = res.get("attachments", [])
        
        self.assertIn("42,2", answer.replace(".", ","))
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0]["filename"], "KinhTe_TaiChinh_Final.docx")
        self.assertIn("/api/insights/documents/finance/download", attachments[0]["download_url"])

    def test_case_04_tourism_attachment(self):
        """4. Hỏi Du lịch: Đính kèm DuLich_KhachSan_Final.docx, giải thích tối ưu năng suất/mùa vụ."""
        payload = {"message": "Tại sao ngành Du lịch chỉ tăng 3,8% dù lượng khách tăng mạnh?"}
        res = requests.post(API_URL, json=payload, timeout=8).json()
        
        answer = res.get("answer", "")
        attachments = res.get("attachments", [])
        
        self.assertIn("3,8", answer.replace(".", ","))
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0]["filename"], "DuLich_KhachSan_Final.docx")
        self.assertIn("/api/insights/documents/tourism/download", attachments[0]["download_url"])

    def test_case_05_shift_overview_attachments(self):
        """5. Hỏi chuyển dịch tổng thể: Đính kèm đúng 3 file liên quan (IT, Logistics, Kinh tế)."""
        payload = {"message": "Vì sao hệ thống kết luận thị trường lao động đang chuyển dịch sang IT và Logistics?"}
        res = requests.post(API_URL, json=payload, timeout=8).json()
        
        attachments = res.get("attachments", [])
        filenames = [a["filename"] for a in attachments]
        
        self.assertEqual(len(attachments), 3, "Chuyển dịch tổng thể phải đính kèm 3 file ngành trực tiếp")
        self.assertIn("IT_CongNghe.docx", filenames)
        self.assertIn("Logistics_XNK_FINAL_HOAN_CHINH.docx", filenames)
        self.assertIn("KinhTe_TaiChinh_Final.docx", filenames)
        self.assertNotIn("So_Lieu_Bieu_do.docx", filenames, "Tuyệt đối không đính kèm So_Lieu_Bieu_do.docx")

    def test_case_06_level_1_no_attachments(self):
        """6. Hỏi số liệu đơn giản (Level 1): KHÔNG đính kèm tài liệu."""
        payload = {"message": "Logistics tăng bao nhiêu?"}
        res = requests.post(API_URL, json=payload, timeout=8).json()
        
        attachments = res.get("attachments", [])
        self.assertEqual(len(attachments), 0, "Câu hỏi Level 1 không được tự động đính kèm file dài dòng")

    def test_case_07_evidence_request_synonyms(self):
        """7. Hỏi bằng chứng / nguồn (Synonyms): Nhận diện đúng và đính kèm tài liệu."""
        synonyms = [
            "Lấy gì chứng minh?",
            "Dựa trên tài liệu nào?",
            "Có bằng chứng không?",
            "Cho tôi xem nguồn.",
            "Số liệu này từ đâu?",
            "Cho tôi tải tài liệu nghiên cứu."
        ]
        for query in synonyms:
            res = requests.post(API_URL, json={"message": query}, timeout=8).json()
            attachments = res.get("attachments", [])
            self.assertGreaterEqual(len(attachments), 1, f"Câu hỏi '{query}' phải đính kèm tài liệu chứng minh")
            filenames = [a["filename"] for a in attachments]
            self.assertNotIn("So_Lieu_Bieu_do.docx", filenames)

    def test_case_08_agritech_no_fake_docs(self):
        """8. Nông nghiệp CNC: Trả lời từ biểu đồ, KHÔNG bịa docx, attachments = []."""
        payload = {"message": "Tại sao Nông nghiệp công nghệ cao tăng 73,3%?"}
        res = requests.post(API_URL, json=payload, timeout=8).json()
        
        answer = res.get("answer", "")
        attachments = res.get("attachments", [])
        
        self.assertIn("73", answer)
        self.assertEqual(len(attachments), 0, "Nông nghiệp CNC không có tài liệu riêng, không được tự chế")

    def test_case_09_multi_turn_dynamic_attachments(self):
        """9. Hội thoại đa lượt: Đính kèm thay đổi linh hoạt theo ngành được hỏi tiếp nối."""
        conv_id = f"test_conv_attach_{os.urandom(4).hex()}"
        
        # Turn 1: Hỏi IT
        r1 = requests.post(API_URL, json={"message": "Vì sao IT tăng 35,1%?", "conversation_id": conv_id}, timeout=8).json()
        att1 = [a["filename"] for a in r1.get("attachments", [])]
        self.assertEqual(att1, ["IT_CongNghe.docx"])
        
        # Turn 2: Hỏi tiếp Logistics
        h2 = [{"role": "user", "content": "Vì sao IT tăng 35,1%?"}, {"role": "assistant", "content": r1.get("answer", "")}]
        r2 = requests.post(API_URL, json={"message": "Còn Logistics?", "conversation_id": conv_id, "history": h2}, timeout=8).json()
        att2 = [a["filename"] for a in r2.get("attachments", [])]
        self.assertEqual(att2, ["Logistics_XNK_FINAL_HOAN_CHINH.docx"], "Turn 2 chỉ đính kèm Logistics, không lẫn IT")
        
        # Turn 3: Hỏi tiếp Kinh tế
        h3 = h2 + [{"role": "user", "content": "Còn Logistics?"}, {"role": "assistant", "content": r2.get("answer", "")}]
        r3 = requests.post(API_URL, json={"message": "Thế còn Kinh tế?", "conversation_id": conv_id, "history": h3}, timeout=8).json()
        att3 = [a["filename"] for a in r3.get("attachments", [])]
        self.assertEqual(att3, ["KinhTe_TaiChinh_Final.docx"], "Turn 3 chỉ đính kèm Kinh tế, không lẫn Logistics")

    def test_case_10_download_and_preview_endpoints(self):
        """10. Endpoint tải file thật và preview thật, chặn tuyệt đối So_Lieu_Bieu_do."""
        docs_to_check = [
            ("it", "IT_CongNghe.docx", 25544),
            ("logistics", "Logistics_XNK_FINAL_HOAN_CHINH.docx", 37432),
            ("tourism", "DuLich_KhachSan_Final.docx", 38660),
            ("finance", "KinhTe_TaiChinh_Final.docx", 38753)
        ]
        
        for doc_key, filename, expected_len in docs_to_check:
            # 1. Test Download endpoint
            dl_res = requests.get(f"{DOCS_API_URL}/{doc_key}/download", timeout=5)
            self.assertEqual(dl_res.status_code, 200, f"Download failed for {doc_key}")
            self.assertEqual(len(dl_res.content), expected_len, f"File size mismatch for {filename}")
            self.assertIn("attachment", dl_res.headers.get("content-disposition", ""))
            
            # 2. Test Preview endpoint
            prev_res = requests.get(f"{DOCS_API_URL}/{doc_key}/preview", timeout=5)
            self.assertEqual(prev_res.status_code, 200, f"Preview failed for {doc_key}")
            prev_data = prev_res.json().get("document", {})
            self.assertEqual(prev_data.get("filename"), filename)
            self.assertIn("summary", prev_data)
            self.assertGreater(len(prev_data.get("key_points", [])), 0)
            
            # 3. Test static Nginx endpoint on port 8080
            nginx_res = requests.head(f"{DASHBOARD_URL}/documents/{filename}", timeout=5)
            self.assertEqual(nginx_res.status_code, 200, f"Nginx static serve failed for {filename}")

        # Kiểm tra chặn tuyệt đối So_Lieu_Bieu_do
        bad_dl = requests.get(f"{DOCS_API_URL}/so_lieu_bieu_do/download", timeout=5)
        self.assertEqual(bad_dl.status_code, 404, "Phải trả về 404 cho So_Lieu_Bieu_do")
        
        bad_prev = requests.get(f"{DOCS_API_URL}/so_lieu_bieu_do/preview", timeout=5)
        self.assertEqual(bad_prev.status_code, 404, "Phải trả về 404 cho preview So_Lieu_Bieu_do")


if __name__ == "__main__":
    unittest.main(verbosity=2)
