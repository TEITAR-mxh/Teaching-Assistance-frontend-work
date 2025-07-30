from sqlalchemy.orm import declarative_base

Base = declarative_base()

# 导入所有模型，确保 Alembic 能够检测到
from .user import User
from .course import Course
from .course_objective import CourseObjective
from .course_syllabus import CourseSyllabus
from .course_material import CourseMaterial 
