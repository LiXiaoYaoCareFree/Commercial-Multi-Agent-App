import json

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="三方API",port=8091)

# 应用配置信息
APP_ID = "4bb580ec-cb2a-47d4-a024-9787819fb7da"
LLMOPS_API = "https://llmops.shortvar.com/api/openapi/chat"
LLMOPS_API_KEY = "llmops-v1/foFOGgFEaE2jagrreR9ln5xCVUlnYMKRnG9KmrlQsh2mbmGL2bLwAt6yyaK__Oah"


@mcp.tool()
async def call_llmops_agent(query: str) -> str:
    """调用外部Agent实现对query的回答，这个Agent支持天气查询、网络内容搜索、获取当前时间等。

    Args:
        query: 用户需要提问的问题。

    Returns:
        外部Agent对query生成的最终答案。
    """
    answer = ""
    with requests.request(
            "POST",
            LLMOPS_API,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {LLMOPS_API_KEY}"
            },
            json={
                "query": query,
                "app_id": APP_ID,
                "stream": True
            }
    ) as resp:
        for line in resp.iter_lines(decode_unicode=True):
            if line:
                if line.startswith("data:"):
                    data = line.lstrip("data:").strip()
                    resp_obj = json.loads(data)
                    if resp_obj.get("event", None) == "agent_message":
                        answer += resp_obj.get("answer", "")

    return answer.strip()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
