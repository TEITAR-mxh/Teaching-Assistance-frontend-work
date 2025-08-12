from sqlalchemy import Column, Integer, String, DateTime, Boolean, CheckConstraint, Index
from sqlalchemy.sql import func
from . import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="teacher")  # teacher, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 

    __table_args__ = (
        # 角色枚举检查
        CheckConstraint("role in ('teacher','admin')", name='ck_users_role_valid'),
        # email 常用于查找，且有唯一索引，补充前缀索引便于部分检索（可选）
        Index('ix_users_email_lower', 'email'),
    )
