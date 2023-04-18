#!/usr/bin/env python3
"""
Telegram bot for managing school canteen (experiment)
"""
from argparse import ArgumentParser
from bcrypt import hashpw  # gensalt
from aiogram import Bot, Dispatcher, executor, types
from database import QueriesManager, DatabaseConnection, load_queries
from functions import get_message, load_configuration
# from logging import info, error
PROG = "broccoli_bot"
DESCRIPTION = "ERP system for school canteen"
DB_TABLES = ["roles_table", "market_table", "users_table"]


def check_new_user(database_connection: DatabaseConnection, userid: int) -> bool:
    """Checks if user with given id is in database, and returns result as bool"""
    query = queries_manager["select_user"]
    data = (userid,)
    result = database_connection.execute_query(query, data)
    if len(result) == 0:
        return False
    return True


context_storage = {"waiting_for_username": False,}
parser = ArgumentParser(prog=PROG, description=DESCRIPTION)
parser.add_argument('token')
args = parser.parse_args()
TOKEN = args.token
bot = Bot(TOKEN)
dispatcher = Dispatcher(bot)
config = load_configuration("config.ini")
message_storage = load_configuration("messages.ini")
DEBUG = config["bot"]["debug"] == "true"
queries_manager = load_queries()
db_connection = DatabaseConnection(config["postgresql"])
if DEBUG is True:
    db_connection.execute_query(queries_manager["drop_all"])
for table in DB_TABLES:
    db_connection.execute_query(queries_manager[table])


async def startup_notification(_):
    """print startup message to stdin"""
    print("\nBot has been launched\n")


@dispatcher.message_handler(commands=["help", "помощь"])
async def help_command(message: types.Message):
    """reply with help message"""
    user_id = int(message.from_user.id)
    query = queries_manager["select_user_lang"]
    result = db_connection.execute_query(query, (user_id,))
    if len(result) == 0:
        output = message_storage["en"]["help"]
    else:
        current_language = result[0]
        output = message_storage[current_language]["help"]
    await message.reply(text=output)


@dispatcher.message_handler(commands=["lang", "язык"])
async def set_lang(message: types.Message):
    """update user's language"""
    user_id = int(message.from_user.id)
    contents = message.text.split()
    query = queries_manager["select_user_lang"]
    current_language = db_connection.execute_query(query, (user_id,))
    if len(contents) != 2:
        reply_message_name = current_language + "_" + "_wrong_message"
        reply_content = get_message(reply_message_name)
        await message.reply(reply_content)
    else:
        lang = contents[1]
        data = {"userid": user_id, "lang": lang}
        query = queries_manager["update_user_lang"]
        db_connection.execute_query(query, data)
        reply_message_name = lang + "_" + "update_language"
        reply_content = get_message(reply_message_name)
        await message.reply(reply_content)


@dispatcher.message_handler(commands=["start", "старт"])
async def login(message: types.Message):
    """Login into system"""
    user_id = int(message.from_user.id)
    is_in_database = check_new_user(db_connection, user_id)
    if is_in_database:
        await message.reply("in_database")
    else:
        await message.reply("not in database yet")
        await message.reply("please, send me username.")


@dispatcher.message_handler(commands=["order", "заказать"])
async def login(message: types.Message):
    """order dishes"""
    user_id = message.from_user.id
    contents = message.text.split()


@dispatcher.message_handler(commands=["addrole"])
async def add_user(message: types.Message):
    """Add new user into system"""
    ...


@dispatcher.message_handler()
async def ping(message: types.Message):
    """ping-pong function"""
    if message.text == "ping":
        await message.reply(text="pong")
    elif message.text == "PING":
        await message.reply(text="PONG")


@dispatcher.message_handler()
async def turn(message: types.Message):
    """mirror sent message"""
    await message.reply(message.text)



if __name__ == "__main__":
    executor.start_polling(dispatcher, on_startup=startup_notification)
