Scheduler
=========

This module provides a simple, opinionated scheduler for running asynchronous jobs.

Overview
--------

The ``Scheduler`` class is a wrapper around APScheduler that simplifies running async functions on a schedule. It supports interval-based and cron-style jobs.

Usage
~~~~~

.. code-block:: python

   import asyncio
   from agentstr.scheduler import Scheduler

   async def my_async_job():
       print("Running my async job!")

   # Create a scheduler instance
   scheduler = Scheduler()

   # Schedule the job to run every 10 seconds
   scheduler.add_interval_job(my_async_job, seconds=10)

   # Start the scheduler (this is a blocking call)
   # scheduler.start()

Reference
---------

.. automodule:: agentstr.scheduler
   :members:
   :undoc-members:
   :show-inheritance:
