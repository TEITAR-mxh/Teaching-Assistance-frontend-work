from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...core.database import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ...core.helpers.token import verify_token
from ..application.service import ChapterService, LectureService
from ..application.schema import (
    ChapterCreate, ChapterUpdate, ChapterResponse, ChapterListResponse,
    LectureResponse, LectureGenerationRequest, LectureGenerationResponse
)
from ..adapter.repository import ChapterRepositoryImpl, LectureRepositoryImpl

router = APIRouter(prefix="/lecture", tags=["lecture"])
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """获取当前用户ID"""
    try:
        payload = verify_token(credentials.credentials)
        user_id = int(payload.get("sub"))
        return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail="无效的认证令牌")

# 依赖注入
async def get_chapter_service(session: AsyncSession = Depends(get_db)) -> ChapterService:
    chapter_repo = ChapterRepositoryImpl(session)
    return ChapterService(chapter_repo)

async def get_lecture_service(session: AsyncSession = Depends(get_db)) -> LectureService:
    chapter_repo = ChapterRepositoryImpl(session)
    lecture_repo = LectureRepositoryImpl(session)
    return LectureService(lecture_repo, chapter_repo)

# 章节管理API
@router.post("/chapters", response_model=ChapterResponse)
async def create_chapter(
    chapter_data: ChapterCreate,
    current_user_id: int = Depends(get_current_user_id),
    chapter_service: ChapterService = Depends(get_chapter_service)
):
    """创建新章节"""
    try:
        chapter = await chapter_service.create_chapter(chapter_data)
        return chapter
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建章节失败: {str(e)}"
        )

@router.get("/chapters/course/{course_id}", response_model=List[ChapterResponse])
async def get_chapters_by_course(
    course_id: int,
    current_user_id: int = Depends(get_current_user_id),
    chapter_service: ChapterService = Depends(get_chapter_service)
):
    """获取课程的所有章节"""
    try:
        chapters = await chapter_service.get_chapters_by_course(course_id)
        return chapters
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取章节列表失败: {str(e)}"
        )

@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter_by_id(
    chapter_id: int,
    current_user_id: int = Depends(get_current_user_id),
    chapter_service: ChapterService = Depends(get_chapter_service)
):
    """根据ID获取章节"""
    try:
        chapter = await chapter_service.get_chapter_by_id(chapter_id)
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="章节不存在"
            )
        return chapter
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取章节失败: {str(e)}"
        )

@router.put("/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    chapter_id: int,
    update_data: ChapterUpdate,
    current_user_id: int = Depends(get_current_user_id),
    chapter_service: ChapterService = Depends(get_chapter_service)
):
    """更新章节"""
    try:
        chapter = await chapter_service.update_chapter(chapter_id, update_data)
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="章节不存在"
            )
        return chapter
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新章节失败: {str(e)}"
        )

@router.delete("/chapters/{chapter_id}")
async def delete_chapter(
    chapter_id: int,
    current_user_id: int = Depends(get_current_user_id),
    chapter_service: ChapterService = Depends(get_chapter_service)
):
    """删除章节"""
    try:
        success = await chapter_service.delete_chapter(chapter_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="章节不存在"
            )
        return {"message": "章节删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除章节失败: {str(e)}"
        )

# 讲义管理API
@router.post("/generate", response_model=LectureGenerationResponse)
async def generate_lecture(
    request: LectureGenerationRequest,
    current_user_id: int = Depends(get_current_user_id),
    lecture_service: LectureService = Depends(get_lecture_service)
):
    """根据章节生成讲义"""
    try:
        lecture = await lecture_service.generate_lecture(request.course_id, request.chapter_ids)
        return LectureGenerationResponse(
            success=True,
            message="讲义生成成功",
            lecture_id=lecture.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成讲义失败: {str(e)}"
        )

@router.get("/course/{course_id}", response_model=LectureResponse)
async def get_lecture_by_course(
    course_id: int,
    current_user_id: int = Depends(get_current_user_id),
    lecture_service: LectureService = Depends(get_lecture_service)
):
    """获取课程的讲义"""
    try:
        lecture = await lecture_service.get_lecture_by_course(course_id)
        if not lecture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="讲义不存在"
            )
        return lecture
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取讲义失败: {str(e)}"
        )
