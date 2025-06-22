import asyncio
import json
import math
import time

from bolt11.decode import decode
from pynostr.encrypted_dm import EncryptedDirectMessage
from pynostr.event import Event
from pynostr.filters import Filters
from pynostr.key import PrivateKey

from agentstr.logger import get_logger
from agentstr.relay import EventRelay

logger = get_logger(__name__)


def encrypt(privkey: str, pubkey: str, plaintext: str) -> str:
    """Encrypt plaintext using ECDH shared secret.
    
    Args:
        privkey: Sender's private key.
        pubkey: Recipient's public key.
        plaintext: The message to encrypt.
        
    Returns:
        The encrypted message as a string.
    """
    dm = EncryptedDirectMessage()
    dm.encrypt(privkey, cleartext_content=plaintext, recipient_pubkey=pubkey)
    return dm.encrypted_message


def decrypt(privkey: str, pubkey: str, ciphertext: str) -> str:
    """Decrypt ciphertext using ECDH shared secret.
    
    Args:
        privkey: Recipient's private key.
        pubkey: Sender's public key.
        ciphertext: The encrypted message to decrypt.
        
    Returns:
        The decrypted plaintext message.
    """
    dm = EncryptedDirectMessage()
    dm.decrypt(privkey, encrypted_message=ciphertext, public_key_hex=pubkey)
    return dm.cleartext_content


def process_nwc_string(string: str) -> dict:
    """Parse Nostr Wallet Connect connection string into its components.
    
    Args:
        string: The NWC connection string to parse.
        
    Returns:
        Dictionary containing connection parameters.
        
    Raises:
        ValueError: If the connection string is invalid.
    """
    if (string[0:22] != "nostr+walletconnect://"):
        logger.error("Your pairing string was invalid, try one that starts with this: nostr+walletconnect://")
        return
    string = string[22:]
    arr = string.split("&")
    item = arr[0].split("?")
    del arr[0]
    arr.insert(0, item[0])
    arr.insert(1, item[1])
    arr[0] = "wallet_pubkey=" + arr[0]
    arr2 = []
    obj = {}
    for item in arr:
        item = item.split("=")
        arr2.append(item[0])
        arr2.append(item[1])
    for index, item in enumerate(arr2):
        if (item == "secret"):
            arr2[index] = "app_privkey"
    for index, item in enumerate(arr2):
        if (index % 2):
            obj[arr2[index - 1]] = item
    obj["app_pubkey"] = PrivateKey.from_hex(obj["app_privkey"]).public_key.hex()
    return obj


def get_signed_event(event: dict, private_key: str) -> Event:
    """Create and sign a Nostr event with the given private key.

    Args:
        event: The event data as a dictionary.
        private_key: The private key to sign the event with.

    Returns:
        A signed Nostr event.
    """
    logger.debug(f"Signing event in nwc_relay: {json.dumps(event)}")
    event = Event(**event)
    event.sign(private_key)
    return event


class NWCRelay:
    """Client for interacting with Nostr Wallet Connect (NWC) relays.

    Handles encrypted communication with wallet services over the Nostr network.
    """
    def __init__(self, nwc_connection_string: str, relay: str | None = None):
        """Initialize NWC client with connection string and optional relay URL.

        Args:
            nwc_connection_string: NWC connection string (starts with 'nostr+walletconnect://')
            relay: Optional relay URL override
        """
        logger.info(f"Initializing NWCRelay with connection string: {nwc_connection_string[:10]}...")
        try:
            self.nwc_info = process_nwc_string(nwc_connection_string)
            logger.debug(f"NWC info: {self.nwc_info}")
            if relay is None:
                relay = self.nwc_info["relay"]
            logger.debug(f"Using relay: {relay}")
            self.private_key = PrivateKey.from_hex(self.nwc_info["app_privkey"])
            logger.info("NWCRelay initialized successfully")
        except Exception as e:
            logger.critical(f"Failed to initialize NWCRelay: {e!s}", exc_info=True)
            raise

    @property
    def event_relay(self) -> EventRelay:
        return EventRelay(self.nwc_info["relay"], private_key=self.private_key)

    async def get_response(self, event_id: str) -> Event | None:
        """Get response for a specific event ID."""
        filters = Filters(
            event_refs=[event_id],
            pubkey_refs=[self.nwc_info["app_pubkey"]],
            kinds=[23195],
            limit=1,
        )
        for _ in range(10):
            event = await self.event_relay.get_event(filters=filters, timeout=10, close_on_eose=False)
            if event:
                return event
            await asyncio.sleep(0)
        return None

    async def make_invoice(self, amount: int, description: str, expires_in: int = 900) -> Event | None:
        """Generate a new payment request.

        Returns:
            Dictionary containing invoice details
        """
        msg = json.dumps({
            "method": "make_invoice",
            "params": {
                "amount": amount * 1000,
                "description": description,
                "expiry": expires_in,
            } if amount else {
                "description": description,
                "expiry": expires_in,
            },
        })
        emsg = encrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], msg)
        obj = {
            "kind": 23194,
            "content": emsg,
            "tags": [["p", self.nwc_info["wallet_pubkey"]]],
            "created_at": math.floor(time.time()),
            "pubkey": self.nwc_info["app_pubkey"],
        }
        logger.debug(f"Sending invoice request: {json.dumps(obj)}")
        event = get_signed_event(obj, self.nwc_info["app_privkey"])
        # Send event and concurrently wait for response
        response_task = asyncio.create_task(self.get_response(event.id))
        await self.event_relay.send_event(event)
        response = await response_task
        if response is None:
            return None
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        logger.debug(f"Received invoice response: {json.dumps(dobj)}")
        return dobj["result"]["invoice"]

    async def check_invoice(self, invoice: str | None = None, payment_hash: str | None = None) -> dict | None:
        """Check the status of an invoice by its payment hash or invoice string."""
        if invoice is None and payment_hash is None:
            raise ValueError("Either 'invoice' or 'payment_hash' must be provided")

        params = {}
        if invoice is not None:
            params["invoice"] = invoice
        if payment_hash is not None:
            params["payment_hash"] = payment_hash

        msg = json.dumps({
            "method": "lookup_invoice",
            "params": params,
        })
        emsg = encrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], msg)
        obj = {
            "kind": 23194,
            "content": emsg,
            "tags": [["p", self.nwc_info["wallet_pubkey"]]],
            "created_at": math.floor(time.time()),
            "pubkey": self.nwc_info["app_pubkey"],
        }
        event = get_signed_event(obj, self.nwc_info["app_privkey"])
        # Send event and concurrently wait for response
        response_task = asyncio.create_task(self.get_response(event.id))
        await self.event_relay.send_event(event)
        response = await response_task
        if response is None:
            return None
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj

    async def did_payment_succeed(self, invoice: str) -> bool:
        """Check if a payment was successful.

        Returns:
            True if payment was successful, False otherwise
        """
        invoice_info = await self.check_invoice(invoice=invoice)
        if (invoice_info and "error" not in invoice_info and ("result" in invoice_info) and (
                "preimage" in invoice_info["result"])):
            return invoice_info.get("result", {}).get("settled_at") or 0 > 0
        return False

    async def try_pay_invoice(self, invoice: str, amount: int | None = None) -> dict | None:
        """Attempt to pay a BOLT11 invoice.
        Returns:
            Dictionary with payment status and details
        """
        decoded = decode(invoice)
        if decoded.amount_msat and amount:
            if decoded.amount_msat != amount * 1000:  # convert to msats
                raise RuntimeError(f"Amount in invoice [{decoded.amount_msat}] does not match amount provided [{amount}]")
        elif not decoded.amount_msat and not amount:
            raise RuntimeError("No amount provided in invoice and no amount provided to pay")
        msg = {
            "method": "pay_invoice",
            "params": {
                "invoice": invoice,
            },
        }
        if amount:
            msg["params"]["amount"] = amount * 1000
        msg = json.dumps(msg)
        emsg = encrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], msg)
        obj = {
            "kind": 23194,
            "content": emsg,
            "tags": [["p", self.nwc_info["wallet_pubkey"]]],
            "created_at": math.floor(time.time()),
            "pubkey": self.nwc_info["app_pubkey"],
        }
        event = get_signed_event(obj, self.nwc_info["app_privkey"])
        await self.event_relay.send_event(event)

    async def get_info(self) -> dict:
        """Get wallet service information and capabilities."""
        msg = {
            "method": "get_info",
        }
        msg = json.dumps(msg)
        emsg = encrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], msg)
        obj = {
            "kind": 23194,
            "content": emsg,
            "tags": [["p", self.nwc_info["wallet_pubkey"]]],
            "created_at": math.floor(time.time()),
            "pubkey": self.nwc_info["app_pubkey"],
        }
        event = get_signed_event(obj, self.nwc_info["app_privkey"])
        # Send event and concurrently wait for response
        response_task = asyncio.create_task(self.get_response(event.id))
        await self.event_relay.send_event(event)
        response = await response_task
        if response is None:
            return None
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj

    async def list_transactions(self, params: dict | None = None) -> list[dict]:
        """List recent transactions matching the given parameters."""
        if params is None:
            params = {}
        msg = {
            "method": "list_transactions",
            "params": params,
        }
        msg = json.dumps(msg)
        emsg = encrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], msg)
        obj = {
            "kind": 23194,
            "content": emsg,
            "tags": [["p", self.nwc_info["wallet_pubkey"]]],
            "created_at": math.floor(time.time()),
            "pubkey": self.nwc_info["app_pubkey"],
        }
        event = get_signed_event(obj, self.nwc_info["app_privkey"])
        # Send event and concurrently wait for response
        response_task = asyncio.create_task(self.get_response(event.id))
        await self.event_relay.send_event(event)
        response = await response_task
        if response is None:
            return None
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj.get("result", {}).get("transactions", [])

    async def get_balance(self) -> int | None:
        """Get current wallet balance."""
        msg = {
            "method": "get_balance",
        }
        msg = json.dumps(msg)
        emsg = encrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], msg)
        obj = {
            "kind": 23194,
            "content": emsg,
            "tags": [["p", self.nwc_info["wallet_pubkey"]]],
            "created_at": math.floor(time.time()),
            "pubkey": self.nwc_info["app_pubkey"],
        }
        event = get_signed_event(obj, self.nwc_info["app_privkey"])
        response_task = asyncio.create_task(self.get_response(event.id))
        await self.event_relay.send_event(event)
        response = await response_task
        if response is None:
            return None
        ersp = response.content
        drsp = decrypt(self.nwc_info["app_privkey"], self.nwc_info["wallet_pubkey"], ersp)
        dobj = json.loads(drsp)
        return dobj.get("result", {}).get("balance")

    async def on_payment_success(self, invoice: str, callback=None, unsuccess_callback=None, timeout: int = 300, interval: int = 2):
        """Listen for payment success for a given invoice.

        This method continuously checks for payment success until either the payment
        is confirmed or the timeout is reached.

        Args:
            invoice (str): The BOLT11 invoice string to listen for.
            callback (callable, optional): A function to call when payment succeeds.
            unsuccess_callback (callable, optional): A function to call if payment fails.
            timeout (int, optional): Maximum time to wait in seconds (default: 300).
            interval (int, optional): Time between checks in seconds (default: 2).

        Raises:
            Exception: If the callback function raises an exception.
        """
        start_time = time.time()
        success = False
        while True:
            if await self.did_payment_succeed(invoice):
                success = True
                if callback:
                    try:
                        await callback()
                    except Exception as e:
                        logger.error(f"Error in callback: {e}", exc_info=True)
                        raise e
                break
            if time.time() - start_time > timeout:
                break
            await asyncio.sleep(interval)
        if not success:
            if unsuccess_callback:
                await unsuccess_callback()
