import json
import traceback

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

from config.logs import logger


class ConfigLoader:
    """配置加载器，支持动态文件监控"""
    def __init__(self):
        self.app_path = "module_aigc/core/config/application_setting.json"
        self.api_path = "module_aigc/core/config/api_config.json"
        self.app_data = {}
        self.api_data = {}
        self.observer = None
        self.lock = threading.Lock()  # 线程安全

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.app_path, "r", encoding="utf-8") as file:
                with self.lock:  # 确保线程安全
                    self.app_data = json.load(file)
            with open(self.api_path, "r", encoding="utf-8") as file:
                with self.lock:  # 确保线程安全
                    self.api_data = json.load(file)
            logger.info("配置文件加载成功")
        except Exception as e:
            error_details = traceback.format_exc()
            logger.info("加载配置文件失败", error_details)

    def start_watchdog(self):
        """启动文件监控"""
        logger.info("启动文件监控")
        event_handler = self.ConfigChangeHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, path="module_aigc/core/config/", recursive=False)
        self.observer.start()

    def stop_watchdog(self):
        """停止文件监控"""
        logger.info("停止文件监控")
        if self.observer:
            self.observer.stop()
            self.observer.join()

    class ConfigChangeHandler(FileSystemEventHandler):
        """文件变更事件处理"""
        def __init__(self, loader):
            self.loader = loader

        def on_modified(self, event):
            if event.src_path.endswith(".json"):
                logger.info(f"检测到配置文件修改: {event.src_path}")
                self.loader.load_config()

    def get_api_config(self):
        """获取当前配置"""
        with self.lock:  # 确保线程安全
            return self.api_data

    def get_app_config(self):
        """获取当前配置"""
        with self.lock:  # 确保线程安全
            return self.app_data


config_loader = ConfigLoader()
