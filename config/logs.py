import logging
import os
from datetime import datetime

from settings import settings

logger: logging.Logger = logging.getLogger("data_bank") # name must be the root package name


def _basic_config() -> None:
    # e.g. [2023-10-05 14:12:26 - botok._base_client:818 - DEBUG] HTTP Request: POST http://127.0.0.1:4010/foo/bar
    # "200 OK"
    logging.basicConfig(
        filename=os.path.join(settings.log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"),
        format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ch = logging.StreamHandler()
    fh = logging.handlers.RotatingFileHandler(os.path.join(settings.log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"), mode="a", maxBytes=5 * 1024 * 1024, backupCount=7, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s - %(module)s - %(funcName)s - line:%(lineno)d - %(levelname)s - %(message)s"
    )

    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)  # 将日志输出至屏幕
    logger.addHandler(fh)  # 将日志输出至文件


def setup_logging() -> None:
    env = settings.log_level.upper()
    print(f"Logging level: {env}")
    if env == "DEBUG":
        _basic_config()
        logger.setLevel(logging.DEBUG)
    elif env == "INFO":
        _basic_config()
        logger.setLevel(logging.INFO)
    elif env == "WARNING":
        _basic_config()
        logger.setLevel(logging.WARNING)
