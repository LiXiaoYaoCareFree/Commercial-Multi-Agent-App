import logging
import sys

from core.config import get_settings


def setup_logging():
    """配置manus-replica项目的日志系统，涵盖日志等级、输出格式、输出渠道等"""
    # 1.获取项目配置
    settings = get_settings()

    # 2.获取根日志处理器
    root_logger = logging.getLogger()

    # 3.设置根日志处理器等级
    log_level = getattr(logging, settings.log_level)
    root_logger.setLevel(log_level)

    # 4.日志输出格式定义
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 5.创建控制台日志输出处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # 6.将控制台日志处理器添加到根日志处理器中
    root_logger.addHandler(console_handler)

    root_logger.info("日志系统初始化完成")