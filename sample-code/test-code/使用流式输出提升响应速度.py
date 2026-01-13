import json

import dotenv
from openai import OpenAI
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall

dotenv.load_dotenv()


def calculator(expression: str) -> str:
    """一个简单的计算器，可以执行数学表达式"""
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": f"无效表达式, 错误信息: {str(e)}"})


class ReActAgent:
    def __init__(self):
        self.client = OpenAI()
        self.messages = [
            {
                "role": "system",
                "content": "你是一个强大的聊天机器人，请根据用户的提问进行答复，如果需要调用工具请直接调用，不知道请直接回复不清楚"
            }
        ]
        self.model = "deepseek-chat"
        self.available_tools = {"calculator": calculator}
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": "一个可以计算数学表达式的计算器",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "需要计算的数学表达式，例如：'123+456+789'"
                            }
                        },
                        "required": ["expression"]
                    }
                }
            }
        ]

    def process_query(self, query: str) -> None:
        # 将用户传递的数据添加到消息列表中
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
                tool_args = json.loads(tool_call.function.arguments)
                print("\nTool Call: ", tool_name)
                print("Tool Parameters: ", tool_args)
                function_to_call = self.available_tools[tool_name]

                # 调用工具
                result = function_to_call(**tool_args)
                print(f"Tool [{tool_name}] Result: {result}")

                # 将工具结果添加到历史消息中
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": result,
                })

            # 再次调用模型，让它基于工具调用的结果生成最终回复内容
            second_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="none",
                stream=True,
            )
            print("Assistant: ", end="", flush=True)
            for chunk in second_response:
                print(chunk.choices[0].delta.content, end="", flush=True)

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
