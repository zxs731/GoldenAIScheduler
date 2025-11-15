# utils.py
from langchain_openai import ChatOpenAI
import os

def parse_nl_to_cron(text: str) -> str:
    """
    自然语言转 cron 表达式。例如: "每周一下午3点" -> "0 15 * * 1"
    这里只示例用 GPT 模型，你可换成其他 GPT4/Claude/自托管API。
    """
    prompt = f'请将以下定时描述转换为标准cron表达式，仅返回表达式:\n"{text}"'
    model = ChatOpenAI(
        base_url=os.environ["openai_base_url"],
        openai_api_key=os.environ["openai_api_key"],
        model=os.environ.get("model", "gpt-4.1")
    )
    result = model.invoke(prompt)
    return result.content.strip().split('\n')[0]  # 只保留表达式