# Teaching-Assistance-demo Backend

本后端基于 FastAPI + SQLAlchemy + Alembic + PostgreSQL

## 目录结构

```
backend/
├── app/
│   ├── user/                  # 用户模块（DDD分层）
│   │   ├── domain/
│   │   │   ├── entity.py
│   │   │   ├── repository.py
│   │   │   ├── vo.py
│   │   │   └── usecase.py
│   │   ├── application/
│   │   │   ├── schema.py
│   │   │   ├── service.py
│   │   │   ├── exception.py
│   │   │   └── dto.py
│   │   ├── adapter/
│   │   │   ├── input.py
│   │   │   └── repository.py
│   │   └── __init__.py
│   ├── core/                  # 全局核心功能
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── repository.py
│   │   ├── exceptions.py
│   │   ├── helpers.py
│   │   └── __init__.py
│   ├── main.py                # FastAPI 入口
│   └── __init__.py
├── repository/                # 全局通用仓储实现/第三方集成
│   └── README.md
├── docker/                    # 容器化相关配置
│   └── README.md
├── tests/                     # 测试代码
│   └── README.md
├── alembic/                   # 数据库迁移
├── alembic.ini
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 说明
- 每个业务模块自成体系，采用 DDD 分层，便于扩展和维护。
- core 层包含全局配置、数据库、异常、工具、通用仓储等。
- repository/、docker/、tests/ 预留未来扩展。
