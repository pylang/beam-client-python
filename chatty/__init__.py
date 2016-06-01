from .connection import Connection


def connect(*args, **kwargs):
    """Helper function for the creation of connections."""
    return Connection(*args, **kwargs)
