from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CourseObjectiveRequest(BaseModel):
    course_content: str
    teaching_target: str

class CourseObjectiveResponse(BaseModel):
    id: int
    course_id: int
    course_content: Optional[str] = None
    teaching_target: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CourseSyllabusRequest(BaseModel):
    content: str

class CourseSyllabusResponse(BaseModel):
    id: int
    course_id: int
    content: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

class CourseMaterialRequest(BaseModel):
    content: str

class CourseMaterialResponse(BaseModel):
    id: int
    course_id: int
    content: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

class GenerateRequest(BaseModel):
    prompt: str 
