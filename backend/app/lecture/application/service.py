from typing import List, Optional
from ..domain.entity import ChapterEntity, LectureEntity, ChapterOrderUpdate
from ..domain.repository import ChapterRepository, LectureRepository
from .schema import ChapterCreate, ChapterUpdate, ChapterResponse, LectureCreate, LectureResponse

class ChapterService:
    def __init__(self, chapter_repo: ChapterRepository):
        self.chapter_repo = chapter_repo
    
    async def create_chapter(self, chapter_data: ChapterCreate) -> ChapterResponse:
        """创建新章节"""
        chapter = ChapterEntity(
            id=None,
            course_id=chapter_data.course_id,
            title=chapter_data.title,
            content=chapter_data.content,
            status=chapter_data.status,
            order_index=chapter_data.order_index
        )
        
        created_chapter = await self.chapter_repo.create(chapter)
        return ChapterResponse.model_validate(created_chapter)
    
    async def get_chapters_by_course(self, course_id: int) -> List[ChapterResponse]:
        """获取课程的所有章节"""
        chapters = await self.chapter_repo.get_by_course_id(course_id)
        return [ChapterResponse.model_validate(chapter) for chapter in chapters]
    
    async def get_chapter_by_id(self, chapter_id: int) -> Optional[ChapterResponse]:
        """根据ID获取章节"""
        chapter = await self.chapter_repo.get_by_id(chapter_id)
        if chapter:
            return ChapterResponse.model_validate(chapter)
        return None
    
    async def update_chapter(self, chapter_id: int, update_data: ChapterUpdate) -> Optional[ChapterResponse]:
        """更新章节"""
        existing_chapter = await self.chapter_repo.get_by_id(chapter_id)
        if not existing_chapter:
            return None
        
        # 更新字段
        if update_data.title is not None:
            existing_chapter.title = update_data.title
        if update_data.content is not None:
            existing_chapter.content = update_data.content
        if update_data.status is not None:
            existing_chapter.status = update_data.status
        if update_data.order_index is not None:
            existing_chapter.order_index = update_data.order_index
        
        updated_chapter = await self.chapter_repo.update(existing_chapter)
        return ChapterResponse.model_validate(updated_chapter)
    
    async def delete_chapter(self, chapter_id: int) -> bool:
        """删除章节"""
        return await self.chapter_repo.delete(chapter_id)
    
    async def update_chapter_order(self, updates: List[ChapterOrderUpdate]) -> bool:
        """更新章节顺序"""
        order_updates = [
            ChapterOrderUpdate(
                chapter_id=update.chapter_id,
                new_order=update.new_order
            )
            for update in updates
        ]
        return await self.chapter_repo.update_order(order_updates)

class LectureService:
    def __init__(self, lecture_repo: LectureRepository, chapter_repo: ChapterRepository):
        self.lecture_repo = lecture_repo
        self.chapter_repo = chapter_repo
    
    async def generate_lecture(self, course_id: int, chapter_ids: List[int]) -> LectureResponse:
        """根据章节生成讲义"""
        # 获取所有章节内容
        chapters = []
        for chapter_id in chapter_ids:
            chapter = await self.chapter_repo.get_by_id(chapter_id)
            if chapter:
                chapters.append(chapter)
        
        if not chapters:
            raise ValueError("没有找到有效的章节")
        
        # 按顺序排列章节
        chapters.sort(key=lambda x: x.order_index)
        
        # 生成讲义内容
        lecture_title = f"课程讲义 - {chapters[0].title.split('：')[0] if '：' in chapters[0].title else '课程'}"
        lecture_content = self._combine_chapters_content(chapters)
        
        # 创建讲义
        lecture = LectureEntity(
            id=None,
            course_id=course_id,
            title=lecture_title,
            content=lecture_content
        )
        
        created_lecture = await self.lecture_repo.create(lecture)
        return LectureResponse.model_validate(created_lecture)
    
    def _combine_chapters_content(self, chapters: List[ChapterEntity]) -> str:
        """合并章节内容"""
        content_parts = []
        
        for i, chapter in enumerate(chapters, 1):
            content_parts.append(f"# {chapter.title}")
            if chapter.content:
                content_parts.append(chapter.content)
            content_parts.append("")  # 空行分隔
        
        return "\n".join(content_parts)
    
    async def get_lecture_by_course(self, course_id: int) -> Optional[LectureResponse]:
        """获取课程的讲义"""
        lecture = await self.lecture_repo.get_by_course_id(course_id)
        if lecture:
            return LectureResponse.model_validate(lecture)
        return None
