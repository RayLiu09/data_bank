from contextvars import ContextVar

from starlette.background import BackgroundTasks

CTX_USER_ID: ContextVar[int] = ContextVar("user_id", default=0)
CTX_BG_TASKS: ContextVar[BackgroundTasks] = ContextVar("bg_task", default=None)
