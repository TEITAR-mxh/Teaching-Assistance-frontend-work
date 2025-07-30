from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.teacher.application.schema import (
    CourseObjectiveRequest, CourseObjectiveResponse,
    CourseSyllabusRequest, CourseSyllabusResponse,
    CourseMaterialRequest, CourseMaterialResponse,
    GenerateRequest
)
from app.teacher.application.service import TeacherService
from app.teacher.adapter.repository import SQLAlchemyTeacherRepository
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teacher", tags=["teacher"])

def get_teacher_repo(db: AsyncSession = Depends(get_db)):
    return SQLAlchemyTeacherRepository(db)

def get_teacher_service(repo = Depends(get_teacher_repo)):
    return TeacherService(repo)

# 课程教学目标相关接口
@router.get("/objective/{course_id}", response_model=CourseObjectiveResponse)
async def get_course_objective(course_id: int, service = Depends(get_teacher_service)):
    try:
        return await service.get_course_objective(course_id)
    except Exception as e:
        logger.error(f"获取课程教学目标失败: {e}")
        raise HTTPException(status_code=500, detail="获取课程教学目标失败")

@router.post("/objective/{course_id}/generate")
async def generate_course_objective(course_id: int, request: GenerateRequest, service = Depends(get_teacher_service)):
    try:
        return await service.generate_course_objective(course_id, request)
    except Exception as e:
        logger.error(f"生成课程教学目标失败: {e}")
        raise HTTPException(status_code=500, detail="生成课程教学目标失败")

@router.post("/objective/{course_id}/save")
async def save_course_objective(course_id: int, request: CourseObjectiveRequest, service = Depends(get_teacher_service)):
    try:
        return await service.save_course_objective(course_id, request)
    except Exception as e:
        logger.error(f"保存课程教学目标失败: {e}")
        raise HTTPException(status_code=500, detail="保存课程教学目标失败")

# 课程大纲相关接口
@router.get("/syllabus/{course_id}")
async def get_course_syllabus(course_id: int, service = Depends(get_teacher_service)):
    try:
        return await service.get_course_syllabus(course_id)
    except Exception as e:
        logger.error(f"获取课程大纲失败: {e}")
        raise HTTPException(status_code=500, detail="获取课程大纲失败")

@router.post("/syllabus/{course_id}/generate")
async def generate_course_syllabus(course_id: int, request: GenerateRequest, service = Depends(get_teacher_service)):
    try:
        return await service.generate_course_syllabus(course_id, request)
    except Exception as e:
        logger.error(f"生成课程大纲失败: {e}")
        raise HTTPException(status_code=500, detail="生成课程大纲失败")

@router.post("/syllabus/{course_id}/save")
async def save_course_syllabus(course_id: int, request: CourseSyllabusRequest, service = Depends(get_teacher_service)):
    try:
        return await service.save_course_syllabus(course_id, request)
    except Exception as e:
        logger.error(f"保存课程大纲失败: {e}")
        raise HTTPException(status_code=500, detail="保存课程大纲失败")

# 课程讲义相关接口
@router.get("/material/{course_id}")
async def get_course_material(course_id: int, service = Depends(get_teacher_service)):
    try:
        return await service.get_course_material(course_id)
    except Exception as e:
        logger.error(f"获取课程讲义失败: {e}")
        raise HTTPException(status_code=500, detail="获取课程讲义失败")

@router.post("/material/{course_id}/generate")
async def generate_course_material(course_id: int, request: GenerateRequest, service = Depends(get_teacher_service)):
    try:
        return await service.generate_course_material(course_id, request)
    except Exception as e:
        logger.error(f"生成课程讲义失败: {e}")
        raise HTTPException(status_code=500, detail="生成课程讲义失败")

@router.post("/material/{course_id}/save")
async def save_course_material(course_id: int, request: CourseMaterialRequest, service = Depends(get_teacher_service)):
    try:
        return await service.save_course_material(course_id, request)
    except Exception as e:
        logger.error(f"保存课程讲义失败: {e}")
        raise HTTPException(status_code=500, detail="保存课程讲义失败") 
