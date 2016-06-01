import requests

from .evented import Evented
from .socket import Socket
from .errors import NotAuthenticatedError, UnknownError


class Connection(Evented):
    '''Parse the config file.'''

    def __init__(self, config):
        super(Connection, self).__init__()

        self.config = config
        self.chat_details = None
        self.channel = None
        self.user_id = None

    def _get_auth_body(self):
        """Return the authentication body for logging in to Beam."""
        return {
            "username": self.config.USERNAME,
            "password": self.config.PASSWORD
        }

    def _build_addr(self, path):
        """Create an address to Beam with the given path."""
        return self.config.BEAM_ADDR + path

    def _log_into_beam(self):
        """Log into Beam via HTTPS."""

        session = requests.Session()

        # Attempt to log in
        login_response = session.post(
            self._build_addr("/api/v1/users/login"),
            data=self._get_auth_body()
        )

        # Throw an error if the user login fails
        if login_response.status_code != requests.codes.ok:
            raise NotAuthenticatedError(login_response)

        self.user_id = login_response.json()["id"]

        # Request auth for the chat server
        chat_response = session.get(
            self._build_addr("/api/v1/chats/{id}".format(id=self.channel))
        )

        # If there's an error here... that should not be!
        if chat_response.status_code != requests.codes.ok:
            raise UnknownError(login_response)

        self.chat_details = chat_response.json()

    def _connect_to_chat(self):
        """Connect to the chat websocket."""

        if self.chat_details is None:
            raise NotAuthenticatedError("You must first log in to Beam!")

        self.websocket = Socket(self.chat_details["endpoints"])
        self.websocket.on("opened", self._send_auth_packet)
        self.websocket.on("message", lambda msg: self.emit("message", msg))

    def _send_auth_packet(self):
        """Send an authentication packet to the chat server"""
        self.websocket.send(
            "method",
            self.channel, self.user_id, self.chat_details["authkey"],
            method="auth"
        )

    def authenticate(self, channel):
        """Log into beam and connects to the chat server."""
        self.channel = channel

        self._log_into_beam()
        self._connect_to_chat()

    def message(self, msg):
        """Send a chat message."""
        self.websocket.send("method", msg, method="msg")
