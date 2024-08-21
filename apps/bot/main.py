import asyncio
import os
import sys
import logging

import aiogram
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs
from aiogram import filters, types
import fluent.runtime
from tortoise import Tortoise

from modules import welcome, registration, trip, users, notes, map
from db import tortoise_config


logging.basicConfig(level=logging.INFO, stream=sys.stdout)

token = os.environ.get("BOT_TOKEN", None)
if token is None:
    raise RuntimeError("No token specified, aborting")
web_app_domain = os.environ.get("WEB_APP_DOMAIN", None)
if web_app_domain is None:
    raise RuntimeError("No web app url specified, aborting")

storage = MemoryStorage()
bot = aiogram.Bot(token=token)
dp = aiogram.Dispatcher(storage=storage)

dp.include_router(welcome.router)
dp.include_router(registration.router)
dp.include_router(notes.router)
dp.include_router(map.router)
dp.include_routers(trip.router, trip.selection_dialog)
dp.include_routers(users.router, users.selection_dialog)
setup_dialogs(dp)

loader = fluent.runtime.FluentResourceLoader("strings/{locale}")
strings = fluent.runtime.FluentLocalization(["ru"], ["main.ftl"], loader)


@dp.shutdown()
async def on_shutdown():
    await Tortoise.close_connections()


async def main():
    await Tortoise.init(config=tortoise_config)
    web_app_url = "https://" + web_app_domain + "/"
    await dp.start_polling(bot, strings=strings, web_app_url=web_app_url)


if __name__ == "__main__":
    asyncio.run(main())
