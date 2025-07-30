# 教师域实体，复用用户实体
from app.models.user import User

class Teacher(User):
    """教师实体，继承自用户实体"""
    pass 
