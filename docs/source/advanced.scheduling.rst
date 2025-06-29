Scheduling
==========

`agentstr` includes a built-in scheduler for running asynchronous jobs at specified intervals or times. The :class:`~agentstr.scheduler.Scheduler` class wraps the `APScheduler` library, providing a simple interface for scheduling tasks within your agent.

Here’s how you can use it:

.. code-block:: python

    from agentstr.scheduler import Scheduler

    async def my_periodic_task():
        print("This task runs every 10 seconds.")

    scheduler = Scheduler()
    scheduler.add_job(my_periodic_task, "interval", seconds=10)
    scheduler.start()

Relevant Modules
----------------

*   :doc:`agentstr.scheduler`
