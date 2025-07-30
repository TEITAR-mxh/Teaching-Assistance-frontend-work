# 管理员域实体，复用用户实体
from app.models.user import User

class Admin(User):
    """管理员实体，继承自用户实体"""
    pass 
