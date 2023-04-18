#!/usr/bin/env python3
"""Experimental telegram bot for managing school canteen"""
from argparse import ArgumentParser
from bcrypt import hashpw  # gensalt
from aiogram import Bot, Dispatcher, executor, types
from database import DatabaseConnection, load_queries
from functions import load_configuration, get_reply_content
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


context_storage = {"waiting_for_username": [],}
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
        output = get_reply_content(message_storage, "en", "help")
    else:
        current_language = result[0]
        output = get_reply_content(message_storage, current_language, "help")
    await bot.send_message(chat_id=message.from_user.id, text=output)
    await message.delete()


@dispatcher.message_handler(commands=["lang", "язык"])
async def set_lang(message: types.Message):
    """update user's language"""
    user_id = int(message.from_user.id)
    contents = message.text.split()
    query = queries_manager["select_user_lang"]
    current_language = db_connection.execute_query(query, (user_id,))
    if len(contents) != 2:
        reply_data = (message_storage, current_language, "wrong_message")
        reply_content = get_reply_content(*reply_data)
        reply_content = message_storage[current_language]["ask_for_username"]
        context_storage["waiting_for_username"].append(user_id)
    else:
        lang = contents[1]
        data = {"userid": user_id, "lang": lang}
        query = queries_manager["update_user_lang"]
        db_connection.execute_query(query, data)
        reply_data = [message_storage, lang, "update_language"]
        reply_content = get_reply_content(*reply_data)
    await bot.send_message(chat_id=message.from_user.id, text=reply_content)
    await message.delete()


@dispatcher.message_handler(commands=["start", "старт"])
async def login(message: types.Message):
    """Login into system"""
    user_id = int(message.from_user.id)
    is_in_database = check_new_user(db_connection, user_id)
    query = queries_manager["select_user_lang"]
    current_language = db_connection.execute_query(query, (user_id,))
    if not current_language:
        current_language = "en"
        data = {"userid": user_id, "lang": "en"}
        query = queries_manager["update_user_lang"]
        db_connection.execute_query(query, data)
        reply = get_reply_content(message_storage, "en", "update_language")
        await message.reply(reply)
    else:
        current_language = current_language[0][0]
    if is_in_database:
        reply_data = [message_storage, current_language]
        reply_data.append("user_exists_in_database")
        reply_content = get_reply_content(*reply_data)
        await bot.send_message(chat_id=message.from_user.id, text=reply_content)
    else:
        reply_data = [message_storage, current_language]
        reply_data.append("user_not_exists_in_database")
        reply_content = get_reply_content(*reply_data)
        await bot.send_message(chat_id=message.from_user.id, text=reply_content)
        reply_data = [message_storage, current_language, "ask_for_username"]
        reply_content = get_reply_content(*reply_data)
        context_storage["waiting_for_username"].append(user_id)
        await bot.send_message(chat_id=message.from_user.id, text=reply_content)
    await message.delete()


# TODO
@dispatcher.message_handler(commands=["order", "заказать"])
async def order(message: types.Message):
    """order dishes"""
    user_id = message.from_user.id
    contents = message.text.split()


@dispatcher.message_handler(commands=["addrole"])
async def add_user(message: types.Message):
    """Add new user into system"""
    ...


@dispatcher.message_handler()
async def other(message: types.Message):
    """
    control non-commands messages:
    - ping feature

    """
    current_user_id = message.from_user.id
    contents = message.text
    match message.text.lower():
        case "ping" | "PING" | "пинг" | "ПИНГ":
            data = [contents]
            if contents == "ping":
                data.extend(["en", "pong_small"])
                result = get_reply_content(*data)
            elif contents == "PING":
                data.extend(["en", "pong_large"])
                result = get_reply_content(*data)
            elif contents == "пинг":
                data.extend(["ru", "pong_small"])
                result = get_reply_content(*data)
            elif contents == "ПИНГ":
                data.extend(["ru", "pong_large"])
                result = get_reply_content(*data)
            await message.reply(text=result)

        case _:
            username_requests = context_storage["waiting_for_username"]
            if current_user_id in username_requests:
                data = {"userid": current_user_id, "username": message.text}
                data["lang"] = "en"
                query = queries_manager["add_user"]
                db_connection.execute_query(query, data)
                reply_data = [message_storage, "en", "username_accepted"]
                reply_content = get_reply_content(*reply_data)
                user_chat = message.from_user.id
                await bot.send_message(chat_id=user_chat, text=reply_content)
            else:
                await message.reply(contents)


if __name__ == "__main__":
    executor.start_polling(dispatcher, on_startup=startup_notification)
