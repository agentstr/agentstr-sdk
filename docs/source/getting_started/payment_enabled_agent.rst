Payment Enabled Agent
=====================

This guide will show you how to create an agent that can handle payments using Nostr Wallet Connect (NWC) with the Agentstr SDK.

Step 1: Initialize Your Project
-------------------------------

If you haven't already, initialize a new project:

.. code-block:: bash

   agentstr init payment_agent

This creates a `payment_agent` directory with the basic structure.

Step 2: Set Up Payment Integration
----------------------------------

Modify `payment_agent/main.py` to include payment processing using NWC. You'll need an NWC connection string for this.

.. code-block:: python

   import asyncio
   from agentstr import NostrAgent, AgentCard, ChatInput, ChatOutput
   from agentstr.relays.nwc_relay import NWCRelay

   async def payment_enabled_chat(input: ChatInput):
       nwc_string = "nostr+walletconnect://<your-nwc-connection-string>"
       nwc_relay = NWCRelay(nwc_string)
       balance = await nwc_relay.get_balance()
       yield ChatOutput(message=f"Hello! Your current balance is {balance} sats.")

   agent_card = AgentCard(name="PaymentAgent", description="An agent that can process payments")
   nostr_agent = NostrAgent(agent_card=agent_card, chat_generator=payment_enabled_chat)

   # Continue with the standard setup for running the agent

.. note::
   Replace `<your-nwc-connection-string>` with your actual NWC connection string. Ensure you have access to a wallet service that supports Nostr Wallet Connect.

Step 3: Start a Local Relay
---------------------------

Start a local Nostr relay for testing:

.. code-block:: bash

   agentstr relay start

Keep this running in a separate terminal.

Step 4: Run Your Payment-Enabled Agent
--------------------------------------

Run your agent with payment processing capabilities:

.. code-block:: bash

   python payment_agent/main.py

Step 5: Test Your Agent
-----------------------

Use the test client to interact with your agent and check your balance:

.. code-block:: bash

   python payment_agent/test_client.py

You should see a response with your current balance if the NWC connection is successful.

.. note::
   If you encounter issues with the NWC connection, ensure your connection string is correct and the wallet service is accessible. Refer to troubleshooting tips in the :doc:`hello_world` guide for general connectivity issues.

Step 6: Cloud Deployment
------------------------

Deploy your Payment Enabled Agent to the cloud for continuous operation and public accessibility. Assuming you are already logged into the Agentstr CLI, follow these steps:

1. **Set your cloud provider**:

   .. code-block:: bash

      export AGENTSTR_PROVIDER=aws  # or gcp, azure

2. **Deploy the agent**:

   .. code-block:: bash

      agentstr deploy -f payment_agent/deploy.yml

   This command packages your agent and deploys it to the specified cloud provider. Ensure your project directory structure is compatible with the deployment requirements.

Next Steps
----------

- **Enhance Payment Logic**: Customize payment amounts, conditions, or integrate with different payment providers via Nostr Wallet Connect.
- **Explore Persistence**: Learn how to store payment history or user data with :doc:`../key_concepts/persistence`.
- **Explore More Examples**: Check out the :doc:`../key_concepts/cookbook` for more advanced use cases and examples.