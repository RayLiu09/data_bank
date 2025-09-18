import logging
import threading
from typing import Callable

logger = logging.getLogger(__name__)


def background_task(task_name: str, task_func: Callable, *args, **kwargs):
    """
    Define a background thread for task execution.

    Parameters:
        task_name(str): The task_name of the task
        task_func(Callable): The function to be executed
        *args, **kwargs: Parameters for the task function
    """

    def run_task():
        """
        Inner function, execute actually in background thread.
        """
        logger.info(f"Starting task: {task_name}")
        task_func(*args, **kwargs)
        logger.info(f"Task completed: {task_name}")

    # Create and start a new thread.
    thread = threading.Thread(target=run_task, name=task_name)
    thread.start()

    # Return the thread object.
    return thread
