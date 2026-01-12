import os

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (Part, Task, TextPart, UnsupportedOperationError)
from a2a.utils import (completed_task, new_artifact)
from a2a.utils.errors import ServerError

from deepseek_react_agent import ReActAgent


class WeatherAgentExecutor(AgentExecutor):

    async def execute(
            self,
            context: RequestContext,
            event_queue: EventQueue,

    ) -> None:
        # 1.获取传递给用户的消息
        text = context.message.parts[0].root.text

        # 2.创建agent
        agent = ReActAgent()
        try:
            # 3.连接高德MCP服务
            await agent.connect_to_streamable_http_server(
                url=f"https://mcp.amap.com/mcp?key={os.getenv('GAODE_API_KEY')}",
                headers={}
            )

            # 4.调用agent获取响应
            response = await agent.process_query(text)

            # 5.将agent响应内容推送到事件队列中
            await event_queue.enqueue_event(
                completed_task(
                    context.task_id,
                    context.context_id,
                    [new_artifact(parts=[Part(root=TextPart(text=response))], name="天气查询结果")],
                    [context.message],
                )
            )
        finally:
            await agent.cleanup()

    async def cancel(
            self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())
