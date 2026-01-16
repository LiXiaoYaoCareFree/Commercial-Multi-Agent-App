import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(port=8089)


@mcp.tool()
async def calculator(expression: str) -> str:
    """一个数学计算器，用于计算传递的Python数学表达式
    Args:
        expression: 符合Python eval()函数调用的数学表达式
    Returns:
        表达式的计算结果
    """
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"result": f"数学表达式计算出错: {str(e)}"})


if __name__ == "__main__":
    mcp.run(transport="stdio")
