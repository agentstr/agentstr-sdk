Logging
=======

The ``agentstr.logger`` module provides a pre-configured logger for use throughout the Agentstr SDK. It ensures that log messages are formatted consistently and can be easily controlled.

Overview
--------

The logger is configured to output messages to the console with a standardized format that includes a timestamp, log level, and message.

**Typical usage:**

.. code-block:: python

   from agentstr.logger import get_logger

   # Get the logger instance
   logger = get_logger(__name__)

   # Log messages at different levels
   logger.debug("This is a debug message.")
   logger.info("This is an info message.")
   logger.warning("This is a warning message.")
   logger.error("This is an error message.")


Reference
---------

.. automodule:: agentstr.logger
   :members:
   :undoc-members:
   :show-inheritance:
