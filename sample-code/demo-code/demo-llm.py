import asyncio
import os

import dotenv
from openai import OpenAI

dotenv.load_dotenv()

class DeepSeekClient:
    """DeepSeek客户端"""

    def __init__(self):
        """构造函数，完成DeepSeek客户端的初始化"""
        self.openai = OpenAI(
            base_url="https://api.deepseek.com/v1",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
        )

    async def process_query(self, query: str) -> str:
        """使用deepseek处理用户输入+mcp工具"""
        # 初始化用户信息
        messages = [{"role": "user", "content": query}]

        # 调用deepseek模型获取响应内容
        response = self.openai.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
        )

        # 获取响应消息+工具响应
        response_message = response.choices[0].message

        # 返回应用响应
        return "Assistant: " + response_message.content

    async def chat_loop(self):
        """运行循环对话"""
        while True:
            try:
                # 获取用户的输入，如果输入quit则退出循环
                query = input("\nQuery: ").strip()
                if query.lower() == "quit":
                    break
                # 调用process_query获取响应内容并打印
                response = await self.process_query(query)
                print(response)
            except Exception as e:
                print(f"\nError: {str(e)}")
async def main():
    client = DeepSeekClient()

    await client.chat_loop()

if __name__ == "__main__":
    asyncio.run(main())