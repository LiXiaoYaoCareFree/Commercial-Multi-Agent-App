import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentSkill, AgentCard, AgentCapabilities

from agent_executor import DeepSeekAgentExecutor

if __name__ == "__main__":
    # 1.定义技能
    skill = AgentSkill(
        id="calculator",
        name="计算器",
        description="支持计算各种复杂数学公式",
        tags=["计算器"],
        examples=["445*34", "211/34.2+12"]
    )

    # 2.定义Agent卡片
    agent_card = AgentCard(
        name="DeepSeek智能体",
        description="这是一个可以调用Deepseek模型进行深度思考的智能体，在需要深度思考时可以使用",
        url="http://localhost:9999",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
        supports_authenticated_extended_card=False,
    )

    # 3.使用a2a默认的请求处理器(jsonrpc)
    request_handler = DefaultRequestHandler(
        agent_executor=DeepSeekAgentExecutor(),
        task_store=InMemoryTaskStore()
    )

    # 4.创建or启动一个a2a服务器
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    uvicorn.run(server.build(), host="127.0.0.1", port=9999)
