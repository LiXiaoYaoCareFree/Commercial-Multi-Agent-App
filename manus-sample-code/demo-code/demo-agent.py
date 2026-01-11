import asyncio
import json
import os
from typing import Optional

import dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from openai import OpenAI

dotenv.load_dotenv()

class ReActAgent:
    """ReAct智能体"""

    def __init__(self):
        """构造函数，完成ReAct智能体的初始化"""
        self.session: Optional[ClientSession] = None
        self.openai = OpenAI(
            base_url="https://api.deepseek.com/v1",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
        )
        self.messages = [{
            "role": "system",
            "content": "你是一个乐于助人的AI助手。你可以调用工具来获取实时信息。请优先使用工具回答问题。回答问题尽可能简洁，不要长篇大论，如果不知道或者无法回答请直接告诉用户。"
        }]

    async def connect_to_streamable_http_server(self, url: str, headers: Optional[dict] = None):
        """连接到streamable http mcp服务器"""
        print("初始化MCP服务器")
        self._streams_context = streamablehttp_client(url=url, headers=headers)
        read_stream, write_stream, _ = await self._streams_context.__aenter__()

        self._session_context = ClientSession(read_stream, write_stream)
        self.session: ClientSession = await self._session_context.__aenter__()

        await self.session.initialize()
        print("初始化MCP服务器完成")
        print("可调用的MCP工具列表:")
        response = await self.session.list_tools()
        for tool in response.tools:
            print(f"工具[{tool.name}]: {tool.description}")

    async def process_query(self, query: str) -> str:
        """使用deepseek处理用户输入+mcp工具"""
        # 获取mcp工具并组装可用工具列表
        response = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                }
            }
            for tool in response.tools
        ]

        # 初始化用户信息
        self.messages.append({"role": "user", "content": query})

        print(f"\n[DEBUG] available_tools:\n{json.dumps(available_tools, ensure_ascii=False, indent=2)}")

        # 调用deepseek模型获取响应内容
        response = self.openai.chat.completions.create(
            model="deepseek-chat",
            messages=self.messages,
            tools=available_tools,
        )

        # 获取响应信息+工具响应
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        print(f"\n[DEBUG] tool_calls:\n{tool_calls}")

        # 判断模型是否决定调用工具
        if tool_calls:
            # 将模型回复添加到历史
            self.messages.append(response_message.model_dump())

            # 执行工具调用
            for tool_call in tool_calls:
                print("正在调用MCP工具: ", tool_call.function.name)
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # 调用mcp服务器执行工具
                result = await self.session.call_tool(tool_name, tool_args)
                print(f"\n[DEBUG] 工具[{tool_call.function.name}]调用结果: {result.model_dump()}")
                # 将工具结果添加到历史中
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(result.model_dump()),
                })

            # 再次调用模型，让它基于工具返回的结果生成最终回复内容(第二次不携带工具)
            second_response = self.openai.chat.completions.create(
                model="deepseek-chat",
                messages=self.messages,
            )

            # 添加最终消息并放回
            self.messages.append(second_response.choices[0].message.model_dump())
            return "Assistant: " + second_response.choices[0].message.content
        else:
            self.messages.append(response_message.model_dump())
            return "Assistant: " + response_message.content

    async def chat_loop(self):
        """运行循环对话(多轮对话)"""
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

    async def cleanup(self):
        """清除会话和流式上下文"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)

async def main():
    # 构建agent
    agent = ReActAgent()

    try:
        # 连接高德mcp服务
        await agent.connect_to_streamable_http_server(
            url=f"https://mcp.amap.com/mcp?key={os.getenv('GAODE_API_KEY')}",
            headers={}
        )

        # 循环对话
        await agent.chat_loop()
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
