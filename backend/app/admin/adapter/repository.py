from app.admin.domain.repository import AdminRepository
from app.models.user import User
from app.models.course import Course
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

class SQLAlchemyAdminRepository(AdminRepository):
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_users(self):
        result = await self.db.execute(select(User))
        return result.scalars().all()
    
    async def get_user_by_id(self, user_id: int):
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def create_user(self, user: User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update_user(self, user: User):
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete_user(self, user_id: int):
        user = await self.get_user_by_id(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
    
    async def get_dashboard_stats(self):
        # 用户统计
        total_users = await self.db.scalar(select(func.count(User.id)))
        teacher_count = await self.db.scalar(select(func.count(User.id)).where(User.role == "teacher"))
        admin_count = await self.db.scalar(select(func.count(User.id)).where(User.role == "admin"))
        
        # 课程统计
        total_courses = await self.db.scalar(select(func.count(Course.id)))
        active_courses = await self.db.scalar(select(func.count(Course.id)).where(Course.status == "active"))
        
        return {
            "userStats": {
                "totalUsers": total_users or 0,
                "teacherCount": teacher_count or 0,
                "adminCount": admin_count or 0
            },
            "courseStats": {
                "totalCourses": total_courses or 0,
                "activeCount": active_courses or 0,
                "pendingCount": 0,  # 简化处理
                "approvedCount": active_courses or 0,
                "rejectedCount": 0
            }
        } 
