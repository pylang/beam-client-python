class Evented():
    """Simple EventEmitter-like class.

    Listens and reponds (emits) when events are discovered.  Directs the websocket.

    See Also
    --------
    connection.Connection: handles connecting to Beam and chat.
    socket.Socket: interacts with chat.

    """
    def __init__(self):
        self._event_handlers = []

    def on(self, event, function):
        """Adds a listener for an event."""
        self._event_handlers.append((event, function))

    def emit(self, event, *args):
        """Process handlers and dispatch an event if found."""
        for handler in self._event_handlers:
            if handler[0] == event:
                handler[1](*args)
                # NOTE: This is where data from chat is handled.
