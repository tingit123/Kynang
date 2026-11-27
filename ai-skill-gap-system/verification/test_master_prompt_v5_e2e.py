"""
test_master_prompt_v5_e2e.py
Bộ kiểm thử tự động toàn diện cho MASTER PROMPT V5.1, V5.2 và V5.3 — SKILLLED LAB
Bao gồm Test A đến Test L:
  - Test A: Bảo toàn 100% dữ liệu 2025 (3.000 JP · 1.500 CV · 4 ngành · 3 địa bàn)
  - Test B: Bảo toàn 100% dữ liệu 2026 sạch (1.000 JD clean · 1.500 CV)
  - Test C: Tầng 1 Staging (jobs_raw, cvs_raw, dedup_hash)
  - Test D: Crawler Job Lifecycle (Start, Live Progress, Graceful Stop)
  - Test E: Deduplication Analysis Engine
  - Test F: Pipeline Làm Sạch 3NF (Positions, Companies, Whitelist 860 Skills)
  - Test G: Quality Gate 5 Tiêu Chí
  - Test H: Export Clean JSON & SHA256
  - Test I: Cloud Sync Manifest Engine
  - Test J: Xuất Bản Dashboard Q4/2026 (reporting_datasets PUBLISHED)
  - Test K: Dashboard Analytics & Period / Location Consistency
  - Test L: Master Prompt V5.3 Live Sync Log, SSE Streaming & Duration Control
"""
import urllib.request
import json
import time
import pymysql

API_BASE = "http://127.0.0.1:8000"
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"
DB_PASS = "Xloc3805no!"
DB_NAME = "skill_intelligence"

def run_tests():
    print("=" * 80)
    print("BẮT ĐẦU KIỂM THỬ TOÀN DIỆN MASTER PROMPT V5.1 -> V5.3 (TESTS A -> L)")
    print("=" * 80)

    results = {}

    # -------------------------------------------------------------------------
    # TEST A: BẢO TOÀN DỮ LIỆU LỊCH SỬ TÁI DỰNG 2025
    # -------------------------------------------------------------------------
    print("\n[TEST A] Kiểm tra bảo toàn dữ liệu lịch sử tái dựng 2025...")
    conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME, autocommit=True)
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM historical_jobs_2025")
        c_j2025 = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM historical_workers_2025")
        c_w2025 = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM historical_job_skills_2025")
        c_js2025 = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM historical_worker_skills_2025")
        c_ws2025 = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM historical_skill_analytics")
        c_sa2025 = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT location_id) FROM historical_period_analytics WHERE location_id != 'all'")
        loc_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM historical_industry_analytics WHERE industry_code = 'agriculture' OR industry_name_vi LIKE '%Nông nghiệp%'")
        agri_count = cur.fetchone()[0]

    test_a_pass = (c_j2025 == 3000 and c_w2025 == 1500 and c_js2025 == 59484 and c_ws2025 == 22098 and c_sa2025 == 5503 and loc_count == 3 and agri_count == 0)
    results["TEST_A"] = {
        "passed": test_a_pass,
        "details": f"2025 Jobs: {c_j2025}/3000, 2025 CVs: {c_w2025}/1500, JobSkills: {c_js2025}/59484, WorkerSkills: {c_ws2025}/22098, SkillAnalytics: {c_sa2025}/5503, Locs: {loc_count}/3, Agri: {agri_count}/0"
    }
    print(f"  -> {'PASS ✅' if test_a_pass else 'FAIL ❌'}: {results['TEST_A']['details']}")

    # -------------------------------------------------------------------------
    # TEST B: BẢO TOÀN DỮ LIỆU SẠCH 2026 (Q2)
    # -------------------------------------------------------------------------
    print("\n[TEST B] Kiểm tra bảo toàn dữ liệu sạch quan sát thực tế 2026...")
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM jobs WHERE job_id <= 1000")
        c_clean_j = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM workers")
        c_clean_w = cur.fetchone()[0]

    test_b_pass = (c_clean_j == 1000 and c_clean_w == 1500)
    results["TEST_B"] = {
        "passed": test_b_pass,
        "details": f"Clean 2026 Jobs: {c_clean_j}/1000, Workers: {c_clean_w}/1500"
    }
    print(f"  -> {'PASS ✅' if test_b_pass else 'FAIL ❌'}: {results['TEST_B']['details']}")

    # -------------------------------------------------------------------------
    # TEST C: TẦNG 1 STAGING (jobs_raw, cvs_raw, dedup_hash)
    # -------------------------------------------------------------------------
    print("\n[TEST C] Kiểm tra Tầng 1 Staging (jobs_raw, cvs_raw, dedup_hash)...")
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*), COUNT(dedup_hash) FROM jobs_raw")
        tot_raw_j, hash_raw_j = cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM cvs_raw")
        tot_raw_cv = cur.fetchone()[0]

    test_c_pass = (tot_raw_j >= 3000 and hash_raw_j >= 3000 and tot_raw_cv == 1500)
    results["TEST_C"] = {
        "passed": test_c_pass,
        "details": f"jobs_raw total: {tot_raw_j}, dedup_hash populated: {hash_raw_j}, cvs_raw total: {tot_raw_cv}"
    }
    print(f"  -> {'PASS ✅' if test_c_pass else 'FAIL ❌'}: {results['TEST_C']['details']}")

    # -------------------------------------------------------------------------
    # TEST D: CRAWLER LIFECYCLE (Start, Progress, Stop)
    # -------------------------------------------------------------------------
    print("\n[TEST D] Kiểm tra Vòng đời tác vụ Cào (Start, Progress, Graceful Stop)...")
    job_id = None
    try:
        # Start
        payload = json.dumps({
            "source_platform": "TopCV",
            "industry": "IT",
            "location": "all",
            "period_code": "2026_Q4",
            "target_limit": 50,
            "duration_minutes": 5,
            "data_type": "JP"
        }).encode("utf-8")
        req = urllib.request.Request(f"{API_BASE}/api/crawler/jobs/start", data=payload, headers={"Content-Type": "application/json"}, method="POST")
        res = json.loads(urllib.request.urlopen(req).read())
        job_id = res.get("job_id")
        print(f"    Started Job #{job_id}: status={res.get('status')}, code={res.get('job_code')}")

        time.sleep(1.5)

        # Status
        st = json.loads(urllib.request.urlopen(f"{API_BASE}/api/crawler/jobs/{job_id}/status").read())
        print(f"    Polling status: {st.get('status')}, progress={st.get('progress_pct')}%, scanned={st.get('scanned_count')}")

        # Stop
        req_stop = urllib.request.Request(f"{API_BASE}/api/crawler/jobs/{job_id}/stop", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        stop_res = json.loads(urllib.request.urlopen(req_stop).read())
        print(f"    Stop response: {stop_res}")

        time.sleep(1)
        st_final = json.loads(urllib.request.urlopen(f"{API_BASE}/api/crawler/jobs/{job_id}/status").read())
        print(f"    Final status: {st_final.get('status')}")

        test_d_pass = (job_id is not None and st_final.get("status") in ("stopped", "completed", "stopping"))
        results["TEST_D"] = {
            "passed": test_d_pass,
            "details": f"Job #{job_id} lifecycle passed, final status: {st_final.get('status')}"
        }
    except Exception as e:
        results["TEST_D"] = {"passed": False, "details": str(e)}
    print(f"  -> {'PASS ✅' if results['TEST_D']['passed'] else 'FAIL ❌'}: {results['TEST_D']['details']}")

    # -------------------------------------------------------------------------
    # TEST E: DEDUPLICATION ENGINE
    # -------------------------------------------------------------------------
    print("\n[TEST E] Kiểm tra Engine Khử Trùng Lặp Lakehouse...")
    try:
        req = urllib.request.Request(f"{API_BASE}/api/crawler/dedup/analyze", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        dedup_res = json.loads(urllib.request.urlopen(req).read())
        test_e_pass = (dedup_res.get("total_raw_jobs", 0) > 0 and dedup_res.get("unique_records", 0) > 0)
        results["TEST_E"] = {
            "passed": test_e_pass,
            "details": f"Total raw: {dedup_res.get('total_raw_jobs')}, Unique: {dedup_res.get('unique_records')}, Dup clusters: {dedup_res.get('duplicate_records')}"
        }
    except Exception as e:
        results["TEST_E"] = {"passed": False, "details": str(e)}
    print(f"  -> {'PASS ✅' if results['TEST_E']['passed'] else 'FAIL ❌'}: {results['TEST_E']['details']}")

    # -------------------------------------------------------------------------
    # TEST F: CLEANING 3NF & ESCO / WHITELIST SKILLS
    # -------------------------------------------------------------------------
    print("\n[TEST F] Kiểm tra Pipeline Làm Sạch 3NF (Positions, Companies, Whitelist 860 Skills)...")
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM jobs WHERE job_id > 1000")
            c_cleaned = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM job_skills WHERE job_id > 1000")
            c_skills = cur.fetchone()[0]
        test_f_pass = (c_cleaned == 80 and c_skills > 0)
        results["TEST_F"] = {
            "passed": test_f_pass,
            "details": f"Cleaned Q4 jobs in 3NF: {c_cleaned}/80, Skills linked: {c_skills}"
        }
    except Exception as e:
        results["TEST_F"] = {"passed": False, "details": str(e)}
    print(f"  -> {'PASS ✅' if results['TEST_F']['passed'] else 'FAIL ❌'}: {results['TEST_F']['details']}")

    # -------------------------------------------------------------------------
    # TEST G: QUALITY GATE (5 TIÊU CHÍ)
    # -------------------------------------------------------------------------
    print("\n[TEST G] Kiểm tra Cổng Kiểm Định Chất Lượng (Quality Gate 5 Tiêu Chí)...")
    try:
        req = urllib.request.Request(f"{API_BASE}/api/crawler/quality-gate", data=json.dumps({"batch_code": "BATCH_2026_Q4_INGEST"}).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        qg_res = json.loads(urllib.request.urlopen(req).read())
        checks = qg_res.get("checks", [])
        all_passed = all(c.get("passed") for c in checks) and len(checks) >= 5
        test_g_pass = (qg_res.get("overall_passed") == True and all_passed)
        results["TEST_G"] = {
            "passed": test_g_pass,
            "details": f"Passed {sum(1 for c in checks if c.get('passed'))}/{len(checks)} criteria. Overall: {qg_res.get('overall_passed')}"
        }
    except Exception as e:
        results["TEST_G"] = {"passed": False, "details": str(e)}
    print(f"  -> {'PASS ✅' if results['TEST_G']['passed'] else 'FAIL ❌'}: {results['TEST_G']['details']}")

    # -------------------------------------------------------------------------
    # TEST H: EXPORT CLEAN JSON & SHA256
    # -------------------------------------------------------------------------
    print("\n[TEST H] Kiểm tra Xuất Bản File JSON Sạch & Mã Băm SHA256...")
    try:
        req = urllib.request.Request(f"{API_BASE}/api/crawler/export-json", data=json.dumps({"batch_code": "BATCH_2026_Q4_INGEST"}).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        exp_res = json.loads(urllib.request.urlopen(req).read())
        test_h_pass = (exp_res.get("jobs_exported", 0) > 0 and len(exp_res.get("jobs_sha256", "")) == 64 and len(exp_res.get("cvs_sha256", "")) == 64)
        results["TEST_H"] = {
            "passed": test_h_pass,
            "details": f"Jobs: {exp_res.get('jobs_exported')} (SHA: {exp_res.get('jobs_sha256')[:10]}...), CVs: {exp_res.get('cvs_exported')} (SHA: {exp_res.get('cvs_sha256')[:10]}...)"
        }
    except Exception as e:
        results["TEST_H"] = {"passed": False, "details": str(e)}
    print(f"  -> {'PASS ✅' if results['TEST_H']['passed'] else 'FAIL ❌'}: {results['TEST_H']['details']}")

    # -------------------------------------------------------------------------
    # TEST I: CLOUD SYNC MANIFEST ENGINE
    # -------------------------------------------------------------------------
    print("\n[TEST I] Kiểm tra Đồng Bộ Cloud Manifest...")
    try:
        req = urllib.request.Request(f"{API_BASE}/api/crawler/cloud-sync", data=json.dumps({"batch_code": "BATCH_2026_Q2_VERIFIED"}).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        sync_res = json.loads(urllib.request.urlopen(req).read())
        test_i_pass = (sync_res.get("integrity_verified") == True and "sync_version" in sync_res)
        results["TEST_I"] = {
            "passed": test_i_pass,
            "details": f"Version: {sync_res.get('sync_version')}, Status: {sync_res.get('sync_status')}"
        }
    except Exception as e:
        results["TEST_I"] = {"passed": False, "details": str(e)}
    print(f"  -> {'PASS ✅' if results['TEST_I']['passed'] else 'FAIL ❌'}: {results['TEST_I']['details']}")

    # -------------------------------------------------------------------------
    # TEST J: XUẤT BẢN DASHBOARD Q4/2026
    # -------------------------------------------------------------------------
    print("\n[TEST J] Kiểm tra Xuất Bản Lên Dashboard Kỳ Q4/2026...")
    try:
        req = urllib.request.Request(f"{API_BASE}/api/crawler/publish-dashboard", data=json.dumps({"batch_code": "BATCH_2026_Q4_INGEST", "target_period": "2026_Q4"}).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        pub_res = json.loads(urllib.request.urlopen(req).read())
        test_j_pass = (pub_res.get("success") == True and pub_res.get("status") == "PUBLISHED")
        results["TEST_J"] = {
            "passed": test_j_pass,
            "details": f"Target: {pub_res.get('target_period')}, Status: {pub_res.get('status')}, Cleaned: {pub_res.get('cleaned_jobs_count')}"
        }
    except Exception as e:
        results["TEST_J"] = {"passed": False, "details": str(e)}
    print(f"  -> {'PASS ✅' if results['TEST_J']['passed'] else 'FAIL ❌'}: {results['TEST_J']['details']}")

    # -------------------------------------------------------------------------
    # TEST K: DASHBOARD ANALYTICS & CONSISTENCY (2025 vs 2026)
    # -------------------------------------------------------------------------
    print("\n[TEST K] Kiểm tra Dashboard Analytics & Đối chiếu số liệu...")
    try:
        # 2025_ALL
        d2025 = json.loads(urllib.request.urlopen(f"{API_BASE}/api/dashboard/analytics?data_source=crawler&location_id=all&period=2025_ALL&skill_type=ALL").read())
        kpi2025 = d2025.get("kpi", {})
        tj2025 = kpi2025.get("total_jobs", 0)
        tc2025 = kpi2025.get("total_surveys", 0)

        # 2026_Q2
        d2026 = json.loads(urllib.request.urlopen(f"{API_BASE}/api/dashboard/analytics?data_source=crawler&location_id=all&period=2026_Q2&skill_type=ALL").read())
        kpi2026 = d2026.get("kpi", {})
        tj2026 = kpi2026.get("total_jobs", 0)
        tc2026 = kpi2026.get("total_surveys", 0)

        # Locations 2025
        locs2025 = json.loads(urllib.request.urlopen(f"{API_BASE}/api/dashboard/locations?period=2025_ALL").read())
        loc_map = {l["id"]: l["job_count"] for l in locs2025}
        sum_locs = loc_map.get("HN", 0) + loc_map.get("HCM", 0) + loc_map.get("CT", 0)

        test_k_pass = (tj2025 == 3000 and tc2025 == 1500 and tj2026 == 1000 and sum_locs == 3000)
        results["TEST_K"] = {
            "passed": test_k_pass,
            "details": f"2025 ALL: {tj2025} JPs · {tc2025} CVs | 2026 Q2: {tj2026} JPs · {tc2026} CVs | 2025 HN+HCM+CT = {sum_locs}/3000"
        }
    except Exception as e:
        results["TEST_K"] = {"passed": False, "details": str(e)}
    print(f"  -> {'PASS ✅' if results['TEST_K']['passed'] else 'FAIL ❌'}: {results['TEST_K']['details']}")

    # -------------------------------------------------------------------------
    # TEST L: MASTER PROMPT V5.3 (SSE STREAMING, CV CRAWL, DURATION, Q4 LOC ISOLATION)
    # -------------------------------------------------------------------------
    print("\n[TEST L] Kiểm tra Tính Năng Mới Master Prompt V5.3 (SSE, CV Crawling, Q4 Isolation)...")
    try:
        # 1. Test SSE Endpoint
        req_sse = urllib.request.Request(f"{API_BASE}/api/crawler/stream")
        with urllib.request.urlopen(req_sse, timeout=5) as sse_resp:
            sse_ct = sse_resp.headers.get("Content-Type", "")
            sse_ok = ("text/event-stream" in sse_ct and sse_resp.status == 200)

        # 2. Test CV Crawling & Duration parameter
        payload_cv = json.dumps({
            "source_platform": "Resumes",
            "industry": "ALL",
            "location": "all",
            "period_code": "2026_Q4",
            "target_limit": 30,
            "duration_minutes": 15,
            "data_type": "CV"
        }).encode("utf-8")
        req_cv = urllib.request.Request(f"{API_BASE}/api/crawler/jobs/start", data=payload_cv, headers={"Content-Type": "application/json"}, method="POST")
        res_cv = json.loads(urllib.request.urlopen(req_cv).read())
        cv_job_id = res_cv.get("job_id")
        cv_code = res_cv.get("job_code", "")

        time.sleep(1)
        # Check logs for this CV job
        logs_cv = json.loads(urllib.request.urlopen(f"{API_BASE}/api/crawler/logs?job_id={cv_job_id}&limit=10").read())
        has_cv_logs = len(logs_cv) > 0 and any("CV" in l.get("message", "") for l in logs_cv)

        # Stop CV job
        req_stop_cv = urllib.request.Request(f"{API_BASE}/api/crawler/jobs/{cv_job_id}/stop", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        urllib.request.urlopen(req_stop_cv)

        # 3. Test Location Isolation: Q1 (0 jobs), Q3 (0 jobs), Q4 (80 jobs)
        locs_q1 = json.loads(urllib.request.urlopen(f"{API_BASE}/api/dashboard/locations?period=2026_Q1").read())
        locs_q3 = json.loads(urllib.request.urlopen(f"{API_BASE}/api/dashboard/locations?period=2026_Q3").read())
        locs_q4 = json.loads(urllib.request.urlopen(f"{API_BASE}/api/dashboard/locations?period=2026_Q4").read())

        q1_zero = (len(locs_q1) == 1 and locs_q1[0].get("job_count") == 0 and not locs_q1[0].get("has_data"))
        q3_zero = (len(locs_q3) == 1 and locs_q3[0].get("job_count") == 0 and not locs_q3[0].get("has_data"))
        q4_80 = (locs_q4[0].get("job_count") == 80 and locs_q4[0].get("has_data") == True)

        test_l_pass = (sse_ok and cv_code.startswith("CRAWL_") and has_cv_logs and q1_zero and q3_zero and q4_80)
        results["TEST_L"] = {
            "passed": test_l_pass,
            "details": f"SSE Stream: {sse_ok} | CV Job: {cv_code} (logs={len(logs_cv)}) | Q1 zero: {q1_zero} | Q3 zero: {q3_zero} | Q4 total 80: {q4_80}"
        }
    except Exception as e:
        results["TEST_L"] = {"passed": False, "details": str(e)}
    print(f"  -> {'PASS ✅' if results['TEST_L']['passed'] else 'FAIL ❌'}: {results['TEST_L']['details']}")

    conn.close()

    # Overall Summary
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r["passed"])
    print("\n" + "=" * 80)
    print(f"TỔNG KẾT KIỂM THỬ: {passed_tests}/{total_tests} TESTS PASS ({round((passed_tests/total_tests)*100, 1)}%)")
    print("=" * 80)
    return results

if __name__ == "__main__":
    run_tests()
