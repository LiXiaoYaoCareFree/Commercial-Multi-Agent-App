import logging

from fastapi import FastAPI



from app.infrastructure.logging import setup_logging
from core.config import get_settings

# 1.加载配置信息
settings = get_settings()

# 2.初始化日志系统
setup_logging()
logger = logging.getLogger()


app = FastAPI()