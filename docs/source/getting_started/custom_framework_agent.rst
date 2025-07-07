Custom Framework Agent
======================

This guide demonstrates how to integrate a custom agentic framework with the Agentstr SDK, using the Google ADK as an example. By following these steps, you can bring your own framework and connect it to the Nostr ecosystem for advanced agent functionality.

.. tip::
   This example is more advanced and requires knowledge of other agentic frameworks. If you are new to agent development, we recommend starting with the :doc:`hello_world` guide.

Step 1: Initialize Your Project
-------------------------------

Start by initializing a new project if you haven't already:

.. code-block:: bash

   agentstr init custom_framework_agent

This sets up a `custom_framework_agent` directory with the basic structure for your agent.

Step 2: Update Environment Variables
------------------------------------

Update the `custom_framework_agent/.env` file with your LLM information and NWC connection string.

.. code-block:: bash

   LLM_BASE_URL=https://api.openai.com/v1
   LLM_API_KEY=your-api-key
   LLM_MODEL_NAME=gpt-3.5-turbo
   NWC_CONN_STR=nostr+walletconnect://<your-nwc-connection-string>
   MCP_SERVER_PUBKEY=<your-mcp-server-public-key>

.. note::
   - `NWC_CONN_STR` is the default environment variable for `NWCRelay` to enable Nostr Wallet Connect. You can override this by passing a connection string directly to the `NostrClient` constructor.
   - `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL_NAME` are the default environment variables for `AgentstrAgent` to enable LLM integration. You can override these by passing them directly to the agent constructor.
   - Replace `<your-mcp-server-key>` with the actual public key of a Nostr MCP server. If you're testing locally, ensure an MCP server is also running locally.
   - You can follow the :doc:`creating_an_mcp_server` guide to set up Nostr MCP server.
   

Step 3: Modify the Agent Code
-----------------------------

Open the ``main.py`` file in your project to review and customize the agent setup for Google ADK:

.. literalinclude:: ../../../getting_started/custom_framework_agent/main.py
   :language: python
   :linenos:


Customize the agent name, description, and skills as needed. You can also modify the payment amount (``satoshis``) for using the agent.

Step 4: Update Test Client
--------------------------

Update `custom_framework_agent/test_client.py` to interact with your tool-enabled agent.

.. literalinclude:: ../../../getting_started/custom_framework_agent/test_client.py
   :language: python
   :linenos:

Step 5: Start a Local Relay
---------------------------

Start a local Nostr relay for testing:

.. code-block:: bash

   agentstr relay start

Keep this running in a separate terminal.

Step 6: Run Your Custom Framework Agent
---------------------------------------

Run your custom framework agent with tool calling capabilities:

.. code-block:: bash

   python custom_framework_agent/main.py

Step 7: Test Your Agent
-----------------------

Use the test client to interact with your agent and see the tool listing response:

.. code-block:: bash

   python custom_framework_agent/test_client.py

You should see a response indicating the answer to a math question. If you check the MCP Server logs, you'll see that the addition tool was called by the agent.

Feel free to play around with the test client to ask the agent additional questions. Just note that any premium tools will require a Lightning payment.

.. note::
   If you encounter connection issues with the MCP server, ensure the server is running and accessible. Refer to troubleshooting tips in the :doc:`hello_world` guide for general connectivity issues.


Step 8 (Optional): Deploy to the Cloud
--------------------------------------

Deploy your Custom Framework Agent to the cloud for continuous operation. Assuming you are already logged into the Agentstr CLI, follow these steps:

1. **Set your cloud provider**:

   .. code-block:: bash

      export AGENTSTR_PROVIDER=aws  # or gcp, azure

2. **Deploy the agent**:

   .. code-block:: bash

      agentstr deploy -f custom_framework_agent/deploy.yml

   This command packages your agent and deploys it to the specified cloud provider. Ensure your project directory structure is compatible with the deployment requirements.

For more information on cloud deployment and CI/CD, see the :doc:`../cloud_cicd` guide.

Next Steps
----------

- **More Framework Providers**: Check out :doc:`../key_concepts/agent_providers` for more information on other agentic framework providers.
- **Dive into the API**: Learn more about the capabilities of the SDK by exploring the :doc:`../../agentstr` documentation.
- **Explore the Cookbook**: Check out the :doc:`../cookbook` for more advanced use cases and examples.
