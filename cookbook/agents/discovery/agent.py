from dotenv import load_dotenv

load_dotenv()

import os
import json
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agentstr import NostrClient, AgentCard, ChatInput, Skill, PrivateKey, NostrAgentServer


base_url = os.getenv("LLM_BASE_URL")
api_key = os.getenv("LLM_API_KEY")
model_name = os.getenv("LLM_MODEL_NAME")


client = NostrClient(relays=os.getenv("NOSTR_RELAYS").split(","), private_key=os.getenv("AGENT_PRIVATE_KEY"))

with open(os.path.join(os.path.dirname(__file__), 'known_agents.txt'), 'r') as f:
    known_agents = f.read().splitlines()

async def run():
    agent_cards = []
    name_to_pubkey = {}
    for pubkey in known_agents:
        metadata = await client.get_metadata_for_pubkey(pubkey.strip())
        try:
            agent_info = AgentCard.model_validate_json(metadata.about)
            agent_cards.append(agent_info)
            name_to_pubkey[agent_info.name] = pubkey
            print(json.dumps(agent_info.model_dump(), indent=4))
        except:
            pass  # Invalid agent card

    print(f'Num agents: {len(agent_cards)}')
    prompt = """You are an intelligent agent router that helps users find the most relevant agents on Nostr based on their requests. 

Your task is to carefully analyze the user's request and match it with the most suitable agent from the list below. Consider the following guidelines:
1. Only recommend an agent if there's a strong match with the user's request
2. Be specific about why the agent is a good match
3. If no agent is a good fit, explicitly state that no agent is a good fit
4. Consider both the agent's name and description when making matches

Available Agents:
"""
    for agent_card in agent_cards:
        prompt += f"""
{'='*80}
Name: {agent_card.name}
Description: {agent_card.description}
{'='*80}"""

    prompt += """

Response Format:
{
    "name": "Agent Name",  // Only include if there's a match
    "message": "Detailed explanation of why this agent is a good match for the user's request."
}

Examples:

User: "I need help with travel planning"
{
    "name": "Travel Assistant",
    "message": "I recommend the Travel Assistant agent which specializes in helping users plan their trips, find flights, and book accommodations."
}

User: "I need help with something completely unrelated"
{
    "message": "I couldn't find an agent that matches your request. Could you provide more details about what you're looking for?"
}

User: "Find me a coding tutor"
{
    "name": "Code Mentor",
    "message": "The Code Mentor agent can help you learn programming with personalized tutoring sessions and coding exercises."
}"""

    print(f'Prompt: {prompt}')

    agent = Agent(
        model=OpenAIChat(
            temperature=0,
            base_url=base_url,
            api_key=api_key,
            id=model_name,
        ),
        system_message=prompt
    )


    # Define agent callable
    async def agent_callable(input: ChatInput) -> str:
        result = await agent.arun(message=input.messages[-1], session_id=input.thread_id)
        content = result.content
        if '{' in content and '}' in content:
            try:
                content = json.loads(content[content.find("{"):content.rfind("}")+1])
                name = content.get('name')
                message = content.get('message')
                if name and name in name_to_pubkey:
                    pubkey = name_to_pubkey[name]
                    link = f'https://primal.net/p/{pubkey}'
                    return f"{message}\n\nYou can find the agent here: {link}"
                return message if message else "No agent with relevant skills found."
            except:
                pass
        elif "none" == content.lower().strip():
            return "No agent with relevant skills found."
        return content.strip()
        

    # Create Nostr Agent Server
    server = NostrAgentServer(relays=os.getenv("NOSTR_RELAYS").split(","),
                              private_key=os.getenv("AGENT_PRIVATE_KEY"),
                              nwc_str=os.getenv("AGENT_NWC_CONN_STR"),
                              agent_info=AgentCard(
                                  name='Discovery Agent',
                                  description='This agent can help users find other agents on Nostr.',
                                  skills=[Skill(
                                    name='agent_finder', 
                                    description='Find an agent that matches users\' request.', 
                                    satoshis=0
                                  )],
                                  satoshis=0,
                                  nostr_pubkey=PrivateKey.from_nsec(os.getenv('AGENT_PRIVATE_KEY')).public_key.bech32(),
                              ),
                              agent_callable=agent_callable)

    # Start server
    await server.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
    