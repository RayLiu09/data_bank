import logging

import aioredis

from settings import settings

logger = logging.getLogger(__name__)


class RedisUtil:
    """
    Redis相关方法
    """

    @classmethod
    async def create_redis_pool(cls) -> aioredis.Redis:
        """
        应用启动时初始化redis连接
        :return: Redis连接对象
        """
        logger.info("开始连接redis...")
        redis = await aioredis.from_url(
            url=f"redis://{settings.redis_url}",
            port=settings.redis_port,
            username=settings.redis_username,
            password=settings.redis_password,
            db=settings.redis_db,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("redis连接成功")
        return redis

    @classmethod
    async def close_redis_pool(cls, app):
        """
        应用关闭时关闭redis连接
        :param app: fastapi对象
        :return:
        """
        await app.state.redis.close()
        logger.info("关闭redis连接成功")
