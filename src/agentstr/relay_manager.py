import asyncio
import json
import time
from collections.abc import Callable

from expiringdict import ExpiringDict
from pynostr.encrypted_dm import EncryptedDirectMessage
from pynostr.event import Event
from pynostr.filters import Filters
from pynostr.utils import get_public_key

from agentstr.logger import get_logger
from agentstr.relay import DecryptedMessage, EventRelay

logger = get_logger(__name__)


class RelayManager:
    """Manages connections to multiple Nostr relays and handles message passing.
    
    Args:
        relays: List of relay URLs to connect to.
        private_key: Optional private key for signing events.
    """
    def __init__(self, relays: list[str], private_key: str | None = None):
        logger.debug(f"Initializing RelayManager with {len(relays)} relays")
        self._relays = relays
        self.private_key = private_key
        self.public_key = self.private_key.public_key if self.private_key else None

    @property
    def relays(self) -> list[EventRelay]:
        """Get a list of connected EventRelay instances.
        
        Returns:
            A list of EventRelay instances, one for each relay URL.
        """
        return [EventRelay(relay, self.private_key, self.public_key) for relay in self._relays]

    async def get_events(self, filters: Filters, limit: int = 10, timeout: int = 30, close_on_eose: bool = True) -> list[Event]:
        """Fetch events matching the given filters from connected relays.
        
        Args:
            filters: The filters to apply when fetching events.
            limit: Maximum number of events to return. Defaults to 10.
            timeout: Maximum time to wait for events in seconds. Defaults to 30.
            close_on_eose: Whether to close the subscription after EOSE. Defaults to True.
            
        Returns:
            A list of up to `limit` unique events that match the filters.
            
        Note:
            Stops early if enough events are found before the timeout.
        """
        limit = filters.limit if filters.limit else limit
        event_id_map = {}
        result = None
        t0 = time.time()
        tasks = []
        for relay in self.relays:
            tasks.append(asyncio.create_task(relay.get_events(filters, limit, timeout, close_on_eose)))
        for done in asyncio.as_completed(tasks):
            result = await done
            if result and len(result) >= limit:
                break
            for event in result:
                if event.id in event_id_map:
                    continue
                event_id_map[event.id] = event
                if len(event_id_map) >= limit:
                    result = list(event_id_map.values())
                    break
            if timeout < time.time() - t0:
                break
        if not result:
            result = list(event_id_map.values())
        return result

    async def get_event(self, filters: Filters, timeout: int = 30, close_on_eose: bool = True) -> Event:
        """Get a single event matching the filters or None if not found."""
        result = await self.get_events(filters, limit=1, timeout=timeout, close_on_eose=close_on_eose)
        if result and len(result) > 0:
            return result[0]
        return None

    async def send_event(self, event: Event) -> Event:
        """Send an event to all connected relays."""
        tasks = []
        event.created_at = int(time.time())
        event.compute_id()
        event.sign(self.private_key.hex())
        for relay in self.relays:
            tasks.append(asyncio.create_task(relay.send_event(event)))
        await asyncio.gather(*tasks)

    def encrypt_message(self, message: str | dict, recipient_pubkey: str, tags: dict[str, str] | None = None) -> Event:
        """Encrypt a message for the recipient and prepare it as a Nostr event."""
        recipient = get_public_key(recipient_pubkey)
        dm = EncryptedDirectMessage()

        if isinstance(message, dict):
            message = json.dumps(message)

        dm.encrypt(self.private_key.hex(), cleartext_content=message, recipient_pubkey=recipient.hex())
        event = dm.to_event()
        event.created_at = int(time.time())
        if tags:
            for tag_key, tag_value in tags.items():
                event.add_tag(tag_key, tag_value)
        event.compute_id()
        event.sign(self.private_key.hex())
        return event

    async def send_message(self, message: str | dict, recipient_pubkey: str, tags: dict[str, str] | None = None) -> Event:
        """Send an encrypted message to a recipient through all connected relays."""
        logger.info(f"Sending message to {recipient_pubkey[:10]}: {message}")

        try:
            event = self.encrypt_message(message, recipient_pubkey, tags=tags)
            logger.debug(f"Encrypted message event: {event.id}")

            tasks = []
            for relay in self.relays:
                logger.debug(f"Queueing message for relay: {relay.relay}")
                tasks.append(asyncio.create_task(relay.send_event(event)))

            logger.debug(f"Dispatching message to {len(tasks)} relays")
            await asyncio.gather(*tasks)
            logger.info(f"Successfully sent message to {recipient_pubkey[:10]} with event id: {event.id[:10]}")

            return event

        except Exception as e:
            logger.error(f"Failed to send message to {recipient_pubkey[:10]}: {e!s}", exc_info=True)
            raise

    async def receive_message(self, author_pubkey: str, timestamp: int | None = None, timeout: int = 30) -> DecryptedMessage | None:
        """Wait for and return the next message from the specified author."""
        logger.info(f"Waiting for message from {author_pubkey[:10]}...")
        logger.debug(f"Timeout: {timeout}s, Timestamp: {timestamp}")

        t0 = time.time()
        tasks = []

        try:
            # Start receive tasks for all relays
            for relay in self.relays:
                logger.debug(f"Starting receive task for relay: {relay.relay}")
                task = asyncio.create_task(relay.receive_message(author_pubkey, timestamp, timeout))
                tasks.append(task)

            # Wait for the first successful response
            for task in asyncio.as_completed(tasks):
                try:
                    result = await task
                    if result:
                        logger.info(f"Received message from {author_pubkey[:10]} with id {result.event.id[:10]}: {result.message}")
                        return result

                    # Check timeout
                    if time.time() - t0 > timeout:
                        logger.warning(f"Receive operation timed out after {timeout} seconds")
                        break

                except Exception as e:
                    logger.warning(f"Error in receive task: {e!s}")
                    continue

            logger.warning("No messages received before timeout")
            return None

        except Exception as e:
            logger.error(f"Error in receive_message: {e!s}", exc_info=True)
            raise

    async def send_receive_message(self, message: str | dict, recipient_pubkey: str, timeout: int = 3, tags: dict[str, str] | None = None) -> DecryptedMessage | None:
        """Send a message and wait for a response from the recipient.

        Returns the first response received within the timeout period.
        """
        dm_event = await self.send_message(message, recipient_pubkey, tags)
        timestamp = dm_event.created_at
        logger.debug(f"Sent receive DM event: {dm_event.to_dict()}")
        return await self.receive_message(recipient_pubkey, timestamp, timeout)

    async def event_listener(self, filters: Filters, callback: Callable[[Event], None]):
        """Start listening for events matching the given filters.

        The callback will be called for each matching event.
        """
        event_cache = ExpiringDict(max_len=1000, max_age_seconds=300)
        lock = asyncio.Lock()
        tasks = []
        for relay in self.relays:
            tasks.append(asyncio.create_task(relay.event_listener(filters, callback, event_cache, lock)))
        await asyncio.gather(*tasks)

    async def direct_message_listener(self, filters: Filters, callback: Callable[[Event, str], None]):
        """Start listening for direct messages.

        The callback will be called with each received message and its decrypted content.
        """
        event_cache = ExpiringDict(max_len=1000, max_age_seconds=300)
        lock = asyncio.Lock()
        tasks = []
        for relay in self.relays:
            tasks.append(asyncio.create_task(relay.direct_message_listener(filters, callback, event_cache, lock)))
        await asyncio.gather(*tasks)

    async def get_following(self, pubkey: str | None = None) -> list[str]:
        """Get the list of public keys that the specified user follows."""
        pubkey = get_public_key(pubkey).hex() if pubkey else self.public_key.hex()
        filters = Filters(authors=[pubkey], kinds=[3], limit=1)
        event = await self.get_event(filters)
        if event:
            return [tag[1] for tag in event.tags if tag[0] == "p"]
        return []
