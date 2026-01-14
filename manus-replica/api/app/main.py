from fastapi import FastAPI
from core.config import get_settings

# 1.加载配置信息
settings = get_settings()

app = FastAPI()