import json
import os

import dotenv
from openai import OpenAI

dotenv.load_dotenv()

def calculator(expression: str) -> str:
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": f"无效表达式，错误信息：{str(e)}"})


class ReActAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com"
        )
        self.messages = [
            {
                "role": "system",
                "content": "你是一个强大的聊天机器人，请根据用户的提问进行答复，如果需要调用工具请直接调用，不知道请直接回复不清楚",
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

    def process_query(self, query: str) -> str:
        """使用deepseek处理用户输出"""
        self.messages.append({"role": "user", "content": query})

        # 调用deepseek发起请求
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools,
        )

        # 获取响应消息+工具响应
        response_message = response.choices[0].message
        print("\n获取响应消息+工具响应", response_message)
        tool_calls = response_message.tool_calls
        print("\ntool_calls: ", tool_calls.__str__())

        # 将模型第一次回复添加到历史消息中
        self.messages.append(response_message.model_dump())
        print("\nself.messages: ", self.messages)
        
        print("\ntool_calls: ", tool_calls.__str__())

        # 判断是否执行工具调用
        if tool_calls:

            # 循环执行工具调用
            for tool_call in tool_calls:
                print("Tool Call: ", tool_call.function.name)
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                function_to_call = self.available_tools[tool_name]
                print("\ntool_name: " ,tool_name, "\ntool_args " , tool_args, "\nfunction_to_call", function_to_call.__str__())

                #调用工具
                result = function_to_call(**tool_args)
                print(f"Tool [{tool_name}] result: {result}")

                # 将工具结果添加到历史信息中
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
                )

                self.messages.append(second_response.choices[0].message.model_dump())
                return "Assistant: " + second_response.choices[0].message.content
            else:
                return "Assistant: " + response_message.content

    def chat_loop(self):
        """运行循环对话"""
        while True:
            try:
                # 获取用户的输入
                query = input("\nQuery: ").strip()
                if query.lower() == "quit":
                    break
                print(self.process_query(query))
            except Exception as e:
                print(f"\nError: {str(e)}")

if __name__ == "__main__":
    ReActAgent().chat_loop()