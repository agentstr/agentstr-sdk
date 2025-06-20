# ✨ Agentstr SDK

[![Docs](https://img.shields.io/badge/docs-online-blue.svg)](https://docs.agentstr.com)
[![PyPI](https://img.shields.io/pypi/v/agentstr-sdk)](https://pypi.org/project/agentstr-sdk/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[agentstr.com](https://agentstr.com)

> Build decentralised agents on the **Nostr** + **Lightning** stack with one super-friendly Python package.

---

## 📖 Documentation
Everything – installation guide, tutorials, SDK reference, CLI reference – lives at **[docs.agentstr.com](https://docs.agentstr.com)**.

## ⚡ Quick install
```bash
pip install "agentstr-sdk[all]"   # or: uv add agentstr-sdk[all]
```

## 🚀 Examples
Run any of the ready-to-go demos in [`examples/`](examples):


| Example | Framework |
|---------|-----------|
| [agent_discovery.py](examples/agent_discovery.py) | Agent discovery |
| [chat_with_agents.py](examples/chat_with_agents.py) | Direct messaging |
| [commands_client.py](examples/commands_client.py) | Command client |
| [commands_server.py](examples/commands_server.py) | Command server |
| [mcp_client.py](examples/mcp_client.py) | Nostr MCP Client |
| [mcp_server.py](examples/mcp_server.py) | Nostr MCP Server |
| [nostr_agno_agent.py](examples/nostr_agno_agent.py) | Agno |
| [nostr_dspy_agent.py](examples/nostr_dspy_agent.py) | DSPy |
| [nostr_google_agent.py](examples/nostr_google_agent.py) | Google ADK |
| [nostr_langgraph_agent.py](examples/nostr_langgraph_agent.py) | LangGraph |
| [nostr_openai_agent.py](examples/nostr_openai_agent.py) | OpenAI |
| [nostr_pydantic_agent.py](examples/nostr_pydantic_agent.py) | PydanticAI |
| [rag.py](examples/rag.py) | RAG / Retrieval |
| [tool_discovery.py](examples/tool_discovery.py) | Tool discovery |

```bash
uv run examples/nostr_dspy_agent.py
```

## 🤝 Contributing
PRs are welcome! Open an issue first to discuss your idea.

## ⚖️ License
MIT