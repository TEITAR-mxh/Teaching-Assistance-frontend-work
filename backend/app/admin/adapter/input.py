from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.admin.application.schema import (
    AdminLoginRequest, AdminLoginResponse, UserCreateRequest, 
    UserUpdateRequest, UserResponse, DashboardStats
)
from app.admin.application.service import AdminService
from app.admin.adapter.repository import SQLAlchemyAdminRepository
from app.core.exceptions import NotFoundException, UnauthorizedException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

def get_admin_repo(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyAdminRepository(db)

def get_admin_service(repo = Depends(get_admin_repo)):
    return AdminService(repo)

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(login_data: AdminLoginRequest, service = Depends(get_admin_service)):
    try:
        return await service.login(login_data)
    except UnauthorizedException as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"管理员登录失败: {e}")
        raise HTTPException(status_code=500, detail="登录失败")

@router.get("/statistics/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(service = Depends(get_admin_service)):
    try:
        return await service.get_dashboard_stats()
    except Exception as e:
        logger.error(f"获取仪表板统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取统计数据失败")

@router.get("/list", response_model=list[UserResponse])
async def get_user_list(service = Depends(get_admin_service)):
    try:
        users = await service.get_all_users()
        return users
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取用户列表失败")

@router.post("/user/add", response_model=UserResponse)
async def add_user(user_data: UserCreateRequest, service = Depends(get_admin_service)):
    try:
        return await service.create_user(user_data)
    except Exception as e:
        logger.error(f"添加用户失败: {e}")
        raise HTTPException(status_code=500, detail="添加用户失败")

@router.delete("/delete/{user_id}")
async def delete_user(user_id: int, service = Depends(get_admin_service)):
    try:
        return await service.delete_user(user_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除用户失败: {e}")
        raise HTTPException(status_code=500, detail="删除用户失败")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_info(user_id: int, service = Depends(get_admin_service)):
    try:
        return await service.get_user_by_id(user_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取用户信息失败")

@router.put("/user/{user_id}/updateName")
async def update_username(user_id: int, user_data: UserUpdateRequest, service = Depends(get_admin_service)):
    try:
        return await service.update_user(user_id, user_data)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"更新用户名失败: {e}")
        raise HTTPException(status_code=500, detail="更新用户名失败")

@router.put("/user/{user_id}/updateEmail")
async def update_email(user_id: int, user_data: UserUpdateRequest, service = Depends(get_admin_service)):
    try:
        return await service.update_user(user_id, user_data)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"更新用户邮箱失败: {e}")
        raise HTTPException(status_code=500, detail="更新用户邮箱失败") 
