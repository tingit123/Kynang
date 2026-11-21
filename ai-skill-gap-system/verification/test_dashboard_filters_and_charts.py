"""
Verification Suite: Hệ thống Biểu đồ & Logic Lọc Dữ liệu Dashboard – Skill Lens Lab
Kiểm thử:
1. Toàn bộ 10+ kịch bản lọc (Toàn quốc Q1/Q2/Q3/Q4/All 2026, 2025, Cần Thơ, Hà Nội, Đà Nẵng, tỉnh chưa có dữ liệu).
2. Kiểm chứng Toàn quốc = SUM từ các tỉnh độc lập (chống cộng trùng vùng, tính lại % từ tổng tử/mẫu).
3. Phân biệt rõ: Giá trị 0 thực tế vs Thiếu dữ liệu (NULL) vs Không có dữ liệu.
4. Kiểm chứng tính đồng bộ giữa KPI, Top 5 Shortage, Industry Pie, Quarterly Trend, Period Comparison, Soft Skills, Industries Detail.
5. Kiểm chứng Frontend HTML/JS không còn lỗi trục ngang 0%, 1%, 2%, 3%, 4% và không còn mapping giả sang tỉnh khác.
"""
import os
import sys
import unittest
from datetime import date
import requests

API_URL = "http://localhost:8000/api/dashboard/analytics"
DASHBOARD_URL = "http://localhost:8080/"

# Cho phép import trực tiếp service để unit-test công thức tổng hợp đa tỉnh
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "core-api-backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


class TestDashboardAnalyticsLiveAPI(unittest.TestCase):
    def _fetch(self, **params):
        r = requests.get(API_URL, params=params, timeout=10)
        self.assertEqual(r.status_code, 200, f"API lỗi {r.status_code} với params={params}")
        return r.json()

    def test_01_national_q1_2026_empty(self):
        """Kịch bản 1: Toàn quốc + Q1/2026 -> DB không có dữ liệu Q1/2026 -> Phải trống, không thay thế bằng quý khác."""
        d = self._fetch(location_id="all", period="2026_Q1")
        self.assertFalse(d["data_availability"]["has_data"])
        self.assertEqual(d["kpi"]["total_jobs"], 0)
        self.assertEqual(d["kpi"]["total_surveys"], 0)
        self.assertIsNone(d["kpi"]["avg_gap_pct"])
        self.assertEqual(d["top_shortage_skills"], [])
        self.assertEqual(d["industry_distribution"], [])
        self.assertTrue(d["data_availability"]["empty_message"])

    def test_02_national_q2_2026_partial_supply_null(self):
        """Kịch bản 2: Toàn quốc + Q2/2026 -> Có 274 tin tuyển dụng nhưng 0 khảo sát -> Demand thật, Supply & Gap phải NULL (không gán 0 giả)."""
        d = self._fetch(location_id="all", period="2026_Q2")
        self.assertTrue(d["data_availability"]["has_data"])
        self.assertTrue(d["data_availability"]["has_job_data"])
        self.assertFalse(d["data_availability"]["has_survey_data"])
        self.assertFalse(d["data_availability"]["has_gap_data"])
        self.assertGreater(d["kpi"]["total_jobs"], 0)
        self.assertEqual(d["kpi"]["total_surveys"], 0)
        self.assertIsNone(d["kpi"]["avg_gap_pct"])
        self.assertGreater(len(d["top_shortage_skills"]), 0)
        for s in d["top_shortage_skills"]:
            self.assertIsNotNone(s["demand"])
            self.assertIsNone(s["supply"], "Không được gán 0 giả cho Supply khi không có khảo sát trong Q2")
            self.assertIsNone(s["gap"], "Không được gán 0 giả cho Gap khi thiếu Supply")
        self.assertTrue(d["data_availability"]["partial_notice"])

    def test_03_national_q3_2026_full_data(self):
        """Kịch bản 3: Toàn quốc + Q3/2026 -> Có đủ cả Jobs & Surveys -> Demand, Supply và Gap = Demand - Supply chính xác."""
        d = self._fetch(location_id="all", period="2026_Q3")
        self.assertTrue(d["data_availability"]["has_gap_data"])
        self.assertGreater(d["kpi"]["total_jobs"], 0)
        self.assertGreater(d["kpi"]["total_surveys"], 0)
        self.assertEqual(len(d["top_shortage_skills"]), 5)
        for s in d["top_shortage_skills"]:
            self.assertIsNotNone(s["demand"])
            self.assertIsNotNone(s["supply"])
            self.assertAlmostEqual(s["gap"], round(s["demand"] - s["supply"], 1), places=1)
        # Kiểm tra tổng ngành trên biểu đồ tròn khớp chính xác KPI total_jobs (đồng bộ tuyệt đối)
        pie_sum = sum(x["count"] for x in d["industry_distribution"])
        self.assertEqual(pie_sum, d["kpi"]["total_jobs"])

    def test_04_national_full_year_2026_equals_sum_of_quarters(self):
        """Kịch bản 4: Toàn quốc + Toàn năm 2026 = SUM(Q1 + Q2 + Q3 + Q4) và tỷ lệ % tính lại từ tổng."""
        q_res = [self._fetch(location_id="all", period=f"2026_Q{q}") for q in (1, 2, 3, 4)]
        full = self._fetch(location_id="all", period="2026_ALL")

        sum_jobs = sum(x["kpi"]["total_jobs"] for x in q_res)
        sum_surveys = sum(x["kpi"]["total_surveys"] for x in q_res)
        self.assertEqual(full["kpi"]["total_jobs"], sum_jobs)
        self.assertEqual(full["kpi"]["total_surveys"], sum_surveys)

        # Kiểm tra quý khác nhau trả dữ liệu khác nhau (không cố định theo quý)
        self.assertNotEqual(q_res[1]["kpi"]["total_jobs"], q_res[2]["kpi"]["total_jobs"])
        self.assertNotEqual(q_res[2]["kpi"]["total_jobs"], q_res[3]["kpi"]["total_jobs"])

        # Kiểm tra từng kỹ năng trong Toàn năm 2026 được tính từ tổng tử/mẫu số
        for s in full["top_shortage_skills"]:
            expected_dem = round(s["demand_count"] / full["kpi"]["total_jobs"] * 100.0, 1)
            expected_sup = round(s["supply_count"] / full["kpi"]["total_surveys"] * 100.0, 1)
            self.assertAlmostEqual(s["demand"], expected_dem, places=1)
            self.assertAlmostEqual(s["supply"], expected_sup, places=1)
            self.assertAlmostEqual(s["gap"], round(expected_dem - expected_sup, 1), places=1)

    def test_05_hanoi_q3_2026_empty_no_fallback(self):
        """Kịch bản 5: Hà Nội + Q3/2026 -> DB hiện chưa có dữ liệu Hà Nội -> Biểu đồ phải trống, không lấy Toàn quốc hay Cần Thơ thay thế."""
        d = self._fetch(location_id="HN", period="2026_Q3")
        self.assertFalse(d["data_availability"]["has_data"])
        self.assertEqual(d["kpi"]["total_jobs"], 0)
        self.assertEqual(d["top_shortage_skills"], [])
        self.assertEqual(d["industry_distribution"], [])
        self.assertFalse(d["quarterly_trend"]["has_data"])

    def test_06_danang_q3_2026_empty_no_fallback(self):
        """Kịch bản 6: Đà Nẵng + Q3/2026 -> DB hiện chưa có dữ liệu Đà Nẵng -> Biểu đồ phải trống."""
        d = self._fetch(location_id="DN_CITY", period="2026_Q3")
        self.assertFalse(d["data_availability"]["has_data"])
        self.assertEqual(d["kpi"]["total_jobs"], 0)
        self.assertEqual(d["top_shortage_skills"], [])
        self.assertEqual(d["industry_distribution"], [])

    def test_07_unsurveyed_provinces_empty(self):
        """Kịch bản 7: Các tỉnh chưa có dữ liệu (An Giang, Hải Phòng, Lâm Đồng) -> Biểu đồ trống hoàn toàn."""
        for code in ("AG", "HP", "LD"):
            d = self._fetch(location_id=code, period="2026_Q3")
            self.assertFalse(d["data_availability"]["has_data"], f"Tỉnh {code} không có dữ liệu nhưng lại trả has_data=True")
            self.assertEqual(d["top_shortage_skills"], [])
            self.assertEqual(d["industry_distribution"], [])
            self.assertEqual(d["soft_skills"], [])

    def test_08_hanoi_q4_2026_empty(self):
        """Kịch bản 8: Hà Nội + Q4/2026 -> Biểu đồ trống."""
        d = self._fetch(location_id="HN", period="2026_Q4")
        self.assertFalse(d["data_availability"]["has_data"])
        self.assertEqual(d["top_shortage_skills"], [])

    def test_09_national_q4_2025_empty(self):
        """Kịch bản 9: Toàn quốc + Q4/2025 -> DB chưa có dữ liệu 2025 -> Biểu đồ trống."""
        d = self._fetch(location_id="all", period="2025_Q4")
        self.assertFalse(d["data_availability"]["has_data"])
        self.assertEqual(d["kpi"]["total_jobs"], 0)
        self.assertEqual(d["top_shortage_skills"], [])
        self.assertFalse(d["quarterly_trend"]["has_data"])

    def test_10_national_full_year_2025_empty(self):
        """Kịch bản 10: Toàn quốc + Toàn năm 2025 -> DB chưa có dữ liệu 2025 -> Biểu đồ trống."""
        d = self._fetch(location_id="all", period="2025_ALL")
        self.assertFalse(d["data_availability"]["has_data"])
        self.assertEqual(d["kpi"]["total_jobs"], 0)
        self.assertEqual(d["top_shortage_skills"], [])

    def test_11_cantho_matches_national_sum_of_independent_provinces(self):
        """Kiểm chứng Toàn quốc = SUM tất cả tỉnh độc lập có dữ liệu (không cộng trùng)."""
        nat = self._fetch(location_id="all", period="2026_Q3")
        provs = nat["data_availability"]["provinces_included"]
        self.assertGreater(len(provs), 0)
        self.assertEqual(nat["kpi"]["total_jobs"], sum(p["job_count"] for p in provs))
        self.assertEqual(nat["kpi"]["total_surveys"], sum(p["survey_count"] for p in provs))

    def test_12_frontend_horizontal_axis_and_no_fake_mapping(self):
        """Kiểm tra HTML Dashboard được phục vụ trên cổng 8080 có cấu hình trục ngang đúng và gọi /api/dashboard/analytics."""
        r = requests.get(DASHBOARD_URL, timeout=10)
        self.assertEqual(r.status_code, 200)
        html = r.text
        self.assertIn("/api/dashboard/analytics", html)
        self.assertIn("isHoriz\n            ? { x: valueAxisConfig, y: categoryAxisConfig }", html)
        self.assertIn("setChartEmptyState", html)
        self.assertIn("AbortController", html)
        self.assertIn('<option value="2026_Q4">', html)


class TestNationalAggregationMathUnit(unittest.TestCase):
    """Kiểm thử đơn vị: Không cộng trùng nhãn vùng & tính lại tỷ lệ % từ tổng tử/mẫu (không lấy trung bình cộng %)."""

    def test_anti_double_counting_and_weighted_ratio(self):
        from src.services.dashboard_analytics import compute_dashboard_analytics, normalize_province_code

        # Kiểm tra nhận diện nhãn vùng tổng hợp vs tỉnh độc lập
        self.assertEqual(normalize_province_code("Quận Ninh Kiều, Cần Thơ"), ("CT", False))
        self.assertEqual(normalize_province_code("Toàn quốc"), (None, True))
        self.assertEqual(normalize_province_code("ĐBSCL"), (None, True))
        self.assertEqual(normalize_province_code("Hà Nội"), ("HN", False))

        # Mock DB với 2 tỉnh độc lập (HN: 100 jobs / 50 Python = 50%; CT: 300 jobs / 30 Python = 10%)
        # + 1 dòng vùng tổng hợp ("Toàn quốc": 400 jobs) phải bị loại trừ!
        class FakeResult:
            def __init__(self, rows):
                self._rows = rows
            def fetchall(self):
                return self._rows

        class FakeSession:
            def execute(self, stmt):
                sql = str(stmt)
                if "FROM skill_catalog" in sql:
                    return FakeResult([(1, "Python", "IT")])
                if "FROM job_postings" in sql:
                    rows = []
                    # 100 jobs HN (id 1..100)
                    for i in range(1, 101):
                        rows.append((i, "Hà Nội", "IT", date(2026, 8, 10), 20, 30))
                    # 300 jobs CT (id 101..400)
                    for i in range(101, 401):
                        rows.append((i, "Cần Thơ", "IT", date(2026, 8, 12), 15, 25))
                    # 400 dòng vùng tổng hợp "Toàn quốc" (id 401..800) -> KHÔNG được cộng trùng!
                    for i in range(401, 801):
                        rows.append((i, "Toàn quốc", "IT", date(2026, 8, 12), 15, 25))
                    return FakeResult(rows)
                if "FROM survey_responses" in sql:
                    rows = []
                    # 50 surveys HN (id 1..50), 150 surveys CT (id 51..200) -> Tổng 200 surveys
                    for i in range(1, 51):
                        rows.append((i, "Công nghệ thông tin", "ĐH Bách Khoa Hà Nội", date(2026, 8, 15)))
                    for i in range(51, 201):
                        rows.append((i, "Công nghệ thông tin", "ĐH Cần Thơ", date(2026, 8, 15)))
                    return FakeResult(rows)
                if "FROM extracted_skills" in sql:
                    # 50 jobs Python ở HN (50%) + 30 jobs Python ở CT (10%) -> Tổng 80/400 = 20.0% (KHÔNG phải (50+10)/2 = 30%!)
                    rows = [(i, "Python") for i in range(1, 51)] + [(i, "Python") for i in range(101, 131)]
                    return FakeResult(rows)
                if "FROM survey_skill_ratings" in sql:
                    # 20 proficient ở HN (40%) + 20 proficient ở CT (13.3%) -> Tổng 40/200 = 20.0%
                    rows = [(i, 1, 80) for i in range(1, 21)] + [(i, 1, 80) for i in range(51, 71)]
                    return FakeResult(rows)
                return FakeResult([])

        res = compute_dashboard_analytics(FakeSession(), location_id="all", period="2026_Q3")
        # Chống cộng trùng vùng: tổng jobs = 100 + 300 = 400 (không phải 800!)
        self.assertEqual(res["kpi"]["total_jobs"], 400)
        self.assertEqual(res["kpi"]["total_surveys"], 200)
        self.assertEqual(res["data_availability"]["provinces_included_count"], 2)

        py = res["top_shortage_skills"][0]
        self.assertEqual(py["skill"], "Python")
        # 80 / 400 = 20.0% (tính từ tổng tử/mẫu, không phải trung bình cộng 30%)
        self.assertEqual(py["demand"], 20.0)
        # 40 / 200 = 20.0%
        self.assertEqual(py["supply"], 20.0)
        # Gap = 20.0 - 20.0 = 0.0 (giá trị 0 THỰC TẾ, không phải NULL!)
        self.assertEqual(py["gap"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
