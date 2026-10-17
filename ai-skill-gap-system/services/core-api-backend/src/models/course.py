from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from src.database import Base


class CourseRecommendation(Base):
    __tablename__ = "course_recommendations"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    skill_id    = Column(Integer, ForeignKey("skill_catalog.id"), nullable=False)
    course_name = Column(String(300), nullable=False)
    platform    = Column(String(100))
    url         = Column(String(500))
    priority    = Column(Integer, default=1)
    status      = Column(String(50), default="pending", nullable=False)
    click_count = Column(Integer, default=0, nullable=False)
    is_deleted  = Column(Boolean, default=False, nullable=False)
