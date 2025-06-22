from dotenv import load_dotenv

load_dotenv()

import os
from agentstr.database import Database, User


async def run():
    db = Database(connection_string=os.getenv("DATABASE_URL"), agent_name='test')
    await db.async_init()

    await db.upsert_user(User(user_id='test', available_balance=100))
    user = await db.get_user('test')
    
    print(user)



if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
