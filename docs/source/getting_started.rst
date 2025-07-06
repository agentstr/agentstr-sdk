Getting Started
===============

Welcome to the Agentstr SDK! This guide will walk you through setting up your first agent project with various examples to get you started. Whether you're new to agent development or looking to integrate advanced functionalities, we've got you covered with the following step-by-step guides.

.. tip::
   Before you begin, make sure you have installed the SDK. If not, please see the :doc:`installation` guide.

Overview of Examples
--------------------

The Agentstr SDK provides a range of examples to help you understand and implement different agent capabilities:

- **Hello World**: A basic introduction to setting up and running your first agent. This example covers initializing a project, starting a local relay, running the agent, testing it, and deploying to the cloud. Ideal for beginners. [:doc:`Learn more <getting_started/hello_world>`]
- **Simple Agent**: Builds on the basics by customizing the agent's response. This guide helps you modify the agent's logic to create a personalized interaction. [:doc:`Learn more <getting_started/simple_agent>`]
- **Tool Calling Agent**: Demonstrates how to integrate external tools using the Model Context Protocol (MCP). This example shows how agents can access and utilize various tools for enhanced functionality. [:doc:`Learn more <getting_started/tool_calling_agent>`]
- **Payment Enabled Agent**: Guides you through setting up an agent capable of handling payments with Nostr Wallet Connect (NWC). Learn to integrate payment processing into your agent's interactions. [:doc:`Learn more <getting_started/payment_enabled_agent>`]

.. toctree::
   :maxdepth: 1
   :caption: Examples

   getting_started/hello_world
   getting_started/simple_agent
   getting_started/tool_calling_agent
   getting_started/payment_enabled_agent

Next Steps
----------

Congratulations on exploring the getting started guides! Here's what you can do next:

*   **Explore the API:** Dive into the :doc:`Core Modules <agentstr>` for in-depth API details.
*   **See More Examples:** Check out the `Examples <https://github.com/agentstr/agentstr-sdk/tree/main/examples>`_ directory for more advanced use cases.
*   **Deploy to the Cloud:** Learn how to deploy your agent with our :doc:`Cloud CI/CD <cloud_cicd>` guide.
