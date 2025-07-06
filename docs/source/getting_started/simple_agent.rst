Simple Agent
============

This guide will help you create a simple agent using the Agentstr SDK, building on the basics from the 'Hello World' example.

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

.. code-block:: python

   """Simple Agentstr agent - pass-through LLM call."""

   from dotenv import load_dotenv
   load_dotenv()

   import asyncio
   from agentstr import AgentstrAgent


   # Define the Nostr Agent Server
   async def main():
      agent = AgentstrAgent(
         name="SimpleAgent",
         description="A simple Agentstr Agent",
      )
      await agent.start()


   # Run the server
   if __name__ == "__main__":
      asyncio.run(main())


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

Step 7: Cloud Deployment
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