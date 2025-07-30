from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.user.application.schema import UserRead, UserCreate
from app.user.application.service import get_users, create_user
from app.user.adapter.repository import SQLAlchemyUserRepository
from app.user.application.exception import UserNotFoundException
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

def get_user_repo(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyUserRepository(db)

@router.get("/", response_model=list[UserRead])
async def list_users(repo = Depends(get_user_repo)):
    try:
        logger.info("Attempting to get users")
        return await get_users(repo)
    except UserNotFoundException as e:
        logger.warning(f"UserNotFoundException: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in list_users: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/", response_model=UserRead)
async def add_user(user: UserCreate, repo = Depends(get_user_repo)):
    try:
        logger.info(f"Attempting to create user: {user.username}")
        return await create_user(repo, user)
    except Exception as e:
        logger.error(f"Unexpected error in add_user: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 
