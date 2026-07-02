"""短视频脚本赛道 Prompt"""

from app.services.prompts.base import PromptTemplate
from app.services.prompts.constraint import PROMPT_CONSTRAINT

SYSTEM_PROMPT = f"""你是短视频脚本分析专家。分析用户提供的短视频脚本/口播稿，重点评估以下维度：

1. 标题钩子力：前 3 秒是否有悬念/反问/惊人数据/冲突开场、是否有效抓住注意力
2. 情绪密度：情绪起伏节奏是否紧凑、每 10-15 秒是否有新的情绪刺激点、结尾是否有互动引导
3. 结构节奏：信息密度是否合理、是否有"黄金 5 秒→内容主体→高潮→结尾引导"的完整结构
4. 人群匹配：是否针对特定人群（知识类/搞笑类/情感类）、完播率设计（信息增量频率）

{PROMPT_CONSTRAINT}"""

USER_PROMPT_TEMPLATE = """请分析以下短视频文案，输出完整的结构化 JSON：

{text}"""

short_video_prompt = PromptTemplate(
    track_type="short_video",
    system_prompt=SYSTEM_PROMPT,
    user_prompt_template=USER_PROMPT_TEMPLATE,
    weights={"title": 0.30, "emotion": 0.25, "structure": 0.30, "audience": 0.15},
    version="1.0",
)
