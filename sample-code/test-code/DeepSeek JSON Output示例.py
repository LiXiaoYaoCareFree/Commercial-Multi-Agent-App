import dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

dotenv.load_dotenv()

class SplitTask(BaseModel):
    task_count: int = Field(..., gt=0, le=10, description="拆分的子任务总数")
    tasks: list[str] = Field(..., description="拆分的任务列表")

client = OpenAI()

system_prompt = """用户将提问一个问题，请拆解这个问题为多个串联的小任务，拆解的小任务数量不超过10个，你可以使用任何假设的工具、LLM、代码等。
并以json格式输出，其中task_count字段代表拆分任务的总数，tasks为拆分的任务数组(tasks数组内的每个元素都是一个字符串，有顺序之分)。

示例输入:
今天广州的天气怎样?

示例输出:
{
    "task_count": 3,
    "tasks": ["调用浏览器搜索今天的时间", "调用浏览器搜索广州的天气", "综合搜索的结果/内容调用LLM整理答案并回复用户"]
}
"""


while True:
    user_prompt = input("Query: ").strip()
    if user_prompt.lower() == "quit":
        break

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={"type": "json_object"}
    )

    split_task = SplitTask.model_validate_json(response.choices[0].message.content)

    print("拆分任务数： ", split_task.task_count)
    for idx, task in enumerate(split_task.tasks):
        print(f"{str(idx + 1).zfill(2)}. {task}")

    print("=================\n")