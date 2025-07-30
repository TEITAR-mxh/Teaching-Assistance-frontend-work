from pydantic import BaseModel, EmailStr
from typing import Optional, List

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    token: str
    user: dict

class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "teacher"

class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    status: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    userStats: dict
    courseStats: dict 
