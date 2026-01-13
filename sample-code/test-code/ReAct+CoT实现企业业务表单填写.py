import json
from datetime import date
from typing import Literal

import dotenv
from openai import OpenAI
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall
from pydantic import BaseModel, Field

dotenv.load_dotenv()

"""
课后挑战:
1.为我们的报销政策增加一条新规则：“如果总金额超过2000元，且员工职级不是‘总监’，则报销级别不能是‘VIP’。”
2.只需要修改你的System Prompt，看看Agent能否在第二次思考时，正确地应用这条新规则，并调整最终的报销级别。
"""


class GetEmployeeInfoInput(BaseModel):
    employee_id: str = Field(..., description="需要查询的员工工号")


class SubmitReimbursementInput(BaseModel):
    employee_id: str = Field(..., description="员工工号")
    employee_name: str = Field(..., description="员工姓名")
    submission_date: date = Field(..., description="提交日期")
    trip_start_date: date = Field(..., description="出差开始日期")
    trip_end_date: date = Field(..., description="出差结束日期")
    destination: str = Field(..., description="出差目的地")
    transportation_cost: float = Field(..., description="交通费用")
    accommodation_cost: float = Field(..., description="住宿费用")
    meal_cost: float = Field(..., description="餐饮费用")
    total_cost: float = Field(..., description="总报销金额")
    reimbursement_level: Literal['标准', '高级', 'VIP'] = Field(..., description="报销级别")


class CalculatorInput(BaseModel):
    expression: str = Field(..., description="需要计算的数学表达式，例如：'123+456+789'")


def get_employee_info(employee_id: str) -> str:
    """根据员工工号查询员工信息，包括姓名和职级"""
    print(f"--- 正在查询工号 {employee_id} 的信息... ---")
    if employee_id == "E12345":
        return json.dumps({"name": "张三", "level": "经理"})
    return json.dumps({"error": "该员工不存在"})


def submit_reimbursement(**kwargs) -> str:
    """提交已填写的报销表单。"""
    print("--- 已提交报销信息 ---")
    print(kwargs)
    return json.dumps({"status": "success", "message": "报销单提交成功"})


def calculator(expression: str) -> str:
    """一个简单的计算器，可以执行数学表达式"""
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": f"无效表达式, 错误信息: {str(e)}"})


SYSTEM_PROMPT = """你是一个智能企业报销助手。你的任务是根据用户的请求和公司的报销政策，帮助员工填写并提交差旅报销单。

你必须遵循以下思考和行动的循环模式（ReAct）：

1. **思考(Thought)**
   - **回顾目标**：当前我的最终目标是什么？(例如：填写并提交一份完整的报销单)
   - **分析现状**：我已经获取了哪些信息？还缺少哪些信息？
   - **运用CoT(Chain-of-Thought)**：仔细阅读并一步一步地应用报销政策。例如，计算总金额、判断报销级别等。把你的计算和推理过程写在思考中。
   - **规划下一步**：接下来我应该做什么？是查询信息，还是计算，还是准备提交？
   
2. **行动(Action)**
   - 根据你的思考，决定是调用工具还是向用户提问。
   - 你可用的工具有：`get_employee_info`、`submit_reimbursement`、`calculator`。
   - 如果所有信息都已集齐并计算完毕，你的最后一步行动应该是调用 `submit_reimbursement` 工具。
   - 在调用工具之前也请输出思考过程，不要直接调用，避免造成高延迟体验。

请开始工作。
"""


class ReActAgent:
    def __init__(self):
        self.client = OpenAI()
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.model = "deepseek-chat"
        self.available_tools = {
            submit_reimbursement.__name__: {"tool": submit_reimbursement, "input": SubmitReimbursementInput},
            get_employee_info.__name__: {"tool": get_employee_info, "input": GetEmployeeInfoInput},
            calculator.__name__: {"tool": calculator, "input": CalculatorInput},
        }
        self.tools = [{
            "type": "function",
            "function": {
                "name": tool["tool"].__name__,
                "description": tool["tool"].__doc__,
                "parameters": tool["input"].model_json_schema(),
            }
        } for tool in self.available_tools.values()]

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
                tool_arguments = tool_call.function.arguments
                print("\nTool Call: ", tool_name)
                print("Tool Parameters: ", tool_arguments)
                function_to_call = self.available_tools[tool_name]["tool"]

                # 调用工具
                try:
                    inputs = self.available_tools[tool_name]["input"].model_validate_json(tool_arguments)
                    result = function_to_call(**inputs.model_dump())
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
