from app.teacher.domain.repository import TeacherRepository
from app.models.course_objective import CourseObjective
from app.models.course_syllabus import CourseSyllabus
from app.models.course_material import CourseMaterial
from app.models.course import Course
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging

logger = logging.getLogger(__name__)

class SQLAlchemyTeacherRepository(TeacherRepository):
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_course_objective(self, course_id: int):
        try:
            result = await self.db.execute(select(CourseObjective).where(CourseObjective.course_id == course_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"获取课程目标失败: {e}")
            raise
    
    async def save_course_objective(self, course_id: int, course_content: str, teaching_target: str):
        try:
            logger.info(f"开始保存课程目标: course_id={course_id}")
            
            # 首先检查课程是否存在
            course_result = await self.db.execute(select(Course).where(Course.id == course_id))
            course = course_result.scalar_one_or_none()
            if not course:
                logger.error(f"课程ID {course_id} 不存在")
                raise ValueError(f"课程ID {course_id} 不存在")
            
            logger.info(f"课程存在，开始处理课程目标")
            
            existing = await self.get_course_objective(course_id)
            if existing:
                logger.info(f"更新现有课程目标: id={existing.id}")
                existing.course_content = course_content
                existing.teaching_target = teaching_target
                await self.db.commit()
                await self.db.refresh(existing)
                return existing
            else:
                logger.info(f"创建新课程目标")
                objective = CourseObjective(
                    course_id=course_id, 
                    content=course_content,
                    course_content=course_content, 
                    teaching_target=teaching_target
                )
                self.db.add(objective)
                await self.db.commit()
                await self.db.refresh(objective)
                logger.info(f"课程目标创建成功: id={objective.id}")
                return objective
        except Exception as e:
            logger.error(f"保存课程目标失败: {e}")
            await self.db.rollback()
            raise
    
    async def get_course_syllabus(self, course_id: int):
        result = await self.db.execute(
            select(CourseSyllabus).where(CourseSyllabus.course_id == course_id)
        )
        return result.scalar_one_or_none()
    
    async def save_course_syllabus(self, course_id: int, content: str):
        print(f"[DEBUG] save_course_syllabus: course_id={course_id}, content={content}")
        existing = await self.get_course_syllabus(course_id)
        if existing:
            existing.content = content
            await self.db.commit()
            await self.db.refresh(existing)
            print(f"[DEBUG] updated syllabus: id={existing.id}, content={existing.content}")
            return existing
        else:
            syllabus = CourseSyllabus(course_id=course_id, content=content)
            self.db.add(syllabus)
            await self.db.commit()
            await self.db.refresh(syllabus)
            print(f"[DEBUG] created syllabus: id={syllabus.id}, content={syllabus.content}")
            return syllabus
    
    async def get_course_material(self, course_id: int):
        result = await self.db.execute(
            select(CourseMaterial).where(CourseMaterial.course_id == course_id)
        )
        return result.scalar_one_or_none()
    
    async def save_course_material(self, course_id: int, content: str):
        # 先查找是否已存在
        existing = await self.get_course_material(course_id)
        if existing:
            existing.content = content
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # 创建新的
            material = CourseMaterial(course_id=course_id, content=content)
            self.db.add(material)
            await self.db.commit()
            await self.db.refresh(material)
            return material 
