from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class AuthRepository(ABC):
    """认证模块仓库接口"""
    
    @abstractmethod
    async def get_user_by_email(self, email: str):
        """根据邮箱获取用户"""
        pass
    
    @abstractmethod
    async def get_user_by_username(self, username: str):
        """根据用户名获取用户"""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: int):
        """根据ID获取用户"""
        pass
    
    @abstractmethod
    async def create_user(self, user_data: Dict[str, Any]):
        """创建用户"""
        pass 
