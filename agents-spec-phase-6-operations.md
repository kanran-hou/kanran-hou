 # Phase 6 — 运营增值功能（P2）
 
 > **目标**: 实现用户反馈入口、用户分层/批量分析权限、后台数据看板、自动化数据统计与文本聚类分析。
 > **依赖**: Phase 1（数据库） + Phase 2（分析 API） + Phase 3（前端框架）
 > **产出**: 反馈系统 + 权限系统 + 数据看板 + 自动化脚本
 
 ---
 
 ## 技术决策
 
 | 选项 | 选定 | 理由 |
 |------|------|------|
 | 后台框架 | **FastAPI Admin** 或 **Simple UI** | 轻量、与现有后端一致 |
 | 定时任务 | **APScheduler** | 与 FastAPI 集成简单 |
 | 文本聚类 | **jieba + scikit-learn (KMeans)** | 中文分词 + 成熟的聚类算法 |
 | 前端后台 | **Vue 3 + Element Plus** | 后台管理界面标准方案 |
 
 ---
 
 ## 任务清单
 
 ### 6.1 用户反馈入口
 - [ ] 在分析结果页底部增加「反馈」入口（文字链接 / 图标按钮）
 - [ ] 实现反馈弹窗页面
   - 反馈类型单选（分析不准确 / 优化建议无效 / 其他）
   - 文本输入框（最多 500 字）
   - 提交按钮 + 防重复提交
 - [ ] 实现 `POST /api/v1/feedback` 端点
   - 请求体：`{ user_openid, analysis_id, feedback_type, feedback_text }`
   - 自动记录到 `user_feedback` 表
 - [ ] 反馈提交后 Toast 提示「感谢您的反馈，我们将持续优化」
 - [ ] 后台反馈管理页面（反馈列表、按类型筛选、标记已处理）
 
 ### 6.2 用户分层与权限管理
 - [ ] 定义用户分层策略
   - 普通用户：每日 5 次免费分析
   - 高频用户（活跃用户）：每日 20 次分析，需人工审核开通
   - VIP 预留：后期可扩展付费
 - [ ] 实现 `users` 表扩展
   - 添加 `tier` 字段（normal / frequent / vip）
   - 添加 `daily_analysis_count`, `last_analysis_date` 字段
 - [ ] 实现次数限制中间件
   - 每次分析前查询当日使用次数
   - 超限返回 429 状态码 + 提示文案
 - [ ] 实现 `POST /api/v1/admin/users/batch` 批量开通高频权限（管理员接口）
 - [ ] 实现「批量分析」功能入口（高频用户可见）
   - 支持一次性提交最多 5 篇文案（输入框数组或文件批量上传）
   - 后台串行/并发执行分析，结果列表展示
 
 ### 6.3 后台数据看板
 - [ ] 设计数据看板首页布局（卡片式：关键指标 + 趋势图 + 排行榜）
 - [ ] 实现以下核心指标统计
   - 总分析次数（今日 / 本周 / 本月 / 累计）
   - 各赛道文案平均综合得分
   - S/A/B/C 评级分布占比
   - 活跃用户数（日 / 周 / 月）
 - [ ] 实现趋势图（ECharts）
   - 近 7 日/30 日分析量趋势折线图
   - 各赛道分析占比饼图
 - [ ] 实现「高频缺陷类型」排行榜
   - 统计所有分析结果中 title_score < 60 的占比 = "标题吸引力不足"
   - 类似统计 emotion_score / structure_score / audience_score 低分占比
 - [ ] 实现「功能点击率」统计
   - 依据 `users_behavior_log` 统计各行为类型占比
 
 ### 6.4 自动化数据处理
 - [ ] 实现定时 SQL 脚本（APScheduler，每日凌晨 3:00 执行）
   - 统计并存储前一日运营指标到 `daily_stats` 汇总表
   - 计算各赛道平均分、各评级占比、活跃用户数
   - 清理超过 90 天的冗余日志
 - [ ] 实现 Python 文本聚类脚本（每周执行）
   - 从 `user_feedback` 表读取反馈文本
   - jieba 分词 → TF-IDF 向量化 → KMeans 聚类（k=3~5）
   - 输出高频产品缺陷分类报告
   - 结果写入 `feedback_clusters` 表
   - 报告以 Markdown 格式保存到 `docs/feedback-report-weekly.md`
 - [ ] 实现聚类报告查看页面（后台数据看板子页面）
 
 ---
 
 ## 新增数据库表
 
 ### Table: `users`
 
 | 字段名 | 类型 | 说明 |
 |--------|------|------|
 | id | BIGINT PK AUTO | 主键 |
 | user_openid | VARCHAR(64) UNIQUE | 微信用户标识 |
 | tier | ENUM('normal','frequent','vip') | 用户层级 |
 | daily_analysis_count | INT DEFAULT 0 | 当日已分析次数 |
 | last_analysis_date | DATE | 最后分析日期 |
 | created_at | DATETIME | 注册时间 |
 | updated_at | DATETIME | 更新时间 |
 
 ### Table: `daily_stats`
 
 | 字段名 | 类型 | 说明 |
 |--------|------|------|
 | id | BIGINT PK AUTO | 主键 |
 | stat_date | DATE UNIQUE | 统计日期 |
 | total_analysis | INT | 总分析次数 |
 | avg_overall_score | DECIMAL(5,2) | 平均综合分 |
 | grade_distribution | JSON | 各评级数量 `{"S":10,"A":20,...}` |
 | track_distribution | JSON | 各赛道数量 |
 | active_users | INT | 活跃用户数 |
 | created_at | DATETIME | 记录时间 |
 
 ### Table: `feedback_clusters`
 
 | 字段名 | 类型 | 说明 |
 |--------|------|------|
 | id | BIGINT PK AUTO | 主键 |
 | cluster_id | INT | 聚类编号 |
 | cluster_label | VARCHAR(64) | 聚类标签（如"标题分析不准"） |
 | sample_count | INT | 样本数量 |
 | sample_texts | JSON | 代表样本（最多 5 条） |
 | created_week | VARCHAR(16) | 统计周（如 "2026-W27"） |
 
 ---
 
 ## 验收标准
 
 1. 分析结果页底部反馈入口可见，点击弹出反馈弹窗
 2. 反馈提交成功写入 `user_feedback` 表
 3. 后台反馈管理页面展示反馈列表，支持按类型筛选
 4. 普通用户同一日分析超过 5 次返回 429 错误提示
 5. 管理员批量开通高频接口可用
 6. 高频用户可见批量分析入口，支持一次提交多篇文案
 7. 后台数据看板展示关键指标 + 趋势图 + 排行榜
 8. 高频缺陷排行榜数据逻辑正确
 9. 定时 SQL 脚本每日凌晨执行成功，`daily_stats` 表有数据
 10. 文本聚类脚本可运行，输出可读的缺陷分类报告
 11. 聚类报告在后台页面可查看
