from abc import ABC, abstractmethod
from app.models.course_objective import CourseObjective
from app.models.course_syllabus import CourseSyllabus
from app.models.course_material import CourseMaterial

class TeacherRepository(ABC):
    @abstractmethod
    async def get_course_objective(self, course_id: int):
        pass
    
    @abstractmethod
    async def save_course_objective(self, course_id: int, content: str):
        pass
    
    @abstractmethod
    async def get_course_syllabus(self, course_id: int):
        pass
    
    @abstractmethod
    async def save_course_syllabus(self, course_id: int, content: str):
        pass
    
    @abstractmethod
    async def get_course_material(self, course_id: int):
        pass
    
    @abstractmethod
    async def save_course_material(self, course_id: int, content: str):
        pass 
