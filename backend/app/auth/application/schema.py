from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str
    userId: int
    username: str
    role: str
    message: str = "登录成功"

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "teacher"

class RegisterResponse(BaseModel):
    success: bool
    message: str

class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    role: str 