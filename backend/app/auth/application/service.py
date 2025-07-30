from app.auth.domain.repository import AuthRepository
from app.auth.application.schema import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, UserInfo
from app.core.exceptions import UnauthorizedException, ValidationException
from app.core.helpers.token import create_access_token, verify_token
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def _get_password_hash(self, password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)
    
    async def login(self, username: str, email: str, password: str) -> LoginResponse:
        """用户登录"""
        # 查找用户（通过邮箱）
        user = await self.repo.get_user_by_email(email)
        if not user:
            raise UnauthorizedException("用户名、邮箱或密码错误")
        
        # 验证用户名
        if user.username != username:
            raise UnauthorizedException("用户名、邮箱或密码错误")
        
        # 验证密码
        if not self._verify_password(password, user.password):
            raise UnauthorizedException("用户名、邮箱或密码错误")
        
        # 生成JWT token
        token = create_access_token(data={"sub": str(user.id), "role": user.role})
        
        return LoginResponse(
            token=token,
            userId=user.id,
            username=user.username,
            role=user.role
        )
    
    async def register(self, register_data: RegisterRequest) -> RegisterResponse:
        """用户注册"""
        # 检查用户名是否已存在
        if await self.repo.get_user_by_username(register_data.username):
            raise ValidationException("用户名已存在")
        
        # 检查邮箱是否已存在
        if await self.repo.get_user_by_email(register_data.email):
            raise ValidationException("邮箱已存在")
        
        # 创建用户
        hashed_password = self._get_password_hash(register_data.password)
        user_data = {
            "username": register_data.username,
            "email": register_data.email,
            "password": hashed_password,
            "role": register_data.role
        }
        
        await self.repo.create_user(user_data)
        
        return RegisterResponse(
            success=True,
            message="注册成功"
        )
    
    async def check_username_available(self, username: str) -> bool:
        """检查用户名是否可用"""
        user = await self.repo.get_user_by_username(username)
        return user is None
    
    async def check_email_available(self, email: str) -> bool:
        """检查邮箱是否可用"""
        user = await self.repo.get_user_by_email(email)
        return user is None
    
    async def get_current_user(self, token: str) -> UserInfo:
        """获取当前用户信息"""
        try:
            payload = verify_token(token)
            user_id = int(payload.get("sub"))
            user = await self.repo.get_user_by_id(user_id)
            
            if not user:
                raise UnauthorizedException("用户不存在")
            
            return UserInfo(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role
            )
        except Exception as e:
            raise UnauthorizedException("无效的token") 
