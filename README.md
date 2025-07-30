# 智教未来 - Teaching Assistance Demo

基于 Vue 3 + TypeScript + Vite 构建的智能教学辅助系统，包含前端课程管理和后端 API 服务。

## 项目概述

本项目是一个完整的教学辅助系统，包含：

- **前端**：Vue 3 + TypeScript + Vite 构建的现代化 Web 应用
- **后端**：FastAPI + SQLAlchemy + PostgreSQL 构建的 RESTful API
- **功能**：课程管理、教学讲义编辑、AI 内容生成、用户认证等

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/Teaching-Assistance-demo.git
cd Teaching-Assistance-demo
```

### 2. 后端设置

#### 2.1 安装 uv 并创建虚拟环境

```bash
# 安装 uv (如果还没有安装)
pip install uv

# 进入后端目录
cd backend

# 使用 uv 创建虚拟环境并安装依赖
uv sync
```

#### 2.2 配置数据库

1. **安装 PostgreSQL**
   - 下载并安装 PostgreSQL: https://www.postgresql.org/download/
   - 创建数据库：`createdb teaching_assistance`

2. **配置环境变量**
   ```bash
   cd backend
   cp env.example .env
   ```
   
   编辑 `.env` 文件，填入你的数据库配置：
   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_actual_password
   POSTGRES_DB=teaching_assistance
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

#### 2.3 数据库迁移

```bash
cd backend
uv run alembic upgrade head
```

#### 2.4 启动后端服务

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 [http://localhost:8000](http://localhost:8000) 上启动。

### 3. 前端设置

#### 3.1 安装依赖

```bash
# 在项目根目录
npm install
# 或者使用 yarn
yarn install
```

#### 3.2 启动开发服务器

```bash
npm run dev
# 或者使用 yarn
yarn dev
```

前端服务将在 [http://localhost:5173](http://localhost:5173) 上启动。

## 项目结构

```
Teaching-Assistance-demo/
├── src/                    # 前端源码
│   ├── api/               # API 请求
│   ├── assets/            # 静态资源
│   ├── components/        # 公共组件
│   ├── router/            # 路由配置
│   ├── views/             # 页面组件
│   └── ...
├── backend/               # 后端源码
│   ├── app/              # 应用代码
│   │   ├── admin/        # 管理员模块
│   │   ├── auth/         # 认证模块
│   │   ├── course/       # 课程模块
│   │   ├── teacher/      # 教师模块
│   │   ├── user/         # 用户模块
│   │   └── core/         # 核心配置
│   ├── tests/            # 测试文件
│   └── requirements.txt   # Python 依赖
├── public/               # 静态文件
└── README.md            # 项目说明
```

## 主要功能

### 前端功能
- 📚 **课程管理**：创建、编辑、删除课程
- 📝 **教学讲义**：Markdown 编辑器，支持数学公式
- 🤖 **AI 生成**：智能生成课程内容和讲义
- 👥 **用户管理**：教师和管理员角色管理
- 📊 **课程大纲**：可视化课程结构

### 后端功能
- 🔐 **用户认证**：JWT Token 认证
- 📚 **课程 CRUD**：完整的课程管理 API
- 📝 **内容管理**：讲义、大纲、目标管理
- 🤖 **AI 集成**：智能内容生成接口
- 🗄️ **数据持久化**：PostgreSQL 数据库

## 安全注意事项

⚠️ **重要**：请确保以下敏感信息不会被提交到 Git 仓库：

1. **数据库密码**：在 `.env` 文件中配置，该文件已被 `.gitignore` 忽略
2. **JWT 密钥**：使用强密钥，不要使用默认值
3. **API 密钥**：如果集成第三方服务，请妥善保管

### 环境变量配置

```bash
# 复制示例文件
cp backend/env.example backend/.env

# 编辑配置文件，填入真实值
nano backend/.env
```

## 开发指南

### 添加新功能

1. **后端**：在 `backend/app/` 下创建新模块
2. **前端**：在 `src/` 下添加新组件和页面
3. **API**：在 `src/api/` 下添加新的 API 调用

### 数据库迁移

```bash
cd backend
# 创建新迁移
uv run alembic revision --autogenerate -m "描述"

# 应用迁移
uv run alembic upgrade head
```

### 测试

```bash
# 后端测试
cd backend
uv run pytest

# 前端测试
npm run test
```

## 部署

### 生产环境配置

1. 设置 `DEBUG=False`
2. 使用强密钥
3. 配置生产数据库
4. 设置 CORS 策略

### Docker 部署

```bash
# 构建镜像
docker build -t teaching-assistance .

# 运行容器
docker run -p 8000:8000 teaching-assistance
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或联系项目维护者。
