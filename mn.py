import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# ==================== CONFIG ====================
# Get these from https://my.telegram.org/apps
API_ID = 12345                # Your API ID (integer)
API_HASH = "your_api_hash"    # Your API hash (string)

# Bot tokens from @BotFather
BOT_TOKENS = [
    ".",
    ".",
    ".",
    ".",
]

MESSAGE = "💥"                 
BURST_DELAY = 0.05            
# =================================================

clients = []
nuke_active = False
target_group = None

async def setup_bots():
    for i, token in enumerate(BOT_TOKENS):
        try:
            client = TelegramClient(None, API_ID, API_HASH)
            await client.start(bot_token=token)
            me = await client.get_me()
            print(f"[✓] Bot {i+1}: @{me.username}")
            clients.append(client)
        except Exception as e:
            print(f"[✗] Bot {i+1} failed: {e}")
    print(f"\n[+] {len(clients)} bots ready")

async def spam_group(chat_id):
    global nuke_active
    while nuke_active:
        tasks = [client.send_message(chat_id, MESSAGE) for client in clients]
        try:
            await asyncio.gather(*tasks)
        except FloodWaitError as e:
            print(f"[!] Flood wait {e.seconds}s")
            await asyncio.sleep(e.seconds)
        except Exception:
            pass
        await asyncio.sleep(BURST_DELAY)

@events.register(events.ChatAction)
async def on_add(event):
    if event.user_added and event.user_id == (await event.client.get_me()).id:
        chat = await event.get_chat()
        print(f"[+] Added to {chat.title}")
        await event.client.send_message(chat.id, "Type /nuke")

@events.register(events.NewMessage(pattern='/nuke'))
async def nuke_cmd(event):
    global nuke_active, target_group
    if nuke_active:
        await event.reply("Already nuking")
        return
    chat = await event.get_chat()
    target_group = chat.id
    nuke_active = True
    await event.reply(f"Nuking {chat.title} with {len(clients)} bots")
    await spam_group(chat.id)

@events.register(events.NewMessage(pattern='/stop'))
async def stop_cmd(event):
    global nuke_active
    if nuke_active:
        nuke_active = False
        await event.reply("Stopped")

async def main():
    await setup_bots()
    if not clients:
        return
    for client in clients:
        client.add_event_handler(on_add)
        client.add_event_handler(nuke_cmd)
        client.add_event_handler(stop_cmd)
    print("\n[✓] Botnet active. Add bots to groups, then type /nuke")
    await asyncio.gather(*[client.run_until_disconnected() for client in clients])

if name == 'main':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Shutting down")
        for client in clients:
            asyncio.run(client.disconnect())
