import asyncio

from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client


async def main() -> None:
    # 1.初始化stdio的服务器连接参数
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

    # 2.创建标准输入输出客户端
    async with stdio_client(server_params) as transport:
        # 3.获取写入和写出流
        stdio, write = transport

        # 4.创建客户端会话上下文
        async with ClientSession(stdio, write) as session:
            # 5.初始化mcp服务器连接
            await session.initialize()

            # 6.获取工具列表信息
            list_tools_response = await session.list_tools()
            tools = list_tools_response.tools
            print("工具列表:", [tool.name for tool in tools])

            # 7.调用指定的工具
            call_tool_response = await session.call_tool("calculator", {"expression": "564*34+12.4/455**2"})
            print("工具结果:", call_tool_response)


if __name__ == "__main__":
    asyncio.run(main())
