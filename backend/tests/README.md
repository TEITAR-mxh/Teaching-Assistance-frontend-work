# 后端测试目录

用于存放后端的单元测试、集成测试等代码。

## 目录结构

```
tests/
├── conftest.py          # pytest配置文件，包含通用fixture
├── test_auth.py         # 认证模块测试
├── test_course.py       # 课程模块测试
├── test_admin.py        # 管理员模块测试
└── README.md           # 本文件
```

## 测试文件说明

### conftest.py
- 配置测试环境和数据库连接
- 提供通用的测试fixture（如client、auth_headers等）
- 设置测试数据库URL和会话管理

### test_auth.py
- 用户注册功能测试
- 用户登录功能测试
- 错误凭据处理测试
- 重复注册检测测试

### test_course.py
- 课程创建、读取、更新、删除测试
- 权限控制测试
- 错误处理测试

### test_admin.py
- 管理员用户管理功能测试
- 权限控制测试
- 统计信息获取测试

## 运行测试

### 安装测试依赖
```bash
pip install pytest pytest-asyncio httpx
```

### 运行所有测试
```bash
pytest tests/
```

### 运行特定模块测试
```bash
pytest tests/test_auth.py
pytest tests/test_course.py
pytest tests/test_admin.py
```

### 运行特定测试用例
```bash
pytest tests/test_auth.py::TestAuth::test_login_success
```

### 生成测试报告
```bash
pytest tests/ --html=report.html --self-contained-html
```

## 测试数据

测试使用独立的测试数据库，避免影响生产数据。测试数据库配置在 `conftest.py` 中设置。

## 注意事项

1. 运行测试前确保测试数据库已创建
2. 测试会自动清理数据，避免测试间相互影响
3. 所有测试都是独立的，可以单独运行
4. 使用fixture确保测试数据的可重复性

## 添加新测试

1. 在对应模块创建新的测试文件
2. 继承现有的测试类结构
3. 使用conftest.py中的fixture
4. 确保测试用例的独立性
5. 添加详细的测试文档 
