from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.application.schema import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from app.auth.application.service import AuthService
from app.auth.adapter.repository import SQLAlchemyAuthRepository
from app.core.exceptions import UnauthorizedException, ValidationException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

def get_auth_repo(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyAuthRepository(db)

def get_auth_service(repo = Depends(get_auth_repo)):
    return AuthService(repo)

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, service = Depends(get_auth_service)):
    """用户登录"""
    try:
        return await service.login(login_data.username, login_data.email, login_data.password)
    except UnauthorizedException as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise HTTPException(status_code=500, detail="登录失败")

@router.post("/register", response_model=RegisterResponse)
async def register(register_data: RegisterRequest, service = Depends(get_auth_service)):
    """用户注册"""
    try:
        return await service.register(register_data)
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"注册失败: {e}")
        raise HTTPException(status_code=500, detail="注册失败")

@router.get("/check-username/{username}")
async def check_username_available(username: str, service = Depends(get_auth_service)):
    """检查用户名是否可用"""
    try:
        available = await service.check_username_available(username)
        return {"available": available}
    except Exception as e:
        logger.error(f"检查用户名失败: {e}")
        raise HTTPException(status_code=500, detail="检查用户名失败")

@router.get("/check-email/{email}")
async def check_email_available(email: str, service = Depends(get_auth_service)):
    """检查邮箱是否可用"""
    try:
        available = await service.check_email_available(email)
        return {"available": available}
    except Exception as e:
        logger.error(f"检查邮箱失败: {e}")
        raise HTTPException(status_code=500, detail="检查邮箱失败")

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """用户登出"""
    try:
        # 这里可以实现token黑名单等逻辑
        return {"message": "登出成功"}
    except Exception as e:
        logger.error(f"登出失败: {e}")
        raise HTTPException(status_code=500, detail="登出失败")

@router.get("/me")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service = Depends(get_auth_service)
):
    """获取当前用户信息"""
    try:
        token = credentials.credentials
        user = await service.get_current_user(token)
        return user
    except UnauthorizedException as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取用户信息失败") 
