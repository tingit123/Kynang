"""
Router: Unified Dashboard Analytics API
Cung cấp nguồn dữ liệu phân tích thị trường lao động thống nhất theo Năm và Quý,
kết hợp dữ liệu lịch sử tái dựng 2025 và dữ liệu crawler quan sát thực tế 2026.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.crawler_data_source import CrawlerDataSource
import os

router = APIRouter()


@router.get("/locations")
def get_dashboard_locations_by_source(
    period: Optional[str] = Query(None, description="Kỳ báo cáo (VD: 2025_ALL, 2025_Q1..Q4, 2026_Q2)"),
    data_source: Optional[str] = Query(None, description="Tùy chọn tương thích ngược"),
    db: Session = Depends(get_db),
):
    """Danh sách địa bàn phân tích thống nhất từ MySQL theo kỳ báo cáo."""
    try:
        return CrawlerDataSource().dashboard_locations(period=period)
    except Exception as e:
        raise HTTPException(status_code=503, detail="Nguồn crawler không khả dụng; không thay bằng dữ liệu mô phỏng") from e


@router.get("/reporting-datasets")
@router.get("/datasets")
@router.get("/periods")
def get_reporting_datasets():
    """Danh sách các kỳ báo cáo phân tích theo Năm và Quý kèm trạng thái chất lượng dữ liệu."""
    try:
        return CrawlerDataSource().reporting_datasets()
    except Exception as e:
        return []


@router.get("")
@router.get("/")
@router.get("/analytics")
def get_dashboard_analytics(
    location_id: str = Query("all", description="Mã địa bàn ('all' hoặc mã tỉnh/thành: CT, HN, HCM, ...)"),
    period: Optional[str] = Query(None, description="Kỳ báo cáo dạng '2025_ALL', '2025_Q1'..'2025_Q4', '2026_Q2', '2026_Q3', '2026_Q4'"),
    period_type: Optional[str] = Query(None, description="'quarter' hoặc 'year'"),
    year: Optional[int] = Query(None, ge=2020, le=2035, description="Năm báo cáo (2025, 2026)"),
    quarter: Optional[int] = Query(None, ge=1, le=4, description="Quý báo cáo (1..4)"),
    industry: Optional[str] = Query(None, description="Lọc ngành nghề: IT, tourism, logistics, economics/accounting"),
    skill_type: Optional[str] = Query("ALL", description="Lọc loại kỹ năng: ALL, HARD, TOOL, KNOWLEDGE, CERTIFICATION, SOFT, LANGUAGE"),
    data_source: Optional[str] = Query(None, description="Tùy chọn tương thích ngược"),
    db: Session = Depends(get_db),
):
    """
    Trả về dữ liệu phân tích thống nhất theo Năm và Quý từ MySQL:
    - 2025 (ALL, Q1..Q4): Dữ liệu lịch sử tái dựng từ bộ thống kê nội bộ, phân bổ quý không đồng đều bảo toàn tổng năm.
    - 2026 Q2: Dữ liệu quan sát thực tế từ TopCV Crawler 3NF & LLM Extraction (1.000 JD sạch & 500 CV).
    - 2026 Q3: Dữ liệu thô đang làm sạch (2.000 JD thô mới cào, chưa làm sạch, trạng thái RAW).
    - 2026 Q4: Kỳ kế hoạch chưa có dữ liệu (trạng thái PENDING).
    """
    # Normalize period from year / quarter query parameters if period not given explicitly
    effective_period = period
    if not effective_period:
        if year == 2025:
            if quarter:
                effective_period = f"2025_Q{quarter}"
            else:
                effective_period = "2025_ALL"
        elif year == 2026:
            if quarter == 1:
                effective_period = "2026_Q1"
            elif quarter == 3:
                effective_period = "2026_Q3"
            elif quarter == 4:
                effective_period = "2026_Q4"
            else:
                effective_period = "2026_Q2"
        else:
            effective_period = "2026_Q2"

    crawler = CrawlerDataSource()
    try:
        return crawler.analytics(
            location=location_id, industry=industry,
            skill_type=skill_type, period=effective_period
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
