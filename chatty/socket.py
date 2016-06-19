"""Simulate a websocket that interacts with chat; a backend to Connection."""

import json
import random

from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop

from .evented import Evented


class Socket(Evented):
    """Setup a websocket, handle internal emitter messages and chat messages."""

    packet_id = 0

    def __init__(self, addresses):
        super(Socket, self).__init__()

        self.connected = False
        self.ws = None

        self.address_offset = random.randint(0, len(addresses)-1)
        self.addresses = addresses

        self._connect()

    # Helper Methods ----------------------------------------------------------
    # ? Seem to send a stream of messages to instruct the websocket
    def _get_address(self):
         # ? Seems to extract an address from addresses/endpoints
        self.address_offset += 1
        self.address_offset %= len(self.addresses)

        return self.addresses[self.address_offset]

    def _connect(self):
        """Return a Future given a url."""
        address = self._get_address()
        print("Connecting to {}...".format(address))

        # Use tornado websockets to connect to chat at the given address
        # Result is WebSocketClientConnection
        # https://tornadokevinlee.readthedocs.io/en/latest/websocket.html#client-side-support
        websocket_connect(
            address,
            callback=self._on_open,
            on_message_callback=self._parse_packet
        )

    def _on_open(self, future):
        """Await a websocket future; connect with client if no exception raised."""
        if future.exception() is None:
            self.ws = future.result()
            self.connected = True
            self.emit("opened")
        else:
            print("Unable to connect to the socket.")
            print("Retrying in 1 second.")

            self.connected = False
            IOLoop.instance().call_later(1, self._connect)

    def _on_close(self, code, reason=None):
        print("Socket closed.")
        print("Reestablishing the socket in 1 second.")
        self.connected = False
        self.emit("closed")

        IOLoop.instance().call_later(1, self._connect)

    def _parse_packet(self, packet_str):
        """Repackage the packet and send to the websocket."""
        if packet_str is None:
            self._on_close(1)
        else:
            packet = json.loads(packet_str)
            self.emit("message", packet["data"])

    # Methods -----------------------------------------------------------------
    # `on` and `emit` are inherited from `Evented`
    def send(self, type_, *args, **kwargs):
        """Send a packet or None."""
        if not self.connected:
            return

        packet = {
            "type": type_,
            "arguments": args,
            "id": self.packet_id
        }

        packet.update(kwargs)
        print("SEND:", packet)

        # Package the packet in json and send the message to the client via wensocket
        self.ws.write_message(json.dumps(packet))
        self.packet_id += 1
