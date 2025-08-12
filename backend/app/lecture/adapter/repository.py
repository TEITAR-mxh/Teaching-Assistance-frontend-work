from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from ..domain.entity import ChapterEntity, LectureEntity, ChapterOrderUpdate
from ..domain.repository import ChapterRepository, LectureRepository
from ...models.lecture import Chapter, Lecture

class ChapterRepositoryImpl(ChapterRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, chapter: ChapterEntity) -> ChapterEntity:
        db_chapter = Chapter(
            course_id=chapter.course_id,
            title=chapter.title,
            content=chapter.content,
            status=chapter.status,
            order_index=chapter.order_index
        )
        
        self.session.add(db_chapter)
        await self.session.commit()
        await self.session.refresh(db_chapter)
        
        return ChapterEntity(
            id=db_chapter.id,
            course_id=db_chapter.course_id,
            title=db_chapter.title,
            content=db_chapter.content,
            status=db_chapter.status,
            order_index=db_chapter.order_index,
            created_at=db_chapter.created_at,
            updated_at=db_chapter.updated_at
        )
    
    async def get_by_id(self, chapter_id: int) -> Optional[ChapterEntity]:
        result = await self.session.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        db_chapter = result.scalar_one_or_none()
        
        if db_chapter:
            return ChapterEntity(
                id=db_chapter.id,
                course_id=db_chapter.course_id,
                title=db_chapter.title,
                content=db_chapter.content,
                status=db_chapter.status,
                order_index=db_chapter.order_index,
                created_at=db_chapter.created_at,
                updated_at=db_chapter.updated_at
            )
        return None
    
    async def get_by_course_id(self, course_id: int) -> List[ChapterEntity]:
        result = await self.session.execute(
            select(Chapter)
            .where(Chapter.course_id == course_id)
            .order_by(Chapter.order_index)
        )
        db_chapters = result.scalars().all()
        
        return [
            ChapterEntity(
                id=chapter.id,
                course_id=chapter.course_id,
                title=chapter.title,
                content=chapter.content,
                status=chapter.status,
                order_index=chapter.order_index,
                created_at=chapter.created_at,
                updated_at=chapter.updated_at
            )
            for chapter in db_chapters
        ]
    
    async def update(self, chapter: ChapterEntity) -> ChapterEntity:
        if not chapter.id:
            raise ValueError("Chapter ID is required for update")
        
        await self.session.execute(
            update(Chapter)
            .where(Chapter.id == chapter.id)
            .values(
                title=chapter.title,
                content=chapter.content,
                status=chapter.status,
                order_index=chapter.order_index
            )
        )
        await self.session.commit()
        
        # 重新获取更新后的数据
        return await self.get_by_id(chapter.id)
    
    async def delete(self, chapter_id: int) -> bool:
        result = await self.session.execute(
            delete(Chapter).where(Chapter.id == chapter_id)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_order(self, updates: List[ChapterOrderUpdate]) -> bool:
        for update_item in updates:
            await self.session.execute(
                update(Chapter)
                .where(Chapter.id == update_item.chapter_id)
                .values(order_index=update_item.new_order)
            )
        
        await self.session.commit()
        return True

class LectureRepositoryImpl(LectureRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, lecture: LectureEntity) -> LectureEntity:
        db_lecture = Lecture(
            course_id=lecture.course_id,
            title=lecture.title,
            content=lecture.content
        )
        
        self.session.add(db_lecture)
        await self.session.commit()
        await self.session.refresh(db_lecture)
        
        return LectureEntity(
            id=db_lecture.id,
            course_id=db_lecture.course_id,
            title=db_lecture.title,
            content=db_lecture.content,
            generated_at=db_lecture.generated_at,
            updated_at=db_lecture.updated_at
        )
    
    async def get_by_course_id(self, course_id: int) -> Optional[LectureEntity]:
        result = await self.session.execute(
            select(Lecture).where(Lecture.course_id == course_id)
        )
        db_lecture = result.scalar_one_or_none()
        
        if db_lecture:
            return LectureEntity(
                id=db_lecture.id,
                course_id=db_lecture.course_id,
                title=db_lecture.title,
                content=db_lecture.content,
                generated_at=db_lecture.generated_at,
                updated_at=db_lecture.updated_at
            )
        return None
    
    async def update(self, lecture: LectureEntity) -> LectureEntity:
        if not lecture.id:
            raise ValueError("Lecture ID is required for update")
        
        await self.session.execute(
            update(Lecture)
            .where(Lecture.id == lecture.id)
            .values(
                title=lecture.title,
                content=lecture.content
            )
        )
        await self.session.commit()
        
        # 重新获取更新后的数据
        return await self.get_by_course_id(lecture.course_id)
