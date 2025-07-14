# Bitcoin MCP Server

## Overview
The Bitcoin MCP Server is a specialized Model Context Protocol (MCP) server designed to integrate Bitcoin blockchain network data into the Agentstr ecosystem. This server enables agents to fetch key Bitcoin metrics such as 24-hour weighted price, market cap, transaction count, BTC sent, hash rate, difficulty, and block count, enhancing the capabilities of Agentstr applications for Bitcoin data analysis.

For more comprehensive documentation on MCP Servers and integrating them with Agentstr, visit the official documentation at [docs.agentstr.com](https://docs.agentstr.com).

## Running the Bitcoin MCP Server
To run the Bitcoin MCP Server locally for development or testing purposes, follow these steps:
1. **Ensure Dependencies**: Make sure you have Python 3.12+ installed along with the necessary packages listed in `requirements.txt`.
2. **Environment Setup**: Configure any required environment variables. You may need to set API keys or connection details for Bitcoin data providers, as well as Nostr relays and private keys for Agentstr.
3. **Start the Server**: From this directory, run the following command:
   ```bash
   python server.py
   ```
   This will initialize the MCP server and connect it to the Nostr decentralized network using Agentstr.
4. **Connect with Agentstr**: Update your Agentstr application configuration to interact with this MCP server via the Nostr network using the appropriate relays and keys.

## File Structure
- **`server.py`**: The main entry point for the Bitcoin MCP Server. It sets up the connection to the Nostr decentralized network using Agentstr, defines tools for fetching Bitcoin blockchain data (e.g., price, market cap, hash rate), and handles MCP communication over Nostr.
- **`requirements.txt`**: Lists the Python dependencies required to run the server.
- **`deploy.yml`**: Configuration file for deployment, detailing how the server is containerized and deployed to cloud services.
- **`nostr-metadata.yml`**: Contains metadata for the MCP server, including its name, display name, username, website, picture, and banner.

## Deployment
The Bitcoin MCP Server is deployed using GitHub Actions for continuous integration and deployment (CI/CD). The workflow configuration can be found in `.github/workflows/` within the Agentstr SDK repository.

For more detailed information on deploying MCP Servers using GitHub Actions and cloud providers, refer to the Cloud CI/CD documentation at [docs.agentstr.com/cloud_cicd](https://docs.agentstr.com/cloud_cicd).

Ensure that the necessary secrets (like API keys or registry credentials) are configured in the GitHub repository settings for the workflow to execute successfully.

## Contributing
If you wish to contribute to the development of the Bitcoin MCP Server, please follow the contribution guidelines outlined in the main Agentstr SDK repository. Pull requests are welcome for bug fixes, feature additions, or documentation improvements.

## Support
For support or to report issues, please file a GitHub issue in the Agentstr SDK repository or reach out through the community channels linked at [docs.agentstr.com](https://docs.agentstr.com).
