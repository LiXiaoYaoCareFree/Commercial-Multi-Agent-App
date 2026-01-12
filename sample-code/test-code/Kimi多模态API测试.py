import base64
import os

import dotenv
import requests

dotenv.load_dotenv()

image_path = "../resources/广州塔.jpeg"

with open(image_path, "rb") as f:
    image_data = f.read()

# 使用python标准的base64.b64encode函数将图片编码成base64字符串
image_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"

response = requests.request(
    "POST",
    "https://api.moonshot.cn/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {os.getenv('MOONSHOT_API_KEY')}"
    },
    json={
        "model": "moonshot-v1-8k-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请描述下这张图片，这张图片所在位置是哪里呢?"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        "stream": False
    }
)

print(response.json())