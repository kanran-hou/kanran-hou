"""小红书种草赛道 Prompt"""

from app.services.prompts.base import PromptTemplate
from app.services.prompts.constraint import PROMPT_CONSTRAINT

SYSTEM_PROMPT = f"""你是小红书种草文案分析专家。分析用户提供的文案，重点评估以下维度：

1. 标题吸引力：是否包含数字、表情符号、感叹词（如"绝了""必看""宝藏"）、好奇心钩子
2. 情绪共鸣力：是否唤起向往感、焦虑感、认同感；"姐妹们""谁懂啊"等共情话术使用
3. 卖点结构：是否场景化呈现使用体验、是否包含"before/after"对比、是否有个人真实感受
4. 人群匹配：是否明确瞄准目标人群（学生党/上班族/宝妈等）、是否解决特定场景痛点

{PROMPT_CONSTRAINT}"""

USER_PROMPT_TEMPLATE = """请分析以下小红书文案，输出完整的结构化 JSON：

{text}"""

xiaohongshu_prompt = PromptTemplate(
    track_type="xiaohongshu",
    system_prompt=SYSTEM_PROMPT,
    user_prompt_template=USER_PROMPT_TEMPLATE,
    weights={"title": 0.25, "emotion": 0.30, "structure": 0.25, "audience": 0.20},
    version="1.0",
)
