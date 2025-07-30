from app.admin.domain.repository import AdminRepository
from app.admin.application.schema import AdminLoginRequest, UserCreateRequest, UserUpdateRequest
from app.models.user import User
from app.core.exceptions import NotFoundException, UnauthorizedException
import hashlib
import jwt
import os
from datetime import datetime, timedelta

class AdminService:
    def __init__(self, repo: AdminRepository):
        self.repo = repo
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    
    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        return self._hash_password(password) == hashed
    
    def _generate_token(self, user_id: int, username: str, role: str) -> str:
        """生成JWT token"""
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    async def login(self, login_data: AdminLoginRequest):
        """管理员登录"""
        # 这里简化处理，实际应该从数据库验证
        if login_data.username == "admin" and login_data.password == "admin123":
            token = self._generate_token(1, "admin", "admin")
            return {
                "token": token,
                "user": {
                    "id": 1,
                    "username": "admin",
                    "role": "admin"
                }
            }
        raise UnauthorizedException("用户名或密码错误")
    
    async def get_all_users(self):
        """获取所有用户"""
        users = await self.repo.get_all_users()
        return users
    
    async def get_user_by_id(self, user_id: int):
        """根据ID获取用户"""
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise NotFoundException(f"用户 {user_id} 不存在")
        return user
    
    async def create_user(self, user_data: UserCreateRequest):
        """创建用户"""
        user = User(
            username=user_data.username,
            email=user_data.email,
            password=self._hash_password(user_data.password),
            role=user_data.role
        )
        return await self.repo.create_user(user)
    
    async def update_user(self, user_id: int, user_data: UserUpdateRequest):
        """更新用户"""
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise NotFoundException(f"用户 {user_id} 不存在")
        
        if user_data.username:
            user.username = user_data.username
        if user_data.email:
            user.email = user_data.email
        if user_data.role:
            user.role = user_data.role
        
        return await self.repo.update_user(user)
    
    async def delete_user(self, user_id: int):
        """删除用户"""
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise NotFoundException(f"用户 {user_id} 不存在")
        
        await self.repo.delete_user(user_id)
        return {"message": "用户删除成功"}
    
    async def get_dashboard_stats(self):
        """获取仪表板统计数据"""
        return await self.repo.get_dashboard_stats() 
