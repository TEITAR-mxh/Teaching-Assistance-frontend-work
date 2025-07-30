from app.teacher.domain.repository import TeacherRepository
from app.models.course_objective import CourseObjective
from app.models.course_syllabus import CourseSyllabus
from app.models.course_material import CourseMaterial
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class SQLAlchemyTeacherRepository(TeacherRepository):
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_course_objective(self, course_id: int):
        result = await self.db.execute(select(CourseObjective).where(CourseObjective.course_id == course_id))
        return result.scalar_one_or_none()
    
    async def save_course_objective(self, course_id: int, course_content: str, teaching_target: str):
        existing = await self.get_course_objective(course_id)
        if existing:
            existing.course_content = course_content
            existing.teaching_target = teaching_target
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            objective = CourseObjective(course_id=course_id, course_content=course_content, teaching_target=teaching_target)
            self.db.add(objective)
            await self.db.commit()
            await self.db.refresh(objective)
            return objective
    
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
