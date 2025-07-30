from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class CourseRepository(ABC):
    """课程管理仓库接口"""
    
    @abstractmethod
    async def get_courses_by_teacher(self, teacher_id: int) -> List:
        """获取教师的所有课程"""
        pass
    
    @abstractmethod
    async def get_course_by_id(self, course_id: int):
        """根据ID获取课程"""
        pass
    
    @abstractmethod
    async def create_course(self, course_data: Dict[str, Any]):
        """创建课程"""
        pass
    
    @abstractmethod
    async def update_course(self, course_id: int, course_data: Dict[str, Any]):
        """更新课程"""
        pass
    
    @abstractmethod
    async def delete_course(self, course_id: int):
        """删除课程"""
        pass
    
    @abstractmethod
    async def get_all_courses(self) -> List:
        """获取所有课程"""
        pass 