Utilities
=========

The ``agentstr.utils`` module contains various helper functions and utility classes used throughout the Agentstr SDK. These utilities provide common functionalities such as asynchronous operations, data handling, and more.

Overview
--------

This module is a collection of tools that support the core functionality of the SDK. You can import and use these utilities in your own code when building on top of Agentstr.

**Typical usage:**

.. code-block:: python

   from agentstr.utils import to_metadata_yaml

   # Assume you have a YAML file named 'sample_metadata.yaml' with the following content:
   #
   # name: "MyAgent"
   # about: "An example agent for demonstration."
   # picture: "https://example.com/my_agent.png"

   # Convert the YAML file to a Metadata object
   metadata = to_metadata_yaml('sample_metadata.yaml')

   print(f"Agent name: {metadata.name}")
   print(f"About: {metadata.about}")
   print(f"Picture URL: {metadata.picture}")


Reference
---------

.. automodule:: agentstr.utils
   :members:
   :undoc-members:
   :show-inheritance:
