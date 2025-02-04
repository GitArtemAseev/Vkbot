import asyncio
import aiohttp
from .bot import VkBot

class LongPoll:
    """
    Класс для получения событий через Long Poll API.
    """
    def __init__(self, bot: VkBot, session: aiohttp.ClientSession, timeout:int):
        self.bot = bot
        self.session = session
        self.timeout = timeout

        self.server = None
        self.key = None
        self.ts = None

    async def _call_api(self, session: aiohttp.ClientSession, method: str, extra_params: dict):
        """
        Вспомогательный метод для вызова метода API ВКонтакте.
        """
        url = f"https://api.vk.com/method/{method}"
        params = {
            "access_token": self.bot.token,
            "group_id": self.bot.group_id,
            "v": self.bot.api_version,
        }
        params.update(extra_params)

        async with session.get(url, params=params) as resp:
            data = await resp.json()
            if 'error' in data:
                raise Exception(f"Ошибка получения параметров Long Poll: {data['error']}")
        return data
    
    async def get_long_poll_server(self):

        data = await self._call_api(self.session,'groups.getLongPollServer',{})

        response = data.get('response', {})

        self.server = response.get('server')
        self.key = response.get('key')
        self.ts = response.get('ts')

    async def init_vk_settings(self, longpoll_params: dict = None,group_edit_params: dict = None, group_settings_params: dict = None):
        """
        Выполняет настройки сообщества в ВКонтакте:
         1) `groups.setLongPollSettings` (при необходимости),
         2) `groups.edit` (при необходимости),
         3) `groups.setSettings` (при необходимости).
        """
        async with aiohttp.ClientSession() as local_session:
            if longpoll_params:
                await self._call_api(local_session, "groups.setLongPollSettings", longpoll_params)
            if group_edit_params:
                await self._call_api(local_session, "groups.edit", group_edit_params)
            if group_settings_params:
                await self._call_api(local_session, "groups.setSettings", group_settings_params)


    async def listen(self):
        """
        Начинает прослушивание событий.
        """
        await self.init_vk_settings(longpoll_params = self.bot.longpoll_params,
                                    group_edit_params = self.bot.group_edit_params,
                                    group_settings_params = self.bot.group_settings_params)
        
        if not all([self.server, self.key, self.ts]):
            await self.get_long_poll_server()

        print("Long Poll слушатель запущен. Ожидание событий...")

        while True:
            params = {
                'act': 'a_check',
                'key': self.key,
                'ts': self.ts,
                'wait': self.timeout,
                'mode': 2,
            }
            try:
                async with self.session.get(self.server, params=params, timeout=self.timeout+5) as resp:
                    data = await resp.json()
            except Exception as e:
                print("Ошибка при запросе к Long Poll серверу:", e)
                await asyncio.sleep(1)
                continue

            if 'failed' in data:
                print("Проблемы с Long Poll сервером, переинициализация:", data)
                if data['failed'] == 1:
                    self.ts = data.get('ts')
                elif data['failed'] in [2, 3]:
                    await self.get_long_poll_server()
                continue

            self.ts = data.get('ts')
            updates = data.get('updates', [])
            for update in updates:
                asyncio.create_task(self.bot.process_event(update))

