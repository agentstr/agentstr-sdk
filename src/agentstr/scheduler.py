"""A simple, opinionated scheduler for running asynchronous jobs using APScheduler."""
import asyncio
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.memory import MemoryJobStore


def job_func(func, *args, **kwargs):
    """A wrapper to run an async function in a synchronous context."""
    def wrapper():
        asyncio.run(func(*args, **kwargs))
    return wrapper


class Scheduler:
    """A wrapper around `apscheduler.schedulers.blocking.BlockingScheduler` to simplify adding and running async jobs."""
    def __init__(self):
        """Initializes the scheduler with a memory-based job store."""
        self.scheduler = BlockingScheduler()
        self.scheduler.add_jobstore(MemoryJobStore(), 'memory')

    def add_interval_job(self, func, seconds, *args, **kwargs):
        """Adds a job to be run at a fixed interval.

        Args:
            func: The asynchronous function to run.
            seconds: The interval in seconds.
        """
        self.scheduler.add_job(job_func(func, *args, **kwargs), IntervalTrigger(seconds=seconds))

    def add_cron_job(self, func, cron_tab: str, *args, **kwargs):
        """Adds a job to be run on a cron schedule.

        Args:
            func: The asynchronous function to run.
            cron_tab: The cron tab string.
        """
        self.scheduler.add_job(job_func(func, *args, **kwargs), CronTrigger.from_crontab(cron_tab))

    def add_job(self, func, trigger, *args, **kwargs):
        """Adds a job with a custom trigger.

        Args:
            func: The asynchronous function to run.
            trigger: An APScheduler trigger instance.
        """
        self.scheduler.add_job(job_func(func, *args, **kwargs), trigger)

    def start(self):
        """Starts the scheduler's blocking loop."""
        self.scheduler.start()
