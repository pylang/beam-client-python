import json
import random

from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop

from .evented import Evented


class Socket(Evented):

    packet_id = 0

    def __init__(self, addresses):
        super(Socket, self).__init__()

        self.connected = False
        self.ws = None

        self.address_offset = random.randint(0, len(addresses)-1)
        self.addresses = addresses

        self._connect()

    def _get_address(self):
        self.address_offset += 1
        self.address_offset %= len(self.addresses)

        return self.addresses[self.address_offset]

    def _connect(self):
        address = self._get_address()
        print("Connecting to {}...".format(address))

        websocket_connect(
            address,
            callback=self._on_open,
            on_message_callback=self._parse_packet
        )

    def _parse_packet(self, packet_str):
        if packet_str is None:
            self._on_close(1)
        else:
            packet = json.loads(packet_str)
            self.emit("message", packet["data"])

    def _on_open(self, future):
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

    def send(self, type_, *args, **kwargs):
        if not self.connected:
            return

        packet = {
            "type": type_,
            "arguments": args,
            "id": self.packet_id
        }

        packet.update(kwargs)
        print("SEND:", packet)
        self.ws.write_message(json.dumps(packet))
        self.packet_id += 1
