Hello World
===========

This example walks you through setting up a basic 'Hello World' agent using the Agentstr SDK.

Step 1: Initialize Your Project
-------------------------------

First, let's create a new project. The ``agentstr init`` command sets up a boilerplate agent for you.

.. code-block:: bash

   agentstr init hello_world

This will create a new directory called ``hello_world`` with a basic agent structure, including a ``deploy.yml`` file for 1-click cloud deployment.

.. note::
   If you encounter issues with the `agentstr` command not being recognized, ensure that the Agentstr SDK is installed correctly and that your environment's PATH includes the location of the installed package. You can verify installation with `pip show agentstr-sdk` or `uv list agentstr-sdk` if using `uv`.

Step 2: Start a Local Relay
---------------------------

To test your agent locally, you need a Nostr relay running. The Agentstr SDK provides a simple way to start one:

.. code-block:: bash

   agentstr relay start

Keep this relay running in a separate terminal window. Your agent will connect to it to send and receive messages.

.. tip::
   The default port is 6969, so make sure that port is not in use. You can specify a different port with a config file. See an example config file `here <https://code.pobblelabs.org/nostr_relay/file?name=nostr_relay/config.yaml>`_.

Step 3: Run Your Agent
----------------------

Now it's time to bring your agent to life. In another terminal, navigate to your project directory and run the main script:

.. code-block:: bash

   python hello_world/main.py

Your agent is now running and listening for events from the relay.

.. warning::
   If you see connection errors, verify that your relay is running and accessible. Check for any firewall settings or network restrictions that might block local WebSocket connections.

Step 4: Test Your Agent
-----------------------

To test that everything is working, you can use the provided test client. In a third terminal, run:

.. code-block:: bash

   python hello_world/test_client.py

You should see a "Hello" message from your agent, confirming that it received and responded to the test event.

.. code-block:: text

   Hello <your-pubkey>!

.. note::
   **Troubleshooting Tips:**
   - **No response from agent**: Ensure both the relay and agent scripts are running. Check the relay logs for connection attempts and the agent logs for any errors processing events.
   - **Test client fails to connect**: Verify the relay URL in `test_client.py` matches the one your relay is running on. The default is usually `ws://localhost:8080`.

Step 5 (Optional): Deploy to the Cloud
--------------------------------------

Deploy your Hello World agent to the cloud for continuous operation and public accessibility. Assuming you are already logged into the Agentstr CLI, follow these steps:

1. **Set your cloud provider**:

   .. code-block:: bash

      export AGENTSTR_PROVIDER=aws  # or gcp, azure

2. **Deploy the agent**:

   .. code-block:: bash

      agentstr deploy -f hello_world/deploy.yml

   This command packages your agent and deploys it to the specified cloud provider. Ensure your project directory structure is compatible with the deployment requirements.

For more information on cloud deployment and CI/CD, see the :doc:`../cloud_cicd` guide.

Next Steps
----------

Congratulations on setting up your first agent with the Agentstr SDK! Here are some suggestions for what to do next:

- **Explore More Examples**: Check out the :doc:`simple_agent`, :doc:`tool_calling_agent`, and :doc:`payment_enabled_agent` guides for more advanced use cases.
- **Dive into the API**: Learn more about the capabilities of the SDK by exploring the :doc:`../../agentstr` documentation.
