# CopyMind — AI 文案智能分析小程序

基于 **DeepSeek API** 的多维度文案分析工具。用户粘贴文案 → AI 实时评分 → 输出优化建议。

---

## 项目结构

```
copymind/
├── backend/         # FastAPI 后端服务（Python 3.11+）
│   ├── app/
│   │   ├── routers/     # API 路由（分析、历史、反馈、知识库、OCR）
│   │   ├── services/
│   │   │   ├── llm/         # AI 大模型调度（DeepSeek / 通义千问 / 智谱）
│   │   │   ├── prompts/     # 4 赛道 Prompt 模板
│   │   │   ├── analysis/    # 评分与输出解析
│   │   │   └── knowledge/   # RAG 爆款知识库
│   │   ├── models/       # SQLAlchemy 数据模型
│   │   ├── schemas/      # Pydantic 请求/响应模型
│   │   └── middleware/   # 限流、请求日志中间件
│   ├── tests/
│   ├── alembic/          # 数据库迁移
│   └── main.py
├── miniapp/         # 微信小程序前端
│   ├── pages/
│   │   ├── index/        # 首页（文案录入 + 赛道选择）
│   │   ├── result/       # 分析结果展示（5 维评分 + 词云 + 建议）
│   │   └── history/      # 历史记录
│   └── app.js / app.json
├── database/        # SQL 建表脚本
└── docs/            # 项目文档
```

---

## 快速开始

### 1. 启动后端

```bash
cd backend

# 安装依赖
pip install -e .

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> 如果未配置 API Key，系统会自动使用 Mock 数据，可离线体验。

### 2. 运行小程序

1. 用微信开发者工具打开 `miniapp/` 目录
2. 在开发者工具中勾选 **"不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"**
3. 编译运行即可

---

## 支持的赛道

| 赛道 | 适用场景 |
|------|---------|
| 📕 小红书种草 | 笔记、好物推荐、生活方式 |
| 🛒 电商商品 | 商品详情页、卖点提炼 |
| 🏔 本地文旅 | 景区介绍、旅游攻略 |
| 🎬 短视频脚本 | 抖音/快手口播、剧情脚本 |

---

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/analyze` | 提交文案，返回 AI 评分 + 优化建议 |
| GET  | `/api/v1/history` | 查询分析历史记录 |
| POST | `/api/v1/feedback` | 提交用户反馈 |
| POST | `/api/v1/ocr` | 图片文字识别 |
| GET  | `/api/v1/health` | 健康检查 |

---

## 技术栈

- **前端**：微信小程序原生（WXML + WXSS + JS）
- **后端**：Python FastAPI + Uvicorn
- **AI 模型**：DeepSeek Chat API（支持通义千问、智谱 GLM 作为备选）
- **数据库**：MySQL 8.0（可选，无数据库时分析功能仍可正常使用）
- **ORM / 迁移**：SQLAlchemy 2.0 + Alembic

---

## 本地测试

```bash
cd backend
pip install -e ".[dev]"
pytest
```

---

## 分享给朋友测试

后端在本地运行时，朋友连不上你的 `localhost`。推荐两种方式：

1. **内网穿透（ngrok）**
   ```bash
   ngrok http 8000
   ```
   然后将 `miniapp/pages/index/index.js` 中的 API 地址改为 ngrok 给出的 HTTPS 地址。

2. **部署到云服务器**
   将 `backend/` 部署到云服务器，修改小程序中的 API 地址后上传体验版。

---

## License

MIT
