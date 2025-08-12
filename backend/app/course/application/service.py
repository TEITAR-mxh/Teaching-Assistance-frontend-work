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
        
        # 处理重复名称：如果标题已存在，自动添加序号
        original_title = course_data.title.strip()
        title = original_title
        counter = 1
        
        while True:
            try:
                # 创建新的字典数据，包含修改后的title
                course_dict = course_data.dict()
                course_dict['title'] = title
                logger.info(f"[Service] 尝试创建课程: {course_dict}")
                
                course = await self.repo.create_course(course_dict)
                logger.info(f"[Service] 课程创建成功: ID={course.id}, title='{course.title}'")
                return CourseResponse.from_orm(course)
            except Exception as e:
                logger.error(f"[Service] 创建课程失败: {e}")
                # 如果是唯一约束错误，尝试添加序号
                if "唯一约束" in str(e) or "unique" in str(e).lower() or "violation" in str(e).lower():
                    counter += 1
                    title = f"{original_title}({counter})"
                    logger.info(f"[Service] 检测到重复名称，尝试新名称: '{title}'")
                    if counter > 100:  # 防止无限循环
                        raise ValidationException("课程名称重复次数过多，请使用不同的名称")
                else:
                    # 其他错误直接抛出
                    raise
    
    async def update_course(self, course_id: int, course_data: CourseUpdate, current_user_id: int = None) -> CourseResponse:
        """更新课程信息"""
        logger.info(f"[Service] 开始更新课程 ID: {course_id}, 数据: {course_data.dict(exclude_unset=True)}")
        
        course = await self.repo.get_course_by_id(course_id)
        if not course:
            raise NotFoundException("课程不存在")
        
        logger.info(f"[Service] 找到课程: ID={course.id}, 当前title='{course.title}'")
        
        # 如果提供了用户ID，验证权限
        if current_user_id is not None and course.teacher_id != current_user_id:
            raise ValidationException("无权限修改此课程")
        
        update_data = course_data.dict(exclude_unset=True)
        if "title" in update_data and (not update_data["title"] or update_data["title"].strip() == ""):
            raise ValidationException("课程名称不能为空")
        
        logger.info(f"[Service] 准备更新数据: {update_data}")
        updated_course = await self.repo.update_course(course_id, update_data)
        logger.info(f"[Service] 更新后课程: ID={updated_course.id}, 新title='{updated_course.title}'")
        
        response = CourseResponse.from_orm(updated_course)
        logger.info(f"[Service] 返回响应: {response.dict()}")
        return response
    
    async def delete_course(self, course_id: int, current_user_id: int = None):
        """删除课程"""
        course = await self.repo.get_course_by_id(course_id)
        if not course:
            raise NotFoundException("课程不存在")
        
        # 如果提供了用户ID，验证权限
        if current_user_id is not None and course.teacher_id != current_user_id:
            raise ValidationException("无权限删除此课程")
        
        await self.repo.delete_course(course_id)
    
    async def get_all_courses(self) -> list[CourseResponse]:
        """获取所有课程（管理员用）"""
        courses = await self.repo.get_all_courses()
        return [CourseResponse.from_orm(course) for course in courses] 
