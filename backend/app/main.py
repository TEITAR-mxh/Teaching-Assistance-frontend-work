from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.user.adapter.input import router as user_router
from app.admin.adapter.input import router as admin_router
from app.teacher.adapter.input import router as teacher_router
from app.auth.adapter.input import router as auth_router
from app.course.adapter.input import router as course_router

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

@app.get("/")
def read_root():
    return {"msg": "Teaching Assistance Backend is running."} 
