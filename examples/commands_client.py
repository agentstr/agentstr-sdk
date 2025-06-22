from dotenv import load_dotenv

load_dotenv()

import os

from agentstr import NostrClient

# Define relays and private key
relays   = os.getenv("NOSTR_RELAYS").split(",")
private_key = os.getenv("EXAMPLE_MCP_CLIENT_NSEC")

# Define MCP server public key
server_public_key = os.getenv("EXAMPLE_MCP_SERVER_PUBKEY")


async def run()   :
    # Initialize the client
    client = NostrClient(relays=relays, private_key=private_key)
    #message = await client.send_direct_message_and_receive_response(server_public_key, "!help")
    #print(message.message)

    #message = await client.send_direct_message_and_receive_response(server_public_key, "!describe")
    #print(message.message)

    message = await client.send_direct_message_and_receive_response(server_public_key, "!balance")
    print(message.message)

    message = await client.send_direct_message_and_receive_response(server_public_key, "!deposit")
    print(message.message)

    #message = await client.send_direct_message_and_receive_response(server_public_key, "!deposit 10")
    #print(message.message)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())