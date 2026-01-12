import os
import requests
import dotenv

dotenv.load_dotenv()

response = requests.request(
    "POST",
    "https://api.deepseek.com/chat/completions",
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"
    },
    json={
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "你好，你是?"}
        ],
        "stream": False
    }
)
print(response)
print(response.json())