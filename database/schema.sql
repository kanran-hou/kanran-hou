 -- ============================================================
 -- CopyMind 数据库建表脚本
 -- 目标数据库: MySQL 8.0
 -- ============================================================
 
 CREATE DATABASE IF NOT EXISTS copymind
     DEFAULT CHARACTER SET utf8mb4
     DEFAULT COLLATE utf8mb4_unicode_ci;
 
 USE copymind;
 
 -- -----------------------------------------------------------
 -- 1. 文案分析记录表
 -- -----------------------------------------------------------
 CREATE TABLE IF NOT EXISTS copywriting_analysis (
     id              BIGINT          NOT NULL AUTO_INCREMENT  COMMENT '主键',
     user_openid     VARCHAR(64)     NOT NULL                 COMMENT '微信用户标识',
     original_text   LONGTEXT        NOT NULL                 COMMENT '用户提交原文',
     track_type      ENUM('xiaohongshu','ecommerce','local_tourism','short_video')
                                     NOT NULL                 COMMENT '赛道类型',
     title_score     DECIMAL(5,2)    DEFAULT NULL             COMMENT '标题评分 0-100',
     emotion_score   DECIMAL(5,2)    DEFAULT NULL             COMMENT '情绪评分 0-100',
     structure_score DECIMAL(5,2)    DEFAULT NULL             COMMENT '卖点结构评分 0-100',
     audience_score  DECIMAL(5,2)    DEFAULT NULL             COMMENT '人群匹配评分 0-100',
     overall_score   DECIMAL(5,2)    DEFAULT NULL             COMMENT '综合流量总分 0-100',
     overall_grade   ENUM('S','A','B','C')
                                     DEFAULT NULL             COMMENT '综合等级',
     analysis_raw    JSON            DEFAULT NULL             COMMENT 'AI 返回完整结构化数据',
     word_count      INT             DEFAULT NULL             COMMENT '原文字数',
     created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                              COMMENT '分析时间',
     PRIMARY KEY (id),
     INDEX idx_user_openid (user_openid),
     INDEX idx_track_type (track_type),
     INDEX idx_created_at (created_at)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
   COMMENT='文案特征与分析结果表';
 
 -- -----------------------------------------------------------
 -- 2. 用户行为埋点表
 -- -----------------------------------------------------------
 CREATE TABLE IF NOT EXISTS users_behavior_log (
     id              BIGINT          NOT NULL AUTO_INCREMENT  COMMENT '主键',
     user_openid     VARCHAR(64)     NOT NULL                 COMMENT '微信用户标识',
     action_type     VARCHAR(32)     NOT NULL                 COMMENT '行为类型',
     action_detail   JSON            DEFAULT NULL             COMMENT '行为附加数据',
     analysis_id     BIGINT          DEFAULT NULL             COMMENT '关联分析记录 ID',
     created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                              COMMENT '行为时间',
     PRIMARY KEY (id),
     INDEX idx_user_openid (user_openid),
     INDEX idx_action_type (action_type),
     INDEX idx_analysis_id (analysis_id),
     CONSTRAINT fk_behavior_analysis FOREIGN KEY (analysis_id)
         REFERENCES copywriting_analysis(id) ON DELETE SET NULL
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
   COMMENT='用户行为埋点表';
 
 -- -----------------------------------------------------------
 -- 3. 用户反馈表
 -- -----------------------------------------------------------
 CREATE TABLE IF NOT EXISTS user_feedback (
     id              BIGINT          NOT NULL AUTO_INCREMENT  COMMENT '主键',
     user_openid     VARCHAR(64)     NOT NULL                 COMMENT '微信用户标识',
     analysis_id     BIGINT          DEFAULT NULL             COMMENT '关联文案分析 ID',
     feedback_type   VARCHAR(32)     NOT NULL                 COMMENT '反馈类型',
     feedback_text   TEXT            DEFAULT NULL             COMMENT '反馈内容',
     created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                              COMMENT '反馈时间',
     PRIMARY KEY (id),
     INDEX idx_user_openid (user_openid),
     INDEX idx_feedback_type (feedback_type),
     INDEX idx_analysis_id (analysis_id),
     CONSTRAINT fk_feedback_analysis FOREIGN KEY (analysis_id)
         REFERENCES copywriting_analysis(id) ON DELETE SET NULL
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
   COMMENT='用户反馈表';

-- -----------------------------------------------------------
-- 2. 文案模板表（知识库）
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS copywriting_templates (
    id              BIGINT          NOT NULL AUTO_INCREMENT  COMMENT '主键',
    track_type      ENUM('xiaohongshu','ecommerce','local_tourism','short_video')
                                    NOT NULL                 COMMENT '赛道类型',
    title           VARCHAR(255)    NOT NULL                 COMMENT '文案标题',
    content         TEXT            NOT NULL                 COMMENT '文案正文',
    tags            JSON            DEFAULT NULL             COMMENT '标签列表',
    overall_score   DECIMAL(5,2)    DEFAULT NULL             COMMENT '综合评分',
    source          VARCHAR(64)     DEFAULT NULL             COMMENT '来源',
    vector_id       INT             DEFAULT NULL             COMMENT 'Faiss 向量索引 ID（预留）',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_track_type (track_type),
    INDEX idx_score (overall_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爆款文案模板知识库';

-- -----------------------------------------------------------
-- 5. 用户分层表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id                  BIGINT          NOT NULL AUTO_INCREMENT  COMMENT '主键',
    user_openid         VARCHAR(64)     NOT NULL                 COMMENT '微信用户标识',
    tier                ENUM('normal','frequent','vip')
                                        NOT NULL DEFAULT 'normal' COMMENT '用户层级',
    daily_analysis_count INT            NOT NULL DEFAULT 0       COMMENT '当日已分析次数',
    last_analysis_date  DATE            DEFAULT NULL             COMMENT '最后分析日期',
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                                 COMMENT '注册时间',
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                                                                 COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE INDEX idx_users_openid (user_openid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='用户分层表';

-- -----------------------------------------------------------
-- 6. 每日运营统计表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_stats (
    id                  BIGINT          NOT NULL AUTO_INCREMENT  COMMENT '主键',
    stat_date           DATE            NOT NULL                 COMMENT '统计日期',
    total_analysis      INT             NOT NULL DEFAULT 0       COMMENT '总分析次数',
    avg_overall_score   DECIMAL(5,2)    DEFAULT NULL             COMMENT '平均综合分',
    grade_distribution  JSON            DEFAULT NULL             COMMENT '各评级数量',
    track_distribution  JSON            DEFAULT NULL             COMMENT '各赛道数量',
    active_users        INT             DEFAULT 0                COMMENT '活跃用户数',
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                                                 COMMENT '记录时间',
    PRIMARY KEY (id),
    UNIQUE INDEX idx_stat_date (stat_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='每日运营统计表';

-- -----------------------------------------------------------
-- 7. 反馈聚类结果表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS feedback_clusters (
    id                  BIGINT          NOT NULL AUTO_INCREMENT  COMMENT '主键',
    cluster_id          INT             NOT NULL                 COMMENT '聚类编号',
    cluster_label       VARCHAR(64)     DEFAULT NULL             COMMENT '聚类标签',
    sample_count        INT             NOT NULL DEFAULT 0       COMMENT '样本数量',
    sample_texts        JSON            DEFAULT NULL             COMMENT '代表样本（最多 5 条）',
    created_week        VARCHAR(16)     NOT NULL                 COMMENT '统计周（如 "2026-W27"）',
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_created_week (created_week)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='反馈聚类结果表';

