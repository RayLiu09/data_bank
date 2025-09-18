import logging
import time

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from common.bus_exception import BusException
from common.db_base import DBBase
from config.app_holder import set_app
from config.database import engine
from config.logs import logger, setup_logging
from kb.v1.api import kb_api_router
from llm.text.v1.api import text_api_router
from security.v1.api import access_token_router
from settings import settings
from utils.ip_util import IPUtils
from vectors.v1.api import vector_api_router

# 后台任务函数
# async def run_background_task(content: str):
#     loop = asyncio.get_event_loop()
#     # 使用 loop.run_in_executor 来运行同步任务
#     await loop.run_in_executor(None, log_task, content)


setup_logging()

# 建表
logger.info("Creating database...")
# Base.metadata.create_all(bind=engine)
DBBase.metadata.create_all(engine)
logger.info("Database created successfully!")
app = FastAPI(title=settings.project_name, description="数据银行中台",
              version=settings.api_version)
set_app(app)
app.include_router(kb_api_router)
app.include_router(vector_api_router)
app.include_router(access_token_router)
app.include_router(text_api_router)

# 跨域配置
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 日志中间件
@app.middleware("http")
async def log_request(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        "Request:{method} {ip} {url} {status_code} {process_time:.2f}ms",
        method=request.method,
        ip=IPUtils.get_ip(request),
        url=request.url,
        status_code=response.status_code,
        process_time=process_time * 1000
    )
    return response


@app.exception_handler(BusException)
async def exception_callback(request: Request, exc: BusException):
    start_time = time.time()
    process_time = time.time() - start_time
    logger.error(
        "Request:{method} {ip} {url} {reason} {process_time:.2f}ms",
        method=request.method,
        ip=IPUtils.get_ip(request),
        url=request.url,
        reason=exc,
        process_time=process_time * 1000
    )
    # await run_background_task(exc)


@app.get("/")
async def root():
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return {"message": f"欢迎访问数据银行平台! now is {now}"}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.server_host, port=settings.server_port, log_level=logging.DEBUG)
