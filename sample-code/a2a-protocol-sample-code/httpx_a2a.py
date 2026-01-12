import uuid

import httpx


async def main() -> None:
    # 1.定义a2a远程agent-card基础url地址
    base_url = "http://localhost:9999"

    # 2.创建一个httpx客户端上下文
    async with httpx.AsyncClient(timeout=600) as httpx_client:
        # 3.获取agent卡片信息
        agent_card_response = await httpx_client.get(f"{base_url}/.well-known/agent-card.json")
        agent_card_response.raise_for_status()
        print("Agent Card:", agent_card_response.json())

        # 4.提取Agent卡片信息+请求端点
        agent_card = agent_card_response.json()
        url = agent_card.get("url", "")
        if url == "":
            return

        # 5.构建发送消息请求体
        request_body = {
            "id": str(uuid.uuid4()),
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": uuid.uuid4().hex,
                    "role": "user",
                    "parts": [
                        {"kind": "text", "text": "帮我随机生成10个整数"},
                    ],
                },
            },
        }
        agent_response = await httpx_client.post(f"{url}", json=request_body)
        agent_response.raise_for_status()
        print(agent_response.json())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
