from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.models import Base

class CourseObjective(Base):
    __tablename__ = "course_objectives"
    
    id = Column(Integer, primary_key=True, index=True)
    # 课程被删除时，自动删除其目标
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    course_content = Column(Text)
    teaching_target = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 

    __table_args__ = (
        # 若业务为“一课一目标”，打开唯一约束；如允许多条，请删除该行
        # UniqueConstraint('course_id', name='uq_objective_course_single'),
    )
