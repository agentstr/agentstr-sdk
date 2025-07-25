Simple Agent
============

This guide will help you create a simple agent using the Agentstr SDK, building on the basics from the :doc:`hello_world` example.

Step 1: Initialize Your Project
-------------------------------

If you haven't already, initialize a new project with the Agentstr SDK:

.. code-block:: bash

   agentstr init simple_agent

This creates a `simple_agent` directory with the basic structure for your agent.

Step 2: Update .env file
------------------------

Update the `simple_agent/.env` file with your LLM information.

.. code-block:: bash

   LLM_BASE_URL=https://api.openai.com/v1
   LLM_API_KEY=your-api-key
   LLM_MODEL_NAME=gpt-3.5-turbo

Step 3: Modify the Agent Logic
------------------------------

Open `simple_agent/main.py` in your preferred editor. You'll see the basic 'Hello World' agent setup. Let's modify it to respond with a custom message.

.. literalinclude:: ../../../getting_started/simple_agent/main.py
   :language: python
   :linenos:


Step 4: Start a Local Relay
---------------------------

Start a local Nostr relay for testing:

.. code-block:: bash

   agentstr relay start

Keep this running in a separate terminal.

Step 5: Run Your Simple Agent
-----------------------------

Run your modified agent:

.. code-block:: bash

   python simple_agent/main.py

Step 6: Test Your Agent
-----------------------

Use the test client to interact with your agent:

.. code-block:: bash

   python simple_agent/test_client.py

You should see a response like:

.. code-block:: text

   Hi there! How are you doing today? Is there anything I can help you with?

.. note::
   If you encounter issues, refer to the troubleshooting tips in the :doc:`hello_world` guide.

Step 7 (Optional): Deploy to the Cloud
--------------------------------------

Deploy your Simple Agent to the cloud for continuous operation and public accessibility. Assuming you are already logged into the Agentstr CLI, follow these steps:

1. **Set your cloud provider**:

   .. code-block:: bash

      export AGENTSTR_PROVIDER=aws  # or gcp, azure

2. **Deploy the agent**:

   .. code-block:: bash

      agentstr deploy -f simple_agent/deploy.yml

   This command packages your agent and deploys it to the specified cloud provider. Ensure your project directory structure is compatible with the deployment requirements.

For more information on cloud deployment and CI/CD, see the :doc:`../cloud_cicd` guide.

Next Steps
----------

- **Explore More Examples**: Check out the :doc:`tool_calling_agent` and :doc:`payment_enabled_agent` guides for adding tool and payment capabilities to your agent.
- **Dive into the API**: Learn more about the capabilities of the SDK by exploring the :doc:`../../agentstr` documentation.
