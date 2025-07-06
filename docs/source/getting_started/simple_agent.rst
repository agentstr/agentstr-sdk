Simple Agent
============

This guide will help you create a simple agent using the Agentstr SDK, building on the basics from the 'Hello World' example.

Step 1: Initialize Your Project
-------------------------------

If you haven't already, initialize a new project with the Agentstr SDK:

.. code-block:: bash

   agentstr init simple_agent

This creates a `simple_agent` directory with the basic structure for your agent.

Step 2: Modify the Agent Logic
------------------------------

Open `simple_agent/main.py` in your preferred editor. You'll see the basic 'Hello World' agent setup. Let's modify it to respond with a custom message.

.. code-block:: python

   from agentstr import NostrAgent, AgentCard, ChatInput, ChatOutput

   async def custom_chat(input: ChatInput):
       yield ChatOutput(message=f"Hello, {input.user_id}! I'm your custom simple agent.")

   agent_card = AgentCard(name="SimpleAgent", description="A basic custom agent")
   nostr_agent = NostrAgent(agent_card=agent_card, chat_generator=custom_chat)

   # The rest of the setup remains similar to the Hello World example

Step 3: Start a Local Relay
---------------------------

Start a local Nostr relay for testing:

.. code-block:: bash

   agentstr relay start

Keep this running in a separate terminal.

Step 4: Run Your Simple Agent
-----------------------------

Run your modified agent:

.. code-block:: bash

   python simple_agent/main.py

Step 5: Test Your Agent
-----------------------

Use the test client to interact with your agent:

.. code-block:: bash

   python simple_agent/test_client.py

You should see a response like:

.. code-block:: text

   Hello, <your-user-id>! I'm your custom simple agent.

.. note::
   If you encounter issues, refer to the troubleshooting tips in the :doc:`hello_world` guide.

Step 6: Cloud Deployment
------------------------

Deploy your Simple Agent to the cloud for continuous operation and public accessibility. Assuming you are already logged into the Agentstr CLI, follow these steps:

1. **Set your cloud provider**:

   .. code-block:: bash

      export AGENTSTR_PROVIDER=aws  # or gcp, azure

2. **Deploy the agent**:

   .. code-block:: bash

      agentstr deploy -f simple_agent/deploy.yml

   This command packages your agent and deploys it to the specified cloud provider. Ensure your project directory structure is compatible with the deployment requirements.

Next Steps
----------

- **Expand Functionality**: Add more complex logic to `handle_message` to handle various user inputs or integrate with external APIs for enhanced capabilities.
- **Explore Advanced Features**: Dive into advanced topics like :doc:`../key_concepts/scheduling` and :doc:`../key_concepts/persistence` to make your agent more robust and stateful.
- **Explore More Examples**: Check out the :doc:`tool_calling_agent` and :doc:`payment_enabled_agent` guides for adding tool capabilities to your agent.