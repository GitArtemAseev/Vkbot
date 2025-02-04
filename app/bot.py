import aiohttp
import random

class VkBot:
    """
    Класс, отвечающий за обработку событий и отправку сообщений.
    """
    def __init__(self, token: str, group_id: str, api_verion: str, session: aiohttp.ClientSession):
        self.token = token
        self.group_id = group_id
        self.api_version = api_verion
        self.session = session

    def set_params(self,longpoll_params: dict = None, group_edit_params: dict = None, group_settings_params: dict = None):
        """
        Устанавливает параметров бота.
        """
        self.longpoll_params = longpoll_params
        self.group_edit_params = group_edit_params
        self.group_settings_params = group_settings_params

    async def process_event(self, event):
        """
        Обрабатывает событие, полученное от Long Poll.
        """
        if isinstance(event, dict) and "type" in event:
            event_type = event.get("type")
            if event_type == "message_allow":
                print("Событие message_allow.")
                user_id = event["object"].get("user_id")
                await self.send_message(user_id, text="Привет! Спасибо, что написали...")

            if event_type == "message_new":
                message = event.get("object", {}).get("message")
                if not message:
                    print("Событие message_new не содержит сообщение.")
                    return

                peer_id = message.get("peer_id", message.get("from_id"))
                if peer_id is None:
                    print("Не удалось определить peer_id.")
                    return

                attachments = message.get("attachments", [])
                photo_attachments = []
                for att in attachments:
                    if att.get("type") == "photo":
                        photo = att.get("photo", {})
                        owner_id = photo.get("owner_id")
                        photo_id = photo.get("id")
                        if owner_id and photo_id:
                            att_str = f"photo{owner_id}_{photo_id}"
                            if "access_key" in photo:
                                att_str += f"_{photo['access_key']}"
                            photo_attachments.append(att_str)
                if photo_attachments:
                    attachment_str = ",".join(photo_attachments)
                    print(f"Получено фото от пользователя {peer_id}. Отправляем его обратно...")
                    await self.send_message(peer_id, attachment=attachment_str)
       

    async def send_message(self, peer_id: int, attachment: str = "", text: str = ""):
        """
        Отправляет сообщение через API ВКонтакте.
        """
        url = "https://api.vk.com/method/messages.send"
        params = {
            "access_token": self.token,
            "peer_id": peer_id,
            "attachment": attachment,
            "random_id": random.randint(1, 2**31 - 1),
            "v": self.api_version,
            "message": text,
        }
        async with self.session.get(url, params=params) as resp:
            data = await resp.json()
            if "error" in data:
                print("Ошибка при отправке сообщения:", data["error"])
            else:
                print("Сообщение успешно отправлено:", data)
