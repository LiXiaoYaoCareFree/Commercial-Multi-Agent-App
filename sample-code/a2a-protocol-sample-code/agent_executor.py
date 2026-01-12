from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from openai import AsyncOpenAI


class DeepSeekAgent:
    @classmethod
    async def invoke(cls, query: str) -> str:
        client = AsyncOpenAI(
            base_url="https://api.deepseek.com",
            api_key="sk-088bd7c594cf415e90f0139e6f9cf908"
        )
        response = await client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[{"role": "user", "content": query}]
        )
        return f"推理内容: {response.choices[0].message.reasoning_content}\n\n答案: {response.choices[0].message.content}"


class DeepSeekAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = DeepSeekAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = context.message.parts[0].root.text
        answer = await self.agent.invoke(query)
        await event_queue.enqueue_event(new_agent_text_message(answer))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("暂不支持取消")
