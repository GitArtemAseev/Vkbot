import sys
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

VK_API_VERSION = "5.199"

if not TOKEN:
    print("Ошибка: TOKEN не задан в переменных окружения. "
          "Создайте файл .env или укажите TOKEN в settings.py")
    sys.exit(1)

if not GROUP_ID:
    print("Ошибка: GROUP_ID не задан в переменных окружения. "
          "Создайте файл .env или укажите GROUP_ID в settings.py")
    sys.exit(1)