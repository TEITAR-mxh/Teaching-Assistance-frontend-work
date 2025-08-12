from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.sql import func
from app.models import Base

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    # 教师删除通常不应级联删除课程，因此使用 RESTRICT 以阻止误删
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    # 课程状态受限为固定枚举值
    status = Column(String(50), default="active")  # active, inactive, draft
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 

    # 约束与索引
    __table_args__ = (
        # 同一位教师下课程标题唯一，避免重复创建
        UniqueConstraint('teacher_id', 'title', name='uq_courses_teacher_title'),
        # 状态枚举检查
        CheckConstraint("status in ('active','inactive','draft')", name='ck_courses_status_valid'),
        # 常用查询的复合索引（按教师与创建时间）
        Index('ix_courses_teacher_created', 'teacher_id', 'created_at'),
    )
