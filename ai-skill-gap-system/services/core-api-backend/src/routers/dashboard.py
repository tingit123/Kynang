"""
Router: Unified Dashboard Analytics API
Cung cấp nguồn dữ liệu duy nhất, đồng bộ theo Địa bàn (location_id) và Kỳ báo cáo (period / year / quarter)
cho toàn bộ biểu đồ và thẻ thống kê trên Dashboard Skill Lens Lab.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.dashboard_analytics import compute_dashboard_analytics

router = APIRouter()


@router.get("")
@router.get("/")
@router.get("/analytics")
def get_dashboard_analytics(
    location_id: str = Query("all", description="Mã địa bàn ('all' hoặc mã tỉnh/thành: CT, HN, HCM, DN_CITY, ...)"),
    period: Optional[str] = Query(None, description="Kỳ báo cáo dạng '2026_Q3', '2026_ALL', '2025_Q4'..."),
    period_type: Optional[str] = Query(None, description="'quarter' hoặc 'year'"),
    year: Optional[int] = Query(None, ge=2020, le=2035, description="Năm báo cáo"),
    quarter: Optional[int] = Query(None, ge=1, le=4, description="Quý báo cáo (1..4)"),
    industry: Optional[str] = Query(None, description="Lọc ngành nghề (tùy chọn)"),
    db: Session = Depends(get_db),
):
    """
    Trả về dữ liệu tổng hợp thực tế từ MySQL cho toàn bộ Dashboard:
    - KPI tổng quan (tin tuyển dụng, hồ sơ khảo sát, gap trung bình, kỹ năng hoạt động)
    - Top 5 kỹ năng thiếu hụt nhiều nhất (Demand, Supply, Gap)
    - Phân bổ ngành nghề (Pie/Doughnut)
    - Chuỗi thời gian 4 quý theo ngành
    - So sánh cơ cấu tỷ trọng giữa kỳ hiện tại và kỳ liền trước
    - Kỹ năng mềm & chuỗi xu hướng kỹ năng mềm
    - Chi tiết Top 10 kỹ năng cho từng ngành nghề
    """
    return compute_dashboard_analytics(
        db=db,
        location_id=location_id,
        period=period,
        period_type=period_type,
        year=year,
        quarter=quarter,
        industry=industry,
    )
