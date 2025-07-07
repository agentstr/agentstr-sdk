# Agentstr Custom Framework Agent Skeleton

This is a minimal example of an Agentstr agent that uses a custom framework (Google ADK) and calls an external Nostr MCP Server. It is also payment enabled.

#### To run it, first install the dependencies:

`pip install -r requirements.txt`

#### Then start the local relay:

`agentstr relay start`

#### Then run it:

`python main.py`

#### You can now test the agent with the test_client.py script:

`python test_client.py`

#### Learn More:

For a complete guide on building a custom framework agent, explore the [Custom Framework Agent Guide](https://docs.agentstr.com/getting_started/custom_framework_agent.html) in the Agentstr documentation.