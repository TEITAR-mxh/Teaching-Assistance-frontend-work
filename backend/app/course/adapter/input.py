from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.course.application.schema import (
    CourseCreate, CourseUpdate, CourseResponse, CourseListResponse
)
from app.course.application.service import CourseService
from app.course.adapter.repository import SQLAlchemyCourseRepository
from app.core.exceptions import NotFoundException, ValidationException
from app.core.helpers.token import verify_token
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/courses", tags=["courses"])
security = HTTPBearer()

def get_course_repo(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyCourseRepository(db)

def get_course_service(repo = Depends(get_course_repo)):
    return CourseService(repo)

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """获取当前用户ID"""
    try:
        payload = verify_token(credentials.credentials)
        user_id = int(payload.get("sub"))
        return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail="无效的认证令牌")

@router.get("/teacher/{teacher_id}", response_model=list[CourseResponse])
async def get_teacher_courses(
    teacher_id: int, 
    current_user_id: int = Depends(get_current_user_id),
    service = Depends(get_course_service)
):
    """获取教师的所有课程"""
    try:
        # 只能获取自己的课程，管理员可以获取任何人的课程
        # 这里简化处理，暂时允许获取任何教师的课程
        # TODO: 后续可以加入角色验证
        return await service.get_teacher_courses(teacher_id)
    except Exception as e:
        logger.error(f"获取教师课程失败: {e}")
        raise HTTPException(status_code=500, detail="获取课程列表失败")

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_detail(course_id: int, service = Depends(get_course_service)):
    """获取课程详情"""
    try:
        course = await service.get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        return course
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取课程详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取课程详情失败")

@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate, 
    current_user_id: int = Depends(get_current_user_id),
    service = Depends(get_course_service)
):
    """创建新课程"""
    try:
        logger.info(f"[API] 创建课程请求: user_id={current_user_id}, data={course_data.dict()}")
        # 确保课程的teacher_id是当前用户
        course_data.teacher_id = current_user_id
        logger.info(f"[API] 设置teacher_id后: {course_data.dict()}")
        result = await service.create_course(course_data)
        logger.info(f"[API] 创建课程成功: {result.dict()}")
        return result
    except ValidationException as e:
        logger.error(f"[API] 创建课程验证错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] 创建课程失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="创建课程失败")

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int, 
    course_data: CourseUpdate,
    current_user_id: int = Depends(get_current_user_id), 
    service = Depends(get_course_service)
):
    """更新课程信息"""
    try:
        return await service.update_course(course_id, course_data, current_user_id)
    except HTTPException:
        raise
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新课程失败: {e}")
        raise HTTPException(status_code=500, detail="更新课程失败")

@router.delete("/{course_id}", status_code=204)
async def delete_course(
    course_id: int, 
    current_user_id: int = Depends(get_current_user_id),
    service = Depends(get_course_service)
):
    """删除课程"""
    try:
        await service.delete_course(course_id, current_user_id)
        # 返回204 No Content状态码，不返回响应体
        return None
    except HTTPException:
        raise
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除课程失败: {e}")
        raise HTTPException(status_code=500, detail="删除课程失败")

@router.get("/", response_model=list[CourseResponse])
async def get_all_courses(service = Depends(get_course_service)):
    """获取所有课程（管理员用）"""
    try:
        return await service.get_all_courses()
    except Exception as e:
        logger.error(f"获取所有课程失败: {e}")
        raise HTTPException(status_code=500, detail="获取课程列表失败") 
