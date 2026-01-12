import uuid
from typing import Any

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import SendMessageRequest, MessageSendParams


async def main() -> None:
    # 1.定义a2a基础url地址
    base_url = "http://localhost:9999"

    # 2.创建一个httpx客户端上下文
    async with httpx.AsyncClient(timeout=600) as httpx_client:
        # 3.创建一个Agent卡片解析器
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )
        card = await resolver.get_agent_card()
        print("Agent Card:", card)

        # 4.创建一个A2A客户端
        client = A2AClient(
            httpx_client=httpx_client,
            agent_card=card,
        )

        # 5.构建发送消息载体
        send_message_payload: dict[str, Any] = {
            "message": {
                "messageId": uuid.uuid4().hex,
                "role": "user",
                "parts": [
                    {"kind": "text", "text": "帮我随机生成10个整数"}
                ]
            }
        }
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(**send_message_payload),
        )
        response = await client.send_message(request)

        # 6.打印响应内容
        print(response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
