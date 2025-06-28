from dotenv import load_dotenv

load_dotenv()

import os
import httpx
from agentstr import NostrMCPServer


BASE_URL = 'https://blockchain.info/q'


async def get_24hr_price(client) -> str:
    """24 hour weighted price from the largest exchanges"""
    return (await client.get(f'{BASE_URL}/24hrprice')).text

async def get_market_cap(client) -> str:
    """USD market cap (based on 24 hour weighted price)"""
    return (await client.get(f'{BASE_URL}/marketcap')).text
    
async def get_24hr_transaction_count(client) -> str:
    """Number of transactions in the last 24 hours"""
    return (await client.get(f'{BASE_URL}/24hrtransactioncount')).text

async def get_24hr_btc_sent(client) -> str:
    """Number of BTC sent in the last 24 hours"""
    return (await client.get(f'{BASE_URL}/24hrbtcsent')).text

async def get_hashrate(client) -> str:
    """Current hashrate in GH/s"""
    return (await client.get(f'{BASE_URL}/hashrate')).text

async def get_difficulty(client) -> str:
    """Current difficulty"""
    return (await client.get(f'{BASE_URL}/getdifficulty')).text

async def get_block_count(client) -> str:
    """Current block count"""
    return (await client.get(f'{BASE_URL}/getblockcount')).text

async def get_bitcoin_data() -> dict:
    """Get latest Bitcoin blockchain data

    Returns:
        24hr_price: 24 hour weighted price from the largest exchanges
        market_cap: USD market cap (based on 24 hour weighted price)
        24hr_transaction_count: Number of transactions in the last 24 hours
        24hr_btc_sent: Number of BTC sent in the last 24 hours
        hashrate: Current hashrate in GH/s
        difficulty: Current difficulty
        block_count: Current block count
    """
    async with httpx.AsyncClient() as client:
        return {
            "24hr_price": await get_24hr_price(client),
            "market_cap": await get_market_cap(client),
            "24hr_transaction_count": await get_24hr_transaction_count(client),
            "24hr_btc_sent": await get_24hr_btc_sent(client),
            "hashrate": await get_hashrate(client),
            "difficulty": await get_difficulty(client),
            "block_count": await get_block_count(client),
        }


async def run():
    relays = os.getenv('NOSTR_RELAYS').split(',')
    private_key = os.getenv('MCP_SERVER_PRIVATE_KEY')

    server = NostrMCPServer("Bitcoin Data Tool", 
                            relays=relays, 
                            private_key=private_key,
                            tools=[get_bitcoin_data])

    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())


    