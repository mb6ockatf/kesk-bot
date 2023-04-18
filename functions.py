"""
Functions storage
This file is supposed to be imported from main.py
"""
from configparser import ConfigParser


def load_configuration(filename: str) -> ConfigParser:
    """Load configuration && return it"""
    configuration = ConfigParser()
    configuration.read(filename)
    return configuration


def get_reply_content(storage: ConfigParser, lang: str, message: str) -> str:
    "get a message from messages.ini file"
    reply = storage[lang][message]
    reply = reply.strip('"')
    return reply
