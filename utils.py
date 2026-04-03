import asyncio
import os
from aiogram import Bot
from aiogram.types import FSInputFile


async def send_safe_message(bot: Bot, chat_id, message):
    while True:
        try:
            await bot.send_message(chat_id, message)
            break
        except:
            await asyncio.sleep(1)


async def send_safe_document(bot: Bot, chat_id, file_path):
    while True:
        try:
            await bot.send_document(chat_id, FSInputFile(file_path))
            break
        except:
            await asyncio.sleep(1)


async def send_file_and_cleanup(bot: Bot, chat_id, file_path, response_text=None):
    await send_safe_document(bot, chat_id, file_path)
    os.remove(file_path)
    return response_text


