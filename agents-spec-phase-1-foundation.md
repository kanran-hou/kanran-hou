 # Phase 1 — 基础骨架搭建（P0）
 
 > **目标**: 搭建项目脚手架、数据库建表、后端 API 框架、基础配置，为后续所有功能提供运行基础。
 > **依赖**: 无
 > **产出**: 可运行的后端项目骨架 + 数据库初始化脚本
 
 ---
 
 ## 技术决策
 
 | 选项 | 选定 | 理由 |
 |------|------|------|
 | 后端框架 | **FastAPI（Python）** | 异步原生支持、自动生成 OpenAPI 文档、与 AI/ML 生态衔接好 |
 | 数据库 | **MySQL 8.0** | 需求文档明确指定 |
 | ORM | **SQLAlchemy 2.0 + Alembic** | FastAPI 生态标准配套 |
 | 向量库 | Phase 4 再定 | Phase 1 仅预留接口 |
 | 运行环境 | Python 3.11+ | FastAPI 最优版本 |
 
 ---
 
 ## 任务清单
 
 ### 1.1 项目脚手架
 - [x] 初始化后端项目目录结构
 - [x] 创建 `requirements.txt` / `pyproject.toml`
 - [x] 配置 `.env` 模板（数据库连接、API Key、环境标识）
 - [x] 配置 `.gitignore`
 - [x] 实现基础 `main.py`（FastAPI app 初始化、CORS 中间件）
 - [x] 实现健康检查 `/health` 端点
 - [x] 配置日志模块（loguru 或 structlog）
 
 ### 1.2 数据库设计与建表
 - [x] 设计并编写 `database/schema.sql`（3 张核心表）
   - `users_behavior_log` — 用户行为埋点表
   - `copywriting_analysis` — 文案特征与分析结果表
   - `user_feedback` — 用户反馈表
 - [x] 配置 Alembic 迁移工具
 - [x] 编写初始迁移脚本
 - [x] 编写种子数据脚本（可选：预置 4 条赛道示例数据）
 
 ### 1.3 后端基础 API 框架
 - [x] 实现数据库连接池配置（SQLAlchemy async session）
 - [x] 实现统一响应模型（`ApiResponse[T]`）
 - [x] 实现全局异常处理器
 - [x] 实现请求限流中间件（令牌桶 / 滑动窗口）
 - [x] 实现请求日志中间件（记录方法、路径、耗时、状态码）
 - [x] 实现 API 路由前缀管理（`/api/v1/...`）
 
 ### 1.4 基础工具模块
 - [x] 实现配置管理模块（pydantic-settings 加载 `.env`）
 - [x] 实现时间工具函数（UTC ↔ 东八区转换）
 - [x] 实现字符串工具函数（字数统计、分段、敏感词过滤预留）
 - [x] 实现重试装饰器 / 工具函数（用于后续 API 调用）
 
 ---
 
 ## 数据库表设计纲要
 
 ### Table: `copywriting_analysis`
 
 | 字段名 | 类型 | 说明 |
 |--------|------|------|
 | id | BIGINT PK AUTO | 主键 |
 | user_openid | VARCHAR(64) | 微信用户标识 |
 | original_text | TEXT | 用户提交原文 |
 | track_type | ENUM('xiaohongshu','ecommerce','local_tourism','short_video') | 赛道类型 |
 | title_score | DECIMAL(5,2) | 标题评分 0-100 |
 | emotion_score | DECIMAL(5,2) | 情绪评分 0-100 |
 | structure_score | DECIMAL(5,2) | 卖点结构评分 0-100 |
 | audience_score | DECIMAL(5,2) | 人群匹配评分 0-100 |
 | overall_score | DECIMAL(5,2) | 综合流量总分 0-100 |
 | overall_grade | ENUM('S','A','B','C') | 爆款潜力/中等/待优化/低分 |
 | analysis_raw | JSON | AI 返回完整结构化数据 |
 | word_count | INT | 原文字数 |
 | created_at | DATETIME | 分析时间 |
 
 ### Table: `users_behavior_log`
 
 | 字段名 | 类型 | 说明 |
 |--------|------|------|
 | id | BIGINT PK AUTO | 主键 |
 | user_openid | VARCHAR(64) | 微信用户标识 |
 | action_type | VARCHAR(32) | 行为类型（open/analyze/export/feedback） |
 | action_detail | JSON | 行为附加数据 |
 | analysis_id | BIGINT FK | 关联分析记录 ID |
 | created_at | DATETIME | 行为时间 |
 
 ### Table: `user_feedback`
 
 | 字段名 | 类型 | 说明 |
 |--------|------|------|
 | id | BIGINT PK AUTO | 主键 |
 | user_openid | VARCHAR(64) | 微信用户标识 |
 | analysis_id | BIGINT FK | 关联文案分析 ID |
 | feedback_type | VARCHAR(32) | 反馈类型（inaccurate/suggestion_invalid/other） |
 | feedback_text | TEXT | 反馈内容 |
 | created_at | DATETIME | 反馈时间 |
 
 ---
 
 ## 目录结构输出
 
 ```
 backend/
 ├── main.py                            # FastAPI 入口
 ├── pyproject.toml                     # 依赖管理
 ├── .env.example                       # 环境变量模板
 ├── .gitignore
 ├── alembic.ini                        # 迁移配置
 ├── alembic/
 │   ├── env.py
 │   └── versions/
 ├── app/
 │   ├── __init__.py
 │   ├── config.py                      # 配置管理
 │   ├── database.py                    # 数据库连接
 │   ├── models/                        # SQLAlchemy 模型
 │   │   ├── __init__.py
 │   │   ├── copywriting.py
 │   │   ├── behavior.py
 │   │   └── feedback.py
 │   ├── schemas/                       # Pydantic 模型
 │   │   ├── __init__.py
 │   │   ├── analysis.py
 │   │   └── common.py
 │   ├── routers/                       # API 路由
 │   │   ├── __init__.py
 │   │   └── health.py
 │   ├── middleware/                    # 中间件
 │   │   ├── __init__.py
 │   │   ├── rate_limit.py
 │   │   └── request_log.py
 │   ├── services/                      # 业务逻辑层（占位）
 │   │   └── __init__.py
 │   └── utils/                         # 工具函数
 │       ├── __init__.py
 │       ├── time_utils.py
 │       └── string_utils.py
 └── tests/
     ├── __init__.py
     ├── conftest.py
     ├── test_health.py
     └── test_database.py
 ```
 
 ---
 
 ## 验收标准
 
 1. `uvicorn main:app` 启动无报错
 2. `GET /health` 返回 `{"status": "ok", "timestamp": "..."}`
 3. 数据库建表脚本执行成功，3 张表可正常 INSERT / SELECT
 4. 请求日志中间件正确记录每次请求
 5. 限流中间件生效（连续请求触发 429）
 6. Alembic 可执行 `upgrade` / `downgrade`
 7. 项目结构符合规范，`.env.example` 不含真实密钥
