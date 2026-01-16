import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main() -> None:
    # 1.百度AI搜索配置信息
    baidu_ai_search_api = "https://qianfan.baidubce.com/v2/ai_search/mcp"
    headers = {"Authorization": "Bearer bce-v3/ALTAK-TjB9iN1wdahfRhBhBWx5k/1b1103fd48590a808822faf6b0dc0cbce6a17a7f"}

    # 2.创建异步上下文管理器
    exit_stack = AsyncExitStack()

    try:
        # 3.创建连接客户端
        transport = await exit_stack.enter_async_context(streamablehttp_client(
            url=baidu_ai_search_api,
            headers=headers,
        ))

        # 4.获取读取、写入流
        read_stream, write_stream, _ = transport

        # 5.创建客户端会话
        session: ClientSession = await exit_stack.enter_async_context(ClientSession(read_stream, write_stream))

        # 6.初始化会话
        await session.initialize()

        # 7.获取工具列表并输出
        list_tools_result = await session.list_tools()
        print(list_tools_result)

        # 8.调用指定工具实现百度搜索
        call_tool_result = await session.call_tool("chatCompletions", {
            "query": "2025年广州马拉松"
        })
        print("工具调用结果:", call_tool_result.content[0].text)
    finally:
        await exit_stack.aclose()


if __name__ == "__main__":
    asyncio.run(main())
