import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCard,
    AgentSkill,
    AgentCapabilities,
)

from agent_executor import WeatherAgentExecutor


def main(host: str, port: int):
    """天气智能体运行主程序"""
    # 定义Agent支持的能力
    capabilities = AgentCapabilities(streaming=True)

    # 定义Agent支持的两个技能，涵盖天气预报+空气质量报告
    forecast_skill = AgentSkill(
        id='天气预告',
        name='天气预告',
        description='给出某地的天气预告',
        tags=['天气', '预告'],
        examples=['给我广州未来 7 天的天气预告'],
    )
    air_quality_skill = AgentSkill(
        id='空气质量报告',
        name='空气质量报告',
        description='给出某地当前时间的空气质量报告，不做预告',
        tags=['空气', '质量'],
        examples=['给我广州当前的空气质量报告'],
    )

    # 定义Agent卡片，告知外部该Agent的作用
    agent_card = AgentCard(
        name='天气 Agent',
        description='这是一个天气Agent，提供天气相关的查询功能',
        url=f'http://{host}:{port}',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=capabilities,
        skills=[forecast_skill, air_quality_skill],
    )

    # 创建请求处理器&服务
    request_handler = DefaultRequestHandler(
        agent_executor=WeatherAgentExecutor(),  # Agent执行者
        task_store=InMemoryTaskStore(),  # 任务存储桶
    )
    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    # 使用uvicorn运行服务
    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main("127.0.0.1", 8888)
