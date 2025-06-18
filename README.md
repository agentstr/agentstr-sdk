# Agentstr SDK

[![Documentation](https://img.shields.io/badge/docs-online-blue.svg)](https://agentstr.com/docs)
[![PyPI](https://img.shields.io/pypi/v/agentstr-sdk)](https://pypi.org/project/agentstr-sdk/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Examples](#examples)
- [Agentstr CLI](#agentstr-cli)
- [Contributing](#contributing)
- [License](#license)

## Overview

Agentstr SDK is a powerful toolkit for building decentralized agentic applications on the Nostr and Lightning protocols. It provides seamless integration with [MCP (Model Context Protocol)](https://modelcontextprotocol.io/introduction), [A2A (Agent-to-Agent)](https://google-a2a.github.io/A2A/), and multiple popular agentic frameworks like [Agno](https://docs.agno.com/introduction), [DSPy](https://dspy.ai/), and [LangGraph](https://www.langchain.com/langgraph).

To ensure full stack decentralization, we recommend using [Routstr](https://routstr.com) as your LLM provider.

## Features

### Core Components
- **Nostr Integration**: Full support for Nostr protocol operations
  - Event publishing and subscription
  - Direct messaging
  - Metadata handling
- **Lightning Integration**: Full support for Nostr Wallet Connect (NWC)
  - Human-to-agent payments
  - Agent-to-agent payments
  - Agent-to-tool payments

### Agent Frameworks
- **[Agno](https://docs.agno.com/introduction)**
- **[DSPy](https://dspy.ai/)**
- **[LangGraph](https://www.langchain.com/langgraph)**
- **[PydanticAI](https://ai.pydantic.dev/)**
- **[Google ADK](https://google.github.io/adk-docs/)**
- **[OpenAI](https://openai.github.io/openai-agents-python/)**
- **Bring Your Own Agent**

### MCP (Model Context Protocol) Support
- Nostr MCP Server for serving tools over Nostr
- Nostr MCP Client for discovering and calling remote tools

### A2A (Agent-to-Agent) Support
- Direct message handling between agents
- Discover agents using Nostr metadata

### RAG (Retrieval-Augmented Generation)
- Query and process Nostr events
- Context-aware response generation
- Event filtering

## Installation

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) recommended (or `pip`)

### Install from PyPI
```bash
uv add agentstr-sdk[all]
```

### Install from source
```bash
git clone https://github.com/agentstr/agentstr-sdk.git
cd agentstr-sdk
uv sync --all-extras
```

## Quick Start

### Environment Setup
Copy the [examples/.env.sample](examples/.env.sample) file to `examples/.env` and fill in the environment variables.

## Examples

The [examples/](examples/) directory contains various implementation examples:

- [nostr_dspy_agent.py](examples/nostr_dspy_agent.py): A DSPy agent connected to Nostr MCP
- [nostr_langgraph_agent.py](examples/nostr_langgraph_agent.py): A LangGraph agent connected to Nostr MCP
- [nostr_agno_agent.py](examples/nostr_agno_agent.py): An Agno agent connected to Nostr MCP
- [nostr_google_agent.py](examples/nostr_google_agent.py): A Google ADK agent connected to Nostr MCP
- [nostr_openai_agent.py](examples/nostr_openai_agent.py): An OpenAI agent connected to Nostr MCP
- [nostr_pydantic_agent.py](examples/nostr_pydantic_agent.py): A PydanticAI agent connected to Nostr MCP
- [mcp_server.py](examples/mcp_server.py): Nostr MCP server implementation
- [mcp_client.py](examples/mcp_client.py): Nostr MCP client example
- [chat_with_agents.py](examples/chat_with_agents.py): Send a direct message to an agent
- [tool_discovery.py](examples/tool_discovery.py): Tool discovery and usage
- [rag.py](examples/rag.py): Retrieval-augmented generation example

To run an example:
```bash
uv run examples/nostr_dspy_agent.py
```

### Security Notes
- Never commit your private keys or sensitive information to version control
- Use environment variables or a secure secret management system
- The `.env.sample` file shows the required configuration structure

## Agentstr CLI

A lightweight command-line tool for deploying Agentstr agents to cloud providers with minimal configuration.

### Prerequisites

You need Docker installed and running for *all* providers.

| Provider | Required CLI tools | Environment variables |
|----------|-------------------|------------------------|
| AWS | `aws` | `AWS_PROFILE` (named profile) *or* standard `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` env vars |
| GCP | `gcloud`, `kubectl` | `GCP_PROJECT` (ID of your GCP project) |
| Azure | `az` | `AZURE_SUBSCRIPTION_ID` (GUID of target subscription) |

Make sure the CLI tools are authenticated against the target account/subscription/project and that Docker can push images to the registry used by each provider.

### Installation
The CLI is installed automatically with the **`agentstr-sdk[cli]`** extra:
```bash
uv add agentstr-sdk[cli]  # or: pip install "agentstr-sdk[cli]"
```
This places an `agentstr` executable on your `$PATH`.

### Global options
| Option | Description | Default |
|--------|-------------|---------|
| `--provider` [aws\|gcp\|azure] | Target cloud provider. | value of `AGENTSTR_PROVIDER` env var, or the provider specified in the config file |
| `-f, --config <path>` | YAML config file. Can also set `AGENTSTR_CONFIG`. | – |
| `-h, --help` | Show help for any command. | – |

If your config YAML contains a `provider:` field the CLI will infer the cloud automatically, so you usually only need the config path.

You can avoid passing `--config` (and optionally `--provider`) every time by exporting:
```bash
export AGENTSTR_PROVIDER=aws  # or gcp / azure
export AGENTSTR_CONFIG=configs/aws.yml
```

### Config files
A YAML file lets you declare most options once and reuse them across commands. Pass it with `-f/--config` **anywhere** on the command line or set `AGENTSTR_CONFIG`.

```bash
# Equivalent syntaxes
agentstr -f configs/azure.yml deploy my_app.py
agentstr deploy my_app.py --config configs/azure.yml
AGENTSTR_CONFIG=configs/azure.yml agentstr deploy my_app.py
```

#### Sample configs  
Sample YAML files live in the [`configs/`](configs) folder: [aws.yml](configs/aws.yml), [gcp.yml](configs/gcp.yml) and [azure.yml](configs/azure.yml).

```yaml
# configs/aws.yml
provider: aws
file_path: examples/mcp_server.py
env:
  NOSTR_RELAYS: wss://relay.primal.net,wss://relay.damus.io
secrets:
  EXAMPLE_MCP_SERVER_NSEC: arn:aws:secretsmanager:us-west-2:123:secret:EXAMPLE_MCP_SERVER_NSEC
```

```yaml
# configs/gcp.yml
provider: gcp
file_path: examples/mcp_server.py
env:
  NOSTR_RELAYS: wss://relay.primal.net,wss://relay.damus.io
secrets:
  EXAMPLE_MCP_SERVER_NSEC: projects/123/secrets/EXAMPLE_MCP_SERVER_NSEC/versions/latest
```

```yaml
# configs/azure.yml
provider: azure
file_path: examples/mcp_server.py
env:
  NOSTR_RELAYS: wss://relay.primal.net,wss://relay.damus.io
secrets:
  EXAMPLE_MCP_SERVER_NSEC: https://myvault.vault.azure.net/secrets/EXAMPLE_MCP_SERVER_NSEC
```

### Commands
| Command | Purpose |
|---------|---------|
| `deploy <app.py>` | Build Docker image, push and deploy your `app.py` as a container task/service. |
| `list` | List existing deployments for the selected provider. |
| `logs <name>` | Stream recent logs from the deployment. |
| `destroy <name>` | Tear down the deployment/service. |
| `put-secret <key> <value>` | Create or update a cloud-provider secret and return its reference string. |
| `put-secrets <env_file>` | Create or update multiple secrets from a .env file. |

#### `deploy` options
| Option | Description | Default |
|--------|-------------|---------|
| `--name <string>`          | Override deployment name (defaults to filename without extension). | `<app>` |
| `--cpu <int>`              | CPU units (AWS) / cores (GCP/Azure). | `256` (AWS) / `1` (GCP/Azure) |
| `--memory <int>`           | MiB (AWS) / MiB (GCP/Azure). | `512` |
| `--env KEY=VAL` (repeat)   | Add environment variables passed to container. | – |
| `--pip <package>` (repeat) | Extra Python dependencies installed into the image. | – |
| `--secret KEY=VAL` (repeat)| Secrets, merged with `--env` but shown separately in logs. | – |

#### Examples (with config files)
```bash
# Deploy an agent with extra deps and environment variables to AWS
agentstr deploy my_agent.py \
    --provider aws \
    --env RELAYS=$RELAYS \
    --secret MY_AGENT_NOSTR_NSEC=$MY_AGENT_NOSTR_NSEC \
    --pip openai langchain

# Upsert secrets from .env file
agentstr put-secrets path/to/.env

# Change provider per command
agentstr deploy bot.py --provider gcp --cpu 2 --memory 1024

# View logs
agentstr logs bot

# Destroy
agentstr destroy bot
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
