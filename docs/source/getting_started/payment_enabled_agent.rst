Payment Enabled Agent
=====================

This guide will show you how to create an agent that can handle payments using Nostr Wallet Connect (NWC) with the Agentstr SDK.

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


Step 3: Set Up Payment Integration
----------------------------------

Modify `payment_enabled/main.py` to include payment processing using NWC. You'll need an NWC connection string for this.

.. code-block:: python

   """Simple Agentstr agent with payment processing."""

   from dotenv import load_dotenv
   load_dotenv()

   import asyncio
   from agentstr import AgentstrAgent, NostrClient
   import os


   # Define the Nostr Agent Server
   async def main():
      agent = AgentstrAgent(
         name="PaymentEnabledAgent",
         description="A simple Agentstr Agent with payment processing",
         satoshis=10,  # 10 sats per message
         nostr_client=NostrClient(nwc_str=os.getenv("NWC_CONN_STR"))
      )
      await agent.start()


   # Run the server
   if __name__ == "__main__":
      asyncio.run(main())

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

Step 7: Cloud Deployment
------------------------

Deploy your Payment Enabled Agent to the cloud for continuous operation and public accessibility. Assuming you are already logged into the Agentstr CLI, follow these steps:

1. **Set your cloud provider**:

   .. code-block:: bash

      export AGENTSTR_PROVIDER=aws  # or gcp, azure

2. **Deploy the agent**:

   .. code-block:: bash

      agentstr deploy -f payment_enabled/deploy.yml

   This command packages your agent and deploys it to the specified cloud provider. Ensure your project directory structure is compatible with the deployment requirements.

Next Steps
----------

- **Enhance Payment Logic**: Customize payment amounts, conditions, or integrate with different payment providers via Nostr Wallet Connect.
- **Explore Persistence**: Learn how to store payment history or user data with :doc:`../key_concepts/persistence`.
- **Explore More Examples**: Check out the :doc:`../key_concepts/cookbook` for more advanced use cases and examples.