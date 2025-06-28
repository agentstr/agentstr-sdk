from dotenv import load_dotenv

load_dotenv()

import os
from agentstr import AgentCard, Skill
from agentstr import ChatInput, NostrAgentServer, NoteFilters, default_price_handler
from pynostr.key import PrivateKey
from langchain_openai import ChatOpenAI
import random
import string
from typing import Literal
from pydantic import BaseModel
import dspy
import datetime


YEAR = 2025
MONTH = 9
DAY = 1


class Date(BaseModel):
    # Somehow LLM is bad at specifying `datetime.datetime`, so
    # we define a custom class to represent the date.
    year: int
    month: int
    day: int
    hour: int = 12

class Flight(BaseModel):
    flight_id: str
    date_time: Date
    origin: str
    destination: str
    duration: float
    price: float

class Itinerary(BaseModel):
    confirmation_number: str
    flight: Flight


flight_database = {
    "DA123": Flight(
        flight_id="DA123",  # DSPy Airline 123
        origin="SFO",
        destination="JFK",
        date_time=Date(year=YEAR, month=MONTH, day=DAY, hour=6),
        duration=5.9,
        price=350,
    ),
    "DA125": Flight(
        flight_id="DA125",
        origin="SFO",
        destination="JFK",
        date_time=Date(year=YEAR, month=MONTH, day=DAY, hour=9),
        duration=4.5,
        price=420,
    ),
    "DA456": Flight(
        flight_id="DA456",
        origin="SFO",
        destination="JFK",
        date_time=Date(year=YEAR, month=MONTH, day=DAY, hour=12),
        duration=5.25,
        price=380,
    ),
    "DA460": Flight(
        flight_id="DA460",
        origin="SFO",
        destination="JFK",
        date_time=Date(year=YEAR, month=MONTH, day=DAY, hour=15),
        duration=5,
        price=400,
    ),
    "DA789": Flight(
        flight_id="DA789",
        origin="SFO",
        destination="JFK",
        date_time=Date(year=YEAR, month=MONTH, day=DAY, hour=18),
        duration=5.25,
        price=450,
    ),
    "DA101": Flight(
        flight_id="DA101",
        origin="SFO",
        destination="JFK",
        date_time=Date(year=YEAR, month=MONTH, day=DAY, hour=7),
        duration=5.5,
        price=390,
    ),
    "DA202": Flight(
        flight_id="DA202",
        origin="SFO",
        destination="JFK",
        date_time=Date(year=YEAR, month=MONTH, day=DAY, hour=10),
        duration=5.25,
        price=410,
    ),
    "DA303": Flight(
        flight_id="DA303",
        origin="SFO",
        destination="JFK",
        date_time=Date(year=YEAR, month=MONTH, day=2, hour=13),
        duration=5.5,
        price=370,
    ),
    "DA404": Flight(
        flight_id="DA404",
        origin="SFO",
        destination="JFK",
        date_time=Date(year=YEAR, month=MONTH, day=DAY, hour=16),
        duration=5.25,
        price=390,
    ),
    "DA505": Flight(
        flight_id="DA505",
        origin="SFO",
        destination="JFK",
        date_time=Date(year=YEAR, month=MONTH, day=DAY, hour=8),
        duration=5.8,
        price=360,
    ),
}

itinery_database = {}
ticket_database = {}


async def show_itinerary():
    """Show the itinerary for the user"""
    return sorted(list(itinery_database.values()), key=lambda x: datetime.datetime(x.date_time.year, x.date_time.month, x.date_time.day, x.date_time.hour))

async def search_flights(criteria: Literal['shortest', 'cheapest'] = 'shortest') -> Flight:
    """Pick up the best flight that matches users' request. we pick the shortest, and cheaper one on ties."""
    sorted_flights = sorted(
        list(flight_database.values()),
        key=lambda x: (
            x.get("duration" if criteria == 'shortest' else "price") if isinstance(x, dict) else x.duration,
            x.get("price" if criteria == 'shortest' else "duration") if isinstance(x, dict) else x.price,
        ),
    )
    return sorted_flights[0]


def _generate_id(length=8):
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choices(chars, k=length))


async def book_flight(flight: Flight):
    """Book a flight on behalf of the user."""
    confirmation_number = _generate_id()
    while confirmation_number in itinery_database:
        confirmation_number = _generate_id()
    itinery_database[confirmation_number] = Itinerary(
        confirmation_number=confirmation_number,
        flight=flight,
    )
    return confirmation_number, itinery_database[confirmation_number]


async def cancel_itinerary(confirmation_number: str):
    """Cancel an itinerary on behalf of the user."""
    if confirmation_number in itinery_database:
        del itinery_database[confirmation_number]
        return
    raise ValueError("Cannot find the itinerary, please check your confirmation number.")



class DSPyAirlineCustomerSerice(dspy.Signature):
    """You are an airline customer service agent that helps user book and manage flights.

    You are given a list of tools to handle user request, and you should decide the right tool to use in order to
    fullfil users' request."""

    user_request: str = dspy.InputField(desc="The user's request")
    history: dspy.History = dspy.InputField(desc="The conversation history")
    process_result: str = dspy.OutputField(
        desc=(
                "Message that summarizes the process result, and the information users need, e.g., the "
                "confirmation_number if a new flight is booked."
            )
        )


agent = dspy.ReAct(
    DSPyAirlineCustomerSerice,
    tools = [
        show_itinerary,
        search_flights,
        book_flight,
        cancel_itinerary
    ]
)

llm_api_key = os.getenv("LLM_API_KEY")
llm_base_url = os.getenv("LLM_BASE_URL")
llm_model_name = os.getenv("LLM_MODEL_NAME")

dspy.configure(lm=dspy.LM(model=llm_model_name, api_base=llm_base_url.rstrip('/v1'), api_key=llm_api_key, model_type='chat'))


async def run():
    message_history = {}

    async def agent_callable(chat_input: ChatInput) -> str:
        thread_id = chat_input.thread_id or str(uuid.uuid4())
        print(f"Found request: {chat_input.messages[-1]}")
        history = dspy.History(messages=message_history.get(thread_id, []))
        if thread_id not in message_history:
            message_history[thread_id] = []
        result = await agent.acall(user_request=chat_input.messages[-1], history=history)
        message_history[thread_id].append({'user_request': chat_input.messages[-1], **result}) 
        print(f"Result: {result.process_result}")       
        return result.process_result

    # Define agent info
    agent_info = AgentCard(
        name='Travel Agent',
        description=('This agent can help you find, book, and manage flights.'),
        skills=[Skill(name='book_flight', description='Book a flight on behalf of a user.', satoshis=25),
                Skill(name='show_itinerary', description='Show the itinerary for the user.', satoshis=0),
                Skill(name='search_flights', description='Search for flights that matches users\' request.', satoshis=0),
                Skill(name='cancel_itinerary', description='Cancel an itinerary on behalf of the user.', satoshis=0),
                ],
        satoshis=0,
        nostr_pubkey=PrivateKey.from_nsec(os.getenv('AGENT_PRIVATE_KEY')).public_key.bech32(),
    )

    relays = os.getenv('NOSTR_RELAYS').split(',')
    private_key = os.getenv('AGENT_PRIVATE_KEY')
    nwc_str = os.getenv('AGENT_NWC_CONN_STR')

    note_filters = NoteFilters(
        nostr_pubkeys=['npub1jch03stp0x3fy6ykv5df2fnhtaq4xqvqlmpjdu68raaqcntca5tqahld7a'],
    )
    
    server = NostrAgentServer(relays=relays, 
                              private_key=private_key, 
                              nwc_str=nwc_str,
                              agent_info=agent_info,
                              agent_callable=agent_callable,
                              note_filters=note_filters,
                              price_handler=default_price_handler())

    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())



    
