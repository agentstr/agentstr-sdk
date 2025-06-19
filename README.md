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

## Full Documentation

For full SDK and CLI documentation, visit **[docs.agentstr.com](https://docs.agentstr.com)**.

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
For the comprehensive command reference, see the [CLI documentation](https://docs.agentstr.com/agentstr.cli.html).

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

### Multicloud CI/CD with GitHub Actions
Ready-to-use workflows let you deploy to **AWS**, **GCP**, or **Azure** with a single push. Each workflow installs the CLI and invokes `agentstr deploy` using the provider-specific config file.

| Cloud | Workflow file | What it does |
|-------|---------------|--------------|
| AWS   | [`deploy-aws.yml`](.github/workflows/deploy-aws.yml) | Installs deps, logs in with AWS creds and runs `agentstr deploy -f configs/aws.yml`. |
| GCP   | [`deploy-gcp.yml`](.github/workflows/deploy-gcp.yml) | Authenticates via service-account JSON, installs `kubectl`, gets GKE creds and runs `agentstr deploy -f configs/gcp.yml`. |
| Azure | [`deploy-azure.yml`](.github/workflows/deploy-azure.yml) | Uses `az` login and runs `agentstr deploy -f configs/azure.yml`. |

Copy the desired file into your own repo, set the referenced secrets, and enjoy push-to-deploy for your agents.

### Global options
| Option | Description | Default |
|--------|-------------|---------|
| `-f, --config <path>` | YAML config file. Can also set `AGENTSTR_CONFIG`. | – |
| `-h, --help` | Show help for any command. | – |

If your config YAML contains a `provider:` field the CLI will infer the cloud automatically, so you usually only need the config path.

### Config files
Declare your deployment once in a YAML file and reuse it across commands.

```bash
agentstr deploy -f configs/aws.yml
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

### Configuration

The `agentstr` commands rely on a small YAML file that bundles everything required for a deployment. A minimal example exists for [AWS](configs/aws.yml), [GCP](configs/gcp.yml) and [Azure](configs/azure.yml).

```yaml
provider: aws             # Target cloud provider: aws | gcp | azure
file_path: app/agent.py   # Path to the Python entry-point for your agent
name: my-agent            # Optional – deployment name (defaults to file_path stem)
cpu: 256                  # Optional – CPU units / cores
memory: 512               # Optional – Memory in MiB
extra_pip_deps:           # Optional – extra Python packages to install
  - openai
  - langchain
env:                      # Optional – environment variables
  KEY: value
secrets:                  # Optional – provider-managed secrets
  MY_SECRET: arn:aws:secretsmanager:us-west-2:123:secret:MY_SECRET
```

Key fields:

| Field | Type | Description |
|-------|------|-------------|
| `provider` | string | Required. One of `aws`, `gcp`, `azure`. |
| `file_path` | path | Required. Python file that will be executed inside the container. |
| `name` | string | Deployment/service name. Defaults to the filename without extension. |
| `cpu` | int | CPU units/cores to allocate. Defaults vary by provider. |
| `memory` | int | Memory in MiB. Defaults to 512. |
| `env` | map | Environment variables passed to the container. |
| `secrets` | map | Key/value pairs stored in the provider’s secret manager. Values must be the provider-specific reference (ARN/URI/path). |
| `extra_pip_deps` | list | Extra PyPI packages installed into the image before deploy. |

With the config in place you can deploy, list, stream logs, etc. by referencing it:

#### Cloud Provider Environment Variables

```bash
# AWS (assuming aws is authenticated)
export AWS_PROFILE=your-profile

# GCP (assuming gcloud is authenticated)
export GCP_PROJECT=your-project

# Azure (assuming az is authenticated)
export AZURE_SUBSCRIPTION_ID=your-subscription-id
```

#### CLI Commands

```bash
# Deploy / update
agentstr deploy -f configs/aws.yml

# View logs
agentstr logs -f configs/aws.yml

# List deployments
agentstr list -f configs/aws.yml

# Destroy
agentstr destroy -f configs/aws.yml
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
