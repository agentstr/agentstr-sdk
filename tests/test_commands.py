import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from agentstr.commands import Commands, DefaultCommands

@pytest_asyncio.fixture
def nostr_client():
    client = MagicMock()
    client.send_direct_message = AsyncMock()
    client.nwc_relay = MagicMock()
    client.nwc_relay.make_invoice = AsyncMock(return_value="invoice123")
    client.nwc_relay.on_payment_success = AsyncMock()
    return client

@pytest_asyncio.fixture
def db():
    db = MagicMock()
    user = MagicMock()
    user.available_balance = 1000
    db.get_user = AsyncMock(return_value=user)
    db.upsert_user = AsyncMock()
    return db

@pytest_asyncio.fixture
def agent_server(nostr_client):
    server = MagicMock()
    server.nostr_client = nostr_client
    agent_info = MagicMock()
    agent_info.name = "TestAgent"
    agent_info.description = "Agent description."
    server.agent_info = agent_info
    return server

@pytest.mark.asyncio
async def test_commands_default(nostr_client):
    commands = Commands(nostr_client, {})
    await commands.default("foo", "pubkey1")
    nostr_client.send_direct_message.assert_awaited_once_with("pubkey1", "Invalid command: foo")

@pytest.mark.asyncio
async def test_commands_run_command_valid(nostr_client):
    called = {}
    async def dummy(cmd, pk):
        called['cmd'] = cmd
        called['pk'] = pk
    commands = Commands(nostr_client, {"bar": dummy})
    await commands.run_command("!bar", "pubkey2")
    assert called == {'cmd': 'bar', 'pk': 'pubkey2'}

@pytest.mark.asyncio
async def test_commands_run_command_invalid(nostr_client):
    commands = Commands(nostr_client, {})
    await commands.run_command("!baz", "pubkey3")
    nostr_client.send_direct_message.assert_awaited_once_with("pubkey3", "Invalid command: baz")

@pytest.mark.asyncio
async def test_commands_run_command_missing_bang(nostr_client):
    commands = Commands(nostr_client, {})
    await commands.run_command("no_bang", "pubkey4")
    nostr_client.send_direct_message.assert_awaited_once_with("pubkey4", "Invalid command: no_bang")

@pytest.mark.asyncio
async def test_defaultcommands_help(agent_server, db):
    dc = DefaultCommands(db, agent_server.nostr_client, agent_server.agent_info)
    await dc._help("help", "pubkey5")
    agent_server.nostr_client.send_direct_message.assert_awaited_once()
    msg = agent_server.nostr_client.send_direct_message.await_args[0][1]
    assert "Available commands" in msg

@pytest.mark.asyncio
async def test_defaultcommands_describe(agent_server, db):
    dc = DefaultCommands(db, agent_server.nostr_client, agent_server.agent_info)
    await dc._describe("describe", "pubkey6")
    agent_server.nostr_client.send_direct_message.assert_awaited_once_with(
        "pubkey6",
        "I am TestAgent\n\nThis is my description:\n\nAgent description."
    )

@pytest.mark.asyncio
async def test_defaultcommands_balance(agent_server, db):
    dc = DefaultCommands(db, agent_server.nostr_client, agent_server.agent_info)
    await dc._balance("balance", "pubkey7")
    agent_server.nostr_client.send_direct_message.assert_awaited_once_with(
        "pubkey7", "Your balance is 1000 sats"
    )

@pytest.mark.asyncio
async def test_defaultcommands_deposit_success(agent_server, db):
    dc = DefaultCommands(db, agent_server.nostr_client, agent_server.agent_info)
    # Patch on_payment_success to call the callback immediately
    async def fake_on_payment_success(invoice, callback, timeout, unsuccess_callback):
        await callback()
    agent_server.nostr_client.nwc_relay.on_payment_success = fake_on_payment_success
    await dc._deposit("deposit 50", "pubkey8")
    # Should send invoice and then payment success message
    calls = [
        call[0][1] for call in agent_server.nostr_client.send_direct_message.await_args_list
    ]
    assert "invoice123" in calls
    assert any("Payment successful" in c or "Your new balance" in c for c in calls)

@pytest.mark.asyncio
async def test_defaultcommands_deposit_failure(agent_server, db):
    dc = DefaultCommands(db, agent_server.nostr_client, agent_server.agent_info)
    # Patch on_payment_success to call the unsuccess_callback
    async def fake_on_payment_success(invoice, callback, timeout, unsuccess_callback):
        await unsuccess_callback()
    agent_server.nostr_client.nwc_relay.on_payment_success = fake_on_payment_success
    await dc._deposit("deposit 50", "pubkey9")
    calls = [
        call[0][1] for call in agent_server.nostr_client.send_direct_message.await_args_list
    ]
    assert "invoice123" in calls
    assert any("Payment failed" in c for c in calls)
