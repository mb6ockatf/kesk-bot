from configparser import ConfigParser


def load_configuration(filename: str) -> ConfigParser:
    configuration = ConfigParser()
    configuration.read(filename)
    return configuration


def get_reply_content(storage: ConfigParser, lang: str, message: str) -> str:
    reply = storage[lang][message]
    return reply.strip('"')
