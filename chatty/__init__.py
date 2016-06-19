"""A basic Python implmentation of a chat bot.

This bot uses the following:
- `requests`: handle user data from the Beam API
- `websockets`: to connect and interact with chat

"""
from .connection import Connection


def connect(*args, **kwargs):
    """Intitate connection to Beam and chat."""
    return Connection(*args, **kwargs)
