from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.course.domain.repository import CourseRepository
from app.models.course import Course
from app.models.course_objective import CourseObjective
from app.models.course_syllabus import CourseSyllabus
from app.models.course_material import CourseMaterial
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
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[Repository] 更新课程 ID: {course_id}, 数据: {course_data}")
        
        # 先查询更新前的状态
        result_before = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        course_before = result_before.scalar_one_or_none()
        if course_before:
            logger.info(f"[Repository] 更新前: ID={course_before.id}, title='{course_before.title}'")
        
        # 执行更新
        update_result = await self.db.execute(
            update(Course)
            .where(Course.id == course_id)
            .values(**course_data)
        )
        logger.info(f"[Repository] 更新影响行数: {update_result.rowcount}")
        
        await self.db.commit()
        logger.info(f"[Repository] 数据库事务已提交")
        
        # 返回更新后的课程
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        updated_course = result.scalar_one()
        logger.info(f"[Repository] 更新后: ID={updated_course.id}, title='{updated_course.title}'")
        
        return updated_course
    
    async def delete_course(self, course_id: int):
        """删除课程"""
        # 1) 先删除依赖于课程的子表记录，避免外键约束错误
        await self.db.execute(
            delete(CourseObjective).where(CourseObjective.course_id == course_id)
        )
        await self.db.execute(
            delete(CourseSyllabus).where(CourseSyllabus.course_id == course_id)
        )
        await self.db.execute(
            delete(CourseMaterial).where(CourseMaterial.course_id == course_id)
        )

        # 2) 再删除课程本身
        await self.db.execute(delete(Course).where(Course.id == course_id))
        await self.db.commit()
    
    async def get_all_courses(self) -> List[Course]:
        """获取所有课程"""
        result = await self.db.execute(select(Course))
        return result.scalars().all() 
