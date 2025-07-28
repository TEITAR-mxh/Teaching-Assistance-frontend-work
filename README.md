# 智教未来 - demo2

基于 Vue 3 + TypeScript + Vite 构建的课程管理前端系统。

## 快速开始

### 1. 安装依赖

```bash
# 使用 npm
npm install

# 或者使用 yarn
yarn install
```

### 2. 配置环境变量

复制 `.env.example` 文件并重命名为 `.env`，然后根据需要进行配置：

```env
VITE_API_BASE_URL=http://localhost:8080
```

### 3. 启动开发服务器

```bash
# 使用 npm
npm run dev

# 或者使用 yarn
yarn dev
```

开发服务器将在 [http://localhost:5173](http://localhost:5173) 上启动。

## 项目结构

```
src/
├── api/               # API 请求
├── assets/            # 静态资源
├── components/        # 公共组件
├── router/            # 路由配置
├── stores/            # 状态管理
├── styles/            # 全局样式
└── views/             # 页面组件
```