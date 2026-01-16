import subprocess

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Bash工具", port=8088)


@mcp.tool()
async def bash(command: str) -> dict:
    """传递command命令，在Windows下执行CMD命令。

    Args:
        command: 需要执行的command命令

    Returns:
        返回命令的执行状态、结果、错误信息
    """
    result = subprocess.run(
        command,
        shell=True,  # 让命令行通过cmd执行
        capture_output=True,  # 捕获输出
        text=True,  # 输出解码为字符串
    )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
