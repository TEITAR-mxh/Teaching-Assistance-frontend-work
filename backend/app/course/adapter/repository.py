from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.course.domain.repository import CourseRepository
from app.models.course import Course
from typing import List, Optional, Dict, Any

class SQLAlchemyCourseRepository(CourseRepository):
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_courses_by_teacher(self, teacher_id: int) -> List[Course]:
        """获取教师的所有课程"""
        result = await self.db.execute(
            select(Course).where(Course.teacher_id == teacher_id)
        )
        return result.scalars().all()
    
    async def get_course_by_id(self, course_id: int) -> Optional[Course]:
        """根据ID获取课程"""
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none()
    
    async def create_course(self, course_data: Dict[str, Any]) -> Course:
        """创建课程"""
        course = Course(**course_data)
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        return course
    
    async def update_course(self, course_id: int, course_data: Dict[str, Any]) -> Course:
        """更新课程"""
        await self.db.execute(
            update(Course)
            .where(Course.id == course_id)
            .values(**course_data)
        )
        await self.db.commit()
        
        # 返回更新后的课程
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one()
    
    async def delete_course(self, course_id: int):
        """删除课程"""
        await self.db.execute(
            delete(Course).where(Course.id == course_id)
        )
        await self.db.commit()
    
    async def get_all_courses(self) -> List[Course]:
        """获取所有课程"""
        result = await self.db.execute(select(Course))
        return result.scalars().all() 