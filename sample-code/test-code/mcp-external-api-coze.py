import os
import dotenv
import json

from cozepy import COZE_CN_BASE_URL
import requests
from mcp.server.fastmcp import FastMCP
from sqlalchemy import true

dotenv.load_dotenv()
mcp = FastMCP(name="三方API",port=8092)


@mcp.tool()
async def call_coze_agent(query: str) -> str:
    """调用外部Agent实现对query的回答，这个Agent支持天气查询、网络内容搜索、获取当前时间等。

    Args:
        query: 用户需要提问的问题。

    Returns:
        外部Agent对query生成的最终答案。
    """
    answer = ""
    # Coze v3 API 请求体结构
    payload = {
        "bot_id": "7595598437056938036",
        "user_id": "123456789",
        "stream": true,
        "auto_save_history": true,
        "additional_messages": [
            {
                "role": "user",
                "content": query,
                "content_type": "text"
            }
        ]
    }
    
    try:
        with requests.post(
                "https://api.coze.cn/v3/chat",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.getenv('COZE_API_TOKEN')}"
                },
                json=payload,
                stream=True  # 确保开启 requests 的流式模式
        ) as resp:
            # 检查 HTTP 状态码
            if resp.status_code != 200:
                return f"调用 Coze API 失败，状态码: {resp.status_code}, 错误信息: {resp.text}"

            for line in resp.iter_lines(decode_unicode=True):
                if line:
                    if line.startswith("data:"):
                        data_str = line.lstrip("data:").strip()
                        try:
                            resp_obj = json.loads(data_str)
                            
                            # 增加类型检查，防止 resp_obj 是字符串或其他非字典类型
                            if not isinstance(resp_obj, dict):
                                # print(f"警告: 解析结果不是字典: {type(resp_obj)} - {resp_obj}")
                                continue

                            event = resp_obj.get("event")
                            
                            # 处理增量消息事件
                            if event == "conversation.message.delta":
                                # v3 接口的内容在 data.content 中
                                content = resp_obj.get("data", {}).get("content", "")
                                answer += content
                            
                            # 处理完成事件（可选，用于调试）
                            elif event == "conversation.chat.completed":
                                pass
                                
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        return f"发生异常: {str(e)}"

    return answer.strip()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
