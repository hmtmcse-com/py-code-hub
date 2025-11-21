from apscheduler.schedulers.asyncio import AsyncIOScheduler


class MWebScheduler:
    _scheduler = None

    def __init__(self):
        self._scheduler = AsyncIOScheduler()

    def start(self, paused=False):
        self._scheduler.start()

    def add_interval_job(self, func, job_id: str, hours=0, minutes=0, seconds=0, args=None, kwargs=None):
        job = self._scheduler.add_job(
            func=func,
            trigger="interval",
            id=job_id,
            replace_existing=True,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            args=args or [],
            kwargs=kwargs or {},
        )
        print(f"MWeb Scheduler Added interval job: {job_id}")
        return job


mweb_scheduler = MWebScheduler()
