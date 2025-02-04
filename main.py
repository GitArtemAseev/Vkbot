import sys
import asyncio
import aiohttp

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
from app.bot import VkBot
from app.longpoll import LongPoll
from settings import TOKEN, GROUP_ID, VK_API_VERSION

async def main():
    longpoll_params = {
        "enabled": 1,
        "message_new": 1,
        "message_allow": 1,
    }
    group_edit_params= {
        "messages":1
    }
    group_settings_params = {
        "bots_capabilities": 1,
        "bots_start_button": 1,
    }

    async with aiohttp.ClientSession() as session:
        bot = VkBot(TOKEN, GROUP_ID, VK_API_VERSION, session)
        bot.set_params(longpoll_params,group_edit_params,group_settings_params)
        longpoll = LongPoll(bot, session, timeout=25)
        await longpoll.listen()

if __name__ == "__main__":
    asyncio.run(main())
