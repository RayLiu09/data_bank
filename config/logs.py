import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from settings import settings

logger: logging.Logger = logging.getLogger("data_bank")  # name must be the root package name


def _basic_config(level: int = logging.DEBUG) -> None:
    # 创建 formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(module)s - %(funcName)s - line:%(lineno)d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 控制台处理器
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)

    # 文件大小轮转处理器
    fh = RotatingFileHandler(
        os.path.join(settings.log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"),
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=7,
        encoding="utf-8"
    )
    fh.setLevel(level)
    fh.setFormatter(formatter)

    # 按日期轮转的处理器（保留最近30天的日志）
    dh = TimedRotatingFileHandler(
        os.path.join(settings.log_dir, "data_bank.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    dh.setLevel(level)
    dh.setFormatter(formatter)

    # 清除现有处理器并添加新的处理器到 logger
    logger.handlers.clear()
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.addHandler(dh)

    # 设置日志级别
    logger.setLevel(level)


def setup_logging() -> None:
    env = settings.log_level.upper()
    print(f"Logging level: {env}")
    if env == "DEBUG":
        _basic_config(logging.DEBUG)
    elif env == "INFO":
        _basic_config(logging.INFO)
    elif env == "WARNING":
        _basic_config(logging.WARNING)
    else:
        _basic_config(logging.INFO)  # 默认 INFO 级别
