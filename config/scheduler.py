import json
from datetime import datetime, timedelta

from apscheduler.events import EVENT_ALL
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from sqlalchemy import text

from config.database import SessionLocal
from module_admin.dao.job_dao import Session
# 重写Cron定时
from module_admin.entity.vo.job_vo import JobLogModel
from module_admin.entity.vo.report_vo import ReportCreate
from module_admin.service.job_log_service import JobLogService
from module_admin.service.job_service import JobService
from module_admin.service.report_service import ReportService
from module_admin.service.requests_service import RequestsService


class MyCronTrigger(CronTrigger):
    @classmethod
    def from_crontab(cls, expr, timezone=None):
        values = expr.split()
        if len(values) != 7:
            raise ValueError('Wrong number of fields; got {}, expected 7'.format(len(values)))

        return cls(second=values[0], minute=values[1], hour=values[2], day=values[3], month=values[4],
                   day_of_week=values[5], year=values[6], timezone=timezone)


job_stores = {
    'default': MemoryJobStore()
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instance': 1
}
scheduler = BackgroundScheduler()
scheduler.configure(jobstores=job_stores, executors=executors, job_defaults=job_defaults)


class SchedulerUtil:
    """
    定时任务相关方法
    """

    @classmethod
    async def init_system_scheduler(cls, result_db: Session = SessionLocal()):
        """
        应用启动时初始化定时任务
        :return:
        """
        logger.info("开始启动定时任务...")
        scheduler.start()
        job_list = JobService.get_job_list_for_scheduler(result_db)
        for item in job_list:
            query_job = cls.get_scheduler_job(job_id=str(item.job_id))
            if query_job:
                cls.remove_scheduler_job(job_id=str(item.job_id))
            cls.add_scheduler_job(item)
        result_db.close()
        scheduler.add_listener(cls.scheduler_event_listener, EVENT_ALL)
        # 判断今天的数据有无生成，如果没有则生成，有则忽略。
        cls.init_data()
        logger.info("系统初始定时任务加载成功")

    @classmethod
    async def close_system_scheduler(cls):
        """
        应用关闭时关闭定时任务
        :return:
        """
        scheduler.shutdown()
        logger.info("关闭定时任务成功")

    @classmethod
    def get_scheduler_job(cls, job_id):
        """
        根据任务id获取任务对象
        :param job_id: 任务id
        :return: 任务对象
        """
        query_job = scheduler.get_job(job_id=str(job_id))

        return query_job

    @classmethod
    def add_scheduler_job(cls, job_info):
        """
        根据输入的任务对象信息添加任务
        :param job_info: 任务对象信息
        :return:
        """
        scheduler.add_job(
            func=eval(job_info.invoke_target),
            trigger=MyCronTrigger.from_crontab(job_info.cron_expression),
            args=job_info.job_args.split(',') if job_info.job_args else None,
            kwargs=json.loads(job_info.job_kwargs) if job_info.job_kwargs else None,
            id=str(job_info.job_id),
            name=job_info.job_name,
            misfire_grace_time=1000000000000 if job_info.misfire_policy == '3' else None,
            coalesce=True if job_info.misfire_policy == '2' else False,
            max_instances=3 if job_info.concurrent == '0' else 1,
            jobstore=job_info.job_group,
            executor=job_info.job_executor
        )

    @classmethod
    def execute_scheduler_job_once(cls, job_info):
        """
        根据输入的任务对象执行一次任务
        :param job_info: 任务对象信息
        :return:
        """
        scheduler.add_job(
            func=eval(job_info.invoke_target),
            trigger='date',
            run_date=datetime.now() + timedelta(seconds=1),
            args=job_info.job_args.split(',') if job_info.job_args else None,
            kwargs=json.loads(job_info.job_kwargs) if job_info.job_kwargs else None,
            id=str(job_info.job_id),
            name=job_info.job_name,
            misfire_grace_time=1000000000000 if job_info.misfire_policy == '3' else None,
            coalesce=True if job_info.misfire_policy == '2' else False,
            max_instances=3 if job_info.concurrent == '0' else 1,
            jobstore=job_info.job_group,
            executor=job_info.job_executor
        )

    @classmethod
    def remove_scheduler_job(cls, job_id):
        """
        根据任务id移除任务
        :param job_id: 任务id
        :return:
        """
        scheduler.remove_job(job_id=str(job_id))

    @classmethod
    def scheduler_event_listener(cls, event):
        # 获取事件类型和任务ID
        event_type = event.__class__.__name__
        # 获取任务执行异常信息
        status = '0'
        exception_info = ''
        if event_type == 'JobExecutionEvent' and event.exception:
            exception_info = str(event.exception)
            status = '1'
        job_id = event.job_id
        query_job = cls.get_scheduler_job(job_id=job_id)
        if query_job:
            query_job_info = query_job.__getstate__()
            # 获取任务名称
            job_name = query_job_info.get('name')
            # 获取任务组名
            job_group = query_job._jobstore_alias
            # 获取任务执行器
            job_executor = query_job_info.get('executor')
            # 获取调用目标字符串
            invoke_target = query_job_info.get('func')
            # 获取调用函数位置参数
            job_args = ','.join(query_job_info.get('args'))
            # 获取调用函数关键字参数
            job_kwargs = json.dumps(query_job_info.get('kwargs'))
            # 获取任务触发器
            job_trigger = str(query_job_info.get('trigger'))
            # 构造日志消息
            job_message = f"事件类型: {event_type}, 任务ID: {job_id}, 任务名称: {job_name}, 执行于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            job_log = dict(
                job_log_id=0,
                job_name=job_name,
                job_group=job_group,
                job_executor=job_executor,
                invoke_target=invoke_target,
                job_args=job_args,
                job_kwargs=job_kwargs,
                job_trigger=job_trigger,
                job_message=job_message,
                status=status,
                exception_info=exception_info,
                create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            session = SessionLocal()
            JobLogService.add_job_log(session, JobLogModel(**job_log))
            session.close()

    @staticmethod
    def init_data():
        db = SessionLocal()
        kwargs = []
        now = datetime.now() - timedelta(days=1)
        date = now.strftime("%Y-%m-%d")
        kwargs.append(text("date >= '" + date + " 00:00:00'"))
        kwargs.append(text("date <= '" + date + " 23:59:59'"))
        report_result = ReportService.get_reports(db, 1, 100, *kwargs)
        if report_result is None:
            kwargs.clear()
            kwargs.append(text("create_time >= '" + date + " 00:00:00'"))
            kwargs.append(text("create_time <= '" + date + " 23:59:59'"))
            total_request = RequestsService.get_requests_count(db, *kwargs)
            report = ReportCreate(date=now, content='{"requests":' + str(total_request) + ',"undoneTask":0}', type=0, createTime=datetime.now())
            ReportService.create_report(db=db, report=report)
        db.close()
