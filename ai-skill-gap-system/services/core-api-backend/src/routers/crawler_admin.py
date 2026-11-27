"""
crawler_admin.py
API Router cho phân hệ Quản lý Auto-Crawler & Lakehouse Ingestion (Admin System)
"""
from typing import Optional, Dict, Any, List
import json
import queue
import asyncio
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from fastapi.responses import StreamingResponse
from src.services.crawler_lakehouse_service import CrawlerLakehouseService

router = APIRouter()
service = CrawlerLakehouseService()


@router.get("/status", tags=["Admin Crawler"])
def get_crawler_status():
    """Lấy tổng quan tình trạng Lakehouse 2 tầng, tiến độ cào, danh sách batch và nhật ký."""
    return service.get_crawler_status()


@router.get("/diagnostics/stopping-jobs", tags=["Admin Crawler"])
def get_stopping_jobs_diagnostic():
    """Kiểm tra chi tiết các job đang STOPPING/RUNNING, worker threads và tình trạng ghi dữ liệu jobs_raw."""
    return service.get_stopping_jobs_diagnostic()


@router.get("/stream", tags=["Admin Crawler"])
async def stream_crawler_logs():
    """Luồng sự kiện thời gian thực Server-Sent Events (SSE) cho Live Sync Log."""
    async def event_generator():
        q = service.subscribe_events()
        try:
            # Gửi sự kiện kết nối ban đầu
            yield f"event: connected\ndata: {json.dumps({'status': 'connected', 'message': 'Live Sync Log SSE stream connected.'})}\n\n"
            while True:
                try:
                    event = await asyncio.to_thread(q.get, timeout=12)
                    yield f"event: log\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"
                except queue.Empty:
                    # Ping định kỳ giữ kết nối không bị ngắt
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            service.unsubscribe_events(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/schedules", tags=["Admin Crawler"])
def get_crawler_schedules():
    """Danh sách lịch trình cào tự động và cấu hình chu kỳ."""
    return service.get_schedules()


@router.put("/schedules/{schedule_id}", tags=["Admin Crawler"])
def update_crawler_schedule(schedule_id: int, data: Dict[str, Any] = Body(...)):
    """Cập nhật cấu hình lịch trình cào (chu kỳ, kích hoạt, custom cron...)."""
    return service.update_schedule(schedule_id, data)


@router.post("/jobs/start", tags=["Admin Crawler"])
def start_crawl_job(params: Dict[str, Any] = Body(...)):
    """Kích hoạt tiến trình cào dữ liệu mới (JP/CV) theo thời lượng (5m..360m)."""
    res = service.start_crawl_job(params)
    return res


@router.post("/jobs/{job_id}/stop", tags=["Admin Crawler"])
def stop_crawl_job(job_id: int):
    """Dừng an toàn tác vụ cào dữ liệu mà không làm mất dữ liệu đã ghi nhận."""
    return service.stop_crawl_job(job_id)


@router.get("/jobs/{job_id}/status", tags=["Admin Crawler"])
def get_job_status(job_id: int):
    """Xem tiến độ thời gian thực của tác vụ cào (scanned, new, duplicates, updated, errors)."""
    st = service.get_crawler_status()
    active = st.get("active_job")
    if active and active.get("id") == job_id:
        return active
    for r in st.get("recent_jobs", []):
        if r.get("id") == job_id:
            return r
    return {"id": job_id, "status": "unknown"}


@router.get("/jobs/history", tags=["Admin Crawler"])
def get_crawler_jobs_history():
    """Lịch sử các lần cào gần nhất."""
    st = service.get_crawler_status()
    return st.get("recent_jobs", [])


@router.get("/logs", tags=["Admin Crawler"])
def get_crawler_logs(
    job_id: Optional[int] = Query(None, description="Lọc theo Job ID"),
    after_id: Optional[int] = Query(None, description="Lấy các log mới hơn ID này"),
    limit: int = Query(50, description="Giới hạn số dòng log tải về")
):
    """Nhật ký thực thi thời gian thực của các tác vụ (hỗ trợ phân trang và polling)."""
    return service.get_logs(job_id=job_id, after_id=after_id, limit=limit)


@router.post("/dedup/analyze", tags=["Admin Crawler"])
def analyze_deduplication():
    """Phân tích tỷ lệ khử trùng lặp dữ liệu thô jobs_raw."""
    return service.analyze_deduplication()


@router.post("/cleaning/start", tags=["Admin Crawler"])
def run_cleaning_pipeline(payload: Dict[str, Any] = Body(default={})):
    """Khởi tạo quy trình làm sạch & chuẩn hóa 3NF bất đồng bộ trên các bản ghi thô của batch."""
    batch_code = payload.get("batch_code", "BATCH_2026_Q4_INGEST")
    limit = int(payload.get("limit", 500))
    return service.start_cleaning_job(batch_code=batch_code, limit=limit)


@router.get("/cleaning/{cleaning_job_id}/status", tags=["Admin Crawler"])
def get_cleaning_job_status(cleaning_job_id: str):
    """Theo dõi tiến độ thời gian thực của tác vụ làm sạch dữ liệu 3NF."""
    return service.get_cleaning_job_status(cleaning_job_id)


@router.post("/quality-gate", tags=["Admin Crawler"])
def run_quality_gate(payload: Dict[str, Any] = Body(default={})):
    """Kiểm tra chất lượng dữ liệu & cổng phê duyệt (Quality Gate)."""
    batch_code = payload.get("batch_code", "BATCH_2026_Q4_INGEST")
    return service.run_quality_gate(batch_code=batch_code)


@router.post("/export-json", tags=["Admin Crawler"])
def export_clean_json(payload: Dict[str, Any] = Body(default={})):
    """Xuất file Clean JSON sạch chuẩn 3.000 JP & 1.500 CV."""
    batch_code = payload.get("batch_code", "BATCH_2026_Q4_INGEST")
    return service.export_clean_json(batch_code=batch_code)


@router.post("/cloud-sync", tags=["Admin Crawler"])
def sync_cloud(payload: Dict[str, Any] = Body(default={})):
    """Xác thực đồng bộ Cloud Lakehouse và tự động cập nhật Dashboard nếu thành công."""
    batch_code = payload.get("batch_code", "BATCH_2026_Q4_INGEST")
    target_period = payload.get("target_period", "2026_Q4")
    return service.sync_cloud(batch_code=batch_code, target_period=target_period)


@router.post("/publish-dashboard", tags=["Admin Crawler"])
def publish_to_dashboard(payload: Dict[str, Any] = Body(default={})):
    """Xuất bản batch dữ liệu sạch lên Dashboard cho kỳ báo cáo đích (mặc định: 2026_Q4)."""
    batch_code = payload.get("batch_code", "BATCH_2026_Q4_INGEST")
    target_period = payload.get("target_period", "2026_Q4")
    return service.publish_to_dashboard(batch_code=batch_code, target_period=target_period)
