from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class ChapterEntity:
    id: Optional[int]
    course_id: int
    title: str
    content: str
    status: str  # empty, draft, published
    order_index: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class LectureEntity:
    id: Optional[int]
    course_id: int
    title: str
    content: str
    generated_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class ChapterOrderUpdate:
    chapter_id: int
    new_order: int

@dataclass
class LectureGenerationRequest:
    course_id: int
    chapter_ids: List[int]
