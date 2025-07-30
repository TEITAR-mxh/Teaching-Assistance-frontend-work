from app.course.domain.repository import CourseRepository
from app.course.application.schema import CourseCreate, CourseUpdate, CourseResponse
from app.core.exceptions import NotFoundException, ValidationException
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CourseService:
    def __init__(self, repo: CourseRepository):
        self.repo = repo
    
    async def get_teacher_courses(self, teacher_id: int) -> list[CourseResponse]:
        """获取教师的所有课程"""
        courses = await self.repo.get_courses_by_teacher(teacher_id)
        return [CourseResponse.from_orm(course) for course in courses]
    
    async def get_course_by_id(self, course_id: int) -> Optional[CourseResponse]:
        """根据ID获取课程"""
        course = await self.repo.get_course_by_id(course_id)
        if not course:
            return None
        return CourseResponse.from_orm(course)
    
    async def create_course(self, course_data: CourseCreate) -> CourseResponse:
        """创建新课程"""
        if not course_data.title or course_data.title.strip() == "":
            raise ValidationException("课程名称不能为空")
        
        course = await self.repo.create_course(course_data.dict())
        return CourseResponse.from_orm(course)
    
    async def update_course(self, course_id: int, course_data: CourseUpdate) -> CourseResponse:
        """更新课程信息"""
        course = await self.repo.get_course_by_id(course_id)
        if not course:
            raise NotFoundException("课程不存在")
        
        update_data = course_data.dict(exclude_unset=True)
        if "title" in update_data and (not update_data["title"] or update_data["title"].strip() == ""):
            raise ValidationException("课程名称不能为空")
        
        updated_course = await self.repo.update_course(course_id, update_data)
        return CourseResponse.from_orm(updated_course)
    
    async def delete_course(self, course_id: int):
        """删除课程"""
        course = await self.repo.get_course_by_id(course_id)
        if not course:
            raise NotFoundException("课程不存在")
        
        await self.repo.delete_course(course_id)
    
    async def get_all_courses(self) -> list[CourseResponse]:
        """获取所有课程（管理员用）"""
        courses = await self.repo.get_all_courses()
        return [CourseResponse.from_orm(course) for course in courses] 