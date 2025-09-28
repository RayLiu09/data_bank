from contextvars import ContextVar

from starlette.background import BackgroundTasks

CTX_BG_TASKS: ContextVar[BackgroundTasks] = ContextVar("bg_task", default=None)
