Core Components
===============

At the heart of `agentstr` are two core components:

*   :class:`~agentstr.agents.nostr_agent.NostrAgent`: This class adapts your agent's logic to the Nostr protocol. It takes a `chat_generator`—an async function that processes chat inputs—and handles the communication layer.
*   :class:`~agentstr.agents.nostr_agent_server.NostrAgentServer`: This class wraps a `NostrAgent` and runs it as a persistent server, listening for and responding to events on the Nostr network.

By working with these components directly, you can customize every aspect of your agent's behavior.

Relevant Modules
----------------

*   :doc:`agentstr.agents.nostr_agent`
*   :doc:`agentstr.agents.nostr_agent_server`
