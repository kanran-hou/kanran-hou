"""电商商品文案赛道 Prompt"""

from app.services.prompts.base import PromptTemplate
from app.services.prompts.constraint import PROMPT_CONSTRAINT

SYSTEM_PROMPT = f"""你是电商商品文案优化专家。分析用户提供的商品文案，重点评估以下维度：

1. 标题转化力：是否包含利益承诺、紧迫感词（"限时""限量""秒杀"）、数字/价格锚点、关键词覆盖
2. 情绪信任度：是否建立信任感（权威背书/销量数据/用户评价）、是否触发购买紧迫感
3. 卖点结构：是否遵循 FAB 法则（Feature-Advantage-Benefit）、促单话术（加购/下单）是否清晰、痛点-解决方案逻辑是否完整
4. 人群匹配：价格锚点是否与目标消费力匹配、使用场景描述是否精准

{PROMPT_CONSTRAINT}"""

USER_PROMPT_TEMPLATE = """请分析以下电商商品文案，输出完整的结构化 JSON：

{text}"""

ecommerce_prompt = PromptTemplate(
    track_type="ecommerce",
    system_prompt=SYSTEM_PROMPT,
    user_prompt_template=USER_PROMPT_TEMPLATE,
    weights={"title": 0.30, "emotion": 0.20, "structure": 0.30, "audience": 0.20},
    version="1.0",
)
