import json
import os

import dotenv
import requests
from openai import OpenAI
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall

dotenv.load_dotenv()

# 定义高德mcp服务基础地址
GAODE_URL = f"https://mcp.amap.com/mcp?key={os.getenv('GAODE_KEY')}"

SYSTEM_PROMPT = "你是一个强大的聊天机器人，请根据用户的提问进行回复，如果需要调用工具请直接调用，不知道请直接回复不知道"


class ReActAgent:
    def __init__(self):
        self.client = OpenAI()
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.model = "deepseek-chat"
        self.tools = []
        self.headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        }
        self.init_gaode_mcp()

    def init_gaode_mcp(self) -> None:
        """初始化高德mcp服务"""
        # 1.调用高德mcp服务获取工具列表信息
        tools_list_response = requests.post(GAODE_URL, headers=self.headers, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        })
        tools_list_response.raise_for_status()
        tools_list_data = tools_list_response.json()

        # 2.组装可用工具列表信息
        self.tools = [{
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["inputSchema"],
            }
        } for tool in tools_list_data["result"]["tools"]]

    def call_gaode_mcp(self, name: str, arguments: dict) -> str:
        """调用高德mcp服务"""
        # 1.发起请求调用高德mcp服务
        tools_call_response = requests.post(GAODE_URL, headers=self.headers, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments,
            }
        })
        tools_call_response.raise_for_status()
        tools_call_data = tools_call_response.json()

        # 2.返回响应内容
        return tools_call_data["result"]["content"][0]["text"]

    def process_query(self, query: str = "") -> None:
        # 将用户传递的数据添加到消息列表中
        if query != "":
            self.messages.append({"role": "user", "content": query})
        print("Assistant: ", end="", flush=True)

        # 调用deepseek发起请求
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools,
            stream=True,
        )

        # 设置变量判断是否执行工具调用、组装content、组装tool_calls
        is_tool_calls = False
        content = ""
        tool_calls_obj: dict[str, ChoiceDeltaToolCall] = {}

        for chunk in response:
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
                    result = self.call_gaode_mcp(tool_name, tool_arguments)
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
            self.process_query()

        print("\n")

    def chat_loop(self):
        """运行循环对话"""
        while True:
            try:
                # 获取用户的输入
                query = input("Query: ").strip()
                if query.lower() == "quit":
                    break
                self.process_query(query)
            except Exception as e:
                print(f"\nError: {str(e)}")


if __name__ == "__main__":
    ReActAgent().chat_loop()
