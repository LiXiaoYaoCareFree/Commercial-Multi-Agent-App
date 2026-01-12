import dotenv
from openai import OpenAI
import os

dotenv.load_dotenv()

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[{"role": "user", "content": "你好，你是?"}],
        stream=False
    )

# response = client.chat.completions.create(
#     model="deepseek-chat",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant"},
#         {"role": "user", "content": "Hello"},
#     ],
#     stream=False
# )

print("推理内容:", response.choices[0].message.reasoning_content)
print("最终答案:", response.choices[0].message.content)
