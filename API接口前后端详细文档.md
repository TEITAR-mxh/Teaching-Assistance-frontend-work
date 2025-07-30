# 前端-后端API接口映射文档

## 概述

本文档详细说明了前端Vue.js应用与后端FastAPI服务之间的接口对应关系。

## 基础配置

### 前端配置
- **基础URL**: `http://localhost:8000` (config.ts)
- **认证方式**: JWT Bearer Token
- **请求头**: `Authorization: Bearer <token>`

### 后端配置
- **服务端口**: 8000
- **CORS**: 允许 `http://localhost:5173` 和 `http://localhost:3000`
- **文档**: `http://localhost:8000/docs`

## 接口映射详情

### 1. 认证模块 (Auth)

#### 前端接口 (auth.ts)
```typescript
// 登录
login(email: string, password: string)
```

#### 后端接口
```
POST /auth/login
Content-Type: application/json

{
  "email": "teacher@qq.com",
  "password": "123456"
}
```

**响应**:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "userId": 1,
  "username": "teacher",
  "role": "teacher"
}
```

#### 前端接口 (auth.ts)
```typescript
// 注册
register(username: string, password: string, email: string, role: string)
```

#### 后端接口
```
POST /auth/register
Content-Type: application/json

{
  "username": "newteacher",
  "email": "newteacher@qq.com",
  "password": "123456",
  "role": "teacher"
}
```

#### 前端接口 (auth.ts)
```typescript
// 检查用户名可用性
checkUsernameAvailable(username: string)
```

#### 后端接口
```
GET /auth/check-username/{username}
```

#### 前端接口 (auth.ts)
```typescript
// 检查邮箱可用性
checkEmailAvailable(email: string)
```

#### 后端接口
```
GET /auth/check-email/{email}
```

#### 前端接口 (auth.ts)
```typescript
// 登出
logout()
```

#### 后端接口
```
POST /auth/logout
Authorization: Bearer <token>
```

#### 前端接口 (auth.ts)
```typescript
// 获取当前用户信息
getMe()
```

#### 后端接口
```
GET /auth/me
Authorization: Bearer <token>
```

### 2. 用户管理模块 (User)

#### 前端接口 (user.ts)
```typescript
// 获取用户列表
getUsers(): Promise<User[]>
```

#### 后端接口
```
GET /users/
Authorization: Bearer <token>
```

#### 前端接口 (user.ts)
```typescript
// 创建用户
createUser(userData: CreateUserRequest): Promise<User>
```

#### 后端接口
```
POST /users/
Authorization: Bearer <token>
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@qq.com",
  "password": "123456"
}
```

### 3. 课程管理模块 (Course)

#### 前端接口 (courseManger.ts)
```typescript
// 获取所有课程
getCourses(): Promise<Course[]>
```

#### 后端接口
```
GET /courses/
Authorization: Bearer <token>
```

#### 前端接口 (courseManger.ts)
```typescript
// 获取教师课程
getTeacherCourses(): Promise<Course[]>
```

#### 后端接口
```
GET /courses/teacher/{teacher_id}
Authorization: Bearer <token>
```

#### 前端接口 (courseManger.ts)
```typescript
// 获取课程详情
getCourseDetail(courseId: number): Promise<Course>
```

#### 后端接口
```
GET /courses/{course_id}
Authorization: Bearer <token>
```

#### 前端接口 (courseManger.ts)
```typescript
// 创建课程
createCourse(courseName: string): Promise<Course>
```

#### 后端接口
```
POST /courses/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "新课程",
  "description": "课程描述",
  "teacher_id": 1
}
```

#### 前端接口 (courseManger.ts)
```typescript
// 更新课程名称
updateCourseName(courseId: number, courseName: string): Promise<Course>
```

#### 后端接口
```
PUT /courses/{course_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "更新后的课程名称"
}
```

#### 前端接口 (courseManger.ts)
```typescript
// 删除课程
deleteCourse(courseId: number): Promise<Result>
```

#### 后端接口
```
DELETE /courses/{course_id}
Authorization: Bearer <token>
```

### 4. 教师功能模块 (Teacher)

#### 前端接口 (functions.ts)
```typescript
// 获取课程教学目标
getCourseObjective(courseId: number): Promise<Objective>
```

#### 后端接口
```
GET /teacher/objective/{course_id}
Authorization: Bearer <token>
```

#### 前端接口 (functions.ts)
```typescript
// AI生成课程教学目标
generateCourseObjective(courseId: number, prompt: string): Promise<Objective>
```

#### 后端接口
```
POST /teacher/objective/{course_id}/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "prompt": "请生成课程教学目标"
}
```

#### 前端接口 (functions.ts)
```typescript
// 保存课程教学目标
saveCourseObjective(courseId: number, objective: any): Promise<Objective>
```

#### 后端接口
```
POST /teacher/objective/{course_id}/save
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "教学目标内容"
}
```

#### 前端接口 (functions.ts)
```typescript
// 获取课程教学大纲
getCourseSyllabus(courseId: number): Promise<Syllabus>
```

#### 后端接口
```
GET /teacher/syllabus/{course_id}
Authorization: Bearer <token>
```

#### 前端接口 (functions.ts)
```typescript
// AI生成教学大纲
generateCourseSyllabus(courseId: number, prompt: string): Promise<Syllabus>
```

#### 后端接口
```
POST /teacher/syllabus/{course_id}/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "prompt": "请生成教学大纲"
}
```

#### 前端接口 (functions.ts)
```typescript
// 保存教学大纲
saveCourseSyllabus(courseId: number, syllabus: any): Promise<Syllabus>
```

#### 后端接口
```
POST /teacher/syllabus/{course_id}/save
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "教学大纲内容"
}
```

#### 前端接口 (functions.ts)
```typescript
// 获取课程讲义
getCourseMaterial(courseId: number): Promise<Material>
```

#### 后端接口
```
GET /teacher/material/{course_id}
Authorization: Bearer <token>
```

#### 前端接口 (functions.ts)
```typescript
// AI生成课程讲义
generateCourseMaterial(courseId: number, courseTitle: string, request: string): Promise<Material>
```

#### 后端接口
```
POST /teacher/material/{course_id}/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "courseTitle": "课程标题",
  "request": "生成请求"
}
```

#### 前端接口 (functions.ts)
```typescript
// 保存课程讲义
saveCourseMaterial(courseId: number, material: any): Promise<Material>
```

#### 后端接口
```
POST /teacher/material/{course_id}/save
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "讲义内容"
}
```

### 5. 管理员模块 (Admin)

#### 前端接口 (admin.ts)
```typescript
// 管理员登录
login(loginData: AdminLoginDTO): Promise<LoginResponse>
```

#### 后端接口
```
POST /admin/login
Content-Type: application/json

{
  "username": "admin",
  "password": "123456"
}
```

#### 前端接口 (admin.ts)
```typescript
// 获取仪表板统计数据
getDashboardData(): Promise<DashboardData>
```

#### 后端接口
```
GET /admin/statistics/dashboard
Authorization: Bearer <token>
```

#### 前端接口 (admin.ts)
```typescript
// 获取用户列表
getUserList(): Promise<User[]>
```

#### 后端接口
```
GET /admin/list
Authorization: Bearer <token>
```

#### 前端接口 (admin.ts)
```typescript
// 获取用户详情
getUser(userId: number): Promise<User>
```

#### 后端接口
```
GET /admin/{user_id}
Authorization: Bearer <token>
```

#### 前端接口 (admin.ts)
```typescript
// 添加用户
addUser(userData: User): Promise<string>
```

#### 后端接口
```
POST /admin/user/add
Authorization: Bearer <token>
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@qq.com",
  "password": "123456",
  "role": "teacher"
}
```

#### 前端接口 (admin.ts)
```typescript
// 删除用户
deleteUser(id: number): Promise<string>
```

#### 后端接口
```
DELETE /admin/delete/{user_id}
Authorization: Bearer <token>
```

#### 前端接口 (admin.ts)
```typescript
// 更新用户名
updateUsername(id: number, username: string): Promise<string>
```

#### 后端接口
```
PUT /admin/user/{user_id}/updateName
Authorization: Bearer <token>
Content-Type: application/json

{
  "username": "newusername"
}
```

#### 前端接口 (admin.ts)
```typescript
// 更新用户邮箱
updateEmail(id: number, email: string): Promise<string>
```

#### 后端接口
```
PUT /admin/user/{user_id}/updateEmail
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newemail@qq.com"
}
```

## 错误处理

### 常见HTTP状态码

- `200` - 请求成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未授权（需要登录）
- `403` - 禁止访问（权限不足）
- `404` - 资源不存在
- `500` - 服务器内部错误

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

## 认证流程

1. **登录**: 用户通过 `/auth/login` 获取JWT token
2. **存储**: 前端将token存储在localStorage和sessionStorage
3. **请求**: 每次API请求在Header中携带 `Authorization: Bearer <token>`
4. **验证**: 后端验证token有效性
5. **登出**: 用户登出时清除本地存储的token

## 数据模型映射

### 用户模型 (User)
```typescript
interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

### 课程模型 (Course)
```typescript
interface Course {
  id: number;
  title: string;
  description: string;
  teacher_id: number;
  status: string;
  created_at: string;
  updated_at: string;
}
```

### 教学目标模型 (CourseObjective)
```typescript
interface CourseObjective {
  id: number;
  course_id: number;
  content: string;
  created_at: string;
  updated_at: string;
}
```

### 教学大纲模型 (CourseSyllabus)
```typescript
interface CourseSyllabus {
  id: number;
  course_id: number;
  content: string;
  created_at: string;
  updated_at: string;
}
```

### 课程讲义模型 (CourseMaterial)
```typescript
interface CourseMaterial {
  id: number;
  course_id: number;
  content: string;
  created_at: string;
  updated_at: string;
}
```

## 开发建议

1. **统一错误处理**: 前端统一处理API错误响应
2. **Token管理**: 实现token自动刷新机制
3. **请求拦截**: 使用axios拦截器统一添加认证头
4. **响应缓存**: 对不常变化的数据实现缓存
5. **加载状态**: 为异步请求添加加载状态指示
6. **表单验证**: 前后端都进行数据验证

## 测试建议

1. **API测试**: 使用Postman或类似工具测试后端API
2. **集成测试**: 测试前后端完整交互流程
3. **错误测试**: 测试各种错误情况的处理
4. **性能测试**: 测试API响应时间和并发处理能力
