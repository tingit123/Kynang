from sqlalchemy import Column, Integer, String, ForeignKey
from src.database import Base


class CourseRecommendation(Base):
    __tablename__ = "course_recommendations"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    skill_id    = Column(Integer, ForeignKey("skill_catalog.id"), nullable=False)
    course_name = Column(String(300), nullable=False)
    platform    = Column(String(100))
    url         = Column(String(500))
    priority    = Column(Integer, default=1)
