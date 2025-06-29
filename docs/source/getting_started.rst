Getting Started
===============

Welcome to the Agentstr SDK! This guide will walk you through setting up your first agent project.

.. tip::
   Before you begin, make sure you have installed the SDK. If not, please see the :doc:`installation` guide.

Step 1: Initialize Your Project
-------------------------------

First, let's create a new project. The ``agentstr init`` command sets up a boilerplate agent for you.

.. code-block:: bash

   agentstr init hello_world

This will create a new directory called ``hello_world`` with a basic agent structure, including a ``deploy.yml`` file for 1-click cloud deployment.

Step 2: Start the Development Relay
-----------------------------------

The Agentstr SDK includes a local development relay for testing. To start it, run:

.. code-block:: bash

   agentstr relay run

.. note::
   Keep this relay running in a separate terminal window. Your agent will connect to it to send and receive messages.

Step 3: Run Your Agent
----------------------

Now it's time to bring your agent to life. In another terminal, navigate to your project directory and run the main script:

.. code-block:: bash

   python hello_world/main.py

Your agent is now running and listening for events from the relay.

Step 4: Test Your Agent
-----------------------

To test that everything is working, you can use the provided test client. In a third terminal, run:

.. code-block:: bash

   python hello_world/test_client.py

You should see a "Hello" message from your agent, confirming that it received and responded to the test event.

.. code-block:: text

   Hello <your-pubkey>!

Step 5: One-Click Cloud Deployment
----------------------------------

Once you've tested your agent locally, you can deploy it to the cloud with a single command. The Agentstr SDK uses the ``hello_world/deploy.yml`` file created during initialization to handle the packaging, containerization, and deployment for you.

.. note::
   The cloud provider can be specified via the ``AGENTSTR_PROVIDER`` environment variable or in the configuration file.

**Cloud Provider Requirements**

Below are the prerequisites and example commands for each supported cloud provider.

*   **AWS (Amazon Web Services)**
    *   **Prerequisites:** `AWS CLI <https://aws.amazon.com/cli/>`_
    *   **Command:**

        .. code-block:: bash

           # Configure your AWS profile
           export AWS_PROFILE=agentstr
           export AGENTSTR_PROVIDER=aws

           # Configure CLI
           aws configure --profile $AWS_PROFILE

           # Deploy
           agentstr deploy -f hello_world/deploy.yml

*   **GCP (Google Cloud Platform)**
    *   **Prerequisites:** `gcloud CLI <https://cloud.google.com/sdk/gcloud>`_ and `kubectl <https://kubernetes.io/docs/tasks/tools/install-kubectl/>`_
    *   **Command:**

        .. code-block:: bash

           # Set your GCP Project ID
           export GCP_PROJECT=agentstr
           export AGENTSTR_PROVIDER=gcp

           # Authenticate with gcloud
           gcloud auth login

           # Deploy
           agentstr deploy -f hello_world/deploy.yml

*   **Azure**
    *   **Prerequisites:** `Azure CLI <https://docs.microsoft.com/en-us/cli/azure/install-azure-cli>`_
    *   **Command:**

        .. code-block:: bash

           # Set your Azure Subscription ID
           export AZURE_SUBSCRIPTION_ID=<your-subscription-id>
           export AGENTSTR_PROVIDER=azure

           # Authenticate with Azure
           az login

           # Deploy
           agentstr deploy -f hello_world/deploy.yml

.. note::
   For more detailed instructions on configuring deployment settings, managing secrets, and setting up CI/CD pipelines, please see the :doc:`Cloud CI/CD <cloud_cicd>` guide.


Next Steps
----------

Congratulations on setting up your first agent! Here's what you can do next:

*   **Explore the API:** Dive into the :doc:`Core Modules <agentstr>` for in-depth API details.
*   **See More Examples:** Check out the `Examples <https://github.com/agentstr/agentstr-sdk/tree/main/examples>`_ directory for more advanced use cases.
*   **Deploy to the Cloud:** Learn how to deploy your agent with our :doc:`Cloud CI/CD <cloud_cicd>` guide.
