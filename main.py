#!/usr/bin/env python3
"""Experimental telegram bot for managing school canteen"""
from argparse import ArgumentParser
from aiogram import Bot, Dispatcher, executor, types
from bcrypt import hashpw
from connection import DatabaseConnection
from functions import load_configuration, get_reply_content
# from logging import info, error
PROG = "broccoli_bot"
DESCRIPTION = "ERP system for school canteen"
DB_TABLES = ["roles_table", "market_table", "users_table"]


def check_new_user(database_connection: DatabaseConnection,
                   userid: int) -> bool:
    """
    Checks if user with given id is in database, and returns result as bool
    """
    query = queries_manager["users"]["select_user"]
    data = (userid,)
    result = database_connection.execute_query(query, data)
    if len(result) == 0:
        return False
    return True


def get_language_by_id(user_id: int):
    query = queries_manager["users"]["select_user_lang"]
    data = (user_id,)
    result = db_connection.execute_query(query, data)
    if result:
        return result[0]
    return False


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
SALT = config["bot"]["salt"].encode("utf-8")
queries_manager = load_configuration("queries.ini")
db_connection = DatabaseConnection(config["postgresql"])
if DEBUG is True:
    query = queries_manager["critical"]["manual_drop_all"]
    db_connection.execute_query(query)
for table in DB_TABLES:
    query = queries_manager["tables"][table]
    db_connection.execute_query(query)
query = queries_manager["roles"]["add_role"]
admin_userid = config["bot"]["admin_userid"]
data = ["admin", admin_userid]
db_connection.execute_query(query, data)


async def startup_notification(_):
    """print startup message to stdin"""
    print("\nBot has been launched\n")


@dispatcher.message_handler(commands=["help", "помощь"])
async def help_command(message: types.Message):
    """reply with help message"""
    user_id = int(message.from_user.id)
    current_language = get_language_by_id(user_id)
    if not current_language:
        current_language = "en"
    output = get_reply_content(message_storage, current_language, "help")
    await bot.send_message(chat_id=message.from_user.id, text=output)
    await message.delete()


@dispatcher.message_handler(commands=["lang", "язык"])
async def set_lang(message: types.Message):
    """update user's language"""
    user_id = int(message.from_user.id)
    contents = message.text.split()
    if len(contents) != 2:
        reply_data = (message_storage, current_language, "wrong_message")
        reply_content = get_reply_content(*reply_data)
        await bot.send_message(chat_id=user_id, text=reply_content)
        return
    current_language = get_language_by_id(user_id)
    lang = contents[1]
    data = {"userid": user_id, "lang": lang}
    query = queries_manager["users"]["update_user_lang"]
    db_connection.execute_query(query, data)
    reply_data = [message_storage, lang, "update_language"]
    reply_content = get_reply_content(*reply_data)
    await bot.send_message(chat_id=user_id, text=reply_content)
    await message.delete()


@dispatcher.message_handler(commands=["start", "старт"])
async def login(message: types.Message):
    """Login into system"""
    user_id = int(message.from_user.id)
    is_in_database = check_new_user(db_connection, user_id)
    current_language = get_language_by_id(user_id)
    if not current_language:
        current_language = "en"
        data = {"userid": user_id, "lang": "en"}
        query = queries_manager["users"]["update_user_lang"]
        db_connection.execute_query(query, data)
        reply = get_reply_content(message_storage, "en", "update_language")
        await message.reply(reply)
    else:
        current_language = current_language[0][0]
    if is_in_database:
        reply_data = [message_storage, current_language]
        reply_data.append("user_exists_in_database")
        reply_content = get_reply_content(*reply_data)
        await bot.send_message(chat_id=user_id, text=reply_content)
    else:
        reply_data = [message_storage, current_language]
        reply_data.append("user_not_exists_in_database")
        reply_content = get_reply_content(*reply_data)
        await bot.send_message(chat_id=user_id, text=reply_content)
        reply_data = [message_storage, current_language, "ask_for_username"]
        reply_content = get_reply_content(*reply_data)
        context_storage["waiting_for_username"].append(user_id)
        await bot.send_message(chat_id=user_id, text=reply_content)
    await message.delete()


# TODO
@dispatcher.message_handler(commands=["order", "заказать"])
async def order(message: types.Message):
    """
    order dishes
    message format: `/order dishname quantity`
    """
    user_id = message.from_user.id
    contents = message.text.split()
    current_language = get_language_by_id(user_id)
    if not current_language:
        current_language = "en"
    if len(contents) != 3:
        reply_data = (message_storage, current_language, "wrong_message")
        reply_contents = get_reply_contents(*reply_data)
        await bot.send_message(chat_id=user_id, text=reply_contents)
        return
    order, quantity = contents[1], contents[2]
    query = queries_manager["market"]["select_dish_quantity"]
    current_quantity = db_connection.execute_query(query)
    if order > quantity:
        reply_data = (message_storage, current_language, "dish_unavailable")
        reply_contents = get_reply_contents(*reply_data)
        await bot.send_message(chat_id=user_id, text=reply_contents)
    query = queries_manager["user"]["select_user"]
    username = db_connection.execute_query(query, (user_id,))
    data = [username, order, quantity]
    query = queries_manager["orders"]["order_dish"]
    db_connection.execute_query(query, data)
    query = queries_manager["roles"]["select_userid_by_role"]
    sellers = db_connection.execute_query(query, ("seller",))
    sellers = [x[0] for x in sellers]
    order_message = ["new order from " + username]
    order_message.append(order + ": " + str(quantity))
    order_message = "\n".join(order_message)
    reply_data = (message_storage, current_language, "order_message")
    reply_contents = get_reply_content(*reply_data)
    for userid in sellers:
        await bot.send_message(chat_id=user_id, text=contents)


@dispatcher.message_handler(commands["confirm", "подтвердить"])
async def confirm(message: types.Message):
    """
    confirm completing an order of selected username
    message format: `/confirm username`
    """
    user_id = message.from_user.id
    contents = contents.split()
    current_language = get_language_by_id(user_id)
    if not current_language:
        current_language = "en"
    if len(contents) != 2:
        reply_data = (message_storage, current_language, "wrong_message")
        reply_contents = get_reply_content(*reply_data)
        await bot.send_message(chat_id=user_id, text=reply_contents)
        return
    username = contents[1]
    query = queries_manager["market"]["decrease_quantity"]
    db_connection.execute_query(query, username)
    query = queries_manager["orders"]["delete_order"]
    db_connection.execute_query(query, username)
    reply_data = (message_storage, current_language, "order_closed")
    reply_contents = get_reply_content(*reply_data)
    query = queries_manager["roles"]["select_userid_by_role"]
    sellers = db_connection.execute_query(query, ("seller",))
    sellers = [x[0] for x in sellers]
    for userid in sellers:
        await bot.send_message(chat_id=userid, text=reply_contents)


@dispatcher.message_handler(commands["adddish", "добавить", "разместить"])
async def place(message: types.Message):
    """
    place new dish if you're a cook or admin
    message format: `/addish dishname price quantity`
    """
    user_id = message.from_user.id
    contents = message.text.split()
    current_language = get_language_by_id(user_id)
    if not current_language:
        current_language = "en"
    roles = ["cook", "admin"]
    has_role = False
    for role in roles:
        data = [user_id, role]
        query = queries_manager["other"]["check_if_role"]
        result = db.execute_query(query, data)
        if result:
            has_role = True
            break
    if not has_role:
        reply_data = [message_storage, current_language, "access_rights"]
        reply_contents = get_reply_content(*reply_data)
        await bot.send_message(chat_id=user_id, text=reply_contents)
        return
    if len(contents) != 3:
        reply_data = [message_storage, current_language, "wrong_massage"]
        reply_contents = get_reply_content(*reply_data)
        await bot.send_message(chat_id=user_id, text=reply_content)
        return
    dish, quantity = contents[1], contents[2]
    data = [dish, price, quantity]
    query = queries_manager["market"]["add_dish"]
    db_connection.execute_query(query, data)
    reply_data = [message_storage, current_laguage, "dish_added"]
    reply_contents = get_reply_content(*reply_data)
    await bot.send_message(chat_id=user_id, text=reply_contents)

@dispatcher.message_handler(comments=["menu", "меню"])
async def menu(message: types.Message):
    """send list of available dishes and their price & quantity"""
    user_id = message.from_user.id
    message = []
    query = queries_manager["market"]["select_dishes"]
    menu = db_connection.execute_query(query)
    for element in menu:
        point = [element[0], element[1], "р.", "-", element[2], "шт."]
        message.append(" ".join(point))
    message = "\n".join(message)
    await bot.send_message(chat_id=user_id, contents=message)


@dispatcher.message_handler(commands=["addrole"])
async def add_user(message: types.Message):
    """
    add new user into system.
    required format is `/addrole userid role`
    """
    user_id = message.from_user.id
    contents = message.text.split()
    current_language = get_language_by_id(user_id)
    data = [userid, "admin"]
    query = queries_manager["roles"]["check_if_admin"]
    result = db_connection.execute_query(query, data)
    if not result:
        reply_data = (message_storage, current_language, "access_rights")
        reply_content = get_reply_content(*reply_data)
        await bot.send_message(chat_id=user_id, text=reply_content)
        return
    if not current_language:
        current_language = "en"
    if len(contents) != 4:
        reply_data = (message_storage, current_language, "wrong_message")
        reply_content = get_reply_content(*reply_data)
        await bot.send_message(chat_id=user_id, text=reply_content)
        return
    name, role, password = contents[1], contents[2], contents[3]
    if role not in ["admin", "cook", "seller"]:
        reply_data = [message_storage, current_language, "unknown_role"]
        reply_content = get_reply_content(*reply_data)
        await bot.send_message(chat_id=user_id, text=reply_content)
    password = password.encode("utf-8")
    password_hash = hashpw(password, SALT)
    data = [name, role, password_hash, user_id]
    query = queries_manager["roles"]["select_roles"]
    existent_roles = [j[0] for j in db_connection.execute_query(query)]
    if name in existent_roles:
        reply_data = [message_storage, current_language, "role_not_added"]
        reply_content = get_reply_content(*reply_data)
        await bot.send_message(chat_id=user_id, text=reply_content)
        return
    query = queries_manager["roles"]["add_role"]
    db_connection.execute_query(query, data)
    reply_data = [message_storage, current_language, "role_added"]
    reply_content = get_reply_content(*reply_data)
    await bot.send_message(chat_id=user_id, text=reply_content)


@dispatcher.message_handler()
async def other(message: types.Message):
    """
    control non-commands messages:
    - ping feature
    - username passing
    """
    current_user_id = message.from_user.id
    contents = message.text
    match message.text.lower():
        case "ping" | "PING" | "пинг" | "ПИНГ":
            data = [message_storage]
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
                query = queries_manager["users"]["add_user"]
                db_connection.execute_query(query, data)
                reply_data = [message_storage, "en", "username_accepted"]
                reply_content = get_reply_content(*reply_data)
                user_chat = message.from_user.id
                await bot.send_message(chat_id=user_chat, text=reply_content)
            else:
                await message.reply(contents)


if __name__ == "__main__":
    executor.start_polling(dispatcher, on_startup=startup_notification)
