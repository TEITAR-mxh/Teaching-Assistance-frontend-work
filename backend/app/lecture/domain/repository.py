from abc import ABC, abstractmethod
from typing import List, Optional
from .entity import ChapterEntity, LectureEntity, ChapterOrderUpdate

class ChapterRepository(ABC):
    @abstractmethod
    async def create(self, chapter: ChapterEntity) -> ChapterEntity:
        pass
    
    @abstractmethod
    async def get_by_id(self, chapter_id: int) -> Optional[ChapterEntity]:
        pass
    
    @abstractmethod
    async def get_by_course_id(self, course_id: int) -> List[ChapterEntity]:
        pass
    
    @abstractmethod
    async def update(self, chapter: ChapterEntity) -> ChapterEntity:
        pass
    
    @abstractmethod
    async def delete(self, chapter_id: int) -> bool:
        pass
    
    @abstractmethod
    async def update_order(self, updates: List[ChapterOrderUpdate]) -> bool:
        pass

class LectureRepository(ABC):
    @abstractmethod
    async def create(self, lecture: LectureEntity) -> LectureEntity:
        pass
    
    @abstractmethod
    async def get_by_course_id(self, course_id: int) -> Optional[LectureEntity]:
        pass
    
    @abstractmethod
    async def update(self, lecture: LectureEntity) -> LectureEntity:
        pass
