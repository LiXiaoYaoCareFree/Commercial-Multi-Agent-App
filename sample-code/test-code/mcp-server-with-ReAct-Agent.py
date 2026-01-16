import asyncio
import json
import os
from contextlib import AsyncExitStack
from typing import Optional

import dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall

dotenv.load_dotenv()

# 定义高德mcp服务基础地址
GAODE_URL = f"https://mcp.amap.com/mcp?key={os.getenv('GAODE_KEY')}"

SYSTEM_PROMPT = "你是一个强大的聊天机器人，请根据用户的提问进行回复，如果需要调用工具请直接调用，不知道请直接回复不知道"


class ReActAgent:
    def __init__(self):
        """构造函数，完成ReActAgent的初始化，涵盖客户端、生命周期、MCP会话"""
        self.model = "deepseek-chat"
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = AsyncOpenAI()
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.tools = []

    async def init_mcp(self) -> None:
        """连接到MCP服务器"""
        # 1.构建stdio本地连接参数信息
        server_params = StdioServerParameters(
            command="uv",
            args=[
                "--directory",
                "E:\\agent code\\Commercial-Multi-Agent-App\\sample-code\\test-code",
                "run",
                "mcp-server-demo-stdio.py",
            ],
            env=None,
        )

        # 2.启动标准输入输出客户端
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))

        # 3.初始化客户端
        await self.session.initialize()

        # 4.获取工具列表数据
        response = await self.session.list_tools()
        tools = response.tools
        print("工具列表:", [tool.name for tool in tools])
        self.tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            }
        } for tool in tools]

    async def process_query(self, query: str = "") -> None:
        # 将用户传递的数据添加到消息列表中
        if query != "":
            self.messages.append({"role": "user", "content": query})
        print("Assistant: ", end="", flush=True)

        # 调用deepseek发起请求
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools,
            stream=True,
        )

        # 设置变量判断是否执行工具调用、组装content、组装tool_calls
        is_tool_calls = False
        content = ""
        tool_calls_obj: dict[str, ChoiceDeltaToolCall] = {}

        async for chunk in response:
            # 叠加内容和工具调用
            chunk_content = chunk.choices[0].delta.content
            chunk_tool_calls = chunk.choices[0].delta.tool_calls

            if chunk_content:
                content += chunk_content
            if chunk_tool_calls:
                for chunk_tool_call in chunk_tool_calls:
                    if tool_calls_obj.get(chunk_tool_call.index) is None:
                        tool_calls_obj[chunk_tool_call.index] = chunk_tool_call
                    else:
                        tool_calls_obj[chunk_tool_call.index].function.arguments += chunk_tool_call.function.arguments

            # 如果是直接生成则流式打印输出的内容
            if chunk_content:
                print(chunk_content, end="", flush=True)

            # 如果还未区分出生成的内容是答案还是工具调用，则循环判断
            if is_tool_calls is False:
                if chunk_tool_calls:
                    is_tool_calls = True

        # 如果是工具调用，则需要将tool_calls_obj转换成列表
        tool_calls_json = [tool_call for tool_call in tool_calls_obj.values()]

        # 将模型第一次回复的内容添加到历史消息中
        self.messages.append({
            "role": "assistant",
            "content": content if content != "" else None,
            "tool_calls": tool_calls_json if tool_calls_json else None,
        })

        if is_tool_calls:
            # 循环调用对应的工具
            for tool_call in tool_calls_json:
                tool_name = tool_call.function.name
                tool_arguments = json.loads(tool_call.function.arguments)
                print("\nTool Call: ", tool_name)
                print("Tool Parameters: ", tool_arguments)

                # 调用工具
                try:
                    result = await self.session.call_tool(tool_name, tool_arguments)
                    result = result.content[0].text
                except Exception as e:
                    result = f"工具执行出错, Error: {str(e)}"

                print(f"Tool [{tool_name}] Result: {result}")

                # 将工具结果添加到历史消息中
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": result,
                })

            # 再次调用模型，让它基于工具调用的结果生成最终回复内容
            await self.process_query()

        print("\n")

    async def chat_loop(self):
        """运行循环对话"""
        while True:
            try:
                # 获取用户的输入
                query = input("Query: ").strip()
                if query.lower() == "quit":
                    break
                await self.process_query(query)
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """清除Agent资源"""
        await self.exit_stack.aclose()


async def main():
    # 1.创建ReAct智能体
    agent = ReActAgent()

    try:
        # 2.初始化mcp服务并开启循环聊天
        await agent.init_mcp()
        await agent.chat_loop()
    finally:
        # 3.清空Agent资源
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
