from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.course.application.schema import (
    CourseCreate, CourseUpdate, CourseResponse, CourseListResponse
)
from app.course.application.service import CourseService
from app.course.adapter.repository import SQLAlchemyCourseRepository
from app.core.exceptions import NotFoundException, ValidationException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/courses", tags=["courses"])

def get_course_repo(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyCourseRepository(db)

def get_course_service(repo = Depends(get_course_repo)):
    return CourseService(repo)

@router.get("/teacher/{teacher_id}", response_model=list[CourseResponse])
async def get_teacher_courses(teacher_id: int, service = Depends(get_course_service)):
    """获取教师的所有课程"""
    try:
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
async def create_course(course_data: CourseCreate, service = Depends(get_course_service)):
    """创建新课程"""
    try:
        return await service.create_course(course_data)
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建课程失败: {e}")
        raise HTTPException(status_code=500, detail="创建课程失败")

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int, 
    course_data: CourseUpdate, 
    service = Depends(get_course_service)
):
    """更新课程信息"""
    try:
        return await service.update_course(course_id, course_data)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新课程失败: {e}")
        raise HTTPException(status_code=500, detail="更新课程失败")

@router.delete("/{course_id}")
async def delete_course(course_id: int, service = Depends(get_course_service)):
    """删除课程"""
    try:
        await service.delete_course(course_id)
        return {"message": "课程删除成功"}
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