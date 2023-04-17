#!/usr/bin/env python3
"""
Telegram bot for managing school canteen (experiment)
"""
# from logging import info, error
from argparse import ArgumentParser
from bcrypt import hashpw  # gensalt
from aiogram import Bot, Dispatcher, executor, types


program_data = {"prog": "broccoli",
                "description": "ERP system for school canteen"}
parser = ArgumentParser(**program_data)
parser.add_argument('token')
args = parser.parse_args()
TOKEN = args.token
bot = Bot(TOKEN)
dispatcher = Dispatcher(bot)


HELP_STRING = """
/help - показать этот список комманд
"""

async def startup_notification(_):
    """print startup message to stdin"""
    print("\nBot has been launched\n")

@dispatcher.message_handler(commands=["help"])
async def help_command(message: types.Message):
    """REPLY WITH HELP MESSAGE"""
    await message.reply(text=HELP_STRING)
    await message.reply(message.text)


@dispatcher.message_handler()
async def turn(message: types.Message):
    await message.reply(message.text)


@dispatcher.message_handler()
async def ping(message: types.Message):
    """ping-pong function"""
    if message.text == "ping":
        await message.reply(text="pong")
    elif message.text == "PING":
        await message.reply(text="PONG")



if __name__ == "__main__":
    executor.start_polling(dispatcher, on_startup=startup_notification)