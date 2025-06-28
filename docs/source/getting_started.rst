Getting Started
===============

Welcome to the Agentstr SDK! This guide will walk you through setting up your first agent project.

.. tip::
   Before you begin, make sure you have installed the SDK. If not, please see the :doc:`installation` guide.

Step 1: Initialize Your Project
-------------------------------

First, let's create a new project. The ``agentstr init`` command sets up a boilerplate agent for you.

.. code-block:: bash

   agentstr init hello_world

This will create a new directory called ``hello_world`` with a basic agent structure.

Step 2: Start the Development Relay
-----------------------------------

The Agentstr SDK includes a local development relay for testing. To start it, run:

.. code-block:: bash

   agentstr relay run

.. note::
   Keep this relay running in a separate terminal window. Your agent will connect to it to send and receive messages.

Step 3: Run Your Agent
----------------------

Now it's time to bring your agent to life. In another terminal, navigate to your project directory and run the main script:

.. code-block:: bash

   python hello_world/main.py

Your agent is now running and listening for events from the relay.

Step 4: Test Your Agent
-----------------------

To test that everything is working, you can use the provided test client. In a third terminal, run:

.. code-block:: bash

   python hello_world/test_client.py

You should see a "Hello" message from your agent, confirming that it received and responded to the test event.

.. code-block:: text

   Hello <your-agent-pubkey>!

Next Steps
----------

Congratulations on setting up your first agent! Here's what you can do next:

*   **Explore the API:** Dive into the :doc:`Core Modules <agentstr>` for in-depth API details.
*   **See More Examples:** Check out the `Examples <https://github.com/agentstr/agentstr-sdk/tree/main/examples>`_ directory for more advanced use cases.
*   **Deploy to the Cloud:** Learn how to deploy your agent with our :doc:`Cloud CI/CD <cloud_cicd>` guide.
