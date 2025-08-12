from app.teacher.domain.repository import TeacherRepository
from app.teacher.application.schema import CourseObjectiveRequest, CourseSyllabusRequest, CourseMaterialRequest, GenerateRequest
from app.core.exceptions import NotFoundException

class TeacherService:
    def __init__(self, repo: TeacherRepository):
        self.repo = repo
    
    async def get_course_objective(self, course_id: int):
        obj = await self.repo.get_course_objective(course_id)
        if obj:
            return {
                "id": obj.id,
                "course_id": obj.course_id,
                "course_content": obj.course_content,
                "teaching_target": obj.teaching_target,
                "created_at": obj.created_at,
                "updated_at": obj.updated_at
            }
        # 返回符合响应模型的空结构，避免响应校验错误
        return {
            "id": 0,
            "course_id": course_id,
            "course_content": "",
            "teaching_target": "",
            "created_at": None,
            "updated_at": None,
        }
    
    async def generate_course_objective(self, course_id: int, request: GenerateRequest):
        """生成课程教学目标（模拟）"""
        # 这里应该调用 AI 服务，现在用模拟数据
        generated_content = f"基于提示 '{request.prompt}' 生成的课程教学目标内容..."
        return await self.repo.save_course_objective(course_id, generated_content)
    
    async def save_course_objective(self, course_id: int, request: CourseObjectiveRequest):
        try:
            obj = await self.repo.save_course_objective(course_id, request.course_content, request.teaching_target)
            return {
                "id": obj.id,
                "course_id": obj.course_id,
                "course_content": obj.course_content,
                "teaching_target": obj.teaching_target,
                "created_at": obj.created_at,
                "updated_at": obj.updated_at
            }
        except ValueError as e:
            # 课程不存在等业务逻辑错误
            raise ValueError(str(e))
        except Exception as e:
            # 数据库错误等其他异常
            raise Exception(f"保存课程目标失败: {str(e)}")
    
    async def get_course_syllabus(self, course_id: int):
        """获取课程大纲"""
        syllabus = await self.repo.get_course_syllabus(course_id)
        if not syllabus:
            return {"content": ""}
        return syllabus
    
    async def generate_course_syllabus(self, course_id: int, request: GenerateRequest):
        """生成课程大纲（模拟）"""
        # 这里应该调用 AI 服务，现在用模拟数据
        generated_content = f"基于提示 '{request.prompt}' 生成的课程大纲内容..."
        return await self.repo.save_course_syllabus(course_id, generated_content)
    
    async def save_course_syllabus(self, course_id: int, request: CourseSyllabusRequest):
        """保存课程大纲"""
        return await self.repo.save_course_syllabus(course_id, request.content)
    
    async def get_course_material(self, course_id: int):
        """获取课程讲义"""
        material = await self.repo.get_course_material(course_id)
        if not material:
            return {"content": ""}
        return material
    
    async def generate_course_material(self, course_id: int, request: GenerateRequest):
        """生成课程讲义（模拟）"""
        # 这里应该调用 AI 服务，现在用模拟数据
        generated_content = f"基于提示 '{request.prompt}' 生成的课程讲义内容..."
        return await self.repo.save_course_material(course_id, generated_content)
    
    async def save_course_material(self, course_id: int, request: CourseMaterialRequest):
        """保存课程讲义"""
        return await self.repo.save_course_material(course_id, request.content) 
