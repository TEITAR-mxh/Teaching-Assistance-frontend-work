from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.user.adapter.input import router as user_router
from app.admin.adapter.input import router as admin_router
from app.teacher.adapter.input import router as teacher_router
from app.auth.adapter.input import router as auth_router
from app.course.adapter.input import router as course_router
from app.lecture.adapter.input import router as lecture_router
from app.models import Base
from app.core.database import engine
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Teaching Assistance Backend", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # 前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含所有路由
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(teacher_router)
app.include_router(course_router)
app.include_router(lecture_router)

@app.on_event("startup")
async def startup_event():
    """应用启动时创建数据库表"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库表创建失败: {e}")

@app.get("/")
def read_root():
    return {"msg": "Teaching Assistance Backend is running."}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 测试数据库连接
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)} 
