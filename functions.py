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

