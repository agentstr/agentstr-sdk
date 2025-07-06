Payment Enabled Agent
=====================

This guide expands on the :doc:`simple_agent` example to show you how to create an agent that can handle payments using Nostr Wallet Connect (NWC) with the Agentstr SDK.

Before you begin, ensure you have a Nostr Wallet Connect connection string. You can get one from a wallet service provider like `Alby <https://getalby.com/>`_.

Step 1: Initialize Your Project
-------------------------------

If you haven't already, initialize a new project:

.. code-block:: bash

   agentstr init payment_enabled

This creates a `payment_enabled` directory with the basic structure.

Step 2: Update .env file
------------------------

Update the `payment_enabled/.env` file with your LLM information and NWC connection string.

.. code-block:: bash

   LLM_BASE_URL=https://api.openai.com/v1
   LLM_API_KEY=your-api-key
   LLM_MODEL_NAME=gpt-3.5-turbo
   NWC_CONN_STR=nostr+walletconnect://<your-nwc-connection-string>

.. note::
   - `NWC_CONN_STR` is the default environment variable for `NWCRelay` to enable Nostr Wallet Connect. You can override this by passing a connection string directly to the `NostrClient` constructor.
   - `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL_NAME` are the default environment variables for `AgentstrAgent` to enable LLM integration. You can override these by passing a connection string directly to the `AgentstrAgent` constructor.

Step 3: Set Up Payment Integration
----------------------------------

Modify `payment_enabled/main.py` to include payment processing using NWC. You'll need an NWC connection string for this.

.. literalinclude:: ../../../getting_started/payment_enabled_agent/main.py
   :language: python
   :linenos:

.. note::
   Ensure you have access to a wallet service that supports Nostr Wallet Connect.

Step 4: Start a Local Relay
---------------------------

Start a local Nostr relay for testing:

.. code-block:: bash

   agentstr relay start

Keep this running in a separate terminal.

Step 5: Run Your Payment-Enabled Agent
--------------------------------------

Run your agent with payment processing capabilities:

.. code-block:: bash

   python payment_enabled/main.py

Step 6: Test Your Agent
-----------------------

Use the test client to interact with your agent and check your balance:

.. code-block:: bash

   python payment_enabled/test_client.py

You should see a lightning invoice for 10 sats. Upon payment, you should see a response from the agent.

.. note::
   If you encounter issues with the NWC connection, ensure your connection string is correct and the wallet service is accessible. Refer to troubleshooting tips in the :doc:`hello_world` guide for general connectivity issues.

Step 7 (Optional): Deploy to the Cloud
--------------------------------------

Deploy your Payment Enabled Agent to the cloud for continuous operation and public accessibility. Assuming you are already logged into the Agentstr CLI, follow these steps:

1. **Set your cloud provider**:

   .. code-block:: bash

      export AGENTSTR_PROVIDER=aws  # or gcp, azure

2. **Deploy the agent**:

   .. code-block:: bash

      agentstr deploy -f payment_enabled/deploy.yml

   This command packages your agent and deploys it to the specified cloud provider. Ensure your project directory structure is compatible with the deployment requirements.

For more information on cloud deployment and CI/CD, see the :doc:`../cloud_cicd` guide.

Next Steps
----------

- **Explore More Examples**: Check out the :doc:`tool_calling_agent` guide for a more advanced use case.
- **Dive into the API**: Learn more about the capabilities of the SDK by exploring the :doc:`../../agentstr` documentation.
