from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

# Chapter Schemas
class ChapterCreate(BaseModel):
    course_id: int = Field(..., gt=0, description="课程ID必须大于0")
    title: str
    content: str = ""
    status: str = "empty"
    order_index: int = 0

    @validator('course_id')
    def validate_course_id(cls, v):
        if v <= 0:
            raise ValueError('课程ID必须大于0')
        return v

class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    order_index: Optional[int] = None

class ChapterResponse(BaseModel):
    id: int
    course_id: int
    title: str
    content: str
    status: str
    order_index: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChapterOrderUpdateSchema(BaseModel):
    chapter_id: int
    new_order: int

# Lecture Schemas
class LectureCreate(BaseModel):
    course_id: int
    title: str
    content: str

class LectureResponse(BaseModel):
    id: int
    course_id: int
    title: str
    content: str
    generated_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LectureGenerationRequest(BaseModel):
    course_id: int
    chapter_ids: List[int]

# Response Schemas
class ChapterListResponse(BaseModel):
    chapters: List[ChapterResponse]
    total: int

class LectureGenerationResponse(BaseModel):
    success: bool
    message: str
    lecture_id: Optional[int] = None
